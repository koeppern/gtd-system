'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  FolderIcon,
  CheckCircleIcon,
  ClockIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';
import { 
  FolderIcon as FolderIconSolid,
  CheckCircleIcon as CheckCircleIconSolid 
} from '@heroicons/react/24/solid';

interface Project {
  id: number;
  project_name?: string;
  name?: string; // Backend sends 'name' instead of 'project_name'
  done_status?: boolean;
  done_at?: string;
  field_id?: number;
  do_this_week?: boolean;
  task_count?: number;
  created_at: string;
  updated_at: string;
}

interface ProjectsListProps {
  projects: Project[];
  isLoading: boolean;
  showCompleted: boolean;
}

export function ProjectsList({ projects, isLoading, showCompleted }: ProjectsListProps) {
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'tasks' | 'created' | 'updated'>('name');
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

  const sortedProjects = [...projects].sort((a, b) => {
    let aValue: string | number;
    let bValue: string | number;

    switch (sortBy) {
      case 'name':
        aValue = (a.project_name || a.name || '').toLowerCase();
        bValue = (b.project_name || b.name || '').toLowerCase();
        break;
      case 'status':
        aValue = a.done_status ? 1 : 0;
        bValue = b.done_status ? 1 : 0;
        break;
      case 'tasks':
        aValue = a.task_count || 0;
        bValue = b.task_count || 0;
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
        aValue = (a.project_name || a.name || '').toLowerCase();
        bValue = (b.project_name || b.name || '').toLowerCase();
    }

    if (sortOrder === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  const handleSort = (newSortBy: 'name' | 'status' | 'tasks' | 'created' | 'updated') => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  };

  const isCompleted = (project: Project) => {
    return project.done_at !== null || project.done_status === true;
  };

  if (projects.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FolderIcon className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">
            {showCompleted ? 'No projects found' : 'No active projects'}
          </h3>
          <p className="text-muted-foreground text-center max-w-md">
            {showCompleted 
              ? 'No projects match your current search criteria.'
              : 'You don\'t have any active projects yet. Create your first project to get started.'
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
                    No
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-muted-foreground">
                    <button
                      onClick={() => handleSort('name')}
                      className="flex items-center space-x-2 hover:text-foreground transition-colors"
                    >
                      <span>Project Name</span>
                      {sortBy === 'name' && (
                        <span className="text-xs">
                          {sortOrder === 'asc' ? '↑' : '↓'}
                        </span>
                      )}
                    </button>
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-muted-foreground">
                    <button
                      onClick={() => handleSort('status')}
                      className="flex items-center space-x-2 hover:text-foreground transition-colors"
                    >
                      <span>Status</span>
                      {sortBy === 'status' && (
                        <span className="text-xs">
                          {sortOrder === 'asc' ? '↑' : '↓'}
                        </span>
                      )}
                    </button>
                  </th>
                  <th className="text-center py-4 px-6 font-semibold text-muted-foreground">
                    <button
                      onClick={() => handleSort('tasks')}
                      className="flex items-center justify-center space-x-2 hover:text-foreground transition-colors w-full"
                    >
                      <span>Tasks</span>
                      {sortBy === 'tasks' && (
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
                {sortedProjects.map((project, index) => (
                  <tr 
                    key={project.id} 
                    className="border-b border-border hover:bg-muted/50 transition-colors"
                  >
                    <td className="py-4 px-6 text-center text-muted-foreground">
                      {index + 1}
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-3">
                        {isCompleted(project) ? (
                          <CheckCircleIconSolid className="h-5 w-5 text-green-600" />
                        ) : (
                          <FolderIconSolid className="h-5 w-5 text-blue-600" />
                        )}
                        <div>
                          <div className="font-medium text-foreground">
                            {project.project_name || project.name || `Project ${project.id}`}
                          </div>
                          {project.do_this_week && (
                            <Badge variant="secondary" className="text-xs mt-1">
                              This Week
                            </Badge>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      {isCompleted(project) ? (
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
                      {project.task_count || 0}
                    </td>
                    <td className="py-4 px-6 text-muted-foreground">
                      {new Date(project.created_at).toISOString().split('T')[0]}
                    </td>
                    <td className="py-4 px-6 text-muted-foreground">
                      {new Date(project.updated_at).toISOString().split('T')[0]}
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
          Showing {sortedProjects.length} {showCompleted ? 'projects' : 'active projects'}
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <FolderIconSolid className="h-4 w-4 text-blue-600" />
            <span>{sortedProjects.filter(p => !isCompleted(p)).length} Active</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircleIconSolid className="h-4 w-4 text-green-600" />
            <span>{sortedProjects.filter(p => isCompleted(p)).length} Completed</span>
          </div>
        </div>
      </div>
    </div>
  );
}