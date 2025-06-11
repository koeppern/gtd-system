"""
Search API endpoints - full-text search across projects and tasks
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_test_user_directly
from app.crud.project import crud_project
from app.crud.task import crud_task
from app.models.user import User
from app.schemas.project import ProjectResponse
from app.schemas.task import TaskResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
async def search_all(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    include_completed: bool = Query(False, description="Include completed items"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Search across all projects and tasks
    
    Args:
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_completed: Include completed items
        
    Returns:
        Dict: Search results with projects and tasks
    """
    # Calculate limits for each type (split the total limit)
    project_limit = limit // 2
    task_limit = limit - project_limit
    
    # Search projects
    projects = await crud_project.search_projects(
        db=db,
        user_id=current_user.id,
        query=query,
        skip=skip // 2,
        limit=project_limit
    )
    
    # Filter completed projects if not requested
    if not include_completed:
        projects = [p for p in projects if not p.done_at]
    
    # Search tasks
    tasks = await crud_task.search_tasks(
        db=db,
        user_id=current_user.id,
        query=query,
        skip=skip // 2,
        limit=task_limit
    )
    
    # Filter completed tasks if not requested
    if not include_completed:
        tasks = [t for t in tasks if not t.done_at]
    
    return {
        "query": query,
        "total_results": len(projects) + len(tasks),
        "projects": {
            "count": len(projects),
            "results": [ProjectResponse.from_model(project) for project in projects]
        },
        "tasks": {
            "count": len(tasks),
            "results": [TaskResponse.from_model(task) for task in tasks]
        }
    }


@router.get("/projects")
async def search_projects(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    include_completed: bool = Query(False, description="Include completed projects"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Search projects only
    
    Args:
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_completed: Include completed projects
        
    Returns:
        Dict: Project search results
    """
    projects = await crud_project.search_projects(
        db=db,
        user_id=current_user.id,
        query=query,
        skip=skip,
        limit=limit
    )
    
    # Filter completed projects if not requested
    if not include_completed:
        projects = [p for p in projects if not p.done_at]
    
    return {
        "query": query,
        "count": len(projects),
        "results": [ProjectResponse.from_model(project) for project in projects]
    }


@router.get("/tasks")
async def search_tasks(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    include_completed: bool = Query(False, description="Include completed tasks"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Search tasks only
    
    Args:
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_completed: Include completed tasks
        
    Returns:
        Dict: Task search results
    """
    tasks = await crud_task.search_tasks(
        db=db,
        user_id=current_user.id,
        query=query,
        skip=skip,
        limit=limit
    )
    
    # Filter completed tasks if not requested
    if not include_completed:
        tasks = [t for t in tasks if not t.done_at]
    
    return {
        "query": query,
        "count": len(tasks),
        "results": [TaskResponse.from_model(task) for task in tasks]
    }


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Search query prefix"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, List[str]]:
    """
    Get search suggestions based on query prefix
    
    Args:
        query: Search query prefix
        limit: Maximum number of suggestions
        
    Returns:
        Dict: Search suggestions
    """
    # Search for projects and tasks with the query prefix
    projects = await crud_project.search_projects(
        db=db,
        user_id=current_user.id,
        query=query,
        skip=0,
        limit=limit // 2
    )
    
    tasks = await crud_task.search_tasks(
        db=db,
        user_id=current_user.id,
        query=query,
        skip=0,
        limit=limit // 2
    )
    
    # Extract unique suggestions from project and task names
    suggestions = set()
    
    # Add project names and keywords
    for project in projects:
        if project.project_name:
            # Add full name if it contains the query
            if query.lower() in project.project_name.lower():
                suggestions.add(project.project_name)
            
            # Add individual words from the name
            words = project.project_name.split()
            for word in words:
                if len(word) > 2 and query.lower() in word.lower():
                    suggestions.add(word)
        
        # Add keywords if available
        if project.keywords:
            keywords = project.keywords.split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                if len(keyword) > 2 and query.lower() in keyword.lower():
                    suggestions.add(keyword)
    
    # Add task names
    for task in tasks:
        if task.task_name:
            # Add full name if it contains the query
            if query.lower() in task.task_name.lower():
                suggestions.add(task.task_name)
            
            # Add individual words from the name
            words = task.task_name.split()
            for word in words:
                if len(word) > 2 and query.lower() in word.lower():
                    suggestions.add(word)
    
    # Convert to sorted list and limit results
    suggestions_list = sorted(list(suggestions))[:limit]
    
    return {
        "suggestions": suggestions_list
    }


@router.get("/recent")
async def get_recent_items(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recent items"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Get recently updated projects and tasks for quick access
    
    Args:
        limit: Maximum number of recent items
        
    Returns:
        Dict: Recently updated items
    """
    # Get recent projects (by updated_at)
    recent_projects = await crud_project.get_by_user(
        db=db,
        user_id=current_user.id,
        skip=0,
        limit=limit // 2
    )
    
    # Get recent tasks (by updated_at)
    recent_tasks = await crud_task.get_by_user(
        db=db,
        user_id=current_user.id,
        skip=0,
        limit=limit // 2
    )
    
    return {
        "recent_projects": [
            {
                "id": project.id,
                "name": project.project_name,
                "updated_at": project.updated_at,
                "is_completed": project.done_at is not None
            }
            for project in recent_projects[:5]
        ],
        "recent_tasks": [
            {
                "id": task.id,
                "name": task.task_name,
                "updated_at": task.updated_at,
                "is_completed": task.done_at is not None,
                "project_id": task.project_id
            }
            for task in recent_tasks[:5]
        ]
    }