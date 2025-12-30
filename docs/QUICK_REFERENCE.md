# AI Optum: Quick Reference Guide

## Running the System

### Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install langchain openai torch transformers pyyaml

# 2. Run test suite (verify everything works)
python test_agent.py

# 3. Start examination
python chat_app.py
```

---

## Command Reference

### Main Application

```bash
# Interactive session (anonymous patient)
python chat_app.py

# With patient ID
python chat_app.py --patient P001

# Debug mode (simulated phoropter, no hardware)
python chat_app.py --debug

# Run comprehensive test suite
python chat_app.py --test
```

### Test Suite

```bash
# Full test suite
python test_agent.py

# Demo mode (shows response parsing)
python test_agent.py --demo
```

### Individual Components

```bash
# Test response parser
python response_parser.py

# Test phoropter controller
python phoropter_controller.py

# Test monitoring system
python monitoring.py

# Test chat flow
python chat_flow_config.py  # (imports only)
```

---

## System Flow Diagram

```
Patient Input
    ↓
[Chat Flow Layer]
    Detect Step: "6.1"
    Get Clinical Context
    ↓
[Response Parser]
    Intent: "refraction_feedback"
    Confidence: 0.95
    ↓
[Phoropter Bridge]
    Action: "adjust_sphere_positive_0.25_OD"
    ↓
[Phoropter Controller]
    Safety Check: ✓ PASS
    New Sphere: -1.00D
    ↓
[Device Command]
    {
        "command": "present_lens_pair",
        "eye": "OD",
        "lens_1": {"SPH": -1.00, "CYL": 0, "AXIS": 0},
        "lens_2": {"SPH": -0.75, "CYL": 0, "AXIS": 0}
    }
    ↓
Hardware Executes
```

---

## File Purpose Reference

| File | Purpose | Entry Point |
|------|---------|-------------|
| `chat_app.py` | CLI interface | `python chat_app.py` |
| `steered_chat.py` | Session orchestrator | `AIOptumExamSession` |
| `steered_llama.py` | LLM engine | `AIOptumLLMEngine` |
| `response_parser.py` | Intent extraction | `AIOptumResponseParser` |
| `phoropter_controller.py` | Hardware control | `PhoropterController` |
| `chat_flow_config.py` | Protocol definition | (imported) |
| `monitoring.py` | Safety monitoring | `ComprehensiveSessionMonitor` |
| `test_agent.py` | Test suite | `python test_agent.py` |

---

## 10-Step Protocol at a Glance

| Step | Name | Key Task | Substeps |
|------|------|----------|----------|
| 0 | Greeting | Consent, language | 0.1, 0.2 |
| 1 | Pre-Testing | Baseline, current lens | 1.1, 1.2 |
| 2 | Visual Acuity | Distance, intermediate, near | 2.1, 2.2, 2.3 |
| 3 | Anterior | Eyes, pupils, chamber | 3.1, 3.2, 3.3 |
| 4 | Alignment | Eye movement, coordination | 4.1, 4.2, 4.3, 4.4 |
| 5 | PD | Distance & near measurements | 5.1, 5.2 |
| 6 | Refraction | **Core:** Right, left, both | 6.1, 6.2, 6.3, 6.4, 6.5 |
| 7 | Near Vision | Age-based presbyopia | 7.1, 7.2 |
| 8 | Verification | Real-world comfort | 8.1, 8.2 |
| 9 | Recommendation | Lens type, coatings | 9.1, 9.2 |

---

## Intent Classification Quick Ref

```python
INTENTS = {
    "test_complete": "Patient confirms test done",
    "vision_reported": "Patient describes what they see",
    "health_check": "Patient reports eye health",
    "alignment_ok": "Eye alignment confirmed",
    "pd_ready": "PD measurement complete",
    "refraction_feedback": "Feedback on lens options",
    "reading_ability": "Near vision feedback",
    "prescription_ok": "Prescription feels good",
    "product_choice": "Patient selects lens/coating",
    "unknown": "Intent unclear"
}
```

---

## Sentiment Analysis Quick Ref

```python
SENTIMENTS = {
    "Confident": "Sure, clearly, definitely, yes",
    "Under Confident": "Maybe, might, could, possibly",
    "Confused": "What, how, don't understand",
    "Overconfident": "Obviously, definitely, course",
    "Fatigued": "Tired, exhausted, struggling"
}
```

---

## Safety Keywords (Red Flags)

```
CRITICAL TRIGGERS:
pain, severe, sudden, loss, flashing, floaters,
infection, discharge, bleeding, trauma, emergency,
vision loss, light sensitivity, persistent
```

**→ Immediate test halt & professional referral**

---

## Phoropter Control Quick Ref

### Safety Limits
- **Max adjustment:** ±0.50D (sphere/cylinder), ±10° (axis)
- **Range:** Sphere [-20, +20], Cylinder [0, -6], Axis [0, 180]
- **Session:** Max 25 minutes

### Device Commands
```python
"present_lens_pair"      # Show two lens options
"adjust_sphere_positive" # Increase minus sphere
"adjust_sphere_negative" # Decrease minus sphere
"adjust_cylinder_axis"   # Refine astigmatism
"balance_binocular"      # Balance both eyes
"finalize"               # Complete prescription
"escalate"               # Emergency halt
```

---

## Monitoring Quick Ref

### Fatigue Triggers
- Accuracy drops >20%
- Hesitation increases to >3 sec
- Confidence drops >30%

**→ Offer break at yellow, halt at red**

### Duration Limits
- **15 min:** Offer break
- **20 min:** Warn approaching limit
- **25 min:** HARD STOP

### Quality Thresholds
- Parse success: >90%
- Avg confidence: >70%
- Device success: >95%

---

## Session Output Location

```
exam_records/
├── OPT-20251229-143022_report.json
├── OPT-20251229-150000_report.json
└── ...
```

**Fields:**
- `session_id`: Unique identifier
- `patient_id`: Anonymized patient
- `final_prescription`: OD/OS measurements
- `session_log`: All responses + parsing
- `test_complete`: Boolean completion status

---

## Troubleshooting Quick Ref

| Problem | Solution |
|---------|----------|
| Parse fails | Check OpenAI key, fallback activates |
| Low confidence | Check network, LLM availability |
| Red flag | Expected - patient sees professional |
| Hardware error | Use `--debug` mode |
| Import errors | `pip install langchain openai pyyaml` |

---

## Clinical Workflow Example

```
STEP 6.1: Right Eye Refraction

