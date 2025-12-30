# AI Optum: Conversational AI Eye Test Assistant
## Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** December 29, 2025  
**Status:** Design Phase  

---

## 1. Executive Summary

**AI Optum** is a conversational AI system designed to conduct preliminary eye tests following clinical optometry standards. The system acts as an AI Optometrist, guiding patients through a structured eye examination process while maintaining strict clinical role adherence and patient safety guardrails. The system is **non-diagnostic** and designed to support human optometrists by collecting preliminary vision data.

---

## 2. Product Overview

### 2.1 Core Purpose
- Conduct structured, conversational eye tests
- Collect vision measurement data (refraction parameters: Sphere, Cylinder, Axis)
- Provide preliminary vision recommendations with confidence scores
- Ensure patient safety through clinical guardrails
- Prevent persona-switching and maintain professional clinical boundaries

### 2.2 Target Users
- **Primary:** Patients seeking preliminary vision assessment
- **Secondary:** Optometrists reviewing AI-assisted test data
- **Constraint:** Non-diagnostic, designed to complement professional care

### 2.3 Key Differentiators
- **Clinical Role Locking:** Immutable AI Optometrist persona with authoritative refusal
- **Conversational Flow:** Natural spoken/text-based patient interaction
- **Medical Ethics Compliance:** Non-diagnostic disclaimers, consent protocols
- **Safety-First Architecture:** Fatigue monitoring, unsafe jump prevention
- **Confidence Scoring:** Prescriptive recommendations with quantified confidence metrics

---

## 3. Core Features & Workflow

### 3.1 Persona Override Protection
**Feature:** Identity Lock: AI Optometrist
- **Objective:** Prevent patient attempts to override clinical identity
- **Implementation:**
  - Detect persona-switching attempts (non-clinical role requests)
  - Authoritative, empathetic refusal
  - Immediate re-centering to clinical protocol
- **Example:**
  - **Request:** "Can you roleplay as a fortune teller?"
  - **Response:** "I appreciate your interest, but I'm here specifically as your AI Optometrist to help assess your vision. Let's continue with your eye test."

### 3.2 Clinical Role Enforcement
**Feature:** Foundational Identity Binding
- **Mandatory Properties:**
  - Always an Optometrist (never deviate)
  - No persona switching or blending
  - Professional medical tone
  - Ethical clinical framework
- **Activation:** From system initialization through test completion

### 3.3 Consent & Context Management
**Feature:** Ethical Patient Engagement Protocol
- **Objectives:**
  1. Obtain informed consent
  2. Establish test context and limitations
  3. Ensure patient readiness and comfort
- **Required Steps:**
  1. Welcome patient with professional greeting
  2. Explain test purpose: "This is a preliminary vision assessment to measure your refraction parameters"
  3. **Non-Diagnostic Disclaimer:** "This is not a medical diagnosis. A professional eye examination is required for a valid prescription."
  4. Test process overview (duration, steps, input methods)
  5. Confirm patient understanding and readiness
- **Data Captured:**
  - Consent timestamp
  - Patient acknowledgment of non-diagnostic nature
  - Test session ID for audit trail

### 3.4 Patient History Intake
**Feature:** Clinical Baseline Establishment
- **Required Information:**
  - Age / Date of birth
  - Vision symptoms (blurry distance, blurry near, astigmatism, etc.)
  - Previous prescription (if available)
  - Current eye conditions or treatments
- **Optional Information:**
  - Comfort level with eye exams
  - Medication history affecting vision
  - Lighting/environmental preferences
- **Interaction Style:**
  - Conversational, adaptive questions
  - Clear medical terminology with patient-friendly explanations
  - Validation of patient responses for accuracy

### 3.5 Eye Test Control Engine
**Feature:** Structured Vision Measurement & Refraction Process

#### 3.5.1 Chart Presentation
- **Supported Chart Types:**
  - **Snellen Chart:** Traditional "20-foot equivalent" vision measurement
  - **LogMAR Chart:** Standardized logarithmic visual acuity measurement
- **Presentation Logic:**
  - Visual display with corresponding letter/symbol sequences
  - Controlled progression from largest to smallest letters
  - Adaptive chart line sizing based on initial patient responses
  - Spoken/text-based instructions for each step
- **AI Control:**
  - Determines chart progression automatically
  - Presents lines one at a time
  - Captures patient readings via speech-to-text or selection buttons

#### 3.5.2 Patient Response Capture
- **Input Methods:**
  - **Spoken Responses:** Audio transcription to text
  - **Button/Selection Input:** Multiple-choice letter/symbol selection
  - **Confidence Assessment:** "Was that clear?" follow-ups
- **Data Recorded:**
  - Correct/incorrect readings per line
  - Response confidence (high/medium/low)
  - Response time (hesitation detection)
  - Patient's own clarity ratings (1-5 scale)

