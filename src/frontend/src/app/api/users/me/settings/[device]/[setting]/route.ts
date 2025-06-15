import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/session';

/**
 * User Settings API Route - Device and Setting Specific
 * 
 * This route handles device-specific user settings storage.
 * For now, we'll use in-memory storage or localStorage fallback.
 * 
 * TODO: Implement proper database storage for user settings
 */

// In-memory storage (replace with database in production)
const settingsStore = new Map<string, any>();

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ device: string; setting: string }> }
) {
  try {
    // Extract session
    const session = await getSessionFromRequest(request);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { userId } = session;
    const { device, setting } = await params;

    // Generate storage key
    const storageKey = `${userId}:${device}:${setting}`;
    
    // Get setting from in-memory store
    const settingValue = settingsStore.get(storageKey);
    
    if (settingValue === undefined) {
      return NextResponse.json({ error: 'Setting not found' }, { status: 404 });
    }

    // Return setting value
    return NextResponse.json({ setting_value: settingValue });

  } catch (error) {
    console.error('User settings GET error:', error);
    
    return NextResponse.json(
      { error: 'Failed to get user setting' }, 
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ device: string; setting: string }> }
) {
  try {
    // Extract session
    const session = await getSessionFromRequest(request);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { userId } = session;
    const { device, setting } = await params;

    // Parse request body
    const settingValue = await request.json();

    // Generate storage key
    const storageKey = `${userId}:${device}:${setting}`;
    
    // Store setting in in-memory store
    settingsStore.set(storageKey, settingValue);

    console.log(`Setting stored: ${storageKey} =`, settingValue);

    // Return success
    return NextResponse.json({ success: true });

  } catch (error) {
    console.error('User settings PUT error:', error);
    
    return NextResponse.json(
      { error: 'Failed to update user setting' }, 
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ device: string; setting: string }> }
) {
  try {
    // Extract session
    const session = await getSessionFromRequest(request);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { userId } = session;
    const { device, setting } = await params;

    // Generate storage key
    const storageKey = `${userId}:${device}:${setting}`;
    
    // Delete setting from in-memory store
    settingsStore.delete(storageKey);

    console.log(`Setting deleted: ${storageKey}`);

    // Return success
    return NextResponse.json({ success: true });

  } catch (error) {
    console.error('User settings DELETE error:', error);
    
    return NextResponse.json(
      { error: 'Failed to delete user setting' }, 
      { status: 500 }
    );
  }
}