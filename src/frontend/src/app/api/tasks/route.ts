import { NextRequest, NextResponse } from 'next/server';
import { backendApi } from '@/lib/backend-client';
import { getSessionFromRequest } from '@/lib/session';

/**
 * Tasks API Route - Server-Side Proxy
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

    // Parse query parameters
    const { searchParams } = new URL(request.url);
    const showCompleted = searchParams.get('showCompleted') === 'true';
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = parseInt(searchParams.get('offset') || '0');
    const search = searchParams.get('search') || '';
    const projectId = searchParams.get('projectId') || '';

    // Build query parameters for backend
    const params: Record<string, any> = {
      limit,
      offset,
      user_id: userId,
    };

    // Filter by completion status
    if (!showCompleted) {
      // Only active tasks (no done_at)
      params.is_done = false;
    }

    if (search) {
      params.search = search;
    }

    if (projectId) {
      params.project_id = projectId;
    }

    // Fetch data from Python backend using server-side client
    const backendTasks = await backendApi.tasks.list(params, userId, authToken);
    
    // Transform backend data to match frontend expectations
    const transformedTasks = Array.isArray(backendTasks) ? backendTasks : [];
    
    // To get the total count, we need to make a separate request without pagination
    // This is necessary because the backend doesn't return total count with paginated results
    const countParams = { ...params };
    delete countParams.limit;
    delete countParams.offset;
    
    // Get total count by fetching all tasks (without pagination)
    // In a production app, you'd want the backend to return count in the response
    let totalCount = transformedTasks.length;
    
    // If we got a full page of results, there might be more
    if (transformedTasks.length === limit) {
      // Make a request with maximum allowed limit to get count
      // Backend maximum is 1000
      const allTasksParams = { ...countParams, limit: 1000, offset: 0 };
      const allTasks = await backendApi.tasks.list(allTasksParams, userId, authToken);
      totalCount = Array.isArray(allTasks) ? allTasks.length : 0;
    }
    
    const tasks = {
      items: transformedTasks.map((task: any) => ({
        id: task.id,
        task_name: task.name || task.task_name || `Task ${task.id}`,
        project_id: task.project_id,
        project_name: task.project_name || null,
        done_at: task.done_at || null,
        do_today: task.do_today || false,
        do_this_week: task.do_this_week || false,
        is_reading: task.is_reading || false,
        wait_for: task.wait_for || false,
        postponed: task.postponed || false,
        reviewed: task.reviewed || false,
        do_on_date: task.do_on_date || null,
        field_id: task.field_id,
        priority: task.priority || 0,
        created_at: task.created_at,
        updated_at: task.updated_at,
      })),
      total: totalCount,
      limit: limit,
      offset: offset,
      has_next: offset + limit < totalCount,
      has_prev: offset > 0,
    };
    
    // Log successful requests (remove in production)
    console.log('Tasks fetched successfully:', {
      count: tasks.items?.length || 0,
      total: tasks.total || 0,
      showCompleted,
      user_id: userId
    });

    // Return data to frontend (no credentials exposed)
    return NextResponse.json(tasks);

  } catch (error) {
    console.error('Tasks API error:', error);
    
    return NextResponse.json(
      { error: 'Failed to fetch tasks' }, 
      { status: 500 }
    );
  }
}