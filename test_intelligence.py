# AI Optum: Intelligence & Semantic Matching Test
import asyncio
import json
from steered_llama import AIOptumLLMEngine
from response_parser import AIOptumResponseParser

async def run_intelligence_test():
    print("=" * 80)
    print("AI OPTUM - INTELLIGENCE & SEMANTIC MATCHING TEST")
    print("Goal: Verify that 'Hey' and other variations work for every step.")
    print("=" * 80)

    engine = AIOptumLLMEngine(use_steering=True)
    
    test_cases = [
        {
            "step": "0", "substep": "0.1", 
            "utterance": "Hey", 
            "expected_intent": "greeting",
            "description": "Casual greeting 'Hey' for Step 0.1"
        },
        {
            "step": "0", "substep": "0.1", 
            "utterance": "Yo, I'm ready", 
            "expected_intent": "greeting",
            "description": "Very casual ready signal"
        },
        {
            "step": "6", "substep": "6.1", 
            "utterance": "The left one looks way sharper", 
            "expected_intent": "refraction_feedback",
            "description": "Semantic variation 'left one' for 'first lens'"
        },
        {
            "step": "3", "substep": "3.1", 
            "utterance": "Everything feels great with my eyes", 
            "expected_intent": "health_check",
            "description": "Semantic variation 'feels great' for 'healthy'"
        },
        {
            "step": "9", "substep": "9.1", 
            "utterance": "I want those ones that change in the sun", 
            "expected_intent": "product_choice",
            "description": "Semantic variation for photochromic lenses"
        }
    ]

    passed_count = 0
    
    for i, test in enumerate(test_cases):
        print(f"\n[Test {i+1}] {test['description']}")
        print(f"Input: '{test['utterance']}' (Substep: {test['substep']})")
        
        result = await engine.process_patient_response(test["step"], test["substep"], test["utterance"])
        
        actual_intent = result.get("intent")
        quality = result.get("response_quality")
        
        passed = (actual_intent == test["expected_intent"]) and (quality == "clear")
        
        if passed:
            print(f"Result: [PASS] (Intent: {actual_intent}, Quality: {quality})")
            passed_count += 1
        else:
            print(f"Result: [FAIL] (Intent: {actual_intent}, Quality: {quality})")
        
        print(f"Debug: {json.dumps(result, indent=2)}")

    print("\n" + "=" * 80)
    print(f"INTELLIGENCE TEST SUMMARY: {passed_count}/{len(test_cases)} Passed")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_intelligence_test())
