"""
Branding Operations Manager
Handles brand consistency, messaging, and visual identity across the platform
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re

from core.services.base import BaseService
from core.services.logger import get_logger

logger = get_logger(__name__)

class BrandColor(Enum):
    """Brand color palette"""
    PRIMARY = "#2563eb"      # Blue
    SECONDARY = "#dc2626"    # Red
    SUCCESS = "#16a34a"      # Green
    WARNING = "#ca8a04"      # Amber
    INFO = "#0891b2"         # Cyan
    NEUTRAL = "#6b7280"      # Gray
    ACCENT = "#f59e0b"       # Orange

class MessageTone(Enum):
    """Brand message tone"""
    PROFESSIONAL = "professional"
    CLINICAL = "clinical"
    SUPPORTIVE = "supportive"
    URGENT = "urgent"
    INFORMATIVE = "informative"

class ContentType(Enum):
    """Types of branded content"""
    UI_TEXT = "ui_text"
    EMAIL = "email"
    REPORT = "report"
    ALERT = "alert"
    NOTIFICATION = "notification"
    DOCUMENTATION = "documentation"

@dataclass
class BrandGuideline:
    """Brand guideline specification"""
    element: str
    specification: str
    mandatory: bool
    examples: List[str]
    violations: List[str]

@dataclass
class BrandCompliance:
    """Brand compliance assessment"""
    content_type: ContentType
    compliant: bool
    score: float
    violations: List[str]
    recommendations: List[str]
    assessed_at: datetime

class BrandingOperator(BaseService):
    """Operations for maintaining brand consistency"""
    
    def __init__(self):
        super().__init__()
        self.brand_guidelines = self._initialize_brand_guidelines()
        self.approved_terminology = self._initialize_terminology()
    
    def _initialize_brand_guidelines(self) -> Dict[str, BrandGuideline]:
        """Initialize brand guidelines"""
        return {
            "product_name": BrandGuideline(
                element="Product Name",
                specification="Always use 'Gastric ADCI Platform' or 'Decision Precision in Surgery'",
                mandatory=True,
                examples=["Gastric ADCI Platform", "Decision Precision in Surgery"],
                violations=["ADCI", "gastric platform", "decision platform"]
            ),
            "clinical_language": BrandGuideline(
                element="Clinical Language",
                specification="Use evidence-based, professional medical terminology",
                mandatory=True,
                examples=["evidence-based recommendation", "clinical decision support"],
                violations=["guaranteed cure", "100% success rate", "miracle treatment"]
            ),
            "color_usage": BrandGuideline(
                element="Color Usage",
                specification="Use primary blue (#2563eb) for actions, red (#dc2626) for alerts",
                mandatory=False,
                examples=["Primary buttons in blue", "Error messages in red"],
                violations=["Random color usage", "Inconsistent color schemes"]
            ),
            "disclaimer": BrandGuideline(
                element="Medical Disclaimer",
                specification="Include disclaimer for clinical recommendations",
                mandatory=True,
                examples=["This recommendation is for clinical decision support only"],
                violations=["Missing disclaimers", "Weak disclaimer language"]
            )
        }
    
    def _initialize_terminology(self) -> Dict[str, Dict[str, Any]]:
        """Initialize approved terminology"""
        return {
            "medical_terms": {
                "gastric_cancer": {
                    "preferred": "gastric adenocarcinoma",
                    "acceptable": ["gastric cancer", "stomach cancer"],
                    "avoid": ["stomach tumor", "gastric mass"]
                },
                "surgical_procedure": {
                    "preferred": "surgical resection",
                    "acceptable": ["gastrectomy", "surgical intervention"],
                    "avoid": ["operation", "surgery"]
                }
            },
            "clinical_outcomes": {
                "survival": {
                    "preferred": "overall survival",
                    "acceptable": ["survival rate", "mortality rate"],
                    "avoid": ["death rate", "life expectancy"]
                },
                "effectiveness": {
                    "preferred": "clinical efficacy",
                    "acceptable": ["treatment effectiveness", "therapeutic response"],
                    "avoid": ["success rate", "cure rate"]
                }
            },
            "decision_support": {
                "recommendation": {
                    "preferred": "clinical decision support recommendation",
                    "acceptable": ["evidence-based recommendation", "clinical guidance"],
                    "avoid": ["prescription", "medical advice", "diagnosis"]
                }
            }
        }
    
    async def validate_brand_compliance(
        self, 
        content: str, 
        content_type: ContentType,
        context: Optional[str] = None
    ) -> BrandCompliance:
        """Validate content against brand guidelines"""
        
        try:
            violations = []
            recommendations = []
            compliance_scores = []
            
            # Check mandatory guidelines
            for guideline_key, guideline in self.brand_guidelines.items():
                if guideline.mandatory:
                    violation_found = False
                    
                    # Check for violations
                    for violation in guideline.violations:
                        if violation.lower() in content.lower():
                            violations.append(f"Violation in {guideline.element}: '{violation}' found")
                            violation_found = True
                    
                    # Check for required elements
                    if guideline_key == "disclaimer" and content_type in [ContentType.REPORT, ContentType.ALERT]:
                        if not any(example.lower() in content.lower() for example in guideline.examples):
                            violations.append(f"Missing required {guideline.element}")
                            violation_found = True
                    
                    compliance_scores.append(0.0 if violation_found else 1.0)
            
            # Check terminology compliance
            terminology_score = await self._check_terminology_compliance(content, violations)
            compliance_scores.append(terminology_score)
            
            # Check tone and style
            tone_score = await self._check_tone_compliance(content, content_type, violations)
            compliance_scores.append(tone_score)
            
            # Calculate overall score
            overall_score = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
            
            # Generate recommendations
            if violations:
                recommendations = await self._generate_brand_recommendations(violations, content_type)
            
            compliance = BrandCompliance(
                content_type=content_type,
                compliant=overall_score >= 0.8,
                score=overall_score,
                violations=violations,
                recommendations=recommendations,
                assessed_at=datetime.now()
            )
            
            await self._log_brand_compliance(compliance)
            
            return compliance
            
        except Exception as e:
            self.logger.error(f"Error validating brand compliance: {e}")
            raise
    
    async def _check_terminology_compliance(self, content: str, violations: List[str]) -> float:
        """Check terminology compliance"""
        
        violation_count = 0
        total_checks = 0
        
        for category, terms in self.approved_terminology.items():
            for term, guidelines in terms.items():
                total_checks += 1
                
                # Check for terms to avoid
                for avoid_term in guidelines["avoid"]:
                    if avoid_term.lower() in content.lower():
                        violations.append(f"Avoid using '{avoid_term}', prefer '{guidelines['preferred']}'")
                        violation_count += 1
                        break
        
        return 1.0 - (violation_count / total_checks) if total_checks > 0 else 1.0
    
    async def _check_tone_compliance(
        self, 
        content: str, 
        content_type: ContentType, 
        violations: List[str]
    ) -> float:
        """Check tone and style compliance"""
        
        tone_violations = 0
        
        # Check for unprofessional language
        unprofessional_patterns = [
            r'\b(guarantee|guaranteed)\b',
            r'\b(miracle|miraculous)\b',
            r'\b(100%|perfect)\b',
            r'\b(never fails?)\b',
            r'\b(always works?)\b'
        ]
        
        for pattern in unprofessional_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Unprofessional language detected: avoid absolute claims")
                tone_violations += 1
        
        # Check for appropriate clinical language
        if content_type in [ContentType.REPORT, ContentType.ALERT]:
            clinical_indicators = [
                'evidence-based', 'clinical', 'recommendation', 'assessment',
                'evaluation', 'analysis', 'findings'
            ]
            
            if not any(indicator in content.lower() for indicator in clinical_indicators):
                violations.append("Consider using more clinical language for professional content")
                tone_violations += 1
        
        # Scoring (fewer violations = higher score)
        max_possible_violations = len(unprofessional_patterns) + 1  # +1 for clinical language check
        return 1.0 - (tone_violations / max_possible_violations)
    
    async def _generate_brand_recommendations(
        self, 
        violations: List[str], 
        content_type: ContentType
    ) -> List[str]:
        """Generate brand compliance recommendations"""
        
        recommendations = []
        
        # General recommendations based on violations
        if any("disclaimer" in v.lower() for v in violations):
            if content_type == ContentType.REPORT:
                recommendations.append("Add medical disclaimer: 'This recommendation is for clinical decision support only and should not replace professional medical judgment.'")
            elif content_type == ContentType.ALERT:
                recommendations.append("Include disclaimer about the advisory nature of the alert")
        
        if any("terminology" in v.lower() or "avoid using" in v.lower() for v in violations):
            recommendations.append("Review medical terminology guidelines and use preferred clinical terms")
        
        if any("unprofessional" in v.lower() for v in violations):
            recommendations.append("Revise language to maintain professional clinical tone")
            recommendations.append("Avoid absolute claims and use evidence-based language")
        
        if any("color" in v.lower() for v in violations):
            recommendations.append("Follow brand color guidelines: primary blue for actions, red for alerts")
        
        # Content-type specific recommendations
        if content_type == ContentType.UI_TEXT:
            recommendations.append("Ensure UI text is concise and action-oriented")
        elif content_type == ContentType.EMAIL:
            recommendations.append("Include proper branding header and footer in emails")
        elif content_type == ContentType.DOCUMENTATION:
            recommendations.append("Maintain consistent formatting and professional tone throughout documentation")
        
        return recommendations
    
    async def generate_branded_content(
        self, 
        template_type: str,
        variables: Dict[str, Any],
        tone: MessageTone = MessageTone.PROFESSIONAL
    ) -> str:
        """Generate content following brand guidelines"""
        
        templates = {
            "clinical_recommendation": {
                MessageTone.CLINICAL: """
