'use client';

import * as React from 'react';
import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { UserProfileMenu } from '@/components/ui/user-profile-menu';
import { LanguageSwitcher } from '@/components/ui/language-switcher';
import { CentralLogin } from '@/components/auth/central-login';
import { useAuth } from '@/contexts/auth-context';
import { useLanguageSettings } from '@/hooks/use-language-settings';
import { useKeyboardShortcuts, useSearchFieldRef } from '@/hooks/use-keyboard-shortcuts';
import { 
  HomeIcon,
  FolderIcon,
  SunIcon,
  MoonIcon,
  Bars3Icon,
  ListBulletIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ChevronDoubleRightIcon,
  ChevronDoubleLeftIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  FolderIcon as FolderIconSolid,
  ListBulletIcon as ListBulletIconSolid,
} from '@heroicons/react/24/solid';

interface AppLayoutProps {
  children: React.ReactNode;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  iconSolid: React.ComponentType<{ className?: string }>;
  badge?: number;
}

// Navigation items will be translated in the component
const navigationKeys = [
  {
    nameKey: 'navigation.dashboard',
    href: '/',
    icon: HomeIcon,
    iconSolid: HomeIconSolid,
  },
  {
    nameKey: 'navigation.projects',
    href: '/projects',
    icon: FolderIcon,
    iconSolid: FolderIconSolid,
  },
  {
    nameKey: 'navigation.tasks',
    href: '/tasks',
    icon: ListBulletIcon,
    iconSolid: ListBulletIconSolid,
  },
];

const secondaryNavigation: NavItem[] = [];

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const { theme, setTheme } = useTheme();
  const { user, login, logout, isLoading } = useAuth();
  const pathname = usePathname();
  const t = useTranslations('common');
  
  // Initialize language settings (will auto-load user preferences)
  const { isLoading: _languageLoading } = useLanguageSettings();

  // Search field refs and keyboard shortcuts
  const { ref: globalSearchRef, searchFieldRef: globalSearchFieldRef } = useSearchFieldRef();
  
  // Initialize keyboard shortcuts for global search (CTRL-K)
  useKeyboardShortcuts({
    globalSearchRef: globalSearchFieldRef
  });

  // Load sidebar state from localStorage on mount
  useEffect(() => {
    setIsClient(true);
    const savedCollapsed = localStorage.getItem('gtd-sidebar-collapsed');
    if (savedCollapsed !== null) {
      setSidebarCollapsed(savedCollapsed === 'true');
    }
  }, []);

  // Save sidebar state to localStorage when it changes
  useEffect(() => {
    if (isClient) {
      localStorage.setItem('gtd-sidebar-collapsed', sidebarCollapsed.toString());
    }
  }, [sidebarCollapsed, isClient]);

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar */}
      <div className={cn(
        'fixed inset-0 z-50 lg:hidden',
        sidebarOpen ? 'block' : 'hidden'
      )}>
        <div className="fixed inset-0 bg-black/20" onClick={() => setSidebarOpen(false)} />
        <div className={cn(
          "fixed inset-y-0 left-0 w-64 bg-background border-r border-border",
          !user && "blur-sm"
        )}>
          <SidebarContent 
            onItemClick={() => setSidebarOpen(false)} 
            pathname={pathname} 
            collapsed={false}
            onToggleCollapse={() => {}}
          />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className={cn(
        "hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-40 lg:block lg:bg-background lg:border-r lg:border-border transition-all duration-300 ease-in-out",
        sidebarCollapsed ? "lg:w-16" : "lg:w-64",
        !user && "blur-sm"
      )}>
        <SidebarContent 
          pathname={pathname} 
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {/* Main content */}
      <div className={cn(
        "transition-all duration-300 ease-in-out",
        sidebarCollapsed ? "lg:pl-16" : "lg:pl-64"
      )}>
        {/* Top navigation */}
        <div className="sticky top-0 z-30 flex h-16 items-center gap-x-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 sm:gap-x-6 sm:px-6">
          <Button
            variant="ghost"
            size="icon"
            className={cn("lg:hidden", !user && "blur-sm")}
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
            <span className="sr-only">{t('buttons.openSidebar')}</span>
          </Button>

          {/* Search */}
          <div className={cn(
            "flex flex-1 gap-x-4 self-stretch lg:gap-x-6",
            !user && "blur-sm"
          )}>
            <div className="relative flex flex-1 items-center">
              <MagnifyingGlassIcon className="pointer-events-none absolute left-3 h-5 w-5 text-muted-foreground" />
              <input
                ref={globalSearchRef}
                className="block h-10 w-full rounded-md border border-input bg-background pl-10 pr-4 text-sm placeholder:text-muted-foreground focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                placeholder={t('search.globalPlaceholder')}
                type="search"
                disabled={!user}
              />
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-x-4 lg:gap-x-6">
            {/* Language switcher */}
            <LanguageSwitcher />
            
            {/* Theme toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className={cn(!user && "blur-sm")}
            >
              <SunIcon className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <MoonIcon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">{t('buttons.toggleTheme')}</span>
            </Button>

            {/* Profile - Only show when logged in */}
            {user && (
              <UserProfileMenu 
                user={user}
                onLogin={login}
                onLogout={logout}
                isLoading={isLoading}
              />
            )}
          </div>
        </div>

        {/* Page content */}
        <main className={cn(
          "px-4 py-8 sm:px-6 lg:px-8",
          !user && "blur-sm"
        )}>
          {children}
        </main>
      </div>

      {/* Central Login Overlay */}
      {!user && (
        <CentralLogin 
          onLogin={login}
          isAuthLoading={isLoading}
        />
      )}
    </div>
  );
}

