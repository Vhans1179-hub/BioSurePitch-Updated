# BioSure Backend API

FastAPI backend for the BioSure application with MongoDB Atlas integration.

## Features

- ✅ FastAPI with async/await support
- ✅ MongoDB Atlas integration using Motor (async driver)
- ✅ CORS configuration for frontend
- ✅ Health check endpoint
- ✅ Environment-based configuration
- ✅ Pydantic v2 for data validation

## Prerequisites

- Python 3.9 or higher
- MongoDB Atlas account (or local MongoDB instance)
- pip or poetry for package management

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your MongoDB connection string:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=biosure_db
CORS_ORIGINS=["http://localhost:5173"]
```

### 4. Run the Application

```bash
# From the backend directory
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or use the main.py directly
python main.py
```

The API will be available at:
- API Base: `http://localhost:8000/api/v1`
- Health Check: `http://localhost:8000/healthz`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```
GET /healthz
```

Returns the health status of the API and database connection.

**Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2025-12-15T20:00:00.000Z"
}
```

### API Root
```
GET /api/v1/
```

Returns welcome message and API information.

## Project Structure

```
backend/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── database.py          # MongoDB connection handling
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Development

### Running Tests
```bash
# Tests will be added in future sprints
pytest
```

### Code Formatting
```bash
# Format code with black
black .

# Sort imports
isort .
```

### Type Checking
```bash
# Run mypy for type checking
mypy .
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `biosure_db` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:5173"]` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `API_V1_PREFIX` | API version prefix | `/api/v1` |

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Verify your MongoDB URI is correct in `.env`
2. Check that your IP address is whitelisted in MongoDB Atlas
3. Ensure your MongoDB user has proper permissions
4. The API will start even if database connection fails, but database operations will not work

### CORS Issues

If frontend cannot connect:

1. Verify `CORS_ORIGINS` in `.env` includes your frontend URL
2. Check that the frontend is running on the specified port
3. Ensure credentials are included in frontend requests

## Next Steps

Sprint S0 is complete. The following sprints will add:
- S1: User authentication and authorization
- S2: Cohort management endpoints
- S3: Contract simulation endpoints
- And more...

## License

Proprietary - BioSure Application