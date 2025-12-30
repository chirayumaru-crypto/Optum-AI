# Jackson Cross Cylinder (JCC) Test with Patient Responses

## Overview

The **JCC (Jackson Cross Cylinder)** test refines the astigmatism correction through three sequential tests:
1. **Horizontal Axis Test** - Determine optimal horizontal/vertical axis orientation
2. **Vertical Axis Test** - Fine-tune axis between two positions
3. **Duochrome Test** - Red/Green balance to finalize sphere correction

This guide shows the complete JSON structure with patient responses for all three tests.

---

## Complete JSON Structure

```json
{
  "command": "present_jcc",
  "timestamp": "ISO8601",
  "session_id": "exam_P001_20251229",
  "step": "6",
  "substep": "6.2",
  "eye": "OS",
  
  // Current prescription being refined
  "current_prescription": {
    "SPH": 0.0,
    "CYL": 0.0,
    "AXIS": 0
  },
  
  // Sequence of JCC test components
  "test_sequence": [
    {
      "sequence_number": 1,
      "test_type": "axis_horizontal",
      "axis": "horizontal",
      "question": "Which axis position is clearer?",
      "options": ["Position 1", "Position 2", "Both same", "Neither clear"],
      "lens_positions": { ... }
    },
    {
      "sequence_number": 2,
      "test_type": "axis_vertical",
      "axis": "vertical",
      "question": "Which vertical position is clearer?",
      "options": ["Position 1", "Position 2", "Both same", "Neither clear"],
      "lens_positions": { ... }
    },
    {
      "sequence_number": 3,
      "test_type": "duochrome",
      "duochrome": true,
      "question": "Red or green? Or equal?",
      "options": ["Red clearer", "Green clearer", "Both equal", "Neither clear"],
      "lens_positions": { ... }
    }
  ],
  
  // PATIENT RESPONSES for each test
  "patient_responses": [
    {
      "sequence_number": 1,
      "test_type": "axis_horizontal",
      "raw_response": "...",
      "selected_option": "Position 1 (horizontal)",
      "confidence": 0.82,
      "sentiment": "Confident",
      "response_quality": "clear"
    },
    {
      "sequence_number": 2,
      "test_type": "axis_vertical",
      "raw_response": "...",
      "selected_option": "Both same",
      "confidence": 0.45,
      "sentiment": "Uncertain",
      "response_quality": "ambiguous"
    },
    {
      "sequence_number": 3,
      "test_type": "duochrome",
      "raw_response": "...",
      "selected_option": "Red clearer",
      "confidence": 0.65,
      "sentiment": "Uncertain",
      "response_quality": "ambiguous"
    }
  ],
  
  // Clinical analysis of responses
  "clinical_analysis": { ... },
  
  // Phoropter control actions
  "phoropter_control": { ... },
  
  "audit_trail": { ... }
}
```

---

## Test Component Breakdown

### Part 1: Horizontal Axis Test

**Purpose:** Determine if axis should be at 180° (horizontal) or 90° (vertical)

```json
{
  "sequence_number": 1,
  "test_type": "axis_horizontal",
  "axis": "horizontal",
  "question": "Looking at these two axis positions, which one is clearer?",
  "options": ["Position 1 (horizontal)", "Position 2 (horizontal)", "Both same", "Neither clear"],
  "lens_positions": {
    "position_1": {"SPH": 0.0, "CYL": -0.25, "AXIS": 180},
    "position_2": {"SPH": 0.0, "CYL": -0.25, "AXIS": 90}
  }
}
```

**Patient Response:**
```json
{
  "sequence_number": 1,
  "test_type": "axis_horizontal",
  "raw_response": "Position 1 looks clearer",
  "selected_option": "Position 1 (horizontal)",
  "confidence": 0.82,
  "sentiment": "Confident",
  "response_quality": "clear"
}
```

**Interpretation:**
- ✅ Clear response with high confidence (0.82)
- **Conclusion:** AXIS 180° is correct
- **Action:** Proceed to next test (vertical refinement)

