# Home Credit LAP AI Voice Agent

A small, submission-ready reference project for the **AI Intern / Prompt Engineer Voice Agent Design** assignment. It implements the required conversation rules in a platform-ready system prompt, a local state-machine simulator, 36 automated regression tests, and 15 end-to-end simulated scenarios.

> **Important boundary:** This repository does not create a hosted voice agent, place telephone calls, or generate genuine platform audio recordings. The local simulator is text-only and runs without API keys. Use the platform-ready prompt in Retell AI, Bolna, or a similar platform to create the actual voice demonstration and public recording/log link required by the assignment.

## Project contents

```text
home_credit_lap_voice_agent/
├── README.md
├── requirements.txt
├── .gitignore
├── lap_voice_agent/
│   ├── __init__.py
│   ├── models.py             # Qualification state and checklist order
│   ├── extractor.py          # Rule-based extraction for local regression tests
│   ├── engine.py             # Conversation state machine and business rules
│   └── cli.py                # Interactive local text simulation
├── prompts/
│   └── system_prompt.md      # Full prompt to paste into the voice platform
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ELIGIBILITY_RULES.md
│   ├── TEST_PLAN.md
│   └── PLATFORM_SETUP.md
├── tests/
│   └── test_engine.py        # Automated unit/regression tests
├── examples/
│   └── run_scenarios.py      # 15 simulated scenarios
└── outputs/                  # Generated test results/transcripts
```

## 1. Requirements

- Python 3.10 or newer.
- No third-party Python package is required for local tests or simulation.
- For the real voice demonstration, an account on a supported voice-agent platform (for example Retell AI or Bolna) is required. Platform features, trials, phone-number availability, and pricing are managed by the provider.

## 2. Setup on Windows 10/11 (PowerShell)

Open PowerShell and move into the extracted project folder:

```powershell
cd path\to\home_credit_lap_voice_agent
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The requirements file intentionally has no external packages. If PowerShell blocks virtual-environment activation, run the project's commands using `\.venv\Scripts\python.exe` instead.

### Run the local simulator

```powershell
python -m lap_voice_agent.cli
```

Enter a customer name or press Enter for the default `Rahul`. Reply to each agent turn as if you were the customer. Type `quit` to stop. After the session, the simulator saves a local text transcript and JSON state export under `outputs/`.

### Run automated tests

```powershell
python -m unittest discover -s tests -v
```

Expected result: all 36 tests pass.

### Run end-to-end scenario simulations

```powershell
python examples/run_scenarios.py
```

The runner tests 15 scenarios and creates:

- `outputs/scenario_results.json`
- `outputs/scenario_transcripts.md`

These are **simulated text transcripts**, not genuine voice recordings or hosted call logs.

## 3. Setup on Ubuntu / macOS

From the project directory:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m lap_voice_agent.cli
python -m unittest discover -s tests -v
python examples/run_scenarios.py
```

## 4. The system prompt

Open `prompts/system_prompt.md`. It includes all runtime variables required by the assignment:

- `company_name`
- `customer_name`
- `agent_name`
- `agent_gender`
- `current_date`, `current_day`, `current_time`
- `additional_context_from_rag`
- `language_to_speak`
- `conversation_history`
- `customer_utterance`

The `{{...}}` form is a template placeholder convention for this project. Map it to the syntax supported by your selected platform. If the platform does not support a particular dynamic variable, substitute an explicit test value for the demonstration. Do not deploy with unresolved placeholders.

## 5. Business logic implemented

- Identity check before discussing the offer.
- Busy-customer callback branch.
- Fresh-loan versus existing-property-loan / EMI-reduction branch.
- Seven checklist items in the required order (occupation + income mode are two fields within item 5).
- Out-of-order answer capture and same-utterance corrections.
- Immediate disqualification for agricultural property, unavailable original documents, cash income, and tenure outside 3–15 years.
- ₹75 lakh cap confirmation rather than automatically rejecting a first request over the cap.
- No invented minimum market value and no fabricated interest rate.
- Final handoff gate that blocks preliminary qualification until every checklist item is answered.

See `docs/ELIGIBILITY_RULES.md` for the decision table and boundary cases.

## 6. Run the real voice demonstration

Follow [`docs/PLATFORM_SETUP.md`](docs/PLATFORM_SETUP.md). The short version is: create a voice agent on your chosen platform, paste the full prompt, map the variables, choose a supported voice, test the scenario matrix, then export/share the **actual** audio recordings and call logs/transcripts.

Do not use real customer information for assignment tests. Use a test identity and your own/approved test number. Check privacy and recording rules that apply to your test setup.

## 7. Submission checklist

- [x] Full platform-ready system prompt.
- [x] Local project with setup/run instructions.
- [x] Eligibility/business decision table.
- [x] Unit tests and scenario runner.
- [x] Architecture and test-plan notes.
- [x] Local validation report (36 unit tests + 15 simulated scenarios).
- [ ] Actual voice-platform calls, audio recordings, and transcripts.
- [ ] Public link to actual call recording and logs from the hosted platform.

The last two items require you to create and test the agent in a platform account. This project deliberately does not label simulated transcripts as actual call recordings.
