'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AppLayout } from '@/components/layout/app-layout';
import { ProjectsList } from '@/components/projects/projects-list';
import { api } from '@/lib/api';

export default function ProjectsPage() {
  const [showCompleted, setShowCompleted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch projects data
  const { data: projectsData, isLoading } = useQuery({
    queryKey: ['projects', { showCompleted, search: searchQuery }],
    queryFn: () => api.projects.list({ 
      showCompleted, 
      search: searchQuery,
      limit: 100 
    }),
  });

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
            <p className="text-muted-foreground">
              Manage your GTD projects and track progress
            </p>
          </div>
          
          {/* Toggle for All/Active Projects */}
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
                  All Projects
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="max-w-md">
          <input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
          />
        </div>

        {/* Projects List */}
        <ProjectsList 
          projects={projectsData?.items || projectsData || []} 
          isLoading={isLoading}
          showCompleted={showCompleted}
        />
      </div>
    </AppLayout>
  );
}