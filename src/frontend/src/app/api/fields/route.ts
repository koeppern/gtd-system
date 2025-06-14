import { NextRequest, NextResponse } from 'next/server';
import { backendApi } from '@/lib/backend-client';
import { getSessionFromRequest } from '@/lib/session';

/**
 * Fields API Route - Server-Side Proxy
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
    const limit = parseInt(searchParams.get('limit') || '100');
    const offset = parseInt(searchParams.get('offset') || '0');

    // Fetch fields from Python backend using server-side client
    const backendFields = await backendApi.fields.list({ limit, offset }, userId, authToken);
    
    // Transform backend data to match frontend expectations
    const transformedFields = Array.isArray(backendFields) ? backendFields : [];
    
    const fields = {
      items: transformedFields.map((field: any) => ({
        id: field.id,
        name: field.name || field.field_name || `Field ${field.id}`,
        field_name: field.name || field.field_name || `Field ${field.id}`,
        description: field.description || null,
        created_at: field.created_at,
        updated_at: field.updated_at,
      })),
      total: transformedFields.length,
      limit: limit,
      offset: offset,
    };
    
    // Log successful requests (remove in production)
    console.log('Fields fetched successfully:', {
      count: fields.items.length,
      user_id: userId
    });

    // Return data to frontend (no credentials exposed)
    return NextResponse.json(fields);

  } catch (error) {
    console.error('Fields API error:', error);
    
    return NextResponse.json(
      { error: 'Failed to fetch fields' }, 
      { status: 500 }
    );
  }
}