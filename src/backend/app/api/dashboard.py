"""
Dashboard API endpoints with Supabase direct connection
"""
from datetime import datetime, timedelta, date
from typing import Dict, Any
from fastapi import APIRouter, Depends
from supabase import Client

from app.database import get_db
from app.config import get_settings

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
async def get_dashboard() -> dict:
    """Get dashboard data"""
    return {"message": "Dashboard endpoints not implemented yet"}

@router.get("/stats")
async def get_dashboard_stats(supabase: Client = Depends(get_db)) -> Dict[str, Any]:
    """
    Get dashboard statistics
    
    Returns comprehensive statistics for the GTD dashboard including:
    - Project counts (total, active, completed)
    - Task counts (total, pending, completed)
    - Time-based metrics (today, this week)
    - Completion rates (7d, 30d)
    """
    try:
        # Get default user ID for RLS compliance
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Current date calculations
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday of current week
        seven_days_ago = today - timedelta(days=7)
        thirty_days_ago = today - timedelta(days=30)
        
        # === PROJECT STATISTICS ===
        
        # Total projects
        projects_response = supabase.table("gtd_projects").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").execute()
        total_projects = len(projects_response.data) if projects_response.data else 0
        
        # Try new done_at logic first, fallback to done_status if column doesn't exist
        try:
            # Active projects (done_at is null)
            active_projects_response = supabase.table("gtd_projects").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").is_("done_at", "null").execute()
            active_projects = len(active_projects_response.data) if active_projects_response.data else 0
            
            # Completed projects (done_at is not null)
            completed_projects_response = supabase.table("gtd_projects").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").not_.is_("done_at", "null").execute()
            completed_projects = len(completed_projects_response.data) if completed_projects_response.data else 0
            
        except Exception as e:
            if "done_at does not exist" in str(e):
                # Fallback to old done_status logic
                print(f"INFO: Using done_status fallback (done_at column not found)")
                active_projects_response = supabase.table("gtd_projects").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").eq("done_status", False).execute()
                active_projects = len(active_projects_response.data) if active_projects_response.data else 0
                
                completed_projects_response = supabase.table("gtd_projects").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").eq("done_status", True).execute()
                completed_projects = len(completed_projects_response.data) if completed_projects_response.data else 0
            else:
                raise e
        
        # === TASK STATISTICS ===
        
        # Total tasks
        tasks_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").execute()
        total_tasks = len(tasks_response.data) if tasks_response.data else 0
        
        # Pending tasks (done_at is null)
        pending_tasks_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").is_("done_at", "null").execute()
        pending_tasks = len(pending_tasks_response.data) if pending_tasks_response.data else 0
        
        # Completed tasks (done_at is not null)
        completed_tasks_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").not_.is_("done_at", "null").execute()
        completed_tasks = len(completed_tasks_response.data) if completed_tasks_response.data else 0
        
        # Tasks for today (not completed)
        tasks_today_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").eq("do_today", True).is_("done_at", "null").execute()
        tasks_today = len(tasks_today_response.data) if tasks_today_response.data else 0
        
        # Tasks for this week (not completed)
        tasks_week_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").eq("do_this_week", True).is_("done_at", "null").execute()
        tasks_this_week = len(tasks_week_response.data) if tasks_week_response.data else 0
        
        # Overdue tasks (do_on_date in the past and not completed)
        overdue_tasks_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).is_("deleted_at", "null").is_("done_at", "null").lt("do_on_date", today.isoformat()).execute()
        overdue_tasks = len(overdue_tasks_response.data) if overdue_tasks_response.data else 0
        
        # === COMPLETION RATES ===
        
        # 7-day completion rate
        tasks_7d_completed_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).gte("done_at", seven_days_ago.isoformat()).execute()
        tasks_7d_completed = len(tasks_7d_completed_response.data) if tasks_7d_completed_response.data else 0
        
        tasks_7d_total_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).gte("created_at", seven_days_ago.isoformat()).execute()
        tasks_7d_total = len(tasks_7d_total_response.data) if tasks_7d_total_response.data else 0
        
        completion_rate_7d = (tasks_7d_completed / tasks_7d_total * 100) if tasks_7d_total > 0 else 0
        
        # 30-day completion rate
        tasks_30d_completed_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).gte("done_at", thirty_days_ago.isoformat()).execute()
        tasks_30d_completed = len(tasks_30d_completed_response.data) if tasks_30d_completed_response.data else 0
        
        tasks_30d_total_response = supabase.table("gtd_tasks").select("*").eq("user_id", default_user_id).gte("created_at", thirty_days_ago.isoformat()).execute()
        tasks_30d_total = len(tasks_30d_total_response.data) if tasks_30d_total_response.data else 0
        
        completion_rate_30d = (tasks_30d_completed / tasks_30d_total * 100) if tasks_30d_total > 0 else 0
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "tasks_today": tasks_today,
            "tasks_this_week": tasks_this_week,
            "overdue_tasks": overdue_tasks,
            "completion_rate_7d": round(completion_rate_7d, 1),
            "completion_rate_30d": round(completion_rate_30d, 1)
        }
        
    except Exception as e:
        # Log the error and return default stats
        print(f"Dashboard API Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "total_projects": 0,
            "active_projects": 0,
            "completed_projects": 0,
            "total_tasks": 0,
            "pending_tasks": 0,
            "completed_tasks": 0,
            "tasks_today": 0,
            "tasks_this_week": 0,
            "overdue_tasks": 0,
            "completion_rate_7d": 0.0,
            "completion_rate_30d": 0.0,
            "error": str(e)
        }