import React from 'react';
import { Outlet } from 'react-router-dom';
import { BottomNav } from './BottomNav';

export const AppLayout = () => {
  return (
    <div className="relative min-h-screen bg-background text-foreground flex flex-col">
      {/* Animated Background Canvas */}
      <div className="bg-mesh" />
      
      {/* Main Content Area */}
      <main className="flex-1 w-full pb-28">
        <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
          <Outlet />
        </div>
      </main>

      {/* Universal Floating Dock Navigation */}
      <BottomNav />
    </div>
  );
};
