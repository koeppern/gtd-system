'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { AppLayout } from '@/components/layout/app-layout';
import { DashboardOverview } from '@/components/gtd/dashboard-overview';
import { QuickCapture } from '@/components/gtd/quick-capture';
import { TodayTasks } from '@/components/gtd/today-tasks';
import { WeeklyProjects } from '@/components/gtd/weekly-projects';
import { InboxItems } from '@/components/gtd/inbox-items';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  PlusIcon, 
  ClockIcon,
  FolderIcon,
  InboxIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

export default function HomePage() {
  // Fetch dashboard data
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => api.dashboard.getStats(),
  });

  const { data: todayTasks, isLoading: todayLoading } = useQuery({
    queryKey: ['tasks', 'today'],
    queryFn: () => api.tasks.getToday(),
  });

  const { data: weeklyProjects, isLoading: weeklyLoading } = useQuery({
    queryKey: ['projects', 'weekly'],
    queryFn: () => api.projects.getWeekly(),
  });

  const { data: inboxTasks, isLoading: inboxLoading } = useQuery({
    queryKey: ['tasks', 'inbox'],
    queryFn: () => api.tasks.list({ 
      limit: 10, 
      do_today: false, 
      do_this_week: false, 
      is_done: false 
    }),
  });

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Good morning! 👋</h1>
            <p className="text-muted-foreground">
              Here's what's on your plate today.
            </p>
          </div>
          <Button size="lg" className="gtd-button-primary">
            <PlusIcon className="mr-2 h-5 w-5" />
            Quick Add
          </Button>
        </div>

        {/* Quick Capture */}
        <QuickCapture />

        {/* Dashboard Overview */}
        <DashboardOverview stats={stats} isLoading={statsLoading} />

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Today's Tasks */}
          <div className="lg:col-span-2">
            <TodayTasks tasks={todayTasks || []} isLoading={todayLoading} />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Inbox */}
            <InboxItems 
              tasks={inboxTasks?.items || []} 
              isLoading={inboxLoading} 
            />

            {/* Weekly Projects */}
            <WeeklyProjects 
              projects={weeklyProjects || []} 
              isLoading={weeklyLoading} 
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-lg">
                <InboxIcon className="mr-2 h-5 w-5 text-orange-500" />
                Process Inbox
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {inboxTasks?.total || 0} items to process
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-lg">
                <ClockIcon className="mr-2 h-5 w-5 text-blue-500" />
                Weekly Review
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Review and plan your week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-lg">
                <FolderIcon className="mr-2 h-5 w-5 text-green-500" />
                Projects
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {stats?.active_projects || 0} active projects
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-lg">
                <ChartBarIcon className="mr-2 h-5 w-5 text-purple-500" />
                Analytics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                View productivity insights
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}