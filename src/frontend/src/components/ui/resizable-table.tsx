'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

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
}

export function ResizableTable({ 
  children, 
  className, 
  columns, 
  onColumnResize 
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
                <div className="px-4 py-3">
                  {col.title}
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

// Hook to persist column widths in localStorage
export function useResizableColumns(tableKey: string, defaultColumns: ResizableTableProps['columns']) {
  const [columns, setColumns] = useState(defaultColumns);

  useEffect(() => {
    const stored = localStorage.getItem(`table-${tableKey}-widths`);
    if (stored) {
      try {
        const widths = JSON.parse(stored);
        setColumns(cols => cols.map(col => ({
          ...col,
          width: widths[col.key] || col.width || 150
        })));
      } catch (e) {
        console.warn('Failed to parse stored column widths');
      }
    }
  }, [tableKey]);

  const handleColumnResize = (columnKey: string, width: number) => {
    const updatedColumns = columns.map(col => 
      col.key === columnKey ? { ...col, width } : col
    );
    setColumns(updatedColumns);

    // Save to localStorage
    const widths = updatedColumns.reduce((acc, col) => {
      acc[col.key] = col.width || 150;
      return acc;
    }, {} as Record<string, number>);
    
    localStorage.setItem(`table-${tableKey}-widths`, JSON.stringify(widths));
  };

  return { columns, handleColumnResize };
}