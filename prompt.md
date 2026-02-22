Create the hackathon web app CourtIQ exactly as specified below, with zero follow-up questions, using the exact tech stack versions, creating every file in the specified file tree, implementing all backend routes, frontend routes/pages/components, Supabase schema + RLS policies, mock/seed data, and deployment files, with all sections preserved in this exact order and all blocks marked EXACT reproduced character-for-character.

---

# COURTIQ — COMPLETE TECHNICAL SPECIFICATION v2
### Basketball Ball Knowledge AI | 2-Day Hackathon | 4-Person Team
### Stack: Next.js + FastAPI + Gemini API + Supabase + balldontlie

---

## 1. PROJECT IDENTITY

| Field | Value |
|---|---|
| App Name | CourtIQ |
| Tagline | Ball Knowledge AI |
| Purpose | NBA live stats dashboard + AI predictions + media takes feed |
| Build Target | Deployed Next.js web app + FastAPI backend, functional at a live Vercel URL |
| Time Budget | 48 hours, 4 devs |
| Demo Duration | 3 minutes |

---

## 2. EXACT TECH STACK (NO SUBSTITUTIONS)

### Frontend
```
next@14.2.5
react@18.3.1
react-dom@18.3.1
typescript@5.4.5
tailwindcss@3.4.4
autoprefixer@10.4.19
postcss@8.4.38
recharts@2.12.7
@tanstack/react-query@5.40.0
axios@1.7.2
```

### Backend
```
python 3.11
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.4
httpx==0.27.0
python-dotenv==1.0.1
supabase==2.5.0
google-generativeai==0.7.2
redis==5.0.6      # for Upstash Redis via REST
```

### AI
```
Provider: Google Gemini API
Model: gemini-1.5-flash
SDK: google-generativeai (Python)
Free tier: 15 requests/min, 1,000,000 tokens/day — NO CREDIT CARD REQUIRED
Get key: https://aistudio.google.com/app/apikey
```

### NBA Data
```
Primary (live): balldontlie.io REST API — FREE, no API key on free tier
  Base URL: https://api.balldontlie.io/v1
  Rate limit: 60 requests/minute
  Use for: live game scores, today's schedule, basic box scores

Secondary (historical/deep): nba_api Python package
  pip install nba_api
  No API key required — reads stats.nba.com
  Use for: advanced stats, player season averages, last-N-game logs
  Built-in rate limit: 0.6s between calls
  ALL results written to Supabase immediately after fetch — never call twice
```

### Database
```
Primary: Supabase (PostgreSQL)
  Free tier: 500MB, unlimited API calls, real-time subscriptions
  Python SDK: supabase==2.5.0
  JS SDK: @supabase/supabase-js@2.43.5

Cache: Upstash Redis (optional but recommended)
  Free tier: 10,000 commands/day, 256MB
  Use REST API — no additional library needed
  TTLs: live game data 30s, predictions 3600s, player cards 86400s
```

### Deployment
```
Frontend: Vercel (free hobby tier — unlimited)
Backend: Railway (free $5 credit/month) OR Render (free tier, slower cold start)
Database: supabase.com (free project)
Cache: upstash.com (free account)
```

---

## 3. COMPLETE FILE TREE (CREATE ALL FILES)

```
courtiq/
├── frontend/                              # Next.js 14 App Router
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── next.config.ts
│   ├── .env.local.example
│   └── src/
│       ├── app/
│       │   ├── layout.tsx                 # Root layout: Navbar + dark bg
│       │   ├── page.tsx                   # Dashboard → /
│       │   ├── predictions/
│       │   │   └── page.tsx               # Predictions → /predictions
│       │   ├── takes/
│       │   │   └── page.tsx               # Takes → /takes
│       │   └── globals.css                # Tailwind + custom vars + scrollbar
│       ├── components/
│       │   ├── layout/
│       │   │   └── Navbar.tsx
│       │   ├── dashboard/
│       │   │   ├── GameCard.tsx
│       │   │   ├── GameExpanded.tsx
│       │   │   ├── BoxScoreTable.tsx
│       │   │   ├── PlayerRow.tsx
│       │   │   ├── OverlaySelector.tsx
│       │   │   └── Sparkline.tsx
│       │   ├── predictions/
│       │   │   ├── PredictionCard.tsx
│       │   │   └── ConfidenceGauge.tsx
│       │   ├── players/
│       │   │   └── PlayerModal.tsx
│       │   ├── takes/
│       │   │   ├── TakesFeed.tsx
│       │   │   ├── TakeCard.tsx
│       │   │   └── AIVerdictBox.tsx
│       │   └── ui/
│       │       ├── Badge.tsx
│       │       ├── LoadingSpinner.tsx
│       │       ├── LoadingSkeleton.tsx
│       │       └── ErrorBanner.tsx
│       ├── lib/
│       │   ├── api.ts                     # Axios client pointing to FastAPI
│       │   ├── supabase.ts                # Supabase JS client
│       │   ├── mockData.ts                # ALL fallback mock data
│       │   └── queryClient.ts             # React Query client config
│       └── styles/
│           └── tokens.ts                  # Design token constants (TS)
│
├── backend/                               # FastAPI Python
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── railway.toml
│   └── app/
│       ├── main.py                        # FastAPI app entry
│       ├── config.py                      # Settings from env vars
│       ├── routes/
│       │   ├── games.py                   # GET /api/games
│       │   ├── predictions.py             # GET /api/predictions/{game_id}
│       │   ├── player_card.py             # POST /api/player-card
│       │   └── takes.py                   # POST /api/takes/verdict
│       ├── services/
│       │   ├── nba_service.py             # balldontlie + nba_api wrapper
│       │   ├── gemini_service.py          # All Gemini API calls
│       │   └── supabase_service.py        # DB reads/writes + cache checks
│       └── data/
│           └── seed_mock.py               # Run once to seed Supabase
│
├── .gitignore
└── README.md
```

Create any additional minimal support files needed for correctness (e.g., a React Query provider component file) but do not remove or rename any file listed above. Ensure all listed files exist.

---

## 4. DESIGN TOKENS — EXACT (REPRODUCE VERBATIM)

