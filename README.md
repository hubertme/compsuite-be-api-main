# FastAPI Production-Ready Boilerplate

A production-ready FastAPI boilerplate with best practices for building secure, scalable, and maintainable APIs.

## Features

### Core Features
- ✨ FastAPI for high-performance API development
- 🔒 Built-in security features and middleware
- 📝 Comprehensive API documentation with Swagger/ReDoc
- 🔄 Database migrations with Alembic
- 🎯 Type checking with Pydantic and MyPy
- 📊 Prometheus metrics and monitoring
- 🚦 Rate limiting with Redis
- 🔍 Structured logging with correlation IDs
- ⚡ CORS, GZip, and other performance middleware
- 🛡️ Exception handling with standardized responses
- 🗄️ Repository pattern for database operations
- 🔄 Async database transaction management
- 📦 Redis caching with decorator support
- 🎯 Background tasks with Celery
- 🏥 Health check system with DB and Redis monitoring

### Development Tools
- 🐳 Docker and Docker Compose support
- 🧪 Comprehensive test suite with pytest
- 🎨 Code formatting with Black and isort
- 📋 Linting with Flake8
- 🔍 Type checking with MyPy
- 🪝 Pre-commit hooks
- 📦 Modern dependency management with Poetry
- 🔄 CI/CD with GitHub Actions

### Security Features
- 🔐 JWT Authentication with refresh tokens
- 🛡️ Enhanced security headers middleware
- 🚫 Rate limiting per endpoint
- 🔒 CORS protection with proper configuration
- 🔑 Environment-based configuration
- 🛡️ Input validation and sanitization
- 🔒 Session security with CSRF protection
- 🛡️ Content Security Policy (CSP)
- 🔒 HTTPS redirection in production
- 🛡️ Permissions Policy
- 🔒 Strict CORS configuration

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Poetry for dependency management
- Docker and Docker Compose (optional)
- PostgreSQL
- Redis

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fastapi-boilerplate.git
cd fastapi-boilerplate
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Copy the environment file and update it:
```bash
cp .env.example .env
```

4. Set `APP_ENV` environment variable`:
```bash
export APP_ENV=dev
export APP_ENV=staging
export APP_ENV=prod
```

5. Start the required services (PostgreSQL and Redis):
```bash
docker-compose up -d db redis
```

6. Create new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

7. Run database migrations:
```bash
poetry run alembic upgrade head
```

8. Start the development server:
```bash
poetry run python main.py
```

9. (Optional) Start the Celery worker for background tasks:
```bash
p
```

The API will be available at http://localhost:8000/api/v1

API Documentation:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Docker Deployment

To run the entire stack with Docker:

```bash
docker-compose up -d
```

This will start:
- FastAPI application
- PostgreSQL database
- Redis for caching and rate limiting
- Celery worker for background tasks

## Project Structure

```
.
├── alembic/            # Database migrations
├── app/
│   ├── api/           # API endpoints and middleware
│   │   ├── v1/       # API version 1 endpoints
│   │   ├── errors/   # Error handlers
│   │   ├── cors.py   # CORS configuration
│   │   └── middleware.py # Application middleware
│   ├── core/         # Core modules
│   │   ├── cache.py  # Redis caching
│   │   ├── config.py # Configuration management
│   │   ├── exceptions.py # Custom exceptions
│   │   └── security.py # Authentication and security
│   ├── models/       # SQLAlchemy models
│   ├── repositories/ # Repository pattern implementations
│   ├── schemas/      # Pydantic models
│   ├── services/     # Business logic
│   ├── utils/        # Utility functions
│   └── worker/       # Celery tasks and configuration
├── tests/            # Test suite
│   ├── api/         # API tests
│   ├── core/        # Core module tests
│   └── conftest.py  # Test configuration
├── .env.example      # Example environment variables
├── .github/         # GitHub configurations
│   └── workflows/   # GitHub Actions workflows
├── .pre-commit-config.yaml # Pre-commit hooks
├── Dockerfile       # Main application Dockerfile
├── celery.dockerfile # Celery worker Dockerfile
├── docker-compose.yml # Docker Compose configuration
├── pyproject.toml   # Project dependencies
└── README.md
```

## Development

### Setting Up Development Environment

1. Install dependencies:
```bash
poetry install
```

2. Set up pre-commit hooks:
```bash
poetry run pre-commit install
```

3. Create and update environment variables:
```bash
cp .env.example .{dev/staging/prod}.env
# Edit .env with your configuration
```

### Running Tests

Run all tests:
```bash
poetry run pytest
```

Run with coverage:
```bash
poetry run pytest --cov=app --cov-report=term-missing
```

Run specific test file:
```bash
poetry run pytest tests/api/v1/test_auth.py -v
```

### Code Quality

Format code:
```bash
poetry run black .
poetry run isort .
```

Run linting:
```bash
poetry run flake8 .
```

Type checking:
```bash
poetry run mypy .
```

### Database Operations

Create new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

Rollback migration:
```bash
poetry run alembic downgrade -1
```

### Running Services

Start API server:
```bash
poetry run python main.py
```

Start Celery worker:
```bash
poetry run celery -A app.worker.celery_app worker --loglevel=info
```

## Production Deployment

### Docker Deployment

Build and run with Docker Compose:
```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale worker=3
```

### Manual Deployment

1. Set up environment:
   - Install Python 3.8+
   - Install PostgreSQL
   - Install Redis
   - Configure environment variables

2. Install dependencies:
```bash
poetry install --no-dev
```

3. Run migrations:
```bash
poetry run alembic upgrade head
```

4. Start services:
```bash
# Start API server
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Start Celery worker
poetry run celery -A app.worker.celery_app worker --loglevel=info
```

### Environment Variables

Key environment variables:

```bash
# API
PROJECT_NAME=FastAPI Boilerplate
VERSION=0.1.0
ENVIRONMENT=production  # development, staging, production

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days
REFRESH_TOKEN_EXPIRE_MINUTES=43200  # 30 days

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-password
POSTGRES_DB=app

# Redis
REDIS_URL=redis://localhost:6379/0

# Server
HOST=0.0.0.0
PORT=8000
ALLOWED_HOSTS=["your-domain.com"]
```

See `.env.example` for all available configuration options.

## Contributing

1. Fork the repository
2. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```
3. Make your changes
4. Run tests and linting:
```bash
poetry run pytest
poetry run black .
poetry run isort .
poetry run flake8 .
poetry run mypy .
```
5. Commit your changes:
```bash
git commit -m "feat: add your feature"
```
6. Push to your fork:
```bash
git push origin feature/your-feature-name
```
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
