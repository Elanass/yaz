"""Common validation classes for general data types."""

import re
from datetime import datetime, date
from typing import Any, List, Optional, Union
from email_validator import validate_email, EmailNotValidError

from .base import BaseValidator, ValidationResult


class EmailValidator(BaseValidator):
    """Validator for email addresses."""
    
    def __init__(self, strict: bool = True, check_deliverability: bool = False):
        """
        Initialize email validator.
        
        Args:
            strict: Strict validation mode
            check_deliverability: Whether to check if email domain exists
        """
        super().__init__(strict)
        self.check_deliverability = check_deliverability
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate email address format."""
        result = self._create_result()
        
        if not isinstance(data, str):
            result.add_error("Email must be a string")
            return self._handle_result(result)
        
        try:
            validate_email(
                data,
                check_deliverability=self.check_deliverability
            )
        except EmailNotValidError as e:
            result.add_error(f"Invalid email: {str(e)}")
        
        return self._handle_result(result)


class PhoneValidator(BaseValidator):
    """Validator for phone numbers."""
    
    # Common phone number patterns
    PATTERNS = {
        'us': re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'),
        'international': re.compile(r'^\+?[1-9]\d{1,14}$'),
        'simple': re.compile(r'^\+?[\d\s\-\(\)\.]{7,15}$')
    }
    
    def __init__(self, format_type: str = 'simple', strict: bool = True):
        """
        Initialize phone validator.
        
        Args:
            format_type: Phone format type ('us', 'international', 'simple')
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.format_type = format_type
        self.pattern = self.PATTERNS.get(format_type, self.PATTERNS['simple'])
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate phone number format."""
        result = self._create_result()
        
        if not isinstance(data, str):
            result.add_error("Phone number must be a string")
            return self._handle_result(result)
        
        # Remove common separators for validation
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', data)
        
        if not self.pattern.match(data):
            result.add_error(f"Invalid phone number format for {self.format_type}")
        
        # Additional US-specific validation
        if self.format_type == 'us' and len(cleaned) >= 10:
            area_code = cleaned[-10:-7] if len(cleaned) > 10 else cleaned[:3]
            if area_code.startswith('0') or area_code.startswith('1'):
                result.add_error("US area code cannot start with 0 or 1")
        
        return self._handle_result(result)


class DateValidator(BaseValidator):
    """Validator for dates."""
    
    def __init__(
        self,
        date_format: str = '%Y-%m-%d',
        min_date: Union[str, date, datetime] = None,
        max_date: Union[str, date, datetime] = None,
        strict: bool = True
    ):
        """
        Initialize date validator.
        
        Args:
            date_format: Expected date format string
            min_date: Minimum allowed date
            max_date: Maximum allowed date
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.date_format = date_format
        self.min_date = self._parse_date(min_date) if min_date else None
        self.max_date = self._parse_date(max_date) if max_date else None
    
    def _parse_date(self, date_value: Union[str, date, datetime]) -> date:
        """Parse date from various formats."""
        if isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, str):
            return datetime.strptime(date_value, self.date_format).date()
        else:
            raise ValueError(f"Invalid date type: {type(date_value)}")
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate date format and range."""
        result = self._create_result()
        
        try:
            if isinstance(data, str):
                parsed_date = datetime.strptime(data, self.date_format).date()
            elif isinstance(data, (date, datetime)):
                parsed_date = data.date() if isinstance(data, datetime) else data
            else:
                result.add_error("Date must be a string, date, or datetime object")
                return self._handle_result(result)
        except ValueError as e:
            result.add_error(f"Invalid date format: {str(e)}")
            return self._handle_result(result)
        
        # Check date range
        if self.min_date and parsed_date < self.min_date:
            result.add_error(f"Date must be after {self.min_date}")
        
        if self.max_date and parsed_date > self.max_date:
            result.add_error(f"Date must be before {self.max_date}")
        
        # Check for reasonable date (not too far in past/future)
        current_year = datetime.now().year
        if parsed_date.year < 1900:
            result.add_warning("Date is very far in the past")
        elif parsed_date.year > current_year + 100:
            result.add_warning("Date is very far in the future")
        
        return self._handle_result(result)


class StringValidator(BaseValidator):
    """Validator for string content and format."""
    
    def __init__(
        self,
        min_length: int = None,
        max_length: int = None,
        pattern: str = None,
        allowed_chars: str = None,
        forbidden_chars: str = None,
        case_sensitive: bool = True,
        strip_whitespace: bool = True,
        strict: bool = True
    ):
        """
        Initialize string validator.
        
        Args:
            min_length: Minimum string length
            max_length: Maximum string length
            pattern: Regular expression pattern to match
            allowed_chars: Characters allowed in string
            forbidden_chars: Characters forbidden in string
            case_sensitive: Whether validation is case sensitive
            strip_whitespace: Whether to strip leading/trailing whitespace
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.allowed_chars = set(allowed_chars) if allowed_chars else None
        self.forbidden_chars = set(forbidden_chars) if forbidden_chars else None
        self.case_sensitive = case_sensitive
        self.strip_whitespace = strip_whitespace
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate string content and format."""
        result = self._create_result()
        
        if not isinstance(data, str):
            result.add_error("Value must be a string")
            return self._handle_result(result)
        
        # Process string
        value = data
        if self.strip_whitespace:
            value = value.strip()
        
        if not self.case_sensitive:
            value = value.lower()
        
        # Length validation
        if self.min_length is not None and len(value) < self.min_length:
            result.add_error(f"String must be at least {self.min_length} characters")
        
        if self.max_length is not None and len(value) > self.max_length:
            result.add_error(f"String must be at most {self.max_length} characters")
        
        # Pattern validation
        if self.pattern and not self.pattern.match(value):
            result.add_error(f"String does not match required pattern")
        
        # Character validation
        if self.allowed_chars:
            invalid_chars = set(value) - self.allowed_chars
            if invalid_chars:
                result.add_error(f"String contains invalid characters: {invalid_chars}")
        
        if self.forbidden_chars:
            found_forbidden = set(value) & self.forbidden_chars
            if found_forbidden:
                result.add_error(f"String contains forbidden characters: {found_forbidden}")
        
        return self._handle_result(result)


class NumericValidator(BaseValidator):
    """Validator for numeric values."""
    
    def __init__(
        self,
        min_value: Union[int, float] = None,
        max_value: Union[int, float] = None,
        decimal_places: int = None,
        allow_negative: bool = True,
        allow_zero: bool = True,
        integer_only: bool = False,
        strict: bool = True
    ):
        """
        Initialize numeric validator.
        
        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            decimal_places: Maximum number of decimal places
            allow_negative: Whether negative values are allowed
            allow_zero: Whether zero is allowed
            integer_only: Whether only integers are allowed
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_places = decimal_places
        self.allow_negative = allow_negative
        self.allow_zero = allow_zero
        self.integer_only = integer_only
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate numeric value."""
        result = self._create_result()
        
        # Type conversion and validation
        try:
            if isinstance(data, str):
                if self.integer_only:
                    value = int(data)
                else:
                    value = float(data)
            elif isinstance(data, (int, float)):
                value = data
            else:
                result.add_error("Value must be numeric")
                return self._handle_result(result)
        except (ValueError, TypeError):
            result.add_error("Value must be a valid number")
            return self._handle_result(result)
        
        # Integer validation
        if self.integer_only and not isinstance(value, int) and value != int(value):
            result.add_error("Value must be an integer")
        
        # Sign validation
        if not self.allow_negative and value < 0:
            result.add_error("Negative values are not allowed")
        
        if not self.allow_zero and value == 0:
            result.add_error("Zero is not allowed")
        
        # Range validation
        if self.min_value is not None and value < self.min_value:
            result.add_error(f"Value must be at least {self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            result.add_error(f"Value must be at most {self.max_value}")
        
        # Decimal places validation
        if self.decimal_places is not None and isinstance(value, float):
            decimal_str = str(value).split('.')
            if len(decimal_str) > 1 and len(decimal_str[1]) > self.decimal_places:
                result.add_error(f"Value can have at most {self.decimal_places} decimal places")
        
        return self._handle_result(result)


class URLValidator(BaseValidator):
    """Validator for URLs."""
    
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    def __init__(self, require_https: bool = False, strict: bool = True):
        """
        Initialize URL validator.
        
        Args:
            require_https: Whether to require HTTPS protocol
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.require_https = require_https
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate URL format."""
        result = self._create_result()
        
        if not isinstance(data, str):
            result.add_error("URL must be a string")
            return self._handle_result(result)
        
        if not self.URL_PATTERN.match(data):
            result.add_error("Invalid URL format")
            return self._handle_result(result)
        
        if self.require_https and not data.lower().startswith('https://'):
            result.add_error("URL must use HTTPS protocol")
        
        return self._handle_result(result)
