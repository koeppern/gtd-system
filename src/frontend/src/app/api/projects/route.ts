import { NextRequest, NextResponse } from 'next/server';
import { backendApi } from '@/lib/backend-client';

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
    // TODO: Server-side authentication
    // const session = await getServerSession(request);
    // if (!session) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    // }
    // const userId = session.user.id;

    // For now, use default user (replace with session-based user)
    const userId = process.env.DEFAULT_USER_ID || '00000000-0000-0000-0000-000000000001';

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
    const projects = await backendApi.projects.list(params, userId);
    
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