import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

# Set modern style with white background
plt.style.use('default')
sns.set_style("whitegrid")
sns.set_palette("viridis")

# Configuration (Mirrors your main script)
CACHE_DIR = "cache"
MODEL_DIR = "trained_models"
DUMMY_CAPITAL = 1000000
TRANSACTION_COST = 0.001
MAX_SHARES = 100

FEATURE_COLS = [
    'close_norm', 'daily_return', 'log_return', 'volatility_10',
    'macd', 'macd_signal', 'macd_hist', 'sma_10', 'sma_50', 'ema_20',
    'rsi', 'stoch_k', 'stoch_d', 'roc', 'bb_pct', 'bb_width', 'atr',
    'obv', 'adx', 'sentiment_score', 'regime_score', 'tech_strength_score'
]

STOCK_OPTIONS = {
    "1": ("RELIANCE.NS",   "Reliance"),
    "2": ("TCS.NS",        "TCS"),
    "3": ("HDFCBANK.NS",   "HDFC Bank"),
    "4": ("INFY.NS",       "Infosys"),
    "5": ("ICICIBANK.NS",  "ICICI Bank"),
    "6": ("HINDUNILVR.NS", "HUL"),
    "7": ("ITC.NS",        "ITC"),
    "8": ("SBIN.NS",       "SBI"),
    "9": ("BHARTIARTL.NS", "Airtel"),
    "10":("KOTAKBANK.NS",  "Kotak Bank"),
}

class NiftyRecommendationEnv(gym.Env):
    def __init__(self, df, feature_cols):
        super().__init__()
        self.df, self.feature_cols = df.reset_index(drop=True), feature_cols
        self.n_days = len(self.df)
        self.obs_shape = (1 + len(feature_cols) + 1,)
        self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-10, high=10, shape=self.obs_shape, dtype=np.float32)
        self.reset()
    def _obs(self):
        if self.current_step >= len(self.df): return np.zeros(self.obs_shape, dtype=np.float32)
        row = self.df.iloc[self.current_step]
        return np.nan_to_num(np.concatenate([[self.position], row[self.feature_cols].values, [row['close_norm']]]), nan=0.0).astype(np.float32)
    def reset(self, seed: int | None = None, options: dict | None = None):
        self.current_step = 0
        self.balance = float(DUMMY_CAPITAL)
        self.shares_held = 0
        self.position = 0.0
        self.portfolio_hist: list[float] = [float(DUMMY_CAPITAL)]
        return self._obs(), {}
    def step(self, action):
        row, action_scalar = self.df.iloc[self.current_step], float(action[0])
        price = float(row['close'])
        if action_scalar > 0.3:
            n = min(int((self.balance * 0.3) / (price * (1+TRANSACTION_COST))), MAX_SHARES)
            if n > 0: self.balance -= n*price*(1+TRANSACTION_COST); self.shares_held += n; self.position = min(1.0, self.position+0.3)
        elif action_scalar < -0.3:
            n = min(self.shares_held, max(1, int(self.shares_held * 0.5)))
            if n > 0: self.balance += n*price*(1-TRANSACTION_COST); self.shares_held -= n; self.position = max(-1.0, self.position-0.3)
        self.current_step += 1
        done = self.current_step >= self.n_days - 1
        val = self.balance + self.shares_held * (float(self.df.iloc[self.current_step]['close']) if not done else price)
        self.portfolio_hist.append(val)
        return self._obs(), 0.0, done, False, {}

def load_all_data():
    all_dfs = {}
    for sid, (ticker, name) in STOCK_OPTIONS.items():
        fname = os.path.join(CACHE_DIR, f"features_{ticker}.csv")
        if os.path.exists(fname):
            df = pd.read_csv(fname, parse_dates=['date'])
            all_dfs[ticker] = df
    return all_dfs

def plot_normalized_prices(all_dfs):
    plt.figure(figsize=(14, 7))
    for ticker, df in all_dfs.items():
        norm_price = (df['close'] / df['close'].iloc[0]) * 100
        plt.plot(df['date'], norm_price, label=ticker, alpha=0.8)
    plt.title("Normalized Price Comparison (Base 100)", fontsize=16, pad=20)
    plt.ylabel("Index Value")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.grid(alpha=0.1)
    plt.tight_layout()
    plt.savefig("normalized_prices.png", dpi=150)
    print("✅ Saved normalized_prices.png")

