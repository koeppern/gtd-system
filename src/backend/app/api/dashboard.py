"""
Dashboard API endpoints - aggregated statistics and overview
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_test_user_directly
from app.crud.user import crud_user
from app.crud.task import crud_task
from app.crud.field import crud_field
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard overview for current user
    
    Returns:
        Dict: Dashboard data with user stats, task stats, and field info
    """
    # Get user statistics
    user_stats = await crud_user.get_user_stats(db=db, user_id=current_user.id)
    
    # Get detailed task statistics
    task_stats = await crud_task.get_task_stats(db=db, user_id=current_user.id)
    
    # Get today's tasks
    today_tasks = await crud_task.get_today_tasks(db=db, user_id=current_user.id)
    
    # Get overdue tasks
    overdue_tasks = await crud_task.get_overdue_tasks(db=db, user_id=current_user.id)
    
    # Get this week's tasks
    week_tasks = await crud_task.get_week_tasks(db=db, user_id=current_user.id)
    
    # Get waiting tasks
    waiting_tasks = await crud_task.get_waiting_tasks(db=db, user_id=current_user.id)
    
    # Get reading tasks
    reading_tasks = await crud_task.get_reading_tasks(db=db, user_id=current_user.id)
    
    # Get popular fields
    popular_fields = await crud_field.get_popular_fields(db=db, limit=5)
    
    return {
        "user": {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email_address,
            "last_login": current_user.last_login_at,
            "stats": user_stats
        },
        "tasks": {
            "stats": task_stats,
            "today": {
                "count": len(today_tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.task_name,
                        "priority": task.priority,
                        "project_id": task.project_id
                    }
                    for task in today_tasks[:10]  # Limit to 10 for overview
                ]
            },
            "overdue": {
                "count": len(overdue_tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.task_name,
                        "due_date": task.do_on_date,
                        "priority": task.priority,
                        "project_id": task.project_id
                    }
                    for task in overdue_tasks[:10]  # Limit to 10 for overview
                ]
            },
            "week": {
                "count": len(week_tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.task_name,
                        "priority": task.priority,
                        "project_id": task.project_id
                    }
                    for task in week_tasks[:10]  # Limit to 10 for overview
                ]
            },
            "waiting": {
                "count": len(waiting_tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.task_name,
                        "project_id": task.project_id
                    }
                    for task in waiting_tasks[:5]  # Limit to 5 for overview
                ]
            },
            "reading": {
                "count": len(reading_tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.task_name,
                        "project_id": task.project_id
                    }
                    for task in reading_tasks[:5]  # Limit to 5 for overview
                ]
            }
        },
        "fields": {
            "popular": popular_fields
        },
        "summary": {
            "total_active_items": (
                user_stats.get("pending_tasks", 0) + 
                user_stats.get("active_projects", 0)
            ),
            "completion_rate": task_stats.get("completion_rate", 0.0),
            "urgent_items": task_stats.get("priority_1", 0) + task_stats.get("priority_2", 0),
            "today_focus": len(today_tasks),
            "attention_needed": len(overdue_tasks) + len(waiting_tasks)
        }
    }


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Get detailed statistics for dashboard widgets
    
    Returns:
        Dict: Comprehensive statistics
    """
    # Get all statistics
    user_stats = await crud_user.get_user_stats(db=db, user_id=current_user.id)
    task_stats = await crud_task.get_task_stats(db=db, user_id=current_user.id)
    
    return {
        "projects": {
            "total": user_stats.get("total_projects", 0),
            "active": user_stats.get("active_projects", 0),
            "completed": user_stats.get("completed_projects", 0),
            "completion_rate": (
                (user_stats.get("completed_projects", 0) / user_stats.get("total_projects", 1)) * 100
                if user_stats.get("total_projects", 0) > 0 else 0.0
            )
        },
        "tasks": {
            "total": task_stats.get("total_tasks", 0),
            "pending": task_stats.get("pending_tasks", 0),
            "completed": task_stats.get("completed_tasks", 0),
            "completion_rate": task_stats.get("completion_rate", 0.0),
            "today": task_stats.get("tasks_today", 0),
            "overdue": task_stats.get("overdue_tasks", 0),
            "reading": task_stats.get("reading_tasks", 0),
            "waiting": task_stats.get("waiting_tasks", 0)
        },
        "priorities": {
            "priority_1": task_stats.get("priority_1", 0),
            "priority_2": task_stats.get("priority_2", 0),
            "priority_3": task_stats.get("priority_3", 0),
            "priority_4": task_stats.get("priority_4", 0),
            "priority_5": task_stats.get("priority_5", 0),
            "no_priority": task_stats.get("no_priority", 0)
        },
        "weekly": {
            "tasks_this_week": user_stats.get("tasks_this_week", 0)
        }
    }


@router.get("/quick-actions")
async def get_quick_actions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Get suggested quick actions for the user
    
    Returns:
        Dict: Suggested actions based on current data
    """
    # Get various task lists for analysis
    today_tasks = await crud_task.get_today_tasks(db=db, user_id=current_user.id)
    overdue_tasks = await crud_task.get_overdue_tasks(db=db, user_id=current_user.id)
    waiting_tasks = await crud_task.get_waiting_tasks(db=db, user_id=current_user.id)
    
    suggestions = []
    
    # Suggest based on overdue tasks
    if len(overdue_tasks) > 0:
        suggestions.append({
            "type": "urgent",
            "title": f"Review {len(overdue_tasks)} overdue task(s)",
            "description": "Some tasks are past their due date",
            "action": "GET /api/tasks/overdue",
            "count": len(overdue_tasks)
        })
    
    # Suggest based on today's tasks
    if len(today_tasks) == 0:
        suggestions.append({
            "type": "planning",
            "title": "Plan your day",
            "description": "No tasks scheduled for today. Consider scheduling some tasks.",
            "action": "GET /api/tasks/week",
            "count": 0
        })
    elif len(today_tasks) > 10:
        suggestions.append({
            "type": "focus",
            "title": "Prioritize today's tasks",
            "description": f"You have {len(today_tasks)} tasks for today. Consider prioritizing the most important ones.",
            "action": "GET /api/tasks/today",
            "count": len(today_tasks)
        })
    
    # Suggest based on waiting tasks
    if len(waiting_tasks) > 0:
        suggestions.append({
            "type": "review",
            "title": f"Check {len(waiting_tasks)} waiting task(s)",
            "description": "Review tasks waiting for external input",
            "action": "GET /api/tasks/waiting",
            "count": len(waiting_tasks)
        })
    
    # General suggestions
    if len(suggestions) == 0:
        suggestions.append({
            "type": "productivity",
            "title": "Great job! Everything looks organized",
            "description": "Consider adding new tasks or projects to continue your productivity",
            "action": "POST /api/tasks/",
            "count": 0
        })
    
    return {
        "suggestions": suggestions,
        "quick_links": [
            {"title": "Add Task", "action": "POST /api/tasks/", "icon": "plus"},
            {"title": "Add Project", "action": "POST /api/projects/", "icon": "folder-plus"},
            {"title": "Today's Tasks", "action": "GET /api/tasks/today", "icon": "calendar"},
            {"title": "Weekly Review", "action": "GET /api/tasks/week", "icon": "list"}
        ]
    }