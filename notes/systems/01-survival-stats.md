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

**[VERIFY] — parked by Jessy (Oct 22): playtest later.** The first two are the priority.
- [ ] [VERIFY] Exact hunger/thirst drop rates per in-game hour while idle, and do they change with activity?
- [ ] [VERIFY] Is there a separate sleep/tiredness bar, and what does it affect?
- [ ] How does "too full" work — a separate threshold above 100%, or vomiting?
- [ ] What raises infection, and can it be cured?
- [ ] Does body temperature exist as a number, or only as cold/hot states?
- [ ] Which property names show up in the UE4SS dump for the player character's stats?

## Our model (`sim/survival.py` + `sim/digestion.py`)
- Hunger and thirst now come from the realistic digestion model — see [01b-digestion.md](01b-digestion.md).
- `Survivor` adds fatigue (`energy`), `stamina`, `health` and `infection` on top of the `Body`.
- Activity is converted to metabolic rate (MET): sleep 0.95, idle 1.3, walk 3.5, sprint 10.
- Dirty water and contaminated food add infection; infection causes fever, which raises metabolism.
- Overeating/overdrinking makes you **vomit** (intentional difference from Vein, which kills you).
- `hud_visible()` returns only stats at extremes, like Vein 0.021.

## Sources
- https://vein.wiki.gg/wiki/Version_0.008
- https://vein.wiki.gg/wiki/Version_0.021
- https://steamcommunity.com/app/1857950/discussions/0/603040822196249928/
- https://hosthavoc.com/blog/vein-game-launch
