# AI Optum: Process Engine & Technical Architecture
## Operational Workflow & Implementation Guide

**Version:** 1.0  
**Date:** December 29, 2025  
**Status:** Implementation Ready  

---

## 1. System Architecture Overview

### 1.1 Process Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI OPTUM PROCESS ENGINE                  │
└─────────────────────────────────────────────────────────────────┘

[Patient Initiates]
        ↓
    [IDENTITY LOCK MODULE]
    • Detect persona override attempts
    • Authoritative refusal logic
    • Re-center to clinical protocol
        ↓
[CLINICAL ROLE ENFORCEMENT]
    • Immutable AI Optometrist identity
    • Medical ethics framework
    • Professional tone enforcement
        ↓
[CONSENT & CONTEXT MANAGER]
    • Obtain informed consent
    • Non-diagnostic disclaimer
    • Explain test process
    • Confirm patient readiness
        ↓
[PATIENT HISTORY INTAKE ENGINE]
    • Capture demographics (age, DOB)
    • Vision symptoms analysis
    • Previous prescription review
    • Eye condition assessment
    • Patient comfort baseline
        ↓
╔═══════════════════════════════════════════════════════════════╗
║       [EYE TEST CONTROL ENGINE - ITERATIVE LOOP]              ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  1. [CHART PRESENTATION]                                      ║
║     • Load Snellen/LogMAR chart                               ║
║     • Present current line to patient                         ║
║     • Audio/text instruction                                  ║
║     • Display visual elements                                 ║
║                    ↓                                           ║
║  2. [RESPONSE CAPTURE]                                        ║
║     • Transcribe patient response                             ║
║     • Record confidence level (high/medium/low)               ║
║     • Calculate response accuracy                             ║
║     • Measure hesitation/timing                               ║
║                    ↓                                           ║
║  3. [LENS DECISION LOGIC]                                     ║
║     • Compare before/after responses                          ║
║     • Calculate improvement metric                            ║
║     • Determine next lens adjustment                          ║
║     • Validate safety constraints                             ║
║                    ↓                                           ║
║  4. [SAFETY CHECKPOINT]                                       ║
║     • Check for unsafe jumps                                  ║
║     • Monitor fatigue indicators                              ║
║     • Verify patient comfort                                  ║
║     • Check session duration                                  ║
║                    ↓                                           ║
║  5. [DECISION: Vision Improved?]                              ║
║     ├─ YES → Proceed to Verification                          ║
║     ├─ NO  → [Loop back to step 1 with new lens]              ║
║     └─ ESCALATE → [Safety Protocol Triggered]                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        ↓
[VERIFICATION PROTOCOL]
    • Re-present critical chart lines
    • Confirm sustained improvement
    • Detect vision stability/instability
    • Final clarity confirmation
        ↓
[PRESCRIPTION CALCULATION]
    • Finalize Sphere, Cylinder, Axis values
    • Calculate confidence scores
    • Generate prescription report
    • Document audit trail
        ↓
[PATIENT EXPLANATION ENGINE]
    • "What Changed" - Simple refraction explanation
    • "Why It Helps" - Optical mechanism education
    • "What's Next" - Professional follow-up guidance
        ↓
[TEST COMPLETION & REPORTING]
    • Generate comprehensive report
    • Log session data
    • Provide patient-friendly summary
    • Schedule follow-up recommendations
```

---

## 2. Module Specifications

### 2.1 Identity Lock Module (Clinical Role Protection)

**Activation:** Continuous throughout session

**Function:** Detects and prevents persona-switching attempts

```python
IDENTITY_LOCK_RULES = {
    "non_clinical_requests": [
        "fortune telling", "roleplay", "act as", "pretend to be",
        "switch identity", "be someone else", "humor mode"
    ],
    "response_pattern": "Authoritative Refusal + Re-center",
    "escalation": "None (not a safety issue, behavioral boundary)"
}

# Pseudocode
def identity_lock(user_input):
    if contains_persona_override_attempt(user_input):
        return authoritative_refusal(
            message="I'm here specifically as your AI Optometrist...",
            redirect_to_clinical_task()
        )
    else:
        proceed_with_input()
