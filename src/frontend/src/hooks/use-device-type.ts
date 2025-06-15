'use client';

import { useState, useEffect } from 'react';

export type DeviceType = 'mobile' | 'desktop';

interface DeviceTypeHook {
  deviceType: DeviceType;
  isMobile: boolean;
  isDesktop: boolean;
  hasHover: boolean;
  hasTouch: boolean;
}

/**
 * Hook to detect device type and capabilities
 * 
 * Uses multiple detection methods:
 * - CSS Media Query for hover capability
 * - Touch event support
 * - Screen width as fallback
 */
export function useDeviceType(): DeviceTypeHook {
  const [deviceType, setDeviceType] = useState<DeviceType>('desktop');
  const [hasHover, setHasHover] = useState(true);
  const [hasTouch, setHasTouch] = useState(false);

  useEffect(() => {
    const detectDevice = () => {
      // Check if we're in browser environment
      if (typeof window === 'undefined') {
        return;
      }

      // Primary detection: CSS Media Query for hover capability
      const hoverMediaQuery = window.matchMedia('(hover: hover)');
      const canHover = hoverMediaQuery.matches;

      // Secondary detection: Touch capability
      const touchCapable = 'ontouchstart' in window || 
                          navigator.maxTouchPoints > 0 || 
                          // @ts-ignore - IE specific
                          navigator.msMaxTouchPoints > 0;

      // Tertiary detection: Screen width (fallback)
      const screenWidth = window.innerWidth;
      const isNarrowScreen = screenWidth < 768; // Tailwind's md breakpoint

      // Determine device type
      // Mobile if: no hover capability OR touch capable with narrow screen
      const isMobileDevice = !canHover || (touchCapable && isNarrowScreen);

      setHasHover(canHover);
      setHasTouch(touchCapable);
      setDeviceType(isMobileDevice ? 'mobile' : 'desktop');
    };

    // Initial detection
    detectDevice();

    // Listen for changes (orientation, window resize)
    const hoverMediaQuery = window.matchMedia('(hover: hover)');
    const handleHoverChange = () => detectDevice();
    const handleResize = () => detectDevice();

    // Add event listeners
    hoverMediaQuery.addEventListener('change', handleHoverChange);
    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    // Cleanup
    return () => {
      hoverMediaQuery.removeEventListener('change', handleHoverChange);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  return {
    deviceType,
    isMobile: deviceType === 'mobile',
    isDesktop: deviceType === 'desktop',
    hasHover,
    hasTouch
  };
}