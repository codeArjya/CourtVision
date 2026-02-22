def run_retrain():
    from app.ml.train import train_and_save_model
    from app.ml.predict import load_model_artifacts
    from app.services.supabase_service import supabase_client
    from loguru import logger
    import pandas as pd
    
    logger.info("Starting schedule model retrain...")
    if not supabase_client:
        logger.error("No Supabase client configured. Cannot retrain.")
        return
        
    res = supabase_client.table("games").select("*").execute()
    if not res.data:
        logger.warning("No games found in database. Exiting retrain job.")
        return
        
    df = pd.DataFrame(res.data)
    
    # Needs scores to be labelled
    if 'home_score' in df.columns and 'away_score' in df.columns:
        df['winner'] = (df['home_score'] > df['away_score']).astype(int)
    
    result = train_and_save_model(df)
    if result and result.get("status") == "success":
        logger.info("Retraining successful. Reloading model artifacts in memory.")
        load_model_artifacts()
    else:
        logger.error("Retraining failed or returned no result.")
