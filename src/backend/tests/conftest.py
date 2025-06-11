"""
Test configuration and fixtures for GTD backend tests
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Set test environment before importing app modules
os.environ["CONFIG_FILE"] = "test_config.yaml"
os.environ["PYTEST_CURRENT_TEST"] = "1"

# Add app directory to Python path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)

from app.main import app
from app.database import get_db
from app.models.base import Base
from app.crud.user import crud_user
from app.crud.field import crud_field
from app.crud.project import crud_project
from app.crud.task import crud_task
from app.schemas.user import UserCreate
from app.schemas.field import FieldCreate
from app.schemas.project import ProjectCreate
from app.schemas.task import TaskCreate
from app.schemas.common import TEST_USER_ID

# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")  
def client() -> TestClient:
    """Create a test client with isolated test database."""
    import asyncio
    
    # Since the app uses in-memory SQLite for tests, we need to create tables
    # The app will use the test database because CONFIG_FILE is set to test_config.yaml
    
    # Get a reference to the app's engine and create tables
    from app.database import engine as app_engine
    from app.models.base import Base
    
    async def create_tables():
        async with app_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    # Create tables in the test database
    asyncio.run(create_tables())
    
    # Create test client
    client = TestClient(app)
    
    yield client
    
    # Clean up by dropping tables
    async def drop_tables():
        async with app_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    asyncio.run(drop_tables())


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user_data = UserCreate(
        first_name="Test",
        last_name="User",
        email_address="test@example.com",
        is_active=True,
        email_verified=True
    )
    user = await crud_user.create(db=db_session, obj_in=user_data)
    return user


@pytest.fixture
async def test_field(db_session: AsyncSession):
    """Create a test field."""
    field_data = FieldCreate(
        name="Test Field",
        description="A test field for testing"
    )
    field = await crud_field.create(db=db_session, obj_in=field_data)
    return field


@pytest.fixture
async def test_project(db_session: AsyncSession, test_user, test_field):
    """Create a test project."""
    project_data = ProjectCreate(
        user_id=test_user.id,
        project_name="Test Project",
        field_id=test_field.id,
        keywords="test, project",
        do_this_week=False
    )
    project = await crud_project.create(db=db_session, obj_in=project_data)
    return project


@pytest.fixture
async def test_task(db_session: AsyncSession, test_user, test_field, test_project):
    """Create a test task."""
    task_data = TaskCreate(
        user_id=test_user.id,
        task_name="Test Task",
        field_id=test_field.id,
        project_id=test_project.id,
        priority=3,
        do_today=False,
        do_this_week=False
    )
    task = await crud_task.create(db=db_session, obj_in=task_data)
    return task


@pytest.fixture
async def multiple_fields(db_session: AsyncSession):
    """Create multiple test fields."""
    fields = []
    field_names = ["Work", "Personal", "Learning", "Health", "Finance"]
    
    for name in field_names:
        field_data = FieldCreate(
            name=name,
            description=f"{name} related activities"
        )
        field = await crud_field.create(db=db_session, obj_in=field_data)
        fields.append(field)
    
    return fields


@pytest.fixture
async def multiple_projects(db_session: AsyncSession, test_user, multiple_fields):
    """Create multiple test projects."""
    projects = []
    project_names = [
        "Backend Development",
        "Frontend Design", 
        "Database Migration",
        "API Documentation",
        "Testing Suite"
    ]
    
    for i, name in enumerate(project_names):
        field_id = multiple_fields[i % len(multiple_fields)].id
        project_data = ProjectCreate(
            user_id=test_user.id,
            project_name=name,
            field_id=field_id,
            keywords=f"test, {name.lower()}",
            do_this_week=(i % 2 == 0)  # Alternate weekly scheduling
        )
        project = await crud_project.create(db=db_session, obj_in=project_data)
        projects.append(project)
    
    return projects


@pytest.fixture
async def multiple_tasks(db_session: AsyncSession, test_user, multiple_fields, multiple_projects):
    """Create multiple test tasks with various states."""
    tasks = []
    task_configs = [
        {"name": "Implement authentication", "priority": 1, "do_today": True, "project_idx": 0},
        {"name": "Design user interface", "priority": 2, "do_this_week": True, "project_idx": 1},
        {"name": "Write unit tests", "priority": 3, "do_today": False, "project_idx": 4},
        {"name": "Update documentation", "priority": 4, "is_reading": True, "project_idx": 3},
        {"name": "Review code changes", "priority": 5, "wait_for": True, "project_idx": 0},
        {"name": "Setup CI/CD pipeline", "priority": 2, "do_this_week": True, "project_idx": 2},
        {"name": "Performance optimization", "priority": 1, "postponed": True, "project_idx": 0},
        {"name": "User feedback analysis", "priority": 3, "is_reading": True, "project_idx": 1},
    ]
    
    for i, config in enumerate(task_configs):
        field_id = multiple_fields[i % len(multiple_fields)].id
        project_id = multiple_projects[config["project_idx"]].id
        
        task_data = TaskCreate(
            user_id=test_user.id,
            task_name=config["name"],
            field_id=field_id,
            project_id=project_id,
            priority=config.get("priority"),
            do_today=config.get("do_today", False),
            do_this_week=config.get("do_this_week", False),
            is_reading=config.get("is_reading", False),
            wait_for=config.get("wait_for", False),
            postponed=config.get("postponed", False)
        )
        task = await crud_task.create(db=db_session, obj_in=task_data)
        tasks.append(task)
    
    return tasks


@pytest.fixture
async def completed_items(db_session: AsyncSession, multiple_projects, multiple_tasks):
    """Complete some projects and tasks for testing."""
    # Complete some projects
    completed_projects = multiple_projects[:2]
    for project in completed_projects:
        await crud_project.complete_project(db=db_session, project=project)
    
    # Complete some tasks
    completed_tasks = multiple_tasks[:3]
    for task in completed_tasks:
        await crud_task.complete_task(db=db_session, task=task)
    
    return {
        "projects": completed_projects,
        "tasks": completed_tasks
    }


# Helper functions for tests
class TestHelpers:
    """Helper functions for tests."""
    
    @staticmethod
    def assert_response_success(response, expected_status=200):
        """Assert that response is successful."""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
        return response.json()
    
    @staticmethod
    def assert_response_error(response, expected_status):
        """Assert that response has expected error status."""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
        return response.json()
    
    @staticmethod
    def assert_user_data(data, expected_name="Test User"):
        """Assert user data structure."""
        assert "id" in data
        assert "name" in data
        assert "email_address" in data
        assert data["name"] == expected_name
        return data
    
    @staticmethod
    def assert_field_data(data, expected_name=None):
        """Assert field data structure."""
        assert "id" in data
        assert "name" in data
        assert "description" in data
        if expected_name:
            assert data["name"] == expected_name
        return data
    
    @staticmethod
    def assert_project_data(data, expected_name=None):
        """Assert project data structure."""
        assert "id" in data
        assert "project_name" in data
        assert "user_id" in data
        if expected_name:
            assert data["project_name"] == expected_name
        return data
    
    @staticmethod
    def assert_task_data(data, expected_name=None):
        """Assert task data structure."""
        assert "id" in data
        assert "task_name" in data
        assert "user_id" in data
        if expected_name:
            assert data["task_name"] == expected_name
        return data


@pytest.fixture
def helpers():
    """Provide test helper functions."""
    return TestHelpers