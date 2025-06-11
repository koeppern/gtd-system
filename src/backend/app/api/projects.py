"""
Project API endpoints with GTD functionality
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_test_user_directly
from app.crud.project import crud_project
from app.models.user import User
from app.schemas.project import (
    ProjectResponse, 
    ProjectCreate, 
    ProjectUpdate, 
    ProjectFilters,
    ProjectWithStats
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    field_id: Optional[int] = Query(None, description="Filter by field ID"),
    is_done: Optional[bool] = Query(None, description="Filter by completion status"),
    do_this_week: Optional[bool] = Query(None, description="Filter by weekly scheduling"),
    has_tasks: Optional[bool] = Query(None, description="Filter by whether project has tasks"),
    include_deleted: bool = Query(False, description="Include soft-deleted projects"),
    search: Optional[str] = Query(None, description="Search in project name, keywords, etc."),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[ProjectResponse]:
    """
    Get projects for current user with optional filters
    
    Returns:
        List[ProjectResponse]: List of project data
    """
    filters = ProjectFilters(
        field_id=field_id,
        is_done=is_done,
        do_this_week=do_this_week,
        has_tasks=has_tasks,
        include_deleted=include_deleted,
        search=search
    )
    
    projects = await crud_project.get_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        filters=filters
    )
    return [ProjectResponse.from_model(project) for project in projects]


@router.get("/active", response_model=List[ProjectResponse])
async def get_active_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[ProjectResponse]:
    """
    Get active (not completed, not deleted) projects for current user
    
    Returns:
        List[ProjectResponse]: List of active project data
    """
    projects = await crud_project.get_active_projects(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return [ProjectResponse.from_model(project) for project in projects]


@router.get("/weekly", response_model=List[ProjectResponse])
async def get_weekly_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[ProjectResponse]:
    """
    Get projects scheduled for this week
    
    Returns:
        List[ProjectResponse]: List of weekly project data
    """
    projects = await crud_project.get_weekly_projects(
        db=db,
        user_id=current_user.id
    )
    return [ProjectResponse.from_model(project) for project in projects]


@router.get("/by-field/{field_id}", response_model=List[ProjectResponse])
async def get_projects_by_field(
    field_id: int,
    include_completed: bool = Query(False, description="Include completed projects"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[ProjectResponse]:
    """
    Get projects in a specific field
    
    Args:
        field_id: Field ID
        include_completed: Include completed projects
        
    Returns:
        List[ProjectResponse]: List of project data
    """
    projects = await crud_project.get_projects_by_field(
        db=db,
        user_id=current_user.id,
        field_id=field_id,
        include_completed=include_completed
    )
    return [ProjectResponse.from_model(project) for project in projects]


@router.get("/search", response_model=List[ProjectResponse])
async def search_projects(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[ProjectResponse]:
    """
    Search projects by name, keywords, and content
    
    Args:
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[ProjectResponse]: List of matching project data
    """
    projects = await crud_project.search_projects(
        db=db,
        user_id=current_user.id,
        query=query,
        skip=skip,
        limit=limit
    )
    return [ProjectResponse.from_model(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> ProjectResponse:
    """
    Get project by ID
    
    Args:
        project_id: Project ID
        
    Returns:
        ProjectResponse: Project data
    """
    project = await crud_project.get(db=db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return ProjectResponse.from_model(project)


@router.get("/{project_id}/with-stats", response_model=ProjectWithStats)
async def get_project_with_stats(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> ProjectWithStats:
    """
    Get project with task statistics
    
    Args:
        project_id: Project ID
        
    Returns:
        ProjectWithStats: Project data with task statistics
    """
    project_data = await crud_project.get_project_with_task_stats(
        db=db, 
        project_id=project_id
    )
    if not project_data or project_data["project"].user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Convert project model to dict and merge with stats
    project_dict = ProjectResponse.from_model(project_data["project"]).model_dump()
    project_dict.update({
        "task_count": project_data["task_count"],
        "completed_tasks": project_data["completed_tasks"],
        "pending_tasks": project_data["pending_tasks"],
        "high_priority_tasks": project_data["high_priority_tasks"],
        "overdue_tasks": project_data["overdue_tasks"],
        "completion_percentage": project_data["completion_percentage"]
    })
    
    return ProjectWithStats(**project_dict)


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_create: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> ProjectResponse:
    """
    Create a new project
    
    Args:
        project_create: Project creation data
        
    Returns:
        ProjectResponse: Created project data
    """
    # Set user_id from current user
    project_data = project_create.model_dump()
    project_data["user_id"] = current_user.id
    
    # Recreate with user_id
    project_create_with_user = ProjectCreate(**project_data)
    
    project = await crud_project.create(db=db, obj_in=project_create_with_user)
    return ProjectResponse.from_model(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> ProjectResponse:
    """
    Update a project
    
    Args:
        project_id: Project ID
        project_update: Project update data
        
    Returns:
        ProjectResponse: Updated project data
    """
    project = await crud_project.get(db=db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    updated_project = await crud_project.update(
        db=db, 
        db_obj=project, 
        obj_in=project_update
    )
    return ProjectResponse.from_model(updated_project)


@router.post("/{project_id}/complete", response_model=ProjectResponse)
async def complete_project(
    project_id: int,
    auto_complete_tasks: bool = Query(False, description="Also complete all active tasks"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> ProjectResponse:
    """
    Mark a project as completed
    
    Args:
        project_id: Project ID
        auto_complete_tasks: Also complete all active tasks in the project
        
    Returns:
        ProjectResponse: Completed project data
    """
    project = await crud_project.get(db=db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.done_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is already completed"
        )
    
    completed_project = await crud_project.complete_project(
        db=db,
        project=project,
        auto_complete_tasks=auto_complete_tasks
    )
    return ProjectResponse.from_model(completed_project)


@router.post("/{project_id}/reopen", response_model=ProjectResponse)
async def reopen_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> ProjectResponse:
    """
    Reopen a completed project
    
    Args:
        project_id: Project ID
        
    Returns:
        ProjectResponse: Reopened project data
    """
    project = await crud_project.get(db=db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if not project.done_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not completed"
        )
    
    reopened_project = await crud_project.reopen_project(db=db, project=project)
    return ProjectResponse.from_model(reopened_project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the project"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Delete a project (soft delete by default)
    
    Args:
        project_id: Project ID
        hard_delete: Permanently delete if True, soft delete if False
        
    Returns:
        dict: Success message
    """
    project = await crud_project.get(db=db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await crud_project.delete(db=db, id=project_id, hard_delete=hard_delete)
    
    action = "permanently deleted" if hard_delete else "soft deleted"
    return {"message": f"Project {action} successfully"}


@router.post("/{project_id}/restore", response_model=ProjectResponse)
async def restore_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> ProjectResponse:
    """
    Restore a soft-deleted project
    
    Args:
        project_id: Project ID
        
    Returns:
        ProjectResponse: Restored project data
    """
    project = await crud_project.restore(db=db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or not deleted"
        )
    
    return ProjectResponse.from_model(project)