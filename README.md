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

## Environment Setup

1. Create a `.env.local` file in the `dailyheavens-frontend` directory with the following content:

```
NEXT_PUBLIC_BIRTH_CHART_API_URL=http://localhost:8001/api/v1/birthchart
NEXT_PUBLIC_INTERPRETATION_API_URL=http://localhost:8002/api/v1/interpretation
```

## Running the Services

1. **Start the Birth Chart Service**:
   - Ensure you are in the project root directory.
   - Run the following command:
     ```bash
     uvicorn app.birth_chart_server:app --host 0.0.0.0 --port 8001
     ```
   - You should see confirmation that the server is running on http://0.0.0.0:8001
   - The API documentation will be available at http://localhost:8001/api/docs

2. **Start the Interpretation Service**:
   - In a separate terminal, run:
     ```bash
     uvicorn app.interpretation_server:app --host 0.0.0.0 --port 8002
     ```
   - You should see confirmation that the server is running on http://0.0.0.0:8002
   - The API documentation will be available at http://localhost:8002/api/docs

3. **Start the Frontend** (optional):
   - Navigate to the `dailyheavens-frontend` directory.
   - Run:
     ```bash
     pnpm dev
     ```

## Generating a Birth Chart and Interpretation

### Using cURL

1. **Generate a Birth Chart**:
   ```bash
   curl -X POST http://localhost:8001/api/v1/birthchart \\
     -H "Content-Type: application/json" \\
     -d \'{\"date\": \"1988-06-20T04:15:00\", \"latitude\": 42.3370, \"longitude\": -71.2092, \"timezone\": \"America/New_York\"}\' \\
     -o birth_chart_response.json
   ```
   *(Note: Ensure the JSON data is on a single line or use appropriate escaping for multi-line JSON in your shell.)*

2. **Format the Birth Chart for Interpretation**: The interpretation service expects the birth chart data nested under a `birth_chart` key. Use `jq` to extract the chart data (`.data`) and wrap it to create the correct payload:
   ```bash
   jq '{birth_chart: .data}' birth_chart_response.json > interpretation_payload.json
   ```

3. **Generate an Interpretation** (using the formatted payload):
   ```bash
   curl -X POST http://localhost:8002/api/v1/interpretation \\
     -H "Content-Type: application/json" \\
     -d @interpretation_payload.json \\
     -o interpretation_response.json
   ```

4. **Extract the Overall Interpretation**: Use `jq` again to extract just the overall interpretation text (located under `data.interpretations.overall`) and save it to a Markdown file:
   ```bash
   jq -r '.data.interpretations.overall' interpretation_response.json > overall_interpretation.md
   ```

### Using the API Documentation UI

1. Open the Birth Chart API docs at http://localhost:8001/api/docs
2. Click on the POST /api/v1/birthchart endpoint
3. Click "Try it out"
4. Enter birth data in the request body (example below) and click "Execute":
   ```json
   {
     "date": "1988-06-20T04:15:00",
     "latitude": 42.3370,
     "longitude": -71.2092,
     "timezone": "America/New_York"
   }
   ```
5. Copy the response body containing the birth chart data
6. Open the Interpretation API docs at http://localhost:8002/api/docs
7. Click on the POST /api/v1/interpretation endpoint
8. Click "Try it out"
9. Paste the birth chart data into the request body. **Important:** You must manually wrap the copied birth chart data within a `birth_chart` key like this:
   ```json
   {
     "birth_chart": {
       // Paste the entire birth chart response from step 5 here
       "planets": { ... },
       "houses": { ... },
       // ... etc ...
     }
   }
   ```
10. Click "Execute" to get your interpretation

## Troubleshooting

- **404 Not Found**: Check that you're using the correct endpoint path (`/api/v1/birthchart` or `/api/v1/interpretation`)
- **Syntax Errors**: Check for syntax or indentation errors in Python files before starting services
- **Port Already in Use**: Kill existing processes using the required ports:
   ```bash
   pkill -f 'uvicorn app.birth_chart_server:app'  # For birth chart service
   pkill -f 'uvicorn app.interpretation_server:app'  # For interpretation service
   ```
- **ModuleNotFoundError**: Ensure you're running commands from the project root directory
- **Missing Outer Planets**: Warnings about missing Uranus, Neptune, or Pluto in charts are normal and don't affect core functionality
- **JSON Formatting**: When copying birth chart data for interpretation, ensure proper JSON formatting is maintained

## Verifying the Setup

- Access the frontend at `http://localhost:3000` (or the next available port).
- Test the birth chart functionality to ensure the frontend and backend are communicating correctly.

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