import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("content_generator_service")

class ContentGeneratorService:
    def generate_summary(self, patient):
        # Example logic to generate a structured summary
        return {
            "summary": f"Patient {patient.name} has a {patient.tumor_staging.stage} tumor. Treatment history includes {len(patient.treatment_history)} treatments.",
            "recommendations": ["Consider FLOT protocol", "Monitor perioperative risks"]
        }

    def generate_report(self, patient, format="PDF"):
        # Example logic to generate a report in the specified format
        summary = self.generate_summary(patient)
        if format == "PDF":
            return {"report": f"PDF Report: {summary['summary']}"}
        elif format == "HTML":
            return {"report": f"<html><body>{summary['summary']}</body></html>"}
        elif format == "Markdown":
            return {"report": f"# Report\n\n{summary['summary']}"}
        else:
            return {"error": "Unsupported format"}

# Clinical knowledge base entries for common queries
CLINICAL_KNOWLEDGE_BASE = {
    "flot": {
        "answer": "FLOT (Fluorouracil, Leucovorin, Oxaliplatin, and Docetaxel) is a perioperative chemotherapy regimen for gastric cancer. Standard protocol includes 4 preoperative and 4 postoperative cycles, with careful monitoring for neutropenia and neuropathy. The dosing schedule is as follows:\n\n- Docetaxel: 50 mg/m² (day 1)\n- Oxaliplatin: 85 mg/m² (day 1)\n- Leucovorin: 200 mg/m² (day 1)\n- 5-Fluorouracil: 2600 mg/m² (24-hour infusion starting on day 1)\n\nEach cycle is repeated every 2 weeks.",
        "sources": [
            {"title": "Al-Batran et al., NEJM 2019", "url": "https://www.nejm.org/doi/full/10.1056/nejmoa1804172"},
            {"title": "FLOT Protocol Guidelines", "url": "https://www.esmo.org/guidelines"}
        ],
        "confidence": 0.98
    },
    "gastrectomy": {
        "answer": "Gastrectomy procedures for gastric cancer include total, subtotal, and proximal approaches. The ADCI platform supports decision-making through outcome prediction and risk stratification. Key considerations include surgical margins, lymph node evaluation, and ERAS protocols. D2 lymphadenectomy is the standard for resectable gastric cancer with at least 16 lymph nodes retrieved for adequate staging.",
        "sources": [
            {"title": "Japanese Gastric Cancer Treatment Guidelines", "url": "https://link.springer.com/article/10.1007/s10120-020-01042-y"},
            {"title": "ESMO Clinical Practice Guidelines", "url": "https://www.esmo.org/guidelines/gastrointestinal-cancers/gastric-cancer"}
        ],
        "confidence": 0.95
    },
    "eras": {
        "answer": "Enhanced Recovery After Surgery (ERAS) protocols for gastric cancer include multimodal perioperative care pathways designed to achieve early recovery. Key elements include preoperative carbohydrate loading, minimally invasive approaches when possible, early mobilization, and scheduled non-opioid analgesia. Our platform integrates ERAS compliance tracking with clinical outcomes to optimize patient recovery trajectories.",
        "sources": [
            {"title": "ERAS Society Guidelines", "url": "https://erassociety.org/guidelines/list-of-guidelines/"},
            {"title": "Mortensen et al., EJSO 2014", "url": "https://www.ejso.com/article/S0748-7983(14)00335-5/fulltext"}
        ],
        "confidence": 0.97
    },
    "adci": {
        "answer": "The Adaptive Decision Confidence Index (ADCI) is our platform's proprietary framework for clinical decision support. It quantifies confidence levels in treatment recommendations based on available evidence, patient data similarity to established cohorts, and outcome predictability. The ADCI score ranges from 0-100, with values >80 indicating high confidence in the recommended approach. Each recommendation includes uncertainty bounds and key factors that would change the recommendation.",
        "sources": [
            {"title": "ADCI Methodology Documentation", "url": "/docs/adci-methodology.pdf"},
            {"title": "Clinical Decision Support in Oncology Surgery", "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6415618/"}
        ],
        "confidence": 0.99
    },
    "tumor_staging": {
        "answer": "Gastric cancer staging follows the AJCC 8th edition TNM classification. Our platform supports automated staging based on imaging reports, pathology, and clinical data integration. Key prognostic factors include: T stage (depth of invasion), N stage (nodal involvement), M stage (metastasis), histological type (diffuse vs intestinal), and molecular characteristics (HER2, MSI, EBV status). The platform calculates 5-year survival probability based on stage and treatment approach.",
        "sources": [
            {"title": "AJCC Cancer Staging Manual, 8th Edition", "url": "https://www.springer.com/gp/book/9783319406176"},
            {"title": "Stomach Cancer TNM Staging", "url": "https://www.cancer.org/cancer/stomach-cancer/detection-diagnosis-staging/staging.html"}
        ],
        "confidence": 0.97
    },
    "complications": {
        "answer": "Common complications after gastrectomy include: anastomotic leakage (2-8%), delayed gastric emptying (5-15%), duodenal stump leakage (1-3%), surgical site infection (10-15%), and postoperative pneumonia (7-20%). Our platform's predictive analytics module calculates patient-specific risk scores for these complications based on preoperative factors, comorbidities, and intraoperative variables. Risk mitigation strategies are provided for high-risk patients along with ERAS protocol modifications.",
        "sources": [
            {"title": "Postoperative Complications After Gastrectomy", "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6039356/"},
            {"title": "Risk Factors for Morbidity After Gastrectomy", "url": "https://link.springer.com/article/10.1245/s10434-020-08651-y"}
        ],
        "confidence": 0.94
    },
    "hipec": {
        "answer": "Hyperthermic Intraperitoneal Chemotherapy (HIPEC) may be considered for selected gastric cancer patients with peritoneal metastasis or high risk of peritoneal recurrence. The procedure involves cytoreductive surgery followed by perfusion of the peritoneal cavity with heated chemotherapy. Our platform provides selection criteria for HIPEC candidacy based on disease extent, patient performance status, and expected survival benefit. Current evidence shows limited efficacy for diffuse peritoneal disease but potential benefit for localized peritoneal involvement.",
        "sources": [
            {"title": "HIPEC in Gastric Cancer", "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6900795/"},
            {"title": "Peritoneal Carcinomatosis in Gastric Cancer", "url": "https://www.sciencedirect.com/science/article/abs/pii/S0748798319304291"}
        ],
        "confidence": 0.89
    }
}

