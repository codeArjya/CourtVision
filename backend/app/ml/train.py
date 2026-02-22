import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from loguru import logger

from app.config import settings

def train_and_save_model(df: pd.DataFrame):
    """
    Trains the XGBoost models on historical data and saves the artifacts.
    """
    if len(df) < settings.MIN_GAMES_FOR_PREDICTION:
        logger.warning(f"Not enough data to train model. Need {settings.MIN_GAMES_FOR_PREDICTION}, got {len(df)}")
        return

    logger.info(f"Starting model training on {len(df)} games...")

    # Required feature pillars per spec
    features = [
        'home_off_rtg_l10', 'home_def_rtg_l10',
        'away_off_rtg_l10', 'away_def_rtg_l10',
        'home_win_pct_l10', 'away_win_pct_l10',
        'home_pace_l10', 'away_pace_l10',
        'home_rest_days', 'away_rest_days',
        'h2h_home_win_pct',
        'home_inj_min_pct', 'away_inj_min_pct'
    ]

    # Ensure all features exist in DF and impute NaNs
    for f in features:
        if f not in df.columns:
            logger.warning(f"Feature '{f}' not found in dataset. Filling with zeros.")
            df[f] = 0.0
    
    # Fill remaining NaNs softly
    df[features] = df[features].fillna(df[features].mean()).fillna(0.0)

    X = df[features]
    y_winner = df['winner'] # 1 if home won, 0 if away won
    y_home_score = df['home_score']
    y_away_score = df['away_score']

    # Normalize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 80/20 train/test split (ideally temporal by season, but simple split for MVP MVP)
    X_train, X_test, yw_train, yw_test = train_test_split(X_scaled, y_winner, test_size=0.2, shuffle=False)
    _, _, yh_train, yh_test = train_test_split(X_scaled, y_home_score, test_size=0.2, shuffle=False)
    _, _, ya_train, ya_test = train_test_split(X_scaled, y_away_score, test_size=0.2, shuffle=False)

    # 1. Train Classifier (Winner)
    clf = xgb.XGBClassifier(
        n_estimators=150, 
        max_depth=4, 
        learning_rate=0.05, 
        objective='binary:logistic'
    )
    clf.fit(X_train, yw_train)
    winner_accuracy = clf.score(X_test, yw_test)
    logger.info(f"Winner Classifier Accuracy: {winner_accuracy * 100:.1f}%")

    # 2. Train Regressors (Scores)
    reg_home = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
    reg_away = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
    
    reg_home.fit(X_train, yh_train)
    reg_away.fit(X_train, ya_train)
    
    # Simple evaluation
    home_mae = np.mean(np.abs(reg_home.predict(X_test) - yh_test))
    away_mae = np.mean(np.abs(reg_away.predict(X_test) - ya_test))
    logger.info(f"Home Score MAE: {home_mae:.1f}, Away Score MAE: {away_mae:.1f}")

    # Save artifacts
    logger.info("Saving model artifacts...")
    os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
    
    models_dict = {
        'classifier': clf,
        'reg_home': reg_home,
        'reg_away': reg_away
    }
    
    joblib.dump(models_dict, settings.MODEL_PATH)
    joblib.dump(scaler, settings.MODEL_SCALER_PATH)
    
    with open(settings.MODEL_FEATURES_PATH, 'w') as f:
        json.dump(features, f)
        
    logger.info("Training complete and artifacts saved.")
    
    return {
        "accuracy": float(winner_accuracy),
        "home_mae": float(home_mae),
        "away_mae": float(away_mae),
        "status": "success"
    }

if __name__ == "__main__":
    # If run directly as module, execute training pulling from Supabase
    from app.services import supabase_service
    from app.ml.features import compute_rolling_features
    
    logger.info("Running training pipeline...")
    
    client = supabase_service.supabase_client
    if not client:
        logger.error("No Supabase client available to pull training data")
        exit(1)
        
    try:
        # Fetch games
        games_res = client.table("games").select("*").execute()
        
        if not games_res.data:
            logger.error("No historical games found in DB. Run bootstrap first.")
            exit(1)
            
        # Simplified feature build for script execution
        # In a deep MVP we would fetch team_game_stats and merge them
        # Let's mock a fast DataFrame
        df = pd.DataFrame(games_res.data)
        
        # We assume df has 'winner' or we calculate it
        if 'home_score' in df.columns and 'away_score' in df.columns:
            df['winner'] = (df['home_score'] > df['away_score']).astype(int)
        else:
            df['home_score'] = 110
            df['away_score'] = 105
            df['winner'] = 1
            
        train_and_save_model(df)
        
    except Exception as e:
        logger.error(f"Training script failed: {e}")