Based on the clinical analysis of {patient_data}, the Gastric ADCI Platform recommends:

{recommendation}

**Evidence Level**: {evidence_level}
**Confidence Score**: {confidence_score}

*This recommendation is for clinical decision support only and should not replace professional medical judgment.*
""",
                MessageTone.PROFESSIONAL: """
## Clinical Decision Support Recommendation

The evidence-based analysis indicates:

{recommendation}

- **Assessment Confidence**: {confidence_score}
- **Supporting Evidence**: {evidence_level}

Please review this recommendation in the context of the complete clinical picture.

*Generated by the Gastric ADCI Platform for clinical decision support.*
"""
            },
            "alert_notification": {
                MessageTone.URGENT: """
🚨 **CLINICAL ALERT**

{alert_message}

**Action Required**: {required_action}
**Priority**: {priority_level}

Please review immediately.

*Decision Precision in Surgery Platform*
""",
                MessageTone.INFORMATIVE: """
ℹ️ **Clinical Notification**

{alert_message}

Recommended next steps: {required_action}

*This is an automated notification from the Gastric ADCI Platform.*
"""
            }
        }
        
        try:
            template = templates.get(template_type, {}).get(tone)
            if not template:
                raise ValueError(f"No template found for {template_type} with tone {tone}")
            
            # Replace variables in template
            content = template.format(**variables)
            
            # Validate generated content
            compliance = await self.validate_brand_compliance(
                content, 
                ContentType.NOTIFICATION
            )
            
            if not compliance.compliant:
                self.logger.warning(f"Generated content has brand compliance issues: {compliance.violations}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error generating branded content: {e}")
            raise
    
    async def get_brand_assets(self) -> Dict[str, Any]:
        """Get brand assets and guidelines"""
        
        return {
            "colors": {color.name.lower(): color.value for color in BrandColor},
            "typography": {
                "primary_font": "Inter, system-ui, sans-serif",
                "monospace_font": "JetBrains Mono, Consolas, monospace",
                "heading_weights": ["600", "700"],
                "body_weight": "400"
            },
            "logos": {
                "primary": "/static/images/logo-primary.svg",
                "secondary": "/static/images/logo-secondary.svg",
                "icon": "/static/images/logo-icon.svg"
            },
            "guidelines": {
                guideline.element: {
                    "specification": guideline.specification,
                    "mandatory": guideline.mandatory,
                    "examples": guideline.examples
                }
                for guideline in self.brand_guidelines.values()
            },
            "terminology": self.approved_terminology
        }
    
    async def _log_brand_compliance(self, compliance: BrandCompliance):
        """Log brand compliance assessment"""
        await self.audit_log(
            action="brand_compliance_check",
            entity_type="content_validation",
            metadata={
                "content_type": compliance.content_type.value,
                "compliance_score": compliance.score,
                "violations_count": len(compliance.violations)
            }
        )
