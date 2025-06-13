"""
Task API endpoints with Supabase direct connection
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from supabase import Client

from app.database import get_db
from app.config import get_settings

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
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
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get tasks from Supabase with filters
    
    Returns:
        List[dict]: List of task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Query tasks from Supabase
        query = supabase.table("gtd_tasks").select("*")
        
        # Add user filter for RLS compliance
        query = query.eq("user_id", default_user_id)
        
        # Add basic filters
        if not include_deleted:
            query = query.is_("deleted_at", "null")
        
        if project_id:
            query = query.eq("project_id", project_id)
        
        if field_id:
            query = query.eq("field_id", field_id)
        
        if is_done is not None:
            if is_done:
                query = query.not_.is_("done_at", "null")
            else:
                query = query.is_("done_at", "null")
        
        if do_today is not None:
            query = query.eq("do_today", str(do_today).lower())
        
        if do_this_week is not None:
            query = query.eq("do_this_week", str(do_this_week).lower())
        
        if is_reading is not None:
            query = query.eq("is_reading", str(is_reading).lower())
        
        if wait_for is not None:
            query = query.eq("wait_for", str(wait_for).lower())
        
        if postponed is not None:
            query = query.eq("postponed", str(postponed).lower())
        
        if reviewed is not None:
            query = query.eq("reviewed", str(reviewed).lower())
        
        if priority:
            query = query.eq("priority", priority)
        
        if priority_min:
            query = query.gte("priority", priority_min)
        
        if priority_max:
            query = query.lte("priority", priority_max)
        
        if due_date:
            query = query.eq("do_on_date", due_date.isoformat())  # Use actual column name
        
        if search:
            query = query.ilike("task_name", f"%{search}%")
        
        # Add pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute query
        result = query.execute()
        
        # Log the response for debugging
        print(f"Query returned {len(result.data) if result.data else 0} tasks")
        if not result.data:
            return []  # Return empty list if no data
        
        # Transform data to match expected format
        tasks = []
        for task in result.data:
            try:
                tasks.append({
                    "id": task.get("id"),
                    "name": task.get("task_name") or f"Task {task.get('id', 'Unknown')}",
                    "project_id": task.get("project_id"),
                    "field_id": task.get("field_id"),
                    "done_at": task.get("done_at"),
                    "do_today": task.get("do_today", False),
                    "do_this_week": task.get("do_this_week", False),
                    "is_reading": task.get("is_reading", False),
                    "wait_for": task.get("wait_for", False),
                    "postponed": task.get("postponed", False),
                    "reviewed": task.get("reviewed", False),
                    "priority": task.get("priority"),
                    "due_date": task.get("do_on_date"),  # Map do_on_date to due_date
                    "created_at": task.get("created_at"),
                    "updated_at": task.get("updated_at")
                })
            except Exception as task_error:
                print(f"Error processing task {task.get('id', 'unknown')}: {task_error}")
                print(f"Task data: {task}")
                raise
        
        return tasks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@router.get("/today")
async def get_today_tasks(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get tasks scheduled for today
    
    Returns:
        List[dict]: List of today's task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("do_today", "true").is_("deleted_at", "null").execute()
        
        if not result.data:
            return []
        
        return [{
            "id": task.get("id"),
            "name": task.get("task_name") or f"Task {task.get('id', 'Unknown')}",
            "project_id": task.get("project_id"),
            "field_id": task.get("field_id"),
            "done_at": task.get("done_at"),
            "do_today": task.get("do_today", True),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at")
        } for task in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch today's tasks: {str(e)}"
        )


@router.get("/week")
async def get_week_tasks(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get tasks scheduled for this week
    
    Returns:
        List[dict]: List of this week's task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("do_this_week", "true").is_("deleted_at", "null").execute()
        
        return [{
            "id": task["id"],
            "name": task["task_name"] or f"Task {task['id']}",
            "project_id": task["project_id"],
            "field_id": task["field_id"],
            "done_at": task["done_at"],
            "do_this_week": task["do_this_week"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"]
        } for task in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch week's tasks: {str(e)}"
        )


@router.get("/waiting")
async def get_waiting_tasks(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get tasks waiting for someone/something
    
    Returns:
        List[dict]: List of waiting task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("wait_for", "true").is_("deleted_at", "null").execute()
        
        return [{
            "id": task["id"],
            "name": task["task_name"] or f"Task {task['id']}",
            "project_id": task["project_id"],
            "field_id": task["field_id"],
            "done_at": task["done_at"],
            "wait_for": task["wait_for"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"]
        } for task in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch waiting tasks: {str(e)}"
        )


@router.get("/reading")
async def get_reading_tasks(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get reading tasks
    
    Returns:
        List[dict]: List of reading task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("is_reading", "true").is_("deleted_at", "null").execute()
        
        return [{
            "id": task["id"],
            "name": task["task_name"] or f"Task {task['id']}",
            "project_id": task["project_id"],
            "field_id": task["field_id"],
            "done_at": task["done_at"],
            "is_reading": task["is_reading"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"]
        } for task in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reading tasks: {str(e)}"
        )


@router.get("/stats")
async def get_task_stats(
    supabase: Client = Depends(get_db)
) -> dict:
    """
    Get comprehensive task statistics
    
    Returns:
        dict: Task statistics
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Get total tasks
        total_result = supabase.table("gtd_tasks").select("count", count="exact").eq("user_id", default_user_id).is_("deleted_at", "null").execute()
        total_tasks = total_result.count or 0
        
        # Get completed tasks
        completed_result = supabase.table("gtd_tasks").select("count", count="exact").eq("user_id", default_user_id).not_.is_("done_at", "null").is_("deleted_at", "null").execute()
        completed_tasks = completed_result.count or 0
        
        # Get today's tasks
        today_result = supabase.table("gtd_tasks").select("count", count="exact").eq("user_id", default_user_id).eq("do_today", "true").is_("deleted_at", "null").execute()
        today_tasks = today_result.count or 0
        
        # Get week's tasks
        week_result = supabase.table("gtd_tasks").select("count", count="exact").eq("user_id", default_user_id).eq("do_this_week", "true").is_("deleted_at", "null").execute()
        week_tasks = week_result.count or 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": total_tasks - completed_tasks,
            "today_tasks": today_tasks,
            "week_tasks": week_tasks
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task stats: {str(e)}"
        )


