# Testing Directory Structure

This directory contains various testing components for the Surgify platform:

## `/api/`
Standard API endpoint tests for all platform functionality:
- `test_auth_endpoints.py` - Authentication API tests
- `test_case_endpoints.py` - Case management API tests  
- `test_dashboard_endpoints.py` - Dashboard API tests
- `test_recommendations_endpoints.py` - Recommendations API tests

## `/integration/`
Integration tests that test multiple components working together:
- `test_api_endpoints.py` - Full API integration tests
- `/demos/` - Demonstration scripts showing platform capabilities

## `/compatibility/`
Backward compatibility tests ensuring existing functionality remains intact:
- `test_backward_compatibility.py` - Comprehensive backward compatibility test suite

## `/unit/`
Unit tests for individual components:
- `test_models.py` - Database model tests

## `/fixtures/`
Test data and database fixtures:
- `test_surgify.db` - Test database with sample data

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/api/          # API tests only
pytest tests/integration/  # Integration tests only
pytest tests/unit/         # Unit tests only

# Run compatibility tests
cd tests/compatibility && python test_backward_compatibility.py

# Run demonstrations
cd tests/integration/demos && python demonstrate_integration.py
```