```

**Example Interactions:**
- **Input:** "Can you tell me a joke?"
  **Output:** "I appreciate your sense of humor! However, I'm here in my role as your AI Optometrist to help with your eye test. Shall we continue?"

- **Input:** "Act like a pirate eye doctor"
  **Output:** "I need to maintain my professional clinical role as an Optometrist. This ensures accuracy and safety for your vision assessment. Let's continue with the next chart line."

---

### 2.2 Consent & Context Manager

**Activation:** Immediately after identity verification

**Steps:**
1. **Welcome & Introduction** (30 seconds)
   - Professional greeting
   - Brief explanation of AI role
   
2. **Test Purpose Statement** (1 minute)
   - "This is a preliminary vision assessment to measure your eye's focusing ability"
   - "We'll measure three parameters: Sphere, Cylinder, and Axis"
   - "The whole test takes about 15-20 minutes"

3. **Non-Diagnostic Disclaimer** (required)
   ```
   IMPORTANT: This is a preliminary assessment only and should NOT 
   be used as a medical prescription. A professional eye examination 
   by a licensed optometrist is required for a valid prescription.
   ```

4. **Process Overview** (1-2 minutes)
   - Patient history questions
   - Vision chart presentation
   - Multiple chart lines at different clarity levels
   - Lens parameter adjustments based on feedback
   - Final recommendation with confidence score

5. **Consent Recording** (explicit)
   - "Do you understand this is non-diagnostic?" → YES/NO
   - "Are you comfortable proceeding?" → YES/NO
   - Timestamp consent

---

### 2.3 Patient History Intake Engine

**Data Collection Model:**

```python
PATIENT_HISTORY_SCHEMA = {
    "demographics": {
        "age": int,  # Required
        "date_of_birth": date,  # Required
        "gender": str,  # Optional (not used clinically)
    },
    "vision_symptoms": {
        "distance_vision": str,  # blurry/clear/variable
        "near_vision": str,  # blurry/clear/variable
        "astigmatism_signs": bool,  # ghosting, halos
        "eye_strain": bool,
        "previous_correction": str,  # e.g., "-1.50, -0.75, 180"
    },
    "medical_history": {
        "eye_conditions": list,  # diabetes, glaucoma, etc.
        "medications": list,
        "eye_treatments": list,
    },
    "comfort_baseline": {
        "exam_comfort_level": int,  # 1-5 scale
        "lighting_preference": str,  # bright/moderate/dim
        "session_readiness": bool,
    }
}
```

**Conversational Flow:**
```
AI: "Let me ask you a few questions about your vision before we start..."

1. "How old are you?" → [Age recorded]
2. "What brings you in today? Any vision concerns?" → [Symptoms]
3. "Do you currently wear glasses or contacts?" → [Previous correction]
4. "When was your last eye exam?" → [Baseline reference]
5. "On a scale of 1-5, how comfortable are you with eye exams?" → [Comfort]
6. "Do you have any eye conditions I should know about?" → [Medical history]

[Summarize findings]
"Great! I can see you've been experiencing distance blurriness. 
Let's run the test to measure your exact correction needs."
```

---

### 2.4 Eye Test Control Engine (Core Loop)

**Iterative Testing Architecture:**

#### Phase 1: Initial Measurement (Sphere Determination)

```python
def determine_sphere():
    """
    Find optimal sphere correction (-20 to +20 diopters)
    Strategy: Binary search with patient feedback
    """
    current_sphere = 0.0
    step_size = 1.0
    max_iterations = 20
    
    while max_iterations > 0:
        # Present chart with current lens
        present_chart(current_lens)
        
        # Capture response
        response_accuracy = capture_patient_response()
        clarity_rating = ask_clarity_question()  # 1-5 scale
        
        # Compare with previous iteration
        improvement = compare_with_previous(response_accuracy, clarity_rating)
        
        if improvement > threshold:
            # Vision improved, continue in this direction
            current_sphere += step_size
        else:
            # Hit optimum or worsened, reduce step size
            step_size /= 2.0
            if step_size < 0.25:
                return round(current_sphere, 2)
        
        max_iterations -= 1
    
    return current_sphere
