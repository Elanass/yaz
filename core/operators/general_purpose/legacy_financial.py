"""
Financial Operations Manager
Handles financial calculations, billing, insurance claims, and cost analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from core.services.base import BaseService
from core.services.logger import get_logger

logger = get_logger(__name__)

class CurrencyCode(Enum):
    """Supported currency codes"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"

class BillingStatus(Enum):
    """Billing status for procedures"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DENIED = "denied"
    PARTIAL = "partial"

@dataclass
class CostBreakdown:
    """Cost breakdown for surgical procedures"""
    procedure_cost: Decimal
    anesthesia_cost: Decimal
    facility_cost: Decimal
    surgeon_fee: Decimal
    equipment_cost: Decimal
    medication_cost: Decimal
    lab_cost: Decimal
    total_cost: Decimal
    currency: CurrencyCode = CurrencyCode.USD

@dataclass
class InsuranceClaim:
    """Insurance claim information"""
    claim_id: str
    patient_id: str
    procedure_codes: List[str]
    diagnosis_codes: List[str]
    total_amount: Decimal
    covered_amount: Decimal
    patient_responsibility: Decimal
    status: BillingStatus
    submitted_date: datetime
    processed_date: Optional[datetime] = None

class FinancialOperator(BaseService):
    """Financial operations for healthcare procedures"""
    
    def __init__(self):
        super().__init__()
        self.currency_rates = {
            CurrencyCode.USD: Decimal("1.0"),
            CurrencyCode.EUR: Decimal("0.85"),
            CurrencyCode.GBP: Decimal("0.75"),
            CurrencyCode.CAD: Decimal("1.25")
        }
    
    async def calculate_procedure_cost(
        self, 
        procedure_type: str,
        facility_tier: str = "standard",
        surgeon_experience: str = "experienced",
        complexity_score: float = 1.0
    ) -> CostBreakdown:
        """Calculate total cost for a surgical procedure"""
        
        try:
            # Base costs by procedure type
            base_costs = {
                "gastric_resection": {
                    "procedure": Decimal("15000"),
                    "anesthesia": Decimal("2500"),
                    "facility": Decimal("8000"),
                    "surgeon": Decimal("5000"),
                    "equipment": Decimal("3000"),
                    "medication": Decimal("1500"),
                    "lab": Decimal("800")
                },
                "laparoscopic_gastrectomy": {
                    "procedure": Decimal("18000"),
                    "anesthesia": Decimal("3000"),
                    "facility": Decimal("10000"),
                    "surgeon": Decimal("6000"),
                    "equipment": Decimal("4000"),
                    "medication": Decimal("2000"),
                    "lab": Decimal("1000")
                },
                "endoscopic_resection": {
                    "procedure": Decimal("8000"),
                    "anesthesia": Decimal("1500"),
                    "facility": Decimal("4000"),
                    "surgeon": Decimal("3000"),
                    "equipment": Decimal("2000"),
                    "medication": Decimal("800"),
                    "lab": Decimal("500")
                }
            }
            
            if procedure_type not in base_costs:
                raise ValueError(f"Unknown procedure type: {procedure_type}")
            
            costs = base_costs[procedure_type].copy()
            
            # Apply facility tier multiplier
            facility_multipliers = {
                "basic": Decimal("0.8"),
                "standard": Decimal("1.0"),
                "premium": Decimal("1.3"),
                "academic": Decimal("1.5")
            }
            facility_mult = facility_multipliers.get(facility_tier, Decimal("1.0"))
            
            # Apply surgeon experience multiplier
            surgeon_multipliers = {
                "resident": Decimal("0.7"),
                "junior": Decimal("0.9"),
                "experienced": Decimal("1.0"),
                "senior": Decimal("1.2"),
                "expert": Decimal("1.5")
            }
            surgeon_mult = surgeon_multipliers.get(surgeon_experience, Decimal("1.0"))
            
            # Apply complexity multiplier
            complexity_mult = Decimal(str(complexity_score))
            
            # Calculate adjusted costs
            breakdown = CostBreakdown(
                procedure_cost=costs["procedure"] * facility_mult * complexity_mult,
                anesthesia_cost=costs["anesthesia"] * complexity_mult,
                facility_cost=costs["facility"] * facility_mult,
                surgeon_fee=costs["surgeon"] * surgeon_mult * complexity_mult,
                equipment_cost=costs["equipment"] * complexity_mult,
                medication_cost=costs["medication"] * complexity_mult,
                lab_cost=costs["lab"],
                total_cost=Decimal("0")  # Will be calculated below
            )
            
            # Calculate total
            breakdown.total_cost = (
                breakdown.procedure_cost + breakdown.anesthesia_cost + 
                breakdown.facility_cost + breakdown.surgeon_fee + 
                breakdown.equipment_cost + breakdown.medication_cost + 
                breakdown.lab_cost
            )
            
            # Round to 2 decimal places
            breakdown.total_cost = breakdown.total_cost.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            
            await self._log_cost_calculation(procedure_type, breakdown)
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"Error calculating procedure cost: {e}")
            raise
    
    async def calculate_insurance_coverage(
        self, 
        cost_breakdown: CostBreakdown,
        insurance_plan: str,
        patient_age: int,
        is_emergency: bool = False
    ) -> InsuranceClaim:
        """Calculate insurance coverage for procedure"""
        
        try:
            # Coverage rates by insurance plan
            coverage_rates = {
                "medicare": {
                    "procedure": 0.80,
                    "anesthesia": 0.80,
                    "facility": 0.80,
                    "surgeon": 0.80,
                    "equipment": 0.80,
                    "medication": 0.80,
                    "lab": 0.80
                },
                "commercial": {
                    "procedure": 0.90,
                    "anesthesia": 0.85,
                    "facility": 0.90,
                    "surgeon": 0.85,
                    "equipment": 0.75,
                    "medication": 0.85,
                    "lab": 0.90
                },
                "medicaid": {
                    "procedure": 0.70,
                    "anesthesia": 0.70,
                    "facility": 0.70,
                    "surgeon": 0.70,
                    "equipment": 0.65,
                    "medication": 0.75,
                    "lab": 0.80
                },
                "self_pay": {
                    "procedure": 0.0,
                    "anesthesia": 0.0,
                    "facility": 0.0,
                    "surgeon": 0.0,
                    "equipment": 0.0,
                    "medication": 0.0,
                    "lab": 0.0
                }
            }
            
            rates = coverage_rates.get(insurance_plan, coverage_rates["commercial"])
            
            # Emergency procedures get higher coverage
            if is_emergency:
                rates = {k: min(v + 0.1, 1.0) for k, v in rates.items()}
            
            # Senior citizens (65+) get enhanced coverage
            if patient_age >= 65:
                rates = {k: min(v + 0.05, 1.0) for k, v in rates.items()}
            
            # Calculate covered amounts
            covered_procedure = cost_breakdown.procedure_cost * Decimal(str(rates["procedure"]))
            covered_anesthesia = cost_breakdown.anesthesia_cost * Decimal(str(rates["anesthesia"]))
            covered_facility = cost_breakdown.facility_cost * Decimal(str(rates["facility"]))
            covered_surgeon = cost_breakdown.surgeon_fee * Decimal(str(rates["surgeon"]))
            covered_equipment = cost_breakdown.equipment_cost * Decimal(str(rates["equipment"]))
            covered_medication = cost_breakdown.medication_cost * Decimal(str(rates["medication"]))
            covered_lab = cost_breakdown.lab_cost * Decimal(str(rates["lab"]))
            
            total_covered = (
                covered_procedure + covered_anesthesia + covered_facility +
                covered_surgeon + covered_equipment + covered_medication + covered_lab
            )
            
            patient_responsibility = cost_breakdown.total_cost - total_covered
            
            claim = InsuranceClaim(
                claim_id=f"CLM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                patient_id="",  # To be filled by caller
                procedure_codes=[],  # To be filled by caller
                diagnosis_codes=[],  # To be filled by caller
                total_amount=cost_breakdown.total_cost,
                covered_amount=total_covered.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                patient_responsibility=patient_responsibility.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                status=BillingStatus.PENDING,
                submitted_date=datetime.now()
            )
            
            return claim
            
        except Exception as e:
            self.logger.error(f"Error calculating insurance coverage: {e}")
            raise
    
    async def calculate_roi_analysis(
        self,
        investment_cost: Decimal,
        annual_savings: Decimal,
        analysis_years: int = 5,
        discount_rate: float = 0.05
    ) -> Dict[str, Any]:
        """Calculate ROI analysis for healthcare investments"""
        
        try:
            # Calculate NPV and ROI
            cash_flows = []
            cumulative_savings = Decimal("0")
            
            for year in range(1, analysis_years + 1):
                # Apply discount rate
                discounted_savings = annual_savings / (Decimal(str(1 + discount_rate)) ** year)
                cash_flows.append(float(discounted_savings))
                cumulative_savings += discounted_savings
            
            net_present_value = cumulative_savings - investment_cost
            roi_percentage = (net_present_value / investment_cost) * 100
            
            # Calculate payback period
            payback_years = float(investment_cost / annual_savings)
            
            analysis = {
                "investment_cost": float(investment_cost),
                "annual_savings": float(annual_savings),
                "analysis_years": analysis_years,
                "discount_rate": discount_rate,
                "net_present_value": float(net_present_value),
                "roi_percentage": float(roi_percentage),
                "payback_years": payback_years,
                "cash_flows": cash_flows,
                "break_even_year": min(analysis_years, int(payback_years) + 1),
                "recommendation": self._get_roi_recommendation(float(roi_percentage), payback_years)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI analysis: {e}")
            raise
    
    def _get_roi_recommendation(self, roi_percentage: float, payback_years: float) -> str:
        """Get investment recommendation based on ROI analysis"""
        if roi_percentage > 20 and payback_years < 3:
            return "Highly Recommended - Excellent ROI with quick payback"
        elif roi_percentage > 10 and payback_years < 5:
            return "Recommended - Good ROI within acceptable timeframe"
        elif roi_percentage > 0 and payback_years < 7:
            return "Consider - Positive ROI but longer payback period"
        else:
            return "Not Recommended - Poor ROI or excessive payback period"
    
    async def convert_currency(
        self, 
        amount: Decimal, 
        from_currency: CurrencyCode, 
        to_currency: CurrencyCode
    ) -> Decimal:
        """Convert between currencies"""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first, then to target currency
        usd_amount = amount / self.currency_rates[from_currency]
        target_amount = usd_amount * self.currency_rates[to_currency]
        
        return target_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    async def _log_cost_calculation(self, procedure_type: str, breakdown: CostBreakdown):
        """Log cost calculation for audit trail"""
        await self.audit_log(
            action="cost_calculation",
            entity_type="procedure_cost",
            metadata={
                "procedure_type": procedure_type,
                "total_cost": str(breakdown.total_cost),
                "currency": breakdown.currency.value
            }
        )
