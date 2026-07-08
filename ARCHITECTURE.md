# System Architecture Diagrams

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER BROWSER                                │
│                  http://localhost:5173                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    HTTP REST API
                    (JSON/CORS)
                         │
┌─────────────────────────┴────────────────────────────────────────┐
│                    FASTAPI SERVER                                │
│                http://localhost:8000                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Endpoints:                                              │  │
│  │  - /api/analyze?ticker=X  → Single stock analysis       │  │
│  │  - /api/all-stocks        → All stocks analysis         │  │
│  │  - /api/market-regime     → Market conditions           │  │
│  │  - /api/stocks            → Available symbols           │  │
│  │  - /api/chat              → Local AI Chatbot (Phi-3)    │  │
│  │  - /health                → Server status               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│              Python function imports                             │
│              (Institutional Upgrades)                            │
│                         │                                        │
├─────────────────────────┴────────────────────────────────────────┤
│              INSTITUTIONAL RL MODELS (PPO)                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Nifty50_RL_Trading_MultiStock.py                        │  │
│  │  - process_stock()       → Core analysis                │  │
│  │  - Optimized Reward      → Risk-aware (Bear Penalty)    │  │
│  │  - Macro Data Feed       → USD/INR, US10Y, VIX          │  │
│  │  - Sector Context        → Industry benchmarks          │  │
│  │  - PPO inference         → GPU Accelerated (RTX 4050)   │  │
│  │  - Trained models        → trained_models/ (500k steps) │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## 2. Request-Response Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER ACTION - Select stock (RELIANCE.NS) and click Refresh   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND - Call fetchAnalysis("RELIANCE.NS")                │
│    Location: src/lib/api.ts                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. HTTP REQUEST                                                 │
│    GET /api/analyze?ticker=RELIANCE.NS                         │
│    To: http://localhost:8000                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. FASTAPI SERVER                                               │
│    - Validates ticker format                                   │
│    - Loads market regime (cached)                              │
│    - Fetches Macro Data (VIX, USD/INR, US10Y)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. CALL INSTITUTIONAL MODEL FUNCTION                            │
│    result = process_stock(                                      │
│        ticker="RELIANCE.NS",                                    │
│        name="Reliance Industries",                              │
│        sector_ticker="^CNXENERGY",                              │
│        macro_df=...,                                            │
│        bull_pct, bear_pct, sideways_pct                         │
│    )                                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬──────────────────┐
        │                │                │                  │
        ↓                ↓                ↓                  ↓
    ┌────────┐    ┌────────────┐  ┌────────────┐  ┌──────────────┐
    │Download│    │Compute Tech│  │Sentiment   │  │Load PPO Model│
    │OHLCV   │    │Indicators  │  │(FinBERT)   │  │& GPU Backtest│
    └────────┘    └────────────┘  └────────────┘  └──────────────┘
        │                │                │                  │
        └────────────────┼────────────────┴──────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. MODEL PROCESSING (GPU ACCELERATED)                           │