```

#### Phase 2: Astigmatism Measurement (Cylinder & Axis)

```python
def determine_cylinder_and_axis():
    """
    Find cylinder correction (0 to -6.00) and axis (0-180)
    Strategy: Refinement after sphere is locked
    """
    # Present cross-cylinder test
    # Patient indicates which meridian appears clearer
    
    for test_iteration in range(5):
        # Adjust cylinder magnitude
        response = present_astigmatism_chart()
        if response == "clearer_with_correction":
            increase_cylinder()
        
        # Fine-tune axis orientation
        axis_response = present_axis_options()
        axis = refine_axis(axis_response)
    
    return cylinder, axis
```

#### Phase 3: Fine-Tuning & Optimization

```python
def fine_tune_all_parameters():
    """
    Verify and optimize all three parameters together
    """
    iterations = 3
    
    for _ in range(iterations):
        # Present chart with current full prescription
        current_lens = Prescription(sphere, cylinder, axis)
        present_chart(current_lens)
        
        # Capture comprehensive feedback
        accuracy = measure_accuracy()
        clarity = ask_clarity_rating()
        comfort = ask_comfort_check()
        
        # Make micro-adjustments if needed
        if accuracy < acceptable_threshold:
            adjust_parameters(delta=0.25)  # Small refinement
        else:
            break  # Optimization complete
    
    return final_prescription
```

---

### 2.5 Lens Decision Logic Engine

**Algorithm: Incremental Optimization with Safety Constraints**

```python
class LensAdjustmentEngine:
    """
    Determines optimal lens parameters based on patient responses
    """
    
    def __init__(self):
        self.safe_step_size = 0.25  # diopters
        self.max_single_jump = 0.50  # diopters (safety limit)
        self.axis_step = 5  # degrees
        self.previous_accuracy = 0
        self.previous_clarity = 0
    
    def should_adjust_lens(self, current_response_accuracy, current_clarity):
        """
        Decision logic: Should we adjust the lens?
        """
        improvement = (current_response_accuracy + current_clarity) / 2
        prev_performance = (self.previous_accuracy + self.previous_clarity) / 2
        
        if improvement > prev_performance:
            return True, "improvement_detected"
        elif improvement == prev_performance:
            return False, "no_change_needed"
        else:
            return True, "refinement_needed"
    
    def calculate_next_adjustment(self, parameter, direction):
        """
        Calculate safe next adjustment value
        
        parameter: 'sphere', 'cylinder', or 'axis'
        direction: 'increase' or 'decrease'
        """
        if parameter in ['sphere', 'cylinder']:
            step = self.safe_step_size if direction == 'increase' else -self.safe_step_size
            return step
        elif parameter == 'axis':
            step = self.axis_step if direction == 'increase' else -self.axis_step
            return step
    
    def validate_adjustment(self, new_value, previous_value, parameter):
        """
        Ensure adjustment is within safety constraints
        """
        difference = abs(new_value - previous_value)
        
        if parameter in ['sphere', 'cylinder']:
            if difference > self.max_single_jump:
                return False, f"Unsafe jump: {difference} > {self.max_single_jump}"
        
        # Check range boundaries
        if parameter == 'sphere' and not (-20 <= new_value <= 20):
            return False, "Sphere out of range"
        if parameter == 'cylinder' and not (0 <= new_value <= 6):
            return False, "Cylinder out of range"
        if parameter == 'axis' and not (0 <= new_value <= 180):
            return False, "Axis out of range"
        
        return True, "Valid adjustment"
