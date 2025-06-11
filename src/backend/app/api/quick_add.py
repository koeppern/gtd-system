"""
Quick-add API endpoints for GTD workflow
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_test_user_directly
from app.crud.project import crud_project
from app.crud.task import crud_task
from app.crud.field import crud_field
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/quick-add", tags=["quick-add"])


@router.post("/task", response_model=TaskResponse)
async def quick_add_task(
    task_name: str = Body(..., description="Task name"),
    project_name: Optional[str] = Body(None, description="Optional project name (will be created if doesn't exist)"),
    field_name: Optional[str] = Body(None, description="Optional field name (will be created if doesn't exist)"),
    priority: Optional[int] = Body(None, ge=1, le=5, description="Task priority (1-5)"),
    do_today: bool = Body(False, description="Schedule for today"),
    do_this_week: bool = Body(False, description="Schedule for this week"),
    is_reading: bool = Body(False, description="Mark as reading task"),
    wait_for: bool = Body(False, description="Mark as waiting for someone/something"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> TaskResponse:
    """
    Quick add a task with automatic project and field creation
    
    Args:
        task_name: Task name
        project_name: Optional project name (creates if not exists)
        field_name: Optional field name (creates if not exists)
        priority: Task priority
        do_today: Schedule for today
        do_this_week: Schedule for this week
        is_reading: Mark as reading task
        wait_for: Mark as waiting task
        
    Returns:
        TaskResponse: Created task data
    """
    # Handle field creation/lookup
    field_id = None
    if field_name:
        field = await crud_field.get_or_create_by_name(db=db, name=field_name)
        field_id = field.id
    
    # Handle project creation/lookup
    project_id = None
    if project_name:
        # Try to find existing project by name
        existing_projects = await crud_project.search_projects(
            db=db,
            user_id=current_user.id,
            query=project_name,
            skip=0,
            limit=1
        )
        
        # Check if we found an exact match
        project = None
        for existing_project in existing_projects:
            if existing_project.project_name.lower() == project_name.lower():
                project = existing_project
                break
        
        # Create project if not found
        if not project:
            project_data = ProjectCreate(
                user_id=current_user.id,
                project_name=project_name,
                field_id=field_id
            )
            project = await crud_project.create(db=db, obj_in=project_data)
        
        project_id = project.id
    
    # Create the task
    task_data = TaskCreate(
        user_id=current_user.id,
        task_name=task_name,
        project_id=project_id,
        field_id=field_id,
        priority=priority,
        do_today=do_today,
        do_this_week=do_this_week,
        is_reading=is_reading,
        wait_for=wait_for
    )
    
    task = await crud_task.create(db=db, obj_in=task_data)
    return TaskResponse.from_model(task)


@router.post("/project", response_model=ProjectResponse)
async def quick_add_project(
    project_name: str = Body(..., description="Project name"),
    field_name: Optional[str] = Body(None, description="Optional field name (will be created if doesn't exist)"),
    do_this_week: bool = Body(False, description="Schedule for this week"),
    keywords: Optional[str] = Body(None, description="Project keywords"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> ProjectResponse:
    """
    Quick add a project with automatic field creation
    
    Args:
        project_name: Project name
        field_name: Optional field name (creates if not exists)
        do_this_week: Schedule for this week
        keywords: Project keywords
        
    Returns:
        ProjectResponse: Created project data
    """
    # Handle field creation/lookup
    field_id = None
    if field_name:
        field = await crud_field.get_or_create_by_name(db=db, name=field_name)
        field_id = field.id
    
    # Create the project
    project_data = ProjectCreate(
        user_id=current_user.id,
        project_name=project_name,
        field_id=field_id,
        do_this_week=do_this_week,
        keywords=keywords
    )
    
    project = await crud_project.create(db=db, obj_in=project_data)
    return ProjectResponse.from_model(project)


@router.post("/capture")
async def quick_capture(
    content: str = Body(..., description="Content to capture (task or project)"),
    auto_categorize: bool = Body(True, description="Automatically try to categorize as task or project"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Quick capture content with intelligent categorization (GTD Inbox processing)
    
    Args:
        content: Content to capture
        auto_categorize: Automatically categorize content
        
    Returns:
        Dict: Created item information
    """
    # Simple heuristics for auto-categorization
    is_project = False
    
    if auto_categorize:
        # Project indicators
        project_keywords = ["project", "goal", "outcome", "result", "achieve", "complete", "finish"]
        task_keywords = ["task", "action", "do", "call", "email", "buy", "write", "read"]
        
        content_lower = content.lower()
        
        # Check for project indicators
        project_score = sum(1 for keyword in project_keywords if keyword in content_lower)
        task_score = sum(1 for keyword in task_keywords if keyword in content_lower)
        
        # Length heuristic (longer content tends to be projects)
        if len(content) > 100:
            project_score += 1
        else:
            task_score += 1
        
        # Multiple words in CAPS or title case might indicate project
        words = content.split()
        if len(words) > 1 and any(word.isupper() or word.istitle() for word in words):
            project_score += 1
        
        is_project = project_score > task_score
    
    if is_project:
        # Create as project
        project_data = ProjectCreate(
            user_id=current_user.id,
            project_name=content[:200],  # Limit length
            keywords="captured"
        )
        
        project = await crud_project.create(db=db, obj_in=project_data)
        
        return {
            "type": "project",
            "id": project.id,
            "name": project.project_name,
            "message": "Content captured as project"
        }
    else:
        # Create as task
        task_data = TaskCreate(
            user_id=current_user.id,
            task_name=content[:200]  # Limit length
        )
        
        task = await crud_task.create(db=db, obj_in=task_data)
        
        return {
            "type": "task",
            "id": task.id,
            "name": task.task_name,
            "message": "Content captured as task"
        }


