'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { AppLayout } from '@/components/layout/app-layout';
import { Button } from '@/components/ui/button';
import { PlusIcon, FolderIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import type { Project } from '@/types';

export default function ProjectsPage() {
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('active');

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects', filter],
    queryFn: () => {
      switch (filter) {
        case 'active':
          return api.projects.getActive();
        case 'completed':
          // For now, get all and filter client-side
          return api.projects.list().then(projects => 
            projects.filter(p => p.done_status === true)
          );
        default:
          return api.projects.list();
      }
    },
  });

  const activeCount = projects?.filter(p => !p.done_status).length || 0;
  const completedCount = projects?.filter(p => p.done_status).length || 0;

  return (
    <AppLayout>
      <div className="py-6">
        <div className="px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="sm:flex sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
                Projects
              </h1>
              <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
                Manage your GTD projects and areas of focus
              </p>
            </div>
            <div className="mt-4 sm:mt-0">
              <Button>
                <PlusIcon className="mr-2 h-4 w-4" />
                New Project
              </Button>
            </div>
          </div>

          {/* Filter Tabs */}
          <div className="mt-6 border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setFilter('active')}
                className={cn(
                  filter === 'active'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                )}
              >
                Active
                <span className="ml-2 text-gray-400">({activeCount})</span>
              </button>
              <button
                onClick={() => setFilter('all')}
                className={cn(
                  filter === 'all'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                )}
              >
                All
                <span className="ml-2 text-gray-400">({projects?.length || 0})</span>
              </button>
              <button
                onClick={() => setFilter('completed')}
                className={cn(
                  filter === 'completed'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                )}
              >
                Completed
                <span className="ml-2 text-gray-400">({completedCount})</span>
              </button>
            </nav>
          </div>

          {/* Projects List */}
          <div className="mt-6">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center space-x-2 text-gray-500">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900 dark:border-white"></div>
                  <span>Loading projects...</span>
                </div>
              </div>
            ) : projects?.length === 0 ? (
              <div className="text-center py-12">
                <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                  No projects found
                </h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Get started by creating a new project
                </p>
                <div className="mt-6">
                  <Button>
                    <PlusIcon className="mr-2 h-4 w-4" />
                    New Project
                  </Button>
                </div>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {projects?.map((project) => (
                  <div
                    key={project.id}
                    className="relative rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow dark:border-gray-700 dark:bg-gray-800"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-base font-medium text-gray-900 dark:text-white">
                          {project.name}
                        </h3>
                        {project.keywords && (
                          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            {project.keywords}
                          </p>
                        )}
                      </div>
                      {project.do_this_week && (
                        <span className="ml-2 inline-flex items-center rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-medium text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
                          This Week
                        </span>
                      )}
                    </div>
                    
                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Field #{project.field_id || 'None'}
                      </span>
                      <Button size="sm" variant="ghost">
                        View Tasks
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}