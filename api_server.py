"""
FastAPI Backend Server - Links Nifty50_RL_Trading_MultiStock Model with Frontend
This server wraps the existing model without any modifications to preserve accuracy.
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env.backend
load_dotenv(".env.backend")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the model components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import model configuration and utilities
import yfinance as yf
from concurrent.futures import ProcessPoolExecutor, as_completed

# ============================================================
# Configuration matching Nifty50_RL_Trading_MultiStock.py
# ============================================================
FINNHUB_API_KEY  = "d7np7rpr01qm36379ongd7np7rpr01qm36379oo0"
NEWSAPI_KEY      = "8d4a630796c94756b96a16efdf92f489"
ALPHAVANTAGE_KEY = "" # Add your Alpha Vantage key here for better sentiment

CACHE_DIR        = "cache"
MODEL_DIR        = "trained_models"
LOG_DIR          = "logs"
FORCE_RETRAIN    = False
FORCE_REFETCH    = False
CONCURRENCY      = 2

STOCK_OPTIONS = {
    "1": ("RELIANCE.NS",   "Reliance Industries",      "^CNXENERGY"),
    "2": ("TCS.NS",        "Tata Consultancy Services", "^CNXIT"),
    "3": ("HDFCBANK.NS",   "HDFC Bank",               "^NSEBANK"),
    "4": ("INFY.NS",       "Infosys",                  "^CNXIT"),
    "5": ("ICICIBANK.NS",  "ICICI Bank",              "^NSEBANK"),
    "6": ("HINDUNILVR.NS", "Hindustan Unilever",       "^CNXFMCG"),
    "7": ("ITC.NS",        "ITC Limited",              "^CNXFMCG"),
    "8": ("SBIN.NS",       "State Bank of India",     "^NSEBANK"),
    "9": ("BHARTIARTL.NS", "Bharti Airtel",            "^CNXSERVICE"),
    "10":("KOTAKBANK.NS",  "Kotak Mahindra Bank",     "^NSEBANK"),
}

TRAIN_START = "2016-01-01"
TRAIN_END   = "2023-12-31"
VAL_START   = "2024-01-01"
VAL_END     = "2024-12-31"
TEST_START  = "2025-01-01"
TEST_END    = datetime.now().strftime("%Y-%m-%d")
FULL_START  = TRAIN_START
FULL_END    = TEST_END

TRANSACTION_COST = 0.001
MAX_SHARES       = 100
DUMMY_CAPITAL    = 1000000
SEED             = 42

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================
# Import model functions from Nifty50_RL_Trading_MultiStock
# ============================================================
from Nifty50_RL_Trading_MultiStock import (
    process_stock,
    compute_regime,
)

from xai_bot import get_bot

# ============================================================
# Pydantic Response Models
# ============================================================
class ChatRequest(BaseModel):
    message: str
    ticker: Optional[str] = None
    analysis_context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str

class Indicator(BaseModel):
    name: str
    value: float
    status: str

class Headline(BaseModel):
    text: str
    sentiment: str
    source: Optional[str] = None

class SentimentChart(BaseModel):
    dates: List[str]
    scores: List[float]

class NiftyPoint(BaseModel):
    date: str
    value: float
    regime: str

class MarketRegime(BaseModel):
    bull_pct: float
    sideways_pct: float
    bear_pct: float
    nifty_data: List[NiftyPoint]

class BacktestMetrics(BaseModel):
    sharpe: float
    sortino: float
    cum_ret: float
    ann_ret: float
    max_dd: float
    win_rate: float
    buy_precision: float
    sell_precision: float
    period: str

class Analysis(BaseModel):
    ticker: str
    name: str
    signal: str
    action_value: float
    technical_score: float
    sentiment_score: float
    regime_score: float
    indicators: List[Indicator]
    sentiment_chart: SentimentChart
    headlines: List[Headline]
    market_regime: MarketRegime
    backtest: BacktestMetrics

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    available_stocks: List[str]
    timestamp: str

# ============================================================
# FastAPI Application
# ============================================================
app = FastAPI(
    title="Nifty 50 RL Trading Model API",
    description="PPO-based stock trading recommendation system",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for market regime computation
_regime_cache = None
_regime_timestamp = None

def get_market_regime():
    """Compute or retrieve cached market regime"""
    global _regime_cache, _regime_timestamp
    
    current_time = datetime.now()
    
    # Use cache if available and less than 1 hour old
    if _regime_cache is not None and _regime_timestamp is not None:
        time_diff = (current_time - _regime_timestamp).total_seconds()
        if time_diff < 3600:
            return _regime_cache
    
    try:
        logger.info("Computing market regime and fetching macros...")
        n_idx, macro_df, b_p, br_p, s_p = compute_regime()
        
        _regime_cache = {
            'nifty_data': n_idx,
            'macro_df': macro_df,
            'bull_pct': b_p,
            'bear_pct': br_p,
            'sideways_pct': s_p
        }
        _regime_timestamp = current_time
        
        return _regime_cache
    except Exception as e:
        logger.error(f"Error computing regime: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compute market regime: {str(e)}")

# ============================================================
# API Endpoints
# ============================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    stocks = [f"{tick} - {name}" for _, (tick, name, _) in STOCK_OPTIONS.items()]
    return HealthResponse(
        status="healthy",
        model_loaded=True,
        available_stocks=stocks,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/analyze", response_model=Analysis)
async def analyze(ticker: str = Query(..., description="Stock ticker symbol (e.g., RELIANCE.NS)")):
    """
    Analyze a stock using the trained PPO model
    
    Returns comprehensive analysis including:
    - Trading signal (BUY/SELL/HOLD)
    - Technical indicators and scores
    - Sentiment analysis from headlines
    - Market regime detection
    - Backtest performance metrics
    """
    try:
        ticker = ticker.upper().strip()
        
        # Validate ticker
        valid_tickers = [tick for _, (tick, _, _) in STOCK_OPTIONS.items()]
        if ticker not in valid_tickers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid ticker. Available: {', '.join(valid_tickers)}"
            )
        
        # Get stock name
        stock_name = next(
            (name for _, (tick, name, _) in STOCK_OPTIONS.items() if tick == ticker),
            ticker
        )
        
        logger.info(f"Processing analysis for {ticker}...")
        
        # Get market regime
        regime_data = get_market_regime()
        
        # Get sector ticker
        sector_ticker = next(
            (sect for _, (tick, _, sect) in STOCK_OPTIONS.items() if tick == ticker),
            "^CNXIT" # Fallback
        )
        
        # Process the stock using the original model
        result = process_stock(
            ticker=ticker,
            name=stock_name,
            sector_ticker=sector_ticker,
            macro_df=regime_data['macro_df'],
            bull_pct=regime_data['bull_pct'],
            bear_pct=regime_data['bear_pct'],
            sideways_pct=regime_data['sideways_pct']
        )
        
        if result is None:
            raise HTTPException(status_code=500, detail=f"Failed to process {ticker}")
        
        # Transform result to match frontend schema
        analysis = _transform_model_output(result, regime_data)
        
        logger.info(f"Analysis complete for {ticker}")
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/all-stocks")
async def analyze_all():
    """Analyze all stocks in parallel and return results"""
    try:
        logger.info("Analyzing all stocks...")
        
        regime_data = get_market_regime()
        results = {}
        
        with ProcessPoolExecutor(max_workers=CONCURRENCY) as executor:
            futures = {
                executor.submit(
                    process_stock,
                    tick, name,
                    next((s for _, (t, _, s) in STOCK_OPTIONS.items() if t == tick), "^CNXIT"),
                    regime_data['macro_df'],
                    regime_data['bull_pct'],
                    regime_data['bear_pct'],
                    regime_data['sideways_pct']
                ): (tick, name)
                for _, (tick, name, _) in STOCK_OPTIONS.items()
                }
            
            for future in as_completed(futures):
                tick, name = futures[future]
                try:
                    result = future.result()
                    if result:
                        results[tick] = _transform_model_output(result, regime_data)
                except Exception as e:
                    logger.error(f"Error processing {tick}: {e}")
                    results[tick] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        logger.error(f"Error in analyze_all: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-regime")
async def market_regime():
    """Get current market regime data"""
    try:
        regime_data = get_market_regime()
        
        nifty_points = []
        for _, row in regime_data['nifty_data'].iterrows():
            regime_map = {2: "Bullish", 0: "Bearish", 1: "Sideways"}
            nifty_points.append({
                "date": row['date'].strftime("%Y-%m-%d"),
                "value": float(row['close']),
                "regime": regime_map.get(row.get('regime_score', 1), "Sideways")
            })
        
        return {
            "bull_pct": float(regime_data['bull_pct']),
            "sideways_pct": float(regime_data['sideways_pct']),
            "bear_pct": float(regime_data['bear_pct']),
            "nifty_data": nifty_points
        }
    except Exception as e:
        logger.error(f"Error getting market regime: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks")
async def get_stocks():
    """Get list of available stocks"""
    stocks = [
        {"id": idx, "ticker": tick, "name": name}
        for idx, (tick, name, _) in STOCK_OPTIONS.items()
    ]
    return stocks

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the Support & XAI Bot
    """
    bot = get_bot()
    if not bot:
        raise HTTPException(status_code=503, detail="Support bot is not configured (missing API key)")
    
    try:
        response_text = await bot.get_response(
            message=request.message,
            ticker=request.ticker,
            analysis_context=request.analysis_context
        )
        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Helper Functions
