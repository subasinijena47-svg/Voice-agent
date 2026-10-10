"""Run representative local simulations; these are not real voice calls."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lap_voice_agent import VoiceAgentEngine  # noqa: E402

OUTPUTS = ROOT / "outputs"
SCENARIOS = [
    ("happy_path_all_information_at_once", "PRELIMINARILY_QUALIFIED", [
        "Yes, this is Rahul, speaking.",
        "This is a fresh loan. It's a residential house, jointly owned with my wife, the original property documents are available, I need ₹50 lakh, I'm salaried and the income comes to my bank account, the property is worth around ₹1 crore, and I'd prefer 10 years."]),
    ("agricultural_property", "NOT_ELIGIBLE", ["Yes, this is Rahul.", "Fresh loan. The property is agricultural land."]),
    ("cash_income", "NOT_ELIGIBLE", ["Yes, I'm Rahul.", "Fresh loan.", "It's residential, I am self-employed, and most of my income comes in cash."]),
    ("original_documents_unavailable", "NOT_ELIGIBLE", ["Yes, speaking.", "This is a fresh loan.", "It's a residential house and I only have photocopies, not the originals."]),
    ("tenure_below_three_years", "NOT_ELIGIBLE", ["Yes, this is Rahul.", "Fresh loan. I would like to repay it in 2 years."]),
    ("tenure_above_fifteen_years", "NOT_ELIGIBLE", ["Yes, speaking.", "This is a new loan. I'd prefer a 16-year tenure."]),
    ("over_limit_accept_cap", "PRELIMINARILY_QUALIFIED", ["Yes, speaking.", "This is a fresh loan, and I need ₹90 lakh.", "Yes, ₹75 lakh will work.", "Residential house, sole owned, original documents are available, I'm salaried and paid through my bank, property worth ₹1 crore, 10 years."]),
    ("over_limit_declined", "AMOUNT_LIMIT_DECLINED", ["Yes, this is Rahul.", "Fresh loan; I need ₹90 lakh.", "No, I cannot proceed with ₹75 lakh."]),
    ("existing_loan_transfer_path", "LOAN_TRANSFER_SPECIALIST", ["Yes, this is Rahul.", "I already have a loan against this property."]),
    ("emi_reduction_transfer_path", "LOAN_TRANSFER_SPECIALIST", ["Yes, speaking.", "I want to reduce my current EMI."]),
    ("busy_customer_callback", "CALLBACK_REQUESTED", ["I'm busy right now, please call tomorrow at 4 PM."]),
    ("out_of_order_information", "PRELIMINARILY_QUALIFIED", ["Yes, it's Rahul.", "It's a fresh loan.", "It's a residential property worth ₹80 lakh, jointly owned with my brother.", "Original papers are available at home.", "I need ₹30 lakh.", "Self-employed, and income is received in my bank account.", "I'd like to repay in 5 years."]),
    ("rate_question_diversion", "ACTIVE_CONTINUATION", ["Yes, this is Rahul.", "Fresh loan.", "Residential property.", "What is your interest rate?"]),
    ("wrong_person_privacy_gate", "WRONG_PERSON", ["Wrong number, I'm not Rahul."]),
    ("cash_corrected_to_bank_in_same_turn", "PRELIMINARILY_QUALIFIED", ["Yes, speaking.", "Fresh loan.", "Residential property, sole owner, original documents at home, I need ₹25 lakh, and I am salaried. My income is cash—sorry, actually it is credited to my bank account. Property is worth ₹70 lakh, and I want 7 years."]),
]


def run_one(name: str, expected: str, turns: list[str]) -> dict:
    engine = VoiceAgentEngine({"customer_name": "Rahul"})
    engine.start()
    for utterance in turns:
        engine.process(utterance)
        if engine.state.call_ended:
            break
    actual = engine.state.result or ("ACTIVE_CONTINUATION" if not engine.state.call_ended else "INCOMPLETE")
    if expected == "ACTIVE_CONTINUATION":
        passed = not engine.state.call_ended and engine.state.phase == "eligibility"
    else:
        passed = actual == expected
    return {"scenario": name, "expected": expected, "actual": actual, "passed": passed,
            "phase": engine.state.phase, "state": engine.state.to_dict(), "transcript": engine.transcript()}


def main() -> int:
    OUTPUTS.mkdir(exist_ok=True)
    results = [run_one(*scenario) for scenario in SCENARIOS]
    report = {"note": "SIMULATED text-based scenarios; not real calls, audio, or platform logs.",
              "scenario_count": len(results), "passed": sum(bool(r["passed"]) for r in results),
              "failed": sum(not bool(r["passed"]) for r in results), "results": results}
    (OUTPUTS / "scenario_results.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    sections = ["# Simulated Scenario Transcripts\n\n**Important:** These are local text simulations, not real voice-platform recordings.\n"]
    for r in results:
        sections.extend([f"\n## {r['scenario']} — {'PASS' if r['passed'] else 'FAIL'}\n",
                         f"Expected: `{r['expected']}`  \nActual: `{r['actual']}`\n",
                         "```text\n" + r["transcript"] + "\n```\n"])
    (OUTPUTS / "scenario_transcripts.md").write_text("\n".join(sections), encoding="utf-8")
    print(f"Scenario results: {report['passed']}/{report['scenario_count']} passed")
    print("JSON report: outputs/scenario_results.json")
    print("Transcripts: outputs/scenario_transcripts.md")
    for r in results:
        print(f"{'PASS' if r['passed'] else 'FAIL':4}  {r['scenario']}: expected={r['expected']} actual={r['actual']}")
    return 0 if report["failed"] == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
