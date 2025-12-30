# AI Optum: Main Chat Application
# Orchestrates entire eye examination flow with phoropter control

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from chat_flow_config import (
    STEP_NAMES, SUBSTEP_NAMES, CLINICAL_CONTEXT, STEP_OPTIONS,
    STEP_PROGRESSION
)
from response_parser import AIOptumResponseParser, PhoropterControlBridge
from phoropter_controller import PhoropterController, EyeDesignation
from steered_llama import AIOptumLLMEngine


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_optum_session.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AIOptumExamSession:
    """
    Main orchestrator for complete eye examination session.
    Manages flow, patient interaction, and phoropter control.
    """
    
    def __init__(self, patient_id: str = "ANON", debug_mode: bool = False):
        """
        Initialize exam session
        
        Args:
            patient_id: Anonymized patient identifier
            debug_mode: Enable debug logging and skip hardware connection
        """
        self.patient_id = patient_id
        self.debug_mode = debug_mode
        self.session_id = f"OPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Initialize components
        self.parser = AIOptumResponseParser()
        self.phoropter = PhoropterController()
        self.bridge = PhoropterControlBridge()
        self.engine = AIOptumLLMEngine() # New intelligent engine
        
        # Session state
        self.current_step = "0.1"
        self.current_step_num = 0
        self.patient_data = {
            "demographics": {},
            "vision_history": {},
            "medical_history": {},
            "test_responses": []
        }
        self.session_log = []
        self.start_time = datetime.now()
        self.test_complete = False
        
        logger.info(f"Session {self.session_id} initialized for patient {patient_id}")
    
    async def start_examination(self) -> None:
        """Start the complete eye examination flow"""
        logger.info(f"Starting examination for {self.patient_id}")
        print("\n" + "=" * 80)
        print("AI OPTUM - COMPREHENSIVE EYE EXAMINATION")
        print("=" * 80 + "\n")
        
        try:
            # Step 0: Greeting & Consent
            await self._execute_step("0.1", "Welcome & Introduction")
            await self._execute_step("0.2", "Language Selection")
            
            # Step 1: Pre-Testing
            await self._execute_step("1.1", "Auto-Refractometer (AR) Test")
            await self._execute_step("1.2", "Lensometer (Lenso) Power Check")
            
            # Step 2: Visual Acuity
            await self._execute_step("2.1", "Distance Vision (6 meters)")
            await self._execute_step("2.2", "Intermediate Vision (6 feet)")
            await self._execute_step("2.3", "Near Vision (33-40 cm)")
            
            # Step 3: Anterior Segment
            await self._execute_step("3.1", "External Eye Inspection")
            await self._execute_step("3.2", "Pupil Tests (PERRLA & RAPD)")
            await self._execute_step("3.3", "Anterior Chamber Assessment")
            
            # Step 4: Ocular Alignment
            await self._execute_step("4.1", "Hirschberg Test")
            await self._execute_step("4.2", "Broad H Motility Test")
            await self._execute_step("4.3", "Cover/Uncover Tests")
            await self._execute_step("4.4", "Convergence Test")
            
            # Step 5: Pupillary Distance
            await self._execute_step("5.1", "Distance PD Measurement")
            await self._execute_step("5.2", "Near PD Measurement")
            
            # Step 6: Subjective Refraction (Core Loop)
            await self._execute_refraction_loop()
            
            # Step 7: Near Vision & Presbyopia
            age = self.patient_data.get("demographics", {}).get("age", 0)
            if age >= 40:
                await self._execute_step("7.1", "Near Vision Assessment (<40 years)")
                await self._execute_step("7.2", "Presbyopia Addition (>40 years)")
            else:
                await self._execute_step("7.1", "Near Vision Assessment (<40 years)")
            
            # Step 8: Verification
            await self._execute_step("8.1", "Real-World Testing")
            await self._execute_step("8.2", "Final Comfort Check")
            
            # Step 9: Recommendations
            await self._execute_step("9.1", "Lens Type Recommendation")
            await self._execute_step("9.2", "Coating & Material Selection")
            
            # Generate final report
            await self._generate_final_report()
            self.test_complete = True
            
        except Exception as e:
            logger.error(f"Error during examination: {str(e)}", exc_info=True)
            await self._handle_escalation("ERROR", str(e))
    
    async def _execute_step(self, substep: str, step_name: str) -> bool:
        """
        Execute a single substep with persistence.
        Will re-ask if the response is unclear or unsatisfied.
        """
        self.current_step = substep
        step_num = int(substep.split(".")[0])
        
        print(f"\n[Step {substep}] {step_name}")
        print("-" * 80)
        
        # Initial context setting
        context = CLINICAL_CONTEXT.get(substep, "")
        if context:
            print(f"AI Optometrist: {context}\n")
        
        while True:
            # Capture patient response (this handles option display internally)
            patient_response = await self._get_patient_input(substep)
            
            # Parse response
            parsed = await self.engine.process_patient_response(
                step=str(step_num),
                substep=substep,
                utterance=patient_response
            )
            
            # Emergency check
            if parsed.get("red_flag"):
                await self._handle_escalation("RED_FLAG", patient_response)
                return False

            # Check if response is clear/satisfactory
            quality = parsed.get("response_quality", "clear")
            if quality != "clear" and parsed.get("intent") != "greeting":
                print(f"\nAI Optometrist: {parsed.get('response')}")
                print(f"I need to confirm this before we proceed. Let's try again.\n")
                
                # Re-display context if it's an options step to help the user
                if context:
                    print(f"Recall: {context}")
                continue
            
            # Satisfied - execute and proceed
            if "phoropter" in substep or "6." in substep or "5." in substep:
                await self._execute_phoropter_action(parsed)
            
            self._log_response(substep, patient_response, parsed)
            self.current_step = parsed.get("next_step", STEP_PROGRESSION.get(substep))
            return True
    
    async def _execute_refraction_loop(self) -> None:
        """
        Execute Step 6: Subjective Refraction (iterative loop)
        """
        print("\n" + "=" * 80)
        print("STEP 6: SUBJECTIVE REFRACTION")
        print("=" * 80)
        
        refraction_steps = ["6.1", "6.2", "6.3", "6.4", "6.5"]
        for step in refraction_steps:
            success = await self._execute_step(step, SUBSTEP_NAMES[step])
            if not success:
                logger.error(f"Refraction step {step} failed")
                break
    
    async def _execute_phoropter_action(self, parsed: Dict[str, Any]) -> None:
        """
        Execute phoropter hardware command based on parsed response
        
        Args:
            parsed: Parsed response with phoropter_action
        """
        action = parsed.get("phoropter_action", "no_action")
        
        if action == "no_action":
            return
        
        if self.debug_mode:
            print(f"[DEBUG] Phoropter Action: {action}")
            print(f"[DEBUG] Device State: {json.dumps(self.phoropter.get_device_state(), indent=2, default=str)}")
        else:
            result = self.phoropter.execute_phoropter_action(action)
            logger.info(f"Phoropter action executed: {action}")
            logger.debug(f"Result: {result}")
            
            # Display device state to patient
            if result.get("device_state"):
                print(f"[Device] {json.dumps(result['device_state'], indent=2, default=str)}")
    
    async def _get_patient_input(self, substep: str) -> str:
        """
        Get patient input with predefined options and validation
        
        Args:
            substep: Current substep
            
        Returns:
            Patient's response
        """
        options = STEP_OPTIONS.get(substep, [])
        
        if options:
            print("Options:")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            print()
        
        # Keep asking until valid response is received
        while True:
            response = input("Patient: ").strip()
            
            if not response:
                print("Please provide a response.")
                continue
            
            # If there are predefined options, handle numeric shortcuts
            if options and response.isdigit():
                option_num = int(response)
                if 1 <= option_num <= len(options):
                    # Valid number - return the corresponding option text
                    return options[option_num - 1]
                else:
                    # Invalid number - out of range
                    print(f"❌ Invalid option number. Please select 1 to {len(options)}, or type your response.")
                    continue
            
            # For all other text input, pass it through to the intelligence engine
            return response
            
            # No predefined options - accept any response
            return response if response else "Not sure"
    
    def _log_response(self, substep: str, utterance: str, parsed: Dict[str, Any]) -> None:
        """Log patient response for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "substep": substep,
            "patient_response": utterance,
            "parsed_intent": parsed.get("intent"),
            "sentiment": parsed.get("sentiment"),
            "confidence": parsed.get("confidence"),
            "phoropter_action": parsed.get("phoropter_action")
        }
        self.session_log.append(log_entry)
        self.patient_data["test_responses"].append(log_entry)
    
    async def _handle_escalation(self, escalation_type: str, details: str) -> None:
        """
        Handle test escalation (red flags, errors)
        
        Args:
            escalation_type: Type of escalation (RED_FLAG, ERROR, etc.)
            details: Escalation details
        """
        print("\n" + "!" * 80)
        print(f"ESCALATION REQUIRED: {escalation_type}")
        print(f"Details: {details}")
        print("!" * 80)
        
        logger.critical(f"Escalation {escalation_type} at step {self.current_step}: {details}")
        
        print("\nRECOMMENDATION:")
        print("Please consult with a professional optometrist immediately.")
        print("This test has been paused for your safety.")
        
        self.test_complete = True
    
    async def _generate_final_report(self) -> None:
        """Generate final prescription report"""
        final_prescription = self.phoropter.finalize_prescription()
        
        print("\n" + "=" * 80)
        print("FINAL VISION ASSESSMENT REPORT")
        print("=" * 80)
        print(f"\nSession ID: {self.session_id}")
        print(f"Patient ID: {self.patient_id}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {(datetime.now() - self.start_time).total_seconds():.1f} seconds")
        
        print("\n" + "-" * 80)
        print("REFRACTION MEASUREMENTS:")
        print("-" * 80)
        
        od = final_prescription["final_prescription"]["OD"]
        os = final_prescription["final_prescription"]["OS"]
        
        print(f"Right Eye (OD):  SPH: {od['SPH']:+.2f}  CYL: {od['CYL']:+.2f}  AXIS: {od['AXIS']:3d}°")
        print(f"Left Eye (OS):   SPH: {os['SPH']:+.2f}  CYL: {os['CYL']:+.2f}  AXIS: {os['AXIS']:3d}°")
        print(f"PD Distance:     {final_prescription['pd']['distance']:.1f} mm")
        print(f"PD Near:         {final_prescription['pd']['near']:.1f} mm")
        
        print("\n" + "-" * 80)
        print("⚠️  MEDICAL DISCLAIMER:")
        print("-" * 80)
        print("This is a PRELIMINARY ASSESSMENT ONLY and should NOT be used as a")
        print("medical prescription. A professional eye examination is required for")
        print("a valid prescription. Please schedule an appointment with a licensed")
        print("optometrist or ophthalmologist within 1-2 weeks.")
        
        print("\n" + "=" * 80)
        
        # Save report
        self._save_session_report(final_prescription)
    
    def _save_session_report(self, final_prescription: Dict[str, Any]) -> None:
        """Save session data to file"""
        report = {
            "session_id": self.session_id,
            "patient_id": self.patient_id,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "test_complete": self.test_complete,
            "patient_data": self.patient_data,
            "final_prescription": final_prescription,
            "session_log": self.session_log
        }
        
        # Save to exam_records
        records_dir = Path("exam_records")
        records_dir.mkdir(exist_ok=True)
        
        report_path = records_dir / f"{self.session_id}_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Session report saved to {report_path}")


class AIOptometrist:
    """
    High-level interface for AI Optometrist with clinical role enforcement
    """
    
    CLINICAL_ROLE = "AI Optometrist"
    SYSTEM_PROMPT = (
        "You are an AI Optometrist conducting a comprehensive eye examination. "
        "You must maintain your clinical role at all times. You are non-diagnostic "
        "and designed to collect preliminary vision data. Always emphasize that "
        "a professional optometrist must review all results."
    )
    
    @staticmethod
    def enforce_clinical_role(user_input: str) -> Optional[str]:
        """
        Detect and refuse persona-switching attempts
        
        Args:
            user_input: Patient input
            
        Returns:
            Refusal message if persona override detected, None otherwise
        """
        override_keywords = [
            "act as", "pretend", "be someone", "switch", "different role",
            "persona", "roleplay", "character", "forget", "ignore your",
            "stop being"
        ]
        
        user_lower = user_input.lower()
        
        for keyword in override_keywords:
            if keyword in user_lower:
                return (
                    "I appreciate your interest, but I need to maintain my role as "
                    "your AI Optometrist. This ensures accuracy and safety for your "
                    "eye examination. Let's continue with your test."
                )
        
        return None
    
    @staticmethod
    async def run_session(patient_id: str = "ANON", debug_mode: bool = False) -> AIOptumExamSession:
        """
        Run a complete examination session
        
        Args:
            patient_id: Patient identifier
            debug_mode: Enable debug logging
            
        Returns:
            Completed session object
        """
        session = AIOptumExamSession(patient_id=patient_id, debug_mode=debug_mode)
        await session.start_examination()
        return session


# Entry point
async def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("AI OPTUM - AI Optometrist Eye Examination System")
    print("=" * 80)
    print("\nWelcome! This system will guide you through a comprehensive eye exam.")
    print("Your responses help measure your vision refraction (sphere, cylinder, axis).")
    print("\n⚠️  IMPORTANT DISCLAIMER:")
    print("This is a preliminary assessment tool. A professional optometrist must")
    print("review results before any prescription is issued.")
    print("=" * 80 + "\n")
    
    # Get patient info
    patient_id = input("Enter patient ID (or press Enter for anonymous): ").strip()
    if not patient_id:
        patient_id = "ANON"
    
    debug = input("Enable debug mode? (y/n): ").lower() == 'y'
    
    # Run session
    session = await AIOptometrist.run_session(patient_id=patient_id, debug_mode=debug)
    
    print("\n" + "=" * 80)
    print("EXAMINATION COMPLETE")
    print(f"Session ID: {session.session_id}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

