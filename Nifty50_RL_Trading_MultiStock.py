# %% [markdown]
# # 📈 Nifty 50 Stock Trading Recommendation System (Multi-Stock Optimized)
# ## Deep Reinforcement Learning (PPO) + Technical Analysis + Sentiment Analysis + Market Regime
# 
# **Framework:** Custom PPO (Proximal Policy Optimization) via Stable-Baselines3  
# **Market:** Indian Stock Market (NSE — Yahoo Finance .NS suffix)  
# **Optimization:** Local Caching (Data/Models) + Parallel Execution
# 
# ### Pipeline:
# 1. Download OHLCV data & detect global Market Regime.
# 2. For each stock (Parallelized):
#    - Fetch news/sentiment or load from cache.
#    - Compute technical indicators or load feature-engineered data from cache.
#    - Load pre-trained PPO model from disk OR train/save if missing.
#    - Run backtest and generate recommendation.
# 3. Output consolidated results for all 10 stocks.

# %%
# ============================================================
# CELL 1: INSTALL & IMPORTS
# ============================================================
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta
import os
import requests
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import yfinance as yf
import ta
from ta.trend import MACD, SMAIndicator, EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, ROCIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from hmmlearn import hmm

import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from sklearn.preprocessing import StandardScaler

# Device configuration for GPU acceleration (GPU-First with CPU Fallback)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"✅ Imports successful! Active Device: {DEVICE}")

# %%
# ============================================================
# CELL 2: CONFIGURATION
# ============================================================
FINNHUB_API_KEY  = "d7np7rpr01qm36379ongd7np7rpr01qm36379oo0"
NEWSAPI_KEY      = "8d4a630796c94756b96a16efdf92f489"
ALPHAVANTAGE_KEY = "9FWL9ZCWVHMODYSL" # Add your Alpha Vantage key here for better sentiment

# ---- PERSISTENCE SETTINGS ----
CACHE_DIR        = "cache"
MODEL_DIR        = "trained_models"
LOG_DIR          = "logs"
FORCE_RETRAIN    = False  # Set to True to ignore saved models and apply new reward function
FORCE_REFETCH    = False  # Set to True to ignore cached data/sentiment and include VIX
CONCURRENCY      = 2      # Number of stocks to process at once (GPU dependent)

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

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
TEST_END    = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
FULL_START  = TRAIN_START
FULL_END    = TEST_END

TRANSACTION_COST = 0.001
MAX_SHARES       = 100
DUMMY_CAPITAL    = 1000000
TOTAL_TIMESTEPS  = 500000
LEARNING_RATE    = 0.0001
N_STEPS          = 1024
BATCH_SIZE       = 128
N_EPOCHS         = 15
GAMMA            = 0.995
GAE_LAMBDA       = 0.95
CLIP_RANGE       = 0.15
ENT_COEF         = 0.005
VF_COEF          = 0.5
MAX_GRAD_NORM    = 0.5

RSI_WINDOW, MACD_FAST, MACD_SLOW, MACD_SIGNAL, BB_WINDOW, SMA_SHORT, SMA_LONG, ATR_WINDOW, ADX_WINDOW, ROC_WINDOW = 14, 12, 26, 9, 20, 10, 50, 14, 14, 10
N_REGIMES, REGIME_LOOKBACK, SEED = 3, 60, 42
np.random.seed(SEED)

FEATURE_COLS = [
    'close_norm', 'daily_return', 'log_return', 'volatility_10',
    'macd', 'macd_signal', 'macd_hist', 'sma_10', 'sma_50', 'ema_20',
    'rsi', 'stoch_k', 'stoch_d', 'roc', 'bb_pct', 'bb_width', 'atr',
    'obv', 'adx', 'sentiment_score', 'regime_score', 'tech_strength_score',
    'vix', 'usd_inr', 'us_10y_yield', 'sector_return'
]

