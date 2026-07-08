import { motion } from "framer-motion";
import type { Indicator } from "@/lib/schema";
import { statusBgClass, statusColorClass } from "@/lib/format";
import { cn } from "@/lib/utils";
import { GlassCard } from "../ui/GlassCard";

interface Props {
  indicators: Indicator[];
}

export function IndicatorsPanel({ indicators }: Props) {
  return (
    <GlassCard className="h-full">
      <PanelHeader title="Technical Indicators" subtitle="Normalised 0–1 with status" />
      <ul className="mt-6 space-y-4">
        {indicators.map((ind, i) => (
          <li key={ind.name} className="grid grid-cols-[80px_1fr_auto] items-center gap-4">
            <span className="font-sans text-xs font-semibold text-foreground/80 uppercase tracking-wider">{ind.name}</span>
            <div className="h-1.5 overflow-hidden rounded-full bg-foreground/10">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.max(2, ind.value * 100)}%` }}
                transition={{ duration: 1, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                className={cn("h-full rounded-full shadow-sm", statusBgClass(ind.status))}
              />
            </div>
            <div className="flex items-center gap-3">
              <span className="font-sans text-xs font-bold text-foreground tabular-nums">
                {ind.value.toFixed(2)}
              </span>
              <span className={cn("min-w-[52px] text-right text-[10px] font-bold uppercase tracking-widest", statusColorClass(ind.status))}>
                {ind.status}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </GlassCard>
  );
}

export function PanelHeader({ title, subtitle, right }: { title: string; subtitle?: string; right?: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-border/50 pb-4">
      <div>
        <h3 className="font-sans text-lg font-bold text-foreground tracking-tight">{title}</h3>
        {subtitle && <p className="text-xs font-medium text-muted-foreground mt-1">{subtitle}</p>}
      </div>
      {right}
    </div>
  );
}
