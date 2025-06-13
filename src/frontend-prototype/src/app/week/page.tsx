'use client';

import { AppLayout } from '@/components/layout/app-layout';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { CheckCircleIcon, CalendarDaysIcon } from '@heroicons/react/24/outline';

export default function WeekPage() {
  const { data: weeklyTasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks', 'week'],
    queryFn: () => api.tasks.getWeek(),
  });

  const { data: weeklyProjects, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects', 'weekly'],
    queryFn: () => api.projects.getWeekly(),
  });

  const isLoading = tasksLoading || projectsLoading;

  return (
    <AppLayout>
      <div className="py-6">
        <div className="px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
              This Week
            </h1>
            <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
              Tasks and projects scheduled for this week
            </p>
          </div>

          {isLoading ? (
            <div className="mt-6 text-center py-12">
              <div className="inline-flex items-center space-x-2 text-gray-500">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900 dark:border-white"></div>
                <span>Loading weekly items...</span>
              </div>
            </div>
          ) : (
            <div className="mt-6 space-y-8">
              {/* Weekly Projects */}
              <div>
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Projects for This Week
                </h2>
                {weeklyProjects?.length === 0 ? (
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    No projects scheduled for this week
                  </div>
                ) : (
                  <div className="grid gap-4 sm:grid-cols-2">
                    {weeklyProjects?.map((project) => (
                      <div
                        key={project.id}
                        className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800"
                      >
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {project.name}
                        </h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                          Field #{project.field_id || 'None'}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Weekly Tasks */}
              <div>
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Tasks for This Week
                </h2>
                {weeklyTasks?.length === 0 ? (
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    No tasks scheduled for this week
                  </div>
                ) : (
                  <ul className="space-y-3">
                    {weeklyTasks?.map((task) => (
                      <li
                        key={task.id}
                        className="flex items-start rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800"
                      >
                        <CheckCircleIcon className="mt-0.5 h-5 w-5 text-gray-400 dark:text-gray-500" />
                        <div className="ml-3 flex-1">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {task.name}
                          </p>
                          {task.project_id && (
                            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                              Project #{task.project_id}
                            </p>
                          )}
                        </div>
                        {task.do_today && (
                          <span className="ml-2 inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">
                            Today
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}