---

### Part 2: Vertical Axis Test

**Purpose:** Fine-tune axis between two nearby positions (e.g., 175° vs 170°)

```json
{
  "sequence_number": 2,
  "test_type": "axis_vertical",
  "axis": "vertical",
  "question": "Now looking at the vertical positions, which is clearer?",
  "options": ["Position 1 (vertical)", "Position 2 (vertical)", "Both same", "Neither clear"],
  "lens_positions": {
    "position_1": {"SPH": 0.0, "CYL": -0.25, "AXIS": 175},
    "position_2": {"SPH": 0.0, "CYL": -0.25, "AXIS": 170}
  }
}
```

**Patient Response:**
```json
{
  "sequence_number": 2,
  "test_type": "axis_vertical",
  "raw_response": "Hmm, they're pretty much the same",
  "selected_option": "Both same",
  "confidence": 0.45,
  "sentiment": "Uncertain",
  "response_quality": "ambiguous"
}
```

**Interpretation:**
- ⚠️ Ambiguous response with low confidence (0.45 < 0.6)
- **Conclusion:** Cannot clearly distinguish between 175° and 170°
- **Action:** Either repeat test or accept 175° from horizontal refinement

---

### Part 3: Duochrome Test (Red/Green)

**Purpose:** Fine-tune sphere correction using red and green light

```json
{
  "sequence_number": 3,
  "test_type": "duochrome",
  "duochrome": true,
  "question": "Which color appears clearer - red or green? Or are they equal?",
  "options": ["Red clearer", "Green clearer", "Both equal", "Neither clear"],
  "lens_positions": {
    "red_filter": {"SPH": 0.0, "CYL": -0.25, "AXIS": 175},
    "green_filter": {"SPH": -0.25, "CYL": -0.25, "AXIS": 175}
  }
}
```

**Patient Response:**
```json
{
  "sequence_number": 3,
  "test_type": "duochrome",
  "raw_response": "Red looks a tiny bit clearer",
  "selected_option": "Red clearer",
  "confidence": 0.65,
  "sentiment": "Uncertain",
  "response_quality": "ambiguous"
}
```

**Interpretation:**
- ⚠️ Ambiguous response with moderate confidence (0.65)
- **Red clearer** means sphere is under-corrected (too much minus/too little plus)
- **Action:** Add slight positive sphere (+0.125D) or -0.125D if negative

---

## Clinical Analysis of All Responses

```json
"clinical_analysis": {
  "axis_horizontal_finding": {
    "status": "CLEAR",
    "patient_preference": "Position 1 (AXIS 180°)",
    "confidence": 0.82,
    "interpretation": "Patient strongly prefers horizontal axis at 180°. High confidence."
  },
  
  "axis_vertical_finding": {
    "status": "AMBIGUOUS",
    "patient_preference": "Both same",
    "confidence": 0.45,
    "interpretation": "Patient uncertain between 175° and 170°. Accept 175° from horizontal test due to low confidence."
  },
  
  "duochrome_finding": {
    "status": "AMBIGUOUS",
    "patient_preference": "Red clearer",
    "confidence": 0.65,
    "interpretation": "Patient slightly prefers red, suggesting sphere may be slightly under-corrected. Consider +0.125D adjustment."
  }
}
```

---

## Phoropter Control Actions

### Multi-Step Actions

```json
"phoropter_control": {
  "primary_actions": [
    {
      "sequence": 1,
      "action": "confirm_axis",
      "parameter": "AXIS",
      "current_value": 0,
      "decision_value": 180,
      "reason": "Patient clearly prefers horizontal axis (AXIS 180°)"
    },
    {
      "sequence": 2,
      "action": "repeat_axis_test",
      "parameter": "AXIS",
      "reason": "Patient ambiguous (confidence 0.45 < 0.6). Repeat or accept 175°."
    },
    {
      "sequence": 3,
      "action": "adjust_sphere_slight",
      "parameter": "SPH",
      "adjustment": {
        "direction": "negative",
        "magnitude": -0.125,
        "reason": "Red clearer indicates under-correction. Add -0.125D sphere."
      }
    }
  ],
  
  "final_recommendation": {
    "action": "accept_jcc_results",
    "new_prescription": {
      "SPH": -0.125,
      "CYL": -0.25,
      "AXIS": 180
    },
    "confidence": "HIGH",
    "next_step": "6.3"
  }
}
```

