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
    """Load trained models and scaler into memory."""
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
    """
    Given a single upcoming game dict and historical games_df, predict outcomes.
    Returns: dict matching prediction schema (winner, confidence, scores, keys).
    """
    if not model_loaded():
        raise Exception("Model not loaded yet.")

    from app.ml.features import extract_features
    
    # Needs a Series for feature extractor
    game_series = pd.Series(game_dict)
    
    # 1. Extract raw features
    feats_dict = extract_features(games_df, game_series)
    
    # Map to list in exact order of trained features
    try:
        raw_feat_arr = np.array([[feats_dict[f] for f in _feature_names]])
    except KeyError as e:
        logger.error(f"Missing feature expected by model: {e}")
        raise e
        
    # 2. Scale
    scaled_feats = _scaler.transform(raw_feat_arr)
    
    # 3. Predict metrics
    model_home = _model_package['model_home']
    model_away = _model_package['model_away']
    model_win = _model_package['model_win']
    
    pred_home_score = float(model_home.predict(scaled_feats)[0])
    pred_away_score = float(model_away.predict(scaled_feats)[0])
    pred_win_prob = float(model_win.predict_proba(scaled_feats)[0][1]) # Assuming 1 is Home Win
    
    # 4. Determine Winner
    is_home_win = pred_win_prob >= 0.5
    
    winner_name = game_dict.get('home_team_name') if is_home_win else game_dict.get('away_team_name')
    winner_abbr = game_dict.get('home_team_abbr') if is_home_win else game_dict.get('away_team_abbr')
    
    # Scale probabilities from 0.5-1.0 to confidence 55-88
    # confidence = 55 + (prob - 0.5) / 0.5 * (88 - 55)
    prob_confidence = pred_win_prob if is_home_win else (1 - pred_win_prob)
    confidence_mapped = 55 + ((prob_confidence - 0.5) / 0.5) * (88 - 55)
    confidence = int(min(max(confidence_mapped, 55), 88))
    
    # Determine key factors dynamically based on driving features
    # For a hackathon, we can use simple heuristic messages off the raw features
    key_factors = []
    
    if feats_dict['home_win_pct_L10'] > feats_dict['away_win_pct_L10']:
        key_factors.append(f"{game_dict.get('home_team_abbr')} has better L10 win record")
    else:
        key_factors.append(f"{game_dict.get('away_team_abbr')} carrying more momentum recently")
        
    if feats_dict['home_rest_days'] > feats_dict['away_rest_days']:
        key_factors.append(f"Rest advantage favors {game_dict.get('home_team_abbr')}")
    elif feats_dict['is_b2b_away'] == 1:
         key_factors.append(f"{game_dict.get('away_team_abbr')} on second night of back-to-back")
    else:
        key_factors.append("Evenly matched on recent rest days")
        
    if pred_home_score + pred_away_score > 230:
        key_factors.append("Projecting a high-paced offensive shootout")
    else:
        key_factors.append("Expect a slower, defensive battle")
        
    # Temporarily add this to predict_game in predict.py, right after extract_features
    print(f"[DEBUG] home_id={game_dict.get('home_team_id')}, away_id={game_dict.get('away_team_id')}")
    print(f"[DEBUG] games_df rows={len(games_df)}, sample team IDs={games_df['home_team_id'].unique()[:3].tolist() if not games_df.empty else 'EMPTY'}")
    print(f"[DEBUG] features: home_pts={feats_dict['home_pts_L5']}, away_pts={feats_dict['away_pts_L5']}, home_win_pct={feats_dict['home_win_pct_L10']}")
        
    return {
        "winner": winner_name,
        "winner_abbr": winner_abbr,
        "confidence": confidence,
        "score_home": int(round(pred_home_score)),
        "score_away": int(round(pred_away_score)),
        "key_factors": key_factors[:3],
        "source": "ml_model" # Tag for verification
    }
