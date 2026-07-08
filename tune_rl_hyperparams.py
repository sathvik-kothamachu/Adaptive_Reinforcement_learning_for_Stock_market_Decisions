
import optuna
import os
import pandas as pd
import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import BaseCallback
from sklearn.preprocessing import StandardScaler
from Nifty50_RL_Trading_MultiStock import (
    NiftyRecommendationEnv, compute_regime, process_stock, 
    STOCK_OPTIONS, FEATURE_COLS, TRAIN_START, TRAIN_END, 
    VAL_START, VAL_END, DEVICE, CACHE_DIR
)

# Configuration
TUNE_TICKER = "RELIANCE.NS"
N_TRIALS = 20
TUNE_STEPS = 50000

def objective(trial):
    # 1. Sample Hyperparameters
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-3, log=True)
    n_steps = trial.suggest_categorical("n_steps", [512, 1024, 2048])
    batch_size = trial.suggest_categorical("batch_size", [64, 128, 256])
    n_epochs = trial.suggest_int("n_epochs", 5, 20)
    gamma = trial.suggest_float("gamma", 0.9, 0.9999)
    gae_lambda = trial.suggest_float("gae_lambda", 0.8, 0.99)
    clip_range = trial.suggest_float("clip_range", 0.1, 0.3)
    ent_coef = trial.suggest_float("ent_coef", 1e-8, 0.1, log=True)
    
    # 2. Prepare Data
    # We use cached features for speed, but verify they have the new features
    cache_feat = os.path.join(CACHE_DIR, f"features_{TUNE_TICKER}.csv")
    needs_fetch = not os.path.exists(cache_feat)
    
    if not needs_fetch:
        # Check if all required columns are present
        temp_df = pd.read_csv(cache_feat, nrows=1)
        if not all(col in temp_df.columns for col in FEATURE_COLS):
            print(f"🔄 Cache for {TUNE_TICKER} is missing new features. Forcing refetch...")
            needs_fetch = True
            
    if needs_fetch:
        # Trigger data fetch with new features
        import Nifty50_RL_Trading_MultiStock as rl
        rl.FORCE_REFETCH = True
        _, macro_df, b_p, br_p, s_p = compute_regime()
        # Find the sector ticker for this stock
        sect = "NSEBANK" # Default fallback
        for k, v in STOCK_OPTIONS.items():
            if v[0] == TUNE_TICKER:
                sect = v[2]
                break
        process_stock(TUNE_TICKER, "Tuning Stock", sect, macro_df, b_p, br_p, s_p)
    
    df = pd.read_csv(cache_feat, parse_dates=['date'])
    
    # Scale
    scaler = StandardScaler()
    df_rl = df.copy()
    df_rl[FEATURE_COLS] = scaler.fit_transform(df_rl[FEATURE_COLS])
    
    train_data = df_rl[(df_rl['date'] >= TRAIN_START) & (df_rl['date'] <= TRAIN_END)].copy()
    val_data = df_rl[(df_rl['date'] >= VAL_START) & (df_rl['date'] <= VAL_END)].copy()
    
    # 3. Environments
    train_env = DummyVecEnv([lambda: Monitor(NiftyRecommendationEnv(train_data, FEATURE_COLS))])
    
    # 4. Train
    model = PPO(
        "MlpPolicy", 
        train_env, 
        learning_rate=learning_rate,
        n_steps=n_steps,
        batch_size=batch_size,
        n_epochs=n_epochs,
        gamma=gamma,
        gae_lambda=gae_lambda,
        clip_range=clip_range,
        ent_coef=ent_coef,
        verbose=0,
        device=DEVICE
    )
    
    model.learn(total_timesteps=TUNE_STEPS)
    
    # 5. Evaluate on Validation Set
    val_env = NiftyRecommendationEnv(val_data, FEATURE_COLS)
    obs, _ = val_env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, done, _, _ = val_env.step(action)
    
    # Metric: Sharpe Ratio on Validation Set
    returns = np.array(val_env.returns_hist)
    if len(returns) < 2: return -100.0
    
    sharpe = (returns.mean() / (returns.std() + 1e-8)) * np.sqrt(252)
    return sharpe

if __name__ == "__main__":
    print(f"🎯 Starting Optuna Hyperparameter Optimization for {TUNE_TICKER} on {DEVICE}...")
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=N_TRIALS)
    
    print("\n🏆 Optimization Finished!")
    print(f"Best trial value (Sharpe): {study.best_trial.value:.4f}")
    print("Best params:")
    for key, value in study.best_params.items():
        print(f"    {key}: {value}")
    
    # Save best params to a file for the main script to use
    import json
    with open("best_hyperparams.json", "w") as f:
        json.dump(study.best_params, f, indent=4)
    print("\n✅ Best hyperparameters saved to best_hyperparams.json")
