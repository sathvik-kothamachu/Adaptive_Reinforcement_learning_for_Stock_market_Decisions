import type { Analysis } from "@/lib/schema";
import { PanelHeader } from "./IndicatorsPanel";
import { cn } from "@/lib/utils";
import { GlassCard } from "../ui/GlassCard";
import { useEffect, useState, useRef } from "react";
import { useInView } from "framer-motion";

interface Props {
  backtest: Analysis["backtest"];
}

const AnimatedMetric = ({ value, isPercent, good }: { value: number, isPercent: boolean, good: boolean }) => {
  const [displayValue, setDisplayValue] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (isInView) {
      let startTimestamp: number;
      const duration = 800;
      
      const step = (timestamp: number) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        setDisplayValue(easeOutQuart * value);

        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      };
      
      window.requestAnimationFrame(step);
    }
  }, [value, isInView]);

  return (
    <div ref={ref} className={cn(
      "mt-2 font-sans text-2xl font-black tabular-nums tracking-tighter",
      good ? "text-signal-buy" : "text-signal-sell"
    )}>
      {value >= 0 && !isPercent ? "+" : ""}
      {displayValue.toFixed(isPercent ? 1 : 2)}
      {isPercent ? "%" : ""}
    </div>
  );
};

export function BacktestPanel({ backtest: b }: Props) {
  const items = [
    { label: "Sharpe Ratio", value: b.sharpe, isPercent: false, good: b.sharpe >= 1 },
    { label: "Sortino Ratio", value: b.sortino, isPercent: false, good: b.sortino >= 1 },
    { label: "Win Rate", value: b.win_rate * 100, isPercent: true, good: b.win_rate >= 0.5 },
    { label: "Cumulative Return", value: b.cum_ret * 100, isPercent: true, good: b.cum_ret >= 0 },
    { label: "Annual Return", value: b.ann_ret * 100, isPercent: true, good: b.ann_ret >= 0 },
    { label: "Max Drawdown", value: b.max_dd * 100, isPercent: true, good: b.max_dd > -0.05 },
    { label: "BUY Precision", value: b.buy_precision * 100, isPercent: true, good: b.buy_precision >= 0.5 },
    { label: "SELL Precision", value: b.sell_precision * 100, isPercent: true, good: b.sell_precision >= 0.5 },
  ];

  return (
    <GlassCard>
      <PanelHeader
        title="Backtest Performance"
        subtitle={b.period}
      />
      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {items.map((m) => (
          <div key={m.label} className="rounded-2xl border border-white/5 bg-black/20 p-4 transition-colors hover:bg-black/40">
            <div className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
              {m.label}
            </div>
            <AnimatedMetric value={m.value} isPercent={m.isPercent} good={m.good} />
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
