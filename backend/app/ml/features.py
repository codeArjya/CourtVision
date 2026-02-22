# backend/app/ml/features.py
import pandas as pd
import numpy as np

FEATURE_NAMES = [
    # Raw team stats
    'home_win_pct_L10', 'away_win_pct_L10',
    'home_rest_days', 'away_rest_days',
    'home_pts_L5', 'away_pts_L5',
    'home_pts_allowed_L5', 'away_pts_allowed_L5',
    'home_off_rtg', 'away_off_rtg',
    'home_def_rtg', 'away_def_rtg',
    'home_pace', 'away_pace',
    'is_b2b_away', 'is_b2b_home',

    # Differential features — XGBoost learns these much better
    'win_pct_diff',       # home - away
    'rest_diff',          # home - away rest days
    'pts_diff',           # home avg pts - away avg pts
    'def_rtg_diff',       # home def_rtg - away def_rtg (lower is better defense)
    'off_rtg_diff',       # home off_rtg - away off_rtg
    'pace_avg',           # average pace of both teams (predicts total)

    # Home court advantage proxy
    'home_win_pct_home_only',   # home team's win% specifically at home
    'away_win_pct_away_only',   # away team's win% specifically on road
]


def _get_team_stats(past_games: pd.DataFrame, team_id: str, as_home_perspective: bool = None):
    """
    Compute rolling stats for a team from their past games.
    Returns a dict of computed stats.
    """
    stats = {
        'win_pct_L10': 0.500,
        'rest_days': 2,
        'pts_L5': 110.0,
        'pts_allowed_L5': 110.0,
        'off_rtg': 113.0,
        'def_rtg': 113.0,
        'pace': 98.5,
        'win_pct_home_only': 0.500,
        'win_pct_away_only': 0.500,
        'is_b2b': 0,
    }

    team_games = past_games[
        (past_games['home_team_id'] == team_id) | (past_games['away_team_id'] == team_id)
    ].sort_values('game_date', ascending=False)

    if team_games.empty:
        return stats

    # Rest days
    last_game_date = pd.to_datetime(team_games.iloc[0]['game_date'])
    # date_obj is not passed here — caller handles rest_days

    # L10 win pct
    last10 = team_games.head(10)
    wins = 0
    for _, row in last10.iterrows():
        if row['home_team_id'] == team_id and row.get('home_score', 0) > row.get('away_score', 0):
            wins += 1
        elif row['away_team_id'] == team_id and row.get('away_score', 0) > row.get('home_score', 0):
            wins += 1
    stats['win_pct_L10'] = wins / len(last10)

    # L5 scoring
    last5 = team_games.head(5)
    pts_list, allowed_list = [], []
    for _, row in last5.iterrows():
        if row['home_team_id'] == team_id:
            pts_list.append(row.get('home_score', 110))
            allowed_list.append(row.get('away_score', 110))
        else:
            pts_list.append(row.get('away_score', 110))
            allowed_list.append(row.get('home_score', 110))

    stats['pts_L5'] = np.mean(pts_list) if pts_list else 110.0
    stats['pts_allowed_L5'] = np.mean(allowed_list) if allowed_list else 110.0

    # Rolling offensive/defensive rating proxy (points per game pace-adjusted over L15)
    # Real off_rtg = 100 * pts / possessions. We approximate possessions as 0.96*(FGA-OR+TO+0.44*FTA)
    # Since we don't have play-by-play, we use pts scored/allowed over L15 as a reasonable proxy
    last15 = team_games.head(15)
    pts15, allowed15 = [], []
    home_wins, home_games, away_wins, away_games = 0, 0, 0, 0

    for _, row in last15.iterrows():
        hs = row.get('home_score', 0) or 0
        as_ = row.get('away_score', 0) or 0
        if row['home_team_id'] == team_id:
            pts15.append(hs)
            allowed15.append(as_)
            home_games += 1
            if hs > as_:
                home_wins += 1
        else:
            pts15.append(as_)
            allowed15.append(hs)
            away_games += 1
            if as_ > hs:
                away_wins += 1

    if pts15:
        # Normalize to a 100-possession scale (NBA average ~100 possessions ≈ 98-100 pts)
        # Simple scaling: off_rtg ≈ pts_per_game / 1.1 * 100 / 100 (roughly)
        stats['off_rtg'] = np.mean(pts15)       # pts per game IS a good off_rtg proxy
        stats['def_rtg'] = np.mean(allowed15)   # pts allowed per game IS a good def_rtg proxy
        # Pace proxy: higher-scoring games = faster pace
        stats['pace'] = (np.mean(pts15) + np.mean(allowed15)) / 2.2

    stats['win_pct_home_only'] = (home_wins / home_games) if home_games > 0 else 0.500
    stats['win_pct_away_only'] = (away_wins / away_games) if away_games > 0 else 0.500

    return stats, last_game_date


