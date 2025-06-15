'use client';

import { useCallback } from 'react';

interface ShiftClickHandlers {
  handleRowClick: (event: React.MouseEvent, id: number, onEdit: (id: number) => void) => void;
  handleShiftClick: (event: React.MouseEvent, id: number, onEdit: (id: number) => void) => void;
}

/**
 * Hook for handling shift+click navigation to edit mode
 */
export function useShiftClick(): ShiftClickHandlers {
  const handleRowClick = useCallback((
    event: React.MouseEvent, 
    id: number, 
    onEdit: (id: number) => void
  ) => {
    // Prevent default if this is meant to be navigation
    if (event.shiftKey) {
      event.preventDefault();
      event.stopPropagation();
      onEdit(id);
    }
  }, []);

  const handleShiftClick = useCallback((
    event: React.MouseEvent, 
    id: number, 
    onEdit: (id: number) => void
  ) => {
    if (event.shiftKey) {
      event.preventDefault();
      event.stopPropagation();
      onEdit(id);
    }
  }, []);

  return {
    handleRowClick,
    handleShiftClick
  };
}