# backend/app/scripts/bootstrap_players.py
import pandas as pd
from loguru import logger
from app.services.supabase_service import supabase_client
from nba_api.stats.endpoints import commonallplayers

def bootstrap():
    logger.info("Bootstrapping players data...")
    if not supabase_client:
        logger.error("No Supabase client")
        return

    try:
        players_api = commonallplayers.CommonAllPlayers(is_only_current_season=1)
        df = players_api.get_data_frames()[0]
        logger.info(f"Found {len(df)} active players.")

        players_to_insert = []
        for _, row in df.iterrows():
            team_id = str(int(row["TEAM_ID"])) if pd.notnull(row["TEAM_ID"]) and int(row["TEAM_ID"]) != 0 else None
            players_to_insert.append({
                "player_id": str(row["PERSON_ID"]),
                "name": row["DISPLAY_FIRST_LAST"],
                "team_id": team_id,  # None for free agents — avoids FK violation
                "status": "active",
            })

        logger.info("Inserting into Supabase players table...")

        batch_size = 500
        for i in range(0, len(players_to_insert), batch_size):
            batch = players_to_insert[i : i + batch_size]
            try:
                supabase_client.table("players").upsert(batch).execute()
                logger.info(f"Inserted batch {i // batch_size + 1}")
            except Exception as e:
                logger.error(f"Failed to upsert batch {i // batch_size + 1}: {e}")

        logger.info("Player bootstrap complete.")

    except Exception as e:
        logger.error(f"Failed to bootstrap players: {e}")

if __name__ == "__main__":
    bootstrap()