```typescript
// frontend/src/styles/tokens.ts
export const COLORS = {
  bg:           '#0D0D0D',
  surface:      '#1A1A1A',
  surfaceHigh:  '#242424',
  border:       '#2E2E2E',
  orange:       '#E87722',
  orangeLight:  '#FF9A45',
  orangeDim:    '#3D2200',
  white:        '#F0F0F0',
  gray:         '#9A9A9A',
  grayDim:      '#555555',
  green:        '#27AE60',
  red:          '#E74C3C',
  yellow:       '#F1C40F',
} as const;
```

```typescript
// tailwind.config.ts — EXACT
import type { Config } from 'tailwindcss';
const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:            '#0D0D0D',
        surface:       '#1A1A1A',
        surfaceHigh:   '#242424',
        border:        '#2E2E2E',
        orange:        '#E87722',
        'orange-light':'#FF9A45',
        'orange-dim':  '#3D2200',
        primary:       '#F0F0F0',
        secondary:     '#9A9A9A',
        dim:           '#555555',
        success:       '#27AE60',
        danger:        '#E74C3C',
        warn:          '#F1C40F',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-live': 'pulse 1.5s cubic-bezier(0.4,0,0.6,1) infinite',
      }
    },
  },
  plugins: [],
};
export default config;
```

```css
/* frontend/src/app/globals.css — EXACT */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

* { box-sizing: border-box; }
html, body { background-color: #0D0D0D; color: #F0F0F0; font-family: 'Inter', sans-serif; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #1A1A1A; }
::-webkit-scrollbar-thumb { background: #E87722; border-radius: 2px; }
.glow-orange { box-shadow: 0 0 20px rgba(232,119,34,0.25); }
.border-orange-glow { border-color: #E87722; box-shadow: 0 0 8px rgba(232,119,34,0.4); }
```

---

## 5. SUPABASE SCHEMA — CREATE ALL TABLES

Run these SQL statements in Supabase SQL editor on project creation. Enable RLS on all tables with a public read+write policy for hackathon (no auth needed).

```sql
-- EXACT SQL TO RUN IN SUPABASE

create table teams (
  team_id text primary key,
  name text not null,
  abbr text not null,
  conference text,
  division text,
  win_count int default 0,
  loss_count int default 0,
  off_rtg float,
  def_rtg float,
  pace float,
  updated_at timestamptz default now()
);

create table players (
  player_id text primary key,
  name text not null,
  team_id text references teams(team_id),
  position text,
  status text default 'active',
  season_avg jsonb,
  updated_at timestamptz default now()
);

create table games (
  game_id text primary key,
  game_date date not null,
  home_team_id text,
  away_team_id text,
  home_team_name text,
  away_team_name text,
  home_team_abbr text,
  away_team_abbr text,
  home_score int,
  away_score int,
  status text,   -- 'upcoming', 'live', 'final'
  quarter int,
  clock text,
  tipoff_time text,
  updated_at timestamptz default now()
);

create table player_game_stats (
  id bigint generated always as identity primary key,
  player_id text,
  game_id text,
  team_id text,
  pts int, reb int, ast int, stl int, blk int,
  turnovers int, fgm int, fga int, fg_pct float,
  plus_minus int, minutes text,
  last5_pts int[],
  league_rank_pts int,
  league_rank_reb int,
  league_rank_ast int,
  matchup_avg_pts float,
  updated_at timestamptz default now(),
  unique(player_id, game_id)
);

create table predictions (
  game_id text primary key,
  winner text,
  winner_abbr text,
  confidence int,
  score_home int,
  score_away int,
  key_factors jsonb,
  result text,   -- 'pending', 'correct', 'incorrect'
  created_at timestamptz default now()
);

create table player_cards (
  id bigint generated always as identity primary key,
  player_id text,
  game_id text,
  report text,
  projection jsonb,
  trend text,
  created_at timestamptz default now(),
  unique(player_id, game_id)
);

create table media_takes (
  id text primary key,
  personality text not null,
  outlet text not null,
  outlet_color text,
  avatar text,
  take_text text not null,
  category text,
  agrees int default 0,
  disagrees int default 0,
  created_at timestamptz default now()
);

create table take_verdicts (
  take_id text primary key references media_takes(id),
  steelman text,
  challenge text,
  verdict_label text,
  created_at timestamptz default now()
);

-- RLS: allow all for hackathon
alter table teams enable row level security;
alter table players enable row level security;
alter table games enable row level security;
alter table player_game_stats enable row level security;
alter table predictions enable row level security;
alter table player_cards enable row level security;
alter table media_takes enable row level security;
alter table take_verdicts enable row level security;

create policy "allow_all" on teams for all using (true) with check (true);
create policy "allow_all" on players for all using (true) with check (true);
create policy "allow_all" on games for all using (true) with check (true);
create policy "allow_all" on player_game_stats for all using (true) with check (true);
create policy "allow_all" on predictions for all using (true) with check (true);
create policy "allow_all" on player_cards for all using (true) with check (true);
create policy "allow_all" on media_takes for all using (true) with check (true);
create policy "allow_all" on take_verdicts for all using (true) with check (true);
```

---

## 6. MOCK / SEED DATA — EMBED IN FULL (EXACT)

This data is used in three places: (1) inserted into Supabase via `seed_mock.py`, (2) exported from `frontend/src/lib/mockData.ts` as TypeScript constants for offline fallback, (3) referenced directly in backend fallback responses.

