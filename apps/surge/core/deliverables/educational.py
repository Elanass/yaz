#!/usr/bin/env python3
"""Educational Content Generation for SurgeAI Platform
Interactive case studies, patient education, and training materials
Multi-language support for global medical education.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.surge.core.models.medical import CohortAnalysis, SRCCCase


logger = logging.getLogger(__name__)


class EducationalContentGenerator:
    """Generate educational content from clinical data."""

    def __init__(self) -> None:
        self.content_types = {
            "case_study": self.generate_case_study,
            "patient_education": self.generate_patient_education_infographic,
            "resident_training": self.generate_resident_training_module,
            "infographic": self.generate_patient_education_infographic,
            "protocol_guide": self.generate_protocol_guide,
        }

    def generate_case_study(
        self, case: SRCCCase, learning_objectives: list[str] | None = None
    ) -> dict[str, Any]:
        """Generate interactive case study from SRCC case."""
        if not learning_objectives:
            learning_objectives = [
                "Recognize clinical presentation of signet ring cell carcinoma",
                "Apply appropriate TNM staging principles",
                "Select optimal treatment protocols",
                "Interpret survival outcomes and prognostic factors",
            ]

        return {
            "metadata": {
                "title": f"Case Study: {case.patient_id} - Signet Ring Cell Carcinoma",
                "case_id": case.case_id,
                "generated_date": datetime.now().isoformat(),
                "learning_objectives": learning_objectives,
                "estimated_duration": "45 minutes",
                "difficulty_level": "Intermediate",
            },
            "patient_presentation": self._create_patient_presentation(case),
            "clinical_questions": self._generate_clinical_questions(case),
            "diagnostic_workup": self._create_diagnostic_workup(case),
            "treatment_planning": self._create_treatment_planning(case),
            "outcome_analysis": self._create_outcome_analysis(case),
            "discussion_points": self._generate_discussion_points(case),
            "references": self._generate_educational_references(),
        }

    def generate_patient_education_infographic(
        self, topic: str, cases: list[SRCCCase]
    ) -> dict[str, Any]:
        """Generate patient education infographic content."""
        return {
            "metadata": {
                "title": f"Understanding {topic}",
                "target_audience": "Patients and Families",
                "language_support": ["English", "French"],
                "generated_date": datetime.now().isoformat(),
            },
            "sections": {
                "what_is_srcc": self._explain_srcc_for_patients(),
                "symptoms_to_watch": self._create_symptom_guide(cases),
                "treatment_options": self._explain_treatments_for_patients(),
                "what_to_expect": self._create_treatment_timeline(),
                "support_resources": self._generate_support_resources(),
                "french_terminology": self._create_french_patient_terms(),
            },
            "visual_elements": self._describe_infographic_visuals(),
            "action_items": self._create_patient_action_items(),
        }

    def generate_resident_training_module(
        self, cohort: CohortAnalysis
    ) -> dict[str, Any]:
        """Generate comprehensive training module for surgical residents."""
        return {
            "metadata": {
                "title": "Signet Ring Cell Carcinoma: A Comprehensive Training Module",
                "target_audience": "Surgical Residents",
                "learning_level": "Advanced",
                "estimated_duration": "2 hours",
                "cme_credits": 2.0,
                "generated_date": datetime.now().isoformat(),
            },
            "learning_objectives": [
                "Master TNM staging principles for gastric SRCC",
                "Evaluate treatment protocol selection criteria",
                "Interpret survival data and prognostic factors",
                "Develop multidisciplinary treatment plans",
                "Understand international collaboration in surgical research",
            ],
            "modules": {
                "module1": self._create_pathology_module(cohort),
                "module2": self._create_staging_module(cohort),
                "module3": self._create_treatment_module(cohort),
                "module4": self._create_outcomes_module(cohort),
                "module5": self._create_research_module(cohort),
            },
            "assessments": self._create_resident_assessments(cohort),
            "case_scenarios": self._create_training_scenarios(cohort),
        }

    def generate_protocol_guide(
        self, treatment_protocol: str, cases: list[SRCCCase]
    ) -> dict[str, Any]:
        """Generate treatment protocol guide."""
        protocol_cases = [
            case
            for case in cases
            if any(
                tp.protocol.value == treatment_protocol
                for tp in case.treatment_protocols
            )
        ]

        return {
            "metadata": {
                "title": f"{treatment_protocol} Protocol Guide for SRCC",
                "version": "1.0",
                "evidence_level": "Level II",
                "generated_date": datetime.now().isoformat(),
                "based_on_cases": len(protocol_cases),
            },
            "indication_criteria": self._create_indication_criteria(treatment_protocol),
            "contraindications": self._create_contraindications(treatment_protocol),
            "dosing_schedule": self._create_dosing_schedule(treatment_protocol),
            "monitoring_guidelines": self._create_monitoring_guidelines(
                treatment_protocol
            ),
            "toxicity_management": self._create_toxicity_management(treatment_protocol),
            "outcome_expectations": self._analyze_protocol_outcomes(protocol_cases),
            "quality_measures": self._create_quality_measures(treatment_protocol),
            "patient_education": self._create_protocol_patient_education(
                treatment_protocol
            ),
        }

    def _create_patient_presentation(self, case: SRCCCase) -> dict[str, Any]:
        """Create patient presentation section."""
        return {
            "demographics": {
                "age": case.age,
                "gender": "Male" if case.gender == "M" else "Female",
                "bmi": case.bmi if case.bmi else "Not documented",
            },
            "chief_complaint": self._generate_chief_complaint(case),
            "history_of_present_illness": self._generate_hpi(case),
            "physical_examination": self._generate_physical_exam(case),
            "initial_impression": "Evaluate for gastric malignancy given presenting symptoms",
        }

    def _generate_chief_complaint(self, case: SRCCCase) -> str:
        """Generate chief complaint based on case data."""
        complaints = []

        # Check both French and English symptoms
        all_symptoms = []
        if case.symptoms_french:
            all_symptoms.extend(
                [
                    symptom.value if hasattr(symptom, "value") else str(symptom)
                    for symptom in case.symptoms_french
                ]
            )
        if case.symptoms_english:
            all_symptoms.extend(case.symptoms_english)

        if all_symptoms:
            for symptom in all_symptoms[:2]:  # Use first 2 symptoms
                if symptom in ["abdominal_pain", "douleur_abdominale"]:
                    complaints.append("abdominal pain")
                elif symptom in ["nausea", "nausées"]:
                    complaints.append("nausea and vomiting")
                elif symptom in ["weight_loss", "perte_de_poids"]:
                    complaints.append("unintentional weight loss")
                elif symptom in ["fatigue"]:
                    complaints.append("fatigue")

        if not complaints:
            complaints = ["abdominal discomfort", "early satiety"]

        duration = "2-3 months" if len(complaints) > 1 else "4-6 weeks"
        return f"{' and '.join(complaints)} for the past {duration}"

    def _generate_hpi(self, case: SRCCCase) -> str:
        """Generate history of present illness."""
        age = case.age
        gender = "male" if case.gender == "M" else "female"

        hpi = f"A {age}-year-old {gender} presents with progressive symptoms including "

        # Check both French and English symptoms
        all_symptoms = []
        if case.symptoms_french:
            all_symptoms.extend(
                [
                    symptom.value if hasattr(symptom, "value") else str(symptom)
                    for symptom in case.symptoms_french
                ]
            )
        if case.symptoms_english:
            all_symptoms.extend(case.symptoms_english)

        if all_symptoms:
            symptom_descriptions = []
            for symptom in all_symptoms:
                if symptom in ["abdominal_pain", "douleur_abdominale"]:
                    symptom_descriptions.append(
                        "epigastric pain that worsens after meals"
                    )
                elif symptom in ["weight_loss", "perte_de_poids"]:
                    symptom_descriptions.append("10-15 pound unintentional weight loss")
                elif symptom in ["nausea", "nausées"]:
                    symptom_descriptions.append(
                        "persistent nausea with occasional vomiting"
                    )

            if symptom_descriptions:
                hpi += ", ".join(symptom_descriptions[:3])
            else:
                hpi += "dyspepsia and early satiety"
        else:
            hpi += "dyspepsia and early satiety"

        hpi += ". No fever, no hematemesis, no melena reported. No family history of gastric cancer."
        return hpi

    def _generate_physical_exam(self, case: SRCCCase) -> dict[str, str]:
        """Generate physical examination findings."""
        return {
            "vital_signs": "BP 130/80, HR 88, Temp 98.6°F, Weight appropriate for height",
            "general": "Alert, oriented, appears mildly uncomfortable",
            "cardiovascular": "Regular rate and rhythm, no murmurs",
            "pulmonary": "Clear to auscultation bilaterally",
            "abdomen": "Mild epigastric tenderness, no masses palpated, no hepatosplenomegaly",
            "extremities": "No edema, no lymphadenopathy",
            "neurologic": "Grossly intact",
        }

    def _generate_clinical_questions(self, case: SRCCCase) -> list[dict[str, Any]]:
        """Generate clinical questions for case study."""
        return [
            {
                "question": "What is the most likely diagnosis based on the clinical presentation?",
                "type": "multiple_choice",
                "options": [
                    "Gastric adenocarcinoma - intestinal type",
                    "Signet ring cell carcinoma",
                    "Gastric lymphoma",
                    "Peptic ulcer disease",
                ],
                "correct_answer": "Signet ring cell carcinoma",
                "explanation": "The clinical presentation and imaging findings are most consistent with signet ring cell carcinoma, particularly given the infiltrative growth pattern.",
            },
            {
                "question": f"How would you stage this patient's tumor as {case.tnm_staging.tnm_string}?",
                "type": "staging_exercise",
                "correct_staging": {
                    "T_stage": case.tnm_staging.tumor.value,
                    "N_stage": case.tnm_staging.node.value,
                    "M_stage": case.tnm_staging.metastasis.value,
                    "overall_stage": case.tnm_staging.stage_group,
                },
                "explanation": "TNM staging is critical for treatment planning and prognosis determination.",
            },
            {
                "question": "What treatment approach would you recommend?",
                "type": "treatment_planning",
                "considerations": [
                    "Patient performance status",
                    "Tumor stage and resectability",
                    "Histological subtype implications",
                    "Multidisciplinary team input",
                ],
            },
        ]

    def _create_diagnostic_workup(self, case: SRCCCase) -> dict[str, Any]:
        """Create diagnostic workup section."""
        return {
            "initial_studies": [
                "Complete blood count",
                "Comprehensive metabolic panel",
                "CEA and CA 19-9 tumor markers",
                "Upper endoscopy with biopsy",
            ],
            "imaging_studies": [
                "CT chest/abdomen/pelvis with contrast",
                "EUS (if available)",
                "PET/CT for staging",
            ],
            "pathology_findings": {
                "histology": case.histology.value,
                "special_features": "Signet ring cells with intracytoplasmic mucin",
                "immunohistochemistry": "CDX2 negative, GATA4/6 positive",
            },
            "staging_results": {
                "tnm_stage": case.tnm_staging.tnm_string,
                "stage_group": case.tnm_staging.stage_group,
            },
        }

    def _create_treatment_planning(self, case: SRCCCase) -> dict[str, Any]:
        """Create treatment planning section."""
        return {
            "multidisciplinary_team": [
                "Surgical oncology",
                "Medical oncology",
                "Radiation oncology",
                "Pathology",
                "Radiology",
                "Nutrition",
            ],
            "treatment_options": [
                {
                    "option": "Perioperative chemotherapy + surgery",
                    "protocols": ["FLOT", "XELOX"],
                    "indication": "Resectable disease, good performance status",
                },
                {
                    "option": "Neoadjuvant chemotherapy + surgery",
                    "protocols": ["ECF", "ECX"],
                    "indication": "Locally advanced resectable disease",
                },
                {
                    "option": "Palliative chemotherapy",
                    "protocols": ["FOLFOX", "Capecitabine"],
                    "indication": "Metastatic disease",
                },
            ],
            "selected_treatment": {
                "rationale": f"Based on {case.tnm_staging.stage_group} disease",
                "protocol": case.primary_treatment.protocol.value
                if case.primary_treatment
                else "Not specified",
                "expected_outcomes": self._describe_expected_outcomes(case),
            },
        }

    def _create_outcome_analysis(self, case: SRCCCase) -> dict[str, Any]:
        """Create outcome analysis section."""
        outcome_data = {
            "surgical_outcome": case.surgical_outcome.value
            if case.surgical_outcome
            else "Not performed",
            "treatment_completion": "Completed as planned"
            if case.primary_treatment
            and case.primary_treatment.completion_rate
            and case.primary_treatment.completion_rate > 80
            else "Modified due to toxicity",
            "complications": case.complications
            if case.complications
            else ["None documented"],
            "follow_up_status": case.survival_metrics.survival_status
            if case.survival_metrics
            else "Follow-up ongoing",
        }

        if case.survival_metrics:
            outcome_data["survival_data"] = {
                "overall_survival": f"{case.survival_metrics.overall_survival_months:.1f} months"
                if case.survival_metrics.overall_survival_months
                else "Not reached",
                "vital_status": case.survival_metrics.vital_status,
                "event_occurred": case.survival_metrics.event_occurred,
            }

        return outcome_data

    def _generate_discussion_points(self, case: SRCCCase) -> list[str]:
        """Generate discussion points for case study."""
        return [
            "Unique characteristics of signet ring cell carcinoma vs. conventional adenocarcinoma",
            "Impact of histological subtype on treatment selection and outcomes",
            "Role of perioperative chemotherapy in SRCC",
            "Prognostic factors and survival expectations",
            "Importance of multidisciplinary care coordination",
            "International collaboration in rare cancer research",
            f"Significance of achieving {case.surgical_outcome.value} surgical resection"
            if case.surgical_outcome
            else "Surgical considerations in SRCC",
        ]

    def _explain_srcc_for_patients(self) -> dict[str, str]:
        """Explain SRCC in patient-friendly language."""
        return {
            "what_is_it": """
