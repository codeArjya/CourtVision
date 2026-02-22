# backend/app/ml/train.py
import os
import json
import joblib
import pandas as pd
import numpy as np
from loguru import logger
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, accuracy_score
from app.services.supabase_service import supabase_client
from app.ml.features import FEATURE_NAMES, extract_features
from app.config import settings

def fetch_training_data() -> pd.DataFrame:
    logger.info("Fetching game data from Supabase for training...")
    if not supabase_client:
        logger.warning("No Supabase client available. Training will fail or use mock data.")
        return pd.DataFrame()
        
    try:
        # Fetch all finalized games
        res = supabase_client.table("games").select("*").eq("status", "final").execute()
        if not res.data:
            logger.warning("No finalized games in DB for training.")
            return pd.DataFrame()
        
        return pd.DataFrame(res.data)
    except Exception as e:
        logger.error(f"Error fetching training data: {e}")
        return pd.DataFrame()

def train_model():
    logger.info("Starting ML Training Pipeline...")
    games_df = fetch_training_data()
    
    if games_df.empty or len(games_df) < settings.MIN_GAMES_FOR_PREDICTION:
        logger.error(f"Not enough games to train ({len(games_df)}). Need at least {settings.MIN_GAMES_FOR_PREDICTION}. Run bootstrap.")
        return False
        
    # Build dataset
    X_rows = []
    y_home_scores = []
    y_away_scores = []
    y_winners = []
    
    logger.info("Extracting features from historical games...")
    # Need to process sequentially to ensure history is rolling
    games_df = games_df.sort_values('game_date').reset_index(drop=True)
    
    for idx, row in games_df.iterrows():
        # Only use games with real scores
        if pd.isna(row.get('home_score')) or pd.isna(row.get('away_score')):
            continue
            
        feats = extract_features(games_df, row)
        row_feat_list = [feats[f] for f in FEATURE_NAMES]
        
        X_rows.append(row_feat_list)
        y_home_scores.append(float(row['home_score']))
        y_away_scores.append(float(row['away_score']))
        y_winners.append(1 if row['home_score'] > row['away_score'] else 0)

    X = np.array(X_rows)
    y_home = np.array(y_home_scores)
    y_away = np.array(y_away_scores)
    y_win = np.array(y_winners)
    
    if len(X) < settings.MIN_GAMES_FOR_PREDICTION:
        logger.error("Not enough valid feature rows.")
        return False

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train test split
    # Since it's time series-adjacent, we don't shuffle for realistic evaluation
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
    yh_train, yh_test = y_home[:split_idx], y_home[split_idx:]
    ya_train, ya_test = y_away[:split_idx], y_away[split_idx:]
    yw_train, yw_test = y_win[:split_idx], y_win[split_idx:]

    # Train Models
    logger.info("Training multi-target XGBoost models...")
    
    # We train two regressors for scores, or a single multi-output
    # To predict winner directly as well for accuracy
    model_home = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
    model_away = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
    model_win = xgb.XGBClassifier(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
    
    model_home.fit(X_train, yh_train)
    model_away.fit(X_train, ya_train)
    model_win.fit(X_train, yw_train)
    
    # Evaluate
    logger.info("Evaluating models...")
    ph_test = model_home.predict(X_test)
    pa_test = model_away.predict(X_test)
    pw_test = model_win.predict(X_test)
    
    mae_home = mean_absolute_error(yh_test, ph_test)
    mae_away = mean_absolute_error(ya_test, pa_test)
    
    # Combine predictions to determine winner to double check
    # Win prediction accuracy vs actual
    acc = accuracy_score(yw_test, pw_test)
    
    logger.info(f"Training Results - Accuracy: {acc*100:.2f}%, Home MAE: {mae_home:.2f}, Away MAE: {mae_away:.2f}")

    # Artifact Serialization
    artifacts_dir = os.path.dirname(settings.MODEL_PATH)
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Combine into generic dictionary object for saving
    model_package = {
        'model_home': model_home,
        'model_away': model_away,
        'model_win': model_win,
        'metrics': {
            'accuracy': float(acc),
            'home_mae': float(mae_home),
            'away_mae': float(mae_away)
        }
    }
    
    joblib.dump(model_package, settings.MODEL_PATH)
    joblib.dump(scaler, settings.MODEL_SCALER_PATH)
    
    with open(settings.MODEL_FEATURES_PATH, 'w') as f:
        json.dump(FEATURE_NAMES, f)
        
    logger.info(f"Model artifacts saved to {artifacts_dir}")
    return True

if __name__ == "__main__":
    train_model()
