# AI Optum: Chat Flow Configuration
# Defines the 10-step clinical protocol with substeps, context, and options

STEP_NAMES = {
    0: "Step 0: Greeting & Language Preference",
    1: "Step 1: Pre-Eye Testing",
    2: "Step 2: Visual Acuity Assessment",
    3: "Step 3: Torch Light & Anterior Segment",
    4: "Step 4: Ocular Alignment & Muscle Testing",
    5: "Step 5: Pupillary Distance Setup",
    6: "Step 6: Subjective Refraction",
    7: "Step 7: Near Vision & Presbyopia",
    8: "Step 8: Prescription Verification",
    9: "Step 9: Product Recommendation"
}

SUBSTEP_NAMES = {
    "0.1": "Welcome & Introduction",
    "0.2": "Language Selection",
    "1.1": "Auto-Refractometer (AR) Test",
    "1.2": "Lensometer (Lenso) Power Check",
    "2.1": "Distance Vision (6 meters)",
    "2.2": "Intermediate Vision (6 feet)",
    "2.3": "Near Vision (33-40 cm)",
    "3.1": "External Eye Inspection",
    "3.2": "Pupil Tests (PERRLA & RAPD)",
    "3.3": "Anterior Chamber Assessment",
    "4.1": "Hirschberg Test",
    "4.2": "Broad H Motility Test",
    "4.3": "Cover/Uncover Tests",
    "4.4": "Convergence Test",
    "5.1": "Distance PD Measurement",
    "5.2": "Near PD Measurement",
    "6.1": "Right Eye Refraction (Left Occluded)",
    "6.2": "Right Eye JCC & Duochrome",
    "6.3": "Left Eye Refraction (Right Occluded)",
    "6.4": "Left Eye JCC & Duochrome",
    "6.5": "Binocular Balance (Both Eyes Open)",
    "7.1": "Near Vision Assessment (<40 years)",
    "7.2": "Presbyopia Addition (>40 years)",
    "8.1": "Real-World Testing",
    "8.2": "Final Comfort Check",
    "9.1": "Lens Type Recommendation",
    "9.2": "Coating & Material Selection"
}

CLINICAL_CONTEXT = {
    "0.1": "Hello! I'm your AI Optometrist. I'll guide you through a comprehensive eye examination today.",
    "0.2": "To provide you with the best experience, please select your preferred language for this examination.",
    "1.1": "The Auto-Refractometer objectively measures your refractive error (sphere, cylinder, axis). This gives us a baseline to start with.",
    "1.2": "I'm checking the power of your current glasses using the lensometer to compare with the new measurements.",
    "2.1": "Please read the smallest line you can see clearly on the Snellen chart at 6 meters distance.",
    "2.2": "Now let's check your vision at intermediate distance, similar to watching TV or using a computer.",
    "2.3": "Please read this near chart at about 33-40 cm, your typical reading distance.",
    "3.1": "I'm examining your eyelids, conjunctiva, cornea, and sclera for any signs of inflammation or infection.",
    "3.2": "Testing your pupils - they should be equal, round, and reactive to light. This checks your optic nerve function.",
    "3.3": "Checking the depth and clarity of your anterior chamber to rule out glaucoma risk.",
    "4.1": "Looking at the corneal light reflex to detect any eye misalignment or squint.",
    "4.2": "Follow this target as I move it in an H pattern - this tests all six eye muscles.",
    "4.3": "These cover tests help detect both manifest and latent eye deviations.",
    "4.4": "Bring your eyes together as I move this pen toward your nose - testing your near convergence.",
    "5.1": "Measuring the distance between your pupils for distance vision correction.",
    "5.2": "Measuring your near PD for reading or progressive lenses.",
    "6.1": "I'm covering your left eye. Focus on the dot chart with your RIGHT EYE only. I'll show you two lens options - tell me which makes the dot sharper and rounder.",
    "6.2": "Still testing your RIGHT EYE. Now I'll use the Jackson Cross Cylinder to fine-tune your astigmatism, then check red-green balance.",
    "6.3": "Now covering your right eye. Focus with your LEFT EYE only. Same process - which lens makes the dot clearer?",
    "6.4": "Still testing your LEFT EYE. Refining cylinder and checking red-green balance for this eye.",
    "6.5": "Both eyes open now! I'm balancing the prescription between your eyes to ensure equal clarity and comfort.",
    "7.1": "Checking if your distance correction provides comfortable near focus.",
    "7.2": "Determining the additional power needed for comfortable reading based on your age and working distance.",
    "8.1": "Please walk around and look at real-world objects to confirm the prescription feels comfortable.",
    "8.2": "Final check for any discomfort, distortion, or visual issues before finalizing.",
    "9.1": "Based on your needs, I recommend [single vision/progressive/bifocal] lenses.",
    "9.2": "For your lifestyle, consider [blue light/anti-glare/UV protection/photochromic] coatings."
}