│    - Scale features including Macro and Sector Context          │
│    - Load trained PPO model (Refined 500k steps)                │
│    - Run inference using NVIDIA RTX 4050 (CUDA 12.6)            │
│    - Apply Weighted Voting (Policy + Tech + Sent + Regime)      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. PYTHON DICT RESULT                                           │
│    {                                                             │
│        'Ticker': 'RELIANCE.NS',                                 │
│        'Name': 'Reliance Industries',                           │
│        'FINAL SIGNAL': 'BUY',                                   │
│        'Sharpe Ratio': '2.45',                                  │
│        'Sortino Ratio': '3.12',                                 │
│        'Max Drawdown': '8.2%',                                  │
│        'Win Rate': '58.1%',                                     │
│        'Buy Precision': '64.2%',                                │
│        'Sell Precision': '61.5%',                               │
│        'Cumulative Return': '18.5%',                            │
│        'Annualised Return': '14.5%',                            │
│        'Headlines': [...]                                       │
│    }                                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. TRANSFORM TO JSON SCHEMA                                      │
│    _transform_model_output() in api_server.py                   │
│    - Converts Python dict to Pydantic model                     │
│    - Validates against frontend schema                          │
│    - Adds calculated fields (scores, statuses)                  │
│    - Structures response for UI                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. JSON RESPONSE (sent to frontend)                             │
│    {                                                             │
│        "ticker": "RELIANCE.NS",                                 │
│        "name": "Reliance Industries",                           │
│        "signal": "BUY",                                         │
│        "action_value": 1.0,                                     │
│        "technical_score": 72,                                   │
│        "sentiment_score": 0.15,                                 │
│        "backtest": {...},                                       │
│        "indicators": [...],                                     │
│        "headlines": [...]                                       │
│    }                                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 10. FRONTEND RECEIVES RESPONSE                                  │
│     - Parses JSON                                               │
│     - Validates schema with Zod                                 │
│     - Updates React state                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 11. DISPLAY RESULTS                                             │
│     - Trading signal badge (BUY/SELL/HOLD)                      │
│     - Performance metrics (Sharpe, Sortino, etc)                │
│     - Technical indicators chart                                │
│     - Sentiment analysis                                        │
│     - Market regime breakdown                                   │
│     - Headlines with sentiment                                  │
│     - Backtest chart with portfolio value                       │
└─────────────────────────────────────────────────────────────────┘
```

## 3. File Organization

```
nif50/
├── 🐍 Python Backend
│   ├── api_server.py              ← FastAPI wrapper (NEW)
│   ├── Nifty50_RL_Trading_MultiStock.py  ← Model (UPDATED)
│   ├── .env.backend               ← Config (NEW)
│   ├── requirements-backend.txt   ← Dependencies (NEW)
│   ├── start_backend.bat/sh       ← Launcher (NEW)
│   ├── quick_start.bat/sh         ← Combined (NEW)
│   │
│   ├── trained_models/            ← PPO models (UNCHANGED)
│   │   ├── PPO_RELIANCE.NS.zip
│   │   ├── PPO_INFY.NS.zip
│   │   └── ...
│   │
│   ├── cache/                     ← Feature cache (UNCHANGED)
│   │   ├── features_RELIANCE.NS.csv
│   │   └── ...
│   │
│   └── logs/                      ← Training logs (UNCHANGED)
│       └── ...
│
├── ⚛️ React Frontend
│   └── trade-signal-dashboard-main/
│       ├── .env.local             ← Config (NEW)
│       ├── src/
│       │   └── lib/
│       │       ├── api.ts         ← API client (UPDATED)
│       │       ├── schema.ts      ← Schema (UNCHANGED)
│       │       └── ...
│       ├── package.json
│       ├── vite.config.ts
│       └── ...
│
└── 📚 Documentation
    ├── INTEGRATION_GUIDE.md       ← Complete guide (NEW)
    ├── SETUP_CHECKLIST.md         ← Setup steps (NEW)
    ├── TROUBLESHOOTING.md         ← Problem solving (NEW)
    ├── QUICK_REFERENCE.md         ← Quick ref (NEW)
    ├── INTEGRATION_SUMMARY.md     ← This project (NEW)
    └── ARCHITECTURE.md            ← This file (NEW)
```

## 4. Component Interaction

```
FRONTEND (React/TypeScript)
    │
    ├── App.tsx
    │   └── useAnalysis hook
    │       └── calls fetchAnalysis()
    │
    ├── src/lib/api.ts
    │   ├── fetchAnalysis(ticker)
    │   │   └── HTTP GET /api/analyze?ticker=X
    │   ├── fetchMarketRegime()
    │   │   └── HTTP GET /api/market-regime
    │   ├── fetchAllStocksAnalysis()
    │   │   └── HTTP GET /api/all-stocks
    │   └── fetchAvailableStocks()
    │       └── HTTP GET /api/stocks
    │
    └── src/lib/schema.ts
        └── Zod validation schemas
            (matches API response)

                    ↓↑ JSON over HTTP

API SERVER (FastAPI/Python)
    │
    ├── api_server.py (620 lines)
    │   ├── @app.get("/health")
    │   ├── @app.get("/api/analyze")
    │   │   └── calls process_stock()
    │   ├── @app.get("/api/all-stocks")
    │   │   └── parallel execution
    │   ├── @app.get("/api/market-regime")
    │   │   └── calls compute_regime()
    │   ├── @app.get("/api/stocks")
    │   └── @app.get("/docs")
    │
    ├── .env.backend (config)
    │
    └── Pydantic models (validation)

                    ↓↑ Direct imports

