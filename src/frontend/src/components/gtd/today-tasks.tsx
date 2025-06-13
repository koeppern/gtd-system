'use client';

import * as React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TaskItem } from './task-item';
import { 
  ClockIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import type { Task } from '@/types';

interface TodayTasksProps {
  tasks: Task[];
  isLoading?: boolean;
}

export function TodayTasks({ tasks, isLoading }: TodayTasksProps) {
  const queryClient = useQueryClient();

  const completeMutation = useMutation({
    mutationFn: (taskId: number) => api.tasks.complete(taskId),
    onSuccess: () => {
      toast.success('Task completed!');
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: () => {
      toast.error('Failed to complete task');
    },
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <ClockIcon className="mr-2 h-5 w-5" />
            Today's Focus
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
        <CardTitle className="flex items-center">
          <ClockIcon className="mr-2 h-5 w-5 text-blue-500" />
          Today's Focus
          {tasks && tasks.length > 0 && (
            <span className="ml-2 inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
              {tasks.length}
            </span>
          )}
        </CardTitle>
        <Button size="sm" variant="ghost">
          <PlusIcon className="h-4 w-4 mr-1" />
          Add Task
        </Button>
      </CardHeader>
      <CardContent>
        {!tasks || tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <ClockIcon className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground mb-2">
              No tasks for today
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Great! You're all caught up. Why not plan for tomorrow?
            </p>
            <Button size="sm">
              <PlusIcon className="h-4 w-4 mr-1" />
              Schedule a task
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks?.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onComplete={() => completeMutation.mutate(task.id)}
                isCompleting={completeMutation.isPending}
                showProject={true}
                showDueDate={false}
              />
            ))}
            
            {/* Quick add for today */}
            <div className="pt-3 border-t border-border">
              <Button variant="ghost" className="w-full justify-start text-muted-foreground">
                <PlusIcon className="h-4 w-4 mr-2" />
                Add another task for today
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}