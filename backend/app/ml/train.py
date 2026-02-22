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
        logger.warning("No Supabase client available.")
        return pd.DataFrame()
    try:
        res = supabase_client.table("games").select("*").eq("status", "final").execute()
        if not res.data:
            logger.warning("No finalized games in DB.")
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception as e:
        logger.error(f"Error fetching training data: {e}")
        return pd.DataFrame()


def train_model():
    logger.info("Starting ML Training Pipeline...")
    games_df = fetch_training_data()

    if games_df.empty or len(games_df) < settings.MIN_GAMES_FOR_PREDICTION:
        logger.error(f"Not enough games ({len(games_df)}). Need {settings.MIN_GAMES_FOR_PREDICTION}.")
        return False

    games_df = games_df.sort_values('game_date').reset_index(drop=True)
    # Ensure team IDs are strings for consistent matching in feature extractor
    games_df['home_team_id'] = games_df['home_team_id'].astype(str)
    games_df['away_team_id'] = games_df['away_team_id'].astype(str)

    X_rows, y_home_scores, y_away_scores, y_winners = [], [], [], []

    total = len(games_df)
    logger.info(f"Extracting features from {total} historical games...")
    skipped = 0
    for idx, row in games_df.iterrows():
        if pd.isna(row.get('home_score')) or pd.isna(row.get('away_score')):
            skipped += 1
            continue

        feats = extract_features(games_df, row)
        X_rows.append([feats[f] for f in FEATURE_NAMES])
        y_home_scores.append(float(row['home_score']))
        y_away_scores.append(float(row['away_score']))
        y_winners.append(1 if row['home_score'] > row['away_score'] else 0)

        if (idx + 1) % 500 == 0:
            logger.info(f"  Processed {idx + 1}/{total} games...")

    logger.info(f"Feature extraction done. {len(X_rows)} valid rows, {skipped} skipped (missing scores).")

    X = np.array(X_rows)
    y_home = np.array(y_home_scores)
    y_away = np.array(y_away_scores)
    y_win = np.array(y_winners)

    if len(X) < settings.MIN_GAMES_FOR_PREDICTION:
        logger.error("Not enough valid feature rows after extraction.")
        return False

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Time-series split — never shuffle NBA game data
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
    yh_train, yh_test = y_home[:split_idx], y_home[split_idx:]
    ya_train, ya_test = y_away[:split_idx], y_away[split_idx:]
    yw_train, yw_test = y_win[:split_idx], y_win[split_idx:]

    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # Improved hyperparameters — more trees, lower LR, subsample for regularization
    common_params = dict(
        n_estimators=400,
        learning_rate=0.03,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        reg_alpha=0.1,      # L1 regularization
        reg_lambda=1.5,     # L2 regularization
        random_state=42,
        n_jobs=-1,
    )

    logger.info("Training XGBoost models...")
    model_home = xgb.XGBRegressor(**common_params)
    model_away = xgb.XGBRegressor(**common_params)
    model_win = xgb.XGBClassifier(
        **common_params,
        eval_metric='logloss',
        use_label_encoder=False,
    )

    model_home.fit(X_train, yh_train, eval_set=[(X_test, yh_test)], verbose=False)
    model_away.fit(X_train, ya_train, eval_set=[(X_test, ya_test)], verbose=False)
    model_win.fit(X_train, yw_train, eval_set=[(X_test, yw_test)], verbose=False)

    # Evaluate
    mae_home = mean_absolute_error(yh_test, model_home.predict(X_test))
    mae_away = mean_absolute_error(ya_test, model_away.predict(X_test))
    acc = accuracy_score(yw_test, model_win.predict(X_test))

    # Also log score-implied accuracy (if predicted home_score > away_score = home win)
    score_implied_winners = (model_home.predict(X_test) > model_away.predict(X_test)).astype(int)
    score_implied_acc = accuracy_score(yw_test, score_implied_winners)

    logger.info(f"Results — Win Classifier Accuracy: {acc*100:.2f}%")
    logger.info(f"Results — Score-Implied Accuracy: {score_implied_acc*100:.2f}%")
    logger.info(f"Results — Home MAE: {mae_home:.2f}, Away MAE: {mae_away:.2f}")

    # Feature importance for debugging
    importances = sorted(
        zip(FEATURE_NAMES, model_win.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    logger.info("Top 10 features by importance:")
    for name, score in importances[:10]:
        logger.info(f"  {name}: {score:.4f}")

    # Save artifacts
    artifacts_dir = os.path.dirname(settings.MODEL_PATH)
    os.makedirs(artifacts_dir, exist_ok=True)

    model_package = {
        'model_home': model_home,
        'model_away': model_away,
        'model_win': model_win,
        'metrics': {
            'accuracy': float(acc),
            'score_implied_accuracy': float(score_implied_acc),
            'home_mae': float(mae_home),
            'away_mae': float(mae_away),
            'train_size': len(X_train),
            'test_size': len(X_test),
        }
    }

    joblib.dump(model_package, settings.MODEL_PATH)
    joblib.dump(scaler, settings.MODEL_SCALER_PATH)
    with open(settings.MODEL_FEATURES_PATH, 'w') as f:
        json.dump(FEATURE_NAMES, f)

    logger.info(f"Artifacts saved to {artifacts_dir}")
    return True

if __name__ == "__main__":
    train_model()