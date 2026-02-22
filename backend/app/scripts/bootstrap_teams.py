# backend/app/scripts/bootstrap_teams.py
import sys
import os
# Ensure the backend/ directory is on the path regardless of where script is run from
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from loguru import logger
from app.services.supabase_service import supabase_client
from nba_api.stats.static import teams as nba_teams

def bootstrap():
    logger.info("Bootstrapping teams data...")
    if not supabase_client:
        logger.error("No Supabase client")
        return

    try:
        all_teams = nba_teams.get_teams()
        logger.info(f"Found {len(all_teams)} teams.")

        teams_to_insert = [
            {
                "team_id": str(t["id"]),
                "name": t["full_name"],
                "abbr": t["abbreviation"],
            }
            for t in all_teams
        ]

        # Log a sample so we can confirm the shape looks right
        logger.info(f"Sample team row: {teams_to_insert[0]}")

        result = supabase_client.table("teams").upsert(teams_to_insert).execute()
        logger.info(f"Upsert response: {result}")

        # Verify rows actually landed
        count_result = supabase_client.table("teams").select("team_id", count="exact").execute()
        logger.info(f"Teams now in DB: {count_result.count}")
        logger.info("Teams bootstrap complete.")

    except Exception as e:
        # Use exception() instead of error() so the full traceback is printed
        logger.exception(f"Failed to bootstrap teams: {e}")

if __name__ == "__main__":
    bootstrap()