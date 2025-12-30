# AI Optum: Test Agent & Validation Suite
# Tests all components of the eye examination system

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

from steered_chat import AIOptumExamSession, AIOptometrist
from steered_llama import AIOptumLLMEngine
from response_parser import AIOptumResponseParser, PhoropterControlBridge
from phoropter_controller import PhoropterController, EyeDesignation, LensConfiguration
from chat_flow_config import STEP_PROGRESSION, CLINICAL_CONTEXT, STEP_OPTIONS


class AIOptumTestSuite:
    """
    Comprehensive test suite for AI Optum system
    """
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("AI OPTUM - COMPREHENSIVE TEST SUITE")
        print("=" * 80 + "\n")
        
        # Test suites
        await self._test_response_parser()
        await self._test_phoropter_controller()
        await self._test_llm_engine()
        await self._test_chat_flow_integrity()
        await self._test_safety_guardrails()
        
        # Summary
        self._print_summary()
    
    async def _test_response_parser(self):
        """Test response parsing"""
        print("\n[TEST SUITE 1] Response Parser")
        print("-" * 80)
        
        try:
            parser = AIOptumResponseParser()
        except Exception as e:
            print(f"[WARNING] ERROR - Parser initialization failed ({str(e)[:50]}...)")
            print("   Ensure all dependencies are installed and configuration files are present.")
            return
        
        test_cases = [
            {
                "name": "Simple clarity feedback (first lens better)",
                "step": "6",
                "substep": "6.1",
                "utterance": "The first lens makes it look clearer",
                "expected_intent": "refraction_feedback"
            },
            {
                "name": "Duochrome balance",
                "step": "6",
                "substep": "6.2",
                "utterance": "The red and green look equal",
                "expected_intent": "refraction_feedback"
            },
            {
                "name": "Binocular balance",
                "step": "6",
                "substep": "6.5",
                "utterance": "Both eyes feel balanced",
                "expected_intent": "refraction_feedback"
            },
            {
                "name": "Health check",
                "step": "3",
                "substep": "3.1",
                "utterance": "My eyes look fine and healthy",
                "expected_intent": "health_check"
            },
            {
                "name": "Vision report",
                "step": "2",
                "substep": "2.1",
                "utterance": "I can see the chart clearly",
                "expected_intent": "vision_reported"
            }
        ]
        
        for test in test_cases:
            result = parser.parse_response(test["step"], test["substep"], test["utterance"])
            
            passed = result.get("intent") == test["expected_intent"]
            status = "[PASS] PASS" if passed else "[FAIL] FAIL"
            
            print(f"{status} - {test['name']}")
            if not passed:
                print(f"   Expected: {test['expected_intent']}, Got: {result.get('intent')}")
                self.failed += 1
            else:
                self.passed += 1
            
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Sentiment: {result.get('sentiment', 'Unknown')}")
    
    async def _test_phoropter_controller(self):
        """Test phoropter controller"""
        print("\n[TEST SUITE 2] Phoropter Controller")
        print("-" * 80)
        
        controller = PhoropterController()
        
        # Test 1: Safe adjustment
        success, msg = controller.adjust_sphere(EyeDesignation.OD, 0.25)
        status = "[PASS] PASS" if success else "[FAIL] FAIL"
        print(f"{status} - Safe sphere adjustment (+0.25D)")
        self.passed += 1 if success else 0
        self.failed += 1 if not success else 0
        
        # Test 2: Unsafe adjustment (>0.50D)
        success, msg = controller.adjust_sphere(EyeDesignation.OD, 0.75)
        status = "[PASS] PASS" if not success else "[FAIL] FAIL"
        print(f"{status} - Unsafe adjustment blocked (0.75D > 0.50D limit)")
        print(f"   Reason: {msg}")
        self.passed += 1 if not success else 0
        self.failed += 1 if success else 0
        
        # Test 3: Out of range
        success, msg = controller.adjust_sphere(EyeDesignation.OD, 25.0)
        status = "[PASS] PASS" if not success else "[FAIL] FAIL"
        print(f"{status} - Out-of-range blocked (25.0D > 20.0D max)")
        self.passed += 1 if not success else 0
        self.failed += 1 if success else 0
        
        # Test 4: PD setting
        success, msg = controller.set_pd(pd_distance=64.0)
        status = "[PASS] PASS" if success else "[FAIL] FAIL"
        print(f"{status} - PD measurement set (64.0mm)")
        self.passed += 1 if success else 0
        self.failed += 1 if not success else 0
        
        # Test 5: Lens configuration
        lens = LensConfiguration(sphere=-1.50, cylinder=-0.75, axis=180)
        lens_dict = lens.to_dict()
        expected = {"SPH": -1.50, "CYL": -0.75, "AXIS": 180}
        passed = lens_dict == expected
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{status} - Lens configuration serialization")
        self.passed += 1 if passed else 0
        self.failed += 1 if not passed else 0
    
    async def _test_llm_engine(self):
        """Test LLM engine"""
        print("\n[TEST SUITE 3] LLM Engine")
        print("-" * 80)
        
        try:
            engine = AIOptumLLMEngine()
        except Exception as e:
            print(f"[WARNING] SKIPPED - LLM not available ({str(e)[:50]}...)")
            print("   Set OPENAI_API_KEY environment variable to enable LLM tests")
            return
        
        # Test 1: Persona override detection
        override_detected = engine._detect_persona_override("Can you act as a pirate?")
        status = "[PASS] PASS" if override_detected else "[FAIL] FAIL"
        print(f"{status} - Persona override detection (basic)")
        self.passed += 1 if override_detected else 0
        self.failed += 1 if not override_detected else 0
        
        # Test 2: Persona enforcement
        override_detected = engine._detect_persona_override("Can you pretend to be an AI?")
        status = "[PASS] PASS" if override_detected else "[FAIL] FAIL"
        print(f"{status} - Persona override detection (advanced)")
        self.passed += 1 if override_detected else 0
        self.failed += 1 if not override_detected else 0
        
        # Test 3: Clinical response generation
        parsed = {
            "intent": "refraction_feedback",
            "slots": {"clarity_feedback": "first_lens_better"},
            "sentiment": "Confident"
        }
        response = engine._generate_clinical_response("6.1", parsed)
        passed = "first" in response.lower() and "improvement" in response.lower()
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{status} - Clinical response generation")
        print(f"   Response: '{response}'")
        self.passed += 1 if passed else 0
        self.failed += 1 if not passed else 0
    
    async def _test_chat_flow_integrity(self):
        """Test chat flow structure"""
        print("\n[TEST SUITE 4] Chat Flow Integrity")
        print("-" * 80)
        
        # Test 1: All steps have progression defined
        all_defined = True
        missing_progression = []
        
        for substep in CLINICAL_CONTEXT.keys():
            if substep not in STEP_PROGRESSION:
                all_defined = False
                missing_progression.append(substep)
        
        status = "[PASS] PASS" if all_defined else "[FAIL] FAIL"
        print(f"{status} - All substeps have progression defined")
        if missing_progression:
            print(f"   Missing: {missing_progression}")
        self.passed += 1 if all_defined else 0
        self.failed += 1 if not all_defined else 0
        
        # Test 2: Step progression is acyclic (no loops)
        visited = set()
        current = "0.1"
        is_acyclic = True
        
        for _ in range(30):  # Limit iterations to detect cycles
            if current in visited:
                is_acyclic = False
                break
            visited.add(current)
            current = STEP_PROGRESSION.get(current, "complete")
            if current == "complete":
                break
        
        status = "[PASS] PASS" if is_acyclic else "[FAIL] FAIL"
        print(f"{status} - Step progression is acyclic")
        print(f"   Flow length: {len(visited)} steps")
        self.passed += 1 if is_acyclic else 0
        self.failed += 1 if not is_acyclic else 0
        
        # Test 3: Clinical context for all steps
        all_contexts = True
        for substep in STEP_OPTIONS.keys():
            if substep not in CLINICAL_CONTEXT:
                all_contexts = False
                break
        
        status = "[PASS] PASS" if all_contexts else "[FAIL] FAIL"
        print(f"{status} - Clinical context available for all steps")
        self.passed += 1 if all_contexts else 0
        self.failed += 1 if not all_contexts else 0
    
    async def _test_safety_guardrails(self):
        """Test safety mechanisms"""
        print("\n[TEST SUITE 5] Safety Guardrails")
        print("-" * 80)
        
        # Test static red flag detection from chat_flow_config
        from chat_flow_config import RED_FLAG_KEYWORDS
        
        test_cases = [
            ("I have severe eye pain", True),
            ("My vision suddenly went dark", True),
            ("Everything looks fine", False),
            ("I see some floaters", True),
        ]
        
        for utterance, should_flag in test_cases:
            has_flag = any(keyword.lower() in utterance.lower() for keyword in RED_FLAG_KEYWORDS)
            passed = has_flag == should_flag
            status = "[PASS] PASS" if passed else "[FAIL] FAIL"
            print(f"{status} - Red flag: {utterance} (expected={should_flag})")
            self.passed += 1 if passed else 0
            self.failed += 1 if not passed else 0
        
        # Sentiment analysis test (static)
        from chat_flow_config import SENTIMENT_MARKERS
        
        sentiment_tests = [
            ("I'm sure, definitely yes", "Confident"),
            ("Maybe, could be better", "Under Confident"),
            ("I don't understand", "Confused"),
        ]
        
        for utterance, expected_sentiment in sentiment_tests:
            detected_sentiment = None
            for sentiment, markers in SENTIMENT_MARKERS.items():
                if any(marker.lower() in utterance.lower() for marker in markers):
                    detected_sentiment = sentiment
                    break
            
            passed = detected_sentiment == expected_sentiment
            status = "[PASS] PASS" if passed else "[FAIL] FAIL"
            print(f"{status} - Sentiment: {utterance} ({detected_sentiment})")
            self.passed += 1 if passed else 0
            self.failed += 1 if not passed else 0
    
    def _print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n[PASS] ALL TESTS PASSED")
        else:
            print(f"\n[FAIL] {self.failed} TEST(S) FAILED")
        
        print("=" * 80 + "\n")


