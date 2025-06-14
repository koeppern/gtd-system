'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface InlineEditProps {
  value: string;
  onSave: (newValue: string) => Promise<void>;
  onCancel?: () => void;
  className?: string;
  inputClassName?: string;
  placeholder?: string;
  disabled?: boolean;
  multiline?: boolean;
}

export function InlineEdit({
  value,
  onSave,
  onCancel,
  className,
  inputClassName,
  placeholder,
  disabled = false,
  multiline = false,
}: InlineEditProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  // Update edit value when prop value changes
  useEffect(() => {
    setEditValue(value);
  }, [value]);

  // Focus input when editing starts
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleDoubleClick = () => {
    if (!disabled) {
      setIsEditing(true);
      setEditValue(value);
    }
  };

  const handleSave = async () => {
    if (editValue.trim() === value.trim()) {
      // No changes, just exit edit mode
      setIsEditing(false);
      return;
    }

    setIsLoading(true);
    try {
      await onSave(editValue.trim());
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to save:', error);
      // Reset to original value on error
      setEditValue(value);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
    onCancel?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !multiline) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Enter' && multiline && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancel();
    }
  };

  const handleBlur = () => {
    // Save on blur (when clicking outside)
    if (isEditing && !isLoading) {
      handleSave();
    }
  };

  if (isEditing) {
    const InputComponent = multiline ? 'textarea' : 'input';
    
    return (
      <InputComponent
        ref={inputRef as any}
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        placeholder={placeholder}
        disabled={isLoading}
        className={cn(
          'w-full bg-background border border-input rounded px-2 py-1',
          'focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          multiline && 'min-h-[2.5rem] resize-vertical',
          inputClassName
        )}
        {...(multiline && { rows: 2 })}
      />
    );
  }

  return (
    <div
      onDoubleClick={handleDoubleClick}
      className={cn(
        'cursor-text hover:bg-muted/50 rounded px-2 py-1 transition-colors',
        'min-h-[2rem] flex items-center',
        disabled && 'cursor-not-allowed opacity-50',
        className
      )}
      title={disabled ? undefined : 'Double-click to edit'}
    >
      {value || (
        <span className="text-muted-foreground italic">
          {placeholder || 'Click to edit'}
        </span>
      )}
    </div>
  );
}