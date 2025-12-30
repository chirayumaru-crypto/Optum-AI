# AI Optum: Chat Flow to Phoropter Integration Guide

**Version:** 1.0  
**Date:** December 29, 2025  

---

## 1. Architecture Overview

The AI Optum system consists of three integrated layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATIENT INTERACTION                          │
│                   (Speech/Text Input)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              CHAT FLOW & RESPONSE PARSER                        │
│   • Step & Substep Management (0.1 - 9.2)                       │
│   • LangChain Intent Extraction                                 │
│   • Red Flag Detection                                          │
│   • Output: Structured JSON                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│            PHOROPTER CONTROL BRIDGE                             │
│   • Translate JSON to Device Commands                           │
│   • Safety Constraint Validation                                │
│   • Current Prescription Tracking                               │
│   • Output: Hardware Control Signals                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHOROPTER HARDWARE DEVICE                          │
│   • Motor Control (Sphere, Cylinder, Axis)                      │
│   • Lens Presentation                                           │
│   • Chart Display                                               │
│   • Feedback Sensors                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Chat Flow Layer (`chat_flow_config.py`)

### 2.1 Role: Navigation & Protocol Definition

The chat flow layer defines:
- **10 Steps** (0-9) covering complete eye examination
- **26 Substeps** (0.1-9.2) with granular task definitions
- **Clinical context** for each substep (what AI says)
- **Patient options** (expected responses)
- **Step progression** (which substep follows which)

### 2.2 Data Structures

```python
# Step names and progression
STEP_NAMES: Dict[int, str]  # Maps step number to name
SUBSTEP_NAMES: Dict[str, str]  # Maps "X.Y" to description
STEP_PROGRESSION: Dict[str, str]  # Maps "X.Y" → "Z.A" (next step)

# Clinical protocol
CLINICAL_CONTEXT: Dict[str, str]  # What AI says at each step
STEP_OPTIONS: Dict[str, List[str]]  # Expected patient responses

# Phoropter integration
PHOROPTER_CONTROLS: Dict[str, Dict]  # Device commands per step
```

### 2.3 Example: Step 6.1 (Right Eye Refraction)

```python
STEP_PROGRESSION["6.1"] = "6.2"  # After 6.1, go to 6.2

CLINICAL_CONTEXT["6.1"] = (
    "I'm covering your left eye. Focus on the dot chart with your "
    "RIGHT EYE only. I'll show you two lens options - tell me which "
    "makes the dot sharper and rounder."
)

STEP_OPTIONS["6.1"] = [
    "First lens better",
    "Second lens better", 
    "Both same",
    "Clear now"
]

PHOROPTER_CONTROLS["6.1"] = {
    "eye": "OD",
    "occluded_eye": "OS",
    "lens_test_pairs": [...],  # Two lens options
    "decision_logic": "increment_sphere"  # How to adjust
}
```

---

## 3. Response Parser Layer (`response_parser.py`)

### 3.1 Role: Convert Utterances to Structured JSON

**Input:** Patient's spoken/text response  
**Output:** Structured JSON with phoropter control signals

### 3.2 Parsing Pipeline

```python
AIOptumResponseParser.parse_response(
    step="6",           # Current step
    substep="6.1",      # Current substep
    utterance="The first lens makes it look clearer"  # Patient said
)
```

**Returns:**
```json
{
    "intent": "refraction_feedback",
    "slots": {
        "clarity_feedback": "first_lens_better"
    },
    "sentiment": "Confident",
    "confidence": 0.95,
    "red_flag": false,
    "phoropter_action": "adjust_sphere_positive_0.25_OD",
    "next_step": "6.2"
}
```

### 3.3 Intent Detection

The parser identifies patient intent using LangChain:

```python
INTENTS = [
    "test_complete",        # Patient confirms test is done
    "vision_reported",      # Patient describes what they see
    "health_check",         # Patient reports eye health
    "alignment_ok",         # Patient confirms eye alignment
    "pd_ready",             # PD measurement complete
    "refraction_feedback",  # Feedback on lens options
    "reading_ability",      # Feedback on near vision
    "prescription_ok",      # Prescription feels comfortable
    "product_choice",       # Patient chooses lens/coating
    "unknown"               # Intent unclear
]
```

