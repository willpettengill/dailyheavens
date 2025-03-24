# Daily Heavens: Astrology Platform

Daily Heavens is a full-stack astrology platform that provides birth chart calculations, interpretations, and forecasts.

## Project Structure

The project consists of three main parts:

1. **Backend Services**:
   - Birth Chart Calculation (Python/FastAPI)
   - Astrological Interpretation (Python/FastAPI)

2. **Frontend**:
   - Next.js application with interactive UI

3. **Integration Layer**:
   - Adapter service that connects frontend and backend

## Key Features

- Accurate birth chart calculations using Flatlib
- Comprehensive astrological interpretations
- Responsive, modern UI built with Next.js
- Easy deployment to Vercel

## Getting Started

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the birth chart service
uvicorn app.birth_chart_server:app --host 0.0.0.0 --port 8001

# In a separate terminal, run the interpretation service
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Integration Adapter Setup

```bash
# Install dependencies for the adapter
cd integration
pip install -r requirements.txt

# Run the adapter
uvicorn birth_chart_adapter:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
pnpm install

# Start the development server
pnpm dev
```

## Docker Compose (Alternative)

You can use Docker Compose to run all services together:

```bash
docker-compose up
```

This will start:
- Birth Chart Service at http://localhost:8001
- Interpretation Service at http://localhost:8002
- Frontend Adapter at http://localhost:8000
- Next.js Frontend at http://localhost:3000

## Detailed Documentation

- [Backend API Documentation](http://localhost:8001/api/docs) - Available when running the birth chart service
- [Integration Guide](./README-INTEGRATION.md) - Detailed guide for connecting frontend and backend
- [Frontend Documentation](./frontend/README.md) - Next.js frontend documentation

## Deployment

### Vercel Deployment (Recommended)

1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy

### Alternative Deployment

You can also deploy the backend services separately on any provider that supports Python/FastAPI applications.

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
make dev-install
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

## Running Tests

The project uses pytest for testing. The following commands are available:

- Run all tests:
```bash
make test
```

- Run tests with coverage report:
```bash
make test-cov
```

- Run specific test files:
```bash
pytest tests/test_api_responses.py
```

- Run tests with specific markers:
```bash
pytest -m api  # Run API tests only
pytest -m integration  # Run integration tests only
pytest -m performance  # Run performance tests only
```

## Test Structure

The test suite is organized into the following categories:

- `test_api_responses.py`: Tests for API response structure and validation
- `test_data_mapping.py`: Tests for mapping between structured data and API responses
- `test_interpretation_service.py`: Tests for the interpretation service functionality
- `test_integration.py`: Tests for integration between different components
- `test_performance.py`: Tests for performance and resource usage
- `test_logging.py`: Tests for logging functionality

## Code Quality

The project uses several tools to maintain code quality:

- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run all code quality checks:
```bash
make lint
```

Format code:
```bash
make format
```

## Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "Description of your changes"
```

3. Run tests and code quality checks:
```bash
make check
```

4. Push your changes:
```bash
git push origin feature/your-feature-name
```

5. Create a pull request

## Running the Application

Development mode:
```bash
make run
```

Production mode:
```bash
make run-prod
```

## Documentation

Generate documentation:
```bash
make docs
```

The documentation will be available in the `docs` directory.

## Cleaning Up

Remove temporary files and caches:
```bash
make clean
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.