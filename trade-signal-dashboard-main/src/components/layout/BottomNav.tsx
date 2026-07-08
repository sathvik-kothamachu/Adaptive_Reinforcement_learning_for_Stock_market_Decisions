import React from 'react';
import { Home, Bot, Settings, TrendingUp } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export const BottomNav = () => {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 w-[calc(100%-3rem)] max-w-sm pointer-events-none">
      <nav className="flex h-16 items-center justify-between rounded-full border border-white/10 bg-black/60 px-8 shadow-2xl backdrop-blur-xl supports-[backdrop-filter]:bg-black/40 pointer-events-auto">
        <NavButton to="/" icon={<Home size={22} />} label="Home" />
        <NavButton to="/market" icon={<TrendingUp size={22} />} label="Market" />
        <NavButton to="/bot" icon={<Bot size={22} />} label="Bot" />
        <NavButton to="/settings" icon={<Settings size={22} />} label="Setup" />
      </nav>
    </div>
  );
};

const NavButton = ({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `flex flex-col items-center gap-1 transition-all duration-300 ${
        isActive 
          ? 'text-primary scale-110 translate-y-[-4px]' 
          : 'text-muted-foreground hover:text-foreground hover:scale-105'
      }`
    }
  >
    {icon}
    <span className="text-[10px] font-bold opacity-0 h-0 transition-all duration-300 sm:opacity-100 sm:h-auto sm:mt-1">{label}</span>
  </NavLink>
);
