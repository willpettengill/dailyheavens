.PHONY: test test-cov lint format clean

# Run all tests
test:
	pytest -v

# Run tests with coverage report
test-cov:
	pytest --cov=app --cov-report=term-missing -v

# Run linting
lint:
	flake8 app tests
	black --check app tests
	isort --check-only app tests

# Format code
format:
	black app tests
	isort app tests

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +

# Install development dependencies
dev-install:
	pip install -r requirements-dev.txt

# Install production dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	uvicorn app.main:app --reload --port 8000

# Run the application in production mode
run-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Generate documentation
docs:
	pdoc --html --output-dir docs app

# Run all checks
check: lint test 