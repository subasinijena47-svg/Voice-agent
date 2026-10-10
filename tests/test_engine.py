"""Regression tests for mandatory assignment behavior."""
import unittest

from lap_voice_agent import VoiceAgentEngine


class VoiceAgentEngineTests(unittest.TestCase):
    def new_engine(self):
        engine = VoiceAgentEngine({"customer_name": "Rahul"})
        engine.start()
        return engine

    def reach_eligibility(self, engine=None):
        engine = engine or self.new_engine()
        engine.process("Yes, this is Rahul, speaking.")
        turn = engine.process("This is a fresh loan.")
        self.assertEqual(engine.state.phase, "eligibility")
        return engine, turn

    def qualify_customer(self, engine=None):
        engine, _ = self.reach_eligibility(engine)
        turns = [
            "It is a residential house.",
            "It is jointly owned with my wife.",
            "The original property documents are available at home.",
            "I need ₹50 lakh.",
            "I am salaried and my income is credited to my bank account.",
            "The property is worth about ₹1 crore.",
            "I would prefer 10 years.",
        ]
        last_turn = None
        for utterance in turns:
            last_turn = engine.process(utterance)
            if last_turn.call_ended:
                break
        return engine, last_turn

    def test_happy_path_handoffs_only_after_all_fields(self):
        engine, turn = self.qualify_customer()
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.result, "PRELIMINARILY_QUALIFIED")
        self.assertTrue(engine.state.checklist_complete())
        self.assertEqual(engine.state.ownership_status, "joint")
        self.assertEqual(engine.state.market_value_rupees, 10_000_000)
        self.assertEqual(engine.state.loan_amount_rupees, 5_000_000)
        self.assertEqual(engine.state.tenure_years, 10)
        self.assertIn("not final loan approval", turn.response.lower())

    def test_agricultural_property_disqualifies_immediately(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("Actually, this is agricultural land.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.result, "NOT_ELIGIBLE")
        self.assertEqual(engine.state.property_type, "agricultural")

    def test_latest_correction_within_same_utterance_is_used(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("It is residential—sorry, I mean agricultural land.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.property_type, "agricultural")
        self.assertEqual(engine.state.result, "NOT_ELIGIBLE")

    def test_joint_ownership_is_eligible(self):
        engine, turn = self.qualify_customer()
        self.assertEqual(engine.state.ownership_status, "joint")
        self.assertEqual(engine.state.result, "PRELIMINARILY_QUALIFIED")

    def test_missing_original_documents_disqualifies(self):
        engine, _ = self.reach_eligibility()
        engine.process("Residential property.")
        engine.process("It is solely owned by me.")
        turn = engine.process("I only have photocopies, not the originals.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.documents_available, False)
        self.assertEqual(engine.state.result, "NOT_ELIGIBLE")

    def test_original_documents_at_home_count_as_available(self):
        engine, _ = self.reach_eligibility()
        engine.process("Residential house.")
        engine.process("Sole ownership.")
        turn = engine.process("The original papers are kept safely at home.")
        self.assertFalse(turn.call_ended)
        self.assertTrue(engine.state.documents_available)
        self.assertEqual(engine.state.next_missing_group(), "loan_amount")

    def test_cash_income_disqualifies(self):
        engine, _ = self.reach_eligibility()
        for utterance in [
            "Residential house.", "Jointly owned.", "Original documents are available.", "I need ₹20 lakh."
        ]:
            engine.process(utterance)
        turn = engine.process("I am self-employed and I receive the income in cash.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.occupation, "self-employed")
        self.assertEqual(engine.state.income_mode, "cash")
        self.assertEqual(engine.state.result, "NOT_ELIGIBLE")

    def test_bank_income_is_eligible_for_both_occupations(self):
        engine, _ = self.reach_eligibility()
        for utterance in [
            "Residential.", "Sole ownership.", "Original documents are available.", "I need ₹10 lakh."
        ]:
            engine.process(utterance)
        turn = engine.process("I run my own business and all income comes into my bank account.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.occupation, "self-employed")
        self.assertEqual(engine.state.income_mode, "bank")
        self.assertEqual(engine.state.next_missing_group(), "market_value")

    def test_tenure_below_range_disqualifies(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I want to repay over 2 years.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.tenure_years, 2)
        self.assertEqual(engine.state.result, "NOT_ELIGIBLE")

    def test_tenure_above_range_disqualifies(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I would like 16 years.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.tenure_years, 16)
        self.assertEqual(engine.state.result, "NOT_ELIGIBLE")

    def test_tenure_boundaries_are_accepted(self):
        for years in (3, 15):
            engine, _ = self.reach_eligibility()
            # Answer the first field with out-of-order tenure information.
            engine.process(f"Residential property, and I want {years} years.")
            self.assertEqual(engine.state.tenure_years, years)
            self.assertFalse(engine.state.call_ended)

    def test_over_limit_amount_prompts_for_capped_amount(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I need ₹90 lakh.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.phase, "amount_cap_confirmation")
        self.assertTrue(engine.state.pending_cap_confirmation)
        self.assertIn("₹75 lakh", turn.response)

    def test_over_limit_amount_can_be_accepted_at_75_lakh(self):
        engine, _ = self.reach_eligibility()
        engine.process("I need ₹90 lakh.")
        turn = engine.process("Yes, please proceed with ₹75 lakh.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.loan_amount_rupees, 7_500_000)
        self.assertFalse(engine.state.pending_cap_confirmation)
        self.assertEqual(engine.state.phase, "eligibility")

    def test_over_limit_amount_can_be_declined(self):
        engine, _ = self.reach_eligibility()
        engine.process("I need ₹90 lakh.")
        turn = engine.process("No, I cannot proceed with ₹75 lakh.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.result, "AMOUNT_LIMIT_DECLINED")

    def test_exactly_75_lakh_is_allowed(self):
        engine, _ = self.reach_eligibility()
        engine.process("Residential.")
        engine.process("Sole owned.")
        engine.process("The original documents are available.")
        turn = engine.process("I need exactly ₹75 lakh.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.loan_amount_rupees, 7_500_000)
        self.assertFalse(engine.state.pending_cap_confirmation)

    def test_out_of_order_facts_are_saved_and_not_reasked(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("It is a residential house, jointly owned with my brother and worth around ₹80 lakh.")
        self.assertEqual(engine.state.property_type, "residential")
        self.assertEqual(engine.state.ownership_status, "joint")
        self.assertEqual(engine.state.market_value_rupees, 8_000_000)
        self.assertEqual(engine.state.next_missing_group(), "documents_available")
        self.assertIn("original property documents", turn.response.lower())

    def test_existing_loan_routes_to_transfer_specialist(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I already have a loan against this property.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.result, "LOAN_TRANSFER_SPECIALIST")
        self.assertTrue(engine.state.transfer_required)

    def test_emi_reduction_routes_to_transfer_specialist(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I want to reduce my current EMI.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.result, "LOAN_TRANSFER_SPECIALIST")

    def test_negative_existing_loan_mention_is_not_misrouted(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I don't have an existing loan; this is a fresh loan.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.phase, "eligibility")
        self.assertFalse(engine.state.transfer_required)


    def test_unrelated_personal_loan_does_not_trigger_transfer_branch(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I have an existing personal loan, but this LAP request is for a fresh loan.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.phase, "eligibility")
        self.assertFalse(engine.state.transfer_required)

    def test_busy_customer_callback_is_captured(self):
        engine = self.new_engine()
        turn = engine.process("I'm busy right now, call me tomorrow at 4 PM.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.callback_time, "tomorrow at 4 PM")
        self.assertEqual(engine.state.result, "CALLBACK_REQUESTED")

    def test_busy_customer_is_asked_for_callback_time(self):
        engine = self.new_engine()
        turn = engine.process("I'm in a meeting.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.phase, "callback_wait")
        self.assertIn("call you back", turn.response.lower())
        final_turn = engine.process("Tomorrow morning.")
        self.assertTrue(final_turn.call_ended)
        self.assertEqual(engine.state.result, "CALLBACK_REQUESTED")

    def test_wrong_person_is_not_told_about_offer(self):
        engine = self.new_engine()
        turn = engine.process("Wrong number, I'm not Rahul.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.result, "WRONG_PERSON")
        self.assertFalse(any("₹75 lakh" in item["text"] for item in engine.history))

    def test_interest_rate_question_does_not_invent_rate(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("What is your interest rate?")
        self.assertFalse(turn.call_ended)
        self.assertIn("senior loan expert", turn.response.lower())
        self.assertNotRegex(turn.response, r"\d+(?:\.\d+)?\s*%")

    def test_low_market_value_has_no_invented_minimum_threshold(self):
        engine, _ = self.reach_eligibility()
        engine.process("Residential.")
        engine.process("Sole owner.")
        engine.process("Original property documents are available.")
        engine.process("I need ₹5 lakh.")
        engine.process("I am salaried and paid through my bank account.")
        turn = engine.process("The property is worth about ₹8 lakh.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.market_value_rupees, 800_000)
        self.assertIsNone(engine.state.disqualification_reason)

    def test_handoff_is_blocked_until_every_item_is_answered(self):
        engine, _ = self.reach_eligibility()
        engine.process("Residential, sole ownership, original documents at home, need ₹20 lakh, salaried with bank income, property worth ₹1 crore.")
        self.assertFalse(engine.state.call_ended)
        self.assertEqual(engine.state.next_missing_group(), "tenure")
        self.assertNotEqual(engine.state.result, "PRELIMINARILY_QUALIFIED")

    def test_multiple_answers_in_one_utterance_are_captured(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("It's my residential house, sole owned, originals available, and I need ₹40 lakh for 10 years.")
        self.assertEqual(engine.state.property_type, "residential")
        self.assertEqual(engine.state.ownership_status, "sole")
        self.assertTrue(engine.state.documents_available)
        self.assertEqual(engine.state.loan_amount_rupees, 4_000_000)
        self.assertEqual(engine.state.tenure_years, 10)
        self.assertEqual(engine.state.next_missing_group(), "occupation_income")
        self.assertFalse(turn.call_ended)

    def test_corrected_tenure_uses_latest_value(self):
        engine, _ = self.reach_eligibility()
        engine.process("Residential, 10 years—actually, 12 years.")
        self.assertEqual(engine.state.tenure_years, 12)
        self.assertFalse(engine.state.call_ended)

    def test_market_value_unknown_can_be_noted_without_making_up_a_threshold(self):
        engine, _ = self.reach_eligibility()
        engine.process("Residential.")
        engine.process("Sole owned.")
        engine.process("Original papers are available.")
        engine.process("₹20 lakh.")
        engine.process("Salaried, bank income.")
        turn = engine.process("I don't know the exact market value.")
        self.assertFalse(turn.call_ended)
        self.assertTrue(engine.state.market_value_answered)
        self.assertEqual(engine.state.market_value_note, "Customer unable to estimate during call")


    def test_spoken_number_words_for_loan_amount_are_scaled_correctly(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I need seventy-five lakh.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.loan_amount_rupees, 7_500_000)
        self.assertFalse(engine.state.pending_cap_confirmation)

    def test_mixed_cash_and_bank_income_disqualifies(self):
        engine, _ = self.reach_eligibility()
        for utterance in [
            "Residential.", "Sole ownership.", "Original documents are available.", "I need ₹20 lakh."
        ]:
            engine.process(utterance)
        turn = engine.process("My income comes partly in cash and partly through the bank.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.income_mode, "cash")
        self.assertEqual(engine.state.result, "NOT_ELIGIBLE")

    def test_cash_corrected_to_bank_uses_latest_clear_correction(self):
        engine, _ = self.reach_eligibility()
        for utterance in [
            "Residential.", "Sole ownership.", "Original documents are available.", "I need ₹20 lakh."
        ]:
            engine.process(utterance)
        turn = engine.process("My income is cash—sorry, actually it is credited to my bank account.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.income_mode, "bank")
        self.assertIsNone(engine.state.disqualification_reason)

    def test_multiple_distinct_money_values_are_assigned_by_context(self):
        engine, _ = self.reach_eligibility()
        engine.process("Residential, jointly owned.")
        turn = engine.process("My property is worth around ₹1 crore, and I need ₹50 lakh.")
        self.assertFalse(turn.call_ended)
        self.assertEqual(engine.state.market_value_rupees, 10_000_000)
        self.assertEqual(engine.state.loan_amount_rupees, 5_000_000)


    def test_hyphenated_tenure_disqualifies_if_outside_range(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I would prefer a 16-year tenure.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.tenure_years, 16)
        self.assertEqual(engine.state.result, "NOT_ELIGIBLE")

    def test_fresh_loan_control_answer_does_not_trigger_false_clarification(self):
        engine = self.new_engine()
        engine.process("Yes, speaking.")
        turn = engine.process("This is a fresh loan.")
        self.assertFalse(turn.call_ended)
        self.assertIn("what type of property", turn.response.lower())
        self.assertNotIn("didn't catch", turn.response.lower())

    def test_customer_can_decline_at_any_point(self):
        engine, _ = self.reach_eligibility()
        turn = engine.process("I'm not interested, please stop calling.")
        self.assertTrue(turn.call_ended)
        self.assertEqual(engine.state.result, "CUSTOMER_DECLINED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