### 3.4 Phoropter Action Generation

Based on parsed intent and slots, the parser generates device commands:

```python
# If patient says "first lens better" at step 6.1 (OD refraction):
phoropter_action = "adjust_sphere_positive_0.25_OD"

# This tells phoropter controller to:
# 1. Select right eye (OD)
# 2. Adjust sphere by +0.25 diopters
# 3. Present next lens pair
```

### 3.5 Safety Red Flags

Red flags trigger immediate test halt:

```python
RED_FLAG_KEYWORDS = [
    "pain", "severe", "sudden", "loss", "flashing",
    "floaters", "infection", "discharge", "bleeding",
    "trauma", "emergency", "urgent", "vision loss"
]
```

If detected:
```json
{
    "red_flag": true,
    "status": "ESCALATION_REQUIRED",
    "next_step": "escalate_to_professional"
}
```

---

## 4. Phoropter Controller Layer (`phoropter_controller.py`)

### 4.1 Role: Hardware Interface & Safety Enforcement

The phoropter controller:
- Executes lens adjustments (Sphere, Cylinder, Axis)
- Maintains device state and adjustment history
- Enforces safety constraints
- Generates hardware control signals

### 4.2 Core Classes

#### `LensConfiguration`
```python
@dataclass
class LensConfiguration:
    sphere: float      # -20.00 to +20.00 diopters
    cylinder: float    # 0 to -6.00 diopters
    axis: int         # 0 to 180 degrees
```

#### `PhoropeterState`
```python
@dataclass
class PhoropeterState:
    od_lens: LensConfiguration       # Right eye prescription
    os_lens: LensConfiguration       # Left eye prescription
    current_eye: EyeDesignation      # OD or OS
    occluded_eye: Optional[EyeDesignation]  # Blocked eye
    pd_distance: float               # Pupillary distance
    adjustment_history: list         # Log of all changes
```

#### `PhoropterController`
```python
class PhoropterController:
    def adjust_sphere(eye, increment) → (bool, str)
    def adjust_cylinder(eye, increment) → (bool, str)
    def adjust_axis(eye, increment) → (int, str)
    def set_occlusion(occluded_eye) → (bool, str)
    def set_pd(pd_distance) → (bool, str)
    def present_lens_pair(eye, lens1, lens2) → Dict
    def present_jcc_test(eye) → Dict
    def balance_binocular() → Dict
    def finalize_prescription() → Dict
```

### 4.3 Safety Constraints

All adjustments are validated:

```python
safety_limits = {
    "max_sphere_jump": 0.50,       # ±0.50D per step
    "max_cylinder_jump": 0.50,     # ±0.50D per step
    "max_axis_jump": 10,           # ±10° per step
    "sphere_range": (-20.0, 20.0),
    "cylinder_range": (0.0, 6.0),
    "axis_range": (0, 180)
}
```

Example:
```python
# Request: adjust_sphere_positive_0.50_OD (unsafe jump)
success, msg = controller.adjust_sphere(OD, increment=0.50)
# Returns: (False, "Unsafe jump: ±0.50 > ±0.25")
```

### 4.4 Device Commands

Commands output JSON for hardware communication:

```python
# Present lens pair
{
    "command": "present_lens_pair",
    "eye": "OD",
    "lens_1": {"SPH": -0.50, "CYL": 0, "AXIS": 0},
    "lens_2": {"SPH": -0.25, "CYL": 0, "AXIS": 0},
    "question": "Which lens makes the dot sharper?",
    "options": ["First", "Second", "Both same", "Neither"]
}

# Present Jackson Cross Cylinder (for astigmatism)
{
    "command": "present_jcc",
    "eye": "OD",
    "current_prescription": {"SPH": -1.50, "CYL": 0, "AXIS": 0},
    "test_sequence": [
        {"axis": "horizontal", "question": "Which is clearer?"},
        {"axis": "vertical", "question": "Which is clearer?"},
        {"duochrome": true, "question": "Red or green?"}
    ]
}

# Finalize prescription
{
    "command": "finalize",
    "final_prescription": {
        "OD": {"SPH": -1.50, "CYL": -0.75, "AXIS": 180},
        "OS": {"SPH": -2.00, "CYL": -0.50, "AXIS": 175}
    },
    "pd": {"distance": 64.0, "near": 61.0}
}
```

