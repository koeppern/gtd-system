'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

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
  onColumnResize?: (columnKey: string, width: number) => void;
  onColumnReorder?: (fromIndex: number, toIndex: number) => void;
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
  const tableRef = useRef<HTMLTableElement>(null);
  const startX = useRef(0);
  const startWidth = useRef(0);

  const handleMoveLeft = (index: number) => {
    if (index > 0 && onColumnReorder) {
      onColumnReorder(index, index - 1);
    }
  };

  const handleMoveRight = (index: number) => {
    if (index < columns.length - 1 && onColumnReorder) {
      onColumnReorder(index, index + 1);
    }
  };

  const handleMouseDown = (e: React.MouseEvent, columnKey: string) => {
    e.preventDefault();
    setResizing(columnKey);
    startX.current = e.clientX;
    startWidth.current = columnWidths[columnKey];
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!resizing) return;
    
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
  };

  const handleMouseUp = () => {
    if (resizing && onColumnResize) {
      onColumnResize(resizing, columnWidths[resizing]);
    }
    setResizing(null);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  // Create style object for column widths
  const columnStyles = columns.reduce((styles, col, index) => {
    styles[`--col-${index}-width`] = `${columnWidths[col.key]}px`;
    return styles;
  }, {} as Record<string, string>);

  return (
    <div className="overflow-x-auto">
      <table 
        ref={tableRef}
        className={cn("w-full table-fixed", className)}
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
                      "absolute top-0 right-0 w-1 h-full cursor-col-resize",
                      "hover:bg-primary/20 transition-colors",
                      resizing === col.key && "bg-primary/40"
                    )}
                    onMouseDown={(e) => handleMouseDown(e, col.key)}
                  >
                    <div className="absolute right-0 top-0 w-4 h-full -mr-2" />
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

// Hook to persist column widths and order in localStorage
export function useResizableColumns(tableKey: string, defaultColumns: ResizableTableProps['columns']) {
  const [columns, setColumns] = useState(defaultColumns);

  useEffect(() => {
    // Load stored column configuration
    const storedWidths = localStorage.getItem(`table-${tableKey}-widths`);
    const storedOrder = localStorage.getItem(`table-${tableKey}-order`);
    
    let updatedColumns = [...defaultColumns];
    
    // Apply stored order first
    if (storedOrder) {
      try {
        const order = JSON.parse(storedOrder);
        const orderedColumns = order
          .map((key: string) => defaultColumns.find(col => col.key === key))
          .filter(Boolean);
        
        // Add any new columns that weren't in the stored order
        const existingKeys = new Set(order);
        const newColumns = defaultColumns.filter(col => !existingKeys.has(col.key));
        
        updatedColumns = [...orderedColumns, ...newColumns];
      } catch (e) {
        console.warn('Failed to parse stored column order');
      }
    }
    
    // Apply stored widths
    if (storedWidths) {
      try {
        const widths = JSON.parse(storedWidths);
        updatedColumns = updatedColumns.map(col => ({
          ...col,
          width: widths[col.key] || col.width || 150
        }));
      } catch (e) {
        console.warn('Failed to parse stored column widths');
      }
    }
    
    setColumns(updatedColumns);
  }, [tableKey]);

  const handleColumnResize = (columnKey: string, width: number) => {
    const updatedColumns = columns.map(col => 
      col.key === columnKey ? { ...col, width } : col
    );
    setColumns(updatedColumns);

    // Save widths to localStorage
    const widths = updatedColumns.reduce((acc, col) => {
      acc[col.key] = col.width || 150;
      return acc;
    }, {} as Record<string, number>);
    
    localStorage.setItem(`table-${tableKey}-widths`, JSON.stringify(widths));
  };

  const handleColumnReorder = (fromIndex: number, toIndex: number) => {
    const newColumns = [...columns];
    const [movedColumn] = newColumns.splice(fromIndex, 1);
    newColumns.splice(toIndex, 0, movedColumn);
    
    setColumns(newColumns);
    
    // Save order to localStorage
    const order = newColumns.map(col => col.key);
    localStorage.setItem(`table-${tableKey}-order`, JSON.stringify(order));
  };

  return { columns, handleColumnResize, handleColumnReorder };
}