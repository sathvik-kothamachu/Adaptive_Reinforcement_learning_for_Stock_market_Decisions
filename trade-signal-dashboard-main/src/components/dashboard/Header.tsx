import { RefreshCw, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StockPicker } from "./StockPicker";
import { LiveStatus } from "./LiveStatus";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";

interface Props {
  ticker: string;
  onTickerChange: (t: string) => void;
  onRefresh: () => void;
  isFetching: boolean;
  lastUpdated?: Date;
  hasError?: boolean;
}

export function Header({ ticker, onTickerChange, onRefresh, isFetching, lastUpdated, hasError }: Props) {
  const { theme, setTheme } = useTheme();

  return (
    <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between w-full">
      <div className="flex items-center gap-3">
        <LiveStatus isFetching={isFetching} lastUpdated={lastUpdated} hasError={hasError} />
      </div>

      <div className="flex flex-1 items-center justify-end gap-3">
        <div className="w-full max-w-[240px] md:w-auto">
          <StockPicker value={ticker} onChange={onTickerChange} />
        </div>
        <Button
          variant="outline"
          size="icon"
          onClick={onRefresh}
          disabled={isFetching}
          aria-label="Refresh analysis"
          className="shrink-0 h-10 w-10 rounded-xl glass-dark hover:bg-black/10 dark:hover:bg-white/10 border-none"
        >
          <RefreshCw className={cn("h-4 w-4", isFetching && "animate-spin")} />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          aria-label="Toggle theme"
          className="shrink-0 h-10 w-10 rounded-xl glass-dark hover:bg-black/10 dark:hover:bg-white/10 border-none"
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>
      </div>
    </header>
  );
}
