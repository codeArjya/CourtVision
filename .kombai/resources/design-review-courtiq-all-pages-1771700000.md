# Design Review Results: CourtIQ — All Pages

**Review Date**: 2026-02-21  
**Routes**: `/` (Games Dashboard), `/predictions`, `/takes`  
**Focus Areas**: Visual Design, UX/Usability, Responsive/Mobile, Micro-interactions/Motion, Consistency, Accessibility

---

## Summary

CourtIQ has a solid dark-theme foundation with good typography choices (Inter + JetBrains Mono) and a consistent orange accent palette. However, the app suffers from **low visual identity** — team abbreviations lack branding, player cards feel sparse, and pages are near-monochromatic. Key UX issues include an incorrect `useState` usage for side-effects in `PlayerModal`, inaccessible interactive elements, and inconsistent hover/focus states. The engineer has already identified the core pain-point: the app looks "boring" — primarily because NBA teams' rich color identities are not reflected anywhere in the UI.

---

## Issues

| # | Issue | Criticality | Category | Location |
|---|-------|-------------|----------|----------|
| 1 | `PlayerModal` uses `useState()` to trigger async fetch — this is incorrect and can cause infinite re-renders. Should use `useEffect()`. | 🔴 Critical | UX / Performance | `components/players/PlayerModal.tsx:34-54` |
| 2 | Team abbreviations ("BOS", "LAL") shown without logos or full names on game cards — NBA fans can identify them but casual users cannot. Full team name exists in data but is unused. | 🟠 High | Visual Design | `components/dashboard/GameCard.tsx:70-99` |
| 3 | Team initials avatar circles (e.g. "BO", "LA") use wrong first 2 chars of abbreviation: "BOS" → "BO", "LAL" → "LA" — misaligned with NBA branding. Also no team color or logo. | 🟠 High | Visual Design | `components/dashboard/GameCard.tsx:70-71` |
| 4 | Zero team-color identity — all teams use the same orange/gray palette. Lakers purple, Celtics green, Heat red are completely absent. Engineer explicitly requested team color theming. | 🟠 High | Visual Design | `styles/tokens.ts`, `components/dashboard/GameCard.tsx` |
| 5 | No team logos displayed anywhere in the app (game cards, expanded view, prediction cards, player modal). Engineer explicitly requested logos. | 🟠 High | Visual Design | `components/dashboard/GameCard.tsx`, `components/predictions/PredictionCard.tsx`, `components/players/PlayerModal.tsx` |
| 6 | PlayerModal has no player avatar or animation — feels empty and static. Engineer requested player action animation. | 🟠 High | Visual Design / Micro-interactions | `components/players/PlayerModal.tsx:70-157` |
| 7 | No `aria-label` on close buttons (only "✕" text) — screen readers will announce "button ✕" with no context. | 🟠 High | Accessibility | `components/players/PlayerModal.tsx:92-97`, `components/dashboard/GameExpanded.tsx:47-51` |
| 8 | Game cards in dashboard show score as `null` for upcoming games with no visual treatment — blank space where a score would go. Should show a clear "TBD" or tipoff countdown. | 🟡 Medium | UX/Usability | `components/dashboard/GameCard.tsx:76-82` |
| 9 | `ConfidenceGauge` semicircle SVG has no accessible text — screen readers get nothing meaningful from this chart. | 🟡 Medium | Accessibility | `components/predictions/ConfidenceGauge.tsx:1-55` |
| 10 | Predictions page: score prediction (`118-109`) uses `text-secondary` (gray) — same visual weight as metadata, hard to spot as a key piece of information. | 🟡 Medium | Visual Design | `components/predictions/PredictionCard.tsx:63-66` |
| 11 | Vote buttons in TakeCard have no `aria-pressed` state — screen readers cannot tell if a button has been selected/clicked. | 🟡 Medium | Accessibility | `components/takes/TakeCard.tsx:110-132` |
| 12 | `GameCard` team tabs in expanded view both use `bg-orange` for the active state — no team color differentiation. Both LAL and BOS tabs look the same. | 🟡 Medium | Visual Design / Consistency | `components/dashboard/GameExpanded.tsx:56-77` |
| 13 | No keyboard focus rings visible on any interactive elements (buttons, links, table rows, game cards). | 🟡 Medium | Accessibility | `app/globals.css`, various components |
| 14 | `PlayerModal` loading state uses `LoadingSkeleton` but `GameExpanded` uses nothing — inconsistent loading patterns across similar data-fetching scenarios. | 🟡 Medium | Consistency | `components/players/PlayerModal.tsx:100-103`, `components/dashboard/GameExpanded.tsx` |
| 15 | Sparkline in `PlayerRow` has no hover tooltip showing actual point values — users cannot get the raw numbers from the visual-only chart. | 🟡 Medium | UX/Usability | `components/dashboard/Sparkline.tsx` |
| 16 | "View Box Score →" footer text in `GameCard` is only visible on hover — keyboard users and touch users cannot discover this affordance. | 🟡 Medium | UX/Usability | `components/dashboard/GameCard.tsx:110-113` |
| 17 | `GameExpanded` modal opens over the page but has no entrance/exit animation — abrupt appearance feels jarring. | ⚪ Low | Micro-interactions | `components/dashboard/GameExpanded.tsx:28-94` |
| 18 | `PlayerModal` has no entrance animation. Modal backdrop fades in but the card just snaps into position. | ⚪ Low | Micro-interactions | `components/players/PlayerModal.tsx:70-75` |
| 19 | Navbar brand text "🏀 CourtIQ" uses an emoji as a logo — inconsistent rendering across platforms; actual SVG/PNG logo would be more reliable. | ⚪ Low | Visual Design / Consistency | `components/layout/Navbar.tsx:16` |
| 20 | Takes page `max-w-3xl` while Games is `max-w-6xl` and Predictions is `max-w-6xl` — inconsistent max-widths make the Takes page feel unusually narrow. | ⚪ Low | Consistency | `app/takes/page.tsx:22` |
| 21 | BoxScoreTable uses `min-w-max` causing horizontal scroll on mobile — no mobile-optimized layout (e.g. collapsible columns) exists. | ⚪ Low | Responsive | `components/dashboard/BoxScoreTable.tsx:41` |
| 22 | `Badge.tsx` component exists but is not used in `PredictionCard.tsx` or `TakeCard.tsx` — these use inline class strings instead, diverging from the design system. | ⚪ Low | Consistency | `components/predictions/PredictionCard.tsx:22-39`, `components/takes/TakeCard.tsx:95-99` |

