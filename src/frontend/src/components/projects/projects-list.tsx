'use client';

import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter, usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { InlineEdit } from '@/components/ui/inline-edit';
import { ResizableTable, useResizableColumns } from '@/components/ui/resizable-table';
import { useGroupBy } from '@/components/ui/group-by-dropdown';
import { useDeviceType } from '@/hooks/use-device-type';
import { useShiftClick } from '@/hooks/use-shift-click';
import { api } from '@/lib/api';
import { 
  FolderIcon,
  EllipsisVerticalIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  PencilIcon
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

type SortableColumn = 'name' | 'field' | 'status' | 'tasks' | 'keywords' | 'mother_project' | 'readings' | 'gtd_processes' | 'created' | 'updated';

export function ProjectsList({ projects, isLoading, showCompleted, groupBy }: ProjectsListProps) {
  const [sortBy, setSortBy] = useState<SortableColumn>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [hoveredRowId, setHoveredRowId] = useState<number | null>(null);
  const queryClient = useQueryClient();
  const router = useRouter();
  const pathname = usePathname();
  const t = useTranslations('projects');
  const tCommon = useTranslations('common');
  const { isDesktop, isMobile } = useDeviceType();
  const { handleRowClick } = useShiftClick();

  // Navigate to edit page
  const navigateToEdit = React.useCallback((projectId: number) => {
    const currentUrl = `${pathname}${window.location.search}`;
    router.push(`/projects/${projectId}/edit?returnTo=${encodeURIComponent(currentUrl)}`);
  }, [router, pathname]);

  // Auto-sort by grouped column when grouping changes
  React.useEffect(() => {
    if (groupBy && groupBy !== sortBy) {
      // Map groupBy values to sortable columns
      const groupToColumnMap: Record<string, SortableColumn> = {
        'status': 'status',
        'field': 'field',
        'task_count': 'tasks'
      };
      
      const newSortBy = groupToColumnMap[groupBy] || 'name';
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  }, [groupBy, sortBy]);

  const handleSort = (newSortBy: SortableColumn) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  };

  // Helper component for sortable column headers
  const SortableHeader = ({ column, children, className = "" }: { 
    column: SortableColumn; 
    children: React.ReactNode; 
    className?: string;
  }) => {
    const isActive = sortBy === column;
    
    return (
      <button
        type="button"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          handleSort(column);
        }}
        className={`flex items-center space-x-1 hover:text-foreground transition-colors cursor-pointer text-left w-full p-0 bg-transparent border-none ${className}`}
      >
        <span>{children}</span>
        {isActive && (
          sortOrder === 'asc' ? 
            <ChevronUpIcon className="h-3 w-3 text-blue-600 ml-1" /> : 
            <ChevronDownIcon className="h-3 w-3 text-blue-600 ml-1" />
        )}
      </button>
    );
  };

  // Define resizable columns
  const defaultColumns = [
    { key: 'no', title: tCommon('table.no'), width: 60, minWidth: 40, maxWidth: 100 },
    { key: 'name', title: <SortableHeader column="name">{t('table.projectName')}</SortableHeader>, width: 300, minWidth: 150, maxWidth: 500 },
    { key: 'field', title: <SortableHeader column="field">{tCommon('table.field')}</SortableHeader>, width: 120, minWidth: 80, maxWidth: 200 },
    { key: 'status', title: <SortableHeader column="status">{tCommon('table.status')}</SortableHeader>, width: 120, minWidth: 80, maxWidth: 200 },
    { key: 'tasks', title: <SortableHeader column="tasks" className="w-full justify-center">{tCommon('table.tasks')}</SortableHeader>, width: 100, minWidth: 70, maxWidth: 150 },
    { key: 'keywords', title: <SortableHeader column="keywords">{tCommon('table.keywords')}</SortableHeader>, width: 150, minWidth: 100, maxWidth: 250 },
    { key: 'mother_project', title: <SortableHeader column="mother_project">{tCommon('table.parentProject')}</SortableHeader>, width: 150, minWidth: 100, maxWidth: 250 },
    { key: 'readings', title: <SortableHeader column="readings">{tCommon('table.readings')}</SortableHeader>, width: 120, minWidth: 80, maxWidth: 200 },
    { key: 'gtd_processes', title: <SortableHeader column="gtd_processes">{tCommon('table.gtdProcesses')}</SortableHeader>, width: 130, minWidth: 100, maxWidth: 200 },
    { key: 'created', title: <SortableHeader column="created">{tCommon('table.created')}</SortableHeader>, width: 120, minWidth: 100, maxWidth: 180 },
    { key: 'updated', title: <SortableHeader column="updated">{tCommon('table.lastUpdated')}</SortableHeader>, width: 140, minWidth: 100, maxWidth: 200 },
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
      case 'field':
        aValue = (a.field_name || '').toLowerCase();
        bValue = (b.field_name || '').toLowerCase();
        break;
      case 'status':
        aValue = a.done_status ? 1 : 0;
        bValue = b.done_status ? 1 : 0;
        break;
      case 'tasks':
        aValue = a.task_count || 0;
        bValue = b.task_count || 0;
        break;
      case 'keywords':
        aValue = (a.keywords || '').toLowerCase();
        bValue = (b.keywords || '').toLowerCase();
        break;
      case 'mother_project':
        aValue = (a.mother_project || '').toLowerCase();
        bValue = (b.mother_project || '').toLowerCase();
        break;
      case 'readings':
        aValue = (a.readings || '').toLowerCase();
        bValue = (b.readings || '').toLowerCase();
        break;
      case 'gtd_processes':
        aValue = (a.gtd_processes || '').toLowerCase();
        bValue = (b.gtd_processes || '').toLowerCase();
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

  // Function to get group value for a project
  const getGroupValue = (project: Project, key: string): string | number | null => {
    switch (key) {
      case 'status':
        return isCompleted(project) ? tCommon('status.completed') : tCommon('status.active');
      case 'field':
        return project.field_name || 'No Field';
      case 'task_count':
        const count = project.task_count || 0;
        if (count === 0) return t('taskCounts.zero');
        if (count <= 5) return t('taskCounts.oneToFive');
        if (count <= 10) return t('taskCounts.sixToTen');
        if (count <= 20) return t('taskCounts.elevenToTwenty');
        return t('taskCounts.twentyPlus');
      case 'do_this_week':
        return project.do_this_week ? tCommon('status.thisWeek') : 'Not This Week';
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
  const groupedProjects = useGroupBy(sortedProjects, groupBy || null, getGroupValue);

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
            {showCompleted ? t('table.noProjectsFound') : t('table.noActiveProjects')}
          </h3>
          <p className="text-muted-foreground text-center max-w-md">
            {showCompleted 
              ? t('table.noProjectsDescription')
              : t('table.noActiveProjectsDescription')
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
        {groupBy ? 
          t('table.summaryWithGrouping', { 
            count: projects.length, 
            type: showCompleted ? 'total' : 'active', 
            groupBy: groupBy 
          }) :
          t('table.summary', { 
            count: projects.length, 
            type: showCompleted ? 'total' : 'active'
          })
        }
      </div>

      {/* Single Table with Group Sections */}
      <Card>
        <CardContent className="p-0">
          <ResizableTable 
            columns={columns} 
            onColumnResize={handleColumnResize}
            onColumnReorder={handleColumnReorder}
            className="text-sm"
          >
            {groupedProjects.map((group, groupIndex) => (
              <React.Fragment key={group.groupName || 'main'}>
                {/* Group Header Row (only show if there's a grouping) */}
                {groupBy && group.groupName && (
                  <tr className="bg-muted/50 border-b border-border">
                    <td colSpan={columns.length} className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <h3 className="text-sm font-semibold text-foreground">
                          {group.groupName}
                        </h3>
                        <Badge variant="secondary" className="text-xs">
                          {t('table.projectsCount', { 
                            count: group.items.length, 
                            plural: group.items.length !== 1 ? 'e' : '' 
                          })}
                        </Badge>
                      </div>
                    </td>
                  </tr>
                )}
                
                {/* Group Items */}
                {group.items.map((project, index) => {
                  // Calculate global index across all groups
                  let globalIndex = 0;
                  for (let i = 0; i < groupIndex; i++) {
                    globalIndex += groupedProjects[i]?.items.length || 0;
                  }
                  globalIndex += index + 1;

              const renderCell = (columnKey: string) => {
                switch (columnKey) {
                  case 'no':
                    return (
                      <td key={columnKey} className="py-3 px-4 text-center text-muted-foreground">
                        {globalIndex}
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
                              placeholder={t('placeholders.projectName')}
                              disabled={updateProjectMutation.isPending}
                            />
                            {project.do_this_week && (
                              <div className="mt-1">
                                <Badge variant="secondary" className="text-xs">
                                  {tCommon('status.thisWeek')}
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
                              {tCommon('status.completed')}
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-xs">
                              {tCommon('status.active')}
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
                      <td key={columnKey} className="py-3 px-4 relative">
                        {/* Desktop: Edit button on hover */}
                        {isDesktop && hoveredRowId === project.id && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigateToEdit(project.id);
                            }}
                            className="h-8 w-8 p-0 opacity-80 hover:opacity-100"
                            title="Edit project (or Shift+Click row)"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </Button>
                        )}
                        
                        {/* Fallback menu button when not hovering */}
                        {(!isDesktop || hoveredRowId !== project.id) && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 opacity-50 hover:opacity-100"
                          >
                            <EllipsisVerticalIcon className="h-4 w-4" />
                          </Button>
                        )}
                      </td>
                    );
                  default:
                    return <td key={columnKey} className="py-3 px-4"></td>;
                }
              };

                  return (
                    <tr 
                      key={project.id} 
                      className={`border-b border-border hover:bg-muted/50 transition-colors ${
                        isMobile ? 'cursor-pointer' : ''
                      }`}
                      onMouseEnter={isDesktop ? () => setHoveredRowId(project.id) : undefined}
                      onMouseLeave={isDesktop ? () => setHoveredRowId(null) : undefined}
                      onClick={isMobile ? () => navigateToEdit(project.id) : (e) => handleRowClick(e, project.id, navigateToEdit)}
                    >
                      {columns.map((col) => renderCell(col.key))}
                    </tr>
                  );
                })}
              </React.Fragment>
            ))}
          </ResizableTable>
        </CardContent>
      </Card>

      {/* Additional Summary */}
      {!groupBy && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <FolderIconSolid className="h-4 w-4 text-blue-600" />
              <span>{t('table.activeSummary', { count: projects.filter(p => !isCompleted(p)).length })}</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIconSolid className="h-4 w-4 text-green-600" />
              <span>{t('table.completedSummary', { count: projects.filter(p => isCompleted(p)).length })}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}