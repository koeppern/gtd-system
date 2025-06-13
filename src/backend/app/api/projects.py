"""
Project API endpoints with Supabase direct connection
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client

from app.database import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get projects from Supabase
    
    Returns:
        List[dict]: List of project data
    """
    try:
        # Try disabling RLS for this specific query using service role
        # The service role should bypass RLS policies
        query = supabase.table("gtd_projects").select("*")
        
        # Add filters
        query = query.is_("deleted_at", "null")  # Exclude deleted projects
        
        # Add pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute query with bypass_rls option if available
        result = query.execute()
        
        # Transform data to match expected format
        projects = []
        for project in result.data:
            projects.append({
                "id": project["id"],
                "name": project["project_name"] or f"Project {project['id']}",
                "field_id": project["field_id"],
                "done_status": project["done_status"],
                "do_this_week": project["do_this_week"],
                "keywords": project["keywords"],
                "readings": project["readings"],
                "created_at": project["created_at"],
                "updated_at": project["updated_at"]
            })
        
        return projects
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )


@router.get("/weekly")
async def get_weekly_projects(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get projects marked for this week
    
    Returns:
        List[dict]: List of projects with do_this_week=true
    """
    try:
        # Get settings for user ID
        from app.config import get_settings
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Query projects for this week
        query = supabase.table("gtd_projects").select("*")
        query = query.eq("user_id", default_user_id)
        query = query.is_("deleted_at", "null")
        query = query.eq("do_this_week", "true")
        
        result = query.execute()
        
        # Transform data to match expected format
        projects = []
        for project in result.data:
            projects.append({
                "id": project["id"],
                "name": project["project_name"] or f"Project {project['id']}",
                "field_id": project["field_id"],
                "done_status": project["done_status"],
                "do_this_week": project["do_this_week"],
                "keywords": project["keywords"],
                "readings": project["readings"],
                "created_at": project["created_at"],
                "updated_at": project["updated_at"]
            })
        
        return projects
        
    except Exception as e:
        # Return empty list in case of error
        return []


@router.get("/active")
async def get_active_projects(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """
    Get active (not completed) projects
    
    Returns:
        List[dict]: List of active projects
    """
    try:
        # Get settings for user ID
        from app.config import get_settings
        settings = get_settings()
        default_user_id = settings.gtd.default_user_id
        
        # Query active projects (done_status = false)
        query = supabase.table("gtd_projects").select("*")
        query = query.eq("user_id", default_user_id)
        query = query.is_("deleted_at", "null")
        query = query.eq("done_status", "false")
        
        result = query.execute()
        
        # Transform data to match expected format
        projects = []
        for project in result.data:
            projects.append({
                "id": project["id"],
                "name": project["project_name"] or f"Project {project['id']}",
                "field_id": project["field_id"],
                "done_status": project["done_status"],
                "do_this_week": project["do_this_week"],
                "keywords": project["keywords"],
                "readings": project["readings"],
                "created_at": project["created_at"],
                "updated_at": project["updated_at"]
            })
        
        return projects
        
    except Exception as e:
        # Return empty list in case of error
        return []


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    supabase: Client = Depends(get_db)
) -> dict:
    """
    Get a specific project by ID
    
    Args:
        project_id: The project ID
        
    Returns:
        dict: Project data
    """
    try:
        result = supabase.table("gtd_projects").select("*").eq("id", project_id).is_("deleted_at", "null").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project = result.data[0]
        return {
            "id": project["id"],
            "name": project["project_name"] or f"Project {project['id']}",
            "field_id": project["field_id"],
            "done_status": project["done_status"],
            "do_this_week": project["do_this_week"],
            "keywords": project["keywords"],
            "readings": project["readings"],
            "created_at": project["created_at"],
            "updated_at": project["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project: {str(e)}"
        )