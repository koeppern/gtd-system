'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  CheckCircleIcon,
  ClockIcon,
  EllipsisVerticalIcon,
  ListBulletIcon,
  FolderIcon,
  BookOpenIcon,
  PauseIcon,
  CalendarDaysIcon,
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

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="animate-pulse">
                <div className="h-6 bg-muted rounded mb-2" />
                <div className="h-4 bg-muted rounded w-1/3" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const sortedTasks = [...tasks].sort((a, b) => {
    let aValue: string | number;
    let bValue: string | number;

    switch (sortBy) {
      case 'name':
        aValue = (a.task_name || a.name || '').toLowerCase();
        bValue = (b.task_name || b.name || '').toLowerCase();
        break;
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

  const handleSort = (newSortBy: 'name' | 'project' | 'priority' | 'created' | 'updated') => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  };

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
      {/* Table Header */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-center py-4 px-6 font-semibold text-muted-foreground w-16">
                    #
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-muted-foreground">
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
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-muted-foreground">
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
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-muted-foreground">
                    Status
                  </th>
                  <th className="text-center py-4 px-6 font-semibold text-muted-foreground">
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
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-muted-foreground">
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
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-muted-foreground">
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
                  </th>
                  <th className="w-20 py-4 px-6"></th>
                </tr>
              </thead>
              <tbody>
                {sortedTasks.map((task, index) => (
                  <tr 
                    key={task.id} 
                    className="border-b border-border hover:bg-muted/50 transition-colors"
                  >
                    <td className="py-4 px-6 text-center text-muted-foreground">
                      {index + 1}
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-3">
                        {isCompleted(task) ? (
                          <CheckCircleIconSolid className="h-5 w-5 text-green-600" />
                        ) : (
                          <ListBulletIconSolid className="h-5 w-5 text-blue-600" />
                        )}
                        <div>
                          <div className="font-medium text-foreground">
                            {task.task_name || task.name || `Task ${task.id}`}
                          </div>
                          <div className="flex items-center space-x-2 mt-1">
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
                              <BookOpenIcon className="h-3 w-3 text-muted-foreground" />
                            )}
                            {task.wait_for && (
                              <PauseIcon className="h-3 w-3 text-orange-500" />
                            )}
                            {task.postponed && (
                              <ClockIcon className="h-3 w-3 text-red-500" />
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      {task.project_name ? (
                        <div className="flex items-center space-x-2">
                          <FolderIcon className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">{task.project_name}</span>
                        </div>
                      ) : (
                        <span className="text-muted-foreground italic">No project</span>
                      )}
                    </td>
                    <td className="py-4 px-6">
                      {isCompleted(task) ? (
                        <Badge variant="default" className="bg-green-100 text-green-800">
                          Completed
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-blue-600 border-blue-200">
                          Active
                        </Badge>
                      )}
                    </td>
                    <td className="py-4 px-6 text-center text-muted-foreground">
                      {task.priority || '-'}
                    </td>
                    <td className="py-4 px-6 text-muted-foreground">
                      {new Date(task.created_at).toISOString().split('T')[0]}
                    </td>
                    <td className="py-4 px-6 text-muted-foreground">
                      {new Date(task.updated_at).toISOString().split('T')[0]}
                    </td>
                    <td className="py-4 px-6">
                      <Button variant="ghost" size="sm">
                        <EllipsisVerticalIcon className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Summary */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div>
          Showing {sortedTasks.length} {showCompleted ? 'tasks' : 'active tasks'}
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <ListBulletIconSolid className="h-4 w-4 text-blue-600" />
            <span>{sortedTasks.filter(t => !isCompleted(t)).length} Active</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircleIconSolid className="h-4 w-4 text-green-600" />
            <span>{sortedTasks.filter(t => isCompleted(t)).length} Completed</span>
          </div>
        </div>
      </div>
    </div>
  );
}