---

## 5. Integration Flow: From Patient to Phoropter

### 5.1 Step 6.1: Right Eye Refraction Example

```
STEP 1: PATIENT INTERACTION
┌─────────────────────────────────────────────────────────────────┐
│ AI: "I'm covering your left eye. Focus on the dot with your   │
│      RIGHT EYE only. I'll show two lens options - which makes  │
│      the dot sharper and rounder?"                             │
│                                                                 │
│ PATIENT: "The first lens makes it look clearer"               │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼

STEP 2: CHAT FLOW DETECTION
┌─────────────────────────────────────────────────────────────────┐
│ Step: "6", Substep: "6.1"                                       │
│ Expected options: ["First lens better", "Second lens better",  │
│                    "Both same", "Clear now"]                   │
│ Next step: "6.2" (Right Eye JCC & Duochrome)                   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼

STEP 3: RESPONSE PARSING
┌─────────────────────────────────────────────────────────────────┐
│ Input: "The first lens makes it look clearer"                  │
│                                                                 │
│ Parsing with LangChain:                                        │
│ - Intent: "refraction_feedback"                                │
│ - Slot clarity_feedback: "first_lens_better"                   │
│ - Sentiment: "Confident"                                       │
│ - Confidence: 0.95                                              │
│ - Red Flag: false                                              │
│                                                                 │
│ Output JSON:                                                    │
│ {                                                              │
│   "intent": "refraction_feedback",                             │
│   "phoropter_action": "adjust_sphere_positive_0.25_OD",       │
│   "next_step": "6.2"                                           │
│ }                                                              │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼

STEP 4: PHOROPTER CONTROL
┌─────────────────────────────────────────────────────────────────┐
│ Action: "adjust_sphere_positive_0.25_OD"                       │
│                                                                 │
│ Controller validation:                                         │
│ - Eye: OD (Right)                                              │
│ - Current sphere: -1.25D                                       │
│ - Adjustment: +0.25D                                           │
│ - New value: -1.00D                                            │
│ - Within range [-20, +20]? YES ✓                               │
│ - Increment < 0.50D? YES ✓                                     │
│ - SAFE: Proceed                                                │
│                                                                 │
│ Device command output:                                         │
│ {                                                              │
│   "command": "present_lens_pair",                              │
│   "eye": "OD",                                                 │
│   "lens_1": {"SPH": -1.00, "CYL": 0, "AXIS": 0},             │
│   "lens_2": {"SPH": -0.75, "CYL": 0, "AXIS": 0},             │
│   "question": "Which is sharper?"                              │
│ }                                                              │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼

STEP 5: HARDWARE EXECUTION
┌─────────────────────────────────────────────────────────────────┐
│ Phoropter Hardware:                                             │
│ 1. Occlude left eye (OS)                                       │
│ 2. Adjust sphere wheel to -1.00D                               │
│ 3. Present first lens pair (click/buzz)                        │
│ 4. Await patient response                                      │
│                                                                 │
│ Loop back to STEP 1 (repeat process)                           │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Decision Tree: Step 6 (Subjective Refraction)

```
Step 6: Subjective Refraction
│
├─ 6.1: Right Eye (OD) Refraction
│  │
│  ├─ If "First lens better" → adjust_sphere_positive_0.25_OD → 6.2
│  ├─ If "Second lens better" → adjust_sphere_negative_0.25_OD → 6.2
│  ├─ If "Both same" → hold_current_lens_OD → 6.2
│  └─ If "Clear now" → proceed_to_jcc_OD → 6.2
│
├─ 6.2: Right Eye JCC & Duochrome
│  │
│  ├─ If cylinder needs adjustment → adjust_cylinder_axis_OD
│  ├─ If "Red clearer" → adjust_sphere_negative_0.25_OD
│  ├─ If "Green clearer" → adjust_sphere_positive_0.25_OD
│  └─ If "Both equal" → finalize_OD → 6.3
│
├─ 6.3: Left Eye (OS) Refraction
│  │
│  └─ [Same as 6.1 but for OS] → 6.4
│
├─ 6.4: Left Eye JCC & Duochrome
│  │
│  └─ [Same as 6.2 but for OS] → 6.5
│
└─ 6.5: Binocular Balance
   │
   ├─ If "Both equal" → finalize_prescription → 7.1
   ├─ If "Right eye clearer" → adjust_OS_negative_0.25 → loop
   └─ If "Left eye clearer" → adjust_OD_negative_0.25 → loop
