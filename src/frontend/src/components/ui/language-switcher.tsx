'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useLanguageSettings } from '@/hooks/use-language-settings';
import { 
  LanguageIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';

interface Language {
  code: string;
  name: string;
  flag: string;
}

const languages: Language[] = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' }
];

export function LanguageSwitcher() {
  const [isOpen, setIsOpen] = useState(false);
  const { currentLanguage, switchLanguage, isLoading } = useLanguageSettings();
  
  const currentLanguageInfo = languages.find(lang => lang.code === currentLanguage) || languages[0];

  const handleLanguageSwitch = async (newLocale: string) => {
    setIsOpen(false);
    await switchLanguage(newLocale as 'en' | 'de');
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
        className="h-9 w-9"
        aria-label="Switch language"
        disabled={isLoading}
      >
        <LanguageIcon className="h-5 w-5" />
        <ChevronDownIcon className="h-3 w-3 ml-1" />
      </Button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute right-0 top-full mt-1 z-50 min-w-[160px] bg-background border border-border rounded-md shadow-lg">
            <div className="py-1">
              {languages.map((language) => (
                <button
                  key={language.code}
                  onClick={() => handleLanguageSwitch(language.code)}
                  disabled={isLoading}
                  className={`w-full px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                    currentLanguageInfo?.code === language.code 
                      ? 'bg-accent text-accent-foreground' 
                      : 'text-muted-foreground'
                  }`}
                >
                  <span className="text-base">{language.flag}</span>
                  <span>{language.name}</span>
                  {currentLanguageInfo?.code === language.code && (
                    <span className="ml-auto text-xs">✓</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}