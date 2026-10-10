# Simulated Scenario Transcripts

**Important:** These are local text simulations, not real voice-platform recordings.


## happy_path_all_information_at_once — PASS

Expected: `PRELIMINARILY_QUALIFIED`  
Actual: `PRELIMINARILY_QUALIFIED`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, this is Rahul, speaking.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: This is a fresh loan. It's a residential house, jointly owned with my wife, the original property documents are available, I need ₹50 lakh, I'm salaried and the income comes to my bank account, the property is worth around ₹1 crore, and I'd prefer 10 years.
AGENT: Thank you for answering all the questions. Based on this preliminary check, your details meet the criteria for this offer. A senior loan expert will contact you shortly to discuss the next steps and provide the exact interest rate. This is not final loan approval. Thank you, and have a good day.
```


## agricultural_property — PASS

Expected: `NOT_ELIGIBLE`  
Actual: `NOT_ELIGIBLE`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, this is Rahul.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: Fresh loan. The property is agricultural land.
AGENT: Thank you for clarifying. Based on the criteria for this specific offer, you do not meet the eligibility requirements at this time. I appreciate your time. Goodbye.
```


## cash_income — PASS

Expected: `NOT_ELIGIBLE`  
Actual: `NOT_ELIGIBLE`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, I'm Rahul.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: Fresh loan.
AGENT: To start, what type of property do you own: residential, commercial, or industrial?
CUSTOMER: It's residential, I am self-employed, and most of my income comes in cash.
AGENT: Thank you for clarifying. Based on the criteria for this specific offer, you do not meet the eligibility requirements at this time. I appreciate your time. Goodbye.
```


## original_documents_unavailable — PASS

Expected: `NOT_ELIGIBLE`  
Actual: `NOT_ELIGIBLE`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, speaking.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: This is a fresh loan.
AGENT: To start, what type of property do you own: residential, commercial, or industrial?
CUSTOMER: It's a residential house and I only have photocopies, not the originals.
AGENT: Thank you for clarifying. Based on the criteria for this specific offer, you do not meet the eligibility requirements at this time. I appreciate your time. Goodbye.
```


## tenure_below_three_years — PASS

Expected: `NOT_ELIGIBLE`  
Actual: `NOT_ELIGIBLE`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, this is Rahul.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: Fresh loan. I would like to repay it in 2 years.
AGENT: Thank you for clarifying. Based on the criteria for this specific offer, you do not meet the eligibility requirements at this time. I appreciate your time. Goodbye.
```


## tenure_above_fifteen_years — PASS

Expected: `NOT_ELIGIBLE`  
Actual: `NOT_ELIGIBLE`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, speaking.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: This is a new loan. I'd prefer a 16-year tenure.
AGENT: Thank you for clarifying. Based on the criteria for this specific offer, you do not meet the eligibility requirements at this time. I appreciate your time. Goodbye.
```


## over_limit_accept_cap — PASS

Expected: `PRELIMINARILY_QUALIFIED`  
Actual: `PRELIMINARILY_QUALIFIED`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, speaking.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: This is a fresh loan, and I need ₹90 lakh.
AGENT: The current offer is available for up to ₹75 lakh. Would you like to proceed with the maximum eligible amount of ₹75 lakh?
CUSTOMER: Yes, ₹75 lakh will work.
AGENT: To start, what type of property do you own: residential, commercial, or industrial?
CUSTOMER: Residential house, sole owned, original documents are available, I'm salaried and paid through my bank, property worth ₹1 crore, 10 years.
AGENT: Thank you for answering all the questions. Based on this preliminary check, your details meet the criteria for this offer. A senior loan expert will contact you shortly to discuss the next steps and provide the exact interest rate. This is not final loan approval. Thank you, and have a good day.
```


## over_limit_declined — PASS

Expected: `AMOUNT_LIMIT_DECLINED`  
Actual: `AMOUNT_LIMIT_DECLINED`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, this is Rahul.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: Fresh loan; I need ₹90 lakh.
AGENT: The current offer is available for up to ₹75 lakh. Would you like to proceed with the maximum eligible amount of ₹75 lakh?
CUSTOMER: No, I cannot proceed with ₹75 lakh.
AGENT: I understand. The current offer has a maximum amount of ₹75 lakh, so I won't continue the qualification. Thank you for your time. Goodbye.
```


