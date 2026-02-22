# backend/app/scripts/bootstrap_historical.py
from loguru import logger
import pandas as pd
from app.services.supabase_service import supabase_client

def bootstrap():
    logger.info("Bootstrapping historical data...")
    if not supabase_client:
        logger.error("No Supabase client")
        return

    from nba_api.stats.endpoints import leaguegamefinder
    
    # 3 seasons roughly back from 2025
    seasons = ['2023-24', '2024-25']
    
    all_games = []
    
    for season in seasons:
        logger.info(f"Fetching {season}...")
        try:
            gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season, league_id_nullable='00')
            df = gamefinder.get_data_frames()[0]
            # Regular season only
            df = df[df['SEASON_ID'].str.startswith('2')]
            all_games.append(df)
        except Exception as e:
            logger.error(f"Failed to fetch {season}: {e}")
            
    if not all_games:
        return
        
    full_df = pd.concat(all_games)
    
    # We need to pivot to game-level for the games table
    # This involves matching the home and away rows for the same GAME_ID
    
    logger.info(f"Loaded {len(full_df)} team-game logs. Shaping into game rows...")
    
    # Simple pairing hack since df has 2 rows per game
    games_dict = {}
    
    # Matchup usually looks like 'LAL vs. BOS' or 'LAL @ BOS'
    # 'vs.' means home, '@' means away
    
    for _, row in full_df.iterrows():
        gid = str(row['GAME_ID'])
        if gid not in games_dict:
            games_dict[gid] = {
                "game_id": gid,
                "game_date": row['GAME_DATE'],
                "status": "final"
            }
            
        matchup = row['MATCHUP']
        is_home = 'vs.' in matchup
        
        if is_home:
            games_dict[gid]['home_team_id'] = str(row['TEAM_ID'])
            games_dict[gid]['home_team_name'] = row['TEAM_NAME']
            games_dict[gid]['home_team_abbr'] = row['TEAM_ABBREVIATION']
            games_dict[gid]['home_score'] = int(row['PTS'])
        else:
            games_dict[gid]['away_team_id'] = str(row['TEAM_ID'])
            games_dict[gid]['away_team_name'] = row['TEAM_NAME']
            games_dict[gid]['away_team_abbr'] = row['TEAM_ABBREVIATION']
            games_dict[gid]['away_score'] = int(row['PTS'])

    # Filter out ones that didn't merge properly
    valid_games = [g for g in games_dict.values() if 'home_score' in g and 'away_score' in g]
    
    logger.info(f"Inserting {len(valid_games)} finalized games into Supabase games table...")
    
    batch_size = 500
    for i in range(0, len(valid_games), batch_size):
        batch = valid_games[i:i+batch_size]
        try:
            supabase_client.table("games").upsert(batch).execute()
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")
            
    logger.info("Historical bootstrap complete.")

if __name__ == "__main__":
    bootstrap()
