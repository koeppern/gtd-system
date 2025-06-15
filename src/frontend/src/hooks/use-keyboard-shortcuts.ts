'use client';

import { useEffect, useRef } from 'react';

export interface SearchFieldRef {
  focus: () => void;
  select?: () => void;
}

export interface KeyboardShortcutOptions {
  onGlobalSearch?: () => void;
  onContextSearch?: () => void;
  globalSearchRef?: React.RefObject<SearchFieldRef>;
  contextSearchRef?: React.RefObject<SearchFieldRef>;
}

/**
 * Custom hook for managing keyboard shortcuts for search fields
 */
export function useKeyboardShortcuts(options: KeyboardShortcutOptions = {}) {
  const {
    onGlobalSearch,
    onContextSearch,
    globalSearchRef,
    contextSearchRef
  } = options;

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // CTRL-K for global search
      if (event.ctrlKey && event.key === 'k' && !event.shiftKey && !event.altKey && !event.metaKey) {
        event.preventDefault();
        
        if (globalSearchRef?.current) {
          globalSearchRef.current.focus();
          // Optionally select all text
          if (globalSearchRef.current.select) {
            globalSearchRef.current.select();
          }
        } else if (onGlobalSearch) {
          onGlobalSearch();
        }
        return;
      }

      // CTRL-SHIFT-F for context-specific search
      if (event.ctrlKey && event.shiftKey && event.key === 'F' && !event.altKey && !event.metaKey) {
        event.preventDefault();
        
        if (contextSearchRef?.current) {
          contextSearchRef.current.focus();
          // Optionally select all text
          if (contextSearchRef.current.select) {
            contextSearchRef.current.select();
          }
        } else if (onContextSearch) {
          onContextSearch();
        }
        return;
      }
    };

    // Add event listener to document
    document.addEventListener('keydown', handleKeyDown);

    // Cleanup
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onGlobalSearch, onContextSearch, globalSearchRef, contextSearchRef]);
}

/**
 * Helper hook to create a ref that can be used with search input fields
 */
export function useSearchFieldRef() {
  const ref = useRef<HTMLInputElement>(null);
  
  const searchFieldRef = useRef<SearchFieldRef>({
    focus: () => {
      if (ref.current) {
        ref.current.focus();
      }
    },
    select: () => {
      if (ref.current) {
        ref.current.select();
      }
    }
  });

  return { ref, searchFieldRef };
}