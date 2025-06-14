'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDownIcon, XMarkIcon, CheckIcon } from '@heroicons/react/24/outline';

export interface GroupByOption {
  key: string;
  label: string;
  enabled: boolean;
}

interface GroupByDropdownProps {
  options: GroupByOption[];
  selectedGroupBy: string | null;
  onGroupByChange: (groupBy: string | null) => void;
  className?: string;
}

export function GroupByDropdown({
  options,
  selectedGroupBy,
  onGroupByChange,
  className
}: GroupByDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleClear = () => {
    onGroupByChange(null);
    setIsOpen(false);
  };

  const handleOptionSelect = (optionKey: string) => {
    if (selectedGroupBy === optionKey) {
      onGroupByChange(null); // Deselect if already selected
    } else {
      onGroupByChange(optionKey);
    }
    setIsOpen(false);
  };

  const selectedOption = options.find(opt => opt.key === selectedGroupBy);

  return (
    <div className={cn("relative inline-block", className)} ref={dropdownRef}>
      {/* Dropdown Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center space-x-2 px-3 py-2 border border-border rounded-md",
          "bg-background text-foreground text-sm font-medium",
          "hover:bg-muted transition-colors",
          "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
          isOpen && "ring-2 ring-ring border-transparent"
        )}
      >
        <span className="text-muted-foreground">Group by:</span>
        <span className="font-normal">
          {selectedOption ? selectedOption.label : 'None'}
        </span>
        <ChevronDownIcon 
          className={cn(
            "h-4 w-4 text-muted-foreground transition-transform",
            isOpen && "rotate-180"
          )} 
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className={cn(
          "absolute right-0 top-full mt-1 w-56 z-50",
          "bg-background border border-border rounded-md shadow-lg",
          "py-1"
        )}>
          {/* Clear Option */}
          <button
            onClick={handleClear}
            className={cn(
              "w-full flex items-center space-x-3 px-3 py-2 text-sm",
              "hover:bg-muted transition-colors text-left",
              !selectedGroupBy && "bg-muted"
            )}
          >
            <XMarkIcon className="h-4 w-4 text-muted-foreground" />
            <span>No grouping</span>
            {!selectedGroupBy && (
              <CheckIcon className="h-4 w-4 text-primary ml-auto" />
            )}
          </button>

          {/* Separator */}
          <div className="border-t border-border my-1" />

          {/* Group By Options */}
          {options.map((option) => (
            <button
              key={option.key}
              onClick={() => handleOptionSelect(option.key)}
              disabled={!option.enabled}
              className={cn(
                "w-full flex items-center space-x-3 px-3 py-2 text-sm text-left",
                "transition-colors",
                option.enabled 
                  ? "hover:bg-muted" 
                  : "opacity-50 cursor-not-allowed",
                selectedGroupBy === option.key && "bg-muted"
              )}
            >
              <div className="w-4 h-4 flex items-center justify-center">
                {selectedGroupBy === option.key && (
                  <CheckIcon className="h-4 w-4 text-primary" />
                )}
              </div>
              <span className={cn(
                option.enabled ? "text-foreground" : "text-muted-foreground"
              )}>
                {option.label}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Hook for grouping data
export function useGroupBy<T>(
  data: T[], 
  groupByKey: string | null, 
  getGroupValue: (item: T, key: string) => string | number | null
) {
  const groupedData = React.useMemo(() => {
    if (!groupByKey || !data.length) {
      return [{ groupName: null, items: data }];
    }

    const groups: Record<string, T[]> = {};
    
    data.forEach(item => {
      const groupValue = getGroupValue(item, groupByKey);
      const groupName = groupValue?.toString() || 'Ungrouped';
      
      if (!groups[groupName]) {
        groups[groupName] = [];
      }
      groups[groupName].push(item);
    });

    // Sort groups by name and return as array
    return Object.entries(groups)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([groupName, items]) => ({ groupName, items }));
  }, [data, groupByKey, getGroupValue]);

  return groupedData;
}