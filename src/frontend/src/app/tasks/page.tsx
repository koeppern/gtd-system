'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AppLayout } from '@/components/layout/app-layout';
import { TasksList } from '@/components/tasks/tasks-list';
import { Pagination, usePagination } from '@/components/ui/pagination';
import { api } from '@/lib/api';

export default function TasksPage() {
  const [showCompleted, setShowCompleted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // First, get total count to initialize pagination
  const { data: totalCountData } = useQuery({
    queryKey: ['tasks-count', { showCompleted, search: searchQuery }],
    queryFn: () => api.tasks.list({ 
      showCompleted, 
      search: searchQuery,
      limit: 1, // Just get count
      offset: 0 
    }),
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
            <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
            <p className="text-muted-foreground">
              Manage your GTD tasks and track progress
            </p>
          </div>
          
          {/* Toggle for All/Active Tasks */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-muted-foreground">
                Show:
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
                  Active
                </button>
                <button
                  onClick={() => setShowCompleted(true)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-r-lg transition-colors ${
                    showCompleted
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  All Tasks
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="max-w-md">
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
          />
        </div>

        {/* Pagination - Top */}
        {totalItems > 0 && (
          <Pagination
            currentPage={pagination.currentPage}
            totalItems={totalItems}
            itemsPerPage={pagination.itemsPerPage}
            onPageChange={pagination.handlePageChange}
            onShowAll={pagination.handleShowAll}
            isShowingAll={pagination.isShowingAll}
            className="mb-4"
          />
        )}

        {/* Tasks List */}
        <TasksList 
          tasks={Array.isArray(tasksData) ? tasksData : (tasksData?.items || [])} 
          isLoading={isLoading}
          showCompleted={showCompleted}
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