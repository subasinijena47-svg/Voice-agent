"""Small dependency-free, rule-based extractor for the local demonstration.

The production voice platform's language model should use prompts/system_prompt.md
for flexible language understanding. This extractor makes the local simulation
and its regression tests runnable without API keys or external services.
"""
from __future__ import annotations

import re
from typing import Any


NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
    "ninety": 90,
}


def _words_to_number(phrase: str) -> int | None:
    phrase = phrase.lower().replace("-", " ")
    words = [w for w in re.split(r"\s+", phrase.strip()) if w and w != "and"]
    if not words:
        return None
    total = 0
    current = 0
    for word in words:
        if word in NUMBER_WORDS:
            current += NUMBER_WORDS[word]
        elif word == "hundred":
            current = max(current, 1) * 100
        elif word in {"thousand", "lakh", "lakhs", "lac", "lacs", "crore", "crores"}:
            scale = 1_000 if word == "thousand" else 100_000 if word in {"lakh", "lakhs", "lac", "lacs"} else 10_000_000
            total += max(current, 1) * scale
            current = 0
        else:
            return None
    return total + current


def _amount_to_rupees(number: float, unit: str | None) -> int:
    unit = (unit or "").lower().rstrip("s")
    if unit in {"crore", "cr"}:
        return int(number * 10_000_000)
    if unit in {"lakh", "lac", "l"}:
        return int(number * 100_000)
    if unit in {"thousand", "k"}:
        return int(number * 1_000)
    return int(number)


_NUMERIC_AMOUNT_RE = re.compile(
    r"(?<![\w.])(?:₹\s*|rs\.?\s*|inr\s*)?"
    r"(?P<number>\d[\d,]*(?:\.\d+)?)\s*"
    r"(?P<unit>crores?|cr|lakhs?|lacs?|lac|l\b|thousand|k\b)?(?!\w)",
    re.IGNORECASE,
)
_WORD_AMOUNT_RE = re.compile(
    r"\b(?P<words>(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)"
    r"(?:[\s-]+(?:and[\s-]+)?(?:zero|one|two|three|four|five|six|seven|eight|nine|"
    r"ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred))*?)"
    r"\s+(?P<unit>crores?|cr|lakhs?|lacs?|lac|l\b|thousand)\b",
    re.IGNORECASE,
)


def _amount_mentions(text: str) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    for match in _NUMERIC_AMOUNT_RE.finditer(text):
        raw_num = match.group("number").replace(",", "")
        unit = match.group("unit")
        raw_span = match.span()
        # Ignore plain small numbers unless their nearby words make them an amount.
        nearby = text[max(0, raw_span[0] - 16): min(len(text), raw_span[1] + 18)].lower()
        has_currency = bool(re.search(r"₹|\brs\.?\b|\binr\b", text[max(0, raw_span[0] - 5):raw_span[0] + 1], re.I))
        try:
            value = float(raw_num)
        except ValueError:
            continue
        if not unit and not has_currency and value < 10_000:
            continue
        mentions.append({"start": match.start(), "end": match.end(), "rupees": _amount_to_rupees(value, unit), "raw": match.group(0), "unit": unit})
        occupied.append(raw_span)

    for match in _WORD_AMOUNT_RE.finditer(text):
        if any(match.start() < end and match.end() > start for start, end in occupied):
            continue
        value = _words_to_number(match.group("words"))
        if value is None:
            continue
        mentions.append({"start": match.start(), "end": match.end(), "rupees": _amount_to_rupees(value, match.group("unit")), "raw": match.group(0), "unit": match.group("unit")})
    return sorted(mentions, key=lambda x: x["start"])


LOAN_CUES = re.compile(r"\b(?:need|want|looking for|require|borrow|loan amount|loan of|take out|take a loan|for a loan|funding|apply for)\b", re.I)
MARKET_CUES = re.compile(r"\b(?:market value|property value|worth|valued at|valuation|value of (?:the )?property|property is worth|house is worth|property is (?:around|approximately|estimated at)|house is (?:around|approximately|estimated at))\b", re.I)


def _cue_distance(text: str, mention_start: int, mention_end: int, pattern: re.Pattern[str]) -> int | None:
    distances: list[int] = []
    for match in pattern.finditer(text):
        if match.end() <= mention_start and mention_start - match.end() <= 55:
            distances.append(mention_start - match.end())
        elif match.start() >= mention_end and match.start() - mention_end <= 32:
            distances.append(match.start() - mention_end)
    return min(distances) if distances else None