# ============================================================

def _transform_model_output(result: Dict[str, Any], regime_data: Dict) -> Analysis:
    """
    Transform raw model output to match frontend schema
    No modification to model accuracy - just reformatting
    """
    try:
        # Extract values safely
        signal = result.get('FINAL SIGNAL', 'HOLD')
        ticker = result.get('Ticker', 'UNKNOWN')
        name = result.get('Name', 'Unknown')
        
        # Parse metrics
        def parse_float(val):
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str):
                return float(val.replace('%', '').strip())
            return 0.0
        
        sharpe = parse_float(result.get('Sharpe Ratio', 0))
        sortino = parse_float(result.get('Sortino Ratio', 0))
        cum_ret = parse_float(result.get('Cumulative Return', 0)) / 100
        ann_ret = parse_float(result.get('Annualised Return', 0)) / 100
        max_dd = parse_float(result.get('Max Drawdown', 0)) / 100
        win_rate = parse_float(result.get('Win Rate', 0)) / 100
        buy_prec = parse_float(result.get('Buy Precision', 0)) / 100
        sell_prec = parse_float(result.get('Sell Precision', 0)) / 100
        
        # Signal mapping
        signal_value = 1.0 if signal == 'BUY' else -1.0 if signal == 'SELL' else 0.0
        
        # Build indicators
        indicators = [
            Indicator(name="Sharpe Ratio", value=sharpe, status="Good" if sharpe > 1 else "OK"),
            Indicator(name="Sortino Ratio", value=sortino, status="Strong" if sortino > 1.5 else "Good"),
            Indicator(name="Win Rate", value=win_rate * 100, status="Strong" if win_rate > 0.55 else "Good"),
            Indicator(name="Buy Precision", value=buy_prec * 100, status="Strong" if buy_prec > 0.60 else "Good"),
            Indicator(name="Sell Precision", value=sell_prec * 100, status="Strong" if sell_prec > 0.60 else "Good"),
        ]
        
        # Headlines (from model result)
        headlines = []
        if 'Headlines' in result and result['Headlines']:
            for h in result['Headlines'][:5]:
                h_text = h.get('text', '') if isinstance(h, dict) else h
                h_score = h.get('score', 0) if isinstance(h, dict) else 0
                sent_label = "pos" if h_score > 0.1 else "neg" if h_score < -0.1 else "neu"
                headlines.append(Headline(text=h_text, sentiment=sent_label))
        
        # Sentiment chart
        raw_hist = result.get('Sentiment History', [])
        sentiment_chart = SentimentChart(
            dates=[item['date'] for item in raw_hist] if raw_hist else [datetime.now().strftime("%Y-%m-%d")],
            scores=[item['score'] for item in raw_hist] if raw_hist else [0.0]
        )
        
        # Market regime
        regime_obj = MarketRegime(
            bull_pct=regime_data['bull_pct'],
            sideways_pct=regime_data['sideways_pct'],
            bear_pct=regime_data['bear_pct'],
            nifty_data=[]
        )
        
        # Backtest metrics
        backtest = BacktestMetrics(
            sharpe=sharpe,
            sortino=sortino,
            cum_ret=cum_ret,
            ann_ret=ann_ret,
            max_dd=max_dd,
            win_rate=win_rate,
            buy_precision=buy_prec,
            sell_precision=sell_prec,
            period="2025-01-01 to Present"
        )
        
        # Calculate scores (0-100 scale)
        # Use institutional Technical Strength (current setup) weighted with model performance
        setup_score = float(result.get('Technical Strength', 50))
        performance_score = (win_rate * 50 + (min(max(0, sharpe), 3) / 3) * 50)
        
        technical_score = setup_score * 0.7 + performance_score * 0.3
        
        sentiment_val = result.get('Sentiment Score', 0.0)
        sentiment_score = (sentiment_val + 1) * 50  # Map -1..1 to 0..100
        regime_score = regime_data['bull_pct'] if signal_value > 0 else regime_data['bear_pct']
        
        return Analysis(
            ticker=ticker,
            name=name,
            signal=signal,
            action_value=signal_value,
            technical_score=technical_score,
            sentiment_score=sentiment_score,
            regime_score=regime_score,
            indicators=indicators,
            sentiment_chart=sentiment_chart,
            headlines=headlines,
            market_regime=regime_obj,
            backtest=backtest
        )
    
    except Exception as e:
        logger.error(f"Error transforming output: {str(e)}", exc_info=True)
        raise

# ============================================================
# Startup/Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 API Server Starting...")
    
    # Initialize Local Bot (Ollama)
    try:
        logger.info("🤖 Mode: Strict Local (Ollama)")
        bot = get_bot()
        
        # Check if Ollama is actually reachable
        is_up = await bot.check_connection()
        if is_up:
            logger.info("✅ Local Ollama Bot Ready.")
        else:
            logger.warning("⚠️ Local Ollama is NOT running on http://localhost:11434")
            logger.warning("⚠️ Chat features will be unavailable until 'ollama serve' is run.")
            
    except Exception as e:
        logger.warning(f"🤖 Support Bot: Failed to initialize ({e})")
        
    logger.info(f"📊 Available stocks: {len(STOCK_OPTIONS)}")
    logger.info(f"💾 Cache directory: {CACHE_DIR}")
    logger.info(f"🤖 Model directory: {MODEL_DIR}")
    logger.info("🚀 API Server Ready!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 API Server Shutting Down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
