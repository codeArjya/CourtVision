# backend/app/ml/features.py
import pandas as pd
import numpy as np

FEATURE_NAMES = [
    'home_win_pct_L10', 'away_win_pct_L10',
    'home_rest_days', 'away_rest_days',
    'home_pts_L5', 'away_pts_L5',
    'home_pts_allowed_L5', 'away_pts_allowed_L5',
    'home_off_rtg', 'away_off_rtg',
    'home_def_rtg', 'away_def_rtg',
    'home_pace', 'away_pace',
    'is_b2b_away', 'is_b2b_home',
    'win_pct_diff',
    'rest_diff',
    'pts_diff',
    'def_rtg_diff',
    'off_rtg_diff',
    'pace_avg',
    'home_win_pct_home_only',
    'away_win_pct_away_only',
]

# BUG FIX 2: League-average defaults that reflect real NBA baselines.
# All-zero differentials put predictions in a model region that happens to
# favour away teams. Using realistic baselines (home teams win ~59% at home,
# away teams win ~41% on road) gives the model the right prior when data is
# sparse, and produces the correct slight home-court-advantage lean.
_HOME_DEFAULTS = {
    'win_pct_L10':       0.550,   # home teams win slightly more often
    'pts_L5':            114.0,   # 2024-25 NBA avg ~114 pts/game
    'pts_allowed_L5':    112.0,
    'off_rtg':           114.0,
    'def_rtg':           112.0,
    'pace':               98.5,
    'win_pct_home_only': 0.590,   # historical home win% ~59%
    'win_pct_away_only': 0.410,
    'is_b2b':            0,
}

_AWAY_DEFAULTS = {
    'win_pct_L10':       0.450,
    'pts_L5':            112.0,
    'pts_allowed_L5':    114.0,
    'off_rtg':           112.0,
    'def_rtg':           114.0,
    'pace':               98.5,
    'win_pct_home_only': 0.590,
    'win_pct_away_only': 0.410,
    'is_b2b':            0,
}


def _get_team_stats(past_games: pd.DataFrame, team_id: str, defaults: dict):
    """
    Compute rolling stats for a team from their past completed games.
    Only uses rows where both scores are present and non-zero (i.e. game finished).
    Returns (stats_dict, last_game_date) or (defaults, None) if no data found.
    """
    team_games = past_games[
        (past_games['home_team_id'] == team_id) |
        (past_games['away_team_id'] == team_id)
    ].sort_values('game_date', ascending=False)

    if team_games.empty:
        return dict(defaults), None

    # BUG FIX 1: Filter to only COMPLETED games (both scores present and > 0).
    # Without this, unstarted games (score=NULL or 0) corrupt win% and pts averages
    # because None is treated as 0, making every game look like a 0-0 tie.
    completed = team_games[
        team_games['home_score'].notna() &
        team_games['away_score'].notna() &
        (team_games['home_score'].astype(float) > 0) &
        (team_games['away_score'].astype(float) > 0)
    ]

    if completed.empty:
        return dict(defaults), pd.to_datetime(team_games.iloc[0]['game_date'])

    last_game_date = pd.to_datetime(completed.iloc[0]['game_date'])
    stats = dict(defaults)  # start from defaults, override with real values

    # L10 win %
    last10 = completed.head(10)
    wins = 0
    for _, row in last10.iterrows():
        hs  = float(row.get('home_score') or 0)
        aws = float(row.get('away_score') or 0)
        if row['home_team_id'] == team_id and hs > aws:
            wins += 1
        elif row['away_team_id'] == team_id and aws > hs:
            wins += 1
    stats['win_pct_L10'] = wins / len(last10)

    # L5 scoring
    last5 = completed.head(5)
    pts_list, allowed_list = [], []
    for _, row in last5.iterrows():
        hs  = float(row.get('home_score') or 0)
        aws = float(row.get('away_score') or 0)
        if row['home_team_id'] == team_id:
            pts_list.append(hs)
            allowed_list.append(aws)
        else:
            pts_list.append(aws)
            allowed_list.append(hs)

    if pts_list:
        stats['pts_L5']         = float(np.mean(pts_list))
        stats['pts_allowed_L5'] = float(np.mean(allowed_list))

    # L15 ratings + home/away splits
    last15 = completed.head(15)
    pts15, allowed15 = [], []
    home_wins, home_games, away_wins, away_games = 0, 0, 0, 0

    for _, row in last15.iterrows():
        hs  = float(row.get('home_score') or 0)
        aws = float(row.get('away_score') or 0)
        if row['home_team_id'] == team_id:
            pts15.append(hs)
            allowed15.append(aws)
            home_games += 1
            if hs > aws:
                home_wins += 1
        else:
            pts15.append(aws)
            allowed15.append(hs)
            away_games += 1
            if aws > hs:
                away_wins += 1

    if pts15:
        stats['off_rtg'] = float(np.mean(pts15))
        stats['def_rtg'] = float(np.mean(allowed15))
        stats['pace']    = float((np.mean(pts15) + np.mean(allowed15)) / 2.2)

    stats['win_pct_home_only'] = (home_wins / home_games) if home_games > 0 else defaults['win_pct_home_only']
    stats['win_pct_away_only'] = (away_wins / away_games) if away_games > 0 else defaults['win_pct_away_only']

    return stats, last_game_date