def _classify_amount(mention: dict[str, Any], text: str, preferred_group: str | None) -> str | None:
    loan_dist = _cue_distance(text, mention["start"], mention["end"], LOAN_CUES)
    market_dist = _cue_distance(text, mention["start"], mention["end"], MARKET_CUES)
    if loan_dist is not None and (market_dist is None or loan_dist < market_dist):
        return "loan_amount"
    if market_dist is not None:
        return "market_value"
    if preferred_group == "loan_amount":
        return "loan_amount"
    if preferred_group == "market_value":
        return "market_value"
    return None


def _last_categorized_match(text: str, patterns: list[tuple[str, str]]) -> str | None:
    matches: list[tuple[int, str]] = []
    lowered = text.lower()
    for pattern, value in patterns:
        for match in re.finditer(pattern, text, re.I):
            # Ignore a label directly negated by phrases such as "not agricultural"
            # or "not salaried". The next clear positive label, if any, wins.
            prefix = lowered[max(0, match.start() - 22):match.start()]
            if re.search(r"\b(?:not|isn't|is not|never|no)\s+(?:(?:an?|the)\s+)?$", prefix):
                continue
            matches.append((match.start(), value))
    return max(matches, key=lambda item: item[0])[1] if matches else None


def _extract_property_type(text: str) -> str | None:
    return _last_categorized_match(text, [
        (r"\bagricultur\w*\b|\bfarm\s*land\b|\bfarm\b|\bkheti\b", "agricultural"),
        (r"\bresidential\b|\bhouse\b|\bflat\b|\bapartment\b|\bmy home\b|\bghar\b", "residential"),
        (r"\bcommercial\b|\bshop\b|\boffice\b|\bretail unit\b", "commercial"),
        (r"\bindustrial\b|\bfactory\b|\bmanufacturing unit\b", "industrial"),
    ])


def _extract_ownership(text: str) -> str | None:
    return _last_categorized_match(text, [
        (r"\bjoint(?:ly)?(?:[- ]owned| ownership| property)?\b|\bco[- ]?owner\b|\bshared ownership\b|\bwith my (?:wife|husband|brother|sister|father|mother|partner|family|friend)\b", "joint"),
        (r"\bsole(?:ly)?[- ]owned\b|\bsole owner\b|\bsole ownership\b|\bsingle owner\b|\bonly owner\b|\bmy own (?:property|house|home|flat|shop)\b|\bowned only by me\b", "sole"),
    ])


def _extract_documents(text: str) -> bool | None:
    lowered = text.lower()
    if not re.search(r"\b(originals?|documents?|papers?|photocopies|copies)\b", lowered):
        return None
    events: list[tuple[int, bool]] = []
    false_patterns = [
        r"\bonly\s+(?:have\s+)?photocopies\b",
        r"\b(?:no|without|lost|missing|unavailable)\s+(?:the\s+)?(?:originals?|original\s+(?:property\s+)?(?:documents?|papers?)|documents?|papers?)\b",
        r"\bnot\s+(?:the\s+)?originals?\b",
        r"\b(?:originals?|original\s+(?:property\s+)?(?:documents?|papers?))\s+(?:are\s+)?unavailable\b",
        r"\b(?:don't|dont|do not|haven't|have not)\s+(?:got\s+)?(?:the\s+)?(?:originals?|original\s+(?:property\s+)?(?:documents?|papers?)|documents?|papers?)\b",
        r"\b(?:originals?|original\s+(?:property\s+)?(?:documents?|papers?)|documents?|papers?)\s+(?:are\s+)?(?:not available|missing|lost)\b",
    ]
    true_patterns = [
        r"\b(?:originals?|original\s+(?:property\s+)?(?:documents?|papers?))\b.{0,28}\b(?:available|at home|ready|with me|at the bank|with the bank)\b",
        r"\b(?:have|got|keep)\b.{0,22}\b(?:the\s+)?(?:originals?|original\s+(?:property\s+)?(?:documents?|papers?))\b",
        r"\b(?:documents?|papers?)\b.{0,20}\b(?:originals?|at home|available|ready)\b",
        r"\b(?:originals?|papers?|documents?)\b.{0,18}\b(?:are|are kept)\b.{0,12}\b(?:at home|with the bank|at the bank)\b",
    ]
    for pattern in false_patterns:
        for match in re.finditer(pattern, lowered, re.I):
            events.append((match.start(), False))
    for pattern in true_patterns:
        for match in re.finditer(pattern, lowered, re.I):
            matched_text = match.group(0)
            # "I have photocopies, not the originals" must not count as having originals.
            if re.search(r"\b(?:photocopies|copies)\b", matched_text) and re.search(r"\b(?:have|got)\b", matched_text):
                continue
            events.append((match.start(), True))
    # Handle "not with me, but at home": availability matters, not physical possession.
    if re.search(r"\b(?:at home|with the bank|at the bank)\b", lowered) and re.search(r"\b(originals?|documents?|papers?)\b", lowered):
        home_match = list(re.finditer(r"\b(?:at home|with the bank|at the bank)\b", lowered))[-1]
        events.append((home_match.start(), True))
    return max(events, key=lambda item: item[0])[1] if events else None