```

---

## 6. JSON Flow Examples

### 6.1 Simple Sphere Adjustment

**Patient:** "The first option is clearer"  
**Step:** 6.1 (OD Refraction)

```json
{
    "input": {
        "step": "6",
        "substep": "6.1",
        "utterance": "The first option is clearer"
    },
    "parsed": {
        "intent": "refraction_feedback",
        "slots": {
            "clarity_feedback": "first_lens_better"
        },
        "sentiment": "Confident",
        "confidence": 0.92,
        "red_flag": false,
        "phoropter_action": "adjust_sphere_positive_0.25_OD",
        "next_step": "6.2"
    },
    "phoropter_state_before": {
        "od_lens": {"SPH": -1.25, "CYL": 0, "AXIS": 0},
        "os_lens": {"SPH": -1.50, "CYL": 0, "AXIS": 0},
        "occluded_eye": "OS"
    },
    "phoropter_state_after": {
        "od_lens": {"SPH": -1.00, "CYL": 0, "AXIS": 0},
        "os_lens": {"SPH": -1.50, "CYL": 0, "AXIS": 0},
        "occluded_eye": "OS"
    },
    "device_command": {
        "command": "present_lens_pair",
        "eye": "OD",
        "lens_1": {"SPH": -1.00, "CYL": 0, "AXIS": 0},
        "lens_2": {"SPH": -0.75, "CYL": 0, "AXIS": 0},
        "question": "Which is sharper and rounder?"
    }
}
```

### 6.2 Duochrome Balance

**Patient:** "The red and green look equal"  
**Step:** 6.2 (Right Eye JCC & Duochrome)

```json
{
    "input": {
        "step": "6",
        "substep": "6.2",
        "utterance": "The red and green look equal"
    },
    "parsed": {
        "intent": "refraction_feedback",
        "slots": {
            "clarity_feedback": "equal"
        },
        "sentiment": "Confident",
        "confidence": 0.88,
        "red_flag": false,
        "phoropter_action": "duochrome_balanced_proceed_to_next",
        "next_step": "6.3"
    },
    "device_command": {
        "command": "proceed_to_next_step",
        "finalized_prescription_od": {
            "SPH": -1.00,
            "CYL": -0.50,
            "AXIS": 180
        },
        "next_step": "6.3"
    }
}
```

### 6.3 Binocular Balance

**Patient:** "Right eye seems a bit clearer"  
**Step:** 6.5 (Binocular Balance)

```json
{
    "input": {
        "step": "6",
        "substep": "6.5",
        "utterance": "Right eye seems a bit clearer"
    },
    "parsed": {
        "intent": "refraction_feedback",
        "slots": {
            "clarity_feedback": "right_eye_clearer"
        },
        "sentiment": "Confident",
        "confidence": 0.90,
        "red_flag": false,
        "phoropter_action": "balance_right_eye_dominant_adjust_os_negative",
        "next_step": "6.5_retry"
    },
    "device_command": {
        "command": "adjust_and_retest_binocular",
        "adjustment": {
            "eye": "OS",
            "parameter": "SPH",
            "change": -0.25,
            "new_value": -2.25
        },
        "new_prescription": {
            "OD": {"SPH": -1.00, "CYL": -0.50, "AXIS": 180},
            "OS": {"SPH": -2.25, "CYL": -0.50, "AXIS": 175}
        }
    }
}
```

---

## 7. Error Handling & Edge Cases

### 7.1 Unsafe Lens Adjustment

```json
{
    "requested_action": "adjust_sphere_positive_0.75_OD",
    "validation": {
        "increment": 0.75,
        "max_allowed": 0.50,
        "status": "BLOCKED"
    },
    "response": {
        "success": false,
        "message": "Unsafe jump: ±0.75 > ±0.50",
        "fallback_action": "adjust_sphere_positive_0.25_OD",
        "device_command": "present_lens_pair_with_smaller_step"
    }
}
```

### 7.2 Red Flag Detection

```json
{
    "input": {
        "step": "6",
        "substep": "6.1",
        "utterance": "Oww, my eye is suddenly in sharp pain"
    },
    "parsed": {
        "intent": "health_check",
        "red_flag": true,
        "severity": "HIGH",
        "keywords_detected": ["sharp", "pain", "sudden"]
    },
    "response": {
        "status": "ESCALATION_REQUIRED",
        "action": "HALT_TEST",
        "next_step": "escalate_to_professional",
        "message": "Please stop and consult with your eye care provider immediately",
        "device_command": "shutdown"
    }
}
```

### 7.3 Ambiguous Response

```json
{
    "input": {
        "step": "6",
        "substep": "6.1",
        "utterance": "Um, I'm not sure"
    },
    "parsed": {
        "intent": "unknown",
        "sentiment": "Under Confident",
        "confidence": 0.45,
        "red_flag": false
    },
    "response": {
        "status": "CLARIFICATION_NEEDED",
        "ai_followup": "I understand it's a bit tricky. Let me ask again - does the FIRST lens option make the dot sharper, or the SECOND one?",
        "device_command": "repeat_lens_pair",
        "confidence_threshold": 0.50
    }
}
```

---

## 8. Implementation Checklist

### Phase 1: Configuration
- [ ] Load `chat_flow_config.py` with all step/substep definitions
- [ ] Define PHOROPTER_CONTROLS mapping for each refraction step
- [ ] Configure intent and sentiment markers

### Phase 2: Response Parser
- [ ] Implement AIOptumResponseParser class
- [ ] Integrate LangChain for NLU
- [ ] Test intent detection on sample utterances
- [ ] Implement fallback rule-based parsing

### Phase 3: Phoropter Controller
- [ ] Implement PhoropterController class
- [ ] Add safety constraint validation
- [ ] Connect to hardware via serial/USB
- [ ] Test lens adjustments

### Phase 4: Integration
- [ ] Create PhoropterControlBridge class
- [ ] Wire parser → controller pipeline
- [ ] Implement error handling
- [ ] Add session logging

### Phase 5: Testing
- [ ] Unit test each component
- [ ] Integration test full flow (patient → device)
- [ ] Load test with 100+ utterances
- [ ] Safety constraint verification

---

## 9. Testing Guide

### Test Patient Responses

```python
from response_parser import AIOptumResponseParser
from phoropter_controller import PhoropterController

