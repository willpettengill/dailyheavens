# Astrological Service

A modern REST API service for generating astrological charts, horoscopes, and reports.

## Features
- Generate birth charts and horoscopes based on birth date, time, and location
- Export reports as PDF
- Email delivery capabilities
- Webhook integration for automated horoscope generation

## Setup
1. Install Poetry (dependency management):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Create `.env` file with required environment variables:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SECRET_KEY=your-secret-key
```

4. Run the service:
```bash
poetry run uvicorn app.main:app --reload
```

## API Documentation
Once running, visit http://localhost:8000/docs for interactive API documentation.
