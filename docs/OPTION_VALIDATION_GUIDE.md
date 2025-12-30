# Option Validation & Input Handling Guide

## Overview

When a question has **predefined options** (1-4 or text choices), the system now validates that the patient selects a **VALID option only**. Invalid inputs are rejected and the question is asked again.

---

## Validation Rules

### Rule 1: Only Accept Valid Option Numbers

```
Question: "Which lens is clearer?"
Options: 1. First lens  2. Second lens  3. Both same  4. Neither clear

✅ VALID:     Patient says: 1, 2, 3, or 4
❌ INVALID:   Patient says: 5, 6, 7, -1, 0, 99
```

**What happens with invalid number:**
```
Patient: 5
❌ Invalid option. Please select 1 to 4, or type one of the options:
  1. First lens
  2. Second lens
  3. Both same
  4. Neither clear

Patient: [Asked to try again]
```

### Rule 2: Accept Exact Text Matches (Case-Insensitive)

```
Question: "Which one do you prefer?"
Options: 1. Hello  2. Hi  3. Good morning  4. Ready to start

✅ VALID:     Patient says: "hello", "Hello", "HELLO"
✅ VALID:     Patient says: "hi", "Hi", "HI"
✅ VALID:     Patient says: "ready to start", "Ready to Start"
❌ INVALID:   Patient says: "hellooo", "hey", "good afternoon"
```

**What happens with text match:**
```
Patient: Hello
✅ Accepted! (matches option "Hello")
Next step: Continue to next question

Patient: HI
✅ Accepted! (matches option "Hi" - case insensitive)
Next step: Continue to next question

Patient: Hey
❌ Invalid response. Please select from available options or type one of these:
  1. Hello
  2. Hi
  3. Good morning
  4. Ready to start
```

### Rule 3: No Extra Text Allowed

```
✅ VALID:     "First lens"
❌ INVALID:   "I think first lens"
❌ INVALID:   "First lens is better"
❌ INVALID:   "option 1"
```

---

## Input Flow Diagrams

### Normal Path (Valid Input)

```
Patient enters response
    ↓
Response empty?
├─ YES → "Please provide a response" → Ask again
└─ NO ↓
   Are predefined options available?
   ├─ NO → Accept any response → Continue
   └─ YES ↓
       Is response a number?
       ├─ YES ↓
       │   Is number in valid range (1-N)?
       │   ├─ YES → Accept & return option text ✅
       │   └─ NO → Show error → Ask again
       │
       └─ NO ↓
           Does response match any option (case-insensitive)?
           ├─ YES → Accept ✅
           └─ NO → Show error → Ask again
```

### Real Example: Step 0.1

```
[Step 0.1] Welcome & Introduction
AI Optemetrist: Hello! I'm your AI Optometrist...

Options:
  1. Hello
  2. Hi
  3. Good morning
  4. Ready to start

Patient: 5                              ❌ Out of range

❌ Invalid option. Please select 1 to 4, or type one of the options:
  1. Hello
  2. Hi
  3. Good morning
  4. Ready to start

Patient: 1                              ✅ Valid!

[Step 0.1] completed. Next: 0.2
```

---

## Code Implementation

### Option Validation Logic

```python
async def _get_patient_input(self, substep: str) -> str:
    """Get patient input with validation"""
    
    options = STEP_OPTIONS.get(substep, [])
    
    if options:
        print("Options:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print()
    
    # Keep asking until valid response received
    while True:
        response = input("Patient: ").strip()
        
        # Check if response is empty
        if not response:
            print("Please provide a response.")
            continue
        
        # If predefined options exist, validate
        if options:
            # RULE 1: Check if valid number (1-N)
            if response.isdigit():
                option_num = int(response)
                if 1 <= option_num <= len(options):
                    return options[option_num - 1]  # Return option text
                else:
                    # Out of range
                    print(f"❌ Invalid option. Please select 1 to {len(options)}")
                    continue
            
            # RULE 2: Check if matches option text (case-insensitive)
            response_lower = response.lower()
            for option in options:
                if option.lower() == response_lower:
                    return option  # Match found
            
            # No match - ask again
            print(f"❌ Invalid response. Please select from available options:")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            continue
        
        # No predefined options - accept any response
        return response
```

---

## Real-World Examples

### Example 1: Valid Number Input ✅

```
Step: 0.1
Question: "Hello! I'm your AI Optometrist..."
Options: Hello, Hi, Good morning, Ready to start

Patient Input: 2
├─ Is digit? YES
├─ In range (1-4)? YES
└─ Return: options[1] = "Hi"

Result: ACCEPTED ✅
Next step: 0.2
```

### Example 2: Invalid Number (Out of Range) ❌

```
Step: 0.1
Question: "Hello! I'm your AI Optometrist..."
Options: Hello, Hi, Good morning, Ready to start

Patient Input: 5
├─ Is digit? YES
├─ In range (1-4)? NO
└─ Error: "Invalid option. Please select 1 to 4"

Result: REJECTED ❌
Action: Ask question again
```

### Example 3: Valid Text Match (Case-Insensitive) ✅