parser = AIOptumResponseParser()
controller = PhoropterController()

test_cases = [
    # (step, substep, utterance)
    ("6", "6.1", "First lens is clearer"),
    ("6", "6.2", "Red and green are equal"),
    ("6", "6.5", "Both eyes feel balanced"),
    ("3", "3.1", "My eyes look fine"),
    ("2", "2.1", "I can read 6/6"),
]

for step, substep, utterance in test_cases:
    result = parser.parse_response(step, substep, utterance)
    print(f"Step {substep}: {result['intent']} → {result['phoropter_action']}")
```

### Test Phoropter Safety

```python
controller = PhoropterController()

# Test 1: Valid adjustment
success, msg = controller.adjust_sphere(OD, 0.25)
# Expected: True, "Adjusted OD sphere to 0.25D"

# Test 2: Unsafe jump (>0.50D)
success, msg = controller.adjust_sphere(OD, 0.75)
# Expected: False, "Unsafe jump: ±0.75 > ±0.50"

# Test 3: Out of range
success, msg = controller.adjust_sphere(OD, 25.0)  # >20.00D max
# Expected: False, "Out of range..."
```

---

## 10. References

- **Chat Flow Configuration:** [chat_flow_config.py](chat_flow_config.py)
- **Response Parser:** [response_parser.py](response_parser.py)
- **Phoropter Controller:** [phoropter_controller.py](phoropter_controller.py)
- **Process Engine:** [PROCESS_ENGINE.md](PROCESS_ENGINE.md)
- **PRD:** [PRD.md](PRD.md)
