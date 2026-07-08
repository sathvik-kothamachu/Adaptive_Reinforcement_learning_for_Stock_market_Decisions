import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HeroSignalProps {
  signal: string;
  ticker: string;
  name: string;
}

export const HeroSignal = ({ signal, ticker, name }: HeroSignalProps) => {
  const isBuy = signal.toUpperCase() === 'BUY';
  const isSell = signal.toUpperCase() === 'SELL';
  
  const accentColor = isBuy 
    ? 'text-signal-buy' 
    : isSell 
    ? 'text-signal-sell' 
    : 'text-signal-hold';
    
  const glowColor = isBuy 
    ? 'shadow-signal-buy/20' 
    : isSell 
    ? 'shadow-signal-sell/20' 
    : 'shadow-signal-hold/20';

  return (
    <div className="flex flex-col items-center justify-center py-10 text-center relative">
      {/* Background Aura */}
      <motion.div
        animate={{ 
          scale: [1, 1.2, 1],
          opacity: [0.1, 0.2, 0.1]
        }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        className={cn(
          "absolute inset-0 m-auto w-64 h-64 rounded-full blur-[80px]",
          isBuy ? "bg-signal-buy" : isSell ? "bg-signal-sell" : "bg-signal-hold"
        )}
      />

      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="z-10"
      >
        <p className="text-sm font-bold tracking-[0.3em] text-muted-foreground uppercase mb-2">
          Final Recommendation
        </p>
        
        <h1 className={cn(
          "text-8xl md:text-9xl font-black tracking-tighter mb-4",
          accentColor,
          isBuy ? "text-glow-buy" : isSell ? "text-glow-sell" : "text-glow-primary"
        )}>
          {signal}
        </h1>

        <div className="flex items-center justify-center gap-3 bg-foreground/5 backdrop-blur-md px-6 py-2 rounded-full border border-border">
          <span className="text-xl font-bold text-foreground">{ticker}</span>
          <div className="h-4 w-[1px] bg-border" />
          <span className="text-sm text-muted-foreground font-medium">{name}</span>
        </div>
      </motion.div>

      {/* Pulsing indicator */}
      <motion.div
        animate={{ y: [0, 5, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="mt-12 text-muted-foreground/40"
      >
        <div className="flex flex-col items-center gap-1">
          <span className="text-[10px] font-bold uppercase tracking-widest">Analysis Feed</span>
          <div className="w-[1px] h-8 bg-gradient-to-b from-foreground/20 to-transparent" />
        </div>
      </motion.div>
    </div>
  );
};
