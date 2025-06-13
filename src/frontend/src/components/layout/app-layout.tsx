'use client';

import * as React from 'react';
import { useState } from 'react';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { 
  HomeIcon,
  InboxIcon,
  CalendarIcon,
  FolderIcon,
  ClockIcon,
  CheckCircleIcon,
  Cog6ToothIcon,
  MagnifyingGlassIcon,
  SunIcon,
  MoonIcon,
  Bars3Icon,
  BellIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  InboxIcon as InboxIconSolid,
  CalendarIcon as CalendarIconSolid,
  FolderIcon as FolderIconSolid,
  ClockIcon as ClockIconSolid,
} from '@heroicons/react/24/solid';

interface AppLayoutProps {
  children: React.ReactNode;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  iconSolid: React.ComponentType<{ className?: string }>;
  current: boolean;
  badge?: number;
}

const navigation: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/',
    icon: HomeIcon,
    iconSolid: HomeIconSolid,
    current: true,
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FolderIcon,
    iconSolid: FolderIconSolid,
    current: false,
  },
];

const secondaryNavigation = [];

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar */}
      <div className={cn(
        'fixed inset-0 z-50 lg:hidden',
        sidebarOpen ? 'block' : 'hidden'
      )}>
        <div className="fixed inset-0 bg-black/20" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 w-64 bg-background border-r border-border">
          <SidebarContent onItemClick={() => setSidebarOpen(false)} />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-40 lg:block lg:w-64 lg:bg-background lg:border-r lg:border-border">
        <SidebarContent />
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top navigation */}
        <div className="sticky top-0 z-30 flex h-16 items-center gap-x-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 sm:gap-x-6 sm:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
            <span className="sr-only">Open sidebar</span>
          </Button>

          {/* Search */}
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="relative flex flex-1 items-center">
              <MagnifyingGlassIcon className="pointer-events-none absolute left-3 h-5 w-5 text-muted-foreground" />
              <input
                className="block h-10 w-full rounded-md border border-input bg-background pl-10 pr-4 text-sm placeholder:text-muted-foreground focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                placeholder="Search tasks, projects..."
                type="search"
              />
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-x-4 lg:gap-x-6">
            {/* Theme toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              <SunIcon className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <MoonIcon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>

            {/* Notifications */}
            <Button variant="ghost" size="icon">
              <BellIcon className="h-6 w-6" />
              <span className="sr-only">View notifications</span>
            </Button>

            {/* Profile */}
            <Button variant="ghost" size="icon">
              <UserCircleIcon className="h-6 w-6" />
              <span className="sr-only">Your profile</span>
            </Button>
          </div>
        </div>

        {/* Page content */}
        <main className="px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
      </div>
    </div>
  );
}

function SidebarContent({ onItemClick }: { onItemClick?: () => void }) {
  return (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center px-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <CheckCircleIcon className="h-5 w-5" />
          </div>
          <span className="text-xl font-bold">GTD</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col px-4">
        <ul role="list" className="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" className="-mx-2 space-y-1">
              {navigation.map((item) => {
                const Icon = item.current ? item.iconSolid : item.icon;
                return (
                  <li key={item.name}>
                    <a
                      href={item.href}
                      onClick={onItemClick}
                      className={cn(
                        'group flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 transition-colors',
                        item.current
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                      )}
                    >
                      <Icon className="h-6 w-6 shrink-0" />
                      <span className="flex-1">{item.name}</span>
                      {item.badge && (
                        <span className={cn(
                          'ml-auto inline-block rounded-full px-2 py-1 text-xs',
                          item.current
                            ? 'bg-primary-foreground text-primary'
                            : 'bg-muted text-muted-foreground'
                        )}>
                          {item.badge}
                        </span>
                      )}
                    </a>
                  </li>
                );
              })}
            </ul>
          </li>

          {secondaryNavigation.length > 0 && (
            <li>
              <div className="text-xs font-semibold leading-6 text-muted-foreground px-2 mb-2">
                More
              </div>
              <ul role="list" className="-mx-2 space-y-1">
                {secondaryNavigation.map((item) => (
                  <li key={item.name}>
                    <a
                      href={item.href}
                      onClick={onItemClick}
                      className={cn(
                        'group flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 transition-colors',
                        item.current
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                      )}
                    >
                      <item.icon className="h-6 w-6 shrink-0" />
                      {item.name}
                    </a>
                  </li>
                ))}
              </ul>
            </li>
          )}

        </ul>
      </nav>
    </div>
  );
}