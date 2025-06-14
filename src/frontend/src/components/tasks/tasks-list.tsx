'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { InlineEdit } from '@/components/ui/inline-edit';
import { ResizableTable, useResizableColumns } from '@/components/ui/resizable-table';
import { api } from '@/lib/api';
import { 
  ClockIcon,
  EllipsisVerticalIcon,
  ListBulletIcon,
  FolderIcon,
  BookOpenIcon,
  PauseIcon,
} from '@heroicons/react/24/outline';
import { 
  CheckCircleIcon as CheckCircleIconSolid,
  ListBulletIcon as ListBulletIconSolid 
} from '@heroicons/react/24/solid';

interface Task {
  id: number;
  task_name?: string;
  name?: string; // Backend might send 'name' instead of 'task_name'
  project_id?: number;
  project_name?: string;
  done_at?: string;
  do_today?: boolean;
  do_this_week?: boolean;
  is_reading?: boolean;
  wait_for?: boolean;
  postponed?: boolean;
  reviewed?: boolean;
  do_on_date?: string;
  field_id?: number;
  priority?: number;
  created_at: string;
  updated_at: string;
}

interface TasksListProps {
  tasks: Task[];
  isLoading: boolean;
  showCompleted: boolean;
}

export function TasksList({ tasks, isLoading, showCompleted }: TasksListProps) {
  const [sortBy, setSortBy] = useState<'name' | 'project' | 'priority' | 'created' | 'updated'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const queryClient = useQueryClient();

  const handleSort = (newSortBy: 'name' | 'project' | 'priority' | 'created' | 'updated') => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  };

  // Define resizable columns
  const defaultColumns = [
    { key: 'no', title: 'No', width: 60, minWidth: 40, maxWidth: 100 },
    { key: 'name', title: (
      <button
        onClick={() => handleSort('name')}
        className="flex items-center space-x-2 hover:text-foreground transition-colors"
      >
        <span>Task Name</span>
        {sortBy === 'name' && (
          <span className="text-xs">
            {sortOrder === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </button>
    ), width: 300, minWidth: 150, maxWidth: 500 },
    { key: 'project', title: (
      <button
        onClick={() => handleSort('project')}
        className="flex items-center space-x-2 hover:text-foreground transition-colors"
      >
        <span>Project</span>
        {sortBy === 'project' && (
          <span className="text-xs">
            {sortOrder === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </button>
    ), width: 180, minWidth: 100, maxWidth: 300 },
    { key: 'status', title: 'Status', width: 120, minWidth: 80, maxWidth: 200 },
    { key: 'priority', title: (
      <button
        onClick={() => handleSort('priority')}
        className="flex items-center justify-center space-x-2 hover:text-foreground transition-colors w-full"
      >
        <span>Priority</span>
        {sortBy === 'priority' && (
          <span className="text-xs">
            {sortOrder === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </button>
    ), width: 100, minWidth: 70, maxWidth: 150 },
    { key: 'created', title: (
      <button
        onClick={() => handleSort('created')}
        className="flex items-center space-x-2 hover:text-foreground transition-colors"
      >
        <span>Created</span>
        {sortBy === 'created' && (
          <span className="text-xs">
            {sortOrder === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </button>
    ), width: 120, minWidth: 100, maxWidth: 180 },
    { key: 'updated', title: (
      <button
        onClick={() => handleSort('updated')}
        className="flex items-center space-x-2 hover:text-foreground transition-colors"
      >
        <span>Last Updated</span>
        {sortBy === 'updated' && (
          <span className="text-xs">
            {sortOrder === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </button>
    ), width: 140, minWidth: 100, maxWidth: 200 },
    { key: 'actions', title: '', width: 80, minWidth: 60, maxWidth: 120 }
  ];

  const { columns, handleColumnResize } = useResizableColumns('tasks', defaultColumns);

  // Mutation for updating task name
  const updateTaskMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      return api.tasks.update(id, data);
    },
    onSuccess: () => {
      // Invalidate and refetch tasks list
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  // Sort tasks
  const sortedTasks = [...tasks].sort((a, b) => {
    let aValue: any;
    let bValue: any;

    switch (sortBy) {
      case 'project':
        aValue = (a.project_name || '').toLowerCase();
        bValue = (b.project_name || '').toLowerCase();
        break;
      case 'priority':
        aValue = a.priority || 0;
        bValue = b.priority || 0;
        break;
      case 'created':
        aValue = new Date(a.created_at).getTime();
        bValue = new Date(b.created_at).getTime();
        break;
      case 'updated':
        aValue = new Date(a.updated_at).getTime();
        bValue = new Date(b.updated_at).getTime();
        break;
      default:
        aValue = (a.task_name || a.name || '').toLowerCase();
        bValue = (b.task_name || b.name || '').toLowerCase();
    }

    if (sortOrder === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  const isCompleted = (task: Task) => {
    return task.done_at !== null;
  };

  if (tasks.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <ListBulletIcon className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">
            {showCompleted ? 'No tasks found' : 'No active tasks'}
          </h3>
          <p className="text-muted-foreground text-center max-w-md">
            {showCompleted 
              ? 'No tasks match your current search criteria.'
              : 'You don\'t have any active tasks yet. Create your first task to get started.'
            }
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="text-sm text-muted-foreground">
        Showing {tasks.length} {showCompleted ? 'total' : 'active'} tasks
      </div>

      {/* Resizable Table */}
      <Card>
        <CardContent className="p-0">
          <ResizableTable 
            columns={columns} 
            onColumnResize={handleColumnResize}
            className="text-sm"
          >
            {sortedTasks.map((task, index) => (
              <tr 
                key={task.id} 
                className="border-b border-border hover:bg-muted/50 transition-colors"
              >
                <td className="py-3 px-4 text-center text-muted-foreground">
                  {index + 1}
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-3">
                    {isCompleted(task) ? (
                      <CheckCircleIconSolid className="h-5 w-5 text-green-600 flex-shrink-0" />
                    ) : (
                      <ListBulletIconSolid className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <InlineEdit
                        value={task.task_name || task.name || `Task ${task.id}`}
                        onSave={async (newValue) => {
                          await updateTaskMutation.mutateAsync({
                            id: task.id,
                            data: { task_name: newValue }
                          });
                        }}
                        className="font-medium text-foreground break-words"
                        placeholder="Task name"
                        disabled={updateTaskMutation.isPending}
                      />
                      <div className="flex items-center space-x-2 mt-1 flex-wrap">
                        {task.do_today && (
                          <Badge variant="secondary" className="text-xs">
                            Today
                          </Badge>
                        )}
                        {task.do_this_week && !task.do_today && (
                          <Badge variant="secondary" className="text-xs">
                            This Week
                          </Badge>
                        )}
                        {task.is_reading && (
                          <Badge variant="outline" className="text-xs">
                            <BookOpenIcon className="h-3 w-3 mr-1" />
                            Reading
                          </Badge>
                        )}
                        {task.wait_for && (
                          <Badge variant="outline" className="text-xs">
                            <ClockIcon className="h-3 w-3 mr-1" />
                            Waiting
                          </Badge>
                        )}
                        {task.postponed && (
                          <Badge variant="outline" className="text-xs">
                            <PauseIcon className="h-3 w-3 mr-1" />
                            Postponed
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2">
                    {task.project_name && (
                      <>
                        <FolderIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <span className="text-sm text-muted-foreground truncate">
                          {task.project_name}
                        </span>
                      </>
                    )}
                  </div>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2 flex-wrap">
                    {isCompleted(task) ? (
                      <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                        Completed
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-xs">
                        Active
                      </Badge>
                    )}
                  </div>
                </td>
                <td className="py-3 px-4 text-center">
                  <span className="text-sm font-medium">
                    {task.priority || 0}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className="text-xs text-muted-foreground">
                    {new Date(task.created_at).toLocaleDateString()}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className="text-xs text-muted-foreground">
                    {new Date(task.updated_at).toLocaleDateString()}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 opacity-50 hover:opacity-100"
                  >
                    <EllipsisVerticalIcon className="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </ResizableTable>
        </CardContent>
      </Card>
    </div>
  );
}