function SidebarContent({ 
  onItemClick, 
  pathname,
  collapsed = false,
  onToggleCollapse
}: { 
  onItemClick?: () => void; 
  pathname: string; 
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}) {
  const t = useTranslations('common');
  return (
    <div className="flex h-full flex-col">
      {/* Logo and Toggle */}
      <div className="flex h-16 shrink-0 items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <CheckCircleIcon className="h-5 w-5" />
          </div>
          {!collapsed && <span className="text-xl font-bold">{t('navigation.gtd')}</span>}
        </div>
        
        {/* Toggle Button */}
        {onToggleCollapse && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleCollapse}
            className="h-8 w-8 hover:bg-accent"
          >
            {collapsed ? (
              <ChevronDoubleRightIcon className="h-4 w-4" />
            ) : (
              <ChevronDoubleLeftIcon className="h-4 w-4" />
            )}
            <span className="sr-only">
              {collapsed ? t('buttons.expandSidebar') : t('buttons.collapseSidebar')}
            </span>
          </Button>
        )}
      </div>

      {/* Navigation */}
      <nav className={cn(
        "flex flex-1 flex-col transition-all duration-300",
        collapsed ? "px-2" : "px-4"
      )}>
        <ul role="list" className="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" className={cn(
              "space-y-1",
              collapsed ? "mx-0" : "-mx-2"
            )}>
              {navigationKeys.map((item) => {
                const isCurrent = pathname === item.href;
                const Icon = isCurrent ? item.iconSolid : item.icon;
                const translatedName = t(item.nameKey as any);
                return (
                  <li key={item.nameKey}>
                    <a
                      href={item.href}
                      onClick={onItemClick}
                      className={cn(
                        'group flex text-sm font-semibold leading-6 transition-colors',
                        collapsed 
                          ? 'p-1 justify-center items-center rounded-lg hover:bg-accent/50' 
                          : 'gap-x-3 p-2 rounded-md',
                        isCurrent
                          ? collapsed
                            ? 'text-primary bg-primary/10'
                            : 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                      )}
                      title={collapsed ? translatedName : undefined}
                    >
                      <Icon className="h-6 w-6 shrink-0" />
                      {!collapsed && (
                        <>
                          <span className="flex-1">{translatedName}</span>
                        </>
                      )}
                    </a>
                  </li>
                );
              })}
            </ul>
          </li>

          {secondaryNavigation.length > 0 && !collapsed && (
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
                        false // No current state needed for secondary nav
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