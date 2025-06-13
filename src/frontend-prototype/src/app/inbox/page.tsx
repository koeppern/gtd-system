'use client';

import { AppLayout } from '@/components/layout/app-layout';
import { InboxItems } from '@/components/gtd/inbox-items';

export default function InboxPage() {
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
            <InboxItems />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}