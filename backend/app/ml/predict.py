# backend/app/ml/predict.py
import json
import joblib
import pandas as pd
import numpy as np
from loguru import logger
from app.config import settings

_model_package = None
_scaler = None
_feature_names = None


def load_model_artifacts():
    global _model_package, _scaler, _feature_names
    if not settings.USE_ML_MODEL:
        logger.info("ML Model disabled in config, skipping load.")
        return False
    try:
        logger.info(f"Loading model artifacts from {settings.MODEL_PATH}...")
        _model_package = joblib.load(settings.MODEL_PATH)
        _scaler = joblib.load(settings.MODEL_SCALER_PATH)
        with open(settings.MODEL_FEATURES_PATH, 'r') as f:
            _feature_names = json.load(f)
        logger.info("Model artifacts successfully loaded into memory.")
        return True
    except Exception as e:
        logger.error(f"Failed to load model artifacts: {e}")
        raise FileNotFoundError("Run training script first to generate artifacts")


def model_loaded() -> bool:
    return _model_package is not None and _scaler is not None


def predict_game(game_dict: dict, games_df: pd.DataFrame) -> dict:
    if not model_loaded():
        raise Exception("Model not loaded yet.")

    from app.ml.features import extract_features

    game_series = pd.Series(game_dict)
    feats_dict = extract_features(games_df, game_series)

    # BUG FIX: Log feature values so we can verify they're non-default.
    # If you still see home_pts=110.0 after the team ID fix, the issue is
    # in features.py — share that file for further debugging.
    logger.info(
        f"[predict] {game_dict.get('home_team_abbr')} vs {game_dict.get('away_team_abbr')} | "
        f"home_team_id={game_dict.get('home_team_id')} away_team_id={game_dict.get('away_team_id')} | "
        f"home_pts_L5={feats_dict.get('home_pts_L5')} away_pts_L5={feats_dict.get('away_pts_L5')} "
        f"home_win_pct_L10={feats_dict.get('home_win_pct_L10')}"
    )

    # Check if features are all defaults — means team ID lookup failed
    if feats_dict.get('home_pts_L5') == 110.0 and feats_dict.get('away_pts_L5') == 110.0:
        logger.warning(
            f"[predict] Default features detected for game {game_dict.get('game_id')} — "
            f"team IDs may not match Supabase historical data. "
            f"home_team_id={game_dict.get('home_team_id')} "
            f"away_team_id={game_dict.get('away_team_id')}"
        )

    try:
        raw_feat_arr = np.array([[feats_dict[f] for f in _feature_names]])
    except KeyError as e:
        logger.error(f"Missing feature expected by model: {e}")
        raise

    scaled_feats = _scaler.transform(raw_feat_arr)

    model_home = _model_package['model_home']
    model_away = _model_package['model_away']
    model_win  = _model_package['model_win']

    pred_home_score = float(model_home.predict(scaled_feats)[0])
    pred_away_score = float(model_away.predict(scaled_feats)[0])
    pred_win_prob   = float(model_win.predict_proba(scaled_feats)[0][1])

    is_home_win  = pred_win_prob >= 0.5
    winner_name  = game_dict.get('home_team_name') if is_home_win else game_dict.get('away_team_name')
    winner_abbr  = game_dict.get('home_team_abbr')  if is_home_win else game_dict.get('away_team_abbr')

    prob_confidence    = pred_win_prob if is_home_win else (1 - pred_win_prob)
    confidence_mapped  = 55 + ((prob_confidence - 0.5) / 0.5) * (88 - 55)
    confidence         = int(min(max(confidence_mapped, 55), 88))

    # Key factors from actual feature values
    key_factors = []
    if feats_dict.get('home_win_pct_L10', 0.5) > feats_dict.get('away_win_pct_L10', 0.5):
        key_factors.append(f"{game_dict.get('home_team_abbr')} has better L10 win record")
    else:
        key_factors.append(f"{game_dict.get('away_team_abbr')} carrying more momentum recently")

    if feats_dict.get('home_rest_days', 0) > feats_dict.get('away_rest_days', 0):
        key_factors.append(f"Rest advantage favors {game_dict.get('home_team_abbr')}")
    elif feats_dict.get('is_b2b_away', 0) == 1:
        key_factors.append(f"{game_dict.get('away_team_abbr')} on second night of back-to-back")
    else:
        key_factors.append("Teams evenly matched on rest")

    total = pred_home_score + pred_away_score
    if total > 230:
        key_factors.append(f"High-scoring pace projected ({int(round(total))} total pts)")
    elif total < 210:
        key_factors.append(f"Defensive battle expected ({int(round(total))} total pts)")
    else:
        key_factors.append(f"Moderate pace projected ({int(round(total))} total pts)")

    logger.info(
        f"[predict] Result: {winner_abbr} wins | "
        f"score={int(round(pred_home_score))}-{int(round(pred_away_score))} | "
        f"confidence={confidence}% | win_prob={pred_win_prob:.3f}"
    )

    return {
        "winner":      winner_name,
        "winner_abbr": winner_abbr,
        "confidence":  confidence,
        "score_home":  int(round(pred_home_score)),
        "score_away":  int(round(pred_away_score)),
        "key_factors": key_factors[:3],
        "source":      "ml_model",
    }