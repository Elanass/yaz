"""
Decision Engine Registry
Central registry for all clinical decision engines
"""

from typing import Dict, Type, Any, Optional, List
from abc import ABC, abstractmethod
import ipfshttpclient
from fhir.resources.patient import Patient
from fhir.resources.bundle import Bundle
import datetime
import smtplib
from email.mime.text import MIMEText
from graphviz import Digraph

from .adci_engine import ADCIEngine
from .gastrectomy_engine import GastrectomyEngine
from .flot_engine import FLOTEngine


class DecisionEngine(ABC):
    """Abstract base class for decision engines"""
    
    @abstractmethod
    async def process_decision(
        self,
        patient_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        include_alternatives: bool = True,
        confidence_threshold: float = 0.75
    ) -> Dict[str, Any]:
        """Process clinical decision"""
        pass
    
    def explain_recommendation(self, recommendation: Dict[str, Any]) -> str:
        """Provide a detailed explanation for a recommendation."""
        explanation = """
        This recommendation is based on the following factors:
        - Patient's clinical history
        - Current protocol guidelines
        - Risk assessment and confidence intervals
        
        Details:
        """
        for key, value in recommendation.items():
            explanation += f"- {key}: {value}\n"
        return explanation

    def generate_patient_explanation(self, recommendation: Dict[str, Any]) -> str:
        """Generate a simplified explanation for patients."""
        explanation = """
        Based on your medical history and current condition, we recommend the following:
        """
        for key, value in recommendation.items():
            explanation += f"- {key.replace('_', ' ').capitalize()}: {value}\n"
        explanation += "\nIf you have any questions, please consult your healthcare provider."
        return explanation

    def store_evidence_snapshot(self, evidence: Dict[str, Any]) -> str:
        """Store evidence snapshot on IPFS and return the CID."""
        try:
            client = ipfshttpclient.connect()
            res = client.add_json(evidence)
            return res  # CID of the stored evidence
        except Exception as e:
            raise RuntimeError(f"Failed to store evidence on IPFS: {str(e)}")

    def export_to_fhir(self, patient_data: Dict[str, Any]) -> str:
        """Export patient data to FHIR format."""
        try:
            patient = Patient(**patient_data)
            bundle = Bundle(entry=[{
                'resource': patient.dict()
            }])
            return bundle.json(indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to export to FHIR: {str(e)}")

    def import_from_fhir(self, fhir_data: str) -> Dict[str, Any]:
        """Import patient data from FHIR format."""
        from fhir.resources.bundle import Bundle
        try:
            bundle = Bundle.parse_raw(fhir_data)
            patient_data = {}
            for entry in bundle.entry:
                if entry.resource.resource_type == "Patient":
                    patient_data = entry.resource.dict()
            return patient_data
        except Exception as e:
            raise RuntimeError(f"Failed to import from FHIR: {str(e)}")

    def log_audit_event(self, user_id: str, action: str, resource: str):
        """Log an audit event for data access or modification."""
        timestamp = datetime.datetime.now().isoformat()
        audit_entry = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "timestamp": timestamp
        }
        # Here, you would typically write to a database or log file
        print(f"Audit Log: {audit_entry}")

    def get_audit_logs(self, resource: str) -> List[Dict[str, Any]]:
        """Retrieve audit logs for a specific resource."""
        # Placeholder: Replace with database query to fetch logs
        return [
            {"user_id": "user123", "action": "viewed", "resource": resource, "timestamp": "2025-07-24T10:00:00Z"},
            {"user_id": "user456", "action": "modified", "resource": resource, "timestamp": "2025-07-24T11:00:00Z"}
        ]

    def check_access(self, user_role: str, resource: str, action: str) -> bool:
        """Check if a user role has access to perform an action on a resource."""
        # Define role-based access control rules
        rbac_rules = {
            "admin": {"*": ["view", "modify", "delete"]},
            "clinician": {"patient_data": ["view", "modify"], "protocols": ["view"]},
            "auditor": {"audit_logs": ["view"]}
        }

        allowed_actions = rbac_rules.get(user_role, {}).get(resource, [])
        return action in allowed_actions or "*" in allowed_actions

    # Example usage
    def access_resource(self, user_role: str, resource: str, action: str):
        if not self.check_access(user_role, resource, action):
            raise PermissionError(f"Role '{user_role}' is not allowed to {action} {resource}")
        print(f"Access granted: {user_role} can {action} {resource}")

    def calculate_qol_score(self, patient_data: Dict[str, Any]) -> float:
        """Calculate a Quality of Life (QoL) score based on patient-reported outcomes."""
        qol_factors = patient_data.get("qol_factors", {})
        weights = {
            "physical_health": 0.4,
            "mental_health": 0.3,
            "social_support": 0.2,
            "financial_stress": 0.1
        }

        score = sum(qol_factors.get(factor, 0) * weight for factor, weight in weights.items())
        return round(score, 2)

    def integrate_qol_into_decision(self, decision: Dict[str, Any], qol_score: float) -> Dict[str, Any]:
        """Adjust the decision based on the QoL score."""
        decision["qol_score"] = qol_score
        if qol_score < 0.5:
            decision["recommendation"] = "Consider palliative care options due to low QoL."
        return decision

    def benchmark_outcomes(self, outcomes: Dict[str, Any], benchmarks: Dict[str, Any]) -> Dict[str, Any]:
        """Compare perioperative outcomes against benchmarks."""
        comparison = {}
        for metric, value in outcomes.items():
            benchmark = benchmarks.get(metric, None)
            if benchmark is not None:
                comparison[metric] = {
                    "value": value,
                    "benchmark": benchmark,
                    "status": "above" if value > benchmark else "below" if value < benchmark else "at"
                }
        return comparison

    # Example usage
    def analyze_outcomes(self, patient_id: str, outcomes: Dict[str, Any]):
        benchmarks = {
            "mortality_rate": 0.02,
            "complication_rate": 0.1,
            "readmission_rate": 0.15
        }
        comparison = self.benchmark_outcomes(outcomes, benchmarks)
        print(f"Outcome analysis for patient {patient_id}: {comparison}")

    def simulate_hypothesis(self, patient_data: Dict[str, Any], parameter_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate changes in patient parameters and observe the impact on recommendations."""
        simulated_data = patient_data.copy()
        simulated_data.update(parameter_changes)

        # Re-run the decision process with updated parameters
        simulated_decision = self.process_decision(
            patient_id=simulated_data.get("patient_id", "unknown"),
            parameters=simulated_data,
            context=simulated_data.get("clinical_context", {}),
            include_alternatives=True,
            confidence_threshold=0.75
        )

        return {
            "original_data": patient_data,
            "parameter_changes": parameter_changes,
            "simulated_decision": simulated_decision
        }

    def send_push_notification(self, user_email: str, subject: str, message: str):
        """Send a push notification via email."""
        try:
            smtp_server = "smtp.example.com"
            smtp_port = 587
            smtp_user = "noreply@example.com"
            smtp_password = "securepassword"

            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = user_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [user_email], msg.as_string())

            print(f"Notification sent to {user_email}")
        except Exception as e:
            raise RuntimeError(f"Failed to send notification: {str(e)}")

    # Example usage
    def notify_evidence_update(self, user_email: str, evidence_id: str):
        subject = "Evidence Update Notification"
        message = f"The evidence with ID {evidence_id} has been updated. Please review the changes."
        self.send_push_notification(user_email, subject, message)

    def update_consent(self, patient_id: str, consent_preferences: Dict[str, bool]):
        """Update a patient's data-sharing preferences."""
        # Placeholder: Replace with database update logic
        print(f"Updating consent for patient {patient_id}: {consent_preferences}")

    def get_consent_status(self, patient_id: str) -> Dict[str, bool]:
        """Retrieve a patient's current data-sharing preferences."""
        # Placeholder: Replace with database query logic
        return {
            "share_with_research": True,
            "share_with_insurance": False
        }

    # Example usage
    def manage_consent(self, patient_id: str, new_preferences: Dict[str, bool]):
        current_preferences = self.get_consent_status(patient_id)
        print(f"Current preferences for patient {patient_id}: {current_preferences}")
        self.update_consent(patient_id, new_preferences)
        print(f"Updated preferences for patient {patient_id}: {new_preferences}")

    def save_protocol_version(self, protocol_name: str, protocol_data: Dict[str, Any]):
        """Save a new version of a clinical protocol."""
        timestamp = datetime.datetime.now().isoformat()
        version_entry = {
            "protocol_name": protocol_name,
            "protocol_data": protocol_data,
            "timestamp": timestamp
        }
        # Placeholder: Replace with database or file storage logic
        print(f"Saved protocol version: {version_entry}")

    def get_protocol_versions(self, protocol_name: str) -> List[Dict[str, Any]]:
        """Retrieve the version history of a clinical protocol."""
        # Placeholder: Replace with database query logic
        return [
            {"protocol_name": protocol_name, "timestamp": "2025-07-01T10:00:00Z", "protocol_data": {"key": "value1"}},
            {"protocol_name": protocol_name, "timestamp": "2025-07-15T12:00:00Z", "protocol_data": {"key": "value2"}}
        ]

    # Example usage
    def manage_protocol_versions(self, protocol_name: str, new_data: Dict[str, Any]):
        self.save_protocol_version(protocol_name, new_data)
        versions = self.get_protocol_versions(protocol_name)
        print(f"Version history for {protocol_name}: {versions}")

    def get_eras_protocol(self, surgery_type: str) -> Dict[str, Any]:
        """Retrieve the enhanced recovery after surgery (ERAS) protocol for a specific surgery type."""
        # Placeholder: Replace with database or predefined protocol logic
        eras_protocols = {
            "gastrectomy": {
                "preoperative": ["Carbohydrate loading", "Smoking cessation", "Prehabilitation"],
                "intraoperative": ["Minimally invasive techniques", "Goal-directed fluid therapy"],
                "postoperative": ["Early mobilization", "Multimodal analgesia", "Early oral feeding"]
            }
        }
        return eras_protocols.get(surgery_type, {})

    def apply_eras_protocol(self, patient_id: str, surgery_type: str):
        """Apply the ERAS protocol to a patient's care plan."""
        protocol = self.get_eras_protocol(surgery_type)
        if not protocol:
            print(f"No ERAS protocol found for surgery type: {surgery_type}")
            return

        print(f"Applying ERAS protocol for patient {patient_id} undergoing {surgery_type}:")
        for phase, steps in protocol.items():
            print(f"  {phase.capitalize()}: {', '.join(steps)}")

    # Example usage
    def manage_eras(self, patient_id: str, surgery_type: str):
        self.apply_eras_protocol(patient_id, surgery_type)

    def calculate_risk_score(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate real-time risk scores for a patient based on clinical parameters."""
        risk_factors = patient_data.get("clinical_parameters", {})
        scores = {
            "operative_risk": self._calculate_operative_risk(risk_factors),
            "morbidity_risk": self._calculate_morbidity_risk(risk_factors),
            "mortality_risk": self._calculate_mortality_risk(risk_factors)
        }
        return scores

    def display_risk_scores(self, patient_id: str, risk_scores: Dict[str, Any]):
        """Display the calculated risk scores for a patient."""
        print(f"Risk scores for patient {patient_id}:")
        for risk_type, score in risk_scores.items():
            print(f"  {risk_type.capitalize()}: {score}")

    # Example usage
    def assess_patient_risks(self, patient_id: str, patient_data: Dict[str, Any]):
        risk_scores = self.calculate_risk_score(patient_data)
        self.display_risk_scores(patient_id, risk_scores)

    # Placeholder methods for risk calculations
    def _calculate_operative_risk(self, risk_factors: Dict[str, Any]) -> str:
        return "moderate"  # Replace with actual logic

    def _calculate_morbidity_risk(self, risk_factors: Dict[str, Any]) -> str:
        return "low"  # Replace with actual logic

    def _calculate_mortality_risk(self, risk_factors: Dict[str, Any]) -> str:
        return "high"  # Replace with actual logic

    def generate_decision_tree(self, recommendation: Dict[str, Any]) -> str:
        """Generate a decision tree visualization for a recommendation."""
        dot = Digraph()
        dot.node('A', 'Start')
        dot.node('B', 'Clinical History')
        dot.node('C', 'Risk Assessment')
        dot.node('D', 'Protocol Guidelines')
        dot.node('E', 'Recommendation')

        dot.edges(['AB', 'AC', 'AD', 'BE', 'CE', 'DE'])

        # Save and return the decision tree as a file path
        file_path = f"/tmp/decision_tree_{recommendation.get('id', 'default')}.gv"
        dot.render(file_path, format='png', cleanup=True)
        return f"{file_path}.png"

    def calculate_qol_metrics(self, patient_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Quality of Life (QoL) metrics based on patient data."""
        # Placeholder: Replace with actual QoL calculation logic
        qol_metrics = {
            "physical_health": 0.8,  # Example static value
            "mental_health": 0.75,
            "social_wellbeing": 0.85
        }
        return qol_metrics

class DecisionEngineRegistry:
    """Registry for managing decision engines"""
    
    def __init__(self):
        self._engines: Dict[str, Type[DecisionEngine]] = {}
        self._register_default_engines()
    
    def _register_default_engines(self):
        """Register default engines"""
        self.register("adci", ADCIEngine)
        self.register("gastrectomy", GastrectomyEngine)
        self.register("flot", FLOTEngine)
    
    def register(self, name: str, engine_class: Type[DecisionEngine]):
        """Register a decision engine"""
        self._engines[name] = engine_class
    
    def get_engine(self, name: str) -> DecisionEngine:
        """Get an engine instance by name"""
        if name not in self._engines:
            raise ValueError(f"Unknown engine: {name}")
        
        return self._engines[name]()
    
    def list_engines(self) -> Dict[str, Dict[str, Any]]:
        """List all available engines with metadata"""
        engines_info = {}
        
        for name, engine_class in self._engines.items():
            # Get engine instance for metadata
            engine = engine_class()
            
            engines_info[name] = {
                "name": name,
                "engine_name": getattr(engine, "engine_name", name),
                "engine_version": getattr(engine, "engine_version", "unknown"),
                "evidence_base": getattr(engine, "evidence_base", "unknown"),
                "description": self._get_engine_description(name)
            }
        
        return engines_info
    
    def _get_engine_description(self, name: str) -> str:
        """Get engine description"""
        descriptions = {
            "adci": "Adaptive Decision Confidence Index for treatment recommendations with uncertainty quantification",
            "gastrectomy": "Surgical approach and technique recommendations for gastric cancer resection",
            "flot": "Fluorouracil, Leucovorin, Oxaliplatin, and Docetaxel perioperative chemotherapy protocol"
        }
        return descriptions.get(name, "Clinical decision support engine")
    
    def update_protocol(self, name: str, protocol_data: Dict[str, Any]):
        """Update the protocol for a specific engine dynamically."""
        if name not in self._engines:
            raise ValueError(f"Engine {name} not found in registry")

        engine_instance = self.get_engine(name)
        if hasattr(engine_instance, 'update_protocol'):
            engine_instance.update_protocol(protocol_data)
        else:
            raise NotImplementedError(f"Engine {name} does not support dynamic protocol updates")


# Global registry instance
engine_registry = DecisionEngineRegistry()


# Convenience functions
def get_engine(name: str) -> DecisionEngine:
    """Get an engine instance"""
    return engine_registry.get_engine(name)


def list_engines() -> Dict[str, Dict[str, Any]]:
    """List all available engines"""
    return engine_registry.list_engines()


def register_engine(name: str, engine_class: Type[DecisionEngine]):
    """Register a new engine"""
    engine_registry.register(name, engine_class)
