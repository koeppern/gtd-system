import { NextRequest, NextResponse } from 'next/server';
import { backendApi } from '@/lib/backend-client';

/**
 * Projects API Route for individual project operations
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
    const projectId = parseInt(id);
    if (isNaN(projectId)) {
      return NextResponse.json({ error: 'Invalid project ID' }, { status: 400 });
    }

    // Parse request body
    const updateData = await request.json();

    // Validate required fields
    if (!updateData || typeof updateData !== 'object') {
      return NextResponse.json({ error: 'Invalid request body' }, { status: 400 });
    }

    // Update project via backend
    const backendProject = await backendApi.projects.update(projectId, updateData, userId);
    
    // Transform backend data to match frontend expectations
    const project = {
      id: backendProject.id,
      project_name: backendProject.project_name || backendProject.name || `Project ${backendProject.id}`,
      name: backendProject.project_name || backendProject.name || `Project ${backendProject.id}`,
      done_status: backendProject.done_status || false,
      done_at: backendProject.done_at || null,
      do_this_week: backendProject.do_this_week || false,
      task_count: backendProject.task_count || 0,
      field_id: backendProject.field_id,
      keywords: backendProject.keywords,
      readings: backendProject.readings,
      created_at: backendProject.created_at,
      updated_at: backendProject.updated_at,
    };
    
    // Log successful requests (remove in production)
    console.log('Project updated successfully:', {
      id: project.id,
      name: project.project_name,
      user_id: userId
    });

    // Return updated project data to frontend (no credentials exposed)
    return NextResponse.json(project);

  } catch (error) {
    console.error('Project update API error:', error);
    
    // Handle different error types
    if (error instanceof Error && error.message.includes('404')) {
      return NextResponse.json(
        { error: 'Project not found' }, 
        { status: 404 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to update project' }, 
      { status: 500 }
    );
  }
}