def _extract_occupation(text: str) -> str | None:
    return _last_categorized_match(text, [
        (r"\bself[- ]employed\b|\bbusiness owner\b|\brun(?:s|ning)?\s+(?:my|a|the)\s+business\b|\bown business\b|\bentrepreneur\b", "self-employed"),
        (r"\bsalaried\b|\bsalary\b|\bemployee\b|\bI have a job\b|\bwork(?:ing)? for (?:a |the )?company\b", "salaried"),
    ])


def _extract_income_mode(text: str) -> str | None:
    lowered = text.lower()
    events: list[tuple[int, str, bool]] = []
    for match in re.finditer(r"\bbank(?:\s+account|\s+transfer|ing)?\b|\baccount\b", lowered):
        prefix = lowered[max(0, match.start()-20):match.start()]
        negated = bool(re.search(r"\b(?:no|not|never|don't|dont|do not|isn't|is not)\s+(?:received\s+)?(?:in\s+)?$", prefix))
        events.append((match.start(), "bank", negated))
    for match in re.finditer(r"\bcash(?:\s+in[- ]hand)?\b", lowered):
        prefix = lowered[max(0, match.start()-24):match.start()]
        negated = bool(re.search(r"\b(?:no|not|never|don't|dont|do not|isn't|is not|without)\s+(?:received\s+)?(?:in\s+)?$", prefix))
        events.append((match.start(), "cash", negated))
    if not events:
        return None

    positive_cash = any(mode == "cash" and not negated for _, mode, negated in events)
    positive_bank = any(mode == "bank" and not negated for _, mode, negated in events)
    # If cash and bank are both stated without a clear correction, treat this as
    # mixed income: the assignment requires income to be received through a bank.
    correction = re.search(r"\b(?:actually|sorry|i mean|rather|instead|but now|correction)\b", lowered)
    if positive_cash and positive_bank:
        if correction:
            values_after_correction = [e for e in events if e[0] > correction.start() and not e[2]]
            if values_after_correction:
                return max(values_after_correction, key=lambda e: e[0])[1]
        return "cash"

    # A negated cash mention plus a clear bank/account mention means bank mode.
    if any(mode == "cash" and negated for _, mode, negated in events) and positive_bank:
        return "bank"
    # A negated bank mention plus a clear cash mention means cash mode.
    if any(mode == "bank" and negated for _, mode, negated in events) and positive_cash:
        return "cash"
    positives = [e for e in events if not e[2]]
    return max(positives, key=lambda e: e[0])[1] if positives else None


