import React from 'react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  animate?: boolean;
  delay?: number;
}

export const GlassCard = ({ children, className, animate = true, delay = 0 }: GlassCardProps) => {
  const Component = animate ? motion.div : 'div';
  
  return (
    <Component
      initial={animate ? { opacity: 0, y: 20 } : undefined}
      animate={animate ? { opacity: 1, y: 0 } : undefined}
      transition={animate ? { duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] } : undefined}
      className={cn(
        "glass-dark rounded-[2rem] p-6 transition-all hover:bg-slate-900/50 hover:border-white/10 group",
        className
      )}
    >
      {children}
    </Component>
  );
};
