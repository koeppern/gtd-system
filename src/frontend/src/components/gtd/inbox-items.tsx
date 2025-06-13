'use client';

import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TaskItem } from './task-item';
import { 
  InboxIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';
import type { Task } from '@/types';

interface InboxItemsProps {
  tasks: Task[];
  isLoading?: boolean;
}

export function InboxItems({ tasks, isLoading }: InboxItemsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <InboxIcon className="mr-2 h-5 w-5" />
            Inbox
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-12 bg-muted animate-pulse rounded-lg" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center text-base">
          <InboxIcon className="mr-2 h-5 w-5 text-orange-500" />
          Inbox
          {tasks.length > 0 && (
            <span className="ml-2 inline-flex items-center rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-medium text-orange-800">
              {tasks.length}
            </span>
          )}
        </CardTitle>
        {tasks.length > 0 && (
          <Button size="sm" variant="ghost" className="text-xs">
            Process All
            <ArrowRightIcon className="ml-1 h-3 w-3" />
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <InboxIcon className="h-8 w-8 text-muted-foreground mb-3" />
            <p className="text-sm text-muted-foreground">
              Inbox is empty! 🎉
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {tasks.slice(0, 5).map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                compact={true}
                showProject={false}
                showField={true}
                showDueDate={false}
              />
            ))}
            
            {tasks.length > 5 && (
              <div className="pt-2 border-t border-border">
                <Button variant="ghost" size="sm" className="w-full">
                  View {tasks.length - 5} more items
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