# %%
# ============================================================
# CELL 3: DATA ENGINE
# ============================================================
# FinBERT Integration (ProsusAI/finbert)
# Pre-trained on financial text for significantly higher accuracy
finbert_name = "ProsusAI/finbert"
vader_analyzer = SentimentIntensityAnalyzer()
USE_FINBERT = False

try:
    print(f"🔄 Loading FinBERT model ({finbert_name})...")
    tokenizer = BertTokenizer.from_pretrained(finbert_name)
    finbert_model = BertForSequenceClassification.from_pretrained(finbert_name)
    finbert_model.to(DEVICE)
    finbert_model.eval()
    USE_FINBERT = True
    print(f"✅ FinBERT loaded successfully on {DEVICE}!")
except Exception as e:
    print(f"⚠️ Warning: Could not load FinBERT ({e}). Falling back to VADER.")
    print("💡 Tip: Ensure internet connection for the first run or download model manually.")

def score_text(text):
    if not text or not isinstance(text, str): return 0.0
    try:
        if USE_FINBERT:
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = finbert_model(**inputs)
            
            # FinBERT labels: 0: positive, 1: negative, 2: neutral
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            # Calculate a compound score: positive - negative
            score = probs[0][0].item() - probs[0][1].item()
            return score
        else:
            # VADER Fallback
            vs = vader_analyzer.polarity_scores(text)
            return vs['compound']
    except Exception as e:
        print(f"Error scoring text: {e}")
        return 0.0

def fetch_finnhub_sentiment(symbol, api_key, days=365):
    end_dt, start_dt = datetime.now(), datetime.now() - timedelta(days=days)
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={start_dt.strftime('%Y-%m-%d')}&to={end_dt.strftime('%Y-%m-%d')}&token={api_key}"
    headlines_top = []
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            news = r.json()
            if isinstance(news, list) and len(news) > 0:
                records = []
                for item in news:
                    headline = item.get('headline', '')
                    score = score_text(headline)
                    if headline and len(headlines_top) < 5 and not any(h[0] == headline for h in headlines_top):
                        headlines_top.append((headline, score))
                    if score is not None:
                        dt = pd.to_datetime(item.get('datetime', 0), unit='s')
                        records.append({'date': dt.date(), 'sentiment_score': score})
                if records:
                    df = pd.DataFrame(records)
                    df['date'] = pd.to_datetime(df['date'])
                    return df.groupby('date')['sentiment_score'].mean().reset_index(), headlines_top
    except: pass
    return pd.DataFrame(), headlines_top

def fetch_newsapi_sentiment(query, api_key, days=29):
    cutoff, headlines_top = datetime.now() - timedelta(days=days), []
    url = f"https://newsapi.org/v2/everything?q={query}&from={cutoff.strftime('%Y-%m-%d')}&sortBy=popularity&language=en&apiKey={api_key}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            if articles:
                records = []
                for item in articles:
                    dt_str = item.get('publishedAt', '')[:10]
                    if not dt_str: continue
                    dt = datetime.strptime(dt_str, '%Y-%m-%d')
                    headline = item.get('title', '')
                    score = score_text(headline) or score_text(item.get('description', '')) or 0
                    if headline and len(headlines_top) < 5 and not any(h[0] == headline for h in headlines_top):
                        headlines_top.append((headline, score))
                    records.append({'date': dt, 'sentiment_score': score})
                if records:
                    df = pd.DataFrame(records)
                    df['date'] = pd.to_datetime(df['date'])
                    return df.groupby('date')['sentiment_score'].mean().reset_index(), headlines_top
    except: pass
    return pd.DataFrame(), headlines_top