MODEL (Original Python - Unchanged)
    │
    └── Nifty50_RL_Trading_MultiStock.py
        ├── process_stock(ticker, name, regime_df, ...)
        │   ├── Download historical data
        │   ├── Compute technical indicators
        │   ├── Build sentiment column
        │   ├── Load PPO model
        │   ├── Run backtest
        │   └── Return results dict
        │
        ├── compute_regime()
        │   ├── Download NIFTY 50 index
        │   ├── Fit HMM for regime detection
        │   └── Return regime dataframe
        │
        ├── add_technical_indicators()
        ├── compute_technical_strength_score()
        ├── NiftyRecommendationEnv (RL env)
        ├── build_sentiment_column()
        └── ... other helper functions
```

## 5. Data Schema Transformation

```
Python Model Output (Dict)          JSON API Response (Schema)
─────────────────────────────────   ────────────────────────────

{                                   {
  'Ticker': 'RELIANCE.NS'     →       "ticker": "RELIANCE.NS",
  'Name': 'Reliance'          →       "name": "Reliance Industries",
  'FINAL SIGNAL': 'BUY'       →       "signal": "BUY",
  (implicit action value)     →       "action_value": 1.0,
  (calculated score)          →       "technical_score": 72,
  (from sentiment)            →       "sentiment_score": 0.15,
  (from regime)               →       "regime_score": 60,
  
  'Sharpe Ratio': '2.45'      →       "backtest": {
  'Sortino Ratio': '3.12'     →         "sharpe": 2.45,
  'Max Drawdown': '8.2%'      →         "sortino": 3.12,
  'Win Rate': '58.1%'         →         "max_dd": 0.082,
  'Buy Precision': '64.2%'    →         "win_rate": 0.581,
  'Sell Precision': '61.5%'   →         "buy_precision": 0.642,
  'Cumulative Return': '18.5%'    →     "sell_precision": 0.615,
  'Annualised Return': '14.5%'    →     "cum_ret": 0.185,
                                        "ann_ret": 0.145,
                                        "period": "2025-01-01..."
                                      },
  
  'Headlines': [...]          →       "headlines": [{
                                        "text": "...",
                                        "sentiment": "neu",
                                        "source": "..."
                                      }],
  
                              →       "indicators": [{
                              →         "name": "Sharpe Ratio",
                              →         "value": 2.45,
                              →         "status": "Good"
                              →       }],
                              
                              →       "sentiment_chart": {
                              →         "dates": [...],
                              →         "scores": [...]
                              →       },
                              
                              →       "market_regime": {
                              →         "bull_pct": 60,
                              →         "sideways_pct": 20,
                              →         "bear_pct": 20,
                              →         "nifty_data": [...]
                              →       }
}                                   }
```

## 6. Deployment Architecture (Optional)

```
Production Setup:

                    ┌──────────────────────┐
                    │  Internet / Users    │
                    └──────────────┬───────┘
                                   │
                    ┌──────────────┴────────────┐
                    │      Load Balancer        │
                    └──────────────┬────────────┘
                                   │
                    ┌──────────────┴────────────┐
         ┌──────────┴──────────┬────────────────┴─────────┐
         │                     │                          │
    ┌────▼────┐          ┌────▼────┐            ┌────▼────┐
    │Frontend  │          │Frontend  │            │Frontend  │
    │Container │          │Container │            │Container │
    │(React)   │          │(React)   │            │(React)   │
    └──────────┘          └──────────┘            └──────────┘
         │                    │                          │
         │                HTTP/REST API                 │
         │                                               │
         └────────────────────┬────────────────────────┘
                              │
                    ┌─────────▼────────┐
                    │ API Load Balancer │
                    └─────────┬────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
    │ Backend  │          │ Backend  │          │ Backend  │
    │ Container│          │ Container│          │ Container│
    │ (API)    │          │ (API)    │          │ (API)    │
    │ :8000    │          │ :8000    │          │ :8000    │
    └──────────┘          └──────────┘          └──────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────▼────────┐
                    │ Shared Resources  │
                    ├─────────────────┤
                    │ Model Cache     │
                    │ Feature Cache   │
                    │ Trained Models  │
                    │ Redis (optional)│
                    └─────────────────┘
```

---

This architecture ensures **zero model modification**, **production readiness**, and **scalability**.
