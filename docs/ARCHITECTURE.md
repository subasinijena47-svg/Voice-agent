# Architecture and Implementation Notes

## Included components

1. **Platform-ready system prompt** — `prompts/system_prompt.md`. Paste it into the instructions/system-prompt field of Retell AI, Bolna, or another supported voice platform. The hosted platform provides natural language understanding, speech-to-text, text-to-speech, and call control.
2. **Local simulator** — `lap_voice_agent/`. Runs without an API key or third-party dependencies. Its deterministic phrase/amount extractor and state machine make the key assignment rules testable locally.

The local simulator is not a speech recognizer, text-to-speech system, or hosted LLM. It covers common regression-test phrases; the complete natural-speech behavior is described in the platform-ready prompt.

## Conversation phases

- `verify`: confirm the intended customer before disclosing offer details.
- `callback_wait`: capture a preferred callback time for busy customers, then end.
- `transfer_check`: explain the offer and identify a fresh-loan versus existing-loan / EMI-reduction case.
- `eligibility`: collect checklist data in the required order while saving clearly volunteered answers out of order.
- `amount_cap_confirmation`: ask if the customer will proceed with ₹75 lakh (or a clearly chosen lower amount).
- terminal outcomes: wrong person, callback, customer declined, amount limit declined, not eligible, loan-transfer specialist, or preliminary qualification.

## Processing algorithm

For each customer utterance:

1. Respect stop/busy requests.
2. Extract recognizable eligibility facts from the complete utterance.
3. Store new facts, including out-of-order details and clear same-utterance corrections.
4. Check for disqualification and end immediately if a mandatory criterion fails.
5. Detect existing-loan / EMI-reduction cases and route to the specialist message.
6. Handle the loan amount cap.
7. Ask the earliest unanswered checklist item only.
8. Handoff only after all seven checklist items are answered and all criteria pass.

The core design principle is **extract first, validate second, ask the next missing question last**. The prompt and tests emphasize state retention, termination gates, and not inventing business rules.

## Data model and outcomes

`QualificationState` stores each checklist value separately. Occupation and income mode are two fields within one checklist item. Market value has a separate `market_value_answered` flag so the customer can explicitly say they cannot estimate without triggering an invented minimum value rule.

Possible outcomes: `CALLBACK_REQUESTED`, `WRONG_PERSON`, `LOAN_TRANSFER_SPECIALIST`, `NOT_ELIGIBLE`, `AMOUNT_LIMIT_DECLINED`, `CUSTOMER_DECLINED`, `PRELIMINARILY_QUALIFIED`.

## Production boundary

The hosted platform must be configured to use its supported end-call action after terminal outcomes. The assignment's senior-expert handoff asks the agent to say a senior expert will contact the customer; it does **not** explicitly require a live warm transfer, so this project does not invent one. A real CRM callback scheduler, call-disposition webhook, live specialist transfer, and secure customer-data store are not implemented here.