def fetch_alphavantage_sentiment(ticker_base, api_key, days=30):
    """Fetches high-quality financial news sentiment from Alpha Vantage."""
    if not api_key: return pd.DataFrame(), []
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker_base}&apikey={api_key}"
    headlines_top = []
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            feed = data.get('feed', [])
            if feed:
                records = []
                for item in feed:
                    headline = item.get('title', '')
                    score = score_text(headline)
                    if headline and len(headlines_top) < 5 and not any(h[0] == headline for h in headlines_top):
                        headlines_top.append((headline, score))
                    
                    dt_str = item.get('time_published', '')[:8]
                    if dt_str:
                        dt = datetime.strptime(dt_str, '%Y%m%d')
                        records.append({'date': dt, 'sentiment_score': score})
                
                if records:
                    df = pd.DataFrame(records)
                    df['date'] = pd.to_datetime(df['date'])
                    return df.groupby('date')['sentiment_score'].mean().reset_index(), headlines_top
    except: pass
    return pd.DataFrame(), headlines_top

def build_sentiment_column(stock_df, ticker, finnhub_key, newsapi_key, av_key=""):
    cache_path = os.path.join(CACHE_DIR, f"sentiment_{ticker}.csv")
    cached_df = None
    if not FORCE_REFETCH and os.path.exists(cache_path):
        cached_df = pd.read_csv(cache_path, parse_dates=['date'])
    
    ticker_base = ticker.replace('.NS', '')
    fh_df, fh_head = fetch_finnhub_sentiment("BSE:" + ticker_base, finnhub_key)
    news_df, news_head = fetch_newsapi_sentiment(ticker_base, newsapi_key)
    av_df, av_head = fetch_alphavantage_sentiment(ticker_base, av_key)
    
    # Merge headlines carefully
    combined_head = fh_head + news_head + av_head
    seen = set()
    top_headlines = []
    for h, s in combined_head:
        if h not in seen:
            top_headlines.append({'text': h, 'score': s})
            seen.add(h)
    top_headlines = top_headlines[:5]
    
    if cached_df is not None:
        return stock_df.merge(cached_df, on='date', how='left').fillna(0), top_headlines
    
    parts = [p for p in [fh_df, news_df, av_df] if not p.empty]
    if parts:
        combined = pd.concat(parts).groupby('date')['sentiment_score'].mean().reset_index()
        combined['date'] = pd.to_datetime(combined['date'])
        combined.to_csv(cache_path, index=False)
        result = stock_df.merge(combined, on='date', how='left')
    else:
        result = stock_df.copy()
        result['sentiment_score'] = 0.0
    
    result['sentiment_score'] = result['sentiment_score'].fillna(0.0)
    
    # Add Sentiment Momentum (Rolling Averages)
    # This helps the RL model distinguish between noise and a sustained change in sentiment
    result['sentiment_7d_avg'] = result['sentiment_score'].rolling(window=7, min_periods=1).mean()
    result['sentiment_30d_avg'] = result['sentiment_score'].rolling(window=30, min_periods=1).mean()
    
    return result, top_headlines

def add_technical_indicators(df):
    df = df.copy().sort_values('date')
    close, high, low, volume = df['close'], df['high'], df['low'], df['volume']
    df['rsi'] = RSIIndicator(close=close, window=RSI_WINDOW).rsi()
    macd_ind = MACD(close=close, window_fast=MACD_FAST, window_slow=MACD_SLOW, window_sign=MACD_SIGNAL)
    df['macd'], df['macd_signal'], df['macd_hist'] = macd_ind.macd(), macd_ind.macd_signal(), macd_ind.macd_diff()
    bb = BollingerBands(close=close, window=BB_WINDOW)
    df['bb_pct'], df['bb_width'] = bb.bollinger_pband(), bb.bollinger_wband()
    df['sma_10'], df['sma_50'] = SMAIndicator(close=close, window=SMA_SHORT).sma_indicator(), SMAIndicator(close=close, window=SMA_LONG).sma_indicator()
    df['ema_20'], df['atr'] = EMAIndicator(close=close, window=20).ema_indicator(), AverageTrueRange(high=high, low=low, close=close, window=ATR_WINDOW).average_true_range()
    df['obv'], df['adx'] = OnBalanceVolumeIndicator(close=close, volume=volume).on_balance_volume(), ADXIndicator(high=high, low=low, close=close, window=ADX_WINDOW).adx()
    stoch = StochasticOscillator(high=high, low=low, close=close)
    df['stoch_k'], df['stoch_d'], df['roc'] = stoch.stoch(), stoch.stoch_signal(), ROCIndicator(close=close, window=ROC_WINDOW).roc()
    df['daily_return'], df['log_return'] = close.pct_change(), np.log(close / close.shift(1))
    df['volatility_10'], df['close_norm'] = df['daily_return'].rolling(10).std(), (close - close.rolling(50).mean()) / (close.rolling(50).std() + 1e-8)
    return df

