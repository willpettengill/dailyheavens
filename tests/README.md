# DailyHeavens API Test Suite

This directory contains the test suite for the DailyHeavens API services. The tests are designed to validate the functionality of the birth chart calculation and interpretation services, ensure environment setup is correct, and verify API responses.

## Test Structure

The test suite is organized into the following modules:

- **test_environment.py**: Verifies the environment setup, including Python version, flatlib availability, and service initialization
- **test_birth_chart.py**: Tests the birth chart calculation service against known reference data
- **test_interpretation.py**: Tests the interpretation service with various birth charts
- **test_api_responses.py**: Tests API response structure and validation

## Running Tests

To run the entire test suite:

```bash
./run_tests.sh
```

To run individual test modules:

```bash
# Run environment tests
python -m pytest tests/test_environment.py -v

# Run birth chart tests
python -m pytest tests/test_birth_chart.py -v

# Run interpretation tests
python -m pytest tests/test_interpretation.py -v

# Run API response tests
python -m pytest tests/test_api_responses.py -v
```

## Reference Chart Data

The test suite uses a reference chart (June 20, 1988, 4:15 AM in Newton, MA) as a known, verified chart to test against. This data is stored in:

- `tests/data/reference_chart.json` (created by the test suite when first run)

This approach allows us to:
1. Verify the birth chart calculation against known data
2. Test the interpretation service with consistent input
3. Ensure API response formats are maintained

## Independent Service Testing

The test suite is designed to allow testing of services in isolation:

- The birth chart service can be tested independently
- The interpretation service can be tested with predefined chart data
- The environment setup can be verified separately
- Individual API endpoints can be tested directly

This isolation helps identify specific issues when they arise.

## Error Handling

Tests include validation of error handling scenarios, ensuring that:

- Invalid inputs are properly rejected with appropriate status codes
- Error messages are clear and helpful
- The services remain stable when receiving invalid data
- API endpoints handle edge cases gracefully

## Performance Testing

Basic performance metrics are collected during testing to help identify:

- Response time for birth chart calculations
- Response time for interpretations
- API endpoint performance under load
- Resource usage patterns

## Extending the Tests

When adding new features to the services, please add corresponding tests that:

1. Verify the API endpoint functionality
2. Test input validation and error handling
3. Include performance benchmarks if relevant
4. Consider edge cases specific to the feature 