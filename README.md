# Daily Heavens: Astrological API Services

Daily Heavens provides robust API services for birth chart calculations and astrological interpretations.

## Project Structure

The project consists of two main services:

1. **Birth Chart Service** (Port 8001):
   - Calculates accurate birth charts using Flatlib
   - Provides detailed planetary positions, houses, and aspects
   - Endpoint: `/api/v1/birthchart`

2. **Interpretation Service** (Port 8002):
   - Generates detailed astrological interpretations
   - Analyzes birth chart patterns and configurations
   - Endpoint: `/api/v1/interpretation`

## Getting Started

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)

### Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Services

1. Start the Birth Chart Service (two options available):

```bash
# Option 1 - Direct API
uvicorn app.birth_chart_server:app --host 0.0.0.0 --port 8001

# Option 2 - V1 API with additional endpoints
uvicorn app.api.v1.api:api_router --host 0.0.0.0 --port 8001
```

2. In a separate terminal, start the Interpretation Service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Important Notes

1. **Birth Chart Service Endpoints**:
   - Direct API: `POST /birthchart`
   - V1 API: `POST /v1/birthchart`
   - The V1 API includes additional endpoints and structured responses

2. **Interpretation Service Endpoints**:
   - Main endpoint: `POST /api/v1/interpretation`
   - Requires a valid birth chart in the request body
   - Structured data files in `data/structured/` must be accessible

3. **Known Issues**:
   - Some planetary positions (Uranus, Neptune, Pluto, Chiron) may show as "not found" - this is expected
   - The service must be run from the project root directory to properly load modules

## API Documentation

### Birth Chart Service
- API Documentation: http://localhost:8001/api/docs
- ReDoc Interface: http://localhost:8001/api/redoc

### Interpretation Service
- API Documentation: http://localhost:8002/api/docs
- ReDoc Interface: http://localhost:8002/api/redoc

## Development Setup

1. Install development dependencies:
```bash
make dev-install
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

## Running Tests

The project uses pytest for testing:

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test files
pytest tests/test_api_responses.py
```

### Test Categories

- API response structure and validation
- Data mapping between structured data and API responses
- Interpretation service functionality
- Performance and resource usage
- Logging functionality

## Code Quality

Maintain code quality with:

```bash
# Run all checks
make check

# Format code
make format

# Run linting
make lint
```

## Development Workflow

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make changes and commit:
```bash
git add .
git commit -m "Description of changes"
```

3. Run tests and checks:
```bash
make check
```

4. Push changes:
```bash
git push origin feature/your-feature-name
```

## Documentation

Generate documentation:
```bash
make docs
```

### Additional Documentation
- [API Documentation](docs/api.md) - Detailed API endpoints and usage
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and their resolutions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.