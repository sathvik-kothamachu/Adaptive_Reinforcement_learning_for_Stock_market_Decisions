import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { NIFTY_TICKERS } from "@/lib/constants";

interface Props {
  value: string;
  onChange: (v: string) => void;
}

export function StockPicker({ value, onChange }: Props) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[230px] bg-foreground/5 border-border rounded-xl h-10 hover:bg-foreground/10 transition-colors" aria-label="Select Nifty 50 stock">
        <SelectValue placeholder="Select stock" />
      </SelectTrigger>
      <SelectContent className="bg-background/80 backdrop-blur-xl border-border text-foreground rounded-xl">
        {NIFTY_TICKERS.map((s) => (
          <SelectItem key={s.ticker} value={s.ticker} className="hover:bg-foreground/10 focus:bg-foreground/10 rounded-lg cursor-pointer">
            <span className="flex items-center justify-between gap-3 w-full pr-2">
              <span className="font-semibold">{s.name}</span>
              <span className="font-mono text-[10px] text-muted-foreground/70">
                {s.ticker.replace(".NS", "")}
              </span>
            </span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
