# Local Test Results

Validation performed in the working environment on **9 October 2026**.

| Check | Command | Result |
|---|---|---|
| Unit / regression tests | `python -m unittest discover -s tests -v` | **36 passed, 0 failed** |
| Simulated end-to-end scenarios | `python examples/run_scenarios.py` | **15 passed, 0 failed** |
| Syntax compilation | `python -m compileall -q lap_voice_agent tests examples` | Passed |

The scenario runner writes state snapshots to `outputs/scenario_results.json` and simulated dialogue transcripts to `outputs/scenario_transcripts.md`.

**Scope note:** These results validate the local Python implementation only. They do not certify a hosted platform's speech recognition, voice quality, dynamic-variable mapping, call termination behavior, telephony setup, or real audio recordings. Complete the hosted voice-platform tests listed in `docs/TEST_PLAN.md` before final submission.
