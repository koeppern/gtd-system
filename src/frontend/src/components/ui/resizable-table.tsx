'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

interface ResizableTableProps {
  children: React.ReactNode;
  className?: string;
  columns: {
    key: string;
    title: React.ReactNode;
    width?: number;
    minWidth?: number;
    maxWidth?: number;
  }[];
  onColumnResize?: (columnKey: string, width: number) => Promise<void>;
  onColumnReorder?: (fromIndex: number, toIndex: number) => Promise<void>;
}

export function ResizableTable({ 
  children, 
  className, 
  columns, 
  onColumnResize,
  onColumnReorder
}: ResizableTableProps) {
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>(() => {
    const initialWidths: Record<string, number> = {};
    columns.forEach(col => {
      initialWidths[col.key] = col.width || 150;
    });
    return initialWidths;
  });

  const [resizing, setResizing] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const tableRef = useRef<HTMLTableElement>(null);
  const startX = useRef(0);
  const startWidth = useRef(0);

  const handleMoveLeft = async (index: number) => {
    if (index > 0 && onColumnReorder) {
      try {
        await onColumnReorder(index, index - 1);
      } catch (error) {
        toast.error(error instanceof Error ? error.message : 'Failed to reorder columns');
      }
    }
  };

  const handleMoveRight = async (index: number) => {
    if (index < columns.length - 1 && onColumnReorder) {
      try {
        await onColumnReorder(index, index + 1);
      } catch (error) {
        toast.error(error instanceof Error ? error.message : 'Failed to reorder columns');
      }
    }
  };

  const handleMouseDown = (e: React.MouseEvent, columnKey: string) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Mouse down on resize handle for column:', columnKey);
    setResizing(columnKey);
    setIsDragging(true);
    startX.current = e.clientX;
    startWidth.current = columnWidths[columnKey];
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!resizing || !isDragging) return;
    
    console.log('Mouse move - resizing:', resizing, 'isDragging:', isDragging);
    
    const diff = e.clientX - startX.current;
    const newWidth = Math.max(50, startWidth.current + diff); // Minimum 50px
    
    const column = columns.find(col => col.key === resizing);
    if (column) {
      const clampedWidth = Math.min(
        Math.max(newWidth, column.minWidth || 50),
        column.maxWidth || 500
      );
      
      setColumnWidths(prev => ({
        ...prev,
        [resizing]: clampedWidth
      }));
    }
  }, [resizing, isDragging, columns]);

  const handleMouseUp = useCallback(async () => {
    console.log('Mouse up - resizing:', resizing);
    if (resizing && onColumnResize) {
      const currentWidth = columnWidths[resizing];
      try {
        await onColumnResize(resizing, currentWidth);
      } catch (error) {
        toast.error(error instanceof Error ? error.message : 'Failed to save column width');
      }
    }
    setResizing(null);
    setIsDragging(false);
  }, [resizing, onColumnResize, columnWidths]);

  // Attach and detach event listeners when resizing state changes
  useEffect(() => {
    if (resizing && isDragging) {
      console.log('Adding event listeners for resizing:', resizing);
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      
      return () => {
        console.log('Removing event listeners for resizing:', resizing);
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [resizing, isDragging, handleMouseMove, handleMouseUp]);

  // Cleanup event listeners on unmount
  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  // Create style object for column widths
  const columnStyles = columns.reduce((styles, col, index) => {
    styles[`--col-${index}-width`] = `${columnWidths[col.key]}px`;
    return styles;
  }, {} as Record<string, string>);

  return (
    <div className="overflow-x-auto">
      <table 
        ref={tableRef}
        className={cn("w-full table-fixed", className, isDragging && "select-none")}
        style={columnStyles as React.CSSProperties}
      >
        <colgroup>
          {columns.map((col, index) => (
            <col 
              key={col.key} 
              style={{ width: `var(--col-${index}-width)` }} 
            />
          ))}
        </colgroup>
        <thead>
          <tr>
            {columns.map((col, index) => (
              <th 
                key={col.key}
                className="relative border-b border-border text-left"
              >
                <div className="px-4 py-3 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {/* Move Left Arrow */}
                    <button
                      onClick={() => handleMoveLeft(index)}
                      disabled={index === 0}
                      className={cn(
                        "p-1 rounded hover:bg-muted transition-colors",
                        index === 0 
                          ? "opacity-30 cursor-not-allowed" 
                          : "opacity-60 hover:opacity-100"
                      )}
                      title="Move column left"
                    >
                      <ChevronLeftIcon className="h-3 w-3" />
                    </button>
                    
                    {/* Column Title */}
                    <div className="flex-1">
                      {col.title}
                    </div>
                    
                    {/* Move Right Arrow */}
                    <button
                      onClick={() => handleMoveRight(index)}
                      disabled={index === columns.length - 1}
                      className={cn(
                        "p-1 rounded hover:bg-muted transition-colors",
                        index === columns.length - 1 
                          ? "opacity-30 cursor-not-allowed" 
                          : "opacity-60 hover:opacity-100"
                      )}
                      title="Move column right"
                    >
                      <ChevronRightIcon className="h-3 w-3" />
                    </button>
                  </div>
                </div>
                
                {/* Resize Handle */}
                {index < columns.length - 1 && (
                  <div
                    className={cn(
                      "absolute top-0 right-0 w-2 h-full cursor-col-resize bg-transparent",
                      "hover:bg-primary/30 transition-colors border-r-2 border-transparent",
                      "hover:border-primary/50",
                      resizing === col.key && "bg-primary/40 border-primary"
                    )}
                    onMouseDown={(e) => handleMouseDown(e, col.key)}
                    title="Drag to resize column"
                  >
                    {/* Expanded clickable area */}
                    <div className="absolute right-0 top-0 w-6 h-full -mr-3 cursor-col-resize" />
                  </div>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {children}
        </tbody>
      </table>
    </div>
  );
}

// Hook to persist column widths and order in database
export function useResizableColumns(tableKey: string, defaultColumns: ResizableTableProps['columns']) {
  const [columns, setColumns] = useState(defaultColumns);
  const [isLoading, setIsLoading] = useState(true);

  // Import api dynamically to avoid circular imports
  const loadSettings = async () => {
    try {
      const { api } = await import('@/lib/api');
      
      // Load stored column configuration from database
      const [widthsSetting, orderSetting] = await Promise.all([
        api.userSettings.get(`table-${tableKey}-widths`).catch(() => null),
        api.userSettings.get(`table-${tableKey}-order`).catch(() => null)
      ]);
      
      let updatedColumns = [...defaultColumns];
      
      // Apply stored order first
      if (orderSetting && Array.isArray(orderSetting)) {
        try {
          const orderedColumns = orderSetting
            .map((key: string) => defaultColumns.find(col => col.key === key))
            .filter(Boolean);
          
          // Add any new columns that weren't in the stored order
          const existingKeys = new Set(orderSetting);
          const newColumns = defaultColumns.filter(col => !existingKeys.has(col.key));
          
          updatedColumns = [...orderedColumns, ...newColumns];
        } catch (e) {
          console.warn('Failed to parse stored column order');
        }
      }
      
      // Apply stored widths
      if (widthsSetting && typeof widthsSetting === 'object') {
        try {
          updatedColumns = updatedColumns.map(col => ({
            ...col,
            width: widthsSetting[col.key] || col.width || 150
          }));
        } catch (e) {
          console.warn('Failed to parse stored column widths');
        }
      }
      
      setColumns(updatedColumns);
    } catch (error) {
      console.warn('Failed to load user settings, using defaults:', error);
      setColumns(defaultColumns);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, [tableKey]);

  const handleColumnResize = async (columnKey: string, width: number) => {
    const updatedColumns = columns.map(col => 
      col.key === columnKey ? { ...col, width } : col
    );
    setColumns(updatedColumns);

    // Save widths to database
    const widths = updatedColumns.reduce((acc, col) => {
      acc[col.key] = col.width || 150;
      return acc;
    }, {} as Record<string, number>);
    
    try {
      const { api } = await import('@/lib/api');
      await api.userSettings.update(`table-${tableKey}-widths`, widths);
    } catch (error) {
      console.error('Failed to save column widths to database:', error);
      // Show user error instead of silent fallback
      throw new Error(`Database connection failed: Unable to save table settings. Please check your connection and try again.`);
    }
  };

  const handleColumnReorder = async (fromIndex: number, toIndex: number) => {
    const newColumns = [...columns];
    const [movedColumn] = newColumns.splice(fromIndex, 1);
    newColumns.splice(toIndex, 0, movedColumn);
    
    setColumns(newColumns);
    
    // Save order to database
    const order = newColumns.map(col => col.key);
    
    try {
      const { api } = await import('@/lib/api');
      await api.userSettings.update(`table-${tableKey}-order`, order);
    } catch (error) {
      console.error('Failed to save column order to database:', error);
      // Show user error instead of silent fallback
      throw new Error(`Database connection failed: Unable to save table settings. Please check your connection and try again.`);
    }
  };

  return { columns, handleColumnResize, handleColumnReorder, isLoading };
}