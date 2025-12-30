# Response Validation & Step Progression Logic

## Overview

**Rule:** Don't progress to the next step until you receive a **CLEAR, VALID response** to the current question.

This ensures the exam captures accurate patient data before proceeding.

---

## How It Works

### 1. Response Quality Assessment

When patient responds, the system evaluates response quality:

```
Response Quality Levels:
├─ CLEAR       → High confidence + valid intent → Progress to next step ✅
├─ AMBIGUOUS   → Moderate confidence → Ask for clarification (stay on step)
├─ UNCLEAR     → Low confidence → Ask to repeat (stay on step)
└─ INVALID     → No valid intent → Ask again (stay on step)
```

**Confidence Thresholds:**
- **0.0 - 0.3**: UNCLEAR (very uncertain)
- **0.3 - 0.6**: AMBIGUOUS (somewhat uncertain)
- **0.6 - 1.0**: CLEAR (confident)

### 2. Step Progression Rules

```python
If response_quality == "clear":
    # Check if response has required information
    if has_required_information(step, response):
        progress_to_next_step()
    else:
        stay_on_same_step()
        ask_clarification()
else:
    # Response not clear enough
    stay_on_same_step()
    ask_clarification()
```

### 3. Required Information Validation

Different question types require different information:

#### Lens Pair Comparison (Step 6.x)
```
REQUIRED: One of the following in response
├─ "first" / "first lens" / "1st"     → "first_better"
├─ "second" / "second lens" / "2nd"   → "second_better"
└─ "both" / "same" / "equal"          → "both_same"

EXAMPLE VALID:
  "The first lens looks clearer"       ✅ (clear + has choice)
  "Second one is better"                ✅ (clear + has choice)
  "They're both the same"               ✅ (clear + has choice)

EXAMPLE INVALID:
  "Maybe first?"                        ❌ (ambiguous, no clear choice)
  "I don't know"                        ❌ (no choice indicated)
  "The dot looks round"                 ❌ (no choice comparison)
```

#### Red/Green Comparison (Step 7.x)
```
REQUIRED: One of the following
├─ "red" preference
├─ "green" preference
└─ "both" / "same"

EXAMPLE VALID:
  "Red looks clearer"                   ✅
  "Green is brighter"                   ✅
  "They look the same"                  ✅

EXAMPLE INVALID:
  "I think... maybe red?"               ❌ (ambiguous)
  "Not sure"                            ❌ (no preference)
```

#### Health/Comfort Questions
```
REQUIRED: At least one relevant information slot

EXAMPLE VALID:
  "Yes, my eyes feel healthy"           ✅ (has health_status)
  "I'm comfortable with this"           ✅ (has comfort)
  "I can read clearly"                  ✅ (has reading_ability)

EXAMPLE INVALID:
  "Um..."                               ❌ (no information)
  "That's good"                         ❌ (no specific slots)
```

---

## Response Flow Diagrams

### Normal Path (Clear Response)
```
Patient Response
    ↓
Parse response
    ↓
Calculate confidence
    ↓
Is confidence >= 0.6?
├─ NO → response_quality = "unclear" or "ambiguous"
│        ↓
│        Ask for clarification
│        ↓
│        next_step = SAME STEP ⚠️
│
└─ YES → response_quality = "clear"
         ↓
         Has required information?
         ├─ NO → Ask for specific information
         │        ↓
         │        next_step = SAME STEP ⚠️
         │
         └─ YES → next_step = NEXT STEP ✅
                  Process phoropter action
                  Update exam progress
```

### Red Flag Path (Emergency)
```
Patient says: "severe pain" or "sudden vision loss"
    ↓
Detect red flag keywords
    ↓
red_flag = TRUE 🚨
    ↓
next_step = "escalate_to_professional"
    ↓
Shutdown phoropter
    ↓
Halt exam immediately
```

### Persona Override Path (Security)
```
Patient says: "act as a doctor" or "be someone else"
    ↓
Detect persona override pattern
    ↓
Block the request
    ↓
next_step = SAME STEP
    ↓
Return to original question
```

