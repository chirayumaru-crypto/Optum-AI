# AI Optum: Phoropter Control System
# Controls automated refraction device based on parsed patient responses

import json
import asyncio
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from chat_flow_config import STEP_PROGRESSION, PHOROPTER_CONTROLS


class EyeDesignation(Enum):
    """Right and Left Eye"""
    OD = "OD"  # Oculus Dexter (Right Eye)
    OS = "OS"  # Oculus Sinister (Left Eye)


class RefractiveParameter(Enum):
    """Refraction parameters"""
    SPHERE = "SPH"
    CYLINDER = "CYL"
    AXIS = "AXIS"


@dataclass
class LensConfiguration:
    """Lens parameters for eye"""
    sphere: float  # -20.00 to +20.00 diopters
    cylinder: float  # 0 to -6.00 diopters (negative for minus cyl)
    axis: int  # 0 to 180 degrees
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "SPH": self.sphere,
            "CYL": self.cylinder,
            "AXIS": self.axis
        }
    
    def from_dict(cls, data: Dict[str, Any]) -> "LensConfiguration":
        return cls(
            sphere=data.get("SPH", 0.0),
            cylinder=data.get("CYL", 0.0),
            axis=data.get("AXIS", 0)
        )


@dataclass
class PhoropeterState:
    """Current state of phoropter device"""
    od_lens: LensConfiguration  # Right eye
    os_lens: LensConfiguration  # Left eye
    current_eye: EyeDesignation  # Which eye being tested
    occluded_eye: Optional[EyeDesignation]  # Occluded eye (if any)
    pd_distance: float  # Pupillary distance at distance (mm)
    pd_near: float  # Pupillary distance at near (mm)
    test_step: str  # Current step (e.g., "6.1")
    lens_pair_index: int  # Index of current lens pair in test sequence
    adjustment_history: list  # Log of all adjustments
    timestamp: datetime  # Last update timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "od_lens": self.od_lens.to_dict(),
            "os_lens": self.os_lens.to_dict(),
            "current_eye": self.current_eye.value,
            "occluded_eye": self.occluded_eye.value if self.occluded_eye else None,
            "pd_distance": self.pd_distance,
            "pd_near": self.pd_near,
            "test_step": self.test_step,
            "lens_pair_index": self.lens_pair_index,
            "adjustment_history_count": len(self.adjustment_history),
            "timestamp": self.timestamp.isoformat()
        }


