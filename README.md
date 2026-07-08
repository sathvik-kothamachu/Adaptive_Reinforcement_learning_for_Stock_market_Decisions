# Adaptive Reinforcement learning for Stock market Decisions


>
> Deep Reinforcement Learning (PPO) + Market Regime Detection + Financial Sentiment Analysis + Explainable AI + GPU Acceleration

# 📖 Overview

Our project is an AI-powered stock market decision support platform designed specifically for the Indian stock market (Nifty 50).

Unlike traditional stock analysis platforms that rely only on technical indicators, AMORS combines:

- Reinforcement Learning
- Financial News Sentiment Analysis
- Market Regime Detection
- Macroeconomic Indicators
- Explainable AI

to generate intelligent BUY, HOLD, and SELL recommendations.

The system is designed as a **decision support system**, not an autonomous trading bot.

---

# 🎯 Problem Statement

Retail investors often make investment decisions based on:

- YouTube recommendations
- Telegram stock groups
- Instagram influencers
- Paid stock advisors

without verifying whether the recommendation is technically or fundamentally valid.

Existing platforms generally suffer from several limitations:

- Only technical analysis
- No market regime awareness
- No financial news understanding
- No AI explainability
- No unified decision-making framework

As a result, investors become vulnerable to misinformation, pump-and-dump schemes, and emotional trading.

---

# 💡 Proposed Solution

AMORS solves these problems by integrating multiple sources of market intelligence into a single AI-driven platform.

The system combines:

- Technical Analysis
- Reinforcement Learning
- Market Regime Detection
- Financial Sentiment Analysis
- Macroeconomic Indicators
- Explainable AI

to generate transparent and explainable BUY, HOLD, and SELL signals.

Rather than replacing investors, AMORS helps them validate investment decisions using institutional-grade quantitative analysis.

---

# ✨ Key Features

## Institutional Reinforcement Learning

- Proximal Policy Optimization (PPO)
- Risk-aware reward engineering
- 500,000 training timesteps
- Continuous action space

---

## Technical Analysis Engine

More than 10 technical indicators including:

- RSI
- MACD
- EMA
- SMA
- ATR
- ADX
- Bollinger Bands
- ROC
- OBV
- Stochastic Oscillator

---

## Financial Sentiment Analysis

Uses **FinBERT** to analyze financial news collected from:

- Finnhub API
- NewsAPI

The sentiment score becomes part of the RL state representation.

---

## Market Regime Detection

A Gaussian Hidden Markov Model (HMM) classifies the market into:

- 🟢 Bull Market
- 🟡 Sideways Market
- 🔴 Bear Market

This allows the RL agent to behave differently under different market conditions.

---

## Macroeconomic Intelligence

The model also incorporates:

- USD/INR Exchange Rate
- India VIX
- US 10-Year Treasury Yield
- Sector Index Performance

to improve decision making during changing economic conditions.

---

## Explainable AI Assistant

A local AI assistant explains:

- Why BUY?
- Why SELL?
- Why HOLD?

using the underlying technical, sentiment, and regime information.

---

## GPU Acceleration

Supports CUDA acceleration for:

- Faster inference
- Faster model loading
- Parallel stock analysis

---

# 🏗️ System Architecture

```
                 React Dashboard
                        │
                        │
                FastAPI Backend
                        │
     ┌──────────────────┼─────────────────┐
     │                  │                 │
Technical Engine   Sentiment Engine   Macro Data
     │                  │                 │
     └──────────────────┼─────────────────┘
                        │
             Market Regime Detection
                 (Gaussian HMM)
                        │
                State Vector Creation
                  (24 Features)
                        │
             PPO Reinforcement Learning
                        │
               BUY / HOLD / SELL Signal
                        │
             Explainable AI Assistant
```

---

# 🔄 Methodology

## Step 1 — Data Collection

Historical stock prices are collected using:

- Yahoo Finance (yfinance)

Financial news is collected using:

- Finnhub
- NewsAPI

Macroeconomic indicators are collected from public APIs.

---

## Step 2 — Feature Engineering

Technical indicators are calculated including:

- RSI
- MACD
- EMA
- SMA
- ATR
- ADX
- ROC
- Bollinger Bands
- OBV

---

## Step 3 — Sentiment Analysis

Financial headlines are processed using FinBERT.

Each stock receives a sentiment score.

---

## Step 4 — Market Regime Detection

A Gaussian Hidden Markov Model identifies whether the market is:

- Bullish
- Sideways
- Bearish

---

## Step 5 — State Vector Construction

The following information is combined into a 24-dimensional feature vector:

- Technical indicators
- Sentiment score
- Regime score
- Macroeconomic variables
- Portfolio information

---

## Step 6 — Reinforcement Learning

The PPO agent learns an optimal trading policy using:

- Historical Nifty 50 data
- Risk-aware rewards
- Market regime penalties

Training Period:

2016 — 2023

Training Timesteps:

500,000

---

## Step 7 — Signal Generation

The trained model outputs:

- BUY
- HOLD
- SELL

based on the current market state.

---

## Step 8 — Explainability

The AI assistant provides a natural-language explanation of every prediction.

---

# 🧠 Reinforcement Learning Details

Algorithm:

- Proximal Policy Optimization (PPO)

Framework:

- Stable-Baselines3

State Space:

24 Features

Action Space:

Continuous

Training Steps:

500,000

Reward Function:

Risk-adjusted reward incorporating:

- Portfolio returns
- Drawdown penalty
- Bear market penalty
- Holding penalty
- Transaction costs

---

# 📊 Dataset

Historical Data:

- Nifty 50 Stocks

Training:

2016–2023

Validation:

2024

Testing:

2025–2026

---

# 💻 Technology Stack

## Backend

- Python
- FastAPI
- Uvicorn

---

## Frontend

- React
- TypeScript
- Vite

---

## Machine Learning

- Stable-Baselines3
- PyTorch
- Scikit-learn
- hmmlearn

---

## NLP

- FinBERT
- Transformers

---

## Data

- Pandas
- NumPy
- yfinance

---

## APIs

- Finnhub
- NewsAPI

---

## Visualization

- Matplotlib
- Plotly

---

## Local AI

- Ollama
- Phi-3
- Llama 3.2

---

## Hardware

- NVIDIA CUDA

---

# 📁 Project Structure

```
AMORS
│
├── api_server.py
├── Nifty50_RL_Trading_MultiStock.py
├── xai_bot.py
├── tune_rl_hyperparams.py
│
├── trade-signal-dashboard-main
│     ├── src
│     ├── components
│     ├── pages
│     └── api
│
├── datasets
├── models
├── docs
├── screenshots
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone <repository-url>
cd AMORS
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

---

## Activate

Windows

```powershell
.venv\Scripts\Activate.ps1
```

Linux

```bash
source .venv/bin/activate
```

---

## Install Backend

```bash
pip install -r requirements-backend.txt
```

---

## Start Backend

```bash
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

---

## Install Frontend

```bash
cd trade-signal-dashboard-main

npm install
```

---

## Start Frontend

```bash
npm run dev
```

---

# 🌐 Application URLs

Dashboard

```
http://localhost:5173
```

Backend

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

Health Check

```
http://localhost:8000/health
```

---

# 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /health | Server status |
| GET /api/analyze | Analyze one stock |
| GET /api/all-stocks | Analyze all stocks |
| GET /api/market-regime | Detect market regime |
| POST /api/chat | AI Assistant |

---

# 📈 Performance

RTX 4050 GPU

| Task | Time |
|------|------|
| Model Loading | 1–2 sec |
| Single Analysis | ~400 ms |
| AI Chat | <100 ms |
| CPU Fallback | 5–10 sec |

---

# 🚀 Future Enhancements

- Portfolio Optimization
- Live NSE Integration
- Kite Connect Trading
- Multi-Agent Reinforcement Learning
- Options Trading Support
- Risk Management Dashboard
- Cloud Deployment
- Mobile Application
- Personalized Portfolio Recommendations

---

# 👨‍💻 Contributors


- **Kothamachu  Sathvik**
-  **G. Charan Kumar**
- **G. Manish Reddy**

Department of Computer Science (AI & ML)

Dayananda Sagar University

Academic Year 2025–2026

---

# 📜 License

This project is developed for academic and research purposes.

---



# 📌 Disclaimer

This project is intended for educational and research purposes only.

The generated BUY, HOLD, and SELL recommendations should not be considered financial advice. Always perform independent research before making investment decisions.