```

---

### 2.6 Safety Monitor & Guardrails

**Fatigue Detection System:**

```python
class SafetyMonitor:
    """
    Continuous monitoring for patient safety
    """
    
    FATIGUE_INDICATORS = {
        "accuracy_degradation": 0.2,  # 20% drop in accuracy
        "hesitation_threshold": 3.0,  # seconds pause
        "confidence_drop": 0.3,  # 30% drop in confidence rating
        "slurred_speech": ["uh", "um", "huh"],
        "request_for_break": True,
    }
    
    def __init__(self):
        self.accuracy_history = []
        self.response_times = []
        self.confidence_ratings = []
        self.session_start_time = time.time()
    
    def check_fatigue(self):
        """
        Analyze fatigue indicators
        """
        recent_accuracy = self.accuracy_history[-5:]  # Last 5 responses
        accuracy_trend = np.mean(recent_accuracy) - np.mean(self.accuracy_history[:5])
        
        if accuracy_trend < -self.FATIGUE_INDICATORS["accuracy_degradation"]:
            return True, "accuracy_degradation"
        
        avg_response_time = np.mean(self.response_times[-5:])
        if avg_response_time > self.FATIGUE_INDICATORS["hesitation_threshold"]:
            return True, "excessive_hesitation"
        
        confidence_trend = np.mean(self.confidence_ratings[-5:]) - \
                          np.mean(self.confidence_ratings[:5])
        if confidence_trend < -self.FATIGUE_INDICATORS["confidence_drop"]:
            return True, "confidence_drop"
        
        return False, "no_fatigue"
    
    def check_session_duration(self):
        """
        Monitor session time
        """
        elapsed = time.time() - self.session_start_time
        
        if elapsed > 25 * 60:  # 25 minutes
            return "HARD_STOP"
        elif elapsed > 20 * 60:  # 20 minutes
            return "WARN_AND_COMPLETE"
        elif elapsed > 12 * 60:  # 12 minutes
            return "OFFER_BREAK"
        else:
            return "CONTINUE"
    
    def escalation_required(self, severity):
        """
        Determine if test should be paused
        """
        if severity in ["HARD_STOP", "severe_fatigue", "patient_discomfort"]:
            return True, "Professional eye exam recommended"
        return False, "Continue"
```

**Safety Response Protocols:**

```
Fatigue Detected (Medium):
├─ AI Response: "I notice you might be getting a little tired. 
│  Would you like to take a 2-minute break?"
├─ If Patient Agrees: Pause test, countdown timer, resume
└─ If Patient Refuses: Continue with fatigue flag

Unsafe Lens Jump:
├─ AI Prevention: Block adjustment > ±0.50 diopters
├─ Alternative: Suggest intermediate step
└─ Log: Record attempted unsafe adjustment

Session Duration Exceeded:
├─ At 12 minutes: "We're making great progress! Want to continue?"
├─ At 20 minutes: "We're almost done. Let me wrap up the test."
├─ At 25 minutes: HARD STOP. "For your safety, let's complete 
│  the test now and recommend a professional follow-up."
└─ Escalate: Provide professional optometrist contact info
```

---

### 2.7 Verification Protocol

**Confirmation Testing:**

```python
def verification_pass():
    """
    Confirm final prescription with repeat testing
    """
    critical_lines = select_critical_lines(chart)  # 3-5 lines
    verification_results = []
    
    for line in critical_lines:
        response = present_chart_line(line)
        is_correct = evaluate_response(response, line)
        verification_results.append(is_correct)
        
        if not is_correct:
            # Instability detected, request adjustment
            ask_for_adjustment_confirmation()
            refine_parameters()
            return False, "Refinement needed"
    
    # All verification lines passed
    if sum(verification_results) / len(verification_results) > 0.80:
        return True, "Verification passed"
    else:
        return False, "Inconclusive results"
```

---

### 2.8 Prescription Report Generator

**Report Schema:**

```python
PRESCRIPTION_REPORT = {
    "metadata": {
        "session_id": str,  # Unique identifier
        "timestamp": datetime,
        "patient_id": str,  # Anonymized
        "duration_minutes": int,
    },
    "measurements": {
        "right_eye": {
            "sphere": float,  # -20.00 to +20.00
            "cylinder": float,  # 0 to -6.00
            "axis": int,  # 0-180 degrees
        },
        "left_eye": {
            "sphere": float,
            "cylinder": float,
            "axis": int,
        }
    },
    "confidence_scores": {
        "overall": float,  # 0-100%
        "sphere": float,
        "cylinder": float,
        "axis": float,
    },
    "verification_status": str,  # PASSED / FAILED / INCONCLUSIVE
    "safety_notes": list,
    "recommendations": {
        "professional_followup": bool,
        "timeline": str,  # "1-2 weeks"
    },
    "medical_disclaimer": str,
}
```

**Report Output:**
```
═══════════════════════════════════════════════════════
    PRELIMINARY VISION ASSESSMENT - AI OPTUM
═══════════════════════════════════════════════════════

