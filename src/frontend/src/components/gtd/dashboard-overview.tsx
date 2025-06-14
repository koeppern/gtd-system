'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  CheckCircleIcon,
  ClockIcon,
  FolderIcon,
  ArrowTrendingUpIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';
import type { DashboardStats } from '@/types';
import { cn } from '@/lib/utils';

interface DashboardOverviewProps {
  stats?: DashboardStats;
  isLoading?: boolean;
}

export function DashboardOverview({ stats, isLoading }: DashboardOverviewProps) {
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 w-20 bg-muted animate-pulse rounded" />
              <div className="h-4 w-4 bg-muted animate-pulse rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-16 bg-muted animate-pulse rounded mb-1" />
              <div className="h-3 w-24 bg-muted animate-pulse rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const overviewCards = [
    {
      title: 'Active Projects',
      value: stats?.active_projects || 0,
      description: 'not completed projects',
      icon: FolderIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      trend: '+3%',
      trendUp: true,
      href: '/projects',
      clickable: true,
    },
    {
      title: 'Tasks Today',
      value: stats?.tasks_today || 0,
      description: `${stats?.pending_tasks || 0} pending`,
      icon: ClockIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      trend: '+12%',
      trendUp: true,
      href: '/tasks',
      clickable: true,
    },
    {
      title: 'Completed',
      value: stats?.completed_tasks || 0,
      description: `${Math.round(stats?.completion_rate_7d || 0)}% this week`,
      icon: CheckCircleIcon,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      trend: '+8%',
      trendUp: true,
      href: '/tasks?filter=completed',
      clickable: true,
    },
    {
      title: 'This Week',
      value: stats?.tasks_this_week || 0,
      description: 'tasks scheduled',
      icon: CalendarIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      trend: '-2%',
      trendUp: false,
      href: '/tasks?filter=week',
      clickable: true,
    },
  ];

  const handleCardClick = (card: typeof overviewCards[0]) => {
    if (card.clickable && card.href) {
      router.push(card.href as any);
    }
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {overviewCards.map((card, index) => (
        <Card 
          key={index} 
          className={cn(
            "transition-all duration-200",
            card.clickable 
              ? "hover:shadow-lg hover:scale-[1.02] cursor-pointer hover:border-primary/50" 
              : "hover:shadow-md"
          )}
          onClick={() => handleCardClick(card)}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <div className={cn(
              'h-8 w-8 rounded-full flex items-center justify-center transition-colors',
              card.bgColor,
              card.clickable && 'group-hover:bg-primary/20'
            )}>
              <card.icon className={cn('h-4 w-4', card.color)} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline justify-between">
              <div className="text-2xl font-bold">{card.value}</div>
              <div className={cn(
                'flex items-center text-xs',
                card.trendUp ? 'text-green-600' : 'text-red-600'
              )}>
                <ArrowTrendingUpIcon className={cn(
                  'h-3 w-3 mr-1',
                  !card.trendUp && 'rotate-180'
                )} />
                {card.trend}
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              {card.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}