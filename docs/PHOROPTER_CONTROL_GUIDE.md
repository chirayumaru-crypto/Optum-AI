# Lens Pair Command with Phoropter Control

## Complete JSON Structure with Patient Response & Phoropter Action

The complete lens pair command now includes three sections:
1. **Lens Presentation** - What lenses are being shown
2. **Patient Response** - How patient answered
3. **Phoropter Control** - What device should do

---

## Full JSON Schema

```json
{
  "command": "present_lens_pair",
  "timestamp": "ISO8601",
  "session_id": "exam_P001_20251229",
  "step": "6",
  "substep": "6.1",
  
  // ===== LENS PRESENTATION =====
  "eye": "OS",
  "lens_pair": {
    "lens_1": { "SPH": float, "CYL": float, "AXIS": int },
    "lens_2": { "SPH": float, "CYL": float, "AXIS": int }
  },
  "question": "Which lens makes the dot sharper and rounder?",
  "options": ["First lens", "Second lens", "Both same", "Neither clear"],
  "presentation_metadata": {
    "duration_ms": 5000,
    "distance": "20 feet",
    "illumination": "optimal",
    "patient_position": "stable"
  },
  
  // ===== PATIENT RESPONSE =====
  "patient_response": {
    "raw_response": "The second lens is clearer",
    "timestamp": "ISO8601",
    "response_time_ms": 6210,
    "selected_option": "Second lens",
    "option_index": 2,
    "confidence": 0.88,
    "intent": "refraction_feedback",
    "sentiment": "Confident",
    "sentiment_score": 0.85,
    "red_flag": false,
    "persona_override_detected": false,
    "response_quality": "clear"
  },
  
  // ===== PHOROPTER CONTROL =====
  "phoropter_control": {
    "action": "adjust_sphere_negative",
    "eye": "OS",
    "current_lens": { "SPH": -0.25, "CYL": 0, "AXIS": 0 },
    "preferred_lens": { "SPH": 0.0, "CYL": 0, "AXIS": 0 },
    "adjustment": {
      "parameter": "SPH",
      "direction": "negative",
      "magnitude": -0.25,
      "new_value": 0.0
    },
    "clinical_decision": "Patient prefers second lens (SPH 0.0) over first lens (SPH -0.25). Remove -0.25D from sphere.",
    "next_step": "6.2"
  },
  
  "audit_trail": {
    "processed_by": "AIOptumLLMEngine",
    "steering_layers_applied": [...],
    "validation_passed": true,
    "processing_time_ms": 15
  }
}
```

---

## Phoropter Control Actions

### 1. Sphere Adjustments

#### Action: adjust_sphere_positive
```json
{
  "action": "adjust_sphere_positive",
  "parameter": "SPH",
  "direction": "positive",
  "magnitude": 0.25,
  "reason": "Patient prefers higher sphere (more plus/less minus)"
}
```

**When:** Patient says "First lens is clearer" when first lens has higher SPH  
**Example:**
```
Current: SPH -0.50
First lens: SPH -0.25 (more positive)
Second lens: SPH -0.50 (more negative)
Patient: "First lens"
Action: adjust_sphere_positive (+0.25D) → SPH becomes -0.25
```

#### Action: adjust_sphere_negative
```json
{
  "action": "adjust_sphere_negative",
  "parameter": "SPH",
  "direction": "negative",
  "magnitude": -0.25,
  "reason": "Patient prefers lower sphere (less plus/more minus)"
}
```

**When:** Patient says "First lens is clearer" when first lens has lower SPH  
**Example:**
```
Current: SPH 0.0
First lens: SPH -0.25 (more negative)
Second lens: SPH 0.0 (less negative)
Patient: "First lens"
Action: adjust_sphere_negative (-0.25D) → SPH becomes -0.25
```

### 2. Cylinder Adjustments

#### Action: adjust_cylinder_positive
```json
{
  "action": "adjust_cylinder_positive",
  "parameter": "CYL",
  "direction": "positive",
  "magnitude": 0.25,
  "reason": "Patient needs more cylinder correction"
}
```

