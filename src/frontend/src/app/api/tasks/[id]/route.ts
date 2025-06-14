import { NextRequest, NextResponse } from 'next/server';
import { backendApi } from '@/lib/backend-client';

/**
 * Tasks API Route for individual task operations
 * 
 * This route acts as a secure proxy between the frontend and Python backend.
 * All credentials and authentication are handled server-side.
 * 
 * SECURITY: Frontend never communicates directly with Python backend.
 */

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // TODO: Server-side authentication
    // const session = await getServerSession(request);
    // if (!session) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    // }
    // const userId = session.user.id;

    // For now, use default user (replace with session-based user)
    const userId = process.env.DEFAULT_USER_ID || '00000000-0000-0000-0000-000000000001';

    const { id } = await params;
    const taskId = parseInt(id);
    if (isNaN(taskId)) {
      return NextResponse.json({ error: 'Invalid task ID' }, { status: 400 });
    }

    // Parse request body
    const updateData = await request.json();

    // Validate required fields
    if (!updateData || typeof updateData !== 'object') {
      return NextResponse.json({ error: 'Invalid request body' }, { status: 400 });
    }

    // Update task via backend
    const backendTask = await backendApi.tasks.update(taskId, updateData, userId);
    
    // Transform backend data to match frontend expectations
    const task = {
      id: backendTask.id,
      task_name: backendTask.task_name || backendTask.name || `Task ${backendTask.id}`,
      name: backendTask.task_name || backendTask.name || `Task ${backendTask.id}`,
      project_id: backendTask.project_id,
      project_name: backendTask.project_name || null,
      done_at: backendTask.done_at || null,
      do_today: backendTask.do_today || false,
      do_this_week: backendTask.do_this_week || false,
      is_reading: backendTask.is_reading || false,
      wait_for: backendTask.wait_for || false,
      postponed: backendTask.postponed || false,
      reviewed: backendTask.reviewed || false,
      do_on_date: backendTask.do_on_date || null,
      field_id: backendTask.field_id,
      priority: backendTask.priority || 0,
      created_at: backendTask.created_at,
      updated_at: backendTask.updated_at,
    };
    
    // Log successful requests (remove in production)
    console.log('Task updated successfully:', {
      id: task.id,
      name: task.task_name,
      user_id: userId
    });

    // Return updated task data to frontend (no credentials exposed)
    return NextResponse.json(task);

  } catch (error) {
    console.error('Task update API error:', error);
    
    // Handle different error types
    if (error instanceof Error && error.message.includes('404')) {
      return NextResponse.json(
        { error: 'Task not found' }, 
        { status: 404 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to update task' }, 
      { status: 500 }
    );
  }
}