"""Run a text simulation of the LAP voice-agent conversation."""
from __future__ import annotations

import json
from pathlib import Path

from .engine import VoiceAgentEngine

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)
    print("Home Credit LAP Voice Agent - Local Text Simulation")
    print("This is a test simulator, not a real telephone call. Type 'quit' to stop.\n")
    customer_name = input("Customer name [Rahul]: ").strip() or "Rahul"
    engine = VoiceAgentEngine({"customer_name": customer_name})
    turn = engine.start()
    print(f"Agent: {turn.response}")

    while not engine.state.call_ended:
        try:
            utterance = input("Customer: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSimulation interrupted.")
            break
        if utterance.lower() in {"quit", "exit"}:
            print("Simulation stopped by user.")
            break
        turn = engine.process(utterance)
        print(f"Agent: {turn.response}")

    if engine.history:
        timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = OUTPUTS / f"call_{timestamp}.json"
        txt_path = OUTPUTS / f"call_{timestamp}.txt"
        json_path.write_text(json.dumps(engine.export_session(), indent=2, ensure_ascii=False), encoding="utf-8")
        txt_path.write_text(engine.transcript() + "\n", encoding="utf-8")
        print(f"\nSaved transcript: {txt_path.relative_to(ROOT)}")
        print(f"Saved session data: {json_path.relative_to(ROOT)}")
        print(f"Final result: {engine.state.result or 'INCOMPLETE'}")


if __name__ == "__main__":
    main()
