"""Conversation state machine for the Home Credit LAP qualification demo."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .extractor import (
    detect_branch_question,
    detect_busy,
    detect_decline,
    detect_fresh_loan,
    detect_interest_rate_question,
    detect_no,
    detect_transfer_request,
    detect_verified,
    detect_yes,
    extract_callback_time,
    extract_facts,
)
from .models import QualificationState

MAX_LOAN_RUPEES = 7_500_000


@dataclass
class AgentTurn:
    response: str
    phase: str
    call_ended: bool
    result: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "response": self.response,
            "phase": self.phase,
            "call_ended": self.call_ended,
            "result": self.result,
        }


class VoiceAgentEngine:
    """Rule-driven local simulator.

    This simulator does not call an LLM or place a real telephone call. It is
    designed to validate business rules locally; use the full system prompt on
    a supported voice-agent platform for natural language / speech behavior.
    """

    def __init__(self, context: dict[str, str] | None = None) -> None:
        self.context = {
            "company_name": "Home Credit",
            "customer_name": "Rahul",
            "agent_name": "Asha",
            "agent_gender": "female",
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "current_day": datetime.now().strftime("%A"),
            "current_time": datetime.now().strftime("%H:%M"),
            "additional_context_from_rag": "No additional product-specific facts provided.",
            "language_to_speak": "English",
        }
        if context:
            self.context.update(context)
        self.state = QualificationState()
        self.history: list[dict[str, str]] = []
        self._started = False

    def start(self) -> AgentTurn:
        if self._started:
            return AgentTurn(self.history[-1]["text"], self.state.phase, self.state.call_ended, self.state.result)
        self._started = True
        message = f"Hello, may I speak with {self.context['customer_name']}?"
        return self._agent(message)

    def process(self, customer_utterance: str) -> AgentTurn:
        """Process one customer turn and return the next agent response."""
        if not self._started:
            self.start()
        utterance = (customer_utterance or "").strip()
        if not utterance:
            return self._agent("Sorry, I didn't catch that. Could you please repeat that?")
        self.history.append({"speaker": "customer", "text": utterance})

        if self.state.call_ended:
            return AgentTurn("This call has already ended.", self.state.phase, True, self.state.result)

        if detect_decline(utterance):
            return self._end("Of course. Thank you for your time. Goodbye.", "CUSTOMER_DECLINED")

        if detect_busy(utterance):
            return self._handle_busy(utterance)

        if self.state.phase == "callback_wait":
            return self._handle_callback_time(utterance)

        if self.state.phase == "verify":
            return self._handle_verification(utterance)

        if self.state.phase == "transfer_check":
            return self._handle_transfer_check(utterance)

        if self.state.phase == "amount_cap_confirmation":
            return self._handle_cap_confirmation(utterance)

        if self.state.phase == "eligibility":
            return self._handle_eligibility(utterance)

        return self._agent("Thank you. Could you please repeat that?", ended=self.state.call_ended)

    # ---------- Conversation branches ----------
    def _handle_busy(self, utterance: str) -> AgentTurn:
        requested_time = extract_callback_time(utterance)
        if requested_time:
            self.state.callback_time = requested_time
            return self._end(
                f"Certainly. I'll note your preferred callback time as {requested_time}. Thank you for your time. Goodbye.",
                "CALLBACK_REQUESTED",
            )
        self.state.phase = "callback_wait"
        self.state.last_question_group = "callback_time"
        return self._agent("Certainly, I understand. What would be a convenient time for us to call you back?")

    def _handle_callback_time(self, utterance: str) -> AgentTurn:
        requested_time = extract_callback_time(utterance)
        if not requested_time:
            # An explicit response such as "tomorrow morning" is also a valid callback preference.
            if any(token in utterance.lower() for token in ("morning", "afternoon", "evening", "tomorrow", "today", "next week", "after lunch")):
                requested_time = " ".join(utterance.split())
        if not requested_time:
            return self._agent("Of course. Could you share a preferred day or time for the callback?")
        self.state.callback_time = requested_time
        return self._end(
            f"Thank you. I'll note {requested_time} as your preferred callback time. Have a good day. Goodbye.",
            "CALLBACK_REQUESTED",
        )

    def _handle_verification(self, utterance: str) -> AgentTurn:
        verification = detect_verified(utterance)
        if verification is False:
            return self._end("I apologize for the inconvenience. I'll end the call here. Goodbye.", "WRONG_PERSON")
        if verification is None:
            lowered = utterance.lower()
            if any(x in lowered for x in ("who is calling", "who are you", "what is this about", "why are you calling")):
                return self._agent(
                    f"My name is {self.context['agent_name']}, and I'm calling on behalf of {self.context['company_name']}. "
                    f"May I confirm I'm speaking with {self.context['customer_name']}?"
                )
            return self._agent(f"I'm calling for {self.context['customer_name']}. May I confirm that I'm speaking with them?")

        self.state.customer_verified = True
        facts = extract_facts(utterance, self.state.next_missing_group())
        self._apply_facts(facts)
        invalid = self._disqualification_reason()
        if invalid:
            return self._disqualify(invalid)
        if detect_transfer_request(utterance):
            return self._transfer()

        self.state.phase = "transfer_check"
        return self._agent(
            f"Thank you for confirming. I'm {self.context['agent_name']} from {self.context['company_name']}. "
            "We're reaching out because, as one of our valued customers, you may be eligible for a special "
            "Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check "
            "whether this offer may suit you. First, is this a fresh loan requirement, or do you already have "
            "a loan on this property or want to reduce an existing EMI?"
        )

    def _handle_transfer_check(self, utterance: str) -> AgentTurn:
        facts = extract_facts(utterance, self.state.next_missing_group())
        self._apply_facts(facts)
        invalid = self._disqualification_reason()
        if invalid:
            return self._disqualify(invalid)
        if detect_transfer_request(utterance):
            return self._transfer()
        if detect_fresh_loan(utterance):
            self.state.phase = "eligibility"
            return self._continue_after_facts(utterance, diversion_prefix=self._diversion_answer(utterance), control_response=True)
        if detect_interest_rate_question(utterance) or detect_branch_question(utterance):
            answer = self._diversion_answer(utterance)
            return self._agent(answer + " Before I continue, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?")
        return self._agent(
            "To route your request correctly, could you clarify whether you need a fresh loan against the property, "
            "or whether you already have a loan on it / want to reduce your current EMI?"
        )

    def _handle_cap_confirmation(self, utterance: str) -> AgentTurn:
        # Process any other eligibility facts supplied alongside the customer's answer.
        facts = extract_facts(utterance, "loan_amount")
        loan_in_utterance = "loan_amount_rupees" in facts
        requested_amount = facts.get("loan_amount_rupees")
        other_facts = {k: v for k, v in facts.items() if k not in {"loan_amount_rupees", "requested_loan_amount_rupees"}}
        self._apply_facts(other_facts)
        invalid = self._disqualification_reason()
        if invalid:
            return self._disqualify(invalid)
        if detect_transfer_request(utterance):
            return self._transfer()

        if detect_no(utterance) and requested_amount == MAX_LOAN_RUPEES:
            return self._end(
                "I understand. The current offer has a maximum amount of ₹75 lakh, so I won't continue the qualification. "
                "Thank you for your time. Goodbye.",
                "AMOUNT_LIMIT_DECLINED",
            )

        if loan_in_utterance and requested_amount is not None:
            if requested_amount > MAX_LOAN_RUPEES:
                self.state.requested_loan_amount_rupees = requested_amount
                self.state.loan_amount_rupees = None
                self.state.pending_cap_confirmation = True
                return self._agent(
                    "The current offer is available for up to ₹75 lakh. Would you like to proceed with ₹75 lakh, "
                    "or would you prefer not to continue with this offer?"
                )
            self.state.loan_amount_rupees = requested_amount
            self.state.requested_loan_amount_rupees = requested_amount
            self.state.pending_cap_confirmation = False
            self.state.phase = "eligibility"
            return self._continue_after_facts(utterance, diversion_prefix=self._diversion_answer(utterance), control_response=True)

        if detect_yes(utterance) and not detect_no(utterance):
            self.state.loan_amount_rupees = MAX_LOAN_RUPEES
            self.state.requested_loan_amount_rupees = MAX_LOAN_RUPEES
            self.state.pending_cap_confirmation = False
            self.state.phase = "eligibility"
            return self._continue_after_facts(utterance, diversion_prefix=self._diversion_answer(utterance), control_response=True)
        if detect_no(utterance):
            return self._end(
                "I understand. The current offer has a maximum amount of ₹75 lakh, so I won't continue the qualification. "
                "Thank you for your time. Goodbye.",
                "AMOUNT_LIMIT_DECLINED",
            )
        if detect_interest_rate_question(utterance) or detect_branch_question(utterance):
            return self._agent(
                self._diversion_answer(utterance)
                + " The current offer's maximum is ₹75 lakh. Would you like to proceed with ₹75 lakh?"
            )
        return self._agent(
            "The current offer is available for up to ₹75 lakh. Would you like to proceed with that amount? "
            "Please say whether ₹75 lakh would work for you."
        )

    def _handle_eligibility(self, utterance: str) -> AgentTurn:
        return self._continue_after_facts(utterance, diversion_prefix=self._diversion_answer(utterance))

    # ---------- State update and decisions ----------
    def _continue_after_facts(self, utterance: str, diversion_prefix: str = "", control_response: bool = False) -> AgentTurn:
        facts = extract_facts(utterance, self.state.next_missing_group())
        self._apply_facts(facts)
        invalid = self._disqualification_reason()
        if invalid:
            return self._disqualify(invalid)
        if detect_transfer_request(utterance):
            return self._transfer()
        if self.state.pending_cap_confirmation:
            self.state.phase = "amount_cap_confirmation"
            message = (
                "The current offer is available for up to ₹75 lakh. Would you like to proceed with the maximum "
                "eligible amount of ₹75 lakh?"
            )
            return self._agent((diversion_prefix + " " if diversion_prefix else "") + message)
        if self.state.next_missing_group() is None:
            return self._qualify_and_handoff()
        self.state.phase = "eligibility"
        message = self._question_for_next_missing()
        prefix = (diversion_prefix + " ") if diversion_prefix else ""
        if not self._has_recognized_answer(facts) and not diversion_prefix and not control_response:
            prefix = "Sorry, I didn't catch that clearly. "
        return self._agent(prefix + message)

    def _apply_facts(self, facts: dict[str, Any]) -> None:
        for key, value in facts.items():
            if key == "loan_amount_rupees":
                self.state.requested_loan_amount_rupees = value
                if value > MAX_LOAN_RUPEES:
                    self.state.loan_amount_rupees = None
                    self.state.pending_cap_confirmation = True
                else:
                    self.state.loan_amount_rupees = value
                    self.state.pending_cap_confirmation = False
            elif key == "requested_loan_amount_rupees":
                # The canonical requested amount is written with loan_amount_rupees above.
                continue
            elif hasattr(self.state, key):
                setattr(self.state, key, value)

    @staticmethod
    def _has_recognized_answer(facts: dict[str, Any]) -> bool:
        return any(k in facts for k in (
            "property_type", "ownership_status", "documents_available", "loan_amount_rupees",
            "occupation", "income_mode", "market_value_answered", "tenure_years",
        ))

    def _disqualification_reason(self) -> str | None:
        state = self.state
        if state.property_type == "agricultural":
            return "The offer accepts residential, commercial, or industrial property, but not agricultural property."
        if state.documents_available is False:
            return "Original property documents must be available for verification."
        if state.income_mode == "cash":
            return "The income must be received through a bank for this offer."
        if state.tenure_years is not None and not 3 <= state.tenure_years <= 15:
            return "The available repayment tenure must be between 3 and 15 years, inclusive."
        return None

    def _disqualify(self, reason: str) -> AgentTurn:
        self.state.disqualified = True
        self.state.disqualification_reason = reason
        self.state.phase = "disqualified"
        self.state.result = "NOT_ELIGIBLE"
        return self._end(
            "Thank you for clarifying. Based on the criteria for this specific offer, you do not meet the eligibility "
            "requirements at this time. I appreciate your time. Goodbye.",
            "NOT_ELIGIBLE",
        )

    def _transfer(self) -> AgentTurn:
        self.state.transfer_required = True
        self.state.phase = "transfer"
        self.state.result = "LOAN_TRANSFER_SPECIALIST"
        return self._end(
            "Thank you for clarifying. Since this involves an existing property loan or EMI reduction, a loan-transfer "
            "specialist will contact you to discuss the appropriate options. Thank you for your time. Goodbye.",
            "LOAN_TRANSFER_SPECIALIST",
        )

    def _qualify_and_handoff(self) -> AgentTurn:
        # Safety gate: never allow handoff until each checklist item has been answered.
        if not self.state.checklist_complete() or self.state.disqualified or self.state.transfer_required:
            return self._agent(self._question_for_next_missing())
        self.state.phase = "handoff"
        self.state.result = "PRELIMINARILY_QUALIFIED"
        return self._end(
            "Thank you for answering all the questions. Based on this preliminary check, your details meet the "
            "criteria for this offer. A senior loan expert will contact you shortly to discuss the next steps and "
            "provide the exact interest rate. This is not final loan approval. Thank you, and have a good day.",
            "PRELIMINARILY_QUALIFIED",
        )

    def _question_for_next_missing(self) -> str:
        group = self.state.next_missing_group()
        self.state.last_question_group = group
        questions = {
            "property_type": "To start, what type of property do you own: residential, commercial, or industrial?",
            "ownership_status": "Is the property solely owned by you, or is it jointly owned with someone else?",
            "documents_available": "Are the original property documents available for verification? You do not need to hold them during this call.",
            "loan_amount": "Approximately how much would you like to borrow under this offer? The maximum available is ₹75 lakh.",
            "market_value": "Approximately what is the current market value of the property? A rough estimate is fine.",
            "tenure": "What repayment tenure would you prefer, in years? The available range is 3 to 15 years.",
        }
        if group == "occupation_income":
            if self.state.occupation is None and self.state.income_mode is None:
                return "Are you salaried or self-employed, and is your income received through a bank account or in cash?"
            if self.state.occupation is None:
                return "Thank you. Are you salaried or self-employed?"
            return "Thank you. Is your income received through a bank account or in cash?"
        if group is None:
            return "Thank you. I've captured all the required details."
        return questions[group]

    def _diversion_answer(self, utterance: str) -> str:
        lowered = utterance.lower()
        if detect_interest_rate_question(lowered):
            return "The exact interest rate will be provided by a senior loan expert after this preliminary qualification. I don't want to give you an unconfirmed rate."
        if detect_branch_question(lowered):
            context = self.context.get("additional_context_from_rag", "").strip()
            if context and context != "No additional product-specific facts provided." and "branch" in context.lower():
                return f"Here is the available information: {context}"
            return "I don't have verified branch-location information available in this call, so I don't want to give you an incorrect address."
        return ""

    def _agent(self, message: str, ended: bool | None = None) -> AgentTurn:
        self.history.append({"speaker": "agent", "text": message})
        actual_ended = self.state.call_ended if ended is None else ended
        return AgentTurn(message, self.state.phase, actual_ended, self.state.result)

    def _end(self, message: str, result: str) -> AgentTurn:
        self.state.call_ended = True
        if self.state.result is None:
            self.state.result = result
        # Keep the branch phase for audit, unless an explicit outcome phase already exists.
        if self.state.phase not in {"disqualified", "transfer", "handoff"}:
            if result == "CALLBACK_REQUESTED":
                self.state.phase = "callback_complete"
            elif result == "WRONG_PERSON":
                self.state.phase = "ended_wrong_person"
            elif result == "CUSTOMER_DECLINED":
                self.state.phase = "ended_declined"
            elif result == "AMOUNT_LIMIT_DECLINED":
                self.state.phase = "ended_amount_limit"
            else:
                self.state.phase = "ended"
        self.history.append({"speaker": "agent", "text": message})
        return AgentTurn(message, self.state.phase, True, self.state.result)

    def transcript(self) -> str:
        return "\n".join(f"{item['speaker'].upper()}: {item['text']}" for item in self.history)

    def export_session(self) -> dict[str, Any]:
        return {
            "context": self.context,
            "state": self.state.to_dict(),
            "history": list(self.history),
            "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        }
