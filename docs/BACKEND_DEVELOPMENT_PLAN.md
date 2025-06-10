# GTD Python Backend Development Plan

**Project:** GTD FastAPI Backend  
**Stack:** FastAPI + SQLAlchemy + PostgreSQL (Supabase) + Docker (Alpine) + Pytest  
**Deployment:** Render.com (später) / Localhost (initial)  

---

## 📋 Architecture Overview

```
gtd-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLAlchemy setup
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── field.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── common.py
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   ├── dashboard.py
│   │   └── search.py
│   ├── crud/                   # CRUD operations
│   │   ├── __init__.py
│   │   ├── project.py
│   │   └── task.py
│   └── core/                   # Core functionality
│       ├── __init__.py
│       ├── security.py         # JWT handling (future)
│       └── dependencies.py     # FastAPI dependencies
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_projects.py
│   ├── test_tasks.py
│   └── test_integration.py
├── cli/
│   └── test_client.py         # Console testing frontend
├── docker/
│   └── Dockerfile.alpine      # Alpine-based image
├── requirements.txt
├── requirements-dev.txt
├── docker-compose.yml
├── .env.example
├── pytest.ini
└── README.md
```

---

## 🎯 Sprint 1: Backend Foundation (Week 1-2)

### Task 1.1: Project Setup & Infrastructure
- [ ] Create FastAPI project structure
- [ ] Setup SQLAlchemy with async support
- [ ] Configure Alembic for migrations
- [ ] Create Docker Alpine image
- [ ] Setup docker-compose for local development
- [ ] Configure pytest with fixtures
- [ ] Setup pre-commit hooks

**Files to create:**
```bash
# Basic setup
app/main.py
app/config.py
app/database.py
docker/Dockerfile.alpine
docker-compose.yml
requirements.txt
pytest.ini
.env.example
```

### Task 1.2: SQLAlchemy Models
- [ ] Create Base model with common fields
- [ ] User model (matching gtd_users)
- [ ] Project model (matching gtd_projects)
- [ ] Task model (matching gtd_tasks)
- [ ] Field model (matching gtd_fields)
- [ ] Define relationships between models
- [ ] Add model validators

**Models to implement:**
```python
# Base Model
- id, created_at, updated_at, deleted_at

# User Model
- id (UUID), email_address, first_name, last_name

# Project Model  
- id, user_id, project_name, done_at, field_id, etc.

# Task Model
- id, user_id, task_name, project_id, done_at, etc.
```

### Task 1.3: Pydantic Schemas
- [ ] Base schemas with common fields
- [ ] Request schemas (Create, Update)
- [ ] Response schemas with relationships
- [ ] Pagination schemas
- [ ] Error response schemas

**Schemas structure:**
```python
# Project Schemas
- ProjectBase
- ProjectCreate
- ProjectUpdate
- ProjectResponse
- ProjectListResponse

# Task Schemas
- TaskBase
- TaskCreate
- TaskUpdate
- TaskResponse
- TaskListResponse
```

### Task 1.4: CRUD Operations
- [ ] Generic CRUD base class
- [ ] Project CRUD with filters
- [ ] Task CRUD with GTD logic
- [ ] Soft delete implementation
- [ ] Query builders for complex filters

**CRUD methods:**
```python
# Base CRUD
- get, get_multi, create, update, delete

# Project CRUD
- get_active_projects
- complete_project

# Task CRUD
- get_tasks_today
- get_tasks_this_week
- complete_task
```

### Task 1.5: API Endpoints Implementation
- [ ] Projects endpoints (CRUD)
- [ ] Tasks endpoints (CRUD)
- [ ] Dashboard endpoint
- [ ] Search endpoint
- [ ] Quick-add endpoint
- [ ] Error handling middleware
- [ ] Request validation

**Endpoints to implement:**
```python
# Projects
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PUT    /api/projects/{id}
DELETE /api/projects/{id}
POST   /api/projects/{id}/complete
GET    /api/projects/active

# Tasks
GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/{id}
PUT    /api/tasks/{id}
DELETE /api/tasks/{id}
POST   /api/tasks/{id}/complete
GET    /api/tasks/today
GET    /api/tasks/week

# Dashboard & Search
GET    /api/dashboard
GET    /api/search?q={query}
POST   /api/quick-add
```

