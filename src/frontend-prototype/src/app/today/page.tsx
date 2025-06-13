'use client';

import { AppLayout } from '@/components/layout/app-layout';
import { TodayTasks } from '@/components/gtd/today-tasks';

export default function TodayPage() {
  return (
    <AppLayout>
      <div className="py-6">
        <div className="px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
              Today
            </h1>
            <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
              Focus on what needs to be done today
            </p>
          </div>
          
          <div className="mt-6">
            <TodayTasks />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}