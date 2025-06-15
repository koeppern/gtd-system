'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';

const STORAGE_KEY = 'preferred-language';
const SUPPORTED_LOCALES = ['en', 'de'] as const;
type SupportedLocale = typeof SUPPORTED_LOCALES[number];

interface LanguageSettings {
  currentLanguage: SupportedLocale;
  isLoading: boolean;
  switchLanguage: (locale: SupportedLocale) => Promise<void>;
  getSupportedLocales: () => typeof SUPPORTED_LOCALES;
}

/**
 * Hook for managing user language preferences with persistence
 * 
 * Priority order:
 * 1. User database setting (when logged in)
 * 2. localStorage (browser-local)
 * 3. Browser language detection
 * 4. Default: English
 */
export function useLanguageSettings(): LanguageSettings {
  const [currentLanguage, setCurrentLanguage] = useState<SupportedLocale>('en');
  const [isLoading, setIsLoading] = useState(true);
  const { user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // Extract current locale from pathname
  const getCurrentLocaleFromPath = useCallback((): SupportedLocale => {
    if (pathname.startsWith('/de')) return 'de';
    if (pathname.startsWith('/en')) return 'en';
    return 'en'; // default
  }, [pathname]);

  // Detect browser language
  const getBrowserLanguage = useCallback((): SupportedLocale => {
    if (typeof window === 'undefined') return 'en';
    
    const browserLang = navigator.language.slice(0, 2);
    return SUPPORTED_LOCALES.includes(browserLang as SupportedLocale) 
      ? (browserLang as SupportedLocale) 
      : 'en';
  }, []);

  // Load language preference from localStorage
  const getStoredLanguage = useCallback((): SupportedLocale | null => {
    if (typeof window === 'undefined') return null;
    
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored && SUPPORTED_LOCALES.includes(stored as SupportedLocale) 
      ? (stored as SupportedLocale) 
      : null;
  }, []);

  // Save language preference to localStorage
  const saveLanguageToStorage = useCallback((locale: SupportedLocale) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, locale);
    }
  }, []);

  // Save language preference to user settings API
  const saveLanguageToAPI = useCallback(async (locale: SupportedLocale) => {
    if (!user) return;
    
    try {
      const response = await fetch('/api/users/me/settings/web/language', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ setting_value: locale })
      });
      
      if (!response.ok) {
        console.warn('Failed to save language preference to API');
      }
    } catch (error) {
      console.warn('Error saving language preference:', error);
    }
  }, [user]);

  // Load language preference from user settings API
  const loadLanguageFromAPI = useCallback(async (): Promise<SupportedLocale | null> => {
    if (!user) return null;
    
    try {
      const response = await fetch('/api/users/me/settings/web/language');
      
      if (response.ok) {
        const data = await response.json();
        const apiLang = data.setting_value;
        
        return apiLang && SUPPORTED_LOCALES.includes(apiLang) 
          ? apiLang 
          : null;
      }
    } catch (error) {
      console.warn('Error loading language preference from API:', error);
    }
    
    return null;
  }, [user]);

  // Navigate to new language route
  const navigateToLanguage = useCallback((locale: SupportedLocale) => {
    const currentPathLocale = getCurrentLocaleFromPath();
    
    if (currentPathLocale === locale) return; // Already on correct language
    
    // Remove current locale from pathname
    let pathWithoutLocale = pathname;
    if (pathname.startsWith('/de')) {
      pathWithoutLocale = pathname.slice(3) || '/';
    } else if (pathname.startsWith('/en')) {
      pathWithoutLocale = pathname.slice(3) || '/';
    }
    
    // Construct new path
    const newPath = locale === 'en' 
      ? pathWithoutLocale 
      : `/${locale}${pathWithoutLocale}`;
    
    router.push(newPath as any);
  }, [pathname, router, getCurrentLocaleFromPath]);

  // Initialize language on mount
  useEffect(() => {
    const initializeLanguage = async () => {
      setIsLoading(true);
      
      // 1. Try to get from current URL path first
      const pathLocale = getCurrentLocaleFromPath();
      
      // 2. Try to get from user API settings
      const apiLanguage = await loadLanguageFromAPI();
      
      // 3. Try to get from localStorage
      const storedLanguage = getStoredLanguage();
      
      // 4. Fall back to browser language
      const browserLanguage = getBrowserLanguage();
      
      // Determine preferred language (priority order)
      const preferredLanguage = apiLanguage || storedLanguage || browserLanguage;
      
      // Use path locale if it matches supported languages, otherwise use preferred
      const finalLanguage = pathLocale || preferredLanguage;
      
      setCurrentLanguage(finalLanguage);
      
      // If preferred differs from path, navigate to preferred
      if (pathLocale !== preferredLanguage && preferredLanguage !== 'en') {
        navigateToLanguage(preferredLanguage);
      }
      
      setIsLoading(false);
    };

    initializeLanguage();
  }, [getCurrentLocaleFromPath, loadLanguageFromAPI, getStoredLanguage, getBrowserLanguage, navigateToLanguage]);

  // Update current language when pathname changes
  useEffect(() => {
    const pathLocale = getCurrentLocaleFromPath();
    setCurrentLanguage(pathLocale);
  }, [pathname, getCurrentLocaleFromPath]);

  // Switch language function
  const switchLanguage = useCallback(async (locale: SupportedLocale) => {
    setCurrentLanguage(locale);
    
    // Save to localStorage immediately
    saveLanguageToStorage(locale);
    
    // Save to API (async, non-blocking)
    saveLanguageToAPI(locale);
    
    // Navigate to new language route
    navigateToLanguage(locale);
  }, [saveLanguageToStorage, saveLanguageToAPI, navigateToLanguage]);

  const getSupportedLocales = useCallback(() => SUPPORTED_LOCALES, []);

  return {
    currentLanguage,
    isLoading,
    switchLanguage,
    getSupportedLocales
  };
}