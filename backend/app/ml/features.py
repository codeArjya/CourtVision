# backend/app/ml/features.py
import pandas as pd

FEATURE_NAMES = [
    'home_win_pct_L10', 'away_win_pct_L10',
    'home_rest_days', 'away_rest_days',
    'home_pts_L5', 'away_pts_L5',
    'home_pts_allowed_L5', 'away_pts_allowed_L5',
    'home_off_rtg', 'away_off_rtg',
    'home_def_rtg', 'away_def_rtg',
    'home_pace', 'away_pace',
    'is_b2b_away'
]

def extract_features(games_df: pd.DataFrame, game_row: pd.Series) -> dict:
    """
    Given a pandas row representing a game, and historical df, calculate features.
    In a real system, you'd calculate rolling stats over the df up to the game date.
    We'll do a simplified mock fallback if df is empty or not enough history.
    """
    home_id = game_row.get('home_team_id', '')
    away_id = game_row.get('away_team_id', '')
    date_val = game_row.get('game_date', '')
    date_obj = pd.to_datetime(date_val) if date_val else pd.Timestamp.today()

    # Very basic default features
    feats = {f: 0.0 for f in FEATURE_NAMES}
    
    if games_df.empty:
        feats['home_win_pct_L10'] = 0.500
        feats['home_rest_days'] = 2
        feats['home_pts_L5'] = 110.0
        feats['home_pts_allowed_L5'] = 110.0
        feats['away_win_pct_L10'] = 0.500
        feats['away_rest_days'] = 2
        feats['is_b2b_away'] = 0
        feats['away_pts_L5'] = 110.0
        feats['away_pts_allowed_L5'] = 110.0
        
        feats['home_off_rtg'] = 115.0
        feats['home_def_rtg'] = 112.0
        feats['home_pace'] = 98.5
        feats['away_off_rtg'] = 113.0
        feats['away_def_rtg'] = 114.0
        feats['away_pace'] = 99.0
        return feats

    past_games = games_df[pd.to_datetime(games_df['game_date']) < date_obj]
    
    # Home Team Stats
    home_past = past_games[(past_games['home_team_id'] == home_id) | (past_games['away_team_id'] == home_id)].sort_values('game_date', ascending=False)
    if not home_past.empty:
        last10 = home_past.head(10)
        wins = 0
        for _, row in last10.iterrows():
            if row['home_team_id'] == home_id and row.get('home_score', 0) > row.get('away_score', 0): wins += 1
            if row['away_team_id'] == home_id and row.get('away_score', 0) > row.get('home_score', 0): wins += 1
        feats['home_win_pct_L10'] = wins / len(last10)
        
        last_game_date = pd.to_datetime(home_past.iloc[0]['game_date'])
        feats['home_rest_days'] = min((date_obj - last_game_date).days, 7)
        
        last5 = home_past.head(5)
        pts = 0
        allowed = 0
        for _, row in last5.iterrows():
            if row['home_team_id'] == home_id:
                pts += row.get('home_score', 0)
                allowed += row.get('away_score', 0)
            else:
                pts += row.get('away_score', 0)
                allowed += row.get('home_score', 0)
        feats['home_pts_L5'] = pts / len(last5)
        feats['home_pts_allowed_L5'] = allowed / len(last5)
    else:
        feats['home_win_pct_L10'] = 0.500
        feats['home_rest_days'] = 2
        feats['home_pts_L5'] = 110.0
        feats['home_pts_allowed_L5'] = 110.0
        
    # Away Team Stats
    away_past = past_games[(past_games['home_team_id'] == away_id) | (past_games['away_team_id'] == away_id)].sort_values('game_date', ascending=False)
    if not away_past.empty:
        last10 = away_past.head(10)
        wins = 0
        for _, row in last10.iterrows():
            if row['home_team_id'] == away_id and row.get('home_score', 0) > row.get('away_score', 0): wins += 1
            if row['away_team_id'] == away_id and row.get('away_score', 0) > row.get('home_score', 0): wins += 1
        feats['away_win_pct_L10'] = wins / len(last10)
        
        last_game_date = pd.to_datetime(away_past.iloc[0]['game_date'])
        feats['away_rest_days'] = min((date_obj - last_game_date).days, 7)
        feats['is_b2b_away'] = 1 if feats['away_rest_days'] == 1 else 0
        
        last5 = away_past.head(5)
        pts = 0
        allowed = 0
        for _, row in last5.iterrows():
            if row['home_team_id'] == away_id:
                pts += row.get('home_score', 0)
                allowed += row.get('away_score', 0)
            else:
                pts += row.get('away_score', 0)
                allowed += row.get('home_score', 0)
        feats['away_pts_L5'] = pts / len(last5)
        feats['away_pts_allowed_L5'] = allowed / len(last5)
    else:
        feats['away_win_pct_L10'] = 0.500
        feats['away_rest_days'] = 2
        feats['is_b2b_away'] = 0
        feats['away_pts_L5'] = 110.0
        feats['away_pts_allowed_L5'] = 110.0

    feats['home_off_rtg'] = 115.0
    feats['home_def_rtg'] = 112.0
    feats['home_pace'] = 98.5
    feats['away_off_rtg'] = 113.0
    feats['away_def_rtg'] = 114.0
    feats['away_pace'] = 99.0

    return feats
