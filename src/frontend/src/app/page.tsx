'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { AppLayout } from '@/components/layout/app-layout';
import { DashboardOverview } from '@/components/gtd/dashboard-overview';

export default function HomePage() {
  // Fetch dashboard data
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => api.dashboard.getStats(),
  });

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              GTD Task Management System
            </p>
          </div>
        </div>

        {/* Dashboard Overview */}
        <DashboardOverview stats={stats} isLoading={statsLoading} />
      </div>
    </AppLayout>
  );
}