```typescript
// frontend/src/lib/mockData.ts — EXACT (also mirror in backend/app/data/seed_mock.py as Python dicts)

export const MOCK_GAMES = [
  {
    game_id: "game_001",
    game_date: "2025-02-21",
    status: "live",
    quarter: 3,
    clock: "4:22",
    home_team_id: "lakers",
    home_team_name: "Los Angeles Lakers",
    home_team_abbr: "LAL",
    home_score: 87,
    away_team_id: "celtics",
    away_team_name: "Boston Celtics",
    away_team_abbr: "BOS",
    away_score: 82,
    tipoff_time: null
  },
  {
    game_id: "game_002",
    game_date: "2025-02-21",
    status: "upcoming",
    quarter: null,
    clock: null,
    home_team_id: "warriors",
    home_team_name: "Golden State Warriors",
    home_team_abbr: "GSW",
    home_score: null,
    away_team_id: "nuggets",
    away_team_name: "Denver Nuggets",
    away_team_abbr: "DEN",
    away_score: null,
    tipoff_time: "7:30 PM ET"
  },
  {
    game_id: "game_003",
    game_date: "2025-02-21",
    status: "final",
    quarter: 4,
    clock: "0:00",
    home_team_id: "heat",
    home_team_name: "Miami Heat",
    home_team_abbr: "MIA",
    home_score: 109,
    away_team_id: "bucks",
    away_team_name: "Milwaukee Bucks",
    away_team_abbr: "MIL",
    away_score: 103,
    tipoff_time: null
  }
];

export const MOCK_PLAYER_STATS = [
  { player_id: "p001", game_id: "game_001", team_id: "lakers", name: "LeBron James", pos: "SF", minutes: "28:14", pts: 24, reb: 8, ast: 7, stl: 2, blk: 1, turnovers: 2, fgm: 9, fga: 17, plus_minus: 7, last5_pts: [28,31,22,26,19], league_rank_pts: 4, league_rank_reb: null, league_rank_ast: 8, matchup_avg_pts: 28.4 },
  { player_id: "p002", game_id: "game_001", team_id: "lakers", name: "Anthony Davis", pos: "C", minutes: "29:01", pts: 22, reb: 11, ast: 2, stl: 1, blk: 3, turnovers: 1, fgm: 9, fga: 14, plus_minus: 9, last5_pts: [18,24,27,21,30], league_rank_pts: 9, league_rank_reb: 5, league_rank_ast: null, matchup_avg_pts: 19.2 },
  { player_id: "p003", game_id: "game_001", team_id: "lakers", name: "D'Angelo Russell", pos: "PG", minutes: "25:33", pts: 14, reb: 3, ast: 6, stl: 1, blk: 0, turnovers: 3, fgm: 5, fga: 12, plus_minus: -2, last5_pts: [11,17,8,20,14], league_rank_pts: null, league_rank_reb: null, league_rank_ast: 19, matchup_avg_pts: 12.1 },
  { player_id: "p004", game_id: "game_001", team_id: "lakers", name: "Austin Reaves", pos: "SG", minutes: "24:10", pts: 10, reb: 4, ast: 3, stl: 0, blk: 0, turnovers: 1, fgm: 4, fga: 9, plus_minus: 5, last5_pts: [8,12,15,7,10], league_rank_pts: null, league_rank_reb: null, league_rank_ast: null, matchup_avg_pts: 9.8 },
  { player_id: "p005", game_id: "game_001", team_id: "lakers", name: "Rui Hachimura", pos: "PF", minutes: "18:44", pts: 7, reb: 5, ast: 1, stl: 0, blk: 1, turnovers: 0, fgm: 3, fga: 7, plus_minus: 3, last5_pts: [9,5,11,8,4], league_rank_pts: null, league_rank_reb: null, league_rank_ast: null, matchup_avg_pts: 7.0 },
  { player_id: "p006", game_id: "game_001", team_id: "celtics", name: "Jayson Tatum", pos: "SF", minutes: "29:55", pts: 21, reb: 7, ast: 4, stl: 1, blk: 2, turnovers: 2, fgm: 8, fga: 18, plus_minus: -3, last5_pts: [29,18,24,32,21], league_rank_pts: 7, league_rank_reb: null, league_rank_ast: null, matchup_avg_pts: 24.6 },
  { player_id: "p007", game_id: "game_001", team_id: "celtics", name: "Jaylen Brown", pos: "SG", minutes: "28:22", pts: 19, reb: 5, ast: 2, stl: 2, blk: 0, turnovers: 1, fgm: 7, fga: 15, plus_minus: -1, last5_pts: [22,27,15,18,24], league_rank_pts: null, league_rank_reb: null, league_rank_ast: null, matchup_avg_pts: 18.3 },
  { player_id: "p008", game_id: "game_001", team_id: "celtics", name: "Jrue Holiday", pos: "PG", minutes: "27:30", pts: 11, reb: 4, ast: 9, stl: 3, blk: 1, turnovers: 2, fgm: 4, fga: 10, plus_minus: 4, last5_pts: [14,9,16,11,13], league_rank_pts: null, league_rank_reb: null, league_rank_ast: null, matchup_avg_pts: 11.5 },
  { player_id: "p009", game_id: "game_001", team_id: "celtics", name: "Al Horford", pos: "C", minutes: "22:15", pts: 8, reb: 6, ast: 2, stl: 0, blk: 2, turnovers: 0, fgm: 3, fga: 7, plus_minus: 2, last5_pts: [6,10,8,12,7], league_rank_pts: null, league_rank_reb: null, league_rank_ast: null, matchup_avg_pts: 8.1 },
  { player_id: "p010", game_id: "game_001", team_id: "celtics", name: "Kristaps Porzingis", pos: "PF", minutes: "23:44", pts: 13, reb: 7, ast: 1, stl: 0, blk: 3, turnovers: 1, fgm: 5, fga: 11, plus_minus: 1, last5_pts: [17,8,15,20,11], league_rank_pts: null, league_rank_reb: null, league_rank_ast: null, matchup_avg_pts: 13.9 }
];

export const MOCK_PREDICTIONS = [
  { game_id: "game_001", winner: "Los Angeles Lakers", winner_abbr: "LAL", confidence: 68, score_home: 118, score_away: 109, key_factors: ["Lakers 7-3 in last 10 home games vs Boston","LeBron averaging 31 PPG over last 5 games","Celtics on back-to-back, 3rd road game in 5 nights"], result: "pending" },
  { game_id: "game_002", winner: "Denver Nuggets", winner_abbr: "DEN", confidence: 72, score_home: 112, score_away: 121, key_factors: ["Nuggets #1 net rating last 15 games at +8.4","Jokic triple-double pace in 4 of last 5 games","Warriors without Draymond; defensive rating drops 11 points"], result: null },
  { game_id: "game_003", winner: "Miami Heat", winner_abbr: "MIA", confidence: 61, score_home: 108, score_away: 104, key_factors: ["Heat 14-4 at home this season","Butler historically elevates in high-leverage games","Giannis played limited minutes — questionable listing"], result: "correct" }
];

export const MOCK_TAKES = [
  { id: "t001", personality: "Stephen A. Smith", outlet: "ESPN First Take", outlet_color: "#CC0000", avatar: "SAS", take_text: "LeBron James is NO LONGER the best player on his own team. Anthony Davis has taken over. Full stop.", category: "hot", agrees: 1243, disagrees: 2891 },
  { id: "t002", personality: "Zach Lowe", outlet: "ESPN", outlet_color: "#CC0000", avatar: "ZL", take_text: "The Celtics are the most complete team in the East and it's not particularly close. Their defense is historically elite.", category: "stat-backed", agrees: 4102, disagrees: 891 },
  { id: "t003", personality: "Shannon Sharpe", outlet: "Club Shay Shay", outlet_color: "#8B5CF6", avatar: "SS", take_text: "Nikola Jokic is the greatest offensive player at any position I have ever seen in my lifetime. He sees things no one else sees.", category: "popular", agrees: 6741, disagrees: 1204 },
  { id: "t004", personality: "Bill Simmons", outlet: "The Ringer", outlet_color: "#E87722", avatar: "BS", take_text: "The Warriors dynasty is officially over. This roster has no path back to the Finals. Steph deserves better.", category: "hot", agrees: 3218, disagrees: 2544 },
  { id: "t005", personality: "Malika Andrews", outlet: "ESPN", outlet_color: "#CC0000", avatar: "MA", take_text: "Sources tell me the Lakers front office is fully committed to re-signing LeBron regardless of the cap situation.", category: "prediction", agrees: 2987, disagrees: 761 },
  { id: "t006", personality: "Skip Bayless", outlet: "Undisputed", outlet_color: "#1D4ED8", avatar: "SB", take_text: "Jayson Tatum is NOT a superstar. He disappears in big moments. Show me a ring.", category: "hot", agrees: 891, disagrees: 5432 },
  { id: "t007", personality: "Tim Bontemps", outlet: "ESPN", outlet_color: "#CC0000", avatar: "TB", take_text: "Victor Wembanyama is already the most unique player to ever enter the NBA. His combination of size and skill has no historical precedent.", category: "popular", agrees: 7823, disagrees: 445 },
  { id: "t008", personality: "Kendrick Perkins", outlet: "ESPN First Take", outlet_color: "#CC0000", avatar: "KP", take_text: "The Miami Heat culture is the gold standard of the NBA. No team does more with less. Every year they compete. Every. Single. Year.", category: "popular", agrees: 3341, disagrees: 1122 }
];

export const FALLBACK_PLAYER_CARD = {
  report: "Player data is currently being processed. Check back in a moment for a full AI scouting analysis.",
  projection: { pts: "18–22", reb: "6–9", ast: "4–7" },
  trend: "neutral" as const
};

export const FALLBACK_PREDICTION = {
  winner: "Data loading",
  winner_abbr: "---",
  confidence: 65,
  score_home: 112,
  score_away: 108,
  key_factors: ["Analyzing team performance data", "Computing rest and travel factors", "Evaluating head-to-head history"],
  result: null
};
```