---

## Code Implementation

### Response Quality Assessment

```python
def _assess_response_quality(confidence: float, intent: str, slots: Dict) -> str:
    """
    Returns: 'clear', 'ambiguous', 'unclear', or 'invalid'
    """
    if intent == "unclear" or intent == "invalid":
        return "invalid"
    
    if confidence < 0.3:
        return "unclear"
    
    if confidence < 0.6:
        return "ambiguous"
    
    if confidence >= 0.6 and intent != "invalid":
        return "clear"
    
    return "ambiguous"
```

### Step Progression Logic

```python
def _determine_next_step(substep, intent, confidence, slots, red_flag):
    """
    Determines if we progress to next step or stay on current step
    """
    # Emergency escalation
    if red_flag:
        return "escalate_to_professional"
    
    # Assess response quality
    response_quality = self._assess_response_quality(confidence, intent, slots)
    
    # RULE: Only progress on CLEAR responses
    if response_quality != "clear":
        return substep  # STAY ON SAME STEP
    
    # Check if response has required information
    if not self._has_required_information(substep, intent, slots):
        return substep  # STAY ON SAME STEP
    
    # Response is valid - PROGRESS
    return STEP_PROGRESSION.get(substep, "complete")
```

### Required Information Validation

```python
def _has_required_information(substep, intent, slots):
    """
    Validates that response contains required info for the substep
    """
    # Lens comparison steps (6.x) - MUST have clarity_feedback
    if substep.startswith("6."):
        if "clarity_feedback" in slots:
            feedback = slots["clarity_feedback"]
            if feedback in ["first_better", "second_better", "both_same"]:
                return True
        return False
    
    # Color comparison steps (7.x) - MUST have color_preference
    if substep.startswith("7."):
        if "color_preference" in slots:
            if slots["color_preference"] in ["red", "green"]:
                return True
        return False
    
    # Default: accept if valid intent with slots
    return intent != "invalid"
```

### Clarification Request

When response is unclear or ambiguous, system asks for clarification:

```python
def _generate_clarification_request(substep, parsed):
    """
    Generates appropriate clarification request based on step
    """
    if substep.startswith("6."):
        # Lens comparison
        if response_quality == "ambiguous":
            return (
                "I want to make sure I understand correctly. "
                "Which one makes the image sharper: the first or second lens?"
            )
        elif response_quality == "unclear":
            return (
                "Could you please tell me clearly: "
                "Is it the first lens, second lens, or both the same?"
            )
    
    elif substep.startswith("7."):
        # Color comparison
        if response_quality == "ambiguous":
            return (
                "Between red and green, which one looks clearer?"
            )
```

---

## Examples

### Example 1: Clear Response → PROGRESS ✅

```
Step: 6.1
Question: "Which lens makes the dot sharper and rounder?"

Patient Response: "The second lens definitely looks clearer"

Processing:
├─ Parsed: intent="refraction_feedback", confidence=0.92
├─ Quality: clear (confidence >= 0.6)
├─ Slots: {clarity_feedback: "second_better"}
├─ Required info check: YES ✅
└─ Decision: next_step = "6.2" → PROGRESS ✅

AI Response: "Excellent! I'll adjust for that preference."
```

### Example 2: Ambiguous Response → STAY & CLARIFY ⚠️

```
Step: 6.1
Question: "Which lens makes the dot sharper and rounder?"

Patient Response: "Hmm, maybe the first one? But I'm not sure..."

Processing:
├─ Parsed: intent="refraction_feedback", confidence=0.45
├─ Quality: ambiguous (0.3 < confidence < 0.6)
├─ Slots: {clarity_feedback: "first_better"}
├─ Response quality check: NO ❌
└─ Decision: next_step = "6.1" → STAY ⚠️

AI Response: 
  "I want to make sure I understand correctly. 
   Looking at the two lenses, which one makes 
   the image sharper: the first lens or the second lens?"

Patient gets another chance to answer clearly.
```