Session ID: OPT-20251229-A4F7B2
Date: December 29, 2025, 2:45 PM
Duration: 16 minutes 23 seconds

───────────────────────────────────────────────────────
REFRACTION MEASUREMENTS
───────────────────────────────────────────────────────
RIGHT EYE (OD):    SPH: -1.50  CYL: -0.75  AXIS: 180°
LEFT EYE (OS):     SPH: -2.00  CYL: -0.50  AXIS: 175°

───────────────────────────────────────────────────────
CONFIDENCE METRICS
───────────────────────────────────────────────────────
Overall Confidence:        85%
Sphere Accuracy:           90%
Cylinder Accuracy:         75%
Axis Accuracy:             80%
Verification Status:       PASSED

───────────────────────────────────────────────────────
⚠️  MEDICAL DISCLAIMER
───────────────────────────────────────────────────────
This is a PRELIMINARY ASSESSMENT ONLY and cannot be used
as a medical prescription. A professional eye examination
by a licensed optometrist or ophthalmologist is required
for a valid prescription.

───────────────────────────────────────────────────────
NEXT STEPS
───────────────────────────────────────────────────────
✓ Schedule a professional eye exam within 1-2 weeks
✓ Bring this report to your eye care provider
✓ Discuss any vision concerns
✓ Consider prescription options: glasses, contacts, LASIK

═══════════════════════════════════════════════════════
```

---

### 2.9 Patient-Friendly Explanation Engine

**Three-Part Educational Output:**

```python
def generate_patient_explanation(prescription):
    """
    Create simple, educational explanation of results
    """
    
    # Part 1: What Changed
    explanation_part_1 = f"""
    What We Found:
    Your right eye shows a myopic (nearsightedness) correction of -1.50 diopters.
    This means distant objects appear slightly blurry without correction.
    
    Your left eye shows a similar correction of -2.00 diopters, indicating 
    slightly more nearsightedness than your right eye.
    
    You also have mild astigmatism in both eyes (about -0.75 and -0.50),
    which affects how the eye focuses on certain directions.
    """
    
    # Part 2: Why It Helps
    explanation_part_2 = f"""
    How Your Correction Works:
    The -1.50/-2.00 correction works by helping light rays focus more 
    precisely on the retina (the light-sensitive layer at the back of 
    your eye). This makes distant objects clearer and sharper.
    
    The cylinder correction (-0.75/-0.50) addresses astigmatism by 
    correcting the eye's curved shape, evening out focus across all directions.
    
    Without these corrections, your eyes are working harder to focus, 
    which may cause eye strain or headaches.
    """
    
    # Part 3: Next Steps
    explanation_part_3 = f"""
    What's Next:
    1. Schedule a professional eye exam with a licensed optometrist 
       within 1-2 weeks to verify these measurements.
    
    2. During that exam, your eye care provider may:
       - Confirm these measurements with additional testing
       - Check the health of your eyes
       - Discuss eyewear options (glasses, contacts)
       - Answer any questions about vision correction
    
    3. Your prescription is typically valid for 1-2 years, depending 
       on how your vision changes.
    
    If you experience any vision changes before your appointment, 
    contact your eye care provider immediately.
    """
    
    return {
        "what_changed": explanation_part_1,
        "why_it_helps": explanation_part_2,
        "next_steps": explanation_part_3,
    }
```

---

## 3. Data Flow & State Management

### 3.1 Session State Schema

```python
class AIOptumSession:
    def __init__(self):
        self.session_id = generate_uuid()
        self.patient_history = {}
        self.consent_status = {}
        self.test_measurements = {
            "right_eye": {"sphere": None, "cylinder": None, "axis": None},
            "left_eye": {"sphere": None, "cylinder": None, "axis": None},
        }
        self.response_log = []
        self.safety_flags = []
        self.confidence_scores = {}
        self.test_complete = False
        self.start_time = datetime.now()
