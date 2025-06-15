'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { api } from '@/lib/api';

interface Task {
  id: number;
  task_name?: string;
  name?: string;
  project_id?: number;
  project_name?: string;
  done_at?: string;
  do_today?: boolean;
  do_this_week?: boolean;
  is_reading?: boolean;
  wait_for?: boolean;
  postponed?: boolean;
  reviewed?: boolean;
  do_on_date?: string;
  field_id?: number;
  field_name?: string;
  priority?: number;
  time_expenditure?: string;
  url?: string;
  knowledge_db_entry?: string;
  // Add other task fields as needed
}

interface TaskEditFormProps {
  task: Task;
  onSaveSuccess: () => void;
  onCancel: () => void;
}

export function TaskEditForm({ task, onSaveSuccess, onCancel }: TaskEditFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const t = useTranslations('tasks');
  const tCommon = useTranslations('common');

  const form = useForm({
    defaultValues: {
      task_name: task.task_name || task.name || '',
      do_today: task.do_today || false,
      do_this_week: task.do_this_week || false,
      is_reading: task.is_reading || false,
      wait_for: task.wait_for || false,
      postponed: task.postponed || false,
      reviewed: task.reviewed || false,
      do_on_date: task.do_on_date || '',
      priority: task.priority || 0,
      time_expenditure: task.time_expenditure || '',
      url: task.url || '',
      knowledge_db_entry: task.knowledge_db_entry || '',
    }
  });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    try {
      await api.tasks.update(task.id, data);
      onSaveSuccess();
    } catch (error) {
      console.error('Failed to update task:', error);
      // TODO: Add proper error handling
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Edit Task</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Task Name */}
            <div className="space-y-2">
              <Label htmlFor="task_name">Task Name</Label>
              <Input
                id="task_name"
                {...form.register('task_name', { required: true })}
                placeholder="Enter task name..."
              />
            </div>

            {/* Status Checkboxes */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="do_today"
                  {...form.register('do_today')}
                />
                <Label htmlFor="do_today">Do Today</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="do_this_week"
                  {...form.register('do_this_week')}
                />
                <Label htmlFor="do_this_week">{tCommon('status.thisWeek')}</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_reading"
                  {...form.register('is_reading')}
                />
                <Label htmlFor="is_reading">Reading</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="wait_for"
                  {...form.register('wait_for')}
                />
                <Label htmlFor="wait_for">Waiting For</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="postponed"
                  {...form.register('postponed')}
                />
                <Label htmlFor="postponed">Postponed</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="reviewed"
                  {...form.register('reviewed')}
                />
                <Label htmlFor="reviewed">Reviewed</Label>
              </div>
            </div>

            {/* Priority and Date */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Input
                  id="priority"
                  type="number"
                  min="0"
                  max="10"
                  {...form.register('priority', { valueAsNumber: true })}
                  placeholder="0-10"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="do_on_date">Due Date</Label>
                <Input
                  id="do_on_date"
                  type="date"
                  {...form.register('do_on_date')}
                />
              </div>
            </div>

            {/* Time Expenditure */}
            <div className="space-y-2">
              <Label htmlFor="time_expenditure">Time Estimate</Label>
              <Input
                id="time_expenditure"
                {...form.register('time_expenditure')}
                placeholder="e.g., 2h, 30min, 1 day"
              />
            </div>

            {/* URL */}
            <div className="space-y-2">
              <Label htmlFor="url">URL</Label>
              <Input
                id="url"
                type="url"
                {...form.register('url')}
                placeholder="https://..."
              />
            </div>

            {/* Knowledge DB Entry */}
            <div className="space-y-2">
              <Label htmlFor="knowledge_db_entry">Knowledge DB Entry</Label>
              <Textarea
                id="knowledge_db_entry"
                {...form.register('knowledge_db_entry')}
                placeholder="Enter knowledge base notes..."
                rows={4}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end space-x-4 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? tCommon('common.loading') : 'Save Changes'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}