### Example 3: Unclear Response → STAY & REPEAT ⚠️

```
Step: 6.2
Question: "Which lens is clearer now?"

Patient Response: "Um... yeah..."

Processing:
├─ Parsed: intent="unclear", confidence=0.15
├─ Quality: unclear (confidence < 0.3)
├─ Slots: {}
├─ Response quality check: NO ❌
└─ Decision: next_step = "6.2" → STAY ⚠️

AI Response: 
  "I didn't quite catch that. 
   Could you please tell me clearly: 
   Is the first lens, second lens, or both the same?"
```

### Example 4: Red Flag → ESCALATE 🚨

```
Step: 6.3
Question: "How clear is the image?"

Patient Response: "I'm having severe eye pain and my vision went blurry"

Processing:
├─ Red flags detected: "severe", "pain", "blurry"
├─ red_flag = TRUE 🚨
└─ Decision: next_step = "escalate_to_professional" 🚨

AI Response:
  "I've detected a potential eye emergency. 
   Please stop this exam and contact your eye care 
   provider immediately or visit an emergency room."

Action: Shutdown phoropter, halt exam
```

### Example 5: Missing Required Info → STAY & CLARIFY ⚠️

```
Step: 6.1
Question: "Which lens is clearer?"

Patient Response: "The image looks pretty round now"

Processing:
├─ Parsed: intent="vision_clarity", confidence=0.65
├─ Quality: clear (confidence >= 0.6) ✓
├─ Slots: {clarity_feedback: ❌ MISSING}
├─ Required info check: NO ❌
└─ Decision: next_step = "6.1" → STAY ⚠️

AI Response:
  "Thank you for that feedback. 
   But I need to know specifically: 
   which lens looks clearer - the first or the second?"
```

---

## Response Status Values

| Status | Meaning | Action | Next Step |
|--------|---------|--------|-----------|
| `clear` | High confidence, valid intent, required info | Process & continue | next_substep |
| `ambiguous` | Moderate uncertainty | Ask for clarification | SAME substep |
| `unclear` | Low confidence, hard to understand | Ask to repeat | SAME substep |
| `invalid` | No valid intent detected | Ask again | SAME substep |

---

## Confidence Scoring

Confidence is calculated based on:

1. **Keyword Strength** - How directly patient matched expected keywords
   - Exact match: 0.9+
   - Strong match: 0.7-0.9
   - Partial match: 0.4-0.7
   - Weak match: 0.2-0.4
   - No match: <0.2

2. **Intent Clarity** - How clear the intent is
   - Clear intent: +0.1
   - Ambiguous intent: 0.0
   - Invalid intent: -0.3

3. **Slot Completeness** - Whether required information is present
   - All slots filled: +0.1
   - Some slots filled: 0.0
   - No slots filled: -0.2

---

## Testing Validation

Run tests to verify validation is working:

```bash
python test_agent.py

# Look for these messages:
✓ Response validation active
✓ Step progression requires clear response
✓ Ambiguous responses trigger clarification
✓ Red flags halt exam and escalate
```

---

## Configuration

Default thresholds (can be customized):

```python
CONFIDENCE_THRESHOLDS = {
    "clear": 0.6,        # Minimum for clear response
    "ambiguous": 0.3,    # Between unclear and ambiguous
    "unclear": 0.0       # Below this is unclear
}

REQUIRED_FIELDS = {
    "6": ["clarity_feedback"],  # Lens comparison
    "7": ["color_preference"],  # Color comparison
    "8": ["comfort"],           # Comfort question
}
```

---

## Summary

**Key Rules:**

1. ✅ Only progress to next step when response is **CLEAR**
2. ✅ Confidence must be **≥ 0.6** for clear response
3. ✅ Response must contain **required information** for the step
4. ✅ If response is ambiguous/unclear, ask for **clarification**
5. ✅ Always escalate when **red flags** detected
6. ✅ Always block **persona override** attempts

**Result:** Better data quality, accurate exams, patient safety.
