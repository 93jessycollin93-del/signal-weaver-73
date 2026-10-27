# 06 — Zombies: senses, AI, infection

## What Vein does (public sources, verify in-game)
| Behaviour | Source | Verified? |
|---|---|---|
| Zombies react to **sight, sound and smell**; servers have separate sight and hearing multipliers | Wabbanode zombie settings guide | [ ] |
| **Idle zombies doing tasks are less likely to see you** (0.019) | Patch notes 0.019 | [ ] |
| Sneak stat masks your noise, but less than before (0.019) | Patch notes 0.019 | [ ] |
| **Firearms are twice as audible**, with a separate multiplier setting (0.021) | Patch notes 0.021 | [ ] |
| Zombies don't collide with each other; horde members can't block hits on players | Earlier patch notes | [ ] |
| Improved pathfinding / new behaviour (0.021) | Patch notes 0.021 | [ ] |
| Per-hit infection chance `vein.ZombieInfectionChance`, 0–1, default **0.01** (one example config uses 0.25); 0 disables | gamesomg console list, HostByte | [ ] |
| Zombie health default **40**; `vein.AISpawner.Enabled` toggles spawns; `vein.AISpawner.HordeMode` for hordes | Server config guides | [ ] |
| Players believe bites infect more than scratches (unconfirmed) | Steam forum | [ ] |

## Open questions
- [ ] Actual sight range by day/night, and is there a vision cone?
- [ ] Footstep noise radius walking vs sprinting vs sneaking; how the sneak skill scales.
- [ ] Does infection on a hit add a fixed amount, or start a progressing sickness?
- [ ] How do hordes form and move? Do zombies respawn in cleared areas?
- [ ] Do zombies break doors or walls (link to 04 building)?

## Our model (`sim/zombies.py`)
- States: `IDLE` → `INVESTIGATING` (heard something) → `CHASING` (saw or smelled you) → `DEAD`.
- Idle zombies see and hear at half range; night cuts sight to 40%; smell works at 3 m in any light.
- Footsteps are a `Noise`; sneaking shrinks it, more with higher `sneak_skill`. Gunfire radius ×2.
- `attack()` deals damage and rolls `infection_chance`, raising the survivor's infection (link to 01). Health 40.

## Vein's real settings for this system
From published server configs — see [research/vein-server-settings.md](../../research/vein-server-settings.md) for sources and conflicts.

| Setting | Default | Wired into |
|---|---|---|
| `vein.AISpawner.Enabled` | 1 | `HordeSettings.enabled` |
| `vein.AISpawner.HordeMode` | 0 (off) | `HordeSettings.horde_mode` |
| `vein.AISpawner.Hordes.ChancePerMinute` | 0.05 | `HordeSettings.chance_per_minute` |
| `vein.AISpawner.Hordes.Duration` | 120 | `HordeSettings.duration_s` |
| `vein.AISpawner.Hordes.MaxDistance` | 25000 cm ⚠️ (one post 20000) | `HordeSettings.max_distance_m` = 250 |
| `vein.AISpawner.Hordes.ScentEffect` | 0.5 | `HordeSettings.scent_effect` |
| noise effect (exact name ⚠️) | 0.1 | `HordeSettings.noise_effect` |
| `vein.ZombieInfectionChance` | 0.01 ⚠️ | `ZombieSettings.infection_chance` |

`HordeDirector` in `sim/zombies.py` uses these knobs; how scent and noise combine is our design.

## Sources
- https://wabbanode.com/help/vein/how-to-change-zombie-settings-on-your-vein-server
- https://vein.wiki.gg/wiki/Version_0.019
- https://vein.wiki.gg/wiki/Version_0.005
- https://steamdb.info/patchnotes/20237024/
- https://gamesomg.com/vein-console-commands/
- https://www.hostbyte.net/billing/knowledgebase/103/Full-VEIN-Server-Configuration-Guide-Game.ini.html
- https://steamcommunity.com/app/1857950/discussions/0/687494495671062086/
