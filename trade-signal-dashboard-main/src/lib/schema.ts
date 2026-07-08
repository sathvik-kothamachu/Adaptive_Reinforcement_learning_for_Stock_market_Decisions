import { z } from "zod";

export const SignalSchema = z.enum(["BUY", "SELL", "HOLD"]);
export type Signal = z.infer<typeof SignalSchema>;

export const StatusSchema = z.enum(["Strong", "Good", "OK", "Weak"]);
export type IndicatorStatus = z.infer<typeof StatusSchema>;

export const RegimeSchema = z.enum(["Bullish", "Sideways", "Bearish"]);
export type Regime = z.infer<typeof RegimeSchema>;

export const HeadlineSentimentSchema = z.enum(["pos", "neu", "neg"]);

export const IndicatorSchema = z.object({
  name: z.string(),
  value: z.number(),
  status: StatusSchema,
});

export const HeadlineSchema = z.object({
  text: z.string(),
  sentiment: HeadlineSentimentSchema,
  source: z.string().nullable().optional(),
});

export const NiftyPointSchema = z.object({
  date: z.string(),
  value: z.number(),
  regime: RegimeSchema,
});

export const AnalysisSchema = z.object({
  ticker: z.string(),
  name: z.string(),
  signal: SignalSchema,
  action_value: z.number(),
  technical_score: z.number(),
  sentiment_score: z.number(),
  regime_score: z.number(),
  indicators: z.array(IndicatorSchema),
  sentiment_chart: z.object({
    dates: z.array(z.string()),
    scores: z.array(z.number()),
  }),
  headlines: z.array(HeadlineSchema),
  market_regime: z.object({
    bull_pct: z.number(),
    sideways_pct: z.number(),
    bear_pct: z.number(),
    nifty_data: z.array(NiftyPointSchema),
  }),
  backtest: z.object({
    sharpe: z.number(),
    sortino: z.number(),
    cum_ret: z.number(),
    ann_ret: z.number(),
    max_dd: z.number(),
    win_rate: z.number(),
    buy_precision: z.number(),
    sell_precision: z.number(),
    period: z.string(),
  }),
});

export type Analysis = z.infer<typeof AnalysisSchema>;
export type Indicator = z.infer<typeof IndicatorSchema>;
export type Headline = z.infer<typeof HeadlineSchema>;
export type NiftyPoint = z.infer<typeof NiftyPointSchema>;