Also mirror the same mock data in backend/app/data/seed_mock.py as Python dicts/lists with the same values and keys, and use those in backend fallback responses.

---

## 7. BACKEND — ALL FASTAPI ROUTES

Implement the backend as a FastAPI app with these routes and logic. Create backend/app/config.py for env settings, backend/app/services/supabase_service.py for Supabase and (optional) Upstash Redis helpers, and create all router files under backend/app/routes/.

### 7.1 main.py
```python
# EXACT structure
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import games, predictions, player_card, takes

app = FastAPI(title="CourtIQ API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router,       prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(player_card.router, prefix="/api")
app.include_router(takes.router,       prefix="/api")

@app.get("/health")
def health(): return {"status": "ok", "service": "courtiq-api"}
```

### 7.2 GET `/api/games`
```
Logic:
1. Try GET https://api.balldontlie.io/v1/games?dates[]={today_ISO}
   (No API key header needed for free tier)
2. On success: upsert into Supabase games table, return transformed list
3. On any failure: query Supabase games table for today's date
4. If Supabase also empty: return MOCK_GAMES Python list
5. Always return: list of game objects matching the schema in Section 6
6. Cache successful balldontlie response in Upstash Redis key "live:games:{date}" TTL=30s
7. Check Redis before calling balldontlie — if hit, return Redis data immediately
```

Implement this route in backend/app/routes/games.py using an APIRouter. In the route handler, implement the Redis check and set via Upstash REST if UPSTASH env vars are present. If cache miss, call nba_service.get_today_games() and then cache the resulting list under the specified key and TTL.

### 7.3 GET `/api/predictions/{game_id}`
```
Logic:
1. Check Supabase predictions table WHERE game_id = {game_id}
2. If found AND created_at > now() - interval '1 hour': return cached row
3. If not found: call gemini_service.generate_prediction(game_data)
4. Write result to Supabase predictions table
5. Return prediction object
6. On Gemini failure: return matching entry from MOCK_PREDICTIONS Python list
```

Implement this route in backend/app/routes/predictions.py using APIRouter. Ensure you can obtain a minimal game_data object: query Supabase games table by game_id first; if missing, fall back to searching MOCK_GAMES. Pass the resulting dict into generate_prediction.

### 7.4 POST `/api/player-card`
```
Request body: { player_id: str, player_name: str, season_avg: dict, last5: list[int], opponent: str, game_id: str }
Logic:
1. Check Supabase player_cards WHERE player_id={} AND game_id={}
2. If found AND created_at > now() - interval '24 hours': return cached row
3. Call gemini_service.generate_player_card(body)
4. Write to Supabase player_cards table
5. Return: { report, projection: {pts, reb, ast}, trend }
6. On Gemini failure: return FALLBACK_PLAYER_CARD
```

