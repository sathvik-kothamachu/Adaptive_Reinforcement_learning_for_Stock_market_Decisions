import type { Headline } from "@/lib/schema";
import { SentimentBarChart } from "@/components/charts/SentimentBarChart";
import { PanelHeader } from "./IndicatorsPanel";
import { cn } from "@/lib/utils";
import { GlassCard } from "../ui/GlassCard";

interface Props {
  dates: string[];
  scores: number[];
  headlines: Headline[];
}

const sentimentLabel = { pos: "Positive", neu: "Neutral", neg: "Negative" } as const;
const sentimentClass = {
  pos: "bg-signal-buy/20 text-signal-buy border-signal-buy/30",
  neu: "bg-foreground/10 text-foreground/70 border-border",
  neg: "bg-signal-sell/20 text-signal-sell border-signal-sell/30",
} as const;

export function SentimentPanel({ dates, scores, headlines }: Props) {
  return (
    <GlassCard className="h-full">
      <PanelHeader title="News Sentiment" subtitle="Last 14 days · headline polarity" />
      <div className="mt-6">
        <SentimentBarChart dates={dates} scores={scores} />
      </div>
      <div className="mt-6 border-t border-border/50 pt-6">
        <h4 className="mb-4 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
          Recent Headlines
        </h4>
        <ul className="space-y-3">
          {headlines.slice(0, 5).map((h, i) => (
            <li
              key={i}
              className="flex items-start gap-3 rounded-2xl border border-border bg-card/50 px-4 py-3 transition-colors hover:bg-card"
            >
              <span
                className={cn(
                  "mt-0.5 shrink-0 rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest",
                  sentimentClass[h.sentiment]
                )}
              >
                {sentimentLabel[h.sentiment]}
              </span>
              <div className="min-w-0">
                <p className="text-sm font-medium leading-relaxed text-foreground/90">{h.text}</p>
                {h.source && (
                  <p className="mt-1 text-[10px] uppercase tracking-wider text-muted-foreground/60">{h.source}</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </GlassCard>
  );
}
