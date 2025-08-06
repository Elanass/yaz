"""
Database Bridge - Connects research engine to existing SQLAlchemy setup
Ensures seamless integration with existing database architecture
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from surgify.core.database import Base, engine, get_db
from surgify.core.models.database_models import Case, Patient, User

from ....modules.universal_research.adapters.surgify_adapter import \
    SurgifyAdapter


class DatabaseBridge:
    """
    Bridges research engine with existing Surgify database architecture
    Preserves all existing database operations while adding research capabilities
    """

    def __init__(self, db_session: Session = None):
        self.db_session = db_session or next(get_db())
        self.surgify_adapter = SurgifyAdapter(self.db_session)

    def create_research_views(self):
        """
        Create database views for research analysis
        Non-destructive - creates views that join existing tables
        """
        research_views = [
            self._create_research_case_view(),
            self._create_cohort_summary_view(),
            self._create_outcome_analysis_view(),
            self._create_research_metrics_view(),
        ]

        for view_sql in research_views:
            try:
                self.db_session.execute(text(view_sql))
                self.db_session.commit()
            except Exception as e:
                print(f"Warning: Could not create research view: {e}")
                self.db_session.rollback()

    def get_research_ready_data(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get research-ready data using existing database queries
        Leverages existing models and relationships
        """
        # Build query using existing SQLAlchemy models
        query = self.db_session.query(Case).join(Patient).join(User)

        # Apply filters based on criteria (preserves existing filtering logic)
        if criteria.get("procedure_type"):
            query = query.filter(Case.procedure_type == criteria["procedure_type"])

        if criteria.get("status"):
            query = query.filter(Case.status == criteria["status"])

        if criteria.get("date_range"):
            start_date, end_date = criteria["date_range"]
            query = query.filter(Case.created_at.between(start_date, end_date))

        if criteria.get("surgeon_id"):
            query = query.filter(Case.surgeon_id == criteria["surgeon_id"])

        # Execute query and convert to research format
        cases = query.all()
        return [self.surgify_adapter.map_case_to_research_data(case) for case in cases]

    def get_aggregated_research_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated research metrics using existing database
        Uses existing SQLAlchemy session and models
        """
        metrics = {}

        try:
            # Total cases
            metrics["total_cases"] = self.db_session.query(Case).count()

            # Cases by status
            status_counts = (
                self.db_session.query(Case.status, func.count(Case.id))
                .group_by(Case.status)
                .all()
            )

            metrics["status_distribution"] = {
                status: count for status, count in status_counts
            }

            # Cases by procedure type
            procedure_counts = (
                self.db_session.query(Case.procedure_type, func.count(Case.id))
                .group_by(Case.procedure_type)
                .all()
            )

            metrics["procedure_distribution"] = {
                proc: count for proc, count in procedure_counts if proc
            }

            # Completed cases (research eligible)
            completed_cases = (
                self.db_session.query(Case).filter(Case.status == "completed").count()
            )
            metrics["research_eligible_cases"] = completed_cases
            metrics["research_eligibility_rate"] = (
                (completed_cases / metrics["total_cases"] * 100)
                if metrics["total_cases"] > 0
                else 0
            )

            # Risk score statistics
            risk_scores = (
                self.db_session.query(Case.risk_score)
                .filter(Case.risk_score.isnot(None))
                .all()
            )
            if risk_scores:
                risk_values = [score[0] for score in risk_scores]
                metrics["risk_score_stats"] = {
                    "count": len(risk_values),
                    "average": sum(risk_values) / len(risk_values),
                    "min": min(risk_values),
                    "max": max(risk_values),
                }

            # Patient demographics
            patient_stats = self._get_patient_demographics_stats()
            metrics["patient_demographics"] = patient_stats

        except Exception as e:
            metrics["error"] = f"Failed to calculate metrics: {str(e)}"

        return metrics

    def create_research_indexes(self):
        """
        Create database indexes to optimize research queries
        Non-destructive - only adds indexes, doesn't modify existing structure
        """
        research_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_cases_procedure_status ON cases(procedure_type, status);",
            "CREATE INDEX IF NOT EXISTS idx_cases_created_date ON cases(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_cases_risk_score ON cases(risk_score) WHERE risk_score IS NOT NULL;",
            "CREATE INDEX IF NOT EXISTS idx_patients_age_gender ON patients(age, gender) WHERE age IS NOT NULL;",
            "CREATE INDEX IF NOT EXISTS idx_patients_bmi ON patients(bmi) WHERE bmi IS NOT NULL;",
        ]

        for index_sql in research_indexes:
            try:
                self.db_session.execute(text(index_sql))
                self.db_session.commit()
            except Exception as e:
                print(f"Warning: Could not create research index: {e}")
                self.db_session.rollback()

    def validate_data_integrity(self) -> Dict[str, Any]:
        """
        Validate data integrity for research purposes
        Ensures existing data quality while identifying research readiness
        """
        validation_results = {
            "total_cases": 0,
            "data_quality_issues": [],
            "research_readiness_score": 0,
            "recommendations": [],
        }

        try:
            # Count total cases
            total_cases = self.db_session.query(Case).count()
            validation_results["total_cases"] = total_cases

            if total_cases == 0:
                validation_results["data_quality_issues"].append(
                    "No cases found in database"
                )
                return validation_results

            # Check for missing patient data
            cases_without_patients = (
                self.db_session.query(Case).filter(Case.patient_id.is_(None)).count()
            )
            if cases_without_patients > 0:
                validation_results["data_quality_issues"].append(
                    f"{cases_without_patients} cases missing patient data"
                )

            # Check for missing procedure types
            cases_without_procedure = (
                self.db_session.query(Case)
                .filter(Case.procedure_type.is_(None))
                .count()
            )
            if cases_without_procedure > 0:
                validation_results["data_quality_issues"].append(
                    f"{cases_without_procedure} cases missing procedure type"
                )

            # Check for missing outcome data (completed cases without risk scores)
            completed_without_risk = (
                self.db_session.query(Case)
                .filter(Case.status == "completed", Case.risk_score.is_(None))
                .count()
            )
            if completed_without_risk > 0:
                validation_results["data_quality_issues"].append(
                    f"{completed_without_risk} completed cases missing risk assessment"
                )

            # Check patient demographic completeness
            patients_without_age = (
                self.db_session.query(Patient).filter(Patient.age.is_(None)).count()
            )
            total_patients = self.db_session.query(Patient).count()
            if patients_without_age > total_patients * 0.1:  # More than 10% missing age
                validation_results["data_quality_issues"].append(
                    f"High percentage of patients missing age data ({patients_without_age}/{total_patients})"
                )

            # Calculate research readiness score
            validation_results[
                "research_readiness_score"
            ] = self._calculate_research_readiness_score(
                total_cases,
                cases_without_patients,
                cases_without_procedure,
                completed_without_risk,
                patients_without_age,
                total_patients,
            )

            # Generate recommendations
            validation_results[
                "recommendations"
            ] = self._generate_data_quality_recommendations(validation_results)

        except Exception as e:
            validation_results["data_quality_issues"].append(
                f"Data validation error: {str(e)}"
            )

        return validation_results

    def _create_research_case_view(self) -> str:
        """Create view for research case analysis"""
        return """
        CREATE OR REPLACE VIEW research_case_view AS
        SELECT 
            c.id as case_id,
            c.case_number,
            c.procedure_type,
            c.diagnosis,
            c.status,
            c.risk_score,
            c.scheduled_date,
            c.actual_start,
            c.actual_end,
            c.created_at,
            p.patient_id,
            p.age,
            p.gender,
            p.bmi,
            p.medical_history,
            u.username as surgeon_username,
            u.role as surgeon_role,
            CASE 
                WHEN c.actual_end IS NOT NULL AND c.actual_start IS NOT NULL 
                THEN EXTRACT(EPOCH FROM (c.actual_end - c.actual_start))/3600.0 
                ELSE NULL 
            END as duration_hours,
            CASE 
                WHEN c.risk_score < 0.3 THEN 'low'
                WHEN c.risk_score < 0.7 THEN 'moderate'
                ELSE 'high'
            END as risk_category
        FROM cases c
        LEFT JOIN patients p ON c.patient_id = p.id
        LEFT JOIN users u ON c.surgeon_id = u.id;
        """

    def _create_cohort_summary_view(self) -> str:
        """Create view for cohort summary statistics"""
        return """
        CREATE OR REPLACE VIEW cohort_summary_view AS
        SELECT 
            procedure_type,
            COUNT(*) as total_cases,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_cases,
            AVG(risk_score) as avg_risk_score,
            AVG(CASE 
                WHEN actual_end IS NOT NULL AND actual_start IS NOT NULL 
                THEN EXTRACT(EPOCH FROM (actual_end - actual_start))/3600.0 
                ELSE NULL 
            END) as avg_duration_hours,
            COUNT(DISTINCT surgeon_id) as unique_surgeons,
            COUNT(DISTINCT patient_id) as unique_patients
        FROM research_case_view
        WHERE procedure_type IS NOT NULL
        GROUP BY procedure_type;
        """

    def _create_outcome_analysis_view(self) -> str:
        """Create view for outcome analysis"""
        return """
        CREATE OR REPLACE VIEW outcome_analysis_view AS
        SELECT 
            procedure_type,
            risk_category,
            COUNT(*) as case_count,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_count,
            AVG(risk_score) as avg_risk_score,
            MIN(risk_score) as min_risk_score,
            MAX(risk_score) as max_risk_score
        FROM research_case_view
        WHERE procedure_type IS NOT NULL
        GROUP BY procedure_type, risk_category;
        """

    def _create_research_metrics_view(self) -> str:
        """Create view for research metrics"""
        return """
        CREATE OR REPLACE VIEW research_metrics_view AS
        SELECT 
            'overall' as metric_category,
            COUNT(*) as total_cases,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as research_eligible,
            COUNT(DISTINCT procedure_type) as unique_procedures,
            COUNT(DISTINCT surgeon_username) as unique_surgeons,
            AVG(CASE WHEN age IS NOT NULL THEN age END) as avg_patient_age,
            COUNT(CASE WHEN age IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as age_completeness_pct,
            COUNT(CASE WHEN risk_score IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as risk_completeness_pct
        FROM research_case_view;
        """

    def _get_patient_demographics_stats(self) -> Dict[str, Any]:
        """Get patient demographics statistics"""
        try:
            # Age statistics
            age_stats = (
                self.db_session.query(
                    func.count(Patient.age).label("count"),
                    func.avg(Patient.age).label("mean"),
                    func.min(Patient.age).label("min"),
                    func.max(Patient.age).label("max"),
                )
                .filter(Patient.age.isnot(None))
                .first()
            )

            # Gender distribution
            gender_dist = (
                self.db_session.query(Patient.gender, func.count(Patient.id))
                .filter(Patient.gender.isnot(None))
                .group_by(Patient.gender)
                .all()
            )

            # BMI statistics
            bmi_stats = (
                self.db_session.query(
                    func.count(Patient.bmi).label("count"),
                    func.avg(Patient.bmi).label("mean"),
                    func.min(Patient.bmi).label("min"),
                    func.max(Patient.bmi).label("max"),
                )
                .filter(Patient.bmi.isnot(None))
                .first()
            )

            return {
                "age_statistics": {
                    "count": age_stats.count if age_stats else 0,
                    "mean": float(age_stats.mean)
                    if age_stats and age_stats.mean
                    else None,
                    "min": age_stats.min if age_stats else None,
                    "max": age_stats.max if age_stats else None,
                },
                "gender_distribution": {gender: count for gender, count in gender_dist},
                "bmi_statistics": {
                    "count": bmi_stats.count if bmi_stats else 0,
                    "mean": float(bmi_stats.mean)
                    if bmi_stats and bmi_stats.mean
                    else None,
                    "min": float(bmi_stats.min)
                    if bmi_stats and bmi_stats.min
                    else None,
                    "max": float(bmi_stats.max)
                    if bmi_stats and bmi_stats.max
                    else None,
                },
            }

        except Exception as e:
            return {"error": f"Failed to get demographics: {str(e)}"}

    def _calculate_research_readiness_score(
        self,
        total_cases: int,
        missing_patients: int,
        missing_procedures: int,
        missing_risk: int,
        missing_age: int,
        total_patients: int,
    ) -> float:
        """Calculate research readiness score (0-100)"""
        if total_cases == 0:
            return 0

        # Calculate completeness percentages
        patient_completeness = (total_cases - missing_patients) / total_cases
        procedure_completeness = (total_cases - missing_procedures) / total_cases
        risk_completeness = (total_cases - missing_risk) / total_cases
        age_completeness = (
            (total_patients - missing_age) / total_patients if total_patients > 0 else 0
        )

        # Weight the different factors
        weights = {
            "patient_data": 0.25,
            "procedure_data": 0.25,
            "outcome_data": 0.30,
            "demographic_data": 0.20,
        }

        score = (
            patient_completeness * weights["patient_data"]
            + procedure_completeness * weights["procedure_data"]
            + risk_completeness * weights["outcome_data"]
            + age_completeness * weights["demographic_data"]
        ) * 100

        return round(score, 2)

    def _generate_data_quality_recommendations(
        self, validation_results: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for improving data quality"""
        recommendations = []

        score = validation_results["research_readiness_score"]

        if score < 50:
            recommendations.append(
                "Critical data quality issues require immediate attention before research use"
            )
        elif score < 75:
            recommendations.append(
                "Data quality is acceptable but improvements would enhance research value"
            )
        else:
            recommendations.append("Data quality is good for research purposes")

        if "cases missing patient data" in str(
            validation_results["data_quality_issues"]
        ):
            recommendations.append(
                "Link all cases to patient records for comprehensive analysis"
            )

        if "cases missing procedure type" in str(
            validation_results["data_quality_issues"]
        ):
            recommendations.append("Ensure all cases have documented procedure types")

        if "completed cases missing risk assessment" in str(
            validation_results["data_quality_issues"]
        ):
            recommendations.append("Complete risk assessments for all finished cases")

        if "patients missing age data" in str(
            validation_results["data_quality_issues"]
        ):
            recommendations.append("Improve patient demographic data collection")

        return recommendations