### Task 1.6: Testing Infrastructure
- [ ] Pytest fixtures for database
- [ ] Factory pattern for test data
- [ ] Unit tests for CRUD operations
- [ ] Integration tests for endpoints
- [ ] Test database isolation
- [ ] Coverage reporting setup

**Test categories:**
```python
# Unit Tests
- Model validation tests
- CRUD operation tests
- Business logic tests

# Integration Tests
- API endpoint tests
- Database transaction tests
- Error handling tests
```

### Task 1.7: Console Testing Client
- [ ] CLI menu system
- [ ] CRUD operations via console
- [ ] Pretty print responses
- [ ] Save/load test scenarios
- [ ] Performance timing

**CLI Features:**
```python
# Console Client
- Interactive menu
- List/Create/Update/Delete operations
- Search functionality
- Bulk operations testing
- Response formatting
```

### Task 1.8: Docker & Deployment Prep
- [ ] Alpine-based Dockerfile
- [ ] Multi-stage build optimization
- [ ] Health check endpoint
- [ ] Environment variable management
- [ ] Logging configuration
- [ ] Production settings

**Docker configuration:**
```dockerfile
# Alpine Linux base
FROM python:3.11-alpine

# Security and optimization
- Non-root user
- Minimal dependencies
- Layer caching
```

---

## 🎯 Sprint 2: Authentication & Advanced Features (Week 3-4)

### Task 2.1: Authentication Setup
- [ ] Supabase JWT validation
- [ ] FastAPI security dependencies
- [ ] User context extraction
- [ ] Protected route decorators
- [ ] CORS configuration

### Task 2.2: Advanced GTD Features
- [ ] Contexts support
- [ ] Areas of responsibility
- [ ] Recurring tasks
- [ ] Batch operations
- [ ] Export functionality

### Task 2.3: Performance & Monitoring
- [ ] Query optimization
- [ ] Caching layer
- [ ] APM integration
- [ ] Error tracking
- [ ] Health metrics

---

## 📊 Success Criteria

### Sprint 1 Completion
- [ ] All CRUD endpoints working
- [ ] 90%+ test coverage
- [ ] Docker image < 100MB
- [ ] All endpoints < 200ms response time
- [ ] Console client fully functional
- [ ] API documentation generated

### Technical Requirements
- [ ] Python 3.11+
- [ ] SQLAlchemy 2.0+
- [ ] FastAPI 0.100+
- [ ] PostgreSQL compatible
- [ ] Alpine Linux based
- [ ] Type hints throughout

---

## 🚀 Quick Start Commands

```bash
# Local Development
docker-compose up -d
pytest
python cli/test_client.py

# Docker Build
docker build -f docker/Dockerfile.alpine -t gtd-backend .

# Run Tests
pytest -v --cov=app tests/

# Database Migrations
alembic upgrade head
```

---

## 📝 Notes & Decisions

### Architecture Decisions
1. **SQLAlchemy over raw SQL:** Type safety and better Python integration
2. **Alpine Linux:** Minimal image size for Render.com deployment
3. **Async SQLAlchemy:** Better performance for I/O operations
4. **Separate CRUD layer:** Clean separation of concerns

### Future Considerations
- [ ] GraphQL API addition
- [ ] WebSocket support for real-time
- [ ] Redis caching layer
- [ ] Celery for background tasks
- [ ] Multi-tenancy support

---

## 🔗 Dependencies

### Production
```
fastapi==0.109.0
sqlalchemy==2.0.25
asyncpg==0.29.0
pydantic==2.5.3
python-dotenv==1.0.0
uvicorn==0.25.0
python-jose==3.3.0
httpx==0.26.0
```

### Development
```
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
black==23.12.1
ruff==0.1.11
pre-commit==3.6.0
faker==22.0.0
```

---

*Backend Development Plan v1.0 - Ready for implementation*