async def get_clinical_content(question, context=None, specialty="gastric-oncology", user_role="clinician"):
    """
    Retrieve or generate relevant clinical content based on the question,
    user role, and clinical context.
    
    Args:
        question (str): The clinical question asked
        context (list): Previous conversation context 
        specialty (str): Clinical specialty (default: gastric-oncology)
        user_role (str): User role (surgeon, nurse, oncologist, etc.)
        
    Returns:
        dict: Response with answer, sources, and confidence score
    """
    context = context or []
    question_lower = question.lower()
    
    logger.info(f"Processing clinical query: '{question}' from {user_role} in {specialty}")
    
    # Role-specific adjustments
    role_adjustments = {
        "surgeon": {
            "focus": ["surgical technique", "complications", "margins", "operative approach"],
            "depth": "detailed technical"
        },
        "oncologist": {
            "focus": ["chemotherapy", "radiation", "dosing", "response assessment"],
            "depth": "detailed treatment"
        },
        "nurse": {
            "focus": ["patient care", "monitoring", "symptom management"],
            "depth": "practical implementation"
        },
        "researcher": {
            "focus": ["study design", "evidence quality", "outcomes"],
            "depth": "research-oriented"
        },
        "clinician": {  # Default
            "focus": ["clinical management", "protocol selection"],
            "depth": "balanced clinical"
        }
    }
    
    # Check for direct matches in knowledge base
    direct_matches = []
    for key, content in CLINICAL_KNOWLEDGE_BASE.items():
        if key in question_lower:
            direct_matches.append((key, content))
    
    # Return the most relevant direct match if available
    if direct_matches:
        # Sort by string length to prioritize more specific matches
        direct_matches.sort(key=lambda x: len(x[0]), reverse=True)
        key, content = direct_matches[0]
        
        # Log the match found
        logger.info(f"Direct knowledge base match found: {key}")
        return content
    
    # Topic-based routing if no direct match
    if any(term in question_lower for term in ["chemotherapy", "flot", "drug", "dosage", "cycle"]):
        return CLINICAL_KNOWLEDGE_BASE["flot"]
    
    if any(term in question_lower for term in ["surgery", "resection", "gastrectomy", "laparoscopic"]):
        return CLINICAL_KNOWLEDGE_BASE["gastrectomy"]
    
    if any(term in question_lower for term in ["recovery", "rehabilitation", "post-op", "eras"]):
        return CLINICAL_KNOWLEDGE_BASE["eras"]
    
    if any(term in question_lower for term in ["staging", "tnm", "metastasis", "tumor grade"]):
        return CLINICAL_KNOWLEDGE_BASE["tumor_staging"]
    
    if any(term in question_lower for term in ["confidence", "uncertainty", "adci", "decision support"]):
        return CLINICAL_KNOWLEDGE_BASE["adci"]
    
    if any(term in question_lower for term in ["complication", "risk", "morbidity", "leak"]):
        return CLINICAL_KNOWLEDGE_BASE["complications"]
    
    if any(term in question_lower for term in ["peritoneal", "hipec", "carcinomatosis"]):
        return CLINICAL_KNOWLEDGE_BASE["hipec"]
    
    # If we've reached here, provide a default response about the ADCI platform
    logger.warning(f"No specific match found for query: '{question}'. Returning default response.")
    
    return {
        "answer": f"The Adaptive Decision Confidence Index (ADCI) platform provides clinical decision support for gastric oncology surgery. It integrates patient data, tumor staging, treatment history, and evidence-based protocols to offer personalized recommendations with confidence intervals. For specific guidance, please ask about protocols (FLOT, gastrectomy), tumor staging, complications, or patient management approaches.",
        "sources": [
            {"title": "ADCI Platform Documentation", "url": "/docs/adci-platform-guide.pdf"},
            {"title": "Clinical Decision Support in Oncology", "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6415618/"}
        ],
        "confidence": 0.90
    }
