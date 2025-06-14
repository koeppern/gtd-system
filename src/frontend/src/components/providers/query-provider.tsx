'use client';

import * as React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { createCacheInvalidator, type CacheInvalidator } from '@/lib/cache-utils';

// Create optimized query client with intelligent caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Aggressive caching for better UX
      staleTime: 1000 * 60 * 10, // 10 minutes - data stays fresh longer
      gcTime: 1000 * 60 * 30, // 30 minutes - keep in cache longer
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors except 408 (timeout)
        if (error?.response?.status >= 400 && error?.response?.status < 500 && error?.response?.status !== 408) {
          return false;
        }
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
      refetchOnReconnect: true, // Refresh when internet connection returns
      refetchOnMount: false, // Don't refetch if data is still fresh
      // Stale-while-revalidate: show cached data immediately, update in background
      refetchInterval: 1000 * 60 * 15, // Background refresh every 15 minutes
    },
    mutations: {
      retry: false,
      // Optimistic updates enabled by default
      onError: (error, variables, context) => {
        console.warn('Mutation failed:', error);
      },
    },
  },
});

// Create cache invalidator for intelligent cache management
const cacheInvalidator = createCacheInvalidator(queryClient);

// Preload critical data on app startup
const preloadCriticalData = async () => {
  const { api } = await import('@/lib/api');
  
  try {
    // Preload essential data that users see immediately
    await Promise.allSettled([
      // Dashboard stats - shown on home page
      queryClient.prefetchQuery({
        queryKey: ['dashboard', 'stats'],
        queryFn: () => api.dashboard.getStats(),
        staleTime: 1000 * 60 * 5, // Refresh dashboard more frequently
      }),
      
      // User settings - needed for table configurations
      queryClient.prefetchQuery({
        queryKey: ['user', 'settings'],
        queryFn: () => api.userSettings.getAll(),
        staleTime: 1000 * 60 * 30, // Settings change rarely
      }),
      
      // Today's tasks - high priority
      queryClient.prefetchQuery({
        queryKey: ['tasks', 'today'],
        queryFn: () => api.tasks.getToday(),
        staleTime: 1000 * 60 * 2, // Today's tasks change frequently
      }),
      
      // Fields for dropdown options
      queryClient.prefetchQuery({
        queryKey: ['fields'],
        queryFn: () => api.fields.list(),
        staleTime: 1000 * 60 * 60, // Fields rarely change
      }),
    ]);
    
    console.log('✅ Critical data preloaded successfully');
  } catch (error) {
    console.warn('⚠️ Some preloading failed:', error);
  }
};

export function QueryProvider({ children }: { children: React.ReactNode }) {
  // Preload data and setup background refresh on first render
  React.useEffect(() => {
    // Small delay to let the app initialize first
    const timer = setTimeout(preloadCriticalData, 100);
    
    // Setup periodic background refresh for stale data
    const refreshInterval = setInterval(() => {
      cacheInvalidator.refreshStaleData();
    }, 1000 * 60 * 10); // Every 10 minutes
    
    return () => {
      clearTimeout(timer);
      clearInterval(refreshInterval);
    };
  }, []);

  // Refresh cache when the window gains focus (user returns to tab)
  React.useEffect(() => {
    const handleFocus = () => {
      cacheInvalidator.refreshStaleData();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

// Export query client and cache invalidator for manual cache management
export { queryClient, cacheInvalidator };