import { motion } from "framer-motion";
import type { Signal } from "@/lib/schema";
import { signalTokens, formatSigned } from "@/lib/format";
import { cn } from "@/lib/utils";

interface Props {
  signal: Signal;
  actionValue: number;
  ticker: string;
  name: string;
}

export function SignalHero({ signal, actionValue, ticker, name }: Props) {
  const tok = signalTokens(signal);
  const confidence = Math.min(100, Math.round(Math.abs(actionValue) * 100));

  return (
    <section className="surface-card relative overflow-hidden p-6 md:p-8">
      <div className="absolute inset-0 opacity-30 pointer-events-none" aria-hidden>
        <div className={cn("absolute -top-20 -right-20 h-64 w-64 rounded-full blur-3xl", tok.gradient)} />
      </div>
      <div className="relative grid gap-6 md:grid-cols-[auto_1fr] md:items-center">
        <motion.div
          initial={{ scale: 0.85, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          key={signal + ticker}
          transition={{ type: "spring", stiffness: 220, damping: 18 }}
          className={cn(
            "flex flex-col items-center justify-center rounded-2xl px-10 py-8 text-primary-foreground",
            tok.gradient,
            tok.glow
          )}
        >
          <div className="font-display text-5xl font-bold tracking-tight md:text-6xl">{signal}</div>
          <div className="mt-1 text-xs font-medium uppercase tracking-widest opacity-90">Signal</div>
        </motion.div>

        <div className="space-y-4">
          <div>
            <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
              {ticker}
            </div>
            <h2 className="font-display text-2xl font-semibold md:text-3xl">{name}</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:max-w-md">
            <Metric label="Action Value" value={formatSigned(actionValue)} accent={tok.text} />
            <Metric label="Confidence" value={`${confidence}%`} accent={tok.text} />
          </div>
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className="rounded-xl border border-border bg-surface-2 px-4 py-3">
      <div className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className={cn("font-mono text-2xl font-bold", accent)}>{value}</div>
    </div>
  );
}
