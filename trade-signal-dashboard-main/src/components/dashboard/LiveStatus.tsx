import { useEffect, useState } from "react";
import { timeAgo } from "@/lib/format";
import { cn } from "@/lib/utils";

interface Props {
  isFetching: boolean;
  lastUpdated?: Date;
  hasError?: boolean;
}

export function LiveStatus({ isFetching, lastUpdated, hasError }: Props) {
  const [, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick((n) => n + 1), 30_000);
    return () => clearInterval(id);
  }, []);

  const label = hasError
    ? "Connection error"
    : isFetching
      ? "Updating…"
      : lastUpdated
        ? `Live · updated ${timeAgo(lastUpdated)}`
        : "Connecting…";

  const dotColor = hasError ? "bg-destructive" : "bg-live";

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-2 rounded-full border border-border bg-surface-2 px-3 py-1.5 text-xs"
    >
      <span className="relative flex h-2 w-2">
        <span
          className={cn(
            "absolute inline-flex h-full w-full rounded-full opacity-60",
            dotColor,
            !hasError && "animate-live-pulse"
          )}
        />
        <span className={cn("relative inline-flex h-2 w-2 rounded-full", dotColor)} />
      </span>
      <span className="font-medium text-muted-foreground">{label}</span>
    </div>
  );
}
