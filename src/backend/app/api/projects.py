"""
Project API endpoints with Supabase direct connection
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel
from supabase import Client

from app.database import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    done_status: Optional[bool] = None
    do_this_week: Optional[bool] = None
    keywords: Optional[str] = None
    readings: Optional[str] = None


@router.get("/")
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_done: Optional[bool] = Query(None, description="Filter by completion status"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
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
        
        # Filter by user if provided
        if user_id:
            query = query.eq("user_id", user_id)
        
        # Filter by completion status if provided
        if is_done is not None:
            query = query.eq("done_status", is_done)
        
        # Add pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute query with bypass_rls option if available
        result = query.execute()
        
        # Transform data to match expected format and get task counts
        projects = []
        for project in result.data:
            # Count tasks for this project
            task_count_result = supabase.table("gtd_tasks").select("id", count="exact") \
                .eq("project_id", project["id"]) \
                .is_("deleted_at", "null") \
                .execute()
            
            task_count = task_count_result.count if task_count_result.count is not None else 0
            
            projects.append({
                "id": project["id"],
                "name": project["project_name"] or f"Project {project['id']}",
                "field_id": project["field_id"],
                "done_status": project["done_status"],
                "do_this_week": project["do_this_week"],
                "keywords": project["keywords"],
                "readings": project["readings"],
                "task_count": task_count,
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


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    supabase: Client = Depends(get_db)
) -> dict:
    """
    Update a project
    
    Args:
        project_id: Project ID
        project_update: Project update data
        
    Returns:
        dict: Updated project data
    """
    try:
        # Check if project exists
        project_result = supabase.table("gtd_projects").select("*").eq("id", project_id).is_("deleted_at", "null").execute()
        
        if not project_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Prepare update data - only include fields that are not None
        update_data = {}
        if project_update.project_name is not None:
            update_data["project_name"] = project_update.project_name
        if project_update.done_status is not None:
            update_data["done_status"] = project_update.done_status
        if project_update.do_this_week is not None:
            update_data["do_this_week"] = project_update.do_this_week
        if project_update.keywords is not None:
            update_data["keywords"] = project_update.keywords
        if project_update.readings is not None:
            update_data["readings"] = project_update.readings
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Perform update
        result = supabase.table("gtd_projects").update(update_data).eq("id", project_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project"
            )
        
        updated_project = result.data[0]
        
        # Count tasks for this project
        task_count_result = supabase.table("gtd_tasks").select("id", count="exact") \
            .eq("project_id", project_id) \
            .is_("deleted_at", "null") \
            .execute()
        
        task_count = task_count_result.count if task_count_result.count is not None else 0
        
        return {
            "id": updated_project["id"],
            "name": updated_project["project_name"] or f"Project {updated_project['id']}",
            "project_name": updated_project["project_name"],
            "field_id": updated_project["field_id"],
            "done_status": updated_project["done_status"],
            "do_this_week": updated_project["do_this_week"],
            "keywords": updated_project["keywords"],
            "readings": updated_project["readings"],
            "task_count": task_count,
            "created_at": updated_project["created_at"],
            "updated_at": updated_project["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )