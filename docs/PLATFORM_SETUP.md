# Hosted Voice-Platform Setup Guide

The assignment permits Retell AI, Bolna, or a similar platform. These instructions stay at the workflow level because dashboard labels and trial capabilities can change.

Helpful official references:

- [Retell AI documentation](https://docs.retellai.com/)
- [Retell website/voice widget setup](https://docs.retellai.com/deploy/chat-widget) — official documentation explains that a voice agent can be created and used for voice/web calls; a web-call option can be useful for testing without calling real customers.
- [Bolna agent templates](https://docs.bolna.ai/agent-templates)
- [Bolna call updates and logs](https://docs.bolna.ai/poll-call-data)

## Step 1 — Create a test agent

1. Sign in to the platform you selected.
2. Create a new **voice agent** (not only a text chatbot).
3. Choose a supported conversational model, speech-to-text option, text-to-speech voice, and language.
4. Use a professional, clear English voice for the first pass. If you later test Hindi, update the language configuration and run the test matrix again.
5. Do not place calls to real customers. Use the platform's test/playground/web-call feature or an approved test number.

## Step 2 — Add the prompt

1. Open `prompts/system_prompt.md`.
2. Copy the full system prompt section into the platform's instruction/system-prompt field.
3. If the platform has a separate “first message” or “welcome message” field, set it to `Hello, may I speak with Rahul?` for the first test and ensure the model does not repeat the same greeting. Alternatively, let the system prompt generate the first message.
4. Enable an end-call/hang-up action if the platform requires an explicit action to end a call after a terminal response. Do not add a live human transfer tool unless you specifically need it; the written assignment asks the agent to tell the customer that a senior expert will call back and then end the current call.

## Step 3 — Configure the runtime variables

Use the platform's supported dynamic variables, or substitute test values directly for your first run. Example values:

| Variable | Test value |
|---|---|
| `company_name` | `Home Credit` |
| `customer_name` | `Rahul` |
| `agent_name` | `Asha` |
| `agent_gender` | `female` |
| `current_date` | Today's date in the platform timezone |
| `current_day` | Today's weekday in the platform timezone |
| `current_time` | Current local time in the platform timezone |
| `additional_context_from_rag` | `No additional product details provided. The exact interest rate and branch locations are unavailable in this test.` |
| `language_to_speak` | `English` |
| `conversation_history` | The running call transcript/history, if platform supports it |
| `customer_utterance` | The latest recognized customer utterance, if platform supports it |

The required assignment variables are included in the prompt. Actual variable interpolation is platform-specific; `{{variable}}` should not be assumed to work unchanged on every platform.

## Step 4 — Test before recording

Start with the scenarios in `docs/TEST_PLAN.md`. At minimum test:

1. Happy path: valid values for every item.
2. Agricultural property: verify immediate disqualification.
3. Cash income: verify immediate disqualification.
4. Existing property loan / EMI reduction: verify specialist message and end.
5. ₹90 lakh request: verify the agent asks whether ₹75 lakh works, rather than rejecting immediately.
6. Busy customer: verify callback preference capture.
7. Out-of-order answers: verify facts are remembered and not asked again.
8. Diversion: ask the interest rate midway and verify that no rate is fabricated.
9. Missing original documents and tenure 2 / 16 years.
10. All seven checklist items: verify the handoff happens only after the last item has been captured.

Speak naturally during tests: use fillers, interrupt the agent, correct a prior answer, and provide two or three eligibility facts in one sentence. Inspect the actual transcript and listen to the audio; a prompt that looks correct on paper can still perform poorly with speech transcription or turn-taking.

## Step 5 — Capture actual recordings and call logs

1. Run the tests through the hosted platform so it creates real test-call records.
2. Save/export the actual audio recording and transcript/log for each useful scenario.
3. Use clear filenames, such as `01_happy_path`, `02_agricultural_property`, `03_cash_income`, `04_existing_loan`, `05_amount_cap`, `06_busy_customer`, and `07_out_of_order`.
4. Check that the recording and transcript correspond to the same call and that the transcript reflects the audio.
5. Create the platform's shareable/public link if supported, or upload the permitted files to an accessible storage location and configure view access according to the assignment instructions.
6. Test the link in a private/incognito browser window before submitting it.

Only real hosted-platform call records satisfy the assignment's audio + transcript deliverable. Files produced by `python examples/run_scenarios.py` are explicitly simulated text artifacts, useful for testing but not a substitute for hosted recordings.

## Step 6 — Final submission

Submit:

- the system prompt (`prompts/system_prompt.md`);
- public link to the actual call recording and call logs;
- test audio recordings and transcripts for multiple scenarios;
- optional architecture/test-plan documents from this repository.

Do not include private API keys, account credentials, real customer PII, or phone numbers in GitHub. The `.gitignore` excludes locally saved call-session outputs by default.