def extract_features(games_df: pd.DataFrame, game_row: pd.Series) -> dict:
    feats = {f: 0.0 for f in FEATURE_NAMES}

    home_id  = str(game_row.get('home_team_id', ''))
    away_id  = str(game_row.get('away_team_id', ''))
    date_val = game_row.get('game_date', '')
    date_obj = pd.to_datetime(date_val) if date_val else pd.Timestamp.today()

    if games_df.empty:
        # Apply asymmetric defaults so model produces realistic home-favoured prior
        feats.update({
            'home_win_pct_L10':      _HOME_DEFAULTS['win_pct_L10'],
            'away_win_pct_L10':      _AWAY_DEFAULTS['win_pct_L10'],
            'home_rest_days':        2,
            'away_rest_days':        2,
            'home_pts_L5':           _HOME_DEFAULTS['pts_L5'],
            'away_pts_L5':           _AWAY_DEFAULTS['pts_L5'],
            'home_pts_allowed_L5':   _HOME_DEFAULTS['pts_allowed_L5'],
            'away_pts_allowed_L5':   _AWAY_DEFAULTS['pts_allowed_L5'],
            'home_off_rtg':          _HOME_DEFAULTS['off_rtg'],
            'away_off_rtg':          _AWAY_DEFAULTS['off_rtg'],
            'home_def_rtg':          _HOME_DEFAULTS['def_rtg'],
            'away_def_rtg':          _AWAY_DEFAULTS['def_rtg'],
            'home_pace':             _HOME_DEFAULTS['pace'],
            'away_pace':             _AWAY_DEFAULTS['pace'],
            'is_b2b_away':           0,
            'is_b2b_home':           0,
            'win_pct_diff':          _HOME_DEFAULTS['win_pct_L10'] - _AWAY_DEFAULTS['win_pct_L10'],
            'rest_diff':             0.0,
            'pts_diff':              _HOME_DEFAULTS['pts_L5'] - _AWAY_DEFAULTS['pts_L5'],
            'def_rtg_diff':          _HOME_DEFAULTS['def_rtg'] - _AWAY_DEFAULTS['def_rtg'],
            'off_rtg_diff':          _HOME_DEFAULTS['off_rtg'] - _AWAY_DEFAULTS['off_rtg'],
            'pace_avg':              _HOME_DEFAULTS['pace'],
            'home_win_pct_home_only': _HOME_DEFAULTS['win_pct_home_only'],
            'away_win_pct_away_only': _AWAY_DEFAULTS['win_pct_away_only'],
        })
        return feats

    # Only look at games strictly before this game's date to avoid data leakage
    past_games = games_df[pd.to_datetime(games_df['game_date']) < date_obj].copy()
    past_games['home_team_id'] = past_games['home_team_id'].astype(str)
    past_games['away_team_id'] = past_games['away_team_id'].astype(str)

    # ── Home team ────────────────────────────────────────────────────────────
    home_stats, home_last_date = _get_team_stats(past_games, home_id, _HOME_DEFAULTS)
    home_rest = min((date_obj - home_last_date).days, 7) if home_last_date else 2

    feats['home_win_pct_L10']     = home_stats['win_pct_L10']
    feats['home_rest_days']       = home_rest
    feats['is_b2b_home']          = 1 if home_rest == 1 else 0
    feats['home_pts_L5']          = home_stats['pts_L5']
    feats['home_pts_allowed_L5']  = home_stats['pts_allowed_L5']
    feats['home_off_rtg']         = home_stats['off_rtg']
    feats['home_def_rtg']         = home_stats['def_rtg']
    feats['home_pace']            = home_stats['pace']
    feats['home_win_pct_home_only'] = home_stats['win_pct_home_only']

    # ── Away team ────────────────────────────────────────────────────────────
    away_stats, away_last_date = _get_team_stats(past_games, away_id, _AWAY_DEFAULTS)
    away_rest = min((date_obj - away_last_date).days, 7) if away_last_date else 2

    feats['away_win_pct_L10']     = away_stats['win_pct_L10']
    feats['away_rest_days']       = away_rest
    feats['is_b2b_away']          = 1 if away_rest == 1 else 0
    feats['away_pts_L5']          = away_stats['pts_L5']
    feats['away_pts_allowed_L5']  = away_stats['pts_allowed_L5']
    feats['away_off_rtg']         = away_stats['off_rtg']
    feats['away_def_rtg']         = away_stats['def_rtg']
    feats['away_pace']            = away_stats['pace']
    feats['away_win_pct_away_only'] = away_stats['win_pct_away_only']

    # ── Differentials ────────────────────────────────────────────────────────
    feats['win_pct_diff'] = feats['home_win_pct_L10']   - feats['away_win_pct_L10']
    feats['rest_diff']    = feats['home_rest_days']      - feats['away_rest_days']
    feats['pts_diff']     = feats['home_pts_L5']         - feats['away_pts_L5']
    feats['def_rtg_diff'] = feats['home_def_rtg']        - feats['away_def_rtg']
    feats['off_rtg_diff'] = feats['home_off_rtg']        - feats['away_off_rtg']
    feats['pace_avg']     = (feats['home_pace'] + feats['away_pace']) / 2

    return feats