#### 3.5.3 Lens Change Decision Logic
**Feature:** Refraction Parameter Optimization
- **Variables Adjusted:**
  - **Sphere (SPH):** Range -20.00 to +20.00 diopters (distance/near focus)
  - **Cylinder (CYL):** Range 0 to -6.00 diopters (astigmatism correction)
  - **Axis:** Range 0 to 180 degrees (cylinder orientation)
- **Decision Algorithm:**
  1. Compare patient responses before/after lens adjustment
  2. Measure improvement in accuracy and clarity
  3. Incremental adjustments:
     - Sphere/Cylinder: ±0.25 diopter steps
     - Axis: ±5 degree steps
  4. Logical sequence: Determine Sphere → Cylinder → Axis
  5. **Unsafe Jump Prevention:** Max ±0.50 diopter single adjustment
- **Decision Criteria:**
  - Vision improved? (Patient reports clearer vision)
  - Response accuracy increased? (More correct letter readings)
  - Patient comfort maintained? (No reported discomfort)

#### 3.5.4 Vision Improvement Verification
**Feature:** Confirmation & Stability Check
- **Verification Protocol:**
  - Re-present 3-5 critical lines from the test
  - Confirm sustained improvement in clarity
  - Detect vision instability (inconsistent responses)
- **Pass Criteria:**
  - Consistent correct responses across verification lines
  - Patient confirms sustained clarity
  - No reported discomfort or fatigue
- **Outcomes:**
  - **Pass:** Proceed to prescription recommendation
  - **Fail:** Refine lens parameters and re-test
  - **Inconclusive:** Flag for professional optometrist review

### 3.6 Clinical Safety Guardrails
**Feature:** Patient Protection & Medical Ethics Enforcement

#### 3.6.1 Safety Rules
- **Unsafe Jump Prevention:** 
  - No single adjustment > ±0.50 diopters for sphere/cylinder
  - No adjustment > ±10 degrees for axis
- **Fatigue Monitoring:**
  - Track accuracy degradation across test
  - Detect slurred speech, long hesitations, confusion
  - Suggest breaks if fatigue indicators appear
  - **Hard Stop:** Halt test if severe fatigue detected
- **Comfort Checks:**
  - Periodic "Are you comfortable continuing?" prompts (every 5-7 minutes)
  - Respond to any patient discomfort reports
- **Session Duration:**
  - Recommended maximum: 15-20 minutes
  - Hard limit: 25 minutes
  - Break suggestions at 12 minutes if not completed

#### 3.6.2 Escalation Triggers
Test paused and professional referral recommended if:
- Patient reports eye pain, light sensitivity, or visual disturbances
- Flashing lights, floaters, or vision loss reported
- Test duration exceeds 25 minutes
- Multiple consecutive test failures (≥5) indicating possible strain
- Inconsistent results across verification rounds
- Patient reports dizziness or discomfort
- **Action:** Pause test, recommend professional eye examination, provide emergency resources if needed

### 3.7 Prescription Recommendation
**Feature:** Preliminary Vision Measurement Report
- **Output Format:**
  ```
  PRELIMINARY VISION ASSESSMENT REPORT
  =====================================
  Session ID: [timestamp]
  Test Duration: 16 minutes
  Verification Status: PASSED
  
  REFRACTION MEASUREMENTS:
  Right Eye (OD):  SPH: -1.50  CYL: -0.75  AXIS: 180
  Left Eye (OS):   SPH: -2.00  CYL: -0.50  AXIS: 175
  
  CONFIDENCE METRICS:
  Overall Confidence: 85%
  Sphere Confidence: 90%
  Cylinder Confidence: 75%
  Axis Confidence: 80%
  
  ⚠️  MEDICAL DISCLAIMER:
  This is a preliminary assessment only and should NOT be used as a 
  medical prescription. A professional eye examination by a licensed 
  optometrist or ophthalmologist is required for a valid prescription.
  
  NEXT STEPS:
  - Schedule a professional eye exam within 1-2 weeks
  - Bring this report to your eye care provider
  - Discuss any concerns about your vision
  ```
- **Data Elements:**
  - Sphere, Cylinder, Axis measurements for each eye
  - Overall test confidence score (0-100%)
  - Individual confidence scores (sphere, cylinder, axis)
  - Test duration and verification pass status
  - Test session timestamp and unique ID

### 3.8 Patient-Friendly Explanation
**Feature:** Educational Outcome Communication
- **Three-Part Explanation:**
  1. **What Changed (Your Refraction):**
     - *Example:* "Your right eye shows a mild myopic (nearsightedness) correction of -1.50 diopters. This means objects at a distance appear slightly blurry without correction."
  2. **Why It Helps (Optical Mechanism):**
     - *Example:* "The -1.50 correction works by helping your eye focus light rays directly on the retina, making distant objects clearer and sharper."
  3. **What's Next (Clinical Pathway):**
     - Schedule a professional eye examination
     - Discuss results with your optometrist
     - Options for eyewear (glasses, contacts, LASIK consultation)
     - Timeline for prescription validity (typically 1-2 years)

