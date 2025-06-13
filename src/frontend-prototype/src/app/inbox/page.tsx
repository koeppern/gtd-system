'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { AppLayout } from '@/components/layout/app-layout';
import { InboxItems } from '@/components/gtd/inbox-items';

export default function InboxPage() {
  const { data: inboxTasks, isLoading } = useQuery({
    queryKey: ['tasks', 'inbox'],
    queryFn: () => api.tasks.list({
      limit: 50,
      do_today: false,
      do_this_week: false,
      is_done: false
    }),
  });

  return (
    <AppLayout>
      <div className="py-6">
        <div className="px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
              Inbox
            </h1>
            <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
              Process and organize tasks without a project
            </p>
          </div>
          
          <div className="mt-6">
            <InboxItems tasks={inboxTasks || []} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}