---

## Criticality Legend
- 🔴 **Critical**: Breaks functionality or violates accessibility standards severely
- 🟠 **High**: Significantly impacts user experience or design quality
- 🟡 **Medium**: Noticeable issue that should be addressed
- ⚪ **Low**: Nice-to-have improvement

---

## Engineer-Requested Improvements (Implementation Checklist)

These specific changes were requested and should be prioritized:

- [ ] **Team logos**: Add NBA team logo images next to team names/initials in `GameCard`, `GameExpanded`, `PredictionCard`, and `PlayerModal`. Use ESPN CDN: `https://a.espncdn.com/i/teamlogos/nba/500/{abbr_lowercase}.png`
- [ ] **Team colors**: Add a `NBA_TEAM_COLORS` map to `styles/tokens.ts`. Apply team-primary color to team name text in `GameCard` and `GameExpanded`. Apply color to active team tabs in `GameExpanded`.
- [ ] **Player animation**: Add CSS keyframe basketball player silhouette animation in `PlayerModal` — a small animated SVG or CSS basketball bounce/dribble sequence below the player header.
- [ ] **More 'full' and detailed**: Expand `PlayerModal` to show: per-game sparkline chart, matchup data, FG%, efficiency rating. Expand `GameCard` to show full team name + arena. Expand `PredictionCard` to show team logos in vs. header.
- [ ] **Fix `PlayerModal` useState bug**: Replace `useState()` used as side-effect trigger with `useEffect()` for the player card fetch.

---

## Next Steps (Priority Order)

1. **🔴 Fix `PlayerModal` data-fetching bug** (useState → useEffect) — prevents potential infinite loops
2. **🟠 Add NBA team logos** to GameCard, PredictionCard, PlayerModal, GameExpanded
3. **🟠 Add team color map** and apply to team names, tabs, game card accents
4. **🟠 Add player animation** area to PlayerModal (CSS keyframe or animated SVG)
5. **🟠 Enrich PlayerModal** with more stats, sparkline, and matchup data
6. **🟡 Fix accessibility** — aria-labels on close buttons, aria-pressed on vote buttons, focus rings
7. **🟡 Add `ConfidenceGauge` accessible text** (SVG title/desc or aria-label)
8. **⚪ Add modal entrance animations** — subtle CSS transform/fade-in
9. **⚪ Standardize max-widths** across pages and use `Badge` component consistently
