'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { AppLayout } from '@/components/layout/app-layout';
import { TasksList } from '@/components/tasks/tasks-list';
import { Pagination, usePagination } from '@/components/ui/pagination';
import { GroupByDropdown, GroupByOption } from '@/components/ui/group-by-dropdown';
import { api } from '@/lib/api';
import { useKeyboardShortcuts, useSearchFieldRef } from '@/hooks/use-keyboard-shortcuts';

export default function TasksPage() {
  const [showCompleted, setShowCompleted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [groupBy, setGroupBy] = useState<string | null>(null);
  const t = useTranslations('tasks');
  const tCommon = useTranslations('common');

  // Search field refs and keyboard shortcuts for tasks
  const { ref: taskSearchRef, searchFieldRef: taskSearchFieldRef } = useSearchFieldRef();
  
  // Initialize keyboard shortcuts for context search (CTRL-SHIFT-F)
  useKeyboardShortcuts({
    contextSearchRef: taskSearchFieldRef
  });

  // Define grouping options for tasks (only meaningful columns)
  const groupByOptions: GroupByOption[] = [
    { key: 'project', label: t('grouping.project'), enabled: true },
    { key: 'status', label: t('grouping.status'), enabled: true },
    { key: 'priority', label: t('grouping.priority'), enabled: true },
    { key: 'field', label: tCommon('table.field'), enabled: true },
    { key: 'do_today', label: 'Do Today', enabled: true },
    { key: 'do_this_week', label: t('grouping.doThisWeek'), enabled: true },
    { key: 'is_reading', label: 'Reading Tasks', enabled: true },
    { key: 'wait_for', label: 'Waiting For', enabled: true },
    { key: 'postponed', label: 'Postponed', enabled: true },
  ];

  // Optimized queries with intelligent caching
  const { data: totalCountData } = useQuery({
    queryKey: ['tasks-count', { showCompleted, search: searchQuery }],
    queryFn: () => api.tasks.list({ 
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

  // Fetch tasks data with pagination
  const { data: tasksData, isLoading } = useQuery({
    queryKey: ['tasks', { 
      showCompleted, 
      search: searchQuery, 
      offset: pagination.offset, 
      limit: pagination.limit 
    }],
    queryFn: () => api.tasks.list({ 
      showCompleted, 
      search: searchQuery,
      limit: pagination.limit,
      offset: pagination.offset
    }),
    enabled: totalItems > 0 || !totalCountData, // Fetch even if no count data yet
    staleTime: 1000 * 60 * 3, // Tasks data stays fresh for 3 minutes
    gcTime: 1000 * 60 * 15, // Keep in cache for 15 minutes
    placeholderData: (previousData) => previousData, // Keep showing old data while loading new
  });
  
  // Debug logging
  console.log('Tasks Page Debug:', {
    totalCountData,
    tasksData,
    totalItems,
    pagination,
    showPagination: totalItems > 0
  });

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
            <p className="text-muted-foreground">
              {t('description')}
            </p>
          </div>
          
          {/* Toggle for All/Active Tasks */}
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
                  All {t('title')}
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
              ref={taskSearchRef}
              type="text"
              placeholder={tCommon('search.tasksPlaceholder')}
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

        {/* Tasks List */}
        <TasksList 
          tasks={Array.isArray(tasksData) ? tasksData : (tasksData?.items || [])} 
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
    </AppLayout>
  );
}