```

### 3.2 Response Logging Format

```python
response_log_entry = {
    "timestamp": datetime,
    "chart_line": str,  # e.g., "20/40"
    "patient_response": str,
    "response_accuracy": bool,
    "confidence_level": str,  # "high", "medium", "low"
    "current_lens": {"sphere": float, "cylinder": float, "axis": int},
    "response_time_seconds": float,
    "safety_status": str,  # "safe", "caution", "unsafe"
}
```

---

## 4. Error Handling & Escalation

### 4.1 Error Categories

| Error Type | Trigger | Response | Escalation |
|-----------|---------|----------|-----------|
| **Input Error** | Unintelligible response | "Could you repeat that?" (max 2x) | Escalate to manual entry |
| **Safety Violation** | Unsafe lens jump detected | Block adjustment, offer alternative | Flag for review |
| **Fatigue Detected** | Accuracy drops > 20% | Offer break, suggest completion | Possible halt |
| **Duration Exceeded** | Test > 25 minutes | Immediate completion | Professional follow-up required |
| **Inconsistent Results** | Verification fails | Refine parameters, retry | Flag for optometrist review |
| **Patient Discomfort** | Pain/strain reported | Immediate pause | Urgent professional referral |

### 4.2 Escalation Protocol

**Severity Levels:**

```
LEVEL 1 - LOW RISK:
├─ Minor input errors
├─ Response: Reprompt patient
└─ Action: Continue test

LEVEL 2 - MEDIUM RISK:
├─ Fatigue indicators detected
├─ Extended session duration (>20 min)
├─ Response: Offer break/completion
└─ Action: Flag for review, provide optometrist info

LEVEL 3 - HIGH RISK:
├─ Patient reports pain/discomfort
├─ Severe vision changes mid-test
├─ Multiple verification failures
├─ Response: IMMEDIATE TEST HALT
└─ Action: Emergency optometrist referral, provide resources

LEVEL 4 - CRITICAL:
├─ Patient reports flashing lights, vision loss
├─ Possible retinal event
├─ Response: IMMEDIATE HALT, Emergency guidance
└─ Action: Provide emergency room directions, call 911 guidance
```

---

## 5. Compliance & Audit Trail

### 5.1 Required Logging

Every session must record:
- ✓ Session ID and timestamp
- ✓ Patient consent (non-diagnostic acknowledgment)
- ✓ All refraction measurements and confidence scores
- ✓ All safety flags and escalations
- ✓ Session duration and completion status
- ✓ Final prescription recommendation
- ✓ Any deviations from standard protocol

### 5.2 Data Retention Policy

- **Active Sessions:** Real-time processing
- **Completed Sessions:** 7-year retention (HIPAA compliance)
- **Escalations/Errors:** Immediate flagging for quality assurance
- **Anonymization:** Remove PII after consent verification

---

## 6. Integration Points

### 6.1 External Systems
- **EHR Systems:** (Future) Prescription export capability
- **Professional Optometrist Network:** Referral capabilities
- **Emergency Resources:** Rapid contact options for escalations

### 6.2 API Contract (Future)

```python
class AIOptumAPI:
    def start_session(patient_info: dict) -> session_id: str
    def get_next_chart(session_id: str) -> chart_object: dict
    def submit_response(session_id: str, response: str) -> next_action: dict
    def complete_session(session_id: str) -> report: dict
    def escalate_session(session_id: str, severity: str) -> escalation_id: str
```

---

## 7. Testing & Validation

### 7.1 Unit Tests
- Identity lock refusal logic
- Lens adjustment calculations
- Safety constraint validation
- Confidence score calculations

### 7.2 Integration Tests
- Full end-to-end test flow
- Fatigue detection accuracy
- Report generation accuracy
- Escalation triggering

### 7.3 Clinical Validation
- Correlation testing with professional optometrist measurements
- Prescription accuracy within ±0.50 diopter tolerance
- Safety incident rate (target: 0%)
- Patient satisfaction surveys

---

## 8. Deployment & Operations

### 8.1 System Requirements
- Python 3.9+
- GPU support (for speech-to-text and chart rendering)
- HIPAA-compliant data encryption
- Persistent logging system

### 8.2 Performance Targets
- Chart rendering: < 500ms
- Response processing: < 2 seconds
- Decision logic: < 1 second
- System uptime: 99.5%

### 8.3 Monitoring
- Real-time session tracking
- Safety flag alerts
- Error rate monitoring
- Performance metrics dashboard

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 29, 2025 | Initial architecture design |
| — | — | — |