Implement this route in backend/app/routes/player_card.py with Pydantic request models and correct response keys. Store projection as jsonb and trend/report as text in Supabase.

### 7.5 POST `/api/takes/verdict`
```
Request body: { take_id: str, take_text: str }
Logic:
1. Check Supabase take_verdicts WHERE take_id={take_id}
2. If found: return cached row (permanent cache — verdict never changes)
3. Call gemini_service.generate_take_verdict(take_text)
4. Write to Supabase take_verdicts table
5. Return: { steelman, challenge, verdict_label }
6. On failure: return { steelman: "Supporting argument unavailable.", challenge: "Counter-argument unavailable.", verdict_label: "Partially supported" }
```

Implement in backend/app/routes/takes.py.

### 7.6 POST `/api/takes/vote`
```
Request body: { take_id: str, vote: 'agree' | 'disagree' }
Logic:
1. If vote == 'agree': UPDATE media_takes SET agrees = agrees + 1 WHERE id = take_id
2. If vote == 'disagree': UPDATE media_takes SET disagrees = disagrees + 1 WHERE id = take_id
3. Return: { take_id, agrees, disagrees }
```

Implement in backend/app/routes/takes.py.

For all backend routes:
- Use try/except around all external calls and all Supabase operations.
- On failure, return mock/fallback data as specified.
- Ensure responses always match the schemas implied by the mock data.
- Ensure CORS allows all origins (already in main.py).

---

## 8. GEMINI SERVICE — EXACT PROMPTS AND CODE

```python
# backend/app/services/gemini_service.py — EXACT

import google.generativeai as genai
import json
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=genai.GenerationConfig(
        temperature=0.7,
        response_mime_type="application/json"
    )
)

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
Home record: {game.get('home_record','N/A')}. Away record: {game.get('away_record','N/A')}.
Home last 5: {game.get('home_last5','W W L W L')}. Away last 5: {game.get('away_last5','L W W L W')}.
Home rest days: {game.get('home_rest',2)}. Away rest days: {game.get('away_rest',1)}."""
    return await _call_gemini(PREDICTION_SYSTEM, user)

# ─── PLAYER CARD ────────────────────────────────────────────────────
PLAYER_CARD_SYSTEM = """You are an NBA scout. Return ONLY valid JSON with these exact keys:
- report: string, exactly 3 sentences, specific and data-driven
- projection: object with keys pts, reb, ast (each a string range like "22-26", "8-11", "4-7")
- trend: string, must be exactly "hot", "cold", or "neutral"
No explanation. No markdown. Raw JSON object only."""

async def generate_player_card(data: dict) -> dict:
    user = f"""Player: {data['player_name']}.
Season averages: {data['season_avg'].get('pts','N/A')} PPG, {data['season_avg'].get('reb','N/A')} RPG, {data['season_avg'].get('ast','N/A')} APG.
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
    prompt = f"{system}\n\n{user}"
    response = model.generate_content(prompt)
    text = response.text.strip()
    # Strip code fences if present
    clean = text.replace('```json','').replace('```','').strip()
    return json.loads(clean)
```

---

## 9. NBA DATA SERVICE — EXACT

```python
# backend/app/services/nba_service.py — EXACT

import httpx
from datetime import date, datetime
import asyncio
from app.services.supabase_service import supabase_client
from app.data.seed_mock import MOCK_GAMES

BALLDONTLIE_BASE = "https://api.balldontlie.io/v1"

async def get_today_games() -> list:
    today = date.today().isoformat()
    
    # 1. Try Redis cache (implement via Upstash REST if UPSTASH_URL set)
    # 2. Try balldontlie
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{BALLDONTLIE_BASE}/games",
                params={"dates[]": today}
            )
            resp.raise_for_status()
            raw = resp.json().get("data", [])
            games = [_transform_balldontlie_game(g) for g in raw]
            if games:
                # Upsert to Supabase
                for g in games:
                    supabase_client.table("games").upsert(g).execute()
                return games
    except Exception:
        pass
    
    # 3. Try Supabase
    try:
        result = supabase_client.table("games").select("*").eq("game_date", today).execute()
        if result.data:
            return result.data
    except Exception:
        pass
    
    # 4. Return mock
    return MOCK_GAMES

def _transform_balldontlie_game(raw: dict) -> dict:
    return {
        "game_id": str(raw["id"]),
        "game_date": raw["date"][:10],
        "status": _map_status(raw.get("status", "")),
        "quarter": raw.get("period"),
        "clock": raw.get("time"),
        "home_team_id": str(raw["home_team"]["id"]),
        "home_team_name": raw["home_team"]["full_name"],
        "home_team_abbr": raw["home_team"]["abbreviation"],
        "home_score": raw.get("home_team_score"),
        "away_team_id": str(raw["visitor_team"]["id"]),
        "away_team_name": raw["visitor_team"]["full_name"],
        "away_team_abbr": raw["visitor_team"]["abbreviation"],
        "away_score": raw.get("visitor_team_score"),
        "tipoff_time": None
    }

def _map_status(s: str) -> str:
    if "Final" in s: return "final"
    if s.isdigit() or "Qtr" in s or "Half" in s: return "live"
    return "upcoming"
```

---

## 10. FRONTEND COMPONENT SPECIFICATIONS

Implement the Next.js 14 App Router frontend in TypeScript, Tailwind, React Query, Axios. Implement all routes, components, and UI states exactly as described.

### 10.1 Navbar.tsx
```
- Fixed top, full width, h-14
- bg-surface/90 backdrop-blur-md border-b border-border
- Left: "🏀 CourtIQ" — text-orange font-black text-xl
- Right nav links: Games (/), Predictions (/predictions), Takes (/takes)
- Active: text-orange underline decoration-orange underline-offset-4
- Inactive: text-secondary hover:text-primary transition-colors
- Use Next.js usePathname() for active detection
```

### 10.2 Dashboard page (src/app/page.tsx)
```
- Page heading: "Today's Games" text-2xl font-bold + subtitle text-secondary
- OverlaySelector sticky below navbar
- React Query: useQuery(['games'], () => api.get('/api/games'), { refetchInterval: 30000 })
- Show LoadingSpinner while isLoading
- Show ErrorBanner if isError, with retry button
- Game cards grid: grid grid-cols-1 lg:grid-cols-2 gap-4
- selectedGame state (null | game object)
- When selectedGame !== null: render <GameExpanded /> as modal overlay
```

