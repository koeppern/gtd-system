'use client';

import { Button } from '@/components/ui/button';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { useTranslations } from 'next-intl';

interface BackButtonProps {
  onClick: () => void;
  label?: string;
  className?: string;
}

export function BackButton({ onClick, label, className = '' }: BackButtonProps) {
  const t = useTranslations('common');
  
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={onClick}
      className={`flex items-center space-x-2 text-muted-foreground hover:text-foreground ${className}`}
    >
      <ArrowLeftIcon className="h-4 w-4" />
      <span>{label || 'Back'}</span>
    </Button>
  );
}