Signet ring cell carcinoma (SRCC) is a specific type of stomach cancer. The cancer cells
have a distinctive appearance under the microscope - they look like signet rings because
of how the cells are shaped. This type of cancer behaves differently from other stomach
cancers and may require specialized treatment approaches.
            """.strip(),
            "how_common": """
SRCC represents about 10-15% of all stomach cancers. While it's less common than other
types, specialized medical teams have extensive experience treating this condition.
            """.strip(),
            "key_characteristics": """
• Grows in a spreading pattern through the stomach wall
• May be harder to detect in early stages
• Requires specialized treatment planning
• Benefits from care by experienced medical teams
            """.strip(),
        }

    def _create_symptom_guide(self, cases: list[SRCCCase]) -> dict[str, Any]:
        """Create symptom guide for patients."""
        # Analyze common symptoms from cases
        all_symptoms = []
        for case in cases:
            if case.symptoms_french:
                all_symptoms.extend([symptom.value for symptom in case.symptoms_french])

        return {
            "early_symptoms": [
                "Persistent stomach pain or discomfort",
                "Feeling full quickly when eating",
                "Nausea or vomiting",
                "Loss of appetite",
                "Unintended weight loss",
            ],
            "advanced_symptoms": [
                "Severe abdominal pain",
                "Vomiting blood or coffee-ground material",
                "Black, tarry stools",
                "Severe fatigue",
                "Difficulty swallowing",
            ],
            "when_to_seek_care": [
                "Symptoms persist for more than 2 weeks",
                "Any vomiting of blood",
                "Black or bloody stools",
                "Severe weight loss",
                "Difficulty eating or drinking",
            ],
            "french_terms": {
                "Épigastralgie": "Upper stomach pain",
                "Vomissement": "Vomiting",
                "Amaigrissement": "Weight loss",
                "Dysphagie": "Difficulty swallowing",
            },
        }

    def _explain_treatments_for_patients(self) -> dict[str, Any]:
        """Explain treatment options in patient-friendly terms."""
        return {
            "chemotherapy": {
                "description": "Medicines that fight cancer cells throughout the body",
                "common_protocols": {
                    "FLOT": "A combination of four medicines given before and after surgery",
                    "XELOX": "A two-medicine combination that can be given as pills and IV",
                },
                "what_to_expect": "Usually given in cycles with rest periods between treatments",
            },
            "surgery": {
                "description": "Removal of the cancerous part of the stomach",
                "types": {
                    "Partial gastrectomy": "Removing part of the stomach",
                    "Total gastrectomy": "Removing the entire stomach",
                },
                "recovery": "Hospital stay of 7-14 days with gradual return to normal activities",
            },
            "combined_approach": {
                "description": "Using chemotherapy and surgery together for the best outcomes",
                "timeline": "Chemotherapy → Surgery → More chemotherapy (if recommended)",
            },
        }

    def _create_treatment_timeline(self) -> list[dict[str, str]]:
        """Create treatment timeline for patients."""
        return [
            {
                "phase": "Diagnosis and Staging",
                "duration": "1-2 weeks",
                "activities": "Tests to determine cancer stage and treatment plan",
            },
            {
                "phase": "Pre-treatment Preparation",
                "duration": "1 week",
                "activities": "Meeting with treatment team, preparation for chemotherapy",
            },
            {
                "phase": "Neoadjuvant Chemotherapy",
                "duration": "3-4 months",
                "activities": "Chemotherapy to shrink tumor before surgery",
            },
            {
                "phase": "Surgery",
                "duration": "1-2 weeks",
                "activities": "Surgical removal of cancer and recovery in hospital",
            },
            {
                "phase": "Recovery and Adjuvant Treatment",
                "duration": "3-6 months",
                "activities": "Healing from surgery and additional chemotherapy if recommended",
            },
            {
                "phase": "Long-term Follow-up",
                "duration": "Ongoing",
                "activities": "Regular check-ups and monitoring for 5+ years",
            },
        ]

    def _create_french_patient_terms(self) -> dict[str, str]:
        """Create French medical terms for international patients."""
        return {
            "Adénocarcinome à cellules en bague à chaton": "Signet ring cell adenocarcinoma",
            "Chimiothérapie néoadjuvante": "Neoadjuvant chemotherapy",
            "Gastrectomie": "Gastrectomy (stomach removal)",
            "Stade TNM": "TNM staging",
            "Survie globale": "Overall survival",
            "Équipe multidisciplinaire": "Multidisciplinary team",
            "Pronostic": "Prognosis",
            "Récidive": "Recurrence",
        }

    def _describe_infographic_visuals(self) -> list[dict[str, str]]:
        """Describe visual elements for infographic."""
        return [
            {
                "element": "Anatomical diagram",
                "description": "Simple illustration of stomach with highlighted areas showing where SRCC typically develops",
            },
            {
                "element": "Cell comparison",
                "description": "Visual comparison between normal stomach cells and signet ring cancer cells",
            },
            {
                "element": "Treatment timeline",
                "description": "Visual flowchart showing typical treatment journey from diagnosis to follow-up",
            },
            {
                "element": "Symptom checklist",
                "description": "Icon-based checklist of symptoms to watch for",
            },
        ]

    def _create_patient_action_items(self) -> list[str]:
        """Create actionable items for patients."""
        return [
            "Keep a symptom diary to track any changes",
            "Prepare questions for your medical team",
            "Connect with support groups or counseling services",
            "Maintain nutrition during treatment",
            "Stay active as approved by your care team",
            "Follow all appointment schedules",
            "Communicate any side effects promptly",
        ]

    def _generate_educational_references(self) -> list[dict[str, str]]:
        """Generate educational references."""
        return [
            {
                "title": "Signet Ring Cell Carcinoma: Current Perspectives",
                "source": "Journal of Surgical Oncology",
                "type": "Peer-reviewed article",
                "relevance": "Comprehensive overview of SRCC characteristics",
            },
            {
                "title": "Patient Guide to Stomach Cancer",
                "source": "National Cancer Institute",
                "type": "Patient education resource",
                "relevance": "General stomach cancer information",
            },
            {
                "title": "Multidisciplinary Care in Gastric Cancer",
                "source": "Clinical Oncology Review",
                "type": "Professional guidelines",
                "relevance": "Treatment team coordination",
            },
        ]

    def export_case_study_html(
        self, case_study: dict[str, Any], output_path: Path
    ) -> None:
        """Export case study to interactive HTML format."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{case_study["metadata"]["title"]}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .case-header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .question {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .learning-objectives {{ background: #f3e5f5; padding: 15px; border-radius: 5px; }}
        ul {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="case-header">
        <h1>{case_study["metadata"]["title"]}</h1>
        <p><strong>Duration:</strong> {case_study["metadata"]["estimated_duration"]}</p>
        <p><strong>Difficulty:</strong> {case_study["metadata"]["difficulty_level"]}</p>
        <div class="learning-objectives">
            <h3>Learning Objectives</h3>
            <ul>
                {"".join([f"<li>{obj}</li>" for obj in case_study["metadata"]["learning_objectives"]])}
            </ul>
        </div>
    </div>

    <div class="section">
        <h2>Patient Presentation</h2>
        <p><strong>Demographics:</strong> {case_study["patient_presentation"]["demographics"]["age"]} year old {case_study["patient_presentation"]["demographics"]["gender"]}</p>
        <p><strong>Chief Complaint:</strong> {case_study["patient_presentation"]["chief_complaint"]}</p>
    </div>

    <div class="section">
        <h2>Clinical Questions</h2>
        {"".join([f'<div class="question"><h4>{q["question"]}</h4><p>{q.get("explanation", "")}</p></div>' for q in case_study["clinical_questions"]])}
    </div>

    <div class="section">
        <h2>Discussion Points</h2>
        <ul>
            {"".join([f"<li>{point}</li>" for point in case_study["discussion_points"]])}
        </ul>
    </div>
</body>
</html>
        """

        output_path.write_text(html_content, encoding="utf-8")
        logger.info(f"Interactive case study exported to {output_path}")


def create_educational_content_generator() -> EducationalContentGenerator:
    """Factory function to create educational content generator."""
    return EducationalContentGenerator()
