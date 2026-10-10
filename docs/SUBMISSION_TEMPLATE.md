# Hiring Assignment Submission Template

**Project:** Home Credit Loan Against Property (LAP) Qualification Voice Agent  
**Candidate:** `[Your name]`  
**Voice platform:** `[Retell AI / Bolna / other]`  
**Agent name / ID:** `[Actual configured agent identifier, if appropriate]`

## Deliverables

- **System prompt:** `prompts/system_prompt.md`
- **Public call recording and call log link:** `[Paste the actual hosted-platform share URL here]`
- **Happy-path audio + transcript:** `[Paste link / filename]`
- **Agricultural-property disqualification:** `[Paste link / filename]`
- **Cash-income disqualification:** `[Paste link / filename]`
- **Existing-loan / EMI-reduction route:** `[Paste link / filename]`
- **₹75 lakh cap confirmation:** `[Paste link / filename]`
- **Busy-customer callback path:** `[Paste link / filename]`
- **Out-of-order answer handling:** `[Paste link / filename]`

## Local verification

- Automated tests: `python -m unittest discover -s tests -v`
- Scenario runner: `python examples/run_scenarios.py`
- Automated results summary: `docs/TEST_RESULTS.md`

> Replace all bracketed fields only after running the actual voice-platform tests. Do not label local simulated transcripts as hosted audio or call logs.