## existing_loan_transfer_path — PASS

Expected: `LOAN_TRANSFER_SPECIALIST`  
Actual: `LOAN_TRANSFER_SPECIALIST`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, this is Rahul.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: I already have a loan against this property.
AGENT: Thank you for clarifying. Since this involves an existing property loan or EMI reduction, a loan-transfer specialist will contact you to discuss the appropriate options. Thank you for your time. Goodbye.
```


## emi_reduction_transfer_path — PASS

Expected: `LOAN_TRANSFER_SPECIALIST`  
Actual: `LOAN_TRANSFER_SPECIALIST`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, speaking.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: I want to reduce my current EMI.
AGENT: Thank you for clarifying. Since this involves an existing property loan or EMI reduction, a loan-transfer specialist will contact you to discuss the appropriate options. Thank you for your time. Goodbye.
```


## busy_customer_callback — PASS

Expected: `CALLBACK_REQUESTED`  
Actual: `CALLBACK_REQUESTED`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: I'm busy right now, please call tomorrow at 4 PM.
AGENT: Certainly. I'll note your preferred callback time as tomorrow at 4 PM. Thank you for your time. Goodbye.
```


## out_of_order_information — PASS

Expected: `PRELIMINARILY_QUALIFIED`  
Actual: `PRELIMINARILY_QUALIFIED`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, it's Rahul.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: It's a fresh loan.
AGENT: To start, what type of property do you own: residential, commercial, or industrial?
CUSTOMER: It's a residential property worth ₹80 lakh, jointly owned with my brother.
AGENT: Are the original property documents available for verification? You do not need to hold them during this call.
CUSTOMER: Original papers are available at home.
AGENT: Approximately how much would you like to borrow under this offer? The maximum available is ₹75 lakh.
CUSTOMER: I need ₹30 lakh.
AGENT: Are you salaried or self-employed, and is your income received through a bank account or in cash?
CUSTOMER: Self-employed, and income is received in my bank account.
AGENT: What repayment tenure would you prefer, in years? The available range is 3 to 15 years.
CUSTOMER: I'd like to repay in 5 years.
AGENT: Thank you for answering all the questions. Based on this preliminary check, your details meet the criteria for this offer. A senior loan expert will contact you shortly to discuss the next steps and provide the exact interest rate. This is not final loan approval. Thank you, and have a good day.
```


## rate_question_diversion — PASS

Expected: `ACTIVE_CONTINUATION`  
Actual: `ACTIVE_CONTINUATION`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, this is Rahul.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: Fresh loan.
AGENT: To start, what type of property do you own: residential, commercial, or industrial?
CUSTOMER: Residential property.
AGENT: Is the property solely owned by you, or is it jointly owned with someone else?
CUSTOMER: What is your interest rate?
AGENT: The exact interest rate will be provided by a senior loan expert after this preliminary qualification. I don't want to give you an unconfirmed rate. Is the property solely owned by you, or is it jointly owned with someone else?
```


## wrong_person_privacy_gate — PASS

Expected: `WRONG_PERSON`  
Actual: `WRONG_PERSON`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Wrong number, I'm not Rahul.
AGENT: I apologize for the inconvenience. I'll end the call here. Goodbye.
```


## cash_corrected_to_bank_in_same_turn — PASS

Expected: `PRELIMINARILY_QUALIFIED`  
Actual: `PRELIMINARILY_QUALIFIED`

```text
AGENT: Hello, may I speak with Rahul?
CUSTOMER: Yes, speaking.
AGENT: Thank you for confirming. I'm Asha from Home Credit. We're reaching out because, as one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few brief questions to check whether this offer may suit you. First, is this a fresh loan requirement, or do you already have a loan on this property or want to reduce an existing EMI?
CUSTOMER: Fresh loan.
AGENT: To start, what type of property do you own: residential, commercial, or industrial?
CUSTOMER: Residential property, sole owner, original documents at home, I need ₹25 lakh, and I am salaried. My income is cash—sorry, actually it is credited to my bank account. Property is worth ₹70 lakh, and I want 7 years.
AGENT: Thank you for answering all the questions. Based on this preliminary check, your details meet the criteria for this offer. A senior loan expert will contact you shortly to discuss the next steps and provide the exact interest rate. This is not final loan approval. Thank you, and have a good day.
```