def compute_technical_strength_score(df):
    df = df.copy()
    signals = pd.DataFrame(index=df.index)
    signals['rsi_sig'] = df['rsi'].clip(0, 100) / 100
    macd_h = df['macd_hist']
    signals['macd_sig'] = ((macd_h - macd_h.min()) / (macd_h.max() - macd_h.min() + 1e-8)).clip(0, 1)
    signals['bb_sig'] = df['bb_pct'].clip(0, 1)
    signals['sma_cross_sig'] = (df['close'] > df['sma_50']).astype(float)
    signals['ema_sig'] = (df['close'] > df['ema_20']).astype(float)
    signals['adx_sig'] = ((df['adx'] - 10) / 40).clip(0, 1)
    signals['stoch_sig'] = df['stoch_k'].clip(0, 100) / 100
    roc = df['roc']
    signals['roc_sig'] = ((roc - roc.min()) / (roc.max() - roc.min() + 1e-8)).clip(0, 1)
    obv_ma = df['obv'].rolling(20).mean()
    signals['obv_sig'] = (df['obv'] > obv_ma).astype(float)
    atr_norm = (df['atr'] / (df['close'] + 1e-8))
    signals['atr_sig'] = (1 - atr_norm.clip(0, 0.1) / 0.1).clip(0, 1)
    df['tech_strength_score'] = signals.mean(axis=1) * 100
    return df

# %%
# ============================================================
# CELL 4: RL ENVIRONMENT
# ============================================================
class NiftyRecommendationEnv(gym.Env):
    def __init__(self, df, feature_cols):
        super().__init__()
        self.df, self.feature_cols = df.reset_index(drop=True), feature_cols
        self.dates = sorted(df['date'].unique())
        self.n_days = len(self.dates)
        self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-10, high=10, shape=(1 + len(feature_cols) + 1,), dtype=np.float32)
        self.reset()
    def _obs(self):
        if self.current_step >= len(self.df): return np.zeros(self.observation_space.shape, dtype=np.float32)
        row = self.df.iloc[self.current_step]
        return np.nan_to_num(np.concatenate([[self.position], row[self.feature_cols].values, [row['close_norm']]]), nan=0.0).astype(np.float32)
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.balance = float(DUMMY_CAPITAL)
        self.shares_held = 0
        self.position = 0.0
        self.portfolio_hist = [DUMMY_CAPITAL]
        self.returns_hist = []
        self.actions_hist = []  # Track raw scalar actions
        return self._obs(), {}
    def step(self, action):
        row, action_scalar = self.df.iloc[self.current_step], float(action[0])
        self.actions_hist.append(action_scalar)
        price = float(row['close'])
        
        # Action execution
        if action_scalar > 0.3:
            n = min(int((self.balance * 0.3) / (price * (1+TRANSACTION_COST))), MAX_SHARES)
            if n > 0: 
                self.balance -= n*price*(1+TRANSACTION_COST)
                self.shares_held += n
                self.position = min(1.0, self.position+0.3)
        elif action_scalar < -0.3:
            n = min(self.shares_held, max(1, int(self.shares_held * 0.5)))
            if n > 0: 
                self.balance += n*price*(1-TRANSACTION_COST)
                self.shares_held -= n
                self.position = max(-1.0, self.position-0.3)
        
        self.current_step += 1
        done = self.current_step >= self.n_days - 1
        val = self.balance + self.shares_held * (float(self.df.iloc[self.current_step]['close']) if not done else price)
        ret = (val - self.portfolio_hist[-1]) / (self.portfolio_hist[-1] + 1e-8)
        self.portfolio_hist.append(val)
        self.returns_hist.append(ret)
        
        # Base Reward: Scale returns
        reward = ret * 100
        
        # Risk-Adjusted Reward (Sharpe-like and Drawdown Penalty)
        if len(self.returns_hist) >= 20:
            ra = np.array(self.returns_hist[-20:])
            # Sharpe component
            sharpe_comp = (ra.mean() / (ra.std() + 1e-8)) * 10
            # Drawdown component
            max_val = max(self.portfolio_hist)
            dd_comp = -max(0, (max_val - val) / (max_val + 1e-8)) * 5
            reward = sharpe_comp + dd_comp
            
        # --- NEW OPTIMIZED PENALTIES ---
        # These features are standardized (StandardScaler), so we check against Z-scores
        
        # 1. Bear Regime Penalty: Heavily penalize holding trades during bearish market regimes
        # If regime_score is low (standardized), it indicates a Bear regime
        if self.shares_held > 0 and row['regime_score'] < -0.8:
            reward -= 0.5  # Fixed penalty for risk exposure in bear market
            
        # 2. High Volatility Penalty: Penalize BUY actions during high market uncertainty (VIX proxy)
        # If volatility_10 is high (standardized), it indicates high risk
        if action_scalar > 0.3 and row['volatility_10'] > 1.0:
            reward -= 0.3 * abs(row['volatility_10']) # Scale penalty with volatility intensity
            
        return self._obs(), float(reward), done, False, {}

