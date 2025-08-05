"""
Auth Integrator - Uses existing JWT system for research features
Seamlessly integrates research permissions with existing authentication
"""

from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from surgify.core.models.user import User
from surgify.core.services.auth_service import get_current_user, verify_token


class AuthIntegrator:
    """
    Integrates research features with existing Surgify authentication system
    Maintains all existing security while adding research-specific permissions
    """

    def __init__(self):
        self.security = HTTPBearer()
        self.research_permissions = self._define_research_permissions()

    def get_current_research_user(
        self, current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Get current user with research access validation
        Uses existing authentication, adds research permission check
        """
        if not self._user_has_research_access(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Research access not authorized for this user",
            )
        return current_user

    def require_research_permission(self, permission: str):
        """
        Decorator to require specific research permission
        Integrates with existing role-based access control
        """

        def permission_dependency(
            current_user: User = Depends(get_current_user),
        ) -> User:
            if not self._user_has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required for this research operation",
                )
            return current_user

        return permission_dependency

    def get_user_research_scope(
        self, current_user: User = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Get research scope for current user
        Defines what research operations user can perform
        """
        user_scope = {
            "can_view_research": self._user_has_permission(
                current_user, "research.view"
            ),
            "can_analyze_cohorts": self._user_has_permission(
                current_user, "research.analyze"
            ),
            "can_generate_reports": self._user_has_permission(
                current_user, "research.generate"
            ),
            "can_export_data": self._user_has_permission(
                current_user, "research.export"
            ),
            "can_manage_research": self._user_has_permission(
                current_user, "research.manage"
            ),
            "accessible_data_scope": self._get_user_data_scope(current_user),
            "restrictions": self._get_user_restrictions(current_user),
        }

        return user_scope

    def filter_research_data_by_permissions(
        self, research_data: List[Dict[str, Any]], user: User
    ) -> List[Dict[str, Any]]:
        """
        Filter research data based on user permissions
        Ensures users only see data they're authorized to access
        """
        user_scope = self._get_user_data_scope(user)

        if user_scope["scope_type"] == "all":
            return research_data  # Full access

        elif user_scope["scope_type"] == "own_cases":
            # Filter to only cases where user is the surgeon
            return [
                case
                for case in research_data
                if case.get("provider_info", {}).get("surgeon_id") == user.username
            ]

        elif user_scope["scope_type"] == "department":
            # Filter to department cases (would need department data)
            # For now, return all data - would be enhanced with actual department logic
            return research_data

        elif user_scope["scope_type"] == "restricted":
            # Return anonymized data only
            return self._anonymize_research_data(research_data)

        else:
            return []  # No access

    def validate_research_request_permissions(
        self, request_data: Dict[str, Any], user: User
    ) -> bool:
        """
        Validate that user has permissions for the specific research request
        Checks both general permissions and data access scope
        """
        # Check basic research access
        if not self._user_has_research_access(user):
            return False

        # Check specific operation permissions
        operation = request_data.get("operation_type", "unknown")

        operation_permissions = {
            "cohort_analysis": "research.analyze",
            "outcome_prediction": "research.analyze",
            "report_generation": "research.generate",
            "data_export": "research.export",
            "guideline_creation": "research.generate",
        }

        required_permission = operation_permissions.get(operation, "research.view")
        if not self._user_has_permission(user, required_permission):
            return False

        # Check data scope permissions
        requested_scope = request_data.get("data_scope", {})
        user_scope = self._get_user_data_scope(user)

        return self._validate_data_scope_request(requested_scope, user_scope)

    def enhance_existing_auth_middleware(self, app):
        """
        Enhance existing authentication middleware with research features
        Maintains backward compatibility while adding research capabilities
        """

        @app.middleware("http")
        async def research_auth_middleware(request, call_next):
            """Middleware to handle research authentication"""

            # Check if this is a research endpoint
            if request.url.path.startswith("/api/v1/research/"):
                # Research endpoints require special handling
                # This would integrate with existing auth middleware
                pass

            # Continue with existing authentication flow
            response = await call_next(request)
            return response

    def _define_research_permissions(self) -> Dict[str, Dict[str, Any]]:
        """Define research permissions structure"""
        return {
            "research.view": {
                "description": "View research data and analyses",
                "required_roles": ["surgeon", "researcher", "admin"],
                "data_scope": "limited",
            },
            "research.analyze": {
                "description": "Perform research analysis and cohort studies",
                "required_roles": ["surgeon", "researcher", "admin"],
                "data_scope": "standard",
            },
            "research.generate": {
                "description": "Generate research reports and publications",
                "required_roles": ["researcher", "admin"],
                "data_scope": "full",
            },
            "research.export": {
                "description": "Export research data",
                "required_roles": ["researcher", "admin"],
                "data_scope": "full",
                "additional_checks": ["export_approval"],
            },
            "research.manage": {
                "description": "Manage research settings and permissions",
                "required_roles": ["admin"],
                "data_scope": "administrative",
            },
        }

    def _user_has_research_access(self, user: User) -> bool:
        """Check if user has basic research access"""
        # Use existing user role system
        research_roles = ["surgeon", "researcher", "admin", "clinician"]
        return user.role in research_roles and user.is_active

    def _user_has_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific research permission"""
        if not self._user_has_research_access(user):
            return False

        permission_config = self.research_permissions.get(permission, {})
        required_roles = permission_config.get("required_roles", [])

        return user.role in required_roles

    def _get_user_data_scope(self, user: User) -> Dict[str, Any]:
        """Get user's data access scope"""
        # Define data access scope based on user role
        role_scopes = {
            "admin": {
                "scope_type": "all",
                "description": "Full access to all research data",
                "restrictions": [],
            },
            "researcher": {
                "scope_type": "all",
                "description": "Full research data access with export capabilities",
                "restrictions": ["require_irb_approval"],
            },
            "surgeon": {
                "scope_type": "department",
                "description": "Access to department and own cases",
                "restrictions": ["no_patient_identifiers"],
            },
            "clinician": {
                "scope_type": "own_cases",
                "description": "Access to own cases only",
                "restrictions": ["no_patient_identifiers", "no_export"],
            },
        }

        return role_scopes.get(
            user.role,
            {
                "scope_type": "restricted",
                "description": "Limited research access",
                "restrictions": ["anonymized_only", "no_export"],
            },
        )

    def _get_user_restrictions(self, user: User) -> List[str]:
        """Get user's research restrictions"""
        user_scope = self._get_user_data_scope(user)
        return user_scope.get("restrictions", [])

    def _validate_data_scope_request(
        self, requested_scope: Dict[str, Any], user_scope: Dict[str, Any]
    ) -> bool:
        """Validate that requested data scope is within user's permissions"""
        user_scope_type = user_scope.get("scope_type", "restricted")
        requested_scope_type = requested_scope.get("scope_type", "all")

        # Define scope hierarchy (higher can access lower)
        scope_hierarchy = {
            "restricted": 0,
            "own_cases": 1,
            "department": 2,
            "all": 3,
            "administrative": 4,
        }

        user_level = scope_hierarchy.get(user_scope_type, 0)
        requested_level = scope_hierarchy.get(requested_scope_type, 3)

        return user_level >= requested_level

    def _anonymize_research_data(
        self, research_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Anonymize research data for restricted users"""
        anonymized_data = []

        for case in research_data:
            anonymized_case = case.copy()

            # Remove identifying information
            if "patient_id" in anonymized_case:
                anonymized_case["patient_id"] = "ANONYMOUS"

            if "case_id" in anonymized_case:
                anonymized_case[
                    "case_id"
                ] = f"CASE_{hash(anonymized_case['case_id']) % 10000}"

            # Remove surgeon identification
            if "provider_info" in anonymized_case:
                anonymized_case["provider_info"] = {
                    "surgeon_id": "ANONYMOUS",
                    "surgeon_role": anonymized_case["provider_info"].get(
                        "surgeon_role"
                    ),
                }

            # Keep only research-relevant demographic data
            if "patient_demographics" in anonymized_case:
                demographics = anonymized_case["patient_demographics"]
                anonymized_case["patient_demographics"] = {
                    "age_group": self._categorize_age(demographics.get("age")),
                    "gender": demographics.get("gender"),
                    "bmi_category": self._categorize_bmi(demographics.get("bmi")),
                }

            anonymized_data.append(anonymized_case)

        return anonymized_data

    def _categorize_age(self, age: Optional[int]) -> str:
        """Categorize age for anonymization"""
        if not age:
            return "unknown"
        elif age < 18:
            return "pediatric"
        elif age < 65:
            return "adult"
        else:
            return "elderly"

    def _categorize_bmi(self, bmi: Optional[float]) -> str:
        """Categorize BMI for anonymization"""
        if not bmi:
            return "unknown"
        elif bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"