---

## Real-World Examples

### Example 1: All Clear Responses

```json
"patient_responses": [
  {
    "sequence_number": 1,
    "test_type": "axis_horizontal",
    "selected_option": "Position 1 (horizontal)",
    "confidence": 0.90,
    "response_quality": "clear"
  },
  {
    "sequence_number": 2,
    "test_type": "axis_vertical",
    "selected_option": "Position 1 (vertical)",
    "confidence": 0.85,
    "response_quality": "clear"
  },
  {
    "sequence_number": 3,
    "test_type": "duochrome",
    "selected_option": "Both equal",
    "confidence": 0.88,
    "response_quality": "clear"
  }
]
```

**Clinical Decision:**
```json
"phoropter_control": {
  "final_recommendation": {
    "action": "accept_jcc_results",
    "new_prescription": {
      "SPH": 0.0,
      "CYL": -0.25,
      "AXIS": 180
    },
    "confidence": "VERY HIGH",
    "next_step": "6.3"
  }
}
```

---

### Example 2: Mixed Clear and Ambiguous

```json
"patient_responses": [
  {
    "sequence_number": 1,
    "selected_option": "Position 1 (horizontal)",
    "confidence": 0.88,
    "response_quality": "clear"
  },
  {
    "sequence_number": 2,
    "selected_option": "Both same",
    "confidence": 0.42,
    "response_quality": "ambiguous"
  },
  {
    "sequence_number": 3,
    "selected_option": "Green clearer",
    "confidence": 0.70,
    "response_quality": "ambiguous"
  }
]
```

**Clinical Decision:**
```json
"phoropter_control": {
  "primary_actions": [
    {
      "sequence": 1,
      "action": "confirm_axis",
      "decision_value": 180
    },
    {
      "sequence": 2,
      "action": "repeat_axis_test",
      "reason": "Low confidence (0.42). Repeat vertical refinement."
    },
    {
      "sequence": 3,
      "action": "adjust_sphere_positive",
      "magnitude": 0.125,
      "reason": "Green clearer indicates over-correction. Add +0.125D sphere."
    }
  ]
}
```

---

### Example 3: All Ambiguous (Need Repeat)

```json
"patient_responses": [
  {
    "sequence_number": 1,
    "selected_option": "Both same",
    "confidence": 0.50,
    "response_quality": "ambiguous"
  },
  {
    "sequence_number": 2,
    "selected_option": "Both same",
    "confidence": 0.48,
    "response_quality": "ambiguous"
  },
  {
    "sequence_number": 3,
    "selected_option": "Neither clear",
    "confidence": 0.35,
    "response_quality": "unclear"
  }
]
```

**Clinical Decision:**
```json
"phoropter_control": {
  "final_recommendation": {
    "action": "repeat_jcc_test",
    "reason": "All responses ambiguous/unclear (avg confidence 0.44). Patient may be fatigued. Repeat JCC or move to next step.",
    "next_step": "6.2"  // Stay on same step
  }
}
```

---

## Confidence Thresholds for JCC

```
RESPONSE QUALITY BASED ON CONFIDENCE:

Confidence Range     Status          Action
═══════════════════════════════════════════
≥ 0.80              VERY CLEAR      Use result directly
0.70 - 0.79         CLEAR           Use result
0.60 - 0.69         ACCEPTABLE      Use with caution
0.50 - 0.59         AMBIGUOUS       Consider repeating or using conservative value
< 0.50              UNCLEAR/INVALID Repeat test
```

---

## Red Flag Responses (Examples)

