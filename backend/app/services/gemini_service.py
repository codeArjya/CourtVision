from google import genai
from google.genai import types
import json
from app.config import settings

# ─── CLIENT SETUP ────────────────────────────────────────────────────
client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"

# ─── GAME PREDICTION ───────────────────────────────────────────────
PREDICTION_SYSTEM = """You are a sharp NBA analyst. Return ONLY valid JSON with these exact keys:
- winner: string (full team name)
- winner_abbr: string (3-letter abbreviation)
- confidence: integer between 55 and 88
- score_home: integer (predicted home team final score)
- score_away: integer (predicted away team final score)
- key_factors: array of exactly 3 strings, each under 15 words, specific and stat-based
No explanation. No markdown. Raw JSON object only."""

async def generate_prediction(game: dict) -> dict:
    user = f"""Game: {game['home_team_name']} (home) vs {game['away_team_name']} (away).
Home record: {game.get('home_record', 'N/A')}. Away record: {game.get('away_record', 'N/A')}.
Home last 5: {game.get('home_last5', 'W W L W L')}. Away last 5: {game.get('away_last5', 'L W W L W')}.
Home rest days: {game.get('home_rest', 2)}. Away rest days: {game.get('away_rest', 1)}."""
    return await _call_gemini(PREDICTION_SYSTEM, user)

# ─── PLAYER CARD ────────────────────────────────────────────────────
PLAYER_CARD_SYSTEM = """You are an NBA scout. Return ONLY valid JSON with these exact keys:
- report: string, exactly 3 sentences, specific and data-driven
- projection: object with keys pts, reb, ast (each a string range like "22-26", "8-11", "4-7")
- trend: string, must be exactly "hot", "cold", or "neutral"
No explanation. No markdown. Raw JSON object only."""

async def generate_player_card(data: dict) -> dict:
    user = f"""Player: {data['player_name']}.
Season averages: {data['season_avg'].get('pts', 'N/A')} PPG, {data['season_avg'].get('reb', 'N/A')} RPG, {data['season_avg'].get('ast', 'N/A')} APG.
Last 5 games (points): {', '.join(str(x) for x in data['last5'])}.
Tonight vs: {data['opponent']}."""
    return await _call_gemini(PLAYER_CARD_SYSTEM, user)

# ─── TAKE VERDICT ────────────────────────────────────────────────────
TAKE_VERDICT_SYSTEM = """You are a data-driven NBA analyst. Return ONLY valid JSON with these exact keys:
- steelman: string, exactly one sentence under 20 words, supports the take with a specific stat
- challenge: string, exactly one sentence under 20 words, pushes back with a specific counter-stat
- verdict_label: string, must be exactly "Backed by data", "Partially supported", or "Overblown"
No explanation. No markdown. Raw JSON object only."""

async def generate_take_verdict(take_text: str) -> dict:
    user = f'Media take: "{take_text}"'
    return await _call_gemini(TAKE_VERDICT_SYSTEM, user)

# ─── SHARED CALLER ───────────────────────────────────────────────────
async def _call_gemini(system: str, user: str) -> dict:
    try:
        response = await client.aio.models.generate_content(
            model=MODEL,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.7,
                response_mime_type="application/json",
            ),
        )
        text = response.text.strip()
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        print(f"[Gemini error] {e}")
        raise

# ─── CHAT STREAMING ──────────────────────────────────────────────────
CHAT_SYSTEM_INSTRUCTION = """You are CourtIQ, an expert AI basketball assistant. You provide concise, insightful, and data-driven answers about NBA news, player stats, and general basketball knowledge. Keep responses under 3 paragraphs. Be friendly, energetic, and talk like a sharp basketball analyst."""

async def generate_chat_stream(messages: list):
    # Build history for all messages except the last
    formatted_history = []
    for msg in messages[:-1]:
        role = "model" if msg.role == "assistant" else "user"
        formatted_history.append(
            types.Content(role=role, parts=[types.Part(text=msg.content)])
        )

    current_message = messages[-1].content

    try:
        chat = client.aio.chats.create(
            model=MODEL,
            history=formatted_history,
            config=types.GenerateContentConfig(
                system_instruction=CHAT_SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
        )
        async for chunk in await chat.send_message_stream(current_message):
            if chunk.text:
                yield chunk.text
    except Exception as e:
        print(f"[Gemini chat error] {e}")
        yield f"Sorry, something went wrong: {e}"