STEP_OPTIONS = {
    "0.1": ["Hello", "Hi", "Good morning", "Ready to start"],
    "0.2": ["English", "Hindi", "Other"],
    "1.1": ["AR test complete", "Values recorded", "Ready for next"],
    "1.2": ["Lenso done", "Old power noted", "No previous glasses"],
    "2.1": ["6/6", "6/9", "6/12", "Worse than 6/12"],
    "2.2": ["Clear", "Slightly blurry", "Need correction"],
    "2.3": ["N6", "N8", "N10", "Difficulty reading"],
    "3.1": ["Eyes healthy", "Some redness", "Discharge present"],
    "3.2": ["PERRLA normal", "RAPD negative", "Abnormal response"],
    "3.3": ["Normal depth", "Shallow chamber", "Hazy"],
    "4.1": ["No deviation", "Slight deviation"],
    "4.2": ["Full motility", "Restriction noted"],
    "4.3": ["No tropia", "Phoria detected", "Tropia present"],
    "4.4": ["Normal convergence", "Weak convergence"],
    "5.1": ["PD measured"],
    "5.2": ["Near PD done", "Ready for refraction"],
    "6.1": ["First lens better", "Second lens better", "Both same", "Clear now"],
    "6.2": ["Axis refined", "Red clearer", "Green clearer", "Both equal"],
    "6.3": ["First lens better", "Second lens better", "Both same", "Clear now"],
    "6.4": ["Axis refined", "Red clearer", "Green clearer", "Both equal"],
    "6.5": ["Balanced", "Right eye clearer", "Left eye clearer"],
    "7.1": ["Near vision good", "Some strain"],
    "7.2": ["Addition determined", "Comfortable reading"],
    "8.1": ["Feels good", "Slight discomfort", "Need adjustment"],
    "8.2": ["Ready to finalize", "Minor tweaks needed"],
    "9.1": ["Single vision", "Progressive", "Bifocal"],
    "9.2": ["Blue light", "Anti-glare", "Photochromic", "UV protection"]
}

# Step progression logic
STEP_PROGRESSION = {
    "0.1": "0.2",      # Greeting → Language
    "0.2": "1.1",      # Language → Auto-Refractometer
    "1.1": "1.2",      # AR → Lensometer
    "1.2": "2.1",      # Lensometer → Distance Vision
    "2.1": "2.2",      # Distance → Intermediate
    "2.2": "2.3",      # Intermediate → Near
    "2.3": "3.1",      # Near → External Inspection
    "3.1": "3.2",      # External → Pupils
    "3.2": "3.3",      # Pupils → Anterior Chamber
    "3.3": "4.1",      # Anterior → Hirschberg
    "4.1": "4.2",      # Hirschberg → H Motility
    "4.2": "4.3",      # Motility → Cover/Uncover
    "4.3": "4.4",      # Cover → Convergence
    "4.4": "5.1",      # Convergence → Distance PD
    "5.1": "5.2",      # Distance PD → Near PD
    "5.2": "6.1",      # Near PD → Right Eye Refraction
    "6.1": "6.2",      # Right Refraction → Right JCC
    "6.2": "6.3",      # Right JCC → Left Eye Refraction
    "6.3": "6.4",      # Left Refraction → Left JCC
    "6.4": "6.5",      # Left JCC → Binocular Balance
    "6.5": "7.1",      # Binocular → Near Vision (age check)
    "7.1": "7.2",      # Near Vision → Presbyopia (conditional)
    "7.2": "8.1",      # Presbyopia → Real-World Testing
    "8.1": "8.2",      # Real-World → Final Comfort
    "8.2": "9.1",      # Final Comfort → Lens Recommendation
    "9.1": "9.2",      # Lens Type → Coating Selection
    "9.2": "complete"  # Coating → Test Complete
}