### Red Flag 1: Emergency Escalation

```json
{
  "sequence_number": 2,
  "test_type": "axis_vertical",
  "raw_response": "I'm having sudden eye pain and flashing lights",
  "confidence": 0,
  "red_flag": true,
  "red_flag_keywords": ["pain", "sudden", "flashing"],
  "response_quality": "emergency"
}
```

**Action:**
```json
"phoropter_control": {
  "action": "escalate",
  "reason": "RED FLAG: Patient reported severe symptoms. Halt test immediately.",
  "next_step": "escalate_to_professional"
}
```

---

### Red Flag 2: Patient Fatigue/Confusion

```json
{
  "sequence_number": 3,
  "test_type": "duochrome",
  "raw_response": "Um... I'm not sure... everything looks blurry now",
  "confidence": 0.20,
  "sentiment": "Fatigued",
  "response_quality": "unclear"
}
```

**Action:**
```json
"phoropter_control": {
  "action": "halt_jcc",
  "reason": "Patient showing fatigue/confusion. Confidence only 0.20. Suggest break.",
  "next_step": "comfort_check"
}
```

---

## Audit Trail for JCC

```json
"audit_trail": {
  "processed_by": "AIOptumLLMEngine",
  "steering_layers_applied": [
    "intent_extraction",
    "sentiment_analysis",
    "confidence_evaluation",
    "fatigue_detection",
    "red_flag_detection"
  ],
  "total_responses_captured": 3,
  "clear_responses": 1,
  "ambiguous_responses": 2,
  "unclear_responses": 0,
  "red_flags": 0,
  "average_confidence": 0.64,
  "test_completeness": "PARTIAL_AMBIGUOUS",
  "validation_passed": true,
  "processing_time_ms": 24
}
```

---

## JCC Test Decision Logic

```
JCC Test Starts
    ↓
Horizontal Axis Test
├─ Clear (≥0.75) → Use AXIS result
├─ Ambiguous (0.50-0.75) → Accept with caution
└─ Unclear (<0.50) → Repeat
    ↓
Vertical Axis Test
├─ Clear (≥0.75) → Refine AXIS further
├─ Ambiguous (0.50-0.75) → Accept previous result
└─ Unclear (<0.50) → Use horizontal result
    ↓
Duochrome Test
├─ Red clearer → Add negative sphere (under-corrected)
├─ Green clearer → Add positive sphere (over-corrected)
├─ Both equal → No sphere adjustment
└─ Unclear → No adjustment
    ↓
Generate Final Prescription
```

---

## Integration with Step 6 Refraction

**Step 6.1-6.4:** Subjective refraction (sphere/cylinder baseline)  
**Step 6.2 / 6.4:** JCC test (refine axis and sphere)

```
Step 6.1 → Coarse Sphere (Right Eye)
    ↓
Step 6.2 → JCC Test (Right Eye Axis + Duochrome)
    ↓
Step 6.3 → Coarse Sphere (Left Eye)
    ↓
Step 6.4 → JCC Test (Left Eye Axis + Duochrome)
    ↓
Step 6.5 → Binocular Balance
```

---

## Summary

**JCC Test JSON includes:**

✅ **Test Sequence** - Horizontal, vertical, duochrome parts  
✅ **Patient Responses** - For each of the 3 tests  
✅ **Clinical Analysis** - Interpretation of responses  
✅ **Phoropter Control** - Multi-step actions  
✅ **Audit Trail** - Full traceability  

**Patient Response fields:**
- `raw_response` - Exact patient input
- `selected_option` - Which option chosen
- `confidence` - Confidence level (0-1)
- `sentiment` - Emotional state
- `response_quality` - clear/ambiguous/unclear
- `red_flag` - Emergency detection

**System automatically:**
- Validates each response quality
- Compares confidence thresholds
- Makes clinical decisions
- Controls phoropter device
- Determines next step
- Flags for review if needed

This provides **complete traceability and clinical decision support for JCC testing**.