class PhoropterController:
    """
    Hardware control interface for automated refraction phoropter.
    Translates parsed patient responses to device commands.
    """
    
    def __init__(self, device_port: str = "COM3", baudrate: int = 9600):
        """
        Initialize phoropter controller
        
        Args:
            device_port: Serial port for phoropter (default: COM3)
            baudrate: Serial communication speed
        """
        self.device_port = device_port
        self.baudrate = baudrate
        self.connected = False
        
        # Initialize phoropter state
        self.state = PhoropeterState(
            od_lens=LensConfiguration(sphere=0.0, cylinder=0.0, axis=0),
            os_lens=LensConfiguration(sphere=0.0, cylinder=0.0, axis=0),
            current_eye=EyeDesignation.OD,
            occluded_eye=EyeDesignation.OS,
            pd_distance=63.0,  # Average adult PD
            pd_near=60.0,
            test_step="1.1",
            lens_pair_index=0,
            adjustment_history=[],
            timestamp=datetime.now()
        )
        
        # Safety constraints
        self.safety_limits = {
            "max_sphere_jump": 0.50,  # Max diopter adjustment per step
            "max_cylinder_jump": 0.50,
            "max_axis_jump": 10,  # degrees
            "max_session_duration": 1500,  # seconds (25 minutes)
            "sphere_range": (-20.0, 20.0),
            "cylinder_range": (0.0, 6.0),
            "axis_range": (0, 180)
        }
    
    async def connect(self) -> bool:
        """
        Establish connection to phoropter device
        
        Returns:
            True if connection successful
        """
        try:
            # TODO: Implement actual serial communication
            # import serial
            # self.serial_conn = serial.Serial(self.device_port, self.baudrate)
            self.connected = True
            print(f"✓ Connected to phoropter on {self.device_port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to phoropter: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from phoropter device"""
        try:
            # self.serial_conn.close()
            self.connected = False
            return True
        except:
            return False
    
    def adjust_sphere(self, eye: EyeDesignation, increment: float) -> Tuple[bool, str]:
        """
        Adjust sphere parameter for specified eye
        
        Args:
            eye: OD or OS
            increment: Positive or negative diopter change
            
        Returns:
            (success: bool, message: str)
        """
        # Get current lens
        current_lens = self.state.od_lens if eye == EyeDesignation.OD else self.state.os_lens
        new_sphere = current_lens.sphere + increment
        
        # Safety check: magnitude
        if abs(increment) > self.safety_limits["max_sphere_jump"]:
            return False, f"Unsafe jump: ±{abs(increment)} > ±{self.safety_limits['max_sphere_jump']}"
        
        # Safety check: range
        min_sph, max_sph = self.safety_limits["sphere_range"]
        if not (min_sph <= new_sphere <= max_sph):
            return False, f"Out of range: {new_sphere} not in [{min_sph}, {max_sph}]"
        
        # Apply adjustment
        if eye == EyeDesignation.OD:
            self.state.od_lens.sphere = new_sphere
        else:
            self.state.os_lens.sphere = new_sphere
        
        # Log adjustment
        self._log_adjustment(eye, RefractiveParameter.SPHERE, increment, new_sphere)
        
        return True, f"Adjusted {eye.value} sphere to {new_sphere:.2f}D"
    
    def adjust_cylinder(self, eye: EyeDesignation, increment: float) -> Tuple[bool, str]:
        """
        Adjust cylinder parameter for specified eye
        
        Args:
            eye: OD or OS
            increment: Positive or negative diopter change
            
        Returns:
            (success: bool, message: str)
        """
        current_lens = self.state.od_lens if eye == EyeDesignation.OD else self.state.os_lens
        new_cylinder = current_lens.cylinder + increment
        
        # Safety check: magnitude
        if abs(increment) > self.safety_limits["max_cylinder_jump"]:
            return False, f"Unsafe jump: ±{abs(increment)} > ±{self.safety_limits['max_cylinder_jump']}"
        
        # Safety check: range
        min_cyl, max_cyl = self.safety_limits["cylinder_range"]
        if not (min_cyl <= new_cylinder <= max_cyl):
            return False, f"Out of range: {new_cylinder} not in [{min_cyl}, {max_cyl}]"
        
        # Apply adjustment
        if eye == EyeDesignation.OD:
            self.state.od_lens.cylinder = new_cylinder
        else:
            self.state.os_lens.cylinder = new_cylinder
        
        self._log_adjustment(eye, RefractiveParameter.CYLINDER, increment, new_cylinder)
        
        return True, f"Adjusted {eye.value} cylinder to {new_cylinder:.2f}D"
    
    def adjust_axis(self, eye: EyeDesignation, increment: int) -> Tuple[bool, str]:
        """
        Adjust axis parameter for specified eye
        
        Args:
            eye: OD or OS
            increment: Positive or negative degree change
            
        Returns:
            (success: bool, message: str)
        """
        current_lens = self.state.od_lens if eye == EyeDesignation.OD else self.state.os_lens
        new_axis = (current_lens.axis + increment) % 180  # Wrap at 180
        
        # Safety check: magnitude
        if abs(increment) > self.safety_limits["max_axis_jump"]:
            return False, f"Unsafe jump: ±{abs(increment)}° > ±{self.safety_limits['max_axis_jump']}°"
        
        # Apply adjustment
        if eye == EyeDesignation.OD:
            self.state.od_lens.axis = new_axis
        else:
            self.state.os_lens.axis = new_axis
        
        self._log_adjustment(eye, RefractiveParameter.AXIS, increment, new_axis)
        
        return True, f"Adjusted {eye.value} axis to {new_axis}°"
    
    def set_occlusion(self, occluded_eye: Optional[EyeDesignation]) -> Tuple[bool, str]:
        """
        Set which eye is occluded during testing
        
        Args:
            occluded_eye: OD, OS, or None (both eyes open)
            
        Returns:
            (success: bool, message: str)
        """
        self.state.occluded_eye = occluded_eye
        if occluded_eye:
            return True, f"Occluded {occluded_eye.value}"
        else:
            return True, "Both eyes open (binocular)"
    
    def set_pd(self, pd_distance: float, pd_near: Optional[float] = None) -> Tuple[bool, str]:
        """
        Set pupillary distance
        
        Args:
            pd_distance: PD for distance vision (mm)
            pd_near: PD for near vision (mm), optional
            
        Returns:
            (success: bool, message: str)
        """
        if not (50 <= pd_distance <= 80):  # Typical range
            return False, f"PD out of typical range: {pd_distance}mm"
        
        self.state.pd_distance = pd_distance
        if pd_near:
            if not (45 <= pd_near <= 75):
                return False, f"Near PD out of typical range: {pd_near}mm"
            self.state.pd_near = pd_near
        else:
            self.state.pd_near = pd_distance - 3  # Typical near reduction
        
        return True, f"PD set to {pd_distance}mm (distance), {self.state.pd_near}mm (near)"
    
    def present_lens_pair(self, eye: EyeDesignation, 
                         lens1: LensConfiguration, 
                         lens2: LensConfiguration) -> Dict[str, Any]:
        """
        Present two lens options to patient for comparison
        
        Args:
            eye: OD or OS
            lens1: First lens option
            lens2: Second lens option
            
        Returns:
            Device command JSON
        """
        return {
            "command": "present_lens_pair",
            "eye": eye.value,
            "lens_1": lens1.to_dict(),
            "lens_2": lens2.to_dict(),
            "question": "Which lens makes the dot sharper and rounder?",
            "options": ["First lens", "Second lens", "Both same", "Neither clear"],
            "timestamp": datetime.now().isoformat()
        }
    
    def present_jcc_test(self, eye: EyeDesignation) -> Dict[str, Any]:
        """
        Present Jackson Cross Cylinder test for astigmatism
        
        Args:
            eye: OD or OS
            
        Returns:
            Device command JSON
        """
        current_lens = self.state.od_lens if eye == EyeDesignation.OD else self.state.os_lens
        
        return {
            "command": "present_jcc",
            "eye": eye.value,
            "current_prescription": current_lens.to_dict(),
            "test_sequence": [
                {"axis": "horizontal", "question": "Which axis position is clearer?"},
                {"axis": "vertical", "question": "Which axis position is clearer?"},
                {"duochrome": True, "question": "Red or green? Or equal?"}
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def present_duochrome_test(self, eye: EyeDesignation) -> Dict[str, Any]:
        """
        Present red-green duochrome balance test
        
        Args:
            eye: OD or OS
            
        Returns:
            Device command JSON
        """
        current_lens = self.state.od_lens if eye == EyeDesignation.OD else self.state.os_lens
        
        return {
            "command": "present_duochrome",
            "eye": eye.value,
            "current_prescription": current_lens.to_dict(),
            "question": "Are the red and green letters equally clear?",
            "options": ["Red clearer", "Green clearer", "Both equal"],
            "clinical_note": "Balance at green for slight myopic bias",
            "timestamp": datetime.now().isoformat()
        }
    
    def balance_binocular(self) -> Dict[str, Any]:
        """
        Present binocular balance test (both eyes open)
        
        Returns:
            Device command JSON
        """
        return {
            "command": "balance_binocular",
            "od_prescription": self.state.od_lens.to_dict(),
            "os_prescription": self.state.os_lens.to_dict(),
            "question": "Are both eyes equally clear, or is one clearer?",
            "options": ["Both equal", "Right eye clearer", "Left eye clearer"],
            "timestamp": datetime.now().isoformat()
        }
    
    def finalize_prescription(self) -> Dict[str, Any]:
        """
        Finalize prescription and generate report
        
        Returns:
            Final prescription JSON
        """
        return {
            "command": "finalize",
            "status": "PRESCRIPTION_COMPLETE",
            "final_prescription": {
                "OD": self.state.od_lens.to_dict(),
                "OS": self.state.os_lens.to_dict(),
            },
            "pd": {
                "distance": self.state.pd_distance,
                "near": self.state.pd_near
            },
            "timestamp": datetime.now().isoformat(),
            "session_duration_seconds": (datetime.now() - self.state.timestamp.replace(hour=0, minute=0, second=0)).total_seconds()
        }
    
    def execute_phoropter_action(self, action: str) -> Dict[str, Any]:
        """
        Execute a phoropter action command
        
        Args:
            action: Action string from parser (e.g., "adjust_sphere_positive_0.25_OD")
            
        Returns:
            Result dictionary with device state
        """
        result = {
            "action": action,
            "success": False,
            "message": "",
            "device_state": None
        }
        
        try:
            if "adjust_sphere_positive" in action:
                eye = EyeDesignation.OD if "OD" in action else EyeDesignation.OS
                success, msg = self.adjust_sphere(eye, 0.25)
                result["success"] = success
                result["message"] = msg
            
            elif "adjust_sphere_negative" in action:
                eye = EyeDesignation.OD if "OD" in action else EyeDesignation.OS
                success, msg = self.adjust_sphere(eye, -0.25)
                result["success"] = success
                result["message"] = msg
            
            elif "adjust_cylinder" in action:
                eye = EyeDesignation.OD if "OD" in action else EyeDesignation.OS
                success, msg = self.adjust_cylinder(eye, -0.25)
                result["success"] = success
                result["message"] = msg
            
            elif "adjust_axis" in action:
                eye = EyeDesignation.OD if "OD" in action else EyeDesignation.OS
                success, msg = self.adjust_axis(eye, 5)
                result["success"] = success
                result["message"] = msg
            
            elif "present_lens_pair" in action:
                eye = EyeDesignation.OD if "6.1" in action else EyeDesignation.OS
                self.set_occlusion(EyeDesignation.OS if eye == EyeDesignation.OD else EyeDesignation.OD)
                result["device_state"] = self.present_lens_pair(
                    eye,
                    LensConfiguration(self.state.od_lens.sphere if eye == EyeDesignation.OD else self.state.os_lens.sphere - 0.25, 0, 0),
                    LensConfiguration(self.state.od_lens.sphere if eye == EyeDesignation.OD else self.state.os_lens.sphere, 0, 0)
                )
                result["success"] = True
            
            elif "present_jcc" in action:
                eye = EyeDesignation.OD if "OD" in action else EyeDesignation.OS
                result["device_state"] = self.present_jcc_test(eye)
                result["success"] = True
            
            elif "balance" in action:
                result["device_state"] = self.balance_binocular()
                result["success"] = True
            
            elif "finalize" in action:
                result["device_state"] = self.finalize_prescription()
                result["success"] = True
            
            # Update device state
            result["device_state_summary"] = self.state.to_dict()
            
        except Exception as e:
            result["message"] = f"Error executing action: {str(e)}"
        
        return result
    
    def _log_adjustment(self, eye: EyeDesignation, parameter: RefractiveParameter, 
                       increment: float, new_value: float) -> None:
        """Log adjustment to history"""
        self.state.adjustment_history.append({
            "timestamp": datetime.now().isoformat(),
            "eye": eye.value,
            "parameter": parameter.value,
            "increment": increment,
            "new_value": new_value
        })
    
    def get_device_state(self) -> Dict[str, Any]:
        """Get current device state as JSON"""
        return self.state.to_dict()
    
    def get_adjustment_history(self) -> list:
        """Get complete adjustment history"""
        return self.state.adjustment_history


# Example usage
if __name__ == "__main__":
    controller = PhoropterController()
    
    print("=" * 80)
    print("PHOROPTER CONTROLLER - TEST SEQUENCE")
    print("=" * 80)
    
    # Step 1: Initial state
    print("\n1. Initial Device State:")
    print(json.dumps(controller.get_device_state(), indent=2))
    
    # Step 2: Set PD
    print("\n2. Setting Pupillary Distance:")
    success, msg = controller.set_pd(pd_distance=64.0)
    print(f"   {msg}")
    
    # Step 3: Adjust sphere OD
    print("\n3. Adjusting Sphere (Right Eye):")
    success, msg = controller.adjust_sphere(EyeDesignation.OD, -0.25)
    print(f"   {msg}")
    
    # Step 4: Present lens pair
    print("\n4. Presenting Lens Pair for OD:")
    lens_pair = controller.present_lens_pair(
        EyeDesignation.OD,
        LensConfiguration(-0.25, 0, 0),
        LensConfiguration(0, 0, 0)
    )
    print(json.dumps(lens_pair, indent=2, default=str))
    
    # Step 5: Final state
    print("\n5. Device State After Adjustments:")
    print(json.dumps(controller.get_device_state(), indent=2))
    
    # Step 6: Adjustment history
    print("\n6. Adjustment History:")
    for entry in controller.get_adjustment_history():
        print(f"   {entry}")
    
    print("\n" + "=" * 80)