AI: "Focus with RIGHT EYE only. Which lens is sharper - first or second?"

PATIENT OPTIONS:
  → "First lens better"
  → "Second lens better"
  → "Both same"
  → "Neither clear"

PARSER DETECTS:
  Intent: "refraction_feedback"
  Clarity: "first_lens_better"
  Sentiment: "Confident"
  Confidence: 0.95

DEVICE ACTION:
  Eye: OD (Right)
  Adjustment: +0.25D sphere
  Next Step: 6.2 (JCC & Duochrome)
```

---

## Testing Checklist

- [ ] Run `python test_agent.py` (all tests pass?)
- [ ] Run `python chat_app.py --debug` (UI works?)
- [ ] Check `exam_records/` (reports generated?)
- [ ] Check `logs/` (audit trail recorded?)
- [ ] Verify safety (red flag detection working?)
- [ ] Verify fatigue (monitoring active?)

---

## Key Classes Reference

```python
# Session Management
AIOptumExamSession()         # Main session orchestrator
AIOptometrist()              # Clinical role enforcement

# LLM & Parsing
AIOptumLLMEngine()           # LLM with phoropter integration
AIOptumResponseParser()      # Intent extraction
PhoropterControlBridge()     # Parser → Device bridge

# Hardware Control
PhoropterController()        # Device interface
LensConfiguration()          # Lens parameters (SPH/CYL/AXIS)
PhoropeterState()           # Device state tracking

# Safety & Monitoring
ComprehensiveSessionMonitor()  # All monitoring systems
PatientFatigueMonitor()       # Fatigue detection
SessionDurationMonitor()      # Time tracking
SafetyIncidentTracker()       # Incident logging
ExaminationQualityMonitor()   # Quality metrics

# Testing
AIOptumTestSuite()           # Comprehensive tests
AIOptumDemoSession()         # Demo mode
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Parse confidence | >70% |
| Device command success | >95% |
| Session completion | >85% |
| Fatigue detection accuracy | >90% |
| Red flag detection | 100% (critical) |
| Response latency | <2 sec |
| System uptime | 99.5% |

---

## Documentation Map

- **Getting Started:** README.md
- **Product Spec:** PRD.md
- **Technical Details:** PROCESS_ENGINE.md
- **Integration:** CHAT_FLOW_INTEGRATION.md
- **This Guide:** QUICK_REFERENCE.md

---

## Contact & Support

For issues or questions:
1. Check documentation (PRD.md, PROCESS_ENGINE.md)
2. Run test suite (`python test_agent.py`)
3. Check logs in `logs/`
4. Review session report in `exam_records/`

---

**AI Optum v1.0 - December 29, 2025**