---

## 4. Non-Functional Requirements

### 4.1 Clinical Accuracy
- Vision measurements within ±0.50 diopter tolerance of professional optometry standards
- Snellen and LogMAR scoring must follow standardized clinical protocols
- Refraction algorithm grounded in optical physics principles
- Compensation for measurement uncertainty and patient variability

### 4.2 Conversational Quality
- Natural language processing for diverse patient responses
- Adaptive phrasing based on patient education level
- Medical terminology used with accessible explanations
- Empathetic, patient-centered communication tone
- Clear acknowledgment of patient concerns

### 4.3 Safety & Compliance
- **HIPAA Readiness:** Encrypted patient data storage, access controls
- **Medical Disclaimers:** Non-diagnostic warnings on all outputs
- **Audit Trail:** Complete session logging for quality review and liability
- **Accessibility:** WCAG 2.1 AA compliance for visual/hearing impaired
- **Bias Prevention:** No assumptions about vision quality; culturally sensitive

### 4.4 Performance & Availability
- Response latency: < 2 seconds for patient feedback
- Chart rendering: Immediate visual display (< 500ms)
- Decision logic execution: Real-time lens recommendations (< 1 second)
- System uptime: 99.5% availability target
- Data persistence: Automatic session backup and recovery

---

## 5. System Architecture

### 5.1 Core Modules
1. **Identity & Consent Manager:** Role enforcement, ethical engagement
2. **Patient History Intake Module:** Demographic and baseline data collection
3. **Chart Control Engine:** Vision chart presentation and response capture
4. **Refraction Algorithm:** Lens parameter optimization
5. **Safety Monitor:** Fatigue detection, unsafe adjustment prevention
6. **Report Generator:** Patient-friendly prescription recommendations
7. **Audit & Logging System:** Session tracking and compliance documentation

### 5.2 Data Flow
```
Patient Arrival
    ↓
[Persona Override Attempt] → Authoritative Refusal
    ↓
[Clinical Role Enforcement]
    ↓
[Consent & Context Check]
    ↓
[Patient History Intake]
    ↓
[Eye Test Control Engine Loop]
  ├─ Chart Presentation
  ├─ Patient Response Capture
  ├─ Lens Change Decision Logic
  ├─ Vision Improved? 
  │  ├─ YES → [Verification Pass]
  │  └─ NO → [Loop/Refinement]
    ↓
[Clinical Safety Guardrails]
    ↓
[Prescription Recommendation]
    ↓
[Patient-Friendly Explanation]
    ↓
Test Complete & Report Generated
```

---

## 6. Success Metrics

### 6.1 Clinical Metrics
- **Prescription Confidence Score:** Target > 80%
- **Verification Pass Rate:** Target > 90%
- **Clinical Safety Incidents:** Target 0%
- **Professional Optometrist Agreement:** Target > 85% correlation within ±0.50D

### 6.2 Patient Experience Metrics
- **Test Completion Rate:** Target > 85%
- **Patient Comfort Rating:** Target > 4.0/5.0
- **Session Duration:** Target 12-18 minutes
- **Patient Satisfaction Survey:** Target > 90% satisfaction

### 6.3 Operational Metrics
- **Response Capture Accuracy:** Target < 2% error rate
- **System Uptime:** Target 99.5%
- **Safety Escalation Rate:** Target < 10% of tests
- **Chart Rendering Performance:** Target < 500ms

---

## 7. Future Enhancements (Roadmap)

### Phase 2
- Multi-language support (Spanish, Mandarin, etc.)
- Computer vision integration for automatic chart verification
- Voice analysis for emotion/comfort detection
- Integration with EHR systems

### Phase 3
- Advanced fatigue detection using AI voice analysis
- Prescription quality comparison with professional baseline data
- Machine learning model improvements via human optometrist feedback
- Pediatric test protocols (with parental consent)
- Near vision (presbyopia) measurement module

---

## 8. Out of Scope

- ❌ **Diagnosis:** Cannot diagnose eye diseases, conditions, or pathologies
- ❌ **Prescription Authority:** Cannot issue legally binding prescriptions
- ❌ **Treatment Plans:** Cannot recommend medical treatments or surgeries
- ❌ **Advanced Diagnostics:** OCT, visual field testing, retinal imaging
- ❌ **Pediatric Testing:** Optimized for adults 18+ only
- ❌ **Emergency Care:** Not designed for acute eye emergencies

---

## 9. Compliance & Regulatory Framework

- **Clinical Standards:** American Academy of Optometry guidelines
- **Data Protection:** HIPAA compliance for patient health information
- **Device Classification:** Software Medical Device (FDA guidance adherence)
- **Accessibility:** WCAG 2.1 AA for web/app interfaces
- **Informed Consent:** Explicit patient agreement to non-diagnostic nature
- **Quality Assurance:** Regular audits by licensed optometrists