#### Action: adjust_cylinder_negative
```json
{
  "action": "adjust_cylinder_negative",
  "parameter": "CYL",
  "direction": "negative",
  "magnitude": -0.25,
  "reason": "Patient needs less cylinder correction"
}
```

### 3. Axis Adjustments

#### Action: adjust_axis_clockwise
```json
{
  "action": "adjust_axis_clockwise",
  "parameter": "AXIS",
  "direction": "clockwise",
  "magnitude": 5,
  "reason": "Patient prefers axis rotated clockwise"
}
```

#### Action: adjust_axis_counterclockwise
```json
{
  "action": "adjust_axis_counterclockwise",
  "parameter": "AXIS",
  "direction": "counterclockwise",
  "magnitude": -5,
  "reason": "Patient prefers axis rotated counterclockwise"
}
```

### 4. No Adjustment Actions

#### Action: no_action
```json
{
  "action": "no_action",
  "reason": "Patient reports both lenses are equally clear"
}
```

**When:** Patient says "Both same" or "Neither clear"

#### Action: repeat_presentation
```json
{
  "action": "repeat_presentation",
  "reason": "Patient response unclear, need to re-present same lenses"
}
```

**When:** Patient response quality is "ambiguous" or "unclear"

#### Action: escalate
```json
{
  "action": "escalate",
  "reason": "Red flag detected or safety concern"
}
```

**When:** Red flag detected (pain, vision loss, etc.)

---

## Real-World Examples

### Example 1: Patient Prefers Second Lens (More Positive Sphere)

```json
{
  "command": "present_lens_pair",
  "step": "6",
  "substep": "6.1",
  "eye": "OD",
  "lens_pair": {
    "lens_1": {"SPH": -0.75, "CYL": 0, "AXIS": 0},
    "lens_2": {"SPH": -0.50, "CYL": 0, "AXIS": 0}
  },
  "question": "Which lens makes the dot sharper and rounder?",
  "options": ["First lens", "Second lens", "Both same", "Neither clear"],
  
  "patient_response": {
    "raw_response": "The second one is definitely clearer",
    "selected_option": "Second lens",
    "confidence": 0.92,
    "intent": "refraction_feedback",
    "response_quality": "clear"
  },
  
  "phoropter_control": {
    "action": "adjust_sphere_positive",
    "eye": "OD",
    "current_lens": {"SPH": -0.75, "CYL": 0, "AXIS": 0},
    "preferred_lens": {"SPH": -0.50, "CYL": 0, "AXIS": 0},
    "adjustment": {
      "parameter": "SPH",
      "direction": "positive",
      "magnitude": 0.25,
      "new_value": -0.50
    },
    "clinical_decision": "Add +0.25D sphere. New prescription: SPH -0.50",
    "next_step": "6.2"
  }
}
```

**Analysis:**
- Patient chose second lens (SPH -0.50 is more positive than SPH -0.75)
- Action: Add positive sphere (+0.25D)
- Result: Sphere changes from -0.75 to -0.50

---

### Example 2: Patient Reports Both Same

```json
{
  "command": "present_lens_pair",
  "step": "6",
  "substep": "6.2",
  "eye": "OS",
  "lens_pair": {
    "lens_1": {"SPH": -1.00, "CYL": -0.25, "AXIS": 180},
    "lens_2": {"SPH": -1.00, "CYL": -0.50, "AXIS": 180}
  },
  "question": "Which lens is clearer for astigmatism correction?",
  "options": ["First lens", "Second lens", "Both same", "Neither clear"],
  
  "patient_response": {
    "raw_response": "They both look the same to me",
    "selected_option": "Both same",
    "confidence": 0.65,
    "intent": "refraction_feedback",
    "response_quality": "ambiguous"
  },
  
  "phoropter_control": {
    "action": "repeat_presentation",
    "eye": "OS",
    "reason": "Patient uncertain about cylinder difference. Response quality is ambiguous (confidence 0.65 < 0.8). Repeat lens pair presentation.",
    "next_step": "6.2"
  }
}
```

