# 01 — Survival stats

## What Vein does (public sources, verify in-game)
| Behaviour | Source | Verified? |
|---|---|---|
| Hunger and thirst drain over time and cause damage when empty; drain was slowed in 0.008 | Patch notes 0.008 (Nov 2023) | [ ] |
| **Overeating and overdrinking can kill you** | Patch notes 0.008 | [ ] |
| HUD only shows hunger/thirst when values are extreme (0.021) | Patch notes 0.021 (Oct 2025) | [ ] |
| Infection makes you hungry faster ("insatiable appetite") | Steam forum, player report | [ ] |
| Unboiled / unfiltered water is unsafe | HostHavoc launch overview | [ ] |
| Cold drains energy; heat exhaustion blurs vision | HostHavoc launch overview | [ ] |
| Overexertion drains stamina faster | HostHavoc launch overview | [ ] |
| Players report food/water needs feel high | Steam forum | [ ] |

## Open questions (answer by playing or with UE4SS live property viewer)
- [ ] Exact drain rates per in-game hour, and do they change with activity?
- [ ] Is there a separate fatigue/sleep stat, and what does it affect?
- [ ] How does "too full" work — a separate threshold above 100%, or vomiting?
- [ ] What raises infection, and can it be cured?
- [ ] Does body temperature exist as a number, or only as cold/hot states?
- [ ] Which property names show up in the UE4SS dump for the player character's stats?

## Our model (`sim/survival.py`)
All numbers are ours and live in `SurvivalConfig` so they can be tuned once real values are measured.

- Stats 0–100: `hunger` (fullness), `thirst` (hydration), `energy` (fatigue), `stamina`, `health`, `infection`.
- Food/water can push fullness/hydration **above 100** up to a fatal limit → overeating/overdrinking kills.
- Drain scales with activity (idle/walk/sprint), infection (hunger multiplier), and temperature (cold drains energy, heat drains water faster).
- Dirty water adds infection; boiled/filtered water doesn't.
- Empty hunger/thirst/energy damages health.
- `hud_visible()` returns only stats at extremes, like Vein 0.021.

## Sources
- https://vein.wiki.gg/wiki/Version_0.008
- https://vein.wiki.gg/wiki/Version_0.021
- https://steamcommunity.com/app/1857950/discussions/0/603040822196249928/
- https://hosthavoc.com/blog/vein-game-launch
