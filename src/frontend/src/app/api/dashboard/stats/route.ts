import { NextRequest, NextResponse } from 'next/server';
import { backendApi } from '@/lib/backend-client';
import { getSessionFromRequest } from '@/lib/session';

/**
 * Dashboard Stats API Route - Server-Side Proxy
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

    // Fetch data from Python backend using server-side client
    const stats = await backendApi.dashboard.getStats(userId, authToken);
    
    // Log successful requests (remove in production)
    console.log('Dashboard stats fetched successfully:', {
      active_projects: stats.active_projects,
      total_projects: stats.total_projects,
      user_id: userId
    });

    // Return data to frontend (no credentials exposed)
    return NextResponse.json(stats);

  } catch (error) {
    console.error('Dashboard stats API error:', error);
    
    return NextResponse.json(
      { error: 'Failed to fetch dashboard stats' }, 
      { status: 500 }
    );
  }
}