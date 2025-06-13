"""
Weekly Review API endpoints
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.database import get_db
from app.config import get_settings

router = APIRouter(prefix="/weekly-review", tags=["weekly-review"])


@router.get("/tasks-to-review")
async def get_tasks_to_review(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get tasks that need to be reviewed during weekly review
    
    Criteria:
    - Not completed
    - Not reviewed yet OR reviewed more than 7 days ago
    - Not deleted
    
    Returns:
        List[dict]: List of tasks needing review
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Calculate date 7 days ago
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Get tasks that haven't been reviewed or were reviewed more than 7 days ago
        query = supabase.table("gtd_tasks").select("*")
        query = query.eq("user_id", default_user_id)
        query = query.is_("deleted_at", "null")
        query = query.is_("done_at", "null")
        
        # Get all non-completed tasks first
        result = query.execute()
        
        # Filter tasks that need review
        tasks_to_review = []
        for task in result.data:
            # Include if never reviewed or reviewed more than 7 days ago
            if not task.get("reviewed") or task.get("last_edited", "") < seven_days_ago:
                tasks_to_review.append({
                    "id": task.get("id"),
                    "name": task.get("task_name") or f"Task {task.get('id', 'Unknown')}",
                    "project_id": task.get("project_id"),
                    "field_id": task.get("field_id"),
                    "do_today": task.get("do_today", False),
                    "do_this_week": task.get("do_this_week", False),
                    "reviewed": task.get("reviewed", False),
                    "last_edited": task.get("last_edited"),
                    "created_at": task.get("created_at")
                })
        
        return tasks_to_review
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks for review: {str(e)}"
        )


@router.get("/projects-to-review")
async def get_projects_to_review(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get projects that need to be reviewed during weekly review
    
    Criteria:
    - Not completed
    - Active projects that haven't been updated in last 7 days
    - Not deleted
    
    Returns:
        List[dict]: List of projects needing review
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Calculate date 7 days ago
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Get active projects
        query = supabase.table("gtd_projects").select("*")
        query = query.eq("user_id", default_user_id)
        query = query.is_("deleted_at", "null")
        query = query.eq("done_status", "false")
        
        result = query.execute()
        
        # Filter projects that need review
        projects_to_review = []
        for project in result.data:
            # Include if not updated in last 7 days
            if project.get("updated_at", "") < seven_days_ago:
                projects_to_review.append({
                    "id": project.get("id"),
                    "name": project.get("project_name") or f"Project {project.get('id', 'Unknown')}",
                    "field_id": project.get("field_id"),
                    "done_status": project.get("done_status", False),
                    "do_this_week": project.get("do_this_week", False),
                    "keywords": project.get("keywords"),
                    "updated_at": project.get("updated_at"),
                    "created_at": project.get("created_at")
                })
        
        return projects_to_review
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects for review: {str(e)}"
        )


@router.post("/mark-task-reviewed/{task_id}")
async def mark_task_reviewed(
    task_id: int,
    supabase: Client = Depends(get_db)
) -> dict:
    """
    Mark a task as reviewed
    
    Args:
        task_id: The task ID to mark as reviewed
        
    Returns:
        dict: Success message
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Update task reviewed status
        result = supabase.table("gtd_tasks").update({
            "reviewed": True,
            "last_edited": datetime.now().isoformat()
        }).eq("id", task_id).eq("user_id", default_user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return {"message": "Task marked as reviewed", "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark task as reviewed: {str(e)}"
        )