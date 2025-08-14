"""Base validation classes and utilities."""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)


class ValidationError(Exception):
    """Exception raised when validation fails."""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class BaseValidator(ABC):
    """Base class for all validators."""
    
    def __init__(self, strict: bool = True):
        """
        Initialize validator.
        
        Args:
            strict: If True, validation errors raise exceptions.
                   If False, return ValidationResult with errors.
        """
        self.strict = strict
    
    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """
        Validate the provided data.
        
        Args:
            data: Data to validate
            
        Returns:
            ValidationResult with validation status and any errors/warnings
            
        Raises:
            ValidationError: If strict=True and validation fails
        """
        pass
    
    def _create_result(self) -> ValidationResult:
        """Create a new validation result."""
        return ValidationResult(is_valid=True, errors=[], warnings=[])
    
    def _handle_result(self, result: ValidationResult) -> ValidationResult:
        """Handle validation result based on strict mode."""
        if self.strict and result.has_errors:
            raise ValidationError(
                f"Validation failed: {'; '.join(result.errors)}",
                errors=result.errors
            )
        return result


class RegexValidator(BaseValidator):
    """Validator that uses regular expressions."""
    
    def __init__(self, pattern: str, message: str = None, strict: bool = True):
        """
        Initialize regex validator.
        
        Args:
            pattern: Regular expression pattern
            message: Custom error message
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.pattern = re.compile(pattern)
        self.message = message or f"Value does not match pattern: {pattern}"
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate data against regex pattern."""
        result = self._create_result()
        
        if not isinstance(data, str):
            result.add_error("Value must be a string")
            return self._handle_result(result)
        
        if not self.pattern.match(data):
            result.add_error(self.message)
        
        return self._handle_result(result)


class LengthValidator(BaseValidator):
    """Validator for string/collection length constraints."""
    
    def __init__(
        self,
        min_length: int = None,
        max_length: int = None,
        strict: bool = True
    ):
        """
        Initialize length validator.
        
        Args:
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate data length constraints."""
        result = self._create_result()
        
        try:
            length = len(data)
        except TypeError:
            result.add_error("Value must have a length")
            return self._handle_result(result)
        
        if self.min_length is not None and length < self.min_length:
            result.add_error(f"Length must be at least {self.min_length}")
        
        if self.max_length is not None and length > self.max_length:
            result.add_error(f"Length must be at most {self.max_length}")
        
        return self._handle_result(result)


class RangeValidator(BaseValidator):
    """Validator for numeric range constraints."""
    
    def __init__(
        self,
        min_value: Union[int, float] = None,
        max_value: Union[int, float] = None,
        strict: bool = True
    ):
        """
        Initialize range validator.
        
        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate numeric range constraints."""
        result = self._create_result()
        
        if not isinstance(data, (int, float)):
            result.add_error("Value must be numeric")
            return self._handle_result(result)
        
        if self.min_value is not None and data < self.min_value:
            result.add_error(f"Value must be at least {self.min_value}")
        
        if self.max_value is not None and data > self.max_value:
            result.add_error(f"Value must be at most {self.max_value}")
        
        return self._handle_result(result)


class CompositeValidator(BaseValidator):
    """Validator that combines multiple validators."""
    
    def __init__(self, validators: List[BaseValidator], strict: bool = True):
        """
        Initialize composite validator.
        
        Args:
            validators: List of validators to apply
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.validators = validators
    
    def validate(self, data: Any) -> ValidationResult:
        """Apply all validators to the data."""
        result = self._create_result()
        
        for validator in self.validators:
            # Temporarily disable strict mode to collect all errors
            validator_strict = validator.strict
            validator.strict = False
            
            try:
                validator_result = validator.validate(data)
                result.errors.extend(validator_result.errors)
                result.warnings.extend(validator_result.warnings)
            except ValidationError as e:
                result.errors.extend(e.errors)
            finally:
                validator.strict = validator_strict
        
        if result.has_errors:
            result.is_valid = False
        
        return self._handle_result(result)


class ConditionalValidator(BaseValidator):
    """Validator that applies validation based on conditions."""
    
    def __init__(
        self,
        condition: callable,
        validator: BaseValidator,
        strict: bool = True
    ):
        """
        Initialize conditional validator.
        
        Args:
            condition: Function that returns True if validation should be applied
            validator: Validator to apply when condition is met
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.condition = condition
        self.validator = validator
    
    def validate(self, data: Any) -> ValidationResult:
        """Apply validator only if condition is met."""
        result = self._create_result()
        
        if self.condition(data):
            return self.validator.validate(data)
        
        return self._handle_result(result)
