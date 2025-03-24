# DailyHeavens Test Suite

This directory contains the test suite for the DailyHeavens application. The tests are designed to validate the functionality of the birth chart calculation and interpretation services, ensure environment setup is correct, and verify end-to-end integration.

## Test Structure

The test suite is organized into the following modules:

- **test_environment.py**: Verifies the environment setup, including Python version, flatlib availability, and service initialization
- **test_birth_chart.py**: Tests the birth chart calculation service against known reference data
- **test_interpretation.py**: Tests the interpretation service with various birth charts
- **test_integration.py**: End-to-end tests of the full flow from birth chart calculation to interpretation

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

# Run integration tests
python -m pytest tests/test_integration.py -v
```

## Reference Chart Data

The test suite uses a reference chart (June 20, 1988, 4:15 AM in Newton, MA) as a known, verified chart to test against. This data is stored in:

- `tests/data/reference_chart.json` (created by the test suite when first run)

This approach allows us to:
1. Verify the birth chart calculation against known data
2. Test the interpretation service independently from the birth chart service
3. Ensure consistency of results over time

## Independent Component Testing

The test suite is designed to allow testing of components in isolation. For example:

- The interpretation service can be tested using the stored reference chart, without requiring the birth chart service
- The environment setup can be verified independently of the API functionality
- Individual methods of the services can be tested directly

This isolation helps identify specific issues when they arise, rather than only detecting problems at the integration level.

## Error Handling

Tests include validation of error handling scenarios, ensuring that:

- Invalid inputs are properly rejected
- Appropriate error messages are returned
- The system remains stable even when receiving bad data

## Performance Testing

Basic performance metrics are collected during testing to help identify performance regressions over time.

## Extending the Tests

When adding new features to the application, please add corresponding tests that:

1. Verify the functionality in isolation
2. Test integration with existing components
3. Include error handling scenarios
4. Consider edge cases specific to the feature 