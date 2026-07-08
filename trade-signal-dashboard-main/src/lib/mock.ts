import type { Analysis, IndicatorStatus, Regime, Signal } from "./schema";
import { NIFTY_TICKERS } from "./constants";

const INDICATOR_NAMES = ["MACD", "RSI", "ADX", "ATR", "OBV", "Stoch %K", "CCI", "Bollinger"];

function seeded(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

function statusFromValue(v: number): IndicatorStatus {
  if (v >= 0.75) return "Strong";
  if (v >= 0.5) return "Good";
  if (v >= 0.25) return "OK";
  return "Weak";
}

function signalFromAction(a: number): Signal {
  if (a > 0.3) return "BUY";
  if (a < -0.3) return "SELL";
  return "HOLD";
}

const REGIMES: Regime[] = ["Bullish", "Sideways", "Bearish"];

export function buildMockAnalysis(ticker: string): Analysis {
  const meta = NIFTY_TICKERS.find((s) => s.ticker === ticker) ?? NIFTY_TICKERS[0];
  const seed = ticker.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = seeded(seed);
  const action_value = +(rand() * 2 - 1).toFixed(2);

  const dates = Array.from({ length: 14 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (13 - i));
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  });

  const niftyDates = Array.from({ length: 60 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (59 - i));
    return d.toISOString().slice(0, 10);
  });

  let v = 22500;
  const niftyData = niftyDates.map((date) => {
    v += (rand() - 0.48) * 180;
    const r = rand();
    const regime: Regime = r > 0.18 ? "Bullish" : r > 0.08 ? "Sideways" : "Bearish";
    return { date, value: +v.toFixed(2), regime };
  });

  const bull = 60 + rand() * 30;
  const bear = rand() * 10;
  const sideways = 100 - bull - bear;

  return {
    ticker: meta.ticker,
    name: meta.name,
    signal: signalFromAction(action_value),
    action_value,
    technical_score: Math.round(40 + rand() * 50),
    sentiment_score: Math.round(35 + rand() * 55),
    regime_score: Math.round(60 + rand() * 35),
    indicators: INDICATOR_NAMES.map((name) => {
      const value = +rand().toFixed(2);
      return { name, value, status: statusFromValue(value) };
    }),
    sentiment_chart: {
      dates,
      scores: dates.map(() => +(rand() * 1.2 - 0.4).toFixed(2)),
    },
    headlines: [
      { text: `${meta.name} posts record quarterly profit, beats analyst estimates`, sentiment: "pos", source: "Reuters" },
      { text: `Brokerages upgrade ${meta.name} on margin expansion outlook`, sentiment: "pos", source: "Bloomberg" },
      { text: `${meta.name} announces capex plan, neutral near-term impact`, sentiment: "neu", source: "Mint" },
      { text: `Regulatory probe weighs on ${meta.name} sentiment`, sentiment: "neg", source: "Economic Times" },
      { text: `${meta.name} dividend confirmed, in line with consensus`, sentiment: "neu", source: "MoneyControl" },
    ],
    market_regime: {
      bull_pct: +bull.toFixed(1),
      sideways_pct: +sideways.toFixed(1),
      bear_pct: +bear.toFixed(1),
      nifty_data: niftyData,
    },
    backtest: {
      sharpe: +(0.6 + rand() * 1.0).toFixed(2),
      sortino: +(0.5 + rand() * 1.2).toFixed(2),
      cum_ret: +(rand() * 18).toFixed(2),
      ann_ret: +(6 + rand() * 12).toFixed(2),
      max_dd: -+(2 + rand() * 6).toFixed(2),
      win_rate: +(45 + rand() * 20).toFixed(1),
      buy_precision: +(40 + rand() * 25).toFixed(1),
      sell_precision: +(25 + rand() * 25).toFixed(1),
      period: "Jan 2025 – Apr 2026",
    },
  };
}