def _extract_tenure(text: str) -> int | None:
    lowered = text.lower()
    candidates: list[tuple[int, int]] = []
    numeric_patterns = [
        re.compile(r"(?<!\w)(\d{1,2})\s*-?\s*(?:years?|yrs?|yr\b)", re.I),
        re.compile(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\s*(?:years?|yrs?|yr\b)", re.I),
    ]
    for pattern in numeric_patterns:
        for match in pattern.finditer(lowered):
            prefix = lowered[max(0, match.start()-12):match.start()]
            # Do not mistake the upper end of "3 to 15 years" / "3-15 years" for a request.
            if re.search(r"\b\d{1,2}\s*(?:-|to)\s*$", prefix):
                continue
            val = int(match.group(1)) if match.group(1).isdigit() else NUMBER_WORDS.get(match.group(1), None)
            if val is not None:
                candidates.append((match.start(), val))
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


def extract_facts(text: str, preferred_group: str | None = None) -> dict[str, Any]:
    """Extract all recognizable eligibility facts from one customer utterance."""
    facts: dict[str, Any] = {}
    property_type = _extract_property_type(text)
    ownership = _extract_ownership(text)
    documents = _extract_documents(text)
    occupation = _extract_occupation(text)
    income_mode = _extract_income_mode(text)
    tenure = _extract_tenure(text)

    if property_type:
        facts["property_type"] = property_type
    if ownership:
        facts["ownership_status"] = ownership
    if documents is not None:
        facts["documents_available"] = documents
    if occupation:
        facts["occupation"] = occupation
    if income_mode:
        facts["income_mode"] = income_mode
    if tenure is not None:
        facts["tenure_years"] = tenure

    for mention in _amount_mentions(text):
        kind = _classify_amount(mention, text, preferred_group)
        if kind == "loan_amount":
            facts["loan_amount_rupees"] = mention["rupees"]
            facts["requested_loan_amount_rupees"] = mention["rupees"]
        elif kind == "market_value":
            facts["market_value_rupees"] = mention["rupees"]
            facts["market_value_note"] = f"Approximately ₹{mention['rupees']:,}"
            facts["market_value_answered"] = True

    if not facts.get("market_value_answered") and re.search(
        r"\b(?:not sure|don't know|dont know|do not know|no idea|can't estimate|cannot estimate|unable to estimate)\b",
        text, re.I,
    ) and (preferred_group == "market_value" or re.search(r"\b(?:market value|property value|worth)\b", text, re.I)):
        facts["market_value_note"] = "Customer unable to estimate during call"
        facts["market_value_answered"] = True

    return facts


def detect_busy(text: str) -> bool:
    return bool(re.search(
        r"\b(?:i'm busy|i am busy|currently busy|in a meeting|driving right now|"
        r"can't talk|cannot talk|not a good time|call me back|call back later|"
        r"please call later|busy right now|have to go|need to leave)\b",
        text, re.I,
    ))


def extract_callback_time(text: str) -> str | None:
    cleaned = " ".join(text.strip().split())
    patterns = [
        r"\b(?:tomorrow|today|this evening|this afternoon|after lunch|in the morning|next week)\b(?:\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?",
        r"\b(?:at|around|after|before)\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)\b",
        r"\b(?:at|around)\s+\d{1,2}\s*(?:o'clock)\b",
        r"\b(?:in|after)\s+\d+\s+(?:minutes?|hours?)\b",
    ]
    matches = []
    for pattern in patterns:
        match = re.search(pattern, cleaned, re.I)
        if match:
            matches.append(match.group(0))
    return matches[0] if matches else None


def detect_verified(text: str) -> bool | None:
    lowered = text.lower()
    if re.search(r"\b(?:wrong number|not (?:the customer|him|her|me|that person)|he isn't here|she isn't here|you have the wrong|no,? this isn't|i am not)\b", lowered):
        return False
    if re.search(r"\b(?:yes|yeah|yep|speaking|this is (?:me|[a-z]+)|that's me|that is me|you are speaking to|correct person|it's me|it is me)\b", lowered):
        return True
    return None


def detect_transfer_request(text: str) -> bool:
    # Route only property-loan / EMI-reduction cases; an unrelated personal loan
    # mentioned in passing should not trigger the specialist branch.
    patterns = [
        r"\balready have (?:an? )?(?:existing )?(?:property )?loan\b.{0,28}\b(?:against|on|for) (?:the|this|my) (?:property|house|flat|home)\b",
        r"\b(?:existing|current|outstanding) loan (?:on|against|for) (?:the|this|my) (?:property|house|flat|home)\b",
        r"\b(?:existing|current|outstanding) (?:property|housing|home|mortgage) loan\b",
        r"\bloan against (?:the|this|my) property\b.{0,20}\b(?:already|existing|current|outstanding)\b",
        r"\b(?:balance transfer|transfer my loan|want to transfer (?:my |the )?loan|looking to transfer (?:my |the )?loan|need a loan transfer)\b",
        r"\b(?:reduce|lower|decrease) (?:(?:my|the|current) ){0,2}emi\b",
        r"\bemi reduction\b|\bwant a lower emi\b",
    ]
    lowered = text.lower()
    for pattern in patterns:
        for match in re.finditer(pattern, lowered, re.I):
            prefix = lowered[max(0, match.start()-32):match.start()]
            if re.search(r"\b(?:don't|dont|do not|no|never|not)\b[^.!?,;]{0,28}$", prefix):
                continue
            return True
    return False


def detect_fresh_loan(text: str) -> bool:
    return bool(re.search(
        r"\b(?:fresh loan|new loan|first loan|no existing loan|don't have an? (?:existing )?loan|"
        r"do not have an? (?:existing )?loan|not an? existing loan|no,? i don't have (?:one|a loan))\b",
        text, re.I,
    ))


def detect_interest_rate_question(text: str) -> bool:
    return bool(re.search(r"\b(?:interest rate|rate of interest|what rate|how much interest|roi)\b", text, re.I))


def detect_branch_question(text: str) -> bool:
    return bool(re.search(r"\b(?:nearest branch|branch near|where is your branch|branch address)\b", text, re.I))


def detect_decline(text: str) -> bool:
    return bool(re.search(r"\b(?:not interested|no thanks|don't want to proceed|do not want to proceed|i decline|stop calling|remove my number)\b", text, re.I))


def detect_yes(text: str) -> bool:
    return bool(re.search(r"\b(?:yes|yeah|yep|sure|okay|ok|proceed|that works|i agree|go ahead)\b", text, re.I))


def detect_no(text: str) -> bool:
    return bool(re.search(r"\b(?:no|nope|not interested|can't|cannot|do not|don't|won't|will not)\b", text, re.I))
