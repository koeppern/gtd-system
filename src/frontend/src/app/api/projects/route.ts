import { NextRequest, NextResponse } from 'next/server';
import { backendApi } from '@/lib/backend-client';
import { getSessionFromRequest } from '@/lib/session';

/**
 * Projects API Route - Server-Side Proxy
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

    // Build query parameters for backend
    const params: Record<string, any> = {
      limit,
      offset,
      user_id: userId,
    };

    // Filter by completion status
    if (!showCompleted) {
      // Only active projects (no done_at)
      params.is_done = false;
    }

    if (search) {
      params.search = search;
    }

    // Fetch data from Python backend using server-side client
    const backendProjects = await backendApi.projects.list(params, userId, authToken);
    
    // Transform backend data to match frontend expectations
    const transformedProjects = Array.isArray(backendProjects) ? backendProjects : [];
    
    // To get the total count, we need to make a separate request without pagination
    // This is necessary because the backend doesn't return total count with paginated results
    const countParams = { ...params };
    delete countParams.limit;
    delete countParams.offset;
    
    // Get total count by fetching all projects (without pagination)
    // In a production app, you'd want the backend to return count in the response
    let totalCount = transformedProjects.length;
    
    // If we got a full page of results, there might be more
    if (transformedProjects.length === limit) {
      // Make a request with maximum allowed limit to get count
      // Backend maximum is 1000
      const allProjectsParams = { ...countParams, limit: 1000, offset: 0 };
      const allProjects = await backendApi.projects.list(allProjectsParams, userId, authToken);
      totalCount = Array.isArray(allProjects) ? allProjects.length : 0;
    }
    
    const projects = {
      items: transformedProjects.map((project: any) => ({
        id: project.id,
        project_name: project.name || project.project_name || `Project ${project.id}`,
        done_status: project.done_status,
        done_at: project.done_at || null,
        field_id: project.field_id,
        do_this_week: project.do_this_week,
        task_count: project.task_count || 0,
        keywords: project.keywords,
        readings: project.readings,
        created_at: project.created_at,
        updated_at: project.updated_at,
      })),
      total: totalCount,
      limit: limit,
      offset: offset,
      has_next: offset + limit < totalCount,
      has_prev: offset > 0,
    };
    
    // Log successful requests (remove in production)
    console.log('Projects fetched successfully:', {
      count: projects.items?.length || 0,
      total: projects.total || 0,
      showCompleted,
      user_id: userId
    });

    // Return data to frontend (no credentials exposed)
    return NextResponse.json(projects);

  } catch (error) {
    console.error('Projects API error:', error);
    
    return NextResponse.json(
      { error: 'Failed to fetch projects' }, 
      { status: 500 }
    );
  }
}