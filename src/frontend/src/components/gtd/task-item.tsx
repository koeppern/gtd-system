'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { 
  CheckCircleIcon,
  ClockIcon,
  FolderIcon,
  CalendarIcon,
  BookOpenIcon,
  PauseIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid';
import type { Task } from '@/types';
import { cn, getPriorityInfo, getTaskStatus, formatRelativeDate } from '@/lib/utils';

interface TaskItemProps {
  task: Task;
  onComplete?: () => void;
  onEdit?: () => void;
  isCompleting?: boolean;
  showProject?: boolean;
  showField?: boolean;
  showDueDate?: boolean;
  compact?: boolean;
}

export function TaskItem({
  task,
  onComplete,
  onEdit,
  isCompleting = false,
  showProject = true,
  showField = true,
  showDueDate = true,
  compact = false,
}: TaskItemProps) {
  const priorityInfo = getPriorityInfo(task.priority);
  const statusInfo = getTaskStatus(task);

  const handleToggleComplete = () => {
    if (!task.is_done && onComplete) {
      onComplete();
    }
  };

  return (
    <div
      className={cn(
        'group flex items-start gap-3 rounded-lg border p-3 transition-colors hover:bg-accent/50',
        task.is_done && 'opacity-60',
        compact && 'p-2',
        task.priority && task.priority <= 2 && 'border-l-4 border-l-red-500',
        task.priority === 3 && 'border-l-4 border-l-yellow-500',
        task.priority && task.priority >= 4 && 'border-l-4 border-l-green-500'
      )}
    >
      {/* Completion checkbox */}
      <Button
        variant="ghost"
        size="icon-sm"
        className={cn(
          'mt-0.5 shrink-0 rounded-full',
          task.is_done && 'text-green-600',
          isCompleting && 'animate-pulse'
        )}
        onClick={handleToggleComplete}
        disabled={task.is_done || isCompleting}
      >
        {task.is_done ? (
          <CheckCircleIconSolid className="h-5 w-5" />
        ) : (
          <CheckCircleIcon className="h-5 w-5" />
        )}
      </Button>

      {/* Task content */}
      <div className="flex-1 min-w-0">
        {/* Task name and status */}
        <div className="flex items-start justify-between gap-2">
          <h3
            className={cn(
              'font-medium text-sm leading-relaxed cursor-pointer',
              task.is_done && 'line-through text-muted-foreground'
            )}
            onClick={onEdit}
          >
            {task.task_name}
          </h3>
          
          {/* Status indicators */}
          <div className="flex items-center gap-1 shrink-0">
            {task.wait_for && (
              <div className="flex items-center text-xs text-yellow-600">
                <PauseIcon className="h-3 w-3 mr-1" />
                <span className="hidden sm:inline">Waiting</span>
              </div>
            )}
            {task.is_reading && (
              <div className="flex items-center text-xs text-blue-600">
                <BookOpenIcon className="h-3 w-3 mr-1" />
                <span className="hidden sm:inline">Reading</span>
              </div>
            )}
            {task.postponed && (
              <div className="flex items-center text-xs text-gray-600">
                <ClockIcon className="h-3 w-3 mr-1" />
                <span className="hidden sm:inline">Postponed</span>
              </div>
            )}
          </div>
        </div>

        {/* Task notes */}
        {task.task_notes && !compact && (
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {task.task_notes}
          </p>
        )}

        {/* Metadata */}
        <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
          {/* Priority */}
          {task.priority && (
            <span className={cn(
              'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
              priorityInfo.bgColor,
              priorityInfo.color
            )}>
              P{task.priority}
            </span>
          )}

          {/* Field */}
          {showField && task.field && (
            <span className="inline-flex items-center">
              <div className="h-2 w-2 rounded-full bg-blue-500 mr-1" />
              {task.field.name}
            </span>
          )}

          {/* Project */}
          {showProject && task.project && (
            <span className="inline-flex items-center">
              <FolderIcon className="h-3 w-3 mr-1" />
              {task.project.project_name}
            </span>
          )}

          {/* Due date */}
          {showDueDate && task.do_on_date && (
            <span className={cn(
              'inline-flex items-center',
              statusInfo.status === 'overdue' && 'text-red-600 font-medium'
            )}>
              <CalendarIcon className="h-3 w-3 mr-1" />
              {formatRelativeDate(task.do_on_date)}
            </span>
          )}

          {/* Schedule indicators */}
          {task.do_today && (
            <span className="inline-flex items-center text-blue-600">
              <ClockIcon className="h-3 w-3 mr-1" />
              Today
            </span>
          )}
          
          {task.do_this_week && !task.do_today && (
            <span className="inline-flex items-center text-purple-600">
              <CalendarIcon className="h-3 w-3 mr-1" />
              This Week
            </span>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" onClick={onEdit}>
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </Button>
      </div>
    </div>
  );
}