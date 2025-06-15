'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { ProjectsList } from '@/components/projects/projects-list';
import { Pagination, usePagination } from '@/components/ui/pagination';
import { GroupByDropdown, GroupByOption } from '@/components/ui/group-by-dropdown';
import { api } from '@/lib/api';
import { useKeyboardShortcuts, useSearchFieldRef } from '@/hooks/use-keyboard-shortcuts';

export default function ProjectsPage() {
  const [showCompleted, setShowCompleted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [groupBy, setGroupBy] = useState<string | null>(null);
  const t = useTranslations('projects');
  const tCommon = useTranslations('common');

  // Search field refs and keyboard shortcuts for projects
  const { ref: projectSearchRef, searchFieldRef: projectSearchFieldRef } = useSearchFieldRef();
  
  // Initialize keyboard shortcuts for context search (CTRL-SHIFT-F)
  useKeyboardShortcuts({
    contextSearchRef: projectSearchFieldRef
  });

  // Define grouping options for projects (only meaningful columns)
  const groupByOptions: GroupByOption[] = [
    { key: 'status', label: t('grouping.status'), enabled: true },
    { key: 'field', label: t('grouping.field'), enabled: true },
    { key: 'task_count', label: t('grouping.taskCount'), enabled: true },
    { key: 'do_this_week', label: t('grouping.doThisWeek'), enabled: true },
  ];

  // Optimized queries with intelligent caching
  const { data: totalCountData } = useQuery({
    queryKey: ['projects-count', { showCompleted, search: searchQuery }],
    queryFn: () => api.projects.list({ 
      showCompleted, 
      search: searchQuery,
      limit: 1, // Just get count
      offset: 0 
    }),
    staleTime: 1000 * 60 * 5, // Count doesn't change often
    gcTime: 1000 * 60 * 10, // Keep count cache longer
  });

  const totalItems = totalCountData?.total || 0;
  
  // Initialize pagination
  const pagination = usePagination(totalItems, 50);

  // Fetch projects data with pagination
  const { data: projectsData, isLoading } = useQuery({
    queryKey: ['projects', { 
      showCompleted, 
      search: searchQuery, 
      offset: pagination.offset, 
      limit: pagination.limit 
    }],
    queryFn: () => api.projects.list({ 
      showCompleted, 
      search: searchQuery,
      limit: pagination.limit,
      offset: pagination.offset
    }),
    enabled: totalItems > 0 || !totalCountData, // Fetch even if no count data yet
    staleTime: 1000 * 60 * 3, // Projects data stays fresh for 3 minutes
    gcTime: 1000 * 60 * 15, // Keep in cache for 15 minutes
    placeholderData: (previousData) => previousData, // Keep showing old data while loading new
  });

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
            <p className="text-muted-foreground">
              {t('description')}
            </p>
          </div>
          
          {/* Toggle for All/Active Projects */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-muted-foreground">
                {tCommon('buttons.show')}
              </label>
              <div className="flex rounded-lg border border-border">
                <button
                  onClick={() => setShowCompleted(false)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-l-lg transition-colors ${
                    !showCompleted
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {tCommon('buttons.active')}
                </button>
                <button
                  onClick={() => setShowCompleted(true)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-r-lg transition-colors ${
                    showCompleted
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {tCommon('buttons.allProjects')}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Search, Group By and Pagination Row */}
        <div className="flex items-center justify-between gap-4">
          {/* Search */}
          <div className="max-w-4xl">
            <input
              ref={projectSearchRef}
              type="text"
              placeholder={tCommon('search.projectsPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
            />
          </div>

          {/* Controls Row */}
          <div className="flex items-center space-x-4">
            {/* Group By Dropdown */}
            <GroupByDropdown
              options={groupByOptions}
              selectedGroupBy={groupBy}
              onGroupByChange={setGroupBy}
            />

            {/* Pagination - Top */}
            {totalItems > 0 && (
              <Pagination
                currentPage={pagination.currentPage}
                totalItems={totalItems}
                itemsPerPage={pagination.itemsPerPage}
                onPageChange={pagination.handlePageChange}
                onShowAll={pagination.handleShowAll}
                isShowingAll={pagination.isShowingAll}
              />
            )}
          </div>
        </div>

        {/* Projects List */}
        <ProjectsList 
          projects={Array.isArray(projectsData) ? projectsData : (projectsData?.items || [])} 
          isLoading={isLoading}
          showCompleted={showCompleted}
          groupBy={groupBy}
        />

        {/* Pagination - Bottom */}
        {totalItems > 0 && (
          <Pagination
            currentPage={pagination.currentPage}
            totalItems={totalItems}
            itemsPerPage={pagination.itemsPerPage}
            onPageChange={pagination.handlePageChange}
            onShowAll={pagination.handleShowAll}
            isShowingAll={pagination.isShowingAll}
            className="mt-8"
          />
        )}
    </div>
  );
}