"""
Task API endpoints with GTD workflow functionality
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_test_user_directly
from app.crud.task import crud_task
from app.models.user import User
from app.schemas.task import (
    TaskResponse, 
    TaskCreate, 
    TaskUpdate, 
    TaskFilters,
    TaskStats
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    field_id: Optional[int] = Query(None, description="Filter by field ID"),
    is_done: Optional[bool] = Query(None, description="Filter by completion status"),
    do_today: Optional[bool] = Query(None, description="Filter by today's tasks"),
    do_this_week: Optional[bool] = Query(None, description="Filter by weekly tasks"),
    is_reading: Optional[bool] = Query(None, description="Filter by reading tasks"),
    wait_for: Optional[bool] = Query(None, description="Filter by waiting tasks"),
    postponed: Optional[bool] = Query(None, description="Filter by postponed tasks"),
    reviewed: Optional[bool] = Query(None, description="Filter by reviewed tasks"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by exact priority"),
    priority_min: Optional[int] = Query(None, ge=1, le=5, description="Filter by minimum priority"),
    priority_max: Optional[int] = Query(None, ge=1, le=5, description="Filter by maximum priority"),
    due_date: Optional[date] = Query(None, description="Filter by exact due date"),
    overdue: Optional[bool] = Query(None, description="Filter by overdue status"),
    include_deleted: bool = Query(False, description="Include soft-deleted tasks"),
    search: Optional[str] = Query(None, description="Search in task name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[TaskResponse]:
    """
    Get tasks for current user with comprehensive filters
    
    Returns:
        List[TaskResponse]: List of task data
    """
    filters = TaskFilters(
        project_id=project_id,
        field_id=field_id,
        is_done=is_done,
        do_today=do_today,
        do_this_week=do_this_week,
        is_reading=is_reading,
        wait_for=wait_for,
        postponed=postponed,
        reviewed=reviewed,
        priority=priority,
        priority_min=priority_min,
        priority_max=priority_max,
        due_date=due_date,
        overdue=overdue,
        include_deleted=include_deleted,
        search=search
    )
    
    tasks = await crud_task.get_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        filters=filters
    )
    return [TaskResponse.from_model(task) for task in tasks]


@router.get("/today", response_model=List[TaskResponse])
async def get_today_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[TaskResponse]:
    """
    Get tasks scheduled for today
    
    Returns:
        List[TaskResponse]: List of today's task data
    """
    tasks = await crud_task.get_today_tasks(db=db, user_id=current_user.id)
    return [TaskResponse.from_model(task) for task in tasks]


@router.get("/week", response_model=List[TaskResponse])
async def get_week_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[TaskResponse]:
    """
    Get tasks scheduled for this week
    
    Returns:
        List[TaskResponse]: List of this week's task data
    """
    tasks = await crud_task.get_week_tasks(db=db, user_id=current_user.id)
    return [TaskResponse.from_model(task) for task in tasks]


@router.get("/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[TaskResponse]:
    """
    Get overdue tasks
    
    Returns:
        List[TaskResponse]: List of overdue task data
    """
    tasks = await crud_task.get_overdue_tasks(db=db, user_id=current_user.id)
    return [TaskResponse.from_model(task) for task in tasks]


@router.get("/waiting", response_model=List[TaskResponse])
async def get_waiting_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[TaskResponse]:
    """
    Get tasks waiting for someone/something
    
    Returns:
        List[TaskResponse]: List of waiting task data
    """
    tasks = await crud_task.get_waiting_tasks(db=db, user_id=current_user.id)
    return [TaskResponse.from_model(task) for task in tasks]


@router.get("/reading", response_model=List[TaskResponse])
async def get_reading_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[TaskResponse]:
    """
    Get reading tasks
    
    Returns:
        List[TaskResponse]: List of reading task data
    """
    tasks = await crud_task.get_reading_tasks(db=db, user_id=current_user.id)
    return [TaskResponse.from_model(task) for task in tasks]


@router.get("/stats", response_model=TaskStats)
async def get_task_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskStats:
    """
    Get comprehensive task statistics for current user
    
    Returns:
        TaskStats: Task statistics
    """
    stats = await crud_task.get_task_stats(db=db, user_id=current_user.id)
    return TaskStats(**stats)


@router.get("/by-project/{project_id}", response_model=List[TaskResponse])
async def get_tasks_by_project(
    project_id: int,
    include_completed: bool = Query(False, description="Include completed tasks"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[TaskResponse]:
    """
    Get tasks for a specific project
    
    Args:
        project_id: Project ID
        include_completed: Include completed tasks
        
    Returns:
        List[TaskResponse]: List of task data
    """
    tasks = await crud_task.get_tasks_by_project(
        db=db,
        project_id=project_id,
        include_completed=include_completed
    )
    # Filter by user ownership through project
    user_tasks = [task for task in tasks if task.user_id == current_user.id]
    return [TaskResponse.from_model(task) for task in user_tasks]


@router.get("/search", response_model=List[TaskResponse])
async def search_tasks(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[TaskResponse]:
    """
    Search tasks by name
    
    Args:
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[TaskResponse]: List of matching task data
    """
    tasks = await crud_task.search_tasks(
        db=db,
        user_id=current_user.id,
        query=query,
        skip=skip,
        limit=limit
    )
    return [TaskResponse.from_model(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Get task by ID
    
    Args:
        task_id: Task ID
        
    Returns:
        TaskResponse: Task data
    """
    task = await crud_task.get(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return TaskResponse.from_model(task)


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_create: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Create a new task
    
    Args:
        task_create: Task creation data
        
    Returns:
        TaskResponse: Created task data
    """
    # Set user_id from current user
    task_data = task_create.model_dump()
    task_data["user_id"] = current_user.id
    
    # Recreate with user_id
    task_create_with_user = TaskCreate(**task_data)
    
    task = await crud_task.create(db=db, obj_in=task_create_with_user)
    return TaskResponse.from_model(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Update a task
    
    Args:
        task_id: Task ID
        task_update: Task update data
        
    Returns:
        TaskResponse: Updated task data
    """
    task = await crud_task.get(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    updated_task = await crud_task.update(
        db=db, 
        db_obj=task, 
        obj_in=task_update
    )
    return TaskResponse.from_model(updated_task)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    completion_time: Optional[datetime] = Body(None, description="Optional completion timestamp"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Mark a task as completed
    
    Args:
        task_id: Task ID
        completion_time: Optional completion timestamp
        
    Returns:
        TaskResponse: Completed task data
    """
    task = await crud_task.get(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.done_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is already completed"
        )
    
    completed_task = await crud_task.complete_task(
        db=db,
        task=task,
        completion_time=completion_time
    )
    return TaskResponse.from_model(completed_task)


@router.post("/{task_id}/reopen", response_model=TaskResponse)
async def reopen_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Reopen a completed task
    
    Args:
        task_id: Task ID
        
    Returns:
        TaskResponse: Reopened task data
    """
    task = await crud_task.get(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not task.done_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not completed"
        )
    
    reopened_task = await crud_task.reopen_task(db=db, task=task)
    return TaskResponse.from_model(reopened_task)


@router.post("/{task_id}/schedule-today", response_model=TaskResponse)
async def schedule_task_for_today(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Schedule task for today
    
    Args:
        task_id: Task ID
        
    Returns:
        TaskResponse: Updated task data
    """
    task = await crud_task.get(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    updated_task = await crud_task.schedule_for_today(db=db, task=task)
    return TaskResponse.from_model(updated_task)


@router.post("/{task_id}/schedule-week", response_model=TaskResponse)
async def schedule_task_for_week(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Schedule task for this week
    
    Args:
        task_id: Task ID
        
    Returns:
        TaskResponse: Updated task data
    """
    task = await crud_task.get(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    updated_task = await crud_task.schedule_for_week(db=db, task=task)
    return TaskResponse.from_model(updated_task)


@router.post("/{task_id}/set-priority", response_model=TaskResponse)
async def set_task_priority(
    task_id: int,
    priority: int = Body(..., ge=1, le=5, description="Priority level (1-5)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Set task priority
    
    Args:
        task_id: Task ID
        priority: Priority level (1-5)
        
    Returns:
        TaskResponse: Updated task data
    """
    task = await crud_task.get(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    try:
        updated_task = await crud_task.set_priority(
            db=db,
            task=task,
            priority=priority
        )
        return TaskResponse.from_model(updated_task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bulk-complete")
async def bulk_complete_tasks(
    task_ids: List[int] = Body(..., description="List of task IDs to complete"),
    completion_time: Optional[datetime] = Body(None, description="Optional completion timestamp"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Bulk complete multiple tasks
    
    Args:
        task_ids: List of task IDs
        completion_time: Optional completion timestamp
        
    Returns:
        dict: Number of tasks completed
    """
    if not task_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task IDs list cannot be empty"
        )
    
    count = await crud_task.bulk_complete_tasks(
        db=db,
        task_ids=task_ids,
        user_id=current_user.id,
        completion_time=completion_time
    )
    
    return {"completed_count": count, "message": f"{count} tasks completed successfully"}


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the task"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Delete a task (soft delete by default)
    
    Args:
        task_id: Task ID
        hard_delete: Permanently delete if True, soft delete if False
        
    Returns:
        dict: Success message
    """
    task = await crud_task.get(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    await crud_task.delete(db=db, id=task_id, hard_delete=hard_delete)
    
    action = "permanently deleted" if hard_delete else "soft deleted"
    return {"message": f"Task {action} successfully"}


@router.post("/{task_id}/restore", response_model=TaskResponse)
async def restore_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Restore a soft-deleted task
    
    Args:
        task_id: Task ID
        
    Returns:
        TaskResponse: Restored task data
    """
    task = await crud_task.restore(db=db, id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not deleted"
        )
    
    return TaskResponse.from_model(task)