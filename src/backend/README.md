# GTD Backend API

FastAPI-based backend for the GTD (Getting Things Done) system.

## 🚀 Quick Start

### 1. Configuration
Copy the environment template and update with your Supabase credentials:
```bash
cp .env.example .env
```

Update the config file:
```bash
# Edit config/config.yaml with your Supabase credentials
vim ../../config/config.yaml
```

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Locally
```bash
# Run with uvicorn
uvicorn app.main:app --reload

# Or use the run script
python -m app.main
```

### 4. Run with Docker
```bash
# Build and run with docker-compose
docker-compose up --build

# Or build the Alpine image
docker build -f docker/Dockerfile.alpine -t gtd-backend .
docker run -p 8000:8000 gtd-backend
```

## 📚 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

## 🏗️ Project Structure

```
src/backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration management
│   ├── database.py      # Database setup
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── api/             # API endpoints
│   ├── crud/            # Database operations
│   └── core/            # Core functionality
├── tests/               # Test suite
├── cli/                 # Console testing client
├── docker/              # Docker configuration
└── config/              # YAML configuration
```

## 🔧 Configuration

All configuration is managed through `config/config.yaml`. The system supports:
- Environment variable overrides for sensitive data
- Different environments (development, testing, production)
- Feature flags for gradual rollout

Key configuration sections:
- `app`: Application metadata
- `database`: Supabase and PostgreSQL settings
- `security`: JWT and authentication
- `cors`: Cross-origin settings
- `gtd`: GTD-specific configuration

## 🐳 Docker

The backend uses Alpine Linux for minimal image size:
```bash
# Build image
docker build -f docker/Dockerfile.alpine -t gtd-backend:latest .

# Run container
docker run -p 8000:8000 \
  -e CONFIG_FILE=/app/config/config.yaml \
  -v $(pwd)/config:/app/config:ro \
  gtd-backend:latest
```

## 🚀 Deployment

The backend is designed to run on Render.com:
1. Connect your GitHub repository
2. Set environment variables
3. Deploy with Docker

## 📝 License

Part of the GTD System project.