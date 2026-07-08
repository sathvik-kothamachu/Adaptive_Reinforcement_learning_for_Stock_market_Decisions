import type { Analysis } from "@/lib/schema";
import { NiftyLineChart } from "@/components/charts/NiftyLineChart";
import { RegimeDonut } from "@/components/charts/RegimeDonut";
import { PanelHeader } from "./IndicatorsPanel";
import { GlassCard } from "../ui/GlassCard";

interface Props {
  regime: Analysis["market_regime"];
}

export function RegimePanel({ regime }: Props) {
  return (
    <GlassCard className="h-full">
      <PanelHeader title="Market Regime" subtitle="Nifty 50 trajectory · regime distribution" />
      <div className="mt-6">
        <NiftyLineChart data={regime.nifty_data} />
      </div>
      <div className="mt-6 grid grid-cols-1 items-center gap-6 border-t border-border/50 pt-6 sm:grid-cols-[auto_1fr]">
        <div className="flex justify-center">
          <RegimeDonut bull={regime.bull_pct} sideways={regime.sideways_pct} bear={regime.bear_pct} />
        </div>
        <ul className="space-y-3">
          <RegimeRow label="Bullish" pct={regime.bull_pct} dotClass="bg-signal-buy" />
          <RegimeRow label="Sideways" pct={regime.sideways_pct} dotClass="bg-signal-hold" />
          <RegimeRow label="Bearish" pct={regime.bear_pct} dotClass="bg-signal-sell" />
        </ul>
      </div>
    </GlassCard>
  );
}

function RegimeRow({ label, pct, dotClass }: { label: string; pct: number; dotClass: string }) {
  return (
    <li className="flex items-center justify-between rounded-2xl border border-border bg-card/50 px-4 py-3">
      <span className="flex items-center gap-3 text-sm font-semibold text-foreground/90">
        <span className={`h-2 w-2 rounded-full shadow-[0_0_8px_rgba(var(--foreground),0.4)] ${dotClass}`} />
        {label}
      </span>
      <span className="font-sans text-sm font-bold tabular-nums text-foreground">
        {pct.toFixed(1)}%
      </span>
    </li>
  );
}
