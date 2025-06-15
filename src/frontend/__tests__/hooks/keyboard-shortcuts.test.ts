/**
 * Tests for keyboard shortcuts functionality
 * Testing CTRL-K and CTRL-SHIFT-F shortcuts for search fields
 */

import { renderHook } from '@testing-library/react';
import { fireEvent } from '@testing-library/react';
import { useKeyboardShortcuts, useSearchFieldRef } from '@/hooks/use-keyboard-shortcuts';

describe('useSearchFieldRef', () => {
  it('creates a ref with focus and select methods', () => {
    const { result } = renderHook(() => useSearchFieldRef());
    
    expect(result.current.ref).toBeDefined();
    expect(result.current.searchFieldRef.current).toBeDefined();
    expect(result.current.searchFieldRef.current.focus).toBeDefined();
    expect(result.current.searchFieldRef.current.select).toBeDefined();
  });

  it('calls focus on the input element', () => {
    const { result } = renderHook(() => useSearchFieldRef());
    
    // Mock HTMLInputElement
    const mockInput = {
      focus: jest.fn(),
      select: jest.fn(),
    };
    
    result.current.ref.current = mockInput as any;
    
    // Call focus through the searchFieldRef
    result.current.searchFieldRef.current.focus();
    
    expect(mockInput.focus).toHaveBeenCalled();
  });

  it('calls select on the input element', () => {
    const { result } = renderHook(() => useSearchFieldRef());
    
    const mockInput = {
      focus: jest.fn(),
      select: jest.fn(),
    };
    
    result.current.ref.current = mockInput as any;
    
    result.current.searchFieldRef.current.select();
    
    expect(mockInput.select).toHaveBeenCalled();
  });
});

describe('useKeyboardShortcuts', () => {
  let mockGlobalSearch: jest.Mock;
  let mockContextSearch: jest.Mock;
  let mockGlobalSearchRef: any;
  let mockContextSearchRef: any;

  beforeEach(() => {
    mockGlobalSearch = jest.fn();
    mockContextSearch = jest.fn();
    
    mockGlobalSearchRef = {
      current: {
        focus: jest.fn(),
        select: jest.fn(),
      },
    };
    
    mockContextSearchRef = {
      current: {
        focus: jest.fn(),
        select: jest.fn(),
      },
    };

    // Clear all event listeners before each test
    document.removeEventListener = jest.fn();
    document.addEventListener = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('sets up keyboard event listeners', () => {
    renderHook(() => useKeyboardShortcuts({
      onGlobalSearch: mockGlobalSearch,
      onContextSearch: mockContextSearch,
    }));

    expect(document.addEventListener).toHaveBeenCalledWith('keydown', expect.any(Function));
  });

  it('handles CTRL-K for global search with ref', () => {
    renderHook(() => useKeyboardShortcuts({
      globalSearchRef: mockGlobalSearchRef,
    }));

    // Get the event handler that was registered
    const eventHandler = (document.addEventListener as jest.Mock).mock.calls[0][1];

    // Simulate CTRL-K keydown
    const event = new KeyboardEvent('keydown', {
      ctrlKey: true,
      key: 'k',
      shiftKey: false,
      altKey: false,
      metaKey: false,
    });

    Object.defineProperty(event, 'preventDefault', {
      value: jest.fn(),
    });

    eventHandler(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(mockGlobalSearchRef.current.focus).toHaveBeenCalled();
    expect(mockGlobalSearchRef.current.select).toHaveBeenCalled();
  });

  it('handles CTRL-K for global search with callback', () => {
    renderHook(() => useKeyboardShortcuts({
      onGlobalSearch: mockGlobalSearch,
    }));

    const eventHandler = (document.addEventListener as jest.Mock).mock.calls[0][1];

    const event = new KeyboardEvent('keydown', {
      ctrlKey: true,
      key: 'k',
      shiftKey: false,
      altKey: false,
      metaKey: false,
    });

    Object.defineProperty(event, 'preventDefault', {
      value: jest.fn(),
    });

    eventHandler(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(mockGlobalSearch).toHaveBeenCalled();
  });

  it('handles CTRL-SHIFT-F for context search with ref', () => {
    renderHook(() => useKeyboardShortcuts({
      contextSearchRef: mockContextSearchRef,
    }));

    const eventHandler = (document.addEventListener as jest.Mock).mock.calls[0][1];

    const event = new KeyboardEvent('keydown', {
      ctrlKey: true,
      key: 'F',
      shiftKey: true,
      altKey: false,
      metaKey: false,
    });

    Object.defineProperty(event, 'preventDefault', {
      value: jest.fn(),
    });

    eventHandler(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(mockContextSearchRef.current.focus).toHaveBeenCalled();
    expect(mockContextSearchRef.current.select).toHaveBeenCalled();
  });

  it('handles CTRL-SHIFT-F for context search with callback', () => {
    renderHook(() => useKeyboardShortcuts({
      onContextSearch: mockContextSearch,
    }));

    const eventHandler = (document.addEventListener as jest.Mock).mock.calls[0][1];

    const event = new KeyboardEvent('keydown', {
      ctrlKey: true,
      key: 'F',
      shiftKey: true,
      altKey: false,
      metaKey: false,
    });

    Object.defineProperty(event, 'preventDefault', {
      value: jest.fn(),
    });

    eventHandler(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(mockContextSearch).toHaveBeenCalled();
  });

  it('ignores other key combinations', () => {
    renderHook(() => useKeyboardShortcuts({
      onGlobalSearch: mockGlobalSearch,
      onContextSearch: mockContextSearch,
    }));

    const eventHandler = (document.addEventListener as jest.Mock).mock.calls[0][1];

    // Test various key combinations that should be ignored
    const ignoredEvents = [
      { ctrlKey: true, key: 'a' }, // CTRL-A
      { ctrlKey: false, key: 'k' }, // Just K
      { ctrlKey: true, key: 'k', shiftKey: true }, // CTRL-SHIFT-K
      { ctrlKey: true, key: 'F', shiftKey: false }, // CTRL-F (without shift)
      { ctrlKey: false, key: 'F', shiftKey: true }, // SHIFT-F
    ];

    ignoredEvents.forEach(eventProps => {
      const event = new KeyboardEvent('keydown', eventProps);
      Object.defineProperty(event, 'preventDefault', {
        value: jest.fn(),
      });

      eventHandler(event);

      expect(event.preventDefault).not.toHaveBeenCalled();
    });

    expect(mockGlobalSearch).not.toHaveBeenCalled();
    expect(mockContextSearch).not.toHaveBeenCalled();
  });

  it('cleans up event listeners on unmount', () => {
    const { unmount } = renderHook(() => useKeyboardShortcuts({
      onGlobalSearch: mockGlobalSearch,
    }));

    unmount();

    expect(document.removeEventListener).toHaveBeenCalledWith('keydown', expect.any(Function));
  });
});