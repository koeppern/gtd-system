'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  ArrowRightOnRectangleIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

interface CentralLoginProps {
  onLogin: (email: string, password: string) => Promise<void>;
  isAuthLoading?: boolean;
}

export function CentralLogin({ onLogin, isAuthLoading = false }: CentralLoginProps) {
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('CentralLogin: handleLogin called with email:', email);
    setLoginLoading(true);
    try {
      await onLogin(email, password);
      setShowLoginDialog(false);
      setEmail('');
      setPassword('');
    } catch (error) {
      console.error('CentralLogin: Login failed:', error);
    } finally {
      setLoginLoading(false);
    }
  };

  // Loading Spinner während Auth-Prozess
  if (isAuthLoading || loginLoading) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="text-center space-y-6">
          {/* Großer Spinner */}
          <div className="mx-auto w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
          
          {/* Login Text */}
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-foreground">
              Anmeldung läuft...
            </h2>
            <p className="text-muted-foreground">
              Bitte warten Sie, während wir Sie anmelden.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Großer zentraler Login-Button
  return (
    <>
      <div className="fixed inset-0 bg-background/95 backdrop-blur-sm z-40 flex items-center justify-center">
        <div className="text-center space-y-8 max-w-md mx-auto px-6">
          {/* Welcome Message */}
          <div className="space-y-4">
            <div className="mx-auto w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
              <ArrowRightOnRectangleIcon className="w-10 h-10 text-primary" />
            </div>
            
            <h1 className="text-4xl font-bold text-foreground">
              Willkommen bei GTD
            </h1>
            
            <p className="text-lg text-muted-foreground">
              Melden Sie sich an, um Ihre Aufgaben und Projekte zu verwalten.
            </p>
          </div>

          {/* Großer Login Button */}
          <Button 
            onClick={() => setShowLoginDialog(true)}
            size="lg"
            className={cn(
              "w-full h-14 text-lg font-semibold",
              "bg-primary text-primary-foreground",
              "hover:bg-primary/90 hover:scale-[1.02]",
              "transition-all duration-200",
              "shadow-lg hover:shadow-xl"
            )}
          >
            <EnvelopeIcon className="w-6 h-6 mr-3" />
            Mit E-Mail anmelden
          </Button>

          {/* Additional Info */}
          <p className="text-sm text-muted-foreground">
            Nutzen Sie Ihr Supabase-Konto für die Anmeldung.
          </p>
        </div>
      </div>

      {/* Login Dialog */}
      <Dialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Bei GTD anmelden</DialogTitle>
            <DialogDescription>
              Melden Sie sich mit Ihrem Supabase-Konto an, um Ihre Aufgaben und Projekte zu verwalten.
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">E-Mail</Label>
              <Input
                id="email"
                type="email"
                placeholder="ihre.email@beispiel.de"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loginLoading}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Passwort</Label>
              <Input
                id="password"
                type="password"
                placeholder="Ihr Passwort"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loginLoading}
              />
            </div>
            
            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowLoginDialog(false)}
                disabled={loginLoading}
                className="flex-1"
              >
                Abbrechen
              </Button>
              
              <Button
                type="submit"
                disabled={loginLoading}
                className="flex-1"
              >
                {loginLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-primary-foreground/20 border-t-primary-foreground rounded-full animate-spin" />
                    Anmelden...
                  </div>
                ) : (
                  'Anmelden'
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}