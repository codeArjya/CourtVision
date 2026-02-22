# 🏀 CourtIQ — Ball Knowledge AI

NBA live stats dashboard + AI predictions + media takes feed.

**Stack:** Next.js 14 · FastAPI · Gemini 1.5 Flash · Supabase · balldontlie

---

## 1. Supabase Setup

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the full SQL block from `Section 5` of `prompt.md`
3. Copy your **Project URL** and **service_role key** from Settings → API

---

## 2. Environment Variables

### Backend

```bash
cp backend/.env.example backend/.env
# Fill in GEMINI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY
```

### Frontend

```bash
cp frontend/.env.local.example frontend/.env.local
# Fill in NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
```

---

## 3. Seed Demo Data

```bash
cd backend
python -m app.data.seed_mock
```

---

## 4. Local Development

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000  
Health check: http://localhost:8000/health

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

---

## 5. Deployment

### Backend → Railway

1. Push to GitHub
2. Create new Railway project → connect repo → set root to `backend/`
3. Set env vars: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
4. Railway auto-detects `railway.toml` and runs uvicorn

### Frontend → Vercel

1. Create Vercel project → connect repo → set root to `frontend/`
2. Set env vars: `NEXT_PUBLIC_API_URL` (your Railway URL), `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. Update `frontend/vercel.json` with your Railway URL
4. Deploy

---

## 6. API Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Health check |
| GET | `/api/games` | Today's NBA games |
| GET | `/api/predictions/{game_id}` | AI prediction for a game |
| POST | `/api/player-card` | AI scouting report for a player |
| POST | `/api/takes/verdict` | AI verdict on a media take |
| POST | `/api/takes/vote` | Vote agree/disagree on a take |

---

## 7. Demo Path

1. `/` → LAL vs BOS with LIVE badge
2. Click game → GameExpanded box score
3. Toggle League Rank overlay → `#4 PTS` pill on LeBron
4. Toggle Form overlay → Recharts sparklines
5. Click LeBron → PlayerModal with AI scouting card
6. `/predictions` → 3 cards with SVG confidence gauges
7. `/takes` → 8 media takes feed
8. Click AI Verdict on Stephen A. take → AIVerdictBox