# %%
# ============================================================
# CELL 5: CORE PIPELINE RUNNER
# ============================================================
def process_stock(ticker, name, sector_ticker, macro_df, bull_pct, bear_pct, sideways_pct):
    try:
        print(f"🚀 Processing {name} ({ticker}) [Sector: {sector_ticker}]...")
        cache_feat = os.path.join(CACHE_DIR, f"features_{ticker}.csv")
        
        if not FORCE_REFETCH and os.path.exists(cache_feat):
            df = pd.read_csv(cache_feat, parse_dates=['date'])
            # Still fetch latest headlines for the UI
            _, tops = build_sentiment_column(df[['date']].copy(), ticker, FINNHUB_API_KEY, NEWSAPI_KEY, ALPHAVANTAGE_KEY)
        else:
            df = yf.download(ticker, start=FULL_START, end=FULL_END, progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            if 'date' not in df.columns and 'index' in df.columns:
                df.rename(columns={'index':'date'}, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            
            # Fetch Sector Data
            s_df = yf.download(sector_ticker, start=FULL_START, end=FULL_END, progress=False, auto_adjust=True)
            if isinstance(s_df.columns, pd.MultiIndex):
                s_df.columns = s_df.columns.get_level_values(0)
            s_df = s_df.reset_index()
            s_df.columns = [str(c).lower().strip() for c in s_df.columns]
            s_df['sector_return'] = s_df['close'].pct_change()
            s_df = s_df[['date', 'sector_return']]
            s_df['date'] = pd.to_datetime(s_df['date'])
            
            df = add_technical_indicators(df)
            df = compute_technical_strength_score(df)
            
            # Merge Macro & Sector
            df = df.merge(macro_df, on='date', how='left').ffill()
            df = df.merge(s_df, on='date', how='left').ffill().fillna(0)
            
            df, tops = build_sentiment_column(df, ticker, FINNHUB_API_KEY, NEWSAPI_KEY, ALPHAVANTAGE_KEY)
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df[FEATURE_COLS] = df[FEATURE_COLS].ffill().bfill().fillna(0)
            df.to_csv(cache_feat, index=False)

        # Scale for RL
        df_rl = df.copy()
        scaler = StandardScaler()
        df_rl[FEATURE_COLS] = scaler.fit_transform(df_rl[FEATURE_COLS])
        train_data = df_rl[(df_rl['date'] >= TRAIN_START) & (df_rl['date'] <= TRAIN_END)].copy()
        test_data = df_rl[(df_rl['date'] >= TEST_START) & (df_rl['date'] <= TEST_END)].copy()

        env = DummyVecEnv([lambda: Monitor(NiftyRecommendationEnv(train_data, FEATURE_COLS))])
        mod_path = os.path.join(MODEL_DIR, f"PPO_{ticker}")
        
        # Hyperparameters
        lr, ns, bs, ne, gam, gael, cr, ec = LEARNING_RATE, N_STEPS, BATCH_SIZE, N_EPOCHS, GAMMA, GAE_LAMBDA, CLIP_RANGE, ENT_COEF
        if os.path.exists("best_hyperparams.json"):
            try:
                import json
                with open("best_hyperparams.json", "r") as f:
                    hp = json.load(f)
                    lr = hp.get("learning_rate", lr)
                    ns = hp.get("n_steps", ns)
                    bs = hp.get("batch_size", bs)
                    ne = hp.get("n_epochs", ne)
                    gam = hp.get("gamma", gam)
                    gael = hp.get("gae_lambda", gael)
                    cr = hp.get("clip_range", cr)
                    ec = hp.get("ent_coef", ec)
                    print(f"✨ Using optimized hyperparameters for {ticker}!")
            except: pass

        # Robust loading for .zip or no-extension legacy files
        if not FORCE_RETRAIN and (os.path.exists(mod_path + ".zip") or os.path.exists(mod_path)):
            load_path = mod_path + ".zip" if os.path.exists(mod_path + ".zip") else mod_path
            print(f"📂 Loading existing trained model for {ticker} from {load_path}...")
            ppo = PPO.load(load_path, env=env, device=DEVICE)
        else:
            ppo = PPO("MlpPolicy", env, learning_rate=lr, n_steps=ns, batch_size=bs, n_epochs=ne, gamma=gam, gae_lambda=gael, clip_range=cr, ent_coef=ec, vf_coef=VF_COEF, max_grad_norm=MAX_GRAD_NORM, verbose=0, seed=SEED, device=DEVICE)
            print(f"🤖 Training PPO for {ticker} on {DEVICE}...")
            ppo.learn(total_timesteps=TOTAL_TIMESTEPS); ppo.save(mod_path)
            print(f"✅ Saved model to {mod_path}.zip")

        # Eval
        tenv = NiftyRecommendationEnv(test_data, FEATURE_COLS)
        obs, _ = tenv.reset(); done = False; last_a = 0
        while not done:
            a, _ = ppo.predict(obs, deterministic=True); obs, _, done, _, _ = tenv.step(a); last_a = float(a[0])
        
        v = np.array(tenv.portfolio_hist); r = np.array(tenv.returns_hist); acts = np.array(tenv.actions_hist)
        cum_ret = (v[-1]/v[0]-1)
        # Annualized Return
        days = len(r)
        ann_ret = (1 + cum_ret)**(252/days) - 1 if days > 0 else 0
        # Sharpe
        sharpe = (r.mean()/(r.std()+1e-8))*np.sqrt(252) if len(r)>0 else 0
        # Sortino
        neg_r = r[r < 0]
        sortino = (r.mean()/(neg_r.std()+1e-8))*np.sqrt(252) if len(neg_r)>0 else 0
        # Max Drawdown
        peaks = np.maximum.accumulate(v)
        drawdowns = (peaks - v) / peaks
        max_dd = np.max(drawdowns)
        # Calmar
        calmar = ann_ret / max_dd if max_dd > 0 else 0
        # Win Rate
        win_rate = np.sum(r > 0) / len(r) if len(r) > 0 else 0
        # Buy/Sell Precision
        buys = acts > 0.3
        sells = acts < -0.3
        # Direct alignment: r[i] is the return resulting from acts[i]
        buy_prec = np.sum(r[buys] > 0) / np.sum(buys) if np.sum(buys) > 0 else 0
        sell_prec = np.sum(r[sells] < 0) / np.sum(sells) if np.sum(sells) > 0 else 0
        
        s_m = {'BUY':1,'HOLD':0,'SELL':-1,'NEUTRAL':0}
        p_s = 'BUY' if last_a > 0.3 else 'SELL' if last_a < -0.3 else 'HOLD'
        t_s = 'BUY' if df['tech_strength_score'].iloc[-1] >= 65 else 'SELL' if df['tech_strength_score'].iloc[-1] <= 35 else 'HOLD'
        sent_v = df['sentiment_score'].iloc[-1]
        sn_s = 'BUY' if sent_v > 0.1 else 'SELL' if sent_v < -0.1 else 'NEUTRAL' if abs(sent_v) < 0.05 else 'HOLD'
        dom = 'Bull' if bull_pct > max(bear_pct, sideways_pct) else 'Bear' if bear_pct > max(bull_pct, sideways_pct) else 'Sideways'
        rg_s = 'BUY' if dom == 'Bull' else 'SELL' if dom == 'Bear' else 'HOLD'
        w = s_m[p_s]*0.5 + s_m[t_s]*0.25 + s_m[sn_s]*0.15 + s_m[rg_s]*0.10
        f_s = 'BUY' if w > 0.15 else 'SELL' if w < -0.15 else 'HOLD'
        
        # Sentiment history for chart
        sent_hist = df[['date', 'sentiment_score']].tail(30).to_dict('records')
        sent_hist = [{'date': d['date'].strftime('%Y-%m-%d'), 'score': d['sentiment_score']} for d in sent_hist]

        return {
            'Ticker': ticker, 'Name': name, 'FINAL SIGNAL': f_s, 
            'action_value': float(last_a),
            'Technical Strength': float(df['tech_strength_score'].iloc[-1]),
            'Sharpe Ratio': f"{sharpe:.2f}",
            'Sortino Ratio': f"{sortino:.2f}",
            'Calmar Ratio': f"{calmar:.2f}",
            'Max Drawdown': f"{max_dd*100:.2f}%",
            'Win Rate': f"{win_rate*100:.1f}%",
            'Buy Precision': f"{buy_prec*100:.1f}%",
            'Sell Precision': f"{sell_prec*100:.1f}%",
            'Cumulative Return': f"{cum_ret*100:.2f}%",
            'Annualised Return': f"{ann_ret*100:.2f}%",
            'Sentiment Score': sent_v,
            'Sentiment History': sent_hist,
            'Headlines': tops
        }
    except Exception as e:
        print(f"❌ Error in {ticker}: {e}"); return None

# %%
# ============================================================
# CELL 6: COMPUTE REGIME (EXPORTABLE FOR API)
# ============================================================
def compute_regime():
    """
    Compute market regime and fetch global macro data
    Returns: (nifty_data, macro_df, bull_pct, bear_pct, sideways_pct)
    """
    # Download NSE Index
    n_idx = yf.download("^NSEI", start=FULL_START, end=FULL_END, progress=False, auto_adjust=True)
    if isinstance(n_idx.columns, pd.MultiIndex):
        n_idx.columns = n_idx.columns.get_level_values(0)
    n_idx = n_idx.reset_index()
    n_idx.columns = [str(c).lower().strip() for c in n_idx.columns]
    
    # Download India VIX
    vix_df = yf.download("^INDIAVIX", start=FULL_START, end=FULL_END, progress=False, auto_adjust=True)
    if isinstance(vix_df.columns, pd.MultiIndex):
        vix_df.columns = vix_df.columns.get_level_values(0)
    vix_df = vix_df.reset_index()
    vix_df.columns = [str(c).lower().strip() for c in vix_df.columns]
    vix_df = vix_df[['date', 'close']].rename(columns={'close': 'vix'})
    
    # Download USD/INR
    usd_inr = yf.download("INR=X", start=FULL_START, end=FULL_END, progress=False, auto_adjust=True)
    if isinstance(usd_inr.columns, pd.MultiIndex):
        usd_inr.columns = usd_inr.columns.get_level_values(0)
    usd_inr = usd_inr.reset_index()
    usd_inr.columns = [str(c).lower().strip() for c in usd_inr.columns]
    usd_inr = usd_inr[['date', 'close']].rename(columns={'close': 'usd_inr'})

    # Download US 10-Year Treasury Yield
    us_10y = yf.download("^TNX", start=FULL_START, end=FULL_END, progress=False, auto_adjust=True)
    if isinstance(us_10y.columns, pd.MultiIndex):
        us_10y.columns = us_10y.columns.get_level_values(0)
    us_10y = us_10y.reset_index()
    us_10y.columns = [str(c).lower().strip() for c in us_10y.columns]
    us_10y = us_10y[['date', 'close']].rename(columns={'close': 'us_10y_yield'})
    
    if 'date' not in n_idx.columns and 'index' in n_idx.columns:
        n_idx.rename(columns={'index':'date'}, inplace=True)
    
    n_idx['date'] = pd.to_datetime(n_idx['date'])
    vix_df['date'] = pd.to_datetime(vix_df['date'])
    usd_inr['date'] = pd.to_datetime(usd_inr['date'])
    us_10y['date'] = pd.to_datetime(us_10y['date'])
    
    # Global Regime (NSE Index)
    ret = np.log(n_idx['close'] / n_idx['close'].shift(1)).dropna()
    vol = ret.rolling(60).std().fillna(0)
    features = np.column_stack([ret.values[59:], vol.values[59:] + 1e-6])
    h_m = hmm.GaussianHMM(n_components=3, covariance_type='diag', n_iter=500, random_state=SEED).fit(features)
    st = h_m.predict(features)
    m_r = {s: ret.values[59:][st == s].mean() for s in range(3)}; s_s = sorted(m_r, key=m_r.get)
    r_map = {s_s[0]:0, s_s[1]:1, s_s[2]:2}
    reg_df = pd.DataFrame({'date': n_idx['date'].values[60:], 'regime_score': [r_map[s] for s in st]})
    
    # Merge all macro data
    macro_df = reg_df.merge(vix_df, on='date', how='left')
    macro_df = macro_df.merge(usd_inr, on='date', how='left')
    macro_df = macro_df.merge(us_10y, on='date', how='left').ffill().bfill()
    
    counts = macro_df['regime_score'].value_counts(normalize=True)*100
    b_p, br_p, s_p = counts.get(2,0), counts.get(0,0), counts.get(1,0)
    
    nifty_data = n_idx.iloc[60:].copy()
    nifty_data = nifty_data.merge(macro_df, on='date', how='left')
    
    return nifty_data, macro_df, b_p, br_p, s_p

# %%
# ============================================================
# CELL 7: EXECUTION
# ============================================================
if __name__ == "__main__":
    nifty_data, macro_df, b_p, br_p, s_p = compute_regime()

    print(f"🌍 Overall Market Regime: Bull {b_p:.1f}% | Bear {br_p:.1f}% | Sideways {s_p:.1f}%")
    
    results = []
    # Using ProcessPoolExecutor for true parallelism
    with ProcessPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(process_stock, tick, name, sect, macro_df, b_p, br_p, s_p) for stock_id, (tick, name, sect) in STOCK_OPTIONS.items()]
        for f in as_completed(futures):
            res = f.result()
            if res: results.append(res)
    
    res_df = pd.DataFrame(results).drop(columns=['Headlines'])
    import IPython.display as display
    display.display(res_df)
    
    print("\n📰 TOP HEADLINES PER STOCK:")
    for r in results:
        if r['Headlines']:
            print(f"\n{r['Ticker']}:")
            for h in r['Headlines']: print(f"  - {h}")