@router.post("/process-inbox")
async def process_inbox_item(
    item_id: int = Body(..., description="Item ID to process"),
    item_type: str = Body(..., description="Item type (task or project)"),
    action: str = Body(..., description="Action to take (schedule_today, schedule_week, mark_reading, mark_waiting, assign_project, delete)"),
    project_name: Optional[str] = Body(None, description="Project name for assign_project action"),
    field_name: Optional[str] = Body(None, description="Field name for categorization"),
    priority: Optional[int] = Body(None, ge=1, le=5, description="Priority for tasks"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> Dict[str, Any]:
    """
    Process an inbox item according to GTD methodology
    
    Args:
        item_id: Item ID
        item_type: Type of item (task or project)
        action: Action to take
        project_name: Project name for assignment
        field_name: Field name for categorization
        priority: Priority for tasks
        
    Returns:
        Dict: Processing result
    """
    if item_type == "task":
        task = await crud_task.get(db=db, id=item_id)
        if not task or task.user_id != current_user.id:
            return {"error": "Task not found"}
        
        # Handle field assignment
        if field_name:
            field = await crud_field.get_or_create_by_name(db=db, name=field_name)
            task.field_id = field.id
        
        # Handle project assignment
        if project_name and action == "assign_project":
            # Find or create project
            existing_projects = await crud_project.search_projects(
                db=db,
                user_id=current_user.id,
                query=project_name,
                skip=0,
                limit=1
            )
            
            project = None
            for existing_project in existing_projects:
                if existing_project.project_name.lower() == project_name.lower():
                    project = existing_project
                    break
            
            if not project:
                project_data = ProjectCreate(
                    user_id=current_user.id,
                    project_name=project_name,
                    field_id=task.field_id
                )
                project = await crud_project.create(db=db, obj_in=project_data)
            
            task.project_id = project.id
        
        # Handle specific actions
        if action == "schedule_today":
            await crud_task.schedule_for_today(db=db, task=task)
        elif action == "schedule_week":
            await crud_task.schedule_for_week(db=db, task=task)
        elif action == "mark_reading":
            task.is_reading = True
        elif action == "mark_waiting":
            task.wait_for = True
        elif action == "delete":
            await crud_task.delete(db=db, id=item_id)
            return {"message": "Task deleted successfully"}
        
        # Set priority if provided
        if priority:
            await crud_task.set_priority(db=db, task=task, priority=priority)
        
        # Save changes
        await db.commit()
        await db.refresh(task)
        
        return {
            "type": "task",
            "id": task.id,
            "message": f"Task processed with action: {action}"
        }
    
    elif item_type == "project":
        project = await crud_project.get(db=db, id=item_id)
        if not project or project.user_id != current_user.id:
            return {"error": "Project not found"}
        
        # Handle field assignment
        if field_name:
            field = await crud_field.get_or_create_by_name(db=db, name=field_name)
            project.field_id = field.id
        
        # Handle specific actions
        if action == "schedule_week":
            project.do_this_week = True
        elif action == "delete":
            await crud_project.delete(db=db, id=item_id)
            return {"message": "Project deleted successfully"}
        
        # Save changes
        await db.commit()
        await db.refresh(project)
        
        return {
            "type": "project",
            "id": project.id,
            "message": f"Project processed with action: {action}"
        }
    
    return {"error": "Invalid item type"}