# Intent classification mapping
INTENT_MAPPING = {
    "test_complete": ["done", "finished", "complete", "ready", "confirm", "yes"],
    "vision_reported": ["clear", "blurry", "sharp", "fuzzy", "better", "worse", "same"],
    "health_check": ["healthy", "normal", "good", "fine", "healthy", "normal"],
    "alignment_ok": ["aligned", "straight", "no deviation", "normal", "okay"],
    "pd_ready": ["measured", "ready", "done", "set"],
    "refraction_feedback": ["first", "second", "both", "clearer", "sharper", "better"],
    "reading_ability": ["read", "comfortable", "strain", "difficulty", "easy"],
    "prescription_ok": ["good", "comfortable", "feels", "okay", "perfect"],
    "product_choice": ["single", "progressive", "bifocal", "lens", "coating"],
    "unknown": []
}

# Sentiment markers
SENTIMENT_MARKERS = {
    "Confident": ["definitely", "clearly", "sure", "absolutely", "definitely", "yes sure"],
    "Under Confident": ["maybe", "somewhat", "might", "could be", "possibly", "i think"],
    "Confused": ["what", "how", "confused", "don't understand", "again", "repeat"],
    "Overconfident": ["obviously", "clearly", "of course", "obviously", "definitely"],
    "Fatigued": ["tired", "exhausted", "hard", "difficult", "struggling", "tired eyes"]
}

# Red flag keywords for escalation
RED_FLAG_KEYWORDS = [
    "pain", "severe", "sudden", "loss", "flashing", "floaters", "infection",
    "discharge", "bleeding", "trauma", "emergency", "urgent", "critical",
    "vision loss", "light sensitivity", "persistent", "worsening"
]

# Age-based branching logic
AGE_BRANCHING = {
    "under_40": "7.1",      # Near vision simple check
    "40_and_above": "7.2"   # Full presbyopia assessment
}

# Phoropter control mappings (for device integration)
PHOROPTER_CONTROLS = {
    "6.1": {
        "eye": "OD",
        "occluded_eye": "OS",
        "lens_test_pairs": [
            {"option_1": {"SPH": -0.25, "CYL": 0, "AXIS": 0}, "option_2": {"SPH": 0, "CYL": 0, "AXIS": 0}},
            {"option_1": {"SPH": -0.50, "CYL": 0, "AXIS": 0}, "option_2": {"SPH": -0.25, "CYL": 0, "AXIS": 0}},
        ],
        "decision_logic": "increment_sphere"
    },
    "6.2": {
        "eye": "OD",
        "test_type": "JCC",
        "duochrome_test": True,
        "decision_logic": "refine_cylinder_axis"
    },
    "6.3": {
        "eye": "OS",
        "occluded_eye": "OD",
        "lens_test_pairs": [
            {"option_1": {"SPH": -0.25, "CYL": 0, "AXIS": 0}, "option_2": {"SPH": 0, "CYL": 0, "AXIS": 0}},
            {"option_1": {"SPH": -0.50, "CYL": 0, "AXIS": 0}, "option_2": {"SPH": -0.25, "CYL": 0, "AXIS": 0}},
        ],
        "decision_logic": "increment_sphere"
    },
    "6.4": {
        "eye": "OS",
        "test_type": "JCC",
        "duochrome_test": True,
        "decision_logic": "refine_cylinder_axis"
    },
    "6.5": {
        "both_eyes": True,
        "decision_logic": "balance_binocular"
    }
}