```
Step: 0.1
Question: "Hello! I'm your AI Optometrist..."
Options: Hello, Hi, Good morning, Ready to start

Patient Input: "ready to start"
├─ Is digit? NO
├─ Compare "ready to start" (lowercase)
├─ Match found: "Ready to start" option
└─ Return: "Ready to start"

Result: ACCEPTED ✅
Next step: 0.2
```

### Example 4: Invalid Text (No Match) ❌

```
Step: 0.1
Question: "Hello! I'm your AI Optometrist..."
Options: Hello, Hi, Good morning, Ready to start

Patient Input: "hellooo"
├─ Is digit? NO
├─ Compare with each option (case-insensitive)
├─ "hellooo" != "hello"
├─ "hellooo" != "hi"
├─ "hellooo" != "good morning"
├─ "hellooo" != "ready to start"
└─ No match found

Result: REJECTED ❌
Action: Show error, ask question again
```

### Example 5: Lens Comparison (Step 6.1)

```
Step: 6.1
Question: "Which lens makes the dot sharper and rounder?"
Options: First lens better, Second lens better, Both same, Clear now

Patient Input: "3"
├─ Is digit? YES
├─ In range (1-4)? YES
└─ Return: "Both same"

Result: ACCEPTED ✅
Action: Process response (no step progression if response quality unclear)

---

Patient Input: "First lens better"
├─ Is digit? NO
├─ Compare "first lens better" (lowercase)
├─ Match found: "First lens better" option
└─ Return: "First lens better"

Result: ACCEPTED ✅
Action: Process response

---

Patient Input: "the first lens"
├─ Is digit? NO
├─ Compare "the first lens" (lowercase)
├─ No exact match found
└─ Error

Result: REJECTED ❌
Action: Show error, ask again
```

---

## Integration with Step Progression

### Complete Flow: Invalid Input → Step Stays Same

```
Patient at Step 0.1
    ↓
AI asks: "Which greeting applies to you?"
Options: 1. Hello  2. Hi  3. Good morning  4. Ready to start
    ↓
Patient inputs: 5
    ↓
Validation: ❌ INVALID (out of range 1-4)
    ↓
System: "❌ Invalid option. Please select 1 to 4..."
    ↓
next_step = "0.1" (SAME STEP)
    ↓
Ask question again at Step 0.1
    ↓
Patient inputs: 1  ✅
    ↓
Validation: ✅ VALID
    ↓
next_step = "0.2" (NEXT STEP)
```

---

## Configuration

### Available Options by Step

Current configuration from `chat_flow_config.py`:

```python
STEP_OPTIONS = {
    "0.1": ["Hello", "Hi", "Good morning", "Ready to start"],
    "0.2": ["English", "Hindi", "Other"],
    "2.1": ["6/6", "6/9", "6/12", "Worse than 6/12"],
    "6.1": ["First lens better", "Second lens better", "Both same", "Clear now"],
    # ... more steps ...
}
```

---

## Error Messages

### Message 1: Out of Range Number
```
❌ Invalid option. Please select 1 to 4, or type one of the options:
  1. Hello
  2. Hi
  3. Good morning
  4. Ready to start
```

### Message 2: Text Doesn't Match
```
❌ Invalid response. Please select from the available options or type one of these:
  1. Hello
  2. Hi
  3. Good morning
  4. Ready to start
```

### Message 3: Empty Response
```
Please provide a response.
```

---

## Testing Validation

### Test Case 1: Valid Option Number
```bash
Input: 1
Expected: Accepted, next step = 0.2
Result: ✅ PASS
```

### Test Case 2: Invalid Option Number (too high)
```bash
Input: 5
Expected: Rejected, ask again, next step = 0.1
Result: ✅ PASS
```

### Test Case 3: Invalid Option Number (zero)
```bash
Input: 0
Expected: Rejected, ask again, next step = 0.1
Result: ✅ PASS
```

### Test Case 4: Valid Text Option
```bash
Input: Hello
Expected: Accepted, next step = 0.2
Result: ✅ PASS
```

### Test Case 5: Valid Text Option (different case)
```bash
Input: HELLO
Expected: Accepted (case-insensitive), next step = 0.2
Result: ✅ PASS
```

### Test Case 6: Invalid Text Option
```bash
Input: "hellooo"
Expected: Rejected, ask again, next step = 0.1
Result: ✅ PASS
```

### Test Case 7: Text with extra words
```bash
Input: "I choose hello"
Expected: Rejected, ask again, next step = 0.1
Result: ✅ PASS
```

### Test Case 8: Empty input
```bash
Input: [empty]
Expected: "Please provide a response", ask again
Result: ✅ PASS
```

---

## Summary

**Key Rules:**

1. ✅ Accept **only valid option numbers** (1-N where N = option count)
2. ✅ Accept **exact text matches** (case-insensitive)
3. ✅ Reject **any other input** (numbers out of range, partial text, extra words)
4. ✅ When invalid: Show error + options list + **ask question again**
5. ✅ **Stay on same step** until valid input received

**Result:** Stricter input validation ensures clean, unambiguous patient responses.
