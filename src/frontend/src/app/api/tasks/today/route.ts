import { NextRequest, NextResponse } from 'next/server';
import { backendApi } from '@/lib/backend-client';
import { getSessionFromRequest } from '@/lib/session';

/**
 * Today's Tasks API Route - Server-Side Proxy
 * 
 * This route acts as a secure proxy between the frontend and Python backend.
 * All credentials and authentication are handled server-side.
 * 
 * SECURITY: Frontend never communicates directly with Python backend.
 */

export async function GET(request: NextRequest) {
  try {
    // Extract session and JWT token
    const session = await getSessionFromRequest(request);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { userId, authToken } = session;

    // Fetch today's tasks from Python backend using server-side client
    const backendTasks = await backendApi.tasks.getToday(userId, authToken);
    
    // Transform backend data to match frontend expectations
    const transformedTasks = Array.isArray(backendTasks) ? backendTasks : [];
    
    const tasks = transformedTasks.map((task: any) => ({
      id: task.id,
      name: task.name || task.task_name || `Task ${task.id}`,
      task_name: task.name || task.task_name || `Task ${task.id}`,
      project_id: task.project_id,
      project_name: task.project_name || null,
      done_at: task.done_at || null,
      do_today: task.do_today || true,
      do_this_week: task.do_this_week || false,
      is_reading: task.is_reading || false,
      wait_for: task.wait_for || false,
      postponed: task.postponed || false,
      reviewed: task.reviewed || false,
      field_id: task.field_id,
      priority: task.priority || 0,
      created_at: task.created_at,
      updated_at: task.updated_at,
    }));
    
    // Log successful requests (remove in production)
    console.log('Today tasks fetched successfully:', {
      count: tasks.length,
      user_id: userId
    });

    // Return data to frontend (no credentials exposed)
    return NextResponse.json(tasks);

  } catch (error) {
    console.error('Today tasks API error:', error);
    
    return NextResponse.json(
      { error: 'Failed to fetch today\'s tasks' }, 
      { status: 500 }
    );
  }
}