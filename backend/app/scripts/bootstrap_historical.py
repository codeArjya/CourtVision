import time
from loguru import logger
from datetime import datetime, timedelta
from app.services.supabase_service import supabase_client
from app.config import settings

def bootstrap_historical(seasons_back: int = 3):
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return
        
    logger.info(f"Looking back {seasons_back} seasons for historical data bootstrap")
    from nba_api.stats.endpoints import leaguegamefinder
    
    # NBA API has standard season formats like 2023-24
    # Simple date math to grab older seasons
    current_year = datetime.now().year
    
    total_inserted = 0
    for s in range(seasons_back):
        start = current_year - s - 1
        end = str(current_year - s)[-2:]
        season_str = f"{start}-{end}"
        
        logger.info(f"Fetching season {season_str} from NBA API...")
        try:
            # 00 represents NBA regular season prefix for Game_ID
            gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season_str, league_id_nullable='00')
            games = gamefinder.get_data_frames()[0]
            
            # Format to DB payload (Games)
            if not games.empty:
                logger.info(f"Found {len(games)} team-games in season {season_str}")
                formatted = []
                for _, row in games.iterrows():
                    matchup = row['MATCHUP']
                    if ' vs. ' in matchup:
                        # Home game
                        home_id = row['TEAM_ID']
                        away_abbr = matchup.split(' vs. ')[1]
                        home_score = row['PTS']
                        # Away score must be derived by matching pairing or ignoring for raw mock
                        formatted.append({
                            "game_id": str(row['GAME_ID']),
                            "date": row['GAME_DATE'],
                            "home_id": str(home_id),
                            "away_abbr": away_abbr, # Needs join mapping or second pass logic in complete impl
                            "status": "final",
                            "home_score": home_score,
                            # Approximate away score based on +/-  if available
                            "away_score": home_score - row.get('PLUS_MINUS', 0)
                        })
                
                # Batch upsert mapped chunks
                chunk_size = 500
                for i in range(0, len(formatted), chunk_size):
                    chunk = formatted[i:i + chunk_size]
                    supabase_client.table("games").upsert(chunk).execute()
                    total_inserted += len(chunk)
                    
            time.sleep(settings.NBA_API_DELAY)
        except Exception as e:
            logger.error(f"Failed pulling historical season {season_str}: {e}")
            
    logger.info(f"Successfully bootstrapped {total_inserted} games.")

if __name__ == "__main__":
    bootstrap_historical()