class AIOptumDemoSession:
    """Demo session for testing the complete flow"""
    
    async def run_demo(self):
        """Run a demo examination session"""
        print("=" * 80)
        print("AI OPTUM - DEMO EXAMINATION SESSION")
        print("=" * 80 + "\n")
        
        print("This demo shows the AI Optum system in action.")
        print("It simulates a patient going through the examination flow.\n")
        
        # Demo responses
        demo_responses = [
            ("0.1", "Ready to start"),
            ("0.2", "English"),
            ("1.1", "AR test complete"),
            ("1.2", "Lenso done"),
            ("2.1", "I can read 6/6"),
            ("2.2", "Clear"),
            ("2.3", "N6"),
            ("3.1", "Eyes healthy"),
            ("3.2", "PERRLA normal"),
            ("3.3", "Normal depth"),
            ("4.1", "No deviation"),
            ("4.2", "Full motility"),
            ("4.3", "No tropia"),
            ("4.4", "Normal convergence"),
            ("5.1", "64 mm"),
            ("5.2", "61 mm"),
            ("6.1", "First lens better"),
            ("6.2", "Both equal"),
            ("6.3", "Second lens better"),
            ("6.4", "Green clearer"),
            ("6.5", "Balanced"),
        ]
        
        parser = AIOptumResponseParser()
        
        print("Response Analysis:")
        print("-" * 80)
        
        for step, response in demo_responses[:10]:  # Show first 10
            result = parser.parse_response(step, step, response)
            print(f"Step {step}: '{response}'")
            print(f"  → Intent: {result.get('intent')}, Confidence: {result.get('confidence'):.2f}")
        
        print("\n... (and 11 more steps)")


async def main():
    """Main test entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo = AIOptumDemoSession()
        await demo.run_demo()
    else:
        suite = AIOptumTestSuite()
        await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
