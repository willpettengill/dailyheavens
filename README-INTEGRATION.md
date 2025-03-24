# Daily Heavens: Frontend and Backend Integration

This document explains how to integrate the Next.js frontend with the Python backend services.

## System Architecture

The Daily Heavens application consists of:

1. **Next.js Frontend**: UI for users to enter birth details and view astrological information
2. **Frontend Adapter**: A FastAPI service that translates between frontend requests and backend services
3. **Birth Chart Service**: Calculates astrological birth charts using flatlib
4. **Interpretation Service**: Interprets birth charts with detailed astrological meanings

## Directory Structure

```
/dailyheavens/
├── app/                # Backend services source code
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality
│   ├── models/         # Data models
│   └── services/       # Business logic
├── data/               # Astrological data
├── frontend/           # Next.js frontend
│   ├── app/            # Next.js app directory
│   ├── components/     # React components
│   ├── lib/            # Frontend utilities
│   └── public/         # Static assets
├── integration/        # Integration adapter
│   └── birth_chart_adapter.py  # Adapter service
└── tests/              # Backend tests
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PNPM
- Docker and Docker Compose (optional, for containerized setup)

### 1. Setup the Backend

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

### 2. Setup the Integration Adapter

```bash
# Install dependencies for the adapter
cd integration
pip install -r requirements.txt

# Run the adapter
uvicorn birth_chart_adapter:app --host 0.0.0.0 --port 8000
```

### 3. Setup the Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
pnpm install

# Start the development server
pnpm dev
```

### 4. Using Docker Compose (Alternative)

```bash
# Start all services
docker-compose up

# Access the frontend at http://localhost:3000
# Access the API at http://localhost:8000
```

## Testing the Integration

### Test the API Directly

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "birth_date": "06/15/1990",
  "birth_time": "14:30",
  "birth_place_zip": "10001"
}' http://localhost:8000/birth-chart
```

### Test via Frontend

1. Open http://localhost:3000/api-test in your browser
2. The test page will check connectivity to all backend services
3. You can manually test different endpoints and configurations

## Debugging Common Issues

### CORS Issues

If you encounter CORS errors, ensure that the CORS middleware is properly configured in all services.

### API Connection Issues

The frontend includes fallback mechanisms and will display mock data if the backend is unavailable.

### Missing Environment Variables

Ensure that all required environment variables are set in `.env.local` files or in your deployment platform.

## Deployment

### Vercel Deployment

1. Connect your GitHub repository to Vercel
2. Configure environment variables:
   - `BIRTH_CHART_API_URL`: URL of the birth chart API
   - `INTERPRETATION_API_URL`: URL of the interpretation API
   - `NEXT_PUBLIC_BIRTH_CHART_API_URL`: Publicly accessible URL for frontend

3. Deploy the project:
   ```bash
   vercel
   ```

### Alternative Deployment Options

1. **Containerized Deployment**: Use the provided Docker Compose setup
2. **Separate Deployments**: Deploy frontend to Vercel and backend to a cloud provider that supports Python

## Known Issues and Limitations

1. The current ZIP code to coordinates mapping is limited. A proper geocoding service should be used in production.
2. The adapter service doesn't yet support the full range of interpretation features.
3. Error handling needs to be improved for production use.

## Next Steps

1. Implement proper geocoding service integration
2. Add authentication and user profiles
3. Enhance error handling and logging
4. Add automated tests for the integrated system 