### 10.3 GameCard.tsx
```
Props: { game: Game, onClick: () => void, isSelected: boolean }
- bg-surface border border-border rounded-xl p-4 cursor-pointer
  hover:border-orange/50 transition-all duration-200
- isSelected: add border-orange-glow class
- Status badge (top): LIVE = green dot + "LIVE" animate-pulse-live | FINAL = dim "FINAL" | upcoming = warn time
- Two team rows: logo img (32x32) | abbr font-bold text-lg | score font-mono text-3xl font-bold
- Winning team score: text-orange
- Live game: show "Q{quarter} {clock}" in orange text-sm below scores
- Hover footer: "View Box Score →" text-orange text-sm
```

### 10.4 GameExpanded.tsx
```
Props: { game: Game, activeOverlay: string, onClose: () => void }
- fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-start justify-center pt-16
- Panel: bg-surface rounded-2xl max-w-4xl w-full mx-4 p-6 max-h-[80vh] overflow-y-auto
- Header: team names + scores + X close button (top-right)
- Tab row: "LAL" | "BOS" (team abbr tabs)
- Active tab: render <BoxScoreTable /> for selected team's players
- Pass activeOverlay down to BoxScoreTable
```

### 10.5 BoxScoreTable.tsx
```
Props: { players: PlayerStat[], activeOverlay: 'none'|'rank'|'sparkline'|'matchup' }
- overflow-x-auto table w-full
- Header: PLAYER | POS | MIN | PTS | REB | AST | STL | BLK | +/- | FG | [overlay header if active]
- Sort players by pts descending
- Each row: <PlayerRow player={p} activeOverlay={activeOverlay} />
- Header: text-dim text-xs uppercase tracking-wider bg-surfaceHigh
```

### 10.6 PlayerRow.tsx
```
Props: { player: PlayerStat, activeOverlay: string }
- onClick: open <PlayerModal />
- Cursor pointer, hover:bg-surfaceHigh transition
- name: text-primary font-medium
- pts: text-white font-bold
- plus_minus: positive → text-success | negative → text-danger | zero → text-dim
- fgm/fga: shown as "9/17"
- Overlay column (last, conditional):
  - 'rank': <StatPill> showing highest league rank (e.g. "#4 PTS") bg-orange-dim text-orange
  - 'sparkline': <Sparkline data={player.last5_pts} width={64} height={28} />
  - 'matchup': small text — "{player.matchup_avg_pts} avg vs opp" text-xs text-secondary
```

### 10.7 Sparkline.tsx
```
Props: { data: number[], width?: number, height?: number }
Uses Recharts <LineChart width={w} height={h} data={data.map((v,i)=>({v,i}))}>
- No axes (hide with tick={false} axisLine={false})
- No grid (CartesianGrid hidden)
- No tooltip
- <Line dataKey="v" dot={false} strokeWidth={2}
    stroke={data[data.length-1] > data[0] ? '#27AE60' : '#E74C3C'} />
- One dot on last point, colored accordingly
```

### 10.8 OverlaySelector.tsx
```
Props: { active: string, onChange: (v: string) => void }
- Horizontal flex row, gap-2, py-2
- Options: [{id:'none',label:'No Overlay'},{id:'rank',label:'📊 League Rank'},{id:'sparkline',label:'📈 Form'},{id:'matchup',label:'🆚 Matchup'}]
- Active: bg-orange text-white rounded-full px-3 py-1 text-sm font-semibold
- Inactive: bg-surface text-secondary border border-border hover:border-orange rounded-full px-3 py-1 text-sm
```

### 10.9 Predictions page (src/app/predictions/page.tsx)
```
- Heading: "AI Predictions" text-2xl font-bold
- Subtitle: "Powered by Ollama · Updated before each tip-off"
- Disclaimer badge: "🤖 AI-generated analysis · Not financial advice" bg-orange-dim text-orange text-xs px-3 py-1 rounded-full
- On mount: fetch all games, then for each fetch /api/predictions/{game_id} via Promise.all
- While loading: show 3 LoadingSkeleton cards
- Grid: grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4
- Render <PredictionCard /> for each
```

### 10.10 PredictionCard.tsx
```
Props: { game: Game, prediction: Prediction }
- bg-surface border border-border rounded-xl p-5 hover:border-orange/30 transition
- Header: "LAL vs BOS · Live Q3 4:22" or tipoff time, text-secondary text-sm
- Winner: large team name + "WIN" text-orange text-2xl font-black
- <ConfidenceGauge value={prediction.confidence} />
- Score: "{score_home}–{score_away}" font-mono text-xl text-secondary
- Key factors: 3 items with orange bullet dot (w-1.5 h-1.5 rounded-full bg-orange mt-1.5 flex-shrink-0)
- Result badge if game.status === 'final':
  correct → "✓ Correct Call" bg-success/20 text-success border border-success/30 rounded-full px-3 py-1 text-xs
  incorrect → "✗ Missed" bg-danger/20 text-danger border border-danger/30 same styles
  pending → "⏳ Pending" bg-warn/20 text-warn border border-warn/30 same styles
```

### 10.11 ConfidenceGauge.tsx
```
Props: { value: number }
- Pure SVG, 120x70 viewBox
- Background arc: M10,60 A50,50 0 0,1 110,60 stroke=#2E2E2E strokeWidth=8 fill=none
- Foreground arc: same path, stroke=#E87722, strokeDasharray computed from value
  dashLength = (value / 100) * 157 (half circumference of r=50 arc)
  strokeDasharray="{dashLength} 157"
- Center text: "{value}%" text-anchor=middle fill=#F0F0F0 font-size=18 font-weight=bold y=55
- Below text: "Confidence" text-anchor=middle fill=#9A9A9A font-size=11 y=70
```

