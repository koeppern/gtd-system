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
      total: transformedProjects.length,
      limit: limit,
      offset: offset,
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