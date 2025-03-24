#!/bin/bash

# DailyHeavens Test Runner Script
# This script runs the tests in isolation and produces a report

set -e  # Exit on any error

# Create necessary directories
mkdir -p tests/data
mkdir -p logs

echo "================================="
echo "DailyHeavens Test Suite"
echo "================================="
echo "Running tests on $(date)"
echo

# Run environment tests first to ensure the system is ready
echo "Running environment tests..."
python -m pytest tests/test_environment.py -v || { echo "Environment setup failed!"; exit 1; }

# Run birth chart tests
echo
echo "Running birth chart service tests..."
python -m pytest tests/test_birth_chart.py -v

# Run interpretation tests
echo
echo "Running interpretation service tests..."
python -m pytest tests/test_interpretation.py -v

# Run integration tests
echo
echo "Running integration tests..."
python -m pytest tests/test_integration.py -v

echo
echo "================================="
echo "Test Summary"
echo "================================="
python -m pytest tests/ --tb=no -v 