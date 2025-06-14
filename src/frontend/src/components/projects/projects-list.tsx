'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { InlineEdit } from '@/components/ui/inline-edit';
import { ResizableTable, useResizableColumns } from '@/components/ui/resizable-table';
import { useGroupBy } from '@/components/ui/group-by-dropdown';
import { api } from '@/lib/api';
import { 
  FolderIcon,
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
  field_name?: string; // Resolved field name from gtd_fields
  do_this_week?: boolean;
  task_count?: number;
  readings?: string;
  keywords?: string;
  mother_project?: string;
  related_projects?: string;
  gtd_processes?: string;
  created_at: string;
  updated_at: string;
}

interface ProjectsListProps {
  projects: Project[];
  isLoading: boolean;
  showCompleted: boolean;
  groupBy?: string | null;
}

export function ProjectsList({ projects, isLoading, showCompleted, groupBy }: ProjectsListProps) {
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'tasks' | 'created' | 'updated'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const queryClient = useQueryClient();

  // Define resizable columns
  const defaultColumns = [
    { key: 'no', title: 'No', width: 60, minWidth: 40, maxWidth: 100 },
    { key: 'name', title: (
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
    ), width: 300, minWidth: 150, maxWidth: 500 },
    { key: 'field', title: 'Field', width: 120, minWidth: 80, maxWidth: 200 },
    { key: 'status', title: (
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
    ), width: 120, minWidth: 80, maxWidth: 200 },
    { key: 'tasks', title: (
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
    ), width: 100, minWidth: 70, maxWidth: 150 },
    { key: 'keywords', title: 'Keywords', width: 150, minWidth: 100, maxWidth: 250 },
    { key: 'mother_project', title: 'Parent Project', width: 150, minWidth: 100, maxWidth: 250 },
    { key: 'readings', title: 'Readings', width: 120, minWidth: 80, maxWidth: 200 },
    { key: 'gtd_processes', title: 'GTD Processes', width: 130, minWidth: 100, maxWidth: 200 },
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

  const { columns, handleColumnResize, handleColumnReorder, isLoading: columnsLoading } = useResizableColumns('projects', defaultColumns);

  // Mutation for updating project name
  const updateProjectMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      return api.projects.update(id, data);
    },
    onSuccess: () => {
      // Invalidate and refetch projects list
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: (error) => {
      console.error('Failed to update project:', error);
    },
  });

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

  // Function to get group value for a project
  const getGroupValue = (project: Project, key: string): string | number | null => {
    switch (key) {
      case 'status':
        return isCompleted(project) ? 'Completed' : 'Active';
      case 'field':
        return project.field_name || 'No Field';
      case 'task_count':
        const count = project.task_count || 0;
        if (count === 0) return '0 tasks';
        if (count <= 5) return '1-5 tasks';
        if (count <= 10) return '6-10 tasks';
        if (count <= 20) return '11-20 tasks';
        return '20+ tasks';
      case 'do_this_week':
        return project.do_this_week ? 'This Week' : 'Not This Week';
      default:
        return 'Unknown';
    }
  };

  // Helper functions
  const isCompleted = (project: Project) => {
    return project.done_at !== null || project.done_status === true;
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toISOString().split('T')[0]; // YYYY-MM-DD format
    } catch (error) {
      return dateString; // fallback to original string if parsing fails
    }
  };

  // Group projects if groupBy is selected
  const groupedProjects = useGroupBy(sortedProjects, groupBy, getGroupValue);

  // Show loading state for data or columns
  if (isLoading || columnsLoading) {
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
      {/* Summary */}
      <div className="text-sm text-muted-foreground">
        Showing {projects.length} {showCompleted ? 'total' : 'active'} projects
        {groupBy && ` grouped by ${groupBy}`}
      </div>

      {/* Grouped Tables or Single Table */}
      {groupedProjects.map((group, groupIndex) => (
        <div key={group.groupName || 'main'} className="space-y-4">
          {/* Group Header (only show if there's a grouping) */}
          {groupBy && group.groupName && (
            <div className="flex items-center space-x-2 pt-4">
              <h3 className="text-lg font-semibold text-foreground">
                {group.groupName}
              </h3>
              <Badge variant="secondary" className="text-xs">
                {group.items.length} project{group.items.length !== 1 ? 's' : ''}
              </Badge>
            </div>
          )}

          {/* Resizable Table */}
          <Card>
            <CardContent className="p-0">
              <ResizableTable 
                columns={columns} 
                onColumnResize={handleColumnResize}
                onColumnReorder={handleColumnReorder}
                className="text-sm"
              >
                {group.items.map((project, index) => {
              const renderCell = (columnKey: string) => {
                switch (columnKey) {
                  case 'no':
                    return (
                      <td key={columnKey} className="py-3 px-4 text-center text-muted-foreground">
                        {index + 1}
                      </td>
                    );
                  case 'name':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          {isCompleted(project) ? (
                            <CheckCircleIconSolid className="h-5 w-5 text-green-600 flex-shrink-0" />
                          ) : (
                            <FolderIconSolid className="h-5 w-5 text-blue-600 flex-shrink-0" />
                          )}
                          <div className="flex-1 min-w-0">
                            <InlineEdit
                              value={project.project_name || project.name || `Project ${project.id}`}
                              onSave={async (newValue) => {
                                await updateProjectMutation.mutateAsync({
                                  id: project.id,
                                  data: { project_name: newValue }
                                });
                              }}
                              className="font-medium text-foreground break-words"
                              placeholder="Project name"
                              disabled={updateProjectMutation.isPending}
                            />
                            {project.do_this_week && (
                              <div className="mt-1">
                                <Badge variant="secondary" className="text-xs">
                                  This Week
                                </Badge>
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                    );
                  case 'status':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <div className="flex items-center space-x-2 flex-wrap">
                          {isCompleted(project) ? (
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
                    );
                  case 'field':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <span className="text-sm text-muted-foreground">
                          {project.field_name || '-'}
                        </span>
                      </td>
                    );
                  case 'tasks':
                    return (
                      <td key={columnKey} className="py-3 px-4 text-center">
                        <span className="text-sm font-medium">
                          {project.task_count || 0}
                        </span>
                      </td>
                    );
                  case 'keywords':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <span className="text-xs text-muted-foreground truncate">
                          {project.keywords || '-'}
                        </span>
                      </td>
                    );
                  case 'mother_project':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <span className="text-xs text-muted-foreground truncate">
                          {project.mother_project || '-'}
                        </span>
                      </td>
                    );
                  case 'readings':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <span className="text-xs text-muted-foreground truncate">
                          {project.readings || '-'}
                        </span>
                      </td>
                    );
                  case 'gtd_processes':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <span className="text-xs text-muted-foreground truncate">
                          {project.gtd_processes || '-'}
                        </span>
                      </td>
                    );
                  case 'created':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <span className="text-xs text-muted-foreground">
                          {formatDate(project.created_at)}
                        </span>
                      </td>
                    );
                  case 'updated':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <span className="text-xs text-muted-foreground">
                          {formatDate(project.updated_at)}
                        </span>
                      </td>
                    );
                  case 'actions':
                    return (
                      <td key={columnKey} className="py-3 px-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 opacity-50 hover:opacity-100"
                        >
                          <EllipsisVerticalIcon className="h-4 w-4" />
                        </Button>
                      </td>
                    );
                  default:
                    return <td key={columnKey} className="py-3 px-4"></td>;
                }
              };

                  return (
                    <tr 
                      key={project.id} 
                      className="border-b border-border hover:bg-muted/50 transition-colors"
                    >
                      {columns.map((col) => renderCell(col.key))}
                    </tr>
                  );
                })}
              </ResizableTable>
            </CardContent>
          </Card>
        </div>
      ))}

      {/* Additional Summary */}
      {!groupBy && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <FolderIconSolid className="h-4 w-4 text-blue-600" />
              <span>{projects.filter(p => !isCompleted(p)).length} Active</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIconSolid className="h-4 w-4 text-green-600" />
              <span>{projects.filter(p => isCompleted(p)).length} Completed</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}