import pandas as pd

def compute_rolling_features(df: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    """
    Computes rolling averages for teams based on their last `window` games.
    Assumes df is sorted by date ascending.
    """
    df = df.copy()
    
    # We need a unified team-game view to compute rolling stats properly
    # This involves melting the game data but for simplicity here's a generic approach
    # assuming we get a dataframe of team_game_stats
    
    # We will compute: off_rtg_l10, def_rtg_l10, win_pct_l10, pace_l10
    
    # In a real app we'd join games to get win/loss. For this MVP we just need 
    # to roll the columns that exist in team_game_stats
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['team_id', 'date'])

    # Rolling win pct (assuming 'won' is a boolean or 1/0)
    if 'won' in df.columns:
        df['win_pct_l10'] = df.groupby('team_id')['won'].transform(lambda x: x.shift().rolling(window, min_periods=1).mean())
    else:
        df['win_pct_l10'] = 0.5  # safe default

    # Rolling stats
    cols_to_roll = ['off_rtg', 'def_rtg', 'pace']
    for col in cols_to_roll:
        if col in df.columns:
            df[f'{col}_l10'] = df.groupby('team_id')[col].transform(lambda x: x.shift().rolling(window, min_periods=1).mean())

    # Forward fill any NaNs from the beginning of the series, then backfill
    df = df.fillna(method='bfill')
    
    return df

def generate_training_data(games_df: pd.DataFrame, team_stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge games with computing rolling features to create the training set.
    """
    # Merge home stats
    home_stats = team_stats_df.copy()
    home_stats = home_stats.add_prefix('home_')
    home_stats = home_stats.rename(columns={'home_game_id': 'game_id', 'home_team_id': 'home_id'})

    # Merge away stats
    away_stats = team_stats_df.copy()
    away_stats = away_stats.add_prefix('away_')
    away_stats = away_stats.rename(columns={'away_game_id': 'game_id', 'away_team_id': 'away_id'})

    # Join
    merged = pd.merge(games_df, home_stats, on=['game_id', 'home_id'], how='inner')
    merged = pd.merge(merged, away_stats, on=['game_id', 'away_id'], how='inner')

    # Basic features
    merged['winner'] = (merged['home_score'] > merged['away_score']).astype(int)
    
    # Rest days is tricky without full schedule, so defaulting to 2 days average if not available
    merged['home_rest_days'] = 2
    merged['away_rest_days'] = 2
    
    merged['h2h_home_win_pct'] = 0.5
    merged['home_inj_min_pct'] = 0.0
    merged['away_inj_min_pct'] = 0.0

    return merged