def extract_features(games_df: pd.DataFrame, game_row: pd.Series) -> dict:
    feats = {f: 0.0 for f in FEATURE_NAMES}

    home_id = str(game_row.get('home_team_id', ''))
    away_id = str(game_row.get('away_team_id', ''))
    date_val = game_row.get('game_date', '')
    date_obj = pd.to_datetime(date_val) if date_val else pd.Timestamp.today()

    if games_df.empty:
        # Sensible defaults
        feats.update({
            'home_win_pct_L10': 0.500, 'away_win_pct_L10': 0.500,
            'home_rest_days': 2, 'away_rest_days': 2,
            'home_pts_L5': 110.0, 'away_pts_L5': 110.0,
            'home_pts_allowed_L5': 110.0, 'away_pts_allowed_L5': 110.0,
            'home_off_rtg': 113.0, 'away_off_rtg': 113.0,
            'home_def_rtg': 113.0, 'away_def_rtg': 113.0,
            'home_pace': 98.5, 'away_pace': 98.5,
            'is_b2b_away': 0, 'is_b2b_home': 0,
            'win_pct_diff': 0.0, 'rest_diff': 0.0, 'pts_diff': 0.0,
            'def_rtg_diff': 0.0, 'off_rtg_diff': 0.0, 'pace_avg': 98.5,
            'home_win_pct_home_only': 0.500, 'away_win_pct_away_only': 0.500,
        })
        return feats

    # Only look at games strictly before this game's date to avoid leakage
    past_games = games_df[pd.to_datetime(games_df['game_date']) < date_obj].copy()
    past_games['home_team_id'] = past_games['home_team_id'].astype(str)
    past_games['away_team_id'] = past_games['away_team_id'].astype(str)

    # --- Home Team ---
    home_result = _get_team_stats(past_games, home_id)
    if isinstance(home_result, tuple):
        home_stats, home_last_date = home_result
        home_rest = min((date_obj - home_last_date).days, 7)
    else:
        home_stats = home_result
        home_rest = 2

    feats['home_win_pct_L10'] = home_stats['win_pct_L10']
    feats['home_rest_days'] = home_rest
    feats['is_b2b_home'] = 1 if home_rest == 1 else 0
    feats['home_pts_L5'] = home_stats['pts_L5']
    feats['home_pts_allowed_L5'] = home_stats['pts_allowed_L5']
    feats['home_off_rtg'] = home_stats['off_rtg']
    feats['home_def_rtg'] = home_stats['def_rtg']
    feats['home_pace'] = home_stats['pace']
    feats['home_win_pct_home_only'] = home_stats['win_pct_home_only']

    # --- Away Team ---
    away_result = _get_team_stats(past_games, away_id)
    if isinstance(away_result, tuple):
        away_stats, away_last_date = away_result
        away_rest = min((date_obj - away_last_date).days, 7)
    else:
        away_stats = away_result
        away_rest = 2

    feats['away_win_pct_L10'] = away_stats['win_pct_L10']
    feats['away_rest_days'] = away_rest
    feats['is_b2b_away'] = 1 if away_rest == 1 else 0
    feats['away_pts_L5'] = away_stats['pts_L5']
    feats['away_pts_allowed_L5'] = away_stats['pts_allowed_L5']
    feats['away_off_rtg'] = away_stats['off_rtg']
    feats['away_def_rtg'] = away_stats['def_rtg']
    feats['away_pace'] = away_stats['pace']
    feats['away_win_pct_away_only'] = away_stats['win_pct_away_only']

    # --- Differential Features ---
    feats['win_pct_diff'] = feats['home_win_pct_L10'] - feats['away_win_pct_L10']
    feats['rest_diff'] = feats['home_rest_days'] - feats['away_rest_days']
    feats['pts_diff'] = feats['home_pts_L5'] - feats['away_pts_L5']
    feats['def_rtg_diff'] = feats['home_def_rtg'] - feats['away_def_rtg']
    feats['off_rtg_diff'] = feats['home_off_rtg'] - feats['away_off_rtg']
    feats['pace_avg'] = (feats['home_pace'] + feats['away_pace']) / 2

    return feats