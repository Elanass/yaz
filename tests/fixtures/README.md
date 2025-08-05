# Test Fixtures

This directory contains test data, sample databases, and other fixtures used across the test suite.

## Database Fixtures

### `test_surgify.db`
SQLite test database containing sample data for testing:
- Sample surgical cases
- Test user accounts
- Procedure types and diagnoses
- Risk assessments
- Recommendations data

**Usage**: This database is automatically used by integration tests and can be used for manual testing.

## Adding New Fixtures

When adding new test fixtures:

1. Place data files in this directory
2. Use descriptive filenames (e.g., `sample_cases.json`, `test_users.csv`)
3. Include documentation about the fixture's purpose
4. Update this README with descriptions

## Fixture Management

- Keep fixtures small and focused
- Use realistic but anonymized data
- Ensure fixtures are version controlled
- Clean up temporary fixtures after tests
