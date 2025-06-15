'use client';

import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { TaskEditForm } from '@/components/tasks/task-edit-form';
import { BackButton } from '@/components/ui/back-button';
import { api } from '@/lib/api';

export default function TaskEditPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations('tasks');
  const tCommon = useTranslations('common');
  
  const taskId = parseInt(params.id as string);
  const returnTo = searchParams.get('returnTo') || '/tasks';

  // Fetch task data
  const { data: task, isLoading, error } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => api.tasks.getById(taskId),
    enabled: !isNaN(taskId),
  });

  const handleBack = () => {
    // Navigate back with highlight parameter
    const url = new URL(returnTo, window.location.origin);
    url.searchParams.set('highlight', taskId.toString());
    router.push(url.pathname + url.search);
  };

  const handleSaveSuccess = () => {
    // After successful save, navigate back with highlight
    handleBack();
  };

  if (isNaN(taskId)) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-foreground mb-2">
            Invalid Task ID
          </h2>
          <p className="text-muted-foreground mb-4">
            The task ID provided is not valid.
          </p>
          <BackButton onClick={handleBack} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-foreground mb-2">
            {tCommon('common.error')}
          </h2>
          <p className="text-muted-foreground mb-4">
            Failed to load task data.
          </p>
          <BackButton onClick={handleBack} />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
        {/* Header with Back Button */}
        <div className="flex items-center space-x-4">
          <BackButton onClick={handleBack} />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {isLoading ? tCommon('common.loading') : `Edit: ${task?.task_name}`}
            </h1>
            <p className="text-muted-foreground">
              Modify task details and settings
            </p>
          </div>
        </div>

        {/* Edit Form */}
        {isLoading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="mt-2 text-muted-foreground">{tCommon('common.loading')}</p>
            </div>
          </div>
        ) : task ? (
          <TaskEditForm 
            task={task} 
            onSaveSuccess={handleSaveSuccess}
            onCancel={handleBack}
          />
        ) : null}
    </div>
  );
}