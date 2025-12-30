# AI Optum: Session Monitoring & Safety Tracking
# Monitors patient fatigue, safety incidents, and quality metrics

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import deque
import numpy as np


logger = logging.getLogger(__name__)


class PatientFatigueMonitor:
    """
    Monitors patient fatigue during examination based on:
    - Response accuracy degradation
    - Hesitation/response time increase
    - Confidence drop
    - Speech quality (voice analysis)
    """
    
    def __init__(self, window_size: int = 5):
        """
        Initialize fatigue monitor
        
        Args:
            window_size: Number of recent responses to analyze
        """
        self.window_size = window_size
        self.response_history = deque(maxlen=window_size)
        self.hesitation_history = deque(maxlen=window_size)
        self.confidence_history = deque(maxlen=window_size)
    
    def add_response(self, response_data: Dict) -> None:
        """
        Add response to history for analysis
        
        Args:
            response_data: Dict with response metrics
                - accuracy: bool (correct response)
                - confidence: float (0.0-1.0)
                - hesitation: float (seconds of pause)
                - timestamp: datetime
        """
        self.response_history.append(response_data.get("accuracy", False))
        self.hesitation_history.append(response_data.get("hesitation", 0.0))
        self.confidence_history.append(response_data.get("confidence", 1.0))
    
    def check_fatigue(self) -> Tuple[bool, Optional[str]]:
        """
        Check for fatigue indicators
        
        Returns:
            (is_fatigued: bool, reason: Optional[str])
        """
        if len(self.response_history) < self.window_size:
            return False, None
        
        # Check accuracy degradation
        recent_accuracy = list(self.response_history)
        if len(recent_accuracy) >= 5:
            first_half = recent_accuracy[:len(recent_accuracy)//2]
            second_half = recent_accuracy[len(recent_accuracy)//2:]
            
            first_rate = sum(first_half) / len(first_half)
            second_rate = sum(second_half) / len(second_half)
            
            accuracy_drop = first_rate - second_rate
            if accuracy_drop > 0.20:  # 20% drop in accuracy
                return True, f"Accuracy degradation: {accuracy_drop:.0%} decrease"
        
        # Check hesitation increase
        hesitations = list(self.hesitation_history)
        avg_hesitation = np.mean(hesitations) if hesitations else 0
        if avg_hesitation > 3.0:  # Average 3+ second hesitation
            return True, f"Excessive hesitation: {avg_hesitation:.1f}s average pause"
        
        # Check confidence drop
        confidences = list(self.confidence_history)
        if len(confidences) >= 5:
            first_conf = np.mean(confidences[:len(confidences)//2])
            second_conf = np.mean(confidences[len(confidences)//2:])
            conf_drop = first_conf - second_conf
            
            if conf_drop > 0.30:  # 30% confidence drop
                return True, f"Confidence degradation: {conf_drop:.0%} decrease"
        
        return False, None
    
    def get_fatigue_score(self) -> float:
        """
        Calculate overall fatigue score (0.0 = fresh, 1.0 = exhausted)
        
        Returns:
            Fatigue score
        """
        if not self.response_history:
            return 0.0
        
        accuracy_score = 1.0 - (sum(self.response_history) / len(self.response_history))
        hesitation_score = min(1.0, np.mean(self.hesitation_history) / 5.0)
        confidence_score = 1.0 - np.mean(self.confidence_history)
        
        # Weighted average
        fatigue = (accuracy_score * 0.4 + hesitation_score * 0.3 + confidence_score * 0.3)
        return min(1.0, max(0.0, fatigue))


class SessionDurationMonitor:
    """
    Monitors session duration and provides timing guidance
    """
    
    DURATION_LIMITS = {
        "recommended_max": 20 * 60,      # 20 minutes
        "warning_threshold": 15 * 60,    # 15 minutes (suggest break)
        "hard_limit": 25 * 60            # 25 minutes (must stop)
    }
    
    def __init__(self, start_time: datetime):
        """
        Initialize duration monitor
        
        Args:
            start_time: Session start time
        """
        self.start_time = start_time
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def check_duration_status(self) -> Tuple[str, Optional[str]]:
        """
        Check session duration status
        
        Returns:
            (status: str, message: Optional[str])
            status: "continue" | "offer_break" | "warn_completion" | "hard_stop"
        """
        elapsed = self.get_elapsed_time()
        
        if elapsed > self.DURATION_LIMITS["hard_limit"]:
            return "hard_stop", (
                f"Test must end (exceeded {self.DURATION_LIMITS['hard_limit']/60:.0f} minute limit). "
                "This protects your comfort and vision."
            )
        
        elif elapsed > self.DURATION_LIMITS["recommended_max"]:
            return "warn_completion", (
                f"We're approaching the recommended test duration. "
                f"Let's complete the final steps."
            )
        
        elif elapsed > self.DURATION_LIMITS["warning_threshold"]:
            remaining = self.DURATION_LIMITS["recommended_max"] - elapsed
            return "offer_break", (
                f"We've been testing for {elapsed/60:.0f} minutes. "
                f"Would you like a 2-minute break?"
            )
        
        else:
            return "continue", None


class SafetyIncidentTracker:
    """
    Tracks safety incidents and escalations
    """
    
    def __init__(self):
        self.incidents = []
        self.escalations = []
    
    def log_incident(self, incident_type: str, description: str, severity: str = "LOW") -> None:
        """
        Log a safety incident
        
        Args:
            incident_type: Type of incident
            description: Detailed description
            severity: LOW | MEDIUM | HIGH | CRITICAL
        """
        incident = {
            "timestamp": datetime.now().isoformat(),
            "type": incident_type,
            "description": description,
            "severity": severity
        }
        self.incidents.append(incident)
        
        if severity in ["HIGH", "CRITICAL"]:
            self.escalations.append(incident)
        
        logger.warning(f"Safety incident logged: {incident_type} ({severity}) - {description}")
    
    def log_escalation(self, escalation_reason: str, recommendation: str) -> None:
        """Log test escalation"""
        escalation = {
            "timestamp": datetime.now().isoformat(),
            "reason": escalation_reason,
            "recommendation": recommendation
        }
        self.escalations.append(escalation)
        logger.critical(f"Test escalated: {escalation_reason}")
    
    def get_incident_count(self, severity: str = None) -> int:
        """Get count of incidents (optionally by severity)"""
        if severity:
            return sum(1 for inc in self.incidents if inc["severity"] == severity)
        return len(self.incidents)
    
    def should_escalate(self) -> Tuple[bool, Optional[str]]:
        """Check if escalation is warranted"""
        critical_incidents = [inc for inc in self.incidents if inc["severity"] == "CRITICAL"]
        
        if critical_incidents:
            return True, critical_incidents[0]["description"]
        
        high_incidents = [inc for inc in self.incidents if inc["severity"] == "HIGH"]
        if len(high_incidents) >= 2:
            return True, f"Multiple high-severity issues detected"
        
        return False, None


class ExaminationQualityMonitor:
    """
    Monitors quality metrics of the examination
    """
    
    def __init__(self):
        self.responses_analyzed = 0
        self.parse_failures = 0
        self.confidence_scores = []
        self.phoropter_actions = []
    
    def record_response(self, parsed: Dict) -> None:
        """Record parsed response metrics"""
        self.responses_analyzed += 1
        confidence = parsed.get("confidence", 0.5)
        self.confidence_scores.append(confidence)
        
        if parsed.get("fallback"):
            self.parse_failures += 1
    
    def record_phoropter_action(self, action: str, success: bool) -> None:
        """Record phoropter action result"""
        self.phoropter_actions.append({
            "action": action,
            "success": success
        })
    
    def get_quality_metrics(self) -> Dict[str, float]:
        """Get overall quality metrics"""
        if not self.responses_analyzed:
            return {}
        
        parse_success_rate = 1.0 - (self.parse_failures / self.responses_analyzed)
        avg_confidence = np.mean(self.confidence_scores) if self.confidence_scores else 0.0
        
        phoropter_success = 0.0
        if self.phoropter_actions:
            phoropter_success = sum(1 for a in self.phoropter_actions if a["success"]) / len(self.phoropter_actions)
        
        return {
            "responses_analyzed": self.responses_analyzed,
            "parse_success_rate": parse_success_rate,
            "average_confidence": avg_confidence,
            "phoropter_success_rate": phoropter_success
        }
    
    def is_quality_acceptable(self) -> bool:
        """Check if examination quality is acceptable"""
        metrics = self.get_quality_metrics()
        
        # All key metrics must meet minimum standards
        return (
            metrics.get("parse_success_rate", 0) >= 0.90 and  # 90%+ parsing success
            metrics.get("average_confidence", 0) >= 0.70 and  # 70%+ average confidence
            metrics.get("phoropter_success_rate", 1.0) >= 0.95  # 95%+ device commands
        )


class ComprehensiveSessionMonitor:
    """
    Comprehensive monitor combining all monitoring systems
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.fatigue_monitor = PatientFatigueMonitor()
        self.duration_monitor = SessionDurationMonitor(self.start_time)
        self.incident_tracker = SafetyIncidentTracker()
        self.quality_monitor = ExaminationQualityMonitor()
    
    def check_session_status(self) -> Tuple[str, Optional[str]]:
        """
        Comprehensive session status check
        
        Returns:
            (status: str, message: Optional[str])
            status: "continue" | "pause_break" | "warn" | "escalate" | "halt"
        """
        # Check for critical escalations first
        should_escalate, reason = self.incident_tracker.should_escalate()
        if should_escalate:
            return "halt", reason
        
        # Check duration
        duration_status, duration_msg = self.duration_monitor.check_duration_status()
        if duration_status == "hard_stop":
            return "halt", duration_msg
        elif duration_status == "warn_completion":
            return "warn", duration_msg
        elif duration_status == "offer_break":
            return "pause_break", duration_msg
        
        # Check fatigue
        is_fatigued, fatigue_reason = self.fatigue_monitor.check_fatigue()
        if is_fatigued:
            fatigue_score = self.fatigue_monitor.get_fatigue_score()
            if fatigue_score > 0.7:  # Severe fatigue
                return "escalate", f"Severe patient fatigue detected: {fatigue_reason}"
            else:  # Mild fatigue
                return "pause_break", f"Patient may need a break: {fatigue_reason}"
        
        # All systems nominal
        return "continue", None
    
    def get_session_report(self) -> Dict:
        """Generate comprehensive session report"""
        return {
            "duration_seconds": self.duration_monitor.get_elapsed_time(),
            "fatigue_score": self.fatigue_monitor.get_fatigue_score(),
            "incident_count": self.incident_tracker.get_incident_count(),
            "critical_incidents": self.incident_tracker.get_incident_count("CRITICAL"),
            "quality_metrics": self.quality_monitor.get_quality_metrics(),
            "quality_acceptable": self.quality_monitor.is_quality_acceptable()
        }


if __name__ == "__main__":
    # Test monitoring systems
    monitor = ComprehensiveSessionMonitor()
    
    print("AI OPTUM - Session Monitoring Systems")
    print("=" * 80)
    
    # Simulate some responses
    print("\nSimulating patient responses...")
    for i in range(5):
        monitor.fatigue_monitor.add_response({
            "accuracy": True,
            "confidence": 0.9 - (i * 0.05),
            "hesitation": 1.0 + (i * 0.3)
        })
    
    # Check status
    status, message = monitor.check_session_status()
    print(f"Session Status: {status}")
    if message:
        print(f"Message: {message}")
    
    # Get report
    report = monitor.get_session_report()
    print("\nSession Report:")
    for key, value in report.items():
        print(f"  {key}: {value}")
