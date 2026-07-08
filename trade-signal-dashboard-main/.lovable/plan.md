# Nifty 50 PPO Trading Dashboard

A responsive React + TypeScript SPA that visualises BUY/SELL/HOLD recommendations from your PPO model for 10 Nifty 50 stocks, fed by your existing Python REST API.

## What you get

**Header**
- App title + tagline ("PPO Reinforcement Learning · Live Market Analysis")
- Stock dropdown (10 Nifty 50 tickers)
- Manual Refresh button (spinner while fetching)
- Live status pill with pulsing dot ("Live · updated 2m ago")
- Theme toggle (dark default / light)

**Hero signal card**
- Large animated BUY / SELL / HOLD badge with colour-coded glow (green / red / amber)
- Action value (e.g. 0.73) and confidence label
- Stock name + ticker

**Score cards (3 across)**
- Technical Score, Sentiment Score, Regime Score
- Animated bar fills with status colour (Weak / OK / Good / Strong)

**Indicators panel**
- List of technical indicators (MACD, RSI, ADX, etc.) each with value, status chip, normalised bar

**Sentiment panel**
- Bar chart of last ~14 days of sentiment scores
- Recent headlines list with pos/neu/neg pill per item

**Market regime panel**
- Line chart of Nifty value, points coloured by regime (bull/sideways/bear)
- Donut showing % bull / sideways / bear

**Backtest performance panel**
- Grid of metrics: Sharpe, Sortino, Max Drawdown, Win Rate, Cumulative Return, Annual Return, Buy/Sell Precision
- Period label (e.g. "Jan 2025 – Apr 2026")

**States**
- Skeleton loaders on first load and ticker switch
- Toast (sonner) on fetch error with Retry
- Empty / partial-data fallbacks per panel

**Behaviour**
- React Query auto-refetches every 5 minutes; manual refresh invalidates cache
- Switching ticker triggers fresh fetch (cached per-ticker for 5 min)
- Fully responsive: 3-col grid → 2-col on tablet → single column on mobile
- Framer Motion: signal badge entrance, score-bar fills, panel fade-in, theme cross-fade
- Accessible: semantic landmarks, ARIA labels on charts and live region, keyboard nav

## Pages & routes

- `/` — single dashboard page (everything above)
- `*` — existing NotFound

## Tech & libraries

- React 18 + TypeScript + Vite (existing stack)
- Tailwind + shadcn/ui (existing) for layout, cards, dropdown, badge, skeleton, toast
- **Add**: `@tanstack/react-query`, `react-chartjs-2` + `chart.js`, `framer-motion`
- **Tests**: Vitest + React Testing Library (already scaffolded) + MSW for API mocking
- Theme via `next-themes`-style CSS class toggle on `<html>`; tokens in `index.css`

## API integration

You confirmed: public URL, CORS enabled. I'll add an `.env`-style constant `VITE_API_BASE_URL` and a single `fetchAnalysis(ticker)` function consuming:

```
GET {VITE_API_BASE_URL}/api/analyze?ticker=KOTAKBANK.NS
```

Expected response shape (per your spec): `signal`, `action_value`, `technical_score`, `sentiment_score`, `regime_score`, `indicators[]`, `sentiment_chart`, `headlines[]`, `market_regime{bull_pct,sideways_pct,bear_pct,nifty_data[]}`, `backtest{...}`.

A typed Zod schema validates responses; mismatches show a friendly toast and fall back to last cached payload.

After approval I'll ask you for the API base URL (or you can paste it) and add it as a Vite env var. Until then the fetcher falls back to a typed mock so the UI is fully usable.

## Design system

Dark-first financial theme with light-mode parity:
- Background: deep navy (`hsl(222 47% 6%)`) / light: `hsl(210 40% 98%)`
- Card surface: subtle gradient + 1px border, soft shadow
- Accents: green `hsl(142 76% 45%)` (BUY), red `hsl(0 84% 60%)` (SELL), amber `hsl(38 92% 55%)` (HOLD)
- Typography: Inter (body) + JetBrains Mono (numbers/tickers)
- Glow effect via animated `box-shadow` keyframes on signal badge

All colours defined as HSL tokens in `index.css`; Tailwind config extended with semantic names (`signal-buy`, `signal-sell`, `signal-hold`, `surface-1`, `surface-2`, `chart-grid`, etc.). No hardcoded colours in components.

## File structure

```
src/
  pages/Index.tsx                 # dashboard composition
  components/dashboard/
    Header.tsx                    # title, picker, refresh, theme
    StockPicker.tsx
    SignalHero.tsx                # animated BUY/SELL/HOLD
    ScoreCard.tsx                 # reusable for 3 scores
    IndicatorsPanel.tsx
    SentimentPanel.tsx            # chart + headlines
    RegimePanel.tsx               # line + donut
    BacktestPanel.tsx
    LiveStatus.tsx
  components/charts/
    SentimentBarChart.tsx
    NiftyLineChart.tsx
    RegimeDonut.tsx
    useChartTheme.ts              # shared chart.js options
  hooks/
    useAnalysis.ts                # React Query wrapper
    useTheme.ts
  lib/
    api.ts                        # fetchAnalysis + Zod schema
    mock.ts                       # fallback payload
    format.ts                     # number/percent helpers
    constants.ts                  # NIFTY_TICKERS list
  test/
    api.test.ts
    SignalHero.test.tsx
    ScoreCard.test.tsx
    useAnalysis.test.tsx          # MSW
```

## Build phases

1. Theme tokens, Tailwind extensions, layout shell, header with picker + theme toggle
2. API layer (Zod + React Query + mock fallback), loading/error states
3. Signal hero + score cards + indicators panel with animations
4. Sentiment, regime, and backtest panels with charts
5. Auto-refresh (5 min), live status, polish, responsive pass, accessibility audit
6. Tests (unit for formatters/schema, component tests for cards, MSW integration for hook)

## Out of scope (v1)

Historical portfolio chart, push notifications, multi-stock comparison, PWA, WebSocket streaming, auth — all noted for v2.
