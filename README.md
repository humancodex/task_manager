# Task Management REST API

A production-ready Task Management REST API built with **FastAPI** and **PostgreSQL**, demonstrating enterprise-level API design, comprehensive testing, and modern Python development best practices.

## 🚀 Features included 

- ✅ **Full CRUD Operations** - Create, read, update, and delete tasks
- ✅ **Advanced Filtering & Sorting** - Filter by status, priority, and sort by multiple fields
- ✅ **Pagination Support** - Efficient data retrieval with configurable page sizes
- ✅ **PostgreSQL Database** - Robust relational database with SQLAlchemy ORM
- ✅ **Input Validation** - Comprehensive validation using Pydantic models
- ✅ **Auto-Generated Documentation** - OpenAPI/Swagger UI and ReDoc
- ✅ **Request/Response Logging** - Structured logging with correlation IDs
- ✅ **Docker Support** - Containerized deployment with Docker Compose
- ✅ **Database Migrations** - Alembic for database schema management
- ✅ **Comprehensive Testing** - pytest with high test coverage
- ✅ **Type Safety** - Full type hints throughout the codebase
- ✅ **Repository Pattern** - Clean separation of concerns
- ✅ **Health Check Endpoint** - Monitor application and database status

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database Setup](#database-setup)
- [Docker Deployment](#docker-deployment)
- [Testing](#testing)
- [Development Workflow](#development-workflow)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

- **Python 3.11+**
- **PostgreSQL 13+** (or Docker for containerized deployment)
- **Git**
- **Docker & Docker Compose** (for containerized deployment)

## 🏃 Quick Start

###  Local Development Setup 

1. **Clone the repository**
   ```bash
   git clone[ <repository-url>](https://github.com/humancodex/task_manager.git)
   cd task_manager
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration if needed
   # Default values work with the Docker PostgreSQL setup
   ```

5. **Start PostgreSQL with automated setup** ⭐ _Recommended!_
   ```bash
   # Make script executable and run automated setup
   chmod +x scripts/setup_postgres.sh
   ./scripts/setup_postgres.sh
   ```
   
   This script will:
   - ✅ Check Docker installation and status
   - ✅ Start PostgreSQL container with correct configuration
   - ✅ Create main and test databases
   - ✅ Verify connectivity
   - ✅ Provide helpful container management commands
   
   **Alternative - Manual PostgreSQL:**
   ```bash
   # macOS with Homebrew
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo systemctl start postgresql
   ```

6. **Verify your environment** ⭐ _New!_
   ```bash
   # Run comprehensive environment check
   python scripts/check_environment.py
   ```
   
   This intelligent script verifies:
   - ✅ Python version compatibility (3.11+)
   - ✅ Required packages installation
   - ✅ Database connectivity and health
   - ✅ Docker services status
   - ✅ Environment configuration
   - ✅ Provides specific fix suggestions for any issues

7. **Run database migrations**
   ```bash
   # Apply database schema migrations
   PYTHONPATH=. alembic upgrade head
   ```

8. **Start the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   🎉 **Success!** Your API is now running at http://localhost:8000

#
 **Access the application**
   - **🏠 Landing Page**: http://localhost:8000/ (smart API overview with task status)
   - **📚 API Base**: http://localhost:8000/api (all endpoints are under this path)
   - **📖 Swagger UI**: http://localhost:8000/docs (interactive API documentation)
   - **📋 ReDoc**: http://localhost:8000/redoc (alternative documentation)
   - **💚 Health Check**: http://localhost:8000/api/health (system status)
   
   ✨ **Smart Start**: Visit the root URL (http://localhost:8000/) to get personalized API guidance based on your current task count!

### 🚀 Quick Test Commands

Once your API is running, test it immediately:

```bash
# Check API health
curl http://localhost:8000/api/health

# Create your first task
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test the API",
    "description": "Verify the task management API is working",
    "status": "pending",
    "priority": "high"
  }'

# List all tasks
curl http://localhost:8000/api/tasks
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME=Task Management API
APP_VERSION=1.0.0
DEBUG=true

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/database_name
DATABASE_URL_SYNC=postgresql+psycopg2://username:password@localhost:5432/database_name


# PostgreSQL Database Settings
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=database_name
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Database Configuration

The application uses PostgreSQL by default. The database connection is configured in `/task_manager/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Important URLs
- **API Landing Page**: `http://localhost:8000/` - Intelligent landing page with task status and API information
- **API Base**: `http://localhost:8000/api` - All API endpoints are under this path
- **Documentation**: `http://localhost:8000/docs` - Interactive Swagger UI
- **ReDoc**: `http://localhost:8000/redoc` - Alternative API documentation

✨ **Smart Root Endpoint**: The root URL (`/`) provides:
- **Task Status**: Shows current task count and suggests next actions
- **API Information**: Complete endpoint reference and base URLs
- **Getting Started**: Example requests and quick start guide
- **Environment Info**: Current configuration and security settings

### Security Features
- **Rate Limiting**: API endpoints are protected with rate limiting (10-60 requests/minute per endpoint)
- **Security Headers**: Comprehensive security headers including XSS protection, CORS control, and CSP
- **CORS Protection**: Environment-controlled CORS origins (no wildcard origins in production)
- **Request Size Limits**: 1MB maximum request body size
- **Production Security**: Debug mode disabled and API docs hidden in production environments


### Core Endpoints

#### 1. Health Check
Monitor API and database status.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

#### 2. List Tasks
Retrieve tasks with filtering, sorting, and pagination.

```http
GET /api/tasks?status=pending&priority=high&sort_by=due_date&order=asc&page=1&limit=10
```

**Query Parameters:**
| Parameter | Type | Description | Options |
|-----------|------|-------------|---------|
| `status` | string | Filter by status | `pending`, `in_progress`, `completed` |
| `priority` | string | Filter by priority | `low`, `medium`, `high` |
| `sort_by` | string | Sort field | `created_at`, `due_date`, `priority` |
| `order` | string | Sort order | `asc`, `desc` |
| `page` | integer | Page number (default: 1) | ≥ 1 |
| `limit` | integer | Items per page (default: 10) | 1-100 |

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete API documentation",
      "description": "Write comprehensive API documentation",
      "status": "pending",
      "priority": "high",
      "due_date": "2024-01-20T23:59:59Z",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 10,
  "pages": 5
}
```

#### 3. Get Task by ID
Retrieve a specific task.

```http
GET /api/tasks/{task_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete API documentation",
  "description": "Write comprehensive API documentation",
  "status": "pending",
  "priority": "high",
  "due_date": "2024-01-20T23:59:59Z",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

#### 4. Create Task
Create a new task.

```http
POST /api/tasks
Content-Type: application/json

{
  "title": "Complete API documentation",
  "description": "Write comprehensive API documentation",
  "status": "pending",
  "priority": "high",
  "due_date": "2024-01-20T23:59:59Z"
}
```

**Validation Rules:**
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters
- `status`: Required, one of: `pending`, `in_progress`, `completed`
- `priority`: Required, one of: `low`, `medium`, `high`
- `due_date`: Optional, ISO 8601 format, must be in the future

#### 5. Update Task
Update an existing task.

```http
PUT /api/tasks/{task_id}
Content-Type: application/json

{
  "title": "Updated task title",
  "status": "in_progress",
  "priority": "medium"
}
```

#### 6. Delete Task
Delete a task by ID.

```http
DELETE /api/tasks/{task_id}
```

**Response:** `204 No Content`

### Example cURL Commands

**Create a task:**
```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for the API",
    "status": "pending",
    "priority": "high",
    "due_date": "2024-01-30T23:59:59Z"
  }'
```

**List tasks with filtering:**
```bash
curl -X GET "http://localhost:8000/api/tasks?status=pending&priority=high&page=1&limit=10"
```

**Update a task:**
```bash
curl -X PUT "http://localhost:8000/api/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "medium"
  }'
```

## 🗄️ Database Setup

### Manual PostgreSQL Setup

#### Option 1: Docker (Recommended)

1. **Install Docker**
   ```bash
   # macOS with Homebrew
   brew install --cask docker
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose
   ```

2. **Start PostgreSQL container**
   ```bash
   docker run -d \
     --name postgres-db \
     -e POSTGRES_USER=taskuser \
     -e POSTGRES_PASSWORD=taskpass \
     -e POSTGRES_DB=taskdb \
     -p 5432:5432 \
     postgres:15
   ```

3. **Create test database**
   ```bash
   docker exec postgres-db psql -U taskuser -d taskdb -c "CREATE DATABASE taskdb_test;"
   ```

4. **Run database migrations**
   ```bash
   PYTHONPATH=. alembic upgrade head
   ```

#### Option 2: Local PostgreSQL Installation

1. **Install PostgreSQL**
   ```bash
   # macOS with Homebrew
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create database and user**
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   CREATE USER taskuser WITH PASSWORD 'taskpass';
   CREATE DATABASE taskdb OWNER taskuser;
   GRANT ALL PRIVILEGES ON DATABASE taskdb TO taskuser;
   \q
   ```

3. **Run database migrations**
   ```bash
   PYTHONPATH=. alembic upgrade head
   ```

### Using the Automated Setup Script (Docker-based) ⭐

For the best experience, use our automated setup script:

```bash
chmod +x scripts/setup_postgres.sh
./scripts/setup_postgres.sh
```

**What this script does:**
- ✅ Validates Docker installation and status
- ✅ Manages existing PostgreSQL containers intelligently
- ✅ Starts PostgreSQL 15 with optimal configuration
- ✅ Creates both main (`taskdb`) and test (`taskdb_test`) databases
- ✅ Tests connectivity and provides troubleshooting info
- ✅ Provides container management commands for ongoing use

**Benefits:**
- 🚀 Zero manual configuration required
- 🐳 Uses Docker for consistent, isolated setup
- 🔒 Secure default credentials that work out-of-the-box
- 📋 No local PostgreSQL installation needed
- 🛠️ Built-in error handling and helpful diagnostics

### Database Migrations

The project uses **Alembic** for database schema management and version control. Alembic provides robust migration capabilities with automatic schema detection and rollback support.

#### Setup Requirements

Ensure you have the necessary dependencies:
- `psycopg2-binary` for synchronous database operations (already included in requirements.txt)
- PostgreSQL database connection configured

#### Migration Commands

**Create a new migration** (auto-detects model changes):
```bash
# Set PYTHONPATH to ensure app modules are found
PYTHONPATH=. alembic revision --autogenerate -m "Add new field to task"
```

**Apply migrations** (run pending migrations):
```bash
PYTHONPATH=. alembic upgrade head
```

**Apply specific migration**:
```bash
PYTHONPATH=. alembic upgrade <revision_id>
```

**Rollback to previous migration**:
```bash
PYTHONPATH=. alembic downgrade -1
```

**Rollback to specific migration**:
```bash
PYTHONPATH=. alembic downgrade <revision_id>
```

**View migration history**:
```bash
PYTHONPATH=. alembic history --verbose
```

**Check current migration status**:
```bash
PYTHONPATH=. alembic current
```

**Show pending migrations**:
```bash
PYTHONPATH=. alembic heads
```

#### Migration Workflow

1. **Make model changes** in `app/models/task.py`
2. **Generate migration**:
   ```bash
   PYTHONPATH=. alembic revision --autogenerate -m "Descriptive message"
   ```
3. **Review generated migration** in `alembic/versions/`
4. **Apply migration**:
   ```bash
   PYTHONPATH=. alembic upgrade head
   ```
5. **Verify database schema** matches your models

#### Important Notes

- **Always use PYTHONPATH=.** to ensure alembic can import your app modules
- **Review auto-generated migrations** before applying them - alembic may not detect all changes
- **Use descriptive migration messages** for easier tracking
- **Test migrations** on a copy of production data before applying to production
- **Backup your database** before running migrations in production

#### Configuration Files

- **`alembic.ini`**: Main configuration file with database URL and logging settings
- **`alembic/env.py`**: Environment setup for migrations, configured for both async (FastAPI) and sync (migrations) database operations
- **`alembic/versions/`**: Directory containing all migration files

#### Troubleshooting Migrations

**Migration fails with import errors**:
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
PYTHONPATH=. alembic current
```

**Database not in sync with migrations**:
```bash
# Check current status
PYTHONPATH=. alembic current
PYTHONPATH=. alembic history

# Force stamp to specific revision (use with caution)
PYTHONPATH=. alembic stamp head
```

**Reset migrations completely** (development only):
```bash
PYTHONPATH=. alembic downgrade base
PYTHONPATH=. alembic upgrade head
```

## 🐳 Docker Deployment

### Development Environment

1. **Start all services**
   ```bash
   docker-compose up --build
   ```

2. **Run in background**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs**
   ```bash
   docker-compose logs -f api
   docker-compose logs -f postgres
   ```

4. **Stop services**
   ```bash
   docker-compose down
   ```

### Production Deployment

1. **Build production image**
   ```bash
   docker build -t task-api:prod .
   ```

2. **Run with production settings**
   ```bash
   docker run -d \
     --name task-api \
     -p 8000:8000 \
     -e DATABASE_URL=postgresql://user:pass@host:5432/db \
     -e DEBUG=false \
     task-api:prod
   ```

### Docker Commands Reference

```bash
# View running containers
docker-compose ps

# Execute commands in container
docker-compose exec api bash
docker-compose exec postgres psql -U taskuser -d taskdb

# View container logs
docker-compose logs api

# Rebuild specific service
docker-compose up --build api

# Clean up
docker-compose down -v  # Remove volumes too
docker system prune     # Clean up unused resources
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_endpoints.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints and database interactions
- **Service Tests**: Test business logic layer

### Test Configuration

Tests use a separate test database configured in `/Users/humancodex/Developer/integrations/task_manager/tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Test database setup
engine = create_engine("postgresql://test_user:test_pass@localhost/test_db")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

### Running Tests in Docker

```bash
# Run tests in Docker container
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app
```

## 🔄 Development Workflow

### Setting up Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run code formatting**
   ```bash
   black app/ tests/
   flake8 app/ tests/
   mypy app/
   ```

### Development Commands

```bash
# Start development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run linting
flake8 app/ tests/

# Format code
black app/ tests/

# Type checking
mypy app/

# Run tests with coverage
pytest --cov=app --cov-report=html

# Generate migration
PYTHONPATH=. alembic revision --autogenerate -m "Description"

# Apply migrations  
PYTHONPATH=. alembic upgrade head
```

### Code Quality Tools

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks for code quality

## 📁 Project Structure

```
task_manager/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection and session
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py            # SQLAlchemy Task model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py            # Pydantic request/response schemas
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py    # Shared dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py         # API router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── tasks.py   # Task CRUD endpoints
│   │           └── health.py  # Health check endpoint
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py    # Business logic layer
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── task_repository.py # Data access layer
│   │
│   └── middleware/
│       ├── __init__.py
│       └── logging.py         # Request/response logging
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test fixtures and configuration
│   ├── test_endpoints.py      # API endpoint tests
│   ├── test_services.py       # Service layer tests
│   └── test_models.py         # Model tests
│
├── alembic/
│   ├── versions/              # Database migration files
│   ├── env.py                 # Alembic environment configuration
│   └── script.py.mako         # Migration template
│
├── scripts/
│   ├── init_db.py            # Database initialization script
│   └── setup_postgres.sh     # PostgreSQL setup script
│
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── alembic.ini               # Alembic configuration
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker image definition
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # Project documentation
```

### Key Components

**Models (`app/models/`)**: SQLAlchemy ORM models defining database schema
**Schemas (`app/schemas/`)**: Pydantic models for request/response validation
**Services (`app/services/`)**: Business logic layer
**Repositories (`app/repositories/`)**: Data access layer with database operations
**API (`app/api/`)**: FastAPI route definitions and endpoint handlers
**Middleware (`app/middleware/`)**: Custom middleware for logging, CORS, etc.

## 🤝 Contributing

### Development Process

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests for new functionality**
5. **Run the test suite**
   ```bash
   pytest --cov=app
   ```
6. **Run code quality checks**
   ```bash
   black app/ tests/
   flake8 app/ tests/
   mypy app/
   ```
7. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
8. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
9. **Open a Pull Request**

### Code Style Guidelines

- Follow **PEP 8** Python style guide
- Use **Black** for automatic code formatting
- Write comprehensive **docstrings** for all functions and classes
- Maintain **test coverage** above 90%
- Use **type hints** throughout the codebase
- Write **descriptive commit messages**

### Pull Request Guidelines

- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass
- Follow the existing code style
- Write clear, descriptive commit messages

## 🔧 Troubleshooting

### 🚨 Quick Diagnostic

Before diving into specific issues, run our comprehensive diagnostic:

```bash
# Run the environment checker for instant diagnosis
python scripts/check_environment.py

# Check Docker services status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test API health
curl http://localhost:8000/api/health
```

### Common Issues

#### 1. Database Connection Issues

**Problem**: `FATAL: password authentication failed` or connection refused

**Quick Fix** (Docker setup):
```bash
# Restart PostgreSQL container with correct credentials
docker stop postgres-db
docker rm postgres-db
./scripts/setup_postgres.sh
```

**Manual Fix** (Local PostgreSQL):
```bash
# Check PostgreSQL is running
brew services list | grep postgresql  # macOS
systemctl status postgresql           # Linux

# Reset password (if using local PostgreSQL)
sudo -u postgres psql
ALTER USER taskuser PASSWORD 'taskpass';
```

**Environment Check**:
```bash
# Verify database URL in .env file
cat .env | grep DATABASE_URL

# Should be: postgresql://taskuser:taskpass@localhost:5432/taskdb
```

#### 2. Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`
**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

#### 3. Migration Issues

**Problem**: `Target database is not up to date`
**Solution**:
```bash
# Check current migration status
PYTHONPATH=. alembic current

# Upgrade to latest
PYTHONPATH=. alembic upgrade head

# If stuck, reset migrations
PYTHONPATH=. alembic downgrade base
PYTHONPATH=. alembic upgrade head
```

#### 4. Docker Issues

**Problem**: Container fails to start or connection issues

**Quick Diagnosis**:
```bash
# Check Docker status
docker info

# List all containers
docker ps -a

# Check PostgreSQL container logs
docker logs postgres-db
```

**Solutions**:
```bash
# Option 1: Restart PostgreSQL container
./scripts/setup_postgres.sh

# Option 2: Full Docker Compose restart
docker-compose down
docker-compose up --build

# Option 3: Clean slate (removes data!)
docker-compose down -v
docker system prune -f
docker-compose up --build

# Option 4: Manual PostgreSQL container management
docker stop postgres-db
docker rm postgres-db
docker run -d --name postgres-db \
  -e POSTGRES_USER=taskuser \
  -e POSTGRES_PASSWORD=taskpass \
  -e POSTGRES_DB=taskdb \
  -p 5432:5432 postgres:15
```

#### 5. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`
**Solution**:
```bash
# Ensure you're in the project root
pwd

# Activate virtual environment
source venv/bin/activate

# Install in development mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Performance Issues

#### Slow Database Queries

1. **Add database indexes**:
   ```sql
   CREATE INDEX idx_tasks_status ON tasks(status);
   CREATE INDEX idx_tasks_priority ON tasks(priority);
   CREATE INDEX idx_tasks_due_date ON tasks(due_date);
   ```

2. **Enable query logging**:
   ```python
   # In database.py
   engine = create_engine(DATABASE_URL, echo=True)
   ```

#### High Memory Usage

1. **Configure connection pooling**:
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_recycle=1800
   )
   ```

### Debugging Tips

1. **Enable debug logging**:
   ```env
   LOG_LEVEL=DEBUG
   DEBUG=true
   ```

2. **Use interactive debugger**:
   ```python
   import pdb; pdb.set_trace()
   ```

3. **Check application health**:
   ```bash
   curl http://localhost:8000/api/health
   ```

4. **Monitor database connections**:
   ```sql
   SELECT * FROM pg_stat_activity WHERE datname = 'taskdb';
   ```


---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Built for Morgan & Morgan team**
