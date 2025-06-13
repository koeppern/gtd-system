'use client';

import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  CalendarIcon,
  FolderIcon,
  ArrowRightIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import type { Project } from '@/types';
import { cn } from '@/lib/utils';

interface WeeklyProjectsProps {
  projects: Project[];
  isLoading?: boolean;
}

export function WeeklyProjects({ projects, isLoading }: WeeklyProjectsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <CalendarIcon className="mr-2 h-5 w-5" />
            This Week
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center text-base">
          <CalendarIcon className="mr-2 h-5 w-5 text-purple-500" />
          This Week
          {projects.length > 0 && (
            <span className="ml-2 inline-flex items-center rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-800">
              {projects.length}
            </span>
          )}
        </CardTitle>
        <Button size="sm" variant="ghost" className="text-xs">
          View All
          <ArrowRightIcon className="ml-1 h-3 w-3" />
        </Button>
      </CardHeader>
      <CardContent>
        {projects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <CalendarIcon className="h-8 w-8 text-muted-foreground mb-3" />
            <p className="text-sm text-muted-foreground">
              No projects scheduled for this week
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {projects.slice(0, 4).map((project) => (
              <ProjectItem key={project.id} project={project} />
            ))}
            
            {projects.length > 4 && (
              <div className="pt-2 border-t border-border">
                <Button variant="ghost" size="sm" className="w-full">
                  View {projects.length - 4} more projects
                  <ArrowRightIcon className="ml-1 h-3 w-3" />
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function ProjectItem({ project }: { project: Project }) {
  const completionPercentage = project.completion_percentage || 0;
  
  return (
    <div className="flex items-start gap-3 rounded-lg border p-3 transition-colors hover:bg-accent/50 cursor-pointer">
      <div className="shrink-0 mt-0.5">
        {project.is_done ? (
          <CheckCircleIcon className="h-5 w-5 text-green-600" />
        ) : (
          <FolderIcon className="h-5 w-5 text-muted-foreground" />
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        <h3 className={cn(
          'font-medium text-sm leading-relaxed',
          project.is_done && 'line-through text-muted-foreground'
        )}>
          {project.project_name}
        </h3>
        
        {/* Progress bar */}
        <div className="mt-2">
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
            <span>{project.completed_task_count} / {project.task_count} tasks</span>
            <span>{Math.round(completionPercentage)}%</span>
          </div>
          <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary rounded-full transition-all duration-300"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
        </div>
        
        {/* Field indicator */}
        {project.field && (
          <div className="flex items-center mt-2 text-xs text-muted-foreground">
            <div className="h-2 w-2 rounded-full bg-blue-500 mr-1" />
            {project.field.name}
          </div>
        )}
      </div>
    </div>
  );
}