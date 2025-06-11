'use client';

import * as React from 'react';
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { api } from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  PlusIcon, 
  PaperAirplaneIcon,
  ClockIcon,
  CalendarIcon,
  FolderIcon
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

export function QuickCapture() {
  const [input, setInput] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [options, setOptions] = useState({
    do_today: false,
    do_this_week: false,
    type: 'task' as 'task' | 'project',
  });

  const queryClient = useQueryClient();

  const quickAddMutation = useMutation({
    mutationFn: api.quickAdd.capture,
    onSuccess: () => {
      toast.success(`${options.type === 'task' ? 'Task' : 'Project'} added successfully!`);
      setInput('');
      setIsExpanded(false);
      setOptions({ do_today: false, do_this_week: false, type: 'task' });
      
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: () => {
      toast.error('Failed to add item. Please try again.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    quickAddMutation.mutate({
      content: input.trim(),
      type: options.type,
      do_today: options.do_today,
      do_this_week: options.do_this_week,
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit(e);
    } else if (e.key === 'Escape') {
      setIsExpanded(false);
      setInput('');
    }
  };

  return (
    <Card className={cn(
      'transition-all duration-200',
      isExpanded ? 'ring-2 ring-ring' : 'hover:shadow-md'
    )}>
      <CardContent className="p-4">
        <form onSubmit={handleSubmit}>
          <div className="flex gap-3">
            <div className="flex-1">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onFocus={() => setIsExpanded(true)}
                onKeyDown={handleKeyDown}
                placeholder="What's on your mind? (Ctrl+Enter to add quickly)"
                className="border-0 text-base placeholder:text-muted-foreground focus-visible:ring-0 focus-visible:ring-offset-0"
                leftIcon={<PlusIcon className="h-4 w-4" />}
              />
            </div>
            <Button 
              type="submit" 
              disabled={!input.trim() || quickAddMutation.isPending}
              loading={quickAddMutation.isPending}
              size="icon"
              className="shrink-0"
            >
              <PaperAirplaneIcon className="h-4 w-4" />
            </Button>
          </div>

          {/* Expanded options */}
          {isExpanded && (
            <div className="mt-4 space-y-4 border-t border-border pt-4">
              {/* Type selection */}
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant={options.type === 'task' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setOptions(prev => ({ ...prev, type: 'task' }))}
                >
                  Task
                </Button>
                <Button
                  type="button"
                  variant={options.type === 'project' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setOptions(prev => ({ ...prev, type: 'project' }))}
                >
                  <FolderIcon className="mr-1 h-3 w-3" />
                  Project
                </Button>
              </div>

              {/* Quick scheduling */}
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant={options.do_today ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setOptions(prev => ({ 
                    ...prev, 
                    do_today: !prev.do_today,
                    do_this_week: prev.do_today ? prev.do_this_week : false
                  }))}
                >
                  <ClockIcon className="mr-1 h-3 w-3" />
                  Today
                </Button>
                <Button
                  type="button"
                  variant={options.do_this_week ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setOptions(prev => ({ 
                    ...prev, 
                    do_this_week: !prev.do_this_week,
                    do_today: prev.do_this_week ? prev.do_today : false
                  }))}
                >
                  <CalendarIcon className="mr-1 h-3 w-3" />
                  This Week
                </Button>
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center">
                <div className="text-xs text-muted-foreground">
                  Press <kbd className="px-1 py-0.5 bg-muted rounded text-xs">Ctrl+Enter</kbd> to add quickly
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setIsExpanded(false);
                      setInput('');
                    }}
                  >
                    Cancel
                  </Button>
                  <Button 
                    type="submit"
                    size="sm"
                    disabled={!input.trim() || quickAddMutation.isPending}
                    loading={quickAddMutation.isPending}
                  >
                    Add {options.type}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  );
}