def plot_correlation_heatmap(all_dfs):
    returns_df = pd.DataFrame()
    for ticker, df in all_dfs.items():
        returns_df[ticker] = df.set_index('date')['daily_return']
    plt.figure(figsize=(12, 10))
    
    # Create custom colormap: Dark Green (negative) -> Light/White (zero) -> Dark Red (positive)
    from matplotlib.colors import LinearSegmentedColormap
    colors_list = ['#004D00', '#90EE90', '#FFFFFF', '#FFB6C6', '#8B0000']  # Dark Green -> Light Green -> White -> Light Red -> Dark Red
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('custom_corr', colors_list, N=n_bins)
    
    sns.heatmap(returns_df.corr(), annot=True, cmap=cmap, fmt=".2f", center=0, 
                vmin=-1, vmax=1, cbar_kws={'label': 'Correlation Coefficient'})
    plt.title("Stock Return Correlation Heatmap\n(Dark Red = Positive | Light/White = No Correlation | Dark Green = Negative)", 
              fontsize=16, pad=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig("correlation_heatmap.png", dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Saved correlation_heatmap.png with custom color scheme")
    plt.show()

def plot_market_regime_distribution(all_dfs):
    first_ticker = list(all_dfs.keys())[0]
    df = all_dfs[first_ticker]
    regime_map = {0: 'Bearish', 1: 'Sideways', 2: 'Bullish'}
    counts = df['regime_score'].map(regime_map).value_counts(normalize=True) * 100
    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['#ffcc00', '#00cc66', '#ff4d4d'], 
            startangle=140, explode=[0.1]*len(counts))
    plt.title("Market Regime Distribution", fontsize=16)
    plt.savefig("regime_distribution.png", dpi=150)
    print("✅ Saved regime_distribution.png")

def plot_monthly_return_heatmap(all_dfs, ticker="RELIANCE.NS"):
    if ticker not in all_dfs: return
    df = all_dfs[ticker].copy()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    monthly_ret = df.groupby(['year', 'month'])['daily_return'].apply(lambda x: (np.prod(1+x) - 1) * 100)
    pivot = monthly_ret.unstack()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot.columns = [month_names[m-1] for m in pivot.columns if m <= len(month_names)]
    plt.figure(figsize=(15, 8))
    sns.heatmap(pivot, annot=True, cmap='RdYlGn', center=0, fmt=".1f", linewidths=.5)
    plt.title(f"Monthly Returns Heatmap (%) - {ticker}", fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(f"monthly_heatmap_{ticker.replace('.', '_')}.png", dpi=150)
    print(f"✅ Saved monthly_heatmap_{ticker}.png")

def plot_rl_performance(all_dfs, ticker="RELIANCE.NS"):
    mod_path = os.path.join(MODEL_DIR, f"PPO_{ticker}")
    # Check for both .zip and extensionless (legacy)
    actual_path = mod_path + ".zip" if os.path.exists(mod_path + ".zip") else mod_path
    
    if not os.path.exists(actual_path) or ticker not in all_dfs:
        print(f"⚠️ Model or data missing for {ticker}, skipping RL curve.")
        return

    df = all_dfs[ticker].copy()
    # Use recent data for evaluation (last 252 days)
    test_data = df.tail(252).copy()
    
    try:
        model = PPO.load(actual_path)
        env = NiftyRecommendationEnv(test_data, FEATURE_COLS)
        obs, _ = env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, _, done, _, _ = env.step(action)
        
        plt.figure(figsize=(12, 6))
        # Cumulative returns
        rl_returns = (np.array(env.portfolio_hist) / env.portfolio_hist[0] - 1) * 100
        bh_returns = (test_data['close'].values / test_data['close'].iloc[0] - 1) * 100
        
        plt.plot(test_data['date'], rl_returns, label='RL Agent Strategy', color='#009966', linewidth=2)
        plt.plot(test_data['date'], bh_returns, label='Buy & Hold Benchmark', color='black', alpha=0.6, linestyle='--')
        
        plt.title(f"RL Performance Curve: {ticker} (Last 252 Days)", fontsize=16, pad=20)
        plt.ylabel("Cumulative Return (%)")
        plt.legend()
        plt.grid(alpha=0.1)
        plt.tight_layout()
        plt.savefig("rl_performance_curve.png", dpi=150)
        print("✅ Saved rl_performance_curve.png")
    except Exception as e:
        print(f"❌ RL Plot Error: {e}")

def plot_rolling_volatility(all_dfs, ticker="KOTAKBANK.NS", window_days=365):
    if ticker not in all_dfs:
        print(f"⚠️ Data missing for {ticker}, skipping rolling volatility chart.")
        return

    df = all_dfs[ticker].copy()
    df['date'] = pd.to_datetime(df['date'])
    end_date = df['date'].max()
    start_date = end_date - pd.Timedelta(days=window_days)
    df = df[df['date'] >= start_date].copy()

    if df.empty:
        print(f"⚠️ No data available for {ticker} in the last {window_days} days.")
        return

    vol = df['daily_return'].rolling(window=21).std() * np.sqrt(252) * 100

    plt.figure(figsize=(14, 7))
    plt.plot(df['date'], vol, label='Kotak Bank', color='#1f3b73', linewidth=2)
    plt.title("Kotak Bank 21-Day Rolling Annualized Volatility (%) - Last 1 Year", fontsize=16, pad=20)
    plt.ylabel("Volatility (%)")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(alpha=0.1)
    plt.tight_layout()
    plt.savefig("rolling_volatility_kotak_1y.png", dpi=150)
    print("✅ Saved rolling_volatility_kotak_1y.png")

def plot_sentiment_distribution(all_dfs):
    plt.figure(figsize=(12, 6))
    for i, (ticker, df) in enumerate(all_dfs.items()):
        if i >= 5: break
        active_sent = df[df['sentiment_score'] != 0]['sentiment_score']
        if not active_sent.empty:
            sns.kdeplot(active_sent, label=ticker, fill=True, alpha=0.3)
    plt.title("Sentiment Score Density", fontsize=16, pad=20)
    plt.axvline(0, color='black', linestyle='--', alpha=0.5)
    plt.legend()
    plt.savefig("sentiment_distribution.png", dpi=150)
    print("✅ Saved sentiment_distribution.png")

if __name__ == "__main__":
    data = load_all_data()
    if data:
        plot_normalized_prices(data)
        plot_correlation_heatmap(data)
        plot_market_regime_distribution(data)
        plot_monthly_return_heatmap(data, ticker=list(data.keys())[0])
        plot_rl_performance(data, ticker=list(data.keys())[0])
        plot_rolling_volatility(data)
        plot_sentiment_distribution(data)
        print("\n✨ All charts generated!")
