# Daily Heavens

An astrology application that generates personalized birth charts and interpretations.

## 🌟 Project Overview

Daily Heavens is a modern astrology application that calculates birth charts and provides detailed interpretations. The application is built with:

- **Next.js Frontend**: Modern React-based web application
- **FastAPI Backend**: Unified API service for birth chart calculation and interpretation
- **Supabase Database**: PostgreSQL database for storing user data

## 📋 Features

- Birth chart calculation using precise astronomical data
- Detailed astrological interpretations
- Planetary positions and aspects analysis
- House system interpretation
- Storage of user birth data and chart results
- Mobile-friendly responsive interface

## 🏗️ Architecture

The application uses a modern, serverless architecture:

```
┌────────────┐     ┌─────────────┐     ┌─────────────┐
│            │     │             │     │             │
│  Frontend  │────▶│  Unified    │────▶│  Supabase   │
│  (Next.js) │     │  API        │     │  Database   │
│            │◀────│  (FastAPI)  │◀────│             │
└────────────┘     └─────────────┘     └─────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Node.js 16+
- Python 3.9+
- Supabase account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/daily-heavens.git
cd daily-heavens
```

2. Install backend dependencies:
```bash
cd api
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd ../frontend
npm install
# or
pnpm install
```

4. Configure environment variables:
```bash
# In the root directory
cp .env.example .env
# Update the .env file with your Supabase credentials
```

### Running Locally

1. Start the API server:
```bash
cd api
uvicorn index:app --reload
```

2. Start the frontend:
```bash
cd frontend
npm run dev
# or
pnpm dev
```

3. Open your browser to `http://localhost:3000`

## 🧪 Testing

Run the test suite:

```bash
# Test the API
cd api
pytest

# Or use the shell script for integration testing
cd ..
./test_new_api.sh
```

## 📦 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🧩 Project Structure

```
├── api/                  # Unified API service (FastAPI)
│   ├── index.py          # Main API entry point
│   ├── requirements.txt  # API dependencies
│   └── test_api.py       # API tests
├── frontend/             # Next.js frontend
│   ├── app/              # Next.js application
│   ├── components/       # React components
│   ├── public/           # Static assets
│   └── package.json      # Frontend dependencies
├── .env.example          # Example environment variables
├── vercel.json           # Vercel deployment configuration
├── README.md             # This file
└── DEPLOYMENT.md         # Deployment instructions
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.