### 10.12 PlayerModal.tsx
```
Props: { player: PlayerStat, game: Game, onClose: () => void }
- Same modal overlay as GameExpanded
- On open: POST /api/player-card with { player_id, player_name: player.name, season_avg: {pts: player.pts, reb: player.reb, ast: player.ast}, last5: player.last5_pts, opponent: game.away_team_name, game_id: game.game_id }
- While loading: show 3 LoadingSkeleton lines
- Header: player name text-xl font-bold + position badge + team abbr
- Season line: "Season avg: {pts}/{reb}/{ast}" text-secondary text-sm
- Projection: "Tonight: {pts} pts · {reb} reb · {ast} ast" text-white text-lg font-semibold
- Trend badge: hot=bg-success/20 text-success "🔥 Hot Streak" | cold=bg-danger/20 text-danger "🥶 Cold Streak" | neutral=bg-dim/20 text-secondary "— Neutral"
- Scouting report: p-4 bg-surfaceHigh rounded-lg italic text-secondary leading-relaxed
- Last 5 circles: flex row, each circle w-8 h-8 rounded-full font-mono text-xs flex items-center justify-center, colored bg-success/20 text-success if above season avg else bg-danger/20 text-danger
```

### 10.13 TakeCard.tsx
```
Props: { take: Take }
State: localAgrees, localDisagrees (init from take), hasVoted (localStorage), verdict, isLoadingVerdict

- bg-surface border border-border rounded-xl p-5 mb-3

Header row:
  - Avatar: w-9 h-9 rounded-full bg-orange-dim text-orange font-bold flex items-center justify-center text-sm
  - Name: font-semibold text-primary
  - Outlet badge: text-xs px-2 py-0.5 rounded-full text-white, bg = outlet_color
  - Category badge: hot="🔥 Hot" | stat-backed="📊 Stat-Backed" | prediction="🎯 Prediction" | popular="👥 Popular"
  - Timestamp: text-dim text-xs ml-auto

Take text: text-primary text-base leading-relaxed my-3 with subtle left border-l-2 border-orange/30 pl-3 italic

Agree/Disagree row:
  - 👍 button: on click → POST /api/takes/vote { take_id, vote:'agree' }, update localAgrees, set hasVoted
  - 👎 button: same for disagree
  - Both disabled if hasVoted
  - Active vote style: green for agree, red for disagree
  - Consensus bar: full-width h-1.5 bg-border rounded, green fill to {agrees/(agrees+disagrees)*100}%
  - Percentage split text-xs text-dim after vote

AI Verdict button:
  - "🤖 AI Verdict" border border-orange/40 text-orange text-sm px-3 py-1.5 rounded-lg hover:bg-orange-dim
  - Loading: spinner + "Analyzing..."
  - On success: show <AIVerdictBox verdict={verdict} />

localStorage key: "courtiq_voted_{take.id}"
```

### 10.14 AIVerdictBox.tsx
```
Props: { verdict: { steelman, challenge, verdict_label } }
- fade-in + slide-up animation: opacity-0 translate-y-2 → opacity-100 translate-y-0 duration-300
- bg-surfaceHigh border border-orange/30 rounded-lg p-4 mt-3
- Header: "🤖 CourtIQ AI Verdict" text-orange text-sm font-semibold
- Verdict badge:
  "Backed by data" → bg-success/20 text-success border-success/30
  "Partially supported" → bg-warn/20 text-warn border-warn/30
  "Overblown" → bg-danger/20 text-danger border-danger/30
  Styles: rounded-full px-3 py-0.5 text-xs border ml-2
- Steelman row: "✓" text-success mr-2 + steelman text-sm text-primary
- Challenge row: "✗" text-danger mr-2 + challenge text-sm text-primary
- Small footer: "Powered by Gemini 1.5 Flash" text-dim text-xs mt-2
```

Implement TakesFeed.tsx to render the list of takes and show Loading/Error/Empty states. Ensure /takes loads all 8 seeded takes.

---

## 11. ENVIRONMENT VARIABLES — EXACT