**Analysis:**
- Patient says "Both same" but confidence is only 0.65 (ambiguous)
- Action: Repeat presentation (stay on same step)
- Result: Ask again until patient gives clear response

---

### Example 3: Red Flag Detected - Emergency Escalation

```json
{
  "command": "present_lens_pair",
  "step": "6",
  "substep": "6.3",
  "eye": "OS",
  "lens_pair": {
    "lens_1": {"SPH": -1.25, "CYL": 0, "AXIS": 0},
    "lens_2": {"SPH": -1.00, "CYL": 0, "AXIS": 0}
  },
  "question": "Which lens makes the dot sharper?",
  "options": ["First lens", "Second lens", "Both same", "Neither clear"],
  
  "patient_response": {
    "raw_response": "I'm having severe eye pain and the vision is blurry",
    "selected_option": null,
    "confidence": 0,
    "intent": "health_emergency",
    "red_flag": true,
    "red_flag_keywords": ["severe", "pain", "blurry"],
    "response_quality": "emergency"
  },
  
  "phoropter_control": {
    "action": "escalate",
    "severity": "HIGH",
    "reason": "RED FLAG: Patient reported severe eye pain and vision loss",
    "clinical_decision": "HALT EXAMINATION IMMEDIATELY. Refer to professional optometrist/ophthalmologist.",
    "next_step": "escalate_to_professional"
  }
}
```

**Analysis:**
- Patient reports emergency symptoms
- Red flags: "severe", "pain", "blurry"
- Action: Escalate immediately
- Result: Shutdown phoropter, halt exam, recommend professional care

---

### Example 4: Axis Adjustment (Jackson Cross Cylinder)

```json
{
  "command": "present_lens_pair",
  "step": "6",
  "substep": "6.2",
  "eye": "OD",
  "lens_pair": {
    "lens_1": {"SPH": -1.50, "CYL": -0.75, "AXIS": 175},
    "lens_2": {"SPH": -1.50, "CYL": -0.75, "AXIS": 180}
  },
  "question": "Which axis orientation is clearer - 175 or 180?",
  "options": ["First lens (175°)", "Second lens (180°)", "Both same", "Neither clear"],
  
  "patient_response": {
    "raw_response": "The 175 angle looks sharper",
    "selected_option": "First lens (175°)",
    "confidence": 0.79,
    "intent": "refraction_feedback",
    "response_quality": "clear"
  },
  
  "phoropter_control": {
    "action": "adjust_axis_counterclockwise",
    "eye": "OD",
    "current_lens": {"SPH": -1.50, "CYL": -0.75, "AXIS": 180},
    "preferred_lens": {"SPH": -1.50, "CYL": -0.75, "AXIS": 175},
    "adjustment": {
      "parameter": "AXIS",
      "direction": "counterclockwise",
      "magnitude": -5,
      "new_value": 175
    },
    "clinical_decision": "Rotate axis counterclockwise by 5°. New axis: 175°",
    "next_step": "6.3"
  }
}
```

**Analysis:**
- Patient chose first lens with axis 175°
- Action: Rotate axis counterclockwise by 5° (from 180° to 175°)
- Result: AXIS changes from 180 to 175

---

### Example 5: Invalid Option Number - Stay on Same Step

```json
{
  "command": "present_lens_pair",
  "step": "6",
  "substep": "6.1",
  "eye": "OS",
  "lens_pair": {
    "lens_1": {"SPH": -0.25, "CYL": 0, "AXIS": 0},
    "lens_2": {"SPH": 0.0, "CYL": 0, "AXIS": 0}
  },
  "question": "Which lens makes the dot sharper and rounder?",
  "options": ["First lens", "Second lens", "Both same", "Neither clear"],
  
  "patient_response": {
    "raw_response": "5",
    "selected_option": null,
    "confidence": 0,
    "intent": "invalid",
    "response_quality": "invalid"
  },
  
  "phoropter_control": {
    "action": "no_action",
    "reason": "Invalid option selected (5 is out of range 1-4). Re-present question.",
    "error_message": "Invalid option. Please select 1 to 4, or type one of the options.",
    "next_step": "6.1"
  }
}
```

**Analysis:**
- Patient entered "5" but only 4 options available (1-4)
- Action: no_action (stay on same step)
- Result: Ask question again at step 6.1

---

## Phoropter Control Command Mapping

```
PATIENT RESPONSE          PARAMETER      ACTION
═════════════════════════════════════════════════
"First lens" (higher SPH) → SPH        → adjust_sphere_positive
"First lens" (lower SPH)  → SPH        → adjust_sphere_negative
"Second lens" (higher SPH)→ SPH        → adjust_sphere_positive
"Second lens" (lower SPH) → SPH        → adjust_sphere_negative

"First lens" (higher CYL) → CYL        → adjust_cylinder_positive
"First lens" (lower CYL)  → CYL        → adjust_cylinder_negative
"Second lens" (higher CYL)→ CYL        → adjust_cylinder_positive
"Second lens" (lower CYL) → CYL        → adjust_cylinder_negative

"First lens" (180°)       → AXIS       → adjust_axis_clockwise
"First lens" (170°)       → AXIS       → adjust_axis_counterclockwise
"Second lens" (175°)      → AXIS       → adjust_axis_clockwise
"Second lens" (170°)      → AXIS       → adjust_axis_counterclockwise

"Both same"               → N/A        → no_action
"Neither clear"           → N/A        → repeat_presentation
[Red flag keywords]       → N/A        → escalate
[Ambiguous response]      → N/A        → repeat_presentation
[Invalid option]          → N/A        → no_action
```

---

## Integration with Phoropter Hardware

### Step 1: Send Control Command
```python
control = phoropter_result["phoropter_control"]
action = control["action"]

if action == "adjust_sphere_positive":
    phoropter.adjust_sphere(eye, magnitude=0.25)

elif action == "adjust_sphere_negative":
    phoropter.adjust_sphere(eye, magnitude=-0.25)

elif action == "adjust_cylinder_positive":
    phoropter.adjust_cylinder(eye, magnitude=0.25)

elif action == "adjust_cylinder_negative":
    phoropter.adjust_cylinder(eye, magnitude=-0.25)

elif action == "adjust_axis_clockwise":
    phoropter.rotate_axis(eye, degrees=5)

elif action == "adjust_axis_counterclockwise":
    phoropter.rotate_axis(eye, degrees=-5)

elif action == "no_action":
    pass  # No adjustment

elif action == "repeat_presentation":
    pass  # Show same lenses again

elif action == "escalate":
    phoropter.shutdown()  # Safety shutdown
```

### Step 2: Verify Device Response
```python
new_state = phoropter.get_device_state()
assert new_state["OD"]["SPH"] == control["adjustment"]["new_value"]
assert new_state["OD"]["CYL"] == control["adjustment"]["new_value"]
assert new_state["OD"]["AXIS"] == control["adjustment"]["new_value"]
```

---

## Safety Constraints

Before executing phoropter command, validate:

```python
# 1. Maximum adjustment per step
assert abs(magnitude) <= 0.50  # Sphere/Cylinder max
assert abs(magnitude) <= 10    # Axis max

# 2. Valid parameter
assert parameter in ["SPH", "CYL", "AXIS"]

# 3. Valid eye
assert eye in ["OD", "OS"]

# 4. Response quality check
assert response_quality in ["clear"]  # Only progress on clear

# 5. Red flag check
assert red_flag == False  # No escalation
```

---

## Summary

**Complete JSON now includes:**

✅ **Lens Presentation** - What lenses are shown  
✅ **Patient Response** - How patient answered  
✅ **Phoropter Control** - What device should do  
✅ **Clinical Decision** - Why this adjustment  
✅ **Audit Trail** - Full traceability  

**Phoropter immediately knows:**
- Which eye to adjust (OD/OS)
- Which parameter to change (SPH/CYL/AXIS)
- What direction and magnitude
- What the new value should be
- Whether to proceed or escalate

This ensures **safe, traceable, clinically sound device control**.
