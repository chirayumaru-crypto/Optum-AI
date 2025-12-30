# AI Optum: Response Parser & Intent Extraction (Local LLM with Steering)
# Converts patient utterances to structured JSON for phoropter control
# Uses local LLM + steering vectors, no external API required

import json
import re
from typing import Dict, Any, Optional
from chat_flow_config import (
    INTENT_MAPPING, SENTIMENT_MARKERS, RED_FLAG_KEYWORDS,
    STEP_OPTIONS, STEP_PROGRESSION, PHOROPTER_CONTROLS
)


class AIOptumResponseParser:
    """
    Parses patient responses during eye examination.
    Uses local LLM with steering vectors + rule-based fallback.
    Outputs JSON that controls phoropter parameters.
    """
    
    def __init__(self, use_steering: bool = True):
        """
        Initialize parser with local LLM steering
        
        Args:
            use_steering: Use steering vectors if available (local mode)
        """
        self.use_steering = use_steering
        self.steering_enabled = False
        
        # Try to load steering vectors if available
        if use_steering:
            try:
                import torch
                steering_path = "steering_vectors.pt"
                self.steering_vectors = torch.load(steering_path)
                self.steering_enabled = True
                print("[Parser] Steering vectors loaded from steering_vectors.pt")
            except Exception as e:
                print(f"[Parser] Steering vectors not available: {str(e)[:50]}...")
                self.steering_enabled = False
    
    def extract_intent(self, utterance: str) -> str:
        """
        Rule-based intent extraction (local, no API needed)
        
        Args:
            utterance: Patient response
            
        Returns:
            Detected intent
        """
        utterance_lower = utterance.lower()
        
        # Refraction feedback (highest priority for eye exam steps)
        if any(re.search(rf"\b{re.escape(word)}\b", utterance_lower) for word in ["first", "second", "both", "clearer", "sharper", "better", "worse", "red", "green", "equal", "balance", "balanced"]):
            return "refraction_feedback"

        # Greeting & Introduction
        if any(re.search(rf"\b{re.escape(word)}\b", utterance_lower) for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"]):
            return "greeting"
        
        # Test complete / Ready to proceed
        if any(re.search(rf"\b{re.escape(word)}\b", utterance_lower) for word in ["done", "finished", "complete", "ready", "confirm", "go ahead", "proceed", "start", "begin", "yes to confirm"]):
            return "test_complete"
        
        # Vision reported
        if any(word in utterance_lower for word in ["can see", "vision", "see", "read", "visible", "appears", "looks"]):
            # But exclude refraction terms
            if not any(word in utterance_lower for word in ["first", "second", "better", "clearer", "red", "green"]):
                return "vision_reported"
        
        # Health check
        if any(word in utterance_lower for word in ["healthy", "normal", "fine", "good", "okay", "no problem", "clear"]):
            # But make sure it's about health, not refraction
            if not any(word in utterance_lower for word in ["lens", "better", "clearer", "sharper"]):
                return "health_check"
        
        # Reading ability
        if any(word in utterance_lower for word in ["read", "reading", "small text", "comfortable", "strain"]):
            return "reading_ability"
        
        # PD ready
        if any(word in utterance_lower for word in ["measured", "measurement done", "ready", "pd ready"]):
            return "pd_ready"
        
        # Alignment
        if any(word in utterance_lower for word in ["aligned", "straight", "no deviation", "alignment"]):
            return "alignment_ok"
        
        # Prescription OK
        if any(word in utterance_lower for word in ["feels good", "comfortable", "perfect", "prescription good"]):
            return "prescription_ok"
        
        # Product choice
        if any(word in utterance_lower for word in ["progressive", "bifocal", "single", "coating", "lens choice"]):
            return "product_choice"
        
        return "unknown"
    
    def extract_sentiment(self, utterance: str) -> str:
        """
        Detect patient sentiment from response
        
        Args:
            utterance: Patient response
            
        Returns:
            Sentiment classification
        """
        utterance_lower = utterance.lower()
        sentiment_scores = {}
        
        for sentiment, markers in SENTIMENT_MARKERS.items():
            score = sum(1 for marker in markers if marker in utterance_lower)
            if score > 0:
                sentiment_scores[sentiment] = score
        
        if sentiment_scores:
            return max(sentiment_scores, key=sentiment_scores.get)
        return "Confident"  # Default
    
    def detect_red_flags(self, utterance: str) -> bool:
        """
        Detect safety red flags in patient response
        
        Args:
            utterance: Patient response
            
        Returns:
            True if red flag detected
        """
        utterance_lower = utterance.lower()
        for keyword in RED_FLAG_KEYWORDS:
            if keyword in utterance_lower:
                return True
        return False
    
    def parse_response(self, step: str, substep: str, utterance: str) -> Dict[str, Any]:
        """
        Main parsing function - uses local LLM with steering or rule-based fallback.
        Converts utterance to structured JSON for phoropter control.
        
        Args:
            step: Current step
            substep: Current substep
            utterance: Patient's response
            
        Returns:
            Structured JSON response with phoropter controls
        """
        # Check if utterance matches any specific options for this step
        matched_option = self._match_to_step_options(substep, utterance)
        if matched_option:
            # If we matched an option, we can be more confident
            intent = self._map_option_to_intent(matched_option, substep)
            confidence = 0.95
        else:
            # Extract components via rules
            intent = self.extract_intent(utterance)
            confidence = self._calculate_confidence(utterance, intent)

        sentiment = self.extract_sentiment(utterance)
        red_flag = self.detect_red_flags(utterance)
        slots = self._extract_slots(step, substep, utterance, intent)
        
        # Determine phoropter action
        phoropter_action = self._determine_phoropter_action(
            step, substep, intent, slots, sentiment
        )
        
        # Determine next step - only progress if response is valid/clear
        next_step = self._determine_next_step(
            substep, intent, confidence, slots, red_flag
        )
        
        # Build response
        result = {
            "intent": intent,
            "slots": slots,
            "sentiment": sentiment,
            "confidence": confidence,
            "red_flag": red_flag,
            "phoropter_action": phoropter_action,
            "next_step": next_step,
            "response_quality": self._assess_response_quality(confidence, intent, slots)
        }
        
        return result
    
    def _match_to_step_options(self, substep: str, utterance: str) -> Optional[str]:
        """
        Fuzzy match utterance against allowed options for the current step.
        Supports synonyms and partial matches for 'intelligence'.
        """
        if substep not in STEP_OPTIONS:
            return None
        
        options = STEP_OPTIONS[substep]
        utterance_lower = utterance.lower()
        
        # Common synonyms for flexibility
        synonyms = {
            "hello": ["hi", "hey", "greetings", "good morning", "ready to start"],
            "ready": ["start", "begin", "go", "proceed", "ready to start"],
            "clear": ["sharp", "visible", "can see", "good"],
            "better": ["clearer", "sharper", "preferred"],
            "same": ["equal", "no difference", "balanced"]
        }
        
        for option in options:
            opt_lower = option.lower()
            # Direct match
            if opt_lower in utterance_lower:
                return option
            
            # Synonym match
            for base, variants in synonyms.items():
                if base in opt_lower:
                    if any(v in utterance_lower for v in variants):
                        return option
        
        return None

    def _map_option_to_intent(self, option: str, substep: str) -> str:
        """Map a matched option back to a system intent"""
        opt_lower = option.lower()
        if any(w in opt_lower for w in ["hello", "hi", "start", "ready"]):
            return "greeting" if "0.1" in substep else "test_complete"
        if any(w in opt_lower for w in ["first", "second", "both", "same", "balanced", "equal", "clearer"]):
            return "refraction_feedback"
        if any(w in opt_lower for w in ["see", "read", "clear", "visible"]):
            return "vision_reported"
        if any(w in opt_lower for w in ["healthy", "normal", "fine"]):
            return "health_check"
        return "test_complete"

    def _assess_response_quality(self, confidence: float, intent: str, slots: Dict) -> str:
        """
        Assess the quality of patient response
        
        Args:
            confidence: AI confidence in parsing (0-1)
            intent: Extracted intent
            slots: Extracted information slots
            
        Returns:
            Quality level: 'clear', 'ambiguous', 'unclear', or 'invalid'
        """
        # Valid intent with moderate/high confidence is clear
        if intent != "unknown" and intent != "invalid" and confidence > 0.6:
            return "clear"
        
        # Special case: greetings are usually clear enough to proceed
        if intent == "greeting" and confidence > 0.4:
            return "clear"
        
        # Special case: refraction feedback with slots is clear
        if intent == "refraction_feedback" and len(slots) > 0:
            return "clear"

        # Unclear if very low confidence
        if confidence < 0.4:
            return "unclear"
        
        return "ambiguous"
    
    def _determine_next_step(self, substep: str, intent: str, confidence: float,
                            slots: Dict, red_flag: bool) -> str:
        """
        Determine next step with validation. Only progresses on clear responses.
        
        Args:
            substep: Current substep
            intent: Extracted intent
            confidence: Confidence level (0-1)
            slots: Extracted slots
            red_flag: Whether red flag detected
            
        Returns:
            Next substep or same substep if response invalid
        """
        # Emergency escalation - always escalate
        if red_flag:
            return "escalate_to_professional"
        
        # Response quality assessment
        response_quality = self._assess_response_quality(confidence, intent, slots)
        
        # VALIDATION RULE: Only progress on CLEAR responses
        if response_quality != "clear":
            # Stay on same substep
            return substep
        
        # Additional validation: Check if response has required information
        if not self._has_required_information(substep, intent, slots):
            # Stay on same substep - ask again
            return substep
        
        # Response is valid and has required info - progress to next step
        return STEP_PROGRESSION.get(substep, "complete")
    
    def _has_required_information(self, substep: str, intent: str, slots: Dict) -> bool:
        """
        Check if response contains required information for the substep
        
        Args:
            substep: Current substep
            intent: Extracted intent
            slots: Extracted slots
            
        Returns:
            True if response has required info, False otherwise
        """
        # For lens pair comparison steps (6.x)
        if substep.startswith("6."):
            # Must have clarity feedback indicating a choice
            if "clarity_feedback" in slots:
                feedback = slots["clarity_feedback"]
                # Valid choices: first_better, second_better, both_same
                if feedback in ["first_better", "second_better", "both_same"]:
                    return True
            return False
        
        # For color comparison steps (7.x)
        if substep.startswith("7."):
            # Must indicate red or green preference
            if "color_preference" in slots:
                if slots["color_preference"] in ["red", "green"]:
                    return True
            return False
        
        # For health/comfort questions, any relevant response is acceptable
        if intent in ["health_question", "discomfort_report", "refraction_feedback"]:
            return len(slots) > 0
        
        # Default: accept if valid intent
        return intent != "invalid"
    
    def _determine_phoropter_action(self, step: str, substep: str, 
                                     parse_result: Dict[str, Any]) -> str:
        """
        Determine phoropter control action based on parsing result
        
        Args:
            step: Current step
            substep: Current substep
            parse_result: Parsed intent, slots, etc.
            
        Returns:
            Phoropter action string
        """
        if substep not in PHOROPTER_CONTROLS:
            return "no_action"
        
        control_config = PHOROPTER_CONTROLS[substep]
    def _extract_slots(self, step: str, substep: str, utterance: str, intent: str) -> Dict[str, Any]:
        """Extract information slots from utterance"""
        slots = {}
        utterance_lower = utterance.lower()
        
        # Vision clarity patterns
        if any(word in utterance_lower for word in ["first", "option 1", "left one", "1st"]):
            slots["clarity_feedback"] = "first_better"
        elif any(word in utterance_lower for word in ["second", "option 2", "right one", "2nd"]):
            slots["clarity_feedback"] = "second_better"
        elif any(word in utterance_lower for word in ["both", "same", "equal"]):
            slots["clarity_feedback"] = "both_same"
        
        # Color comparison (red/green)
        if "red" in utterance_lower:
            slots["color_preference"] = "red"
        elif "green" in utterance_lower:
            slots["color_preference"] = "green"
        
        # Comfort
        if any(word in utterance_lower for word in ["comfortable", "good", "perfect", "better"]):
            slots["comfort"] = "comfortable"
        elif any(word in utterance_lower for word in ["uncomfortable", "strain", "tired"]):
            slots["comfort"] = "uncomfortable"
        
        # Health
        if any(word in utterance_lower for word in ["healthy", "normal", "fine", "okay"]):
            slots["health_status"] = "normal"
        
        # Reading ability
        if any(word in utterance_lower for word in ["read", "see", "clear"]):
            slots["reading_ability"] = "able"
        
        return slots
    
    def _calculate_confidence(self, utterance: str, intent: str) -> float:
        """Calculate parse confidence based on keyword matches"""
        if intent == "unknown":
            return 0.5
        
        # Check how many keywords matched in utterance
        utterance_lower = utterance.lower()
        keyword_matches = 0
        
        if intent in INTENT_MAPPING:
            for keyword in INTENT_MAPPING[intent]:
                if keyword in utterance_lower:
                    keyword_matches += 1
        
        # Base confidence + boost for clarity
        base_confidence = 0.7
        clarity_boost = min(0.25, keyword_matches * 0.05)
        
        return min(0.99, base_confidence + clarity_boost)
    
    def _determine_phoropter_action(self, step: str, substep: str, 
                                     intent: str, slots: Dict[str, Any], 
                                     sentiment: str) -> str:
        """Determine phoropter action based on parsing result"""
        if substep not in PHOROPTER_CONTROLS:
            return "no_action"
        
        control_config = PHOROPTER_CONTROLS[substep]
        
        # Step 6.1 and 6.3: Monocular refraction
        if substep in ["6.1", "6.3"]:
            if intent == "refraction_feedback":
                clarity = str(slots.get("clarity_feedback", "")).lower()
                if any(w in clarity for w in ["first", "option 1", "1"]):
                    return f"adjust_sphere_positive_0.25_eye_{control_config['eye']}"
                elif any(w in clarity for w in ["second", "option 2", "2"]):
                    return f"adjust_sphere_negative_0.25_eye_{control_config['eye']}"
                else:
                    return "hold_current_lens"
            return "present_lens_pair"
        
        # Step 6.2 and 6.4: Cylinder and duochrome
        if substep in ["6.2", "6.4"]:
            if intent == "refraction_feedback":
                color = str(slots.get("color_preference", "")).lower()
                if "red" in color:
                    return f"adjust_sphere_negative_0.25_eye_{control_config['eye']}"
                elif "green" in color:
                    return f"adjust_sphere_positive_0.25_eye_{control_config['eye']}"
                else:
                    return "hold_current_lens"
            return "present_jcc_test"
        
        # Step 6.5: Binocular balance
        if substep == "6.5":
            if intent == "refraction_feedback":
                clarity = slots.get("clarity_feedback", "")
                if "right" in clarity.lower():
                    return "balance_right_eye_dominant"
                elif "left" in clarity.lower():
                    return "balance_left_eye_dominant"
                else:
                    return "finalize_prescription"
            return "present_binocular_test"
        
        return "no_action"


class PhoropterControlBridge:
    """
    Converts parsed JSON responses to phoropter device commands
    """
    
    def __init__(self):
        self.parser = AIOptumResponseParser()
        self.current_prescription = {
            "OD": {"SPH": 0, "CYL": 0, "AXIS": 0},
            "OS": {"SPH": 0, "CYL": 0, "AXIS": 0}
        }
        self.pd_distance = 0
        self.pd_near = 0
    
    def process_patient_response(self, step: str, substep: str, 
                                 utterance: str, pre_parsed: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process patient response and generate phoropter command
        
        Args:
            step: Current step
            substep: Current substep
            utterance: Patient's spoken/text response
            
        Returns:
            Device command JSON for phoropter
        """
        # Parse response or use pre-parsed structured data
        if pre_parsed:
            parsed = pre_parsed
        else:
            parsed = self.parser.parse_response(step, substep, utterance)
        
        # Check for red flags first
        if parsed.get("red_flag"):
            return {
                "status": "ESCALATION_REQUIRED",
                "severity": "HIGH",
                "message": "Patient reported emergency symptoms. Halt test and refer to professional.",
                "next_step": "escalate_to_professional",
                "phoropter_action": "shutdown"
            }
        
        # Generate phoropter command
        phoropter_cmd = self._translate_to_phoropter_command(parsed)
        
        # Augment response with device feedback
        parsed["phoropter_command"] = phoropter_cmd
        parsed["current_prescription"] = self.current_prescription.copy()
        
        return parsed
    
    def _translate_to_phoropter_command(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate phoropter_action string to device command
        
        Args:
            parsed: Parsed response
            
        Returns:
            Device command dictionary
        """
        action = parsed.get("phoropter_action", "no_action")
        
        if "adjust_sphere_positive" in action:
            eye = self._extract_eye_from_action(action)
            self.current_prescription[eye]["SPH"] += 0.25
            return {
                "command": "adjust_sphere",
                "eye": eye,
                "value": 0.25,
                "new_prescription": self.current_prescription[eye],
                "action": action
            }
        
        elif "adjust_sphere_negative" in action:
            eye = self._extract_eye_from_action(action)
            self.current_prescription[eye]["SPH"] -= 0.25
            return {
                "command": "adjust_sphere",
                "eye": eye,
                "value": -0.25,
                "new_prescription": self.current_prescription[eye],
                "action": action
            }
        
        elif "adjust_cylinder_axis" in action:
            eye = self._extract_eye_from_action(action)
            return {
                "command": "present_jcc",
                "eye": eye,
                "current_prescription": self.current_prescription[eye],
                "action": action
            }
        
        elif "balance" in action:
            return {
                "command": "balance_binocular",
                "current_prescription": self.current_prescription,
                "action": action
            }
        
        elif "finalize" in action:
            return {
                "command": "finalize_prescription",
                "final_prescription": self.current_prescription,
                "action": action
            }
        
        elif "present" in action:
            return {
                "command": "present_chart",
                "action": action
            }
        
        else:
            return {
                "command": "no_action",
                "action": action
            }
    
    @staticmethod
    def _extract_eye_from_action(action: str) -> str:
        """Extract eye designation (OD/OS) from action string"""
        if "OD" in action:
            return "OD"
        elif "OS" in action:
            return "OS"
        return "OD"  # Default


# Example usage and testing
if __name__ == "__main__":
    parser = AIOptumResponseParser()
    bridge = PhoropterControlBridge()
    
    # Example: Patient response during Step 6.1
    test_responses = [
        ("6", "6.1", "The first lens makes it look clearer and rounder"),
        ("6", "6.2", "The red and green look equal now"),
        ("6", "6.5", "Both eyes feel balanced, very comfortable"),
        ("3", "3.1", "My eyes look fine, no problems"),
    ]
    
    print("=" * 80)
    print("AI OPTUM RESPONSE PARSER - TEST OUTPUT")
    print("=" * 80)
    
    for step, substep, utterance in test_responses:
        print(f"\nStep {substep}: Patient said: '{utterance}'")
        result = bridge.process_patient_response(step, substep, utterance)
        print(json.dumps(result, indent=2, default=str))
        print("-" * 80)
