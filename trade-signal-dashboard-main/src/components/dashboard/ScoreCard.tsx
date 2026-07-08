import React, { useEffect, useState } from 'react';
import { motion, useAnimation, useInView } from "framer-motion";
import { scoreStatus, statusColorClass } from "@/lib/format";
import { cn } from "@/lib/utils";
import { GlassCard } from '../ui/GlassCard';

interface Props {
  label: string;
  score: number;
  description?: string;
  delay?: number;
}

export function ScoreCard({ label, score, description, delay = 0 }: Props) {
  const status = scoreStatus(score);
  const [displayScore, setDisplayScore] = useState(0);
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (isInView) {
      let startTimestamp: number;
      const duration = 1000; // 1 second animation

      const step = (timestamp: number) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        // Easing function for smooth slowdown at the end
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        setDisplayScore(Math.floor(easeOutQuart * score));

        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      };
      
      const timeoutId = setTimeout(() => {
        window.requestAnimationFrame(step);
      }, delay * 1000);

      return () => clearTimeout(timeoutId);
    }
  }, [score, isInView, delay]);

  return (
    <GlassCard delay={delay} className="flex flex-col justify-between relative overflow-hidden group">
      {/* Background Glow based on status */}
      <div className={cn(
        "absolute -right-12 -top-12 w-24 h-24 rounded-full blur-[40px] opacity-20 group-hover:opacity-40 transition-opacity",
        status === 'Strong' ? "bg-signal-buy" : status === 'Weak' ? "bg-signal-sell" : "bg-signal-hold"
      )} />

      <div ref={ref} className="z-10">
        <div className="flex items-start justify-between mb-4">
          <h3 className="text-sm font-semibold tracking-wide text-muted-foreground uppercase">{label}</h3>
          <span className={cn(
            "text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-foreground/5 border border-border",
            statusColorClass(status)
          )}>
            {status}
          </span>
        </div>
        
        <div className="flex items-baseline gap-1 mt-2">
          <span className="font-sans text-5xl font-black text-foreground tracking-tighter tabular-nums">
            {displayScore}
          </span>
          <span className="text-sm font-medium text-muted-foreground/60">/ 100</span>
        </div>

        <div className="mt-6 h-1.5 w-full rounded-full bg-foreground/5 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={isInView ? { width: `${score}%` } : { width: 0 }}
            transition={{ duration: 1, delay: delay + 0.2, ease: [0.16, 1, 0.3, 1] }}
            className={cn(
              "h-full rounded-full shadow-sm",
              status === 'Strong' ? "bg-signal-buy" : status === 'Weak' ? "bg-signal-sell" : "bg-signal-hold"
            )}
          />
        </div>
        
        {description && (
          <p className="mt-4 text-[11px] font-medium text-muted-foreground/80 leading-relaxed max-w-[90%]">
            {description}
          </p>
        )}
      </div>
    </GlassCard>
  );
}