```bash
# backend/.env.example — EXACT
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
UPSTASH_REDIS_REST_URL=https://your-upstash-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_upstash_token
PORT=8000

# frontend/.env.local.example — EXACT
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

```typescript
// frontend/src/lib/api.ts — EXACT
import axios from 'axios';
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
});
export default api;
```

---

## 12. DEPLOYMENT FILES — EXACT

```toml
# backend/railway.toml — EXACT
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
```

```json
// frontend/vercel.json — EXACT
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://YOUR_RAILWAY_URL/api/:path*" }
  ]
}
```

---

## 13. LOADING, ERROR & EMPTY STATES

Every component with async data MUST implement all three states:
```
Loading: <LoadingSpinner /> centered OR <LoadingSkeleton /> for list items
Error: <ErrorBanner message={error.message} onRetry={refetch} />
Empty: friendly text message "No games found today. Check back at tip-off." centered, text-secondary
All fetch calls: wrapped in try/catch, fallback to mock data on any error
React Query: staleTime=30000, retry=2, retryDelay=1000
```

Implement these UI components in frontend/src/components/ui and use them everywhere appropriate: dashboard, predictions, takes, player card loading, verdict loading.

---

## 14. DEMO PATH — GUARANTEE THESE WORK

Pre-generate Gemini responses and store in Supabase before the demo. These 8 interactions must be instant:
```
1. / loads showing game_001 (LAL vs BOS) with red LIVE badge + animated pulse
2. Clicking game_001 opens GameExpanded with LAL player list
3. Clicking "📊 League Rank" overlay shows "#4 PTS" orange pill on LeBron row
4. Clicking "📈 Form" overlay shows Recharts sparkline on every player row
5. Clicking LeBron's row opens PlayerModal — scouting card loads from Supabase cache in <200ms
6. /predictions loads 3 cards with SVG confidence gauges, game_003 shows "✓ Correct Call" badge
7. /takes loads 8 takes feed
8. Clicking "🤖 AI Verdict" on t001 (Stephen A.) renders AIVerdictBox from Supabase cache in <200ms
```

Ensure backend/app/data/seed_mock.py seeds:
- MOCK_GAMES into games
- MOCK_TAKES into media_takes
- MOCK_PREDICTIONS into predictions (with created_at recent enough to be cached)
- A pre-generated player_cards row for player_id "p001" and game_id "game_001" with a realistic report/projection/trend
- A pre-generated take_verdicts row for take_id "t001" with realistic steelman/challenge/verdict_label
- Optionally seed player_game_stats using MOCK_PLAYER_STATS for game_001 to support future features

---

## 15. COMPLETION CHECKLIST

- Build the full working application with:
  - frontend Next.js app under courtiq/frontend
  - backend FastAPI app under courtiq/backend
  - Supabase schema and RLS policies from Section 5
  - Seed script under backend/app/data/seed_mock.py to populate demo data
  - All UI, routes, and behaviors specified above
  - No missing imports, no runtime errors, and instant demo-path interactions via Supabase cache

- Implement the remaining required files (not provided as EXACT blocks) with correct, minimal, production-hackathon quality defaults:
  - frontend/package.json with exact dependency versions and scripts (dev/build/start/lint)
  - frontend/tsconfig.json suitable for Next.js 14 + TS 5.4
  - frontend/postcss.config.js
  - frontend/next.config.ts
  - frontend/src/lib/supabase.ts using @supabase/supabase-js@2.43.5 and NEXT_PUBLIC_SUPABASE_URL/NEXT_PUBLIC_SUPABASE_ANON_KEY
  - frontend/src/lib/queryClient.ts configuring React Query per Section 13 (staleTime=30000, retry=2, retryDelay=1000)
  - frontend/src/app/layout.tsx root layout rendering Navbar and applying global dark theme, wrapping children with QueryClientProvider
  - frontend/src/app/page.tsx implementing Dashboard specs
  - frontend/src/app/predictions/page.tsx implementing Predictions specs
  - frontend/src/app/takes/page.tsx implementing Takes specs
  - All frontend components listed in the file tree implemented exactly per Section 10 specs
  - backend/requirements.txt with exact versions from Section 2
  - backend/.env.example EXACT from Section 11
  - backend/Dockerfile suitable for Railway/Render (python:3.11-slim, install requirements, run uvicorn)
  - backend/app/config.py reading env vars with python-dotenv + pydantic settings and exposing settings.GEMINI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN, PORT
  - backend/app/services/supabase_service.py creating supabase_client using supabase==2.5.0 create_client and implementing helper functions for:
    - selecting cached predictions/player_cards/take_verdicts with time windows
    - upserting predictions/player_cards
    - updating vote counts and returning updated agrees/disagrees
    - optional Upstash Redis REST get/set with TTL
  - backend/app/routes/games.py, predictions.py, player_card.py, takes.py implementing Section 7 logic and using gemini_service/nba_service/supabase_service
  - .gitignore suitable for Next.js + Python + env files + node_modules + __pycache__
  - README.md with setup steps for Supabase SQL, env vars, seeding, and local dev commands for frontend and backend

- Ensure frontend uses mock data as fallback on any error:
  - games fallback to MOCK_GAMES
  - predictions fallback to MOCK_PREDICTIONS or FALLBACK_PREDICTION
  - takes fallback to MOCK_TAKES
  - player card fallback to FALLBACK_PLAYER_CARD

- Ensure API calls:
  - frontend uses Axios client from frontend/src/lib/api.ts
  - backend exposes /health and /api routes
  - vercel.json rewrites /api/* to backend in production

Now verify the completed app using this checkbox checklist (format as a checkbox list):

BACKEND
- [ ] FastAPI starts on port 8000 with no errors: uvicorn app.main:app --reload
- [ ] GET /health returns {"status":"ok"}
- [ ] GET /api/games returns games array (real or mock, never empty)
- [ ] GET /api/predictions/game_001 returns valid prediction JSON with all required keys
- [ ] POST /api/player-card returns {report, projection:{pts,reb,ast}, trend}
- [ ] POST /api/takes/verdict returns {steelman, challenge, verdict_label}
- [ ] POST /api/takes/vote increments correct counter in Supabase
- [ ] All Gemini calls check Supabase cache first
- [ ] All routes have try/except with mock data fallback
- [ ] CORS allows all origins

FRONTEND
- [ ] Dark theme applied globally (bg #0D0D0D, surface #1A1A1A, orange #E87722)
- [ ] Inter font loaded from Google Fonts
- [ ] Navbar with active link detection renders on all pages
- [ ] / loads game cards with LIVE/FINAL/upcoming status badges
- [ ] Clicking game card opens GameExpanded modal with correct team's players
- [ ] OverlaySelector toggles rank/sparkline/matchup columns in BoxScoreTable
- [ ] Sparkline renders as Recharts mini line chart with green/red color
- [ ] League rank pill shows "#N STAT" in orange-dim bg
- [ ] Clicking player row opens PlayerModal with Gemini scouting card
- [ ] PlayerModal shows projection range, trend badge, last 5 circles
- [ ] /predictions page loads with ConfidenceGauge SVG arcs
- [ ] Result badges show on completed games
- [ ] /takes shows all 8 seeded takes
- [ ] Agree/Disagree buttons update Supabase vote counts
- [ ] Vote state persists via localStorage
- [ ] Consensus bar fills proportionally
- [ ] AI Verdict button fetches and renders AIVerdictBox
- [ ] AIVerdictBox shows verdict badge + steelman + challenge
- [ ] Loading states shown during all async operations
- [ ] Error states with retry shown on all failures
- [ ] Empty states shown when data is absent

DATABASE
- [ ] All 8 Supabase tables created with correct schema
- [ ] RLS enabled with public allow_all policies
- [ ] MOCK_TAKES seeded into media_takes table
- [ ] MOCK_GAMES seeded into games table
- [ ] Demo player cards pre-generated in player_cards table
- [ ] Demo take verdict pre-generated in take_verdicts table

DEPLOYMENT
- [ ] Backend live on Railway with GEMINI_API_KEY and SUPABASE env vars set
- [ ] Frontend live on Vercel with NEXT_PUBLIC_API_URL pointing to Railway URL
- [ ] vercel.json rewrites /api/* to Railway backend
- [ ] App fully functional at Vercel URL — no localhost references
- [ ] All 8 demo path items (Section 14) verified at live URL