@router.get("/by-project/{project_id}")
async def get_tasks_by_project(
    project_id: int,
    include_completed: bool = Query(False, description="Include completed tasks"),
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get tasks for a specific project
    
    Args:
        project_id: Project ID
        include_completed: Include completed tasks
        
    Returns:
        List[dict]: List of task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        query = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("project_id", project_id).is_("deleted_at", "null")
        
        if not include_completed:
            query = query.is_("done_at", "null")
        
        result = query.execute()
        
        return [{
            "id": task["id"],
            "name": task["task_name"] or f"Task {task['id']}",
            "project_id": task["project_id"],
            "field_id": task["field_id"],
            "done_at": task["done_at"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"]
        } for task in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project tasks: {str(e)}"
        )


@router.get("/search")
async def search_tasks(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Search tasks by name
    
    Args:
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[dict]: List of matching task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).ilike("task_name", f"%{query}%").is_("deleted_at", "null").range(skip, skip + limit - 1).execute()
        
        return [{
            "id": task["id"],
            "name": task["task_name"] or f"Task {task['id']}",
            "project_id": task["project_id"],
            "field_id": task["field_id"],
            "done_at": task["done_at"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"]
        } for task in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search tasks: {str(e)}"
        )


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    supabase: Client = Depends(get_db)
) -> dict:
    """
    Get task by ID
    
    Args:
        task_id: Task ID
        
    Returns:
        dict: Task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("id", task_id).is_("deleted_at", "null").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task = result.data[0]
        return {
            "id": task.get("id"),
            "name": task.get("task_name") or f"Task {task.get('id', 'Unknown')}",
            "project_id": task.get("project_id"),
            "field_id": task.get("field_id"),
            "done_at": task.get("done_at"),
            "do_today": task.get("do_today", False),
            "do_this_week": task.get("do_this_week", False),
            "is_reading": task.get("is_reading", False),
            "wait_for": task.get("wait_for", False),
            "postponed": task.get("postponed", False),
            "reviewed": task.get("reviewed", False),
            "priority": task.get("priority"),
            "due_date": task.get("do_on_date"),  # Map do_on_date to due_date
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task: {str(e)}"
        )


@router.post("/{task_id}/complete")
async def complete_task(
    task_id: int,
    completion_time: Optional[datetime] = Body(None, description="Optional completion timestamp"),
    supabase: Client = Depends(get_db)
) -> dict:
    """
    Mark a task as completed
    
    Args:
        task_id: Task ID
        completion_time: Optional completion timestamp
        
    Returns:
        dict: Completed task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Get the task first
        task_result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("id", task_id).is_("deleted_at", "null").execute()
        
        if not task_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task = task_result.data[0]
        
        if task["done_at"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already completed"
            )
        
        # Update task with completion timestamp
        update_data = {"done_at": (completion_time or datetime.now()).isoformat()}
        
        result = supabase.table("gtd_tasks").update(update_data).eq("id", task_id).execute()
        
        return {"message": "Task completed successfully", "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )


@router.post("/{task_id}/reopen")
async def reopen_task(
    task_id: int,
    supabase: Client = Depends(get_db)
) -> dict:
    """
    Reopen a completed task
    
    Args:
        task_id: Task ID
        
    Returns:
        dict: Reopened task data
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Get the task first
        task_result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("id", task_id).is_("deleted_at", "null").execute()
        
        if not task_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task = task_result.data[0]
        
        if not task["done_at"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is not completed"
            )
        
        # Update task to remove completion timestamp
        update_data = {"done_at": None}
        
        result = supabase.table("gtd_tasks").update(update_data).eq("id", task_id).execute()
        
        return {"message": "Task reopened successfully", "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reopen task: {str(e)}"
        )


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the task"),
    supabase: Client = Depends(get_db)
) -> dict:
    """
    Delete a task (soft delete by default)
    
    Args:
        task_id: Task ID
        hard_delete: Permanently delete if True, soft delete if False
        
    Returns:
        dict: Success message
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Check if task exists
        task_result = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).eq("id", task_id).is_("deleted_at", "null").execute()
        
        if not task_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        if hard_delete:
            # Permanently delete the task
            result = supabase.table("gtd_tasks").delete().eq("id", task_id).execute()
            action = "permanently deleted"
        else:
            # Soft delete - set deleted_at timestamp
            update_data = {"deleted_at": datetime.now().isoformat()}
            result = supabase.table("gtd_tasks").update(update_data).eq("id", task_id).execute()
            action = "soft deleted"
        
        return {"message": f"Task {action} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )