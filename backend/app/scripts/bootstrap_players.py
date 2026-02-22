import time
import requests
from loguru import logger
from app.services.supabase_service import supabase_client

def bootstrap():
    if not supabase_client:
        logger.error("Supabase client not initialized")
        return
        
    logger.info("Bootstrapping players from balldontlie via REST API")
    url = "https://www.balldontlie.io/api/v1/players?per_page=100"
    
    # balldontlie API structure: metadata contains total_pages
    try:
        page = 1
        total_players = 0
        while True:
            logger.info(f"Fetching page {page}")
            resp = requests.get(f"{url}&page={page}")
            
            if resp.status_code != 200:
                logger.error(f"Failed pulling from {url}. Status: {resp.status_code}")
                break
                
            data = resp.json()
            players = data.get("data", [])
            meta = data.get("meta", {})
            
            if not players:
                break
                
            formatted = []
            for p in players:
                formatted.append({
                    "player_id": str(p["id"]),
                    "name": f"{p['first_name']} {p['last_name']}".strip(),
                    "position": p.get("position", ""),
                    "team_id": str(p["team"]["id"]) if "team" in p else None
                })
                
            # Upsert
            try:
                supabase_client.table("players").upsert(formatted).execute()
                total_players += len(formatted)
            except Exception as e:
                logger.error(f"Failed upserting block: {e}")
                
            if page >= meta.get("total_pages", page):
                break
                
            page += 1
            time.sleep(1) # simple rate limit respect
            
        logger.info(f"Successfully bootstrapped {total_players} players")
    except Exception as e:
        logger.exception("Bootstrap script failed unexpectedly")
        
if __name__ == "__main__":
    bootstrap()
