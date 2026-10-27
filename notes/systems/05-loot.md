# 05 — Loot & world persistence

## What Vein does (public sources, verify in-game)
| Behaviour | Source | Verified? |
|---|---|---|
| Containers respawn loot: `vein.ContainersRespawn.Enabled`, default **1** (on) | Server config guides | [ ] |
| Respawn timer `vein.ContainersRespawn.Interval`, in **seconds**, default **10800** (3 h), range **600–43200** | Server config guides | [ ] |
| Loot amount `vein.Scarcity.Difficulty`, default **2**, range **0–4** | Server config guides | [ ] |
| Items stay where you leave them — the world is persistent (core selling point) | Official site / store page | [ ] |
| Full list of `vein.*` cvars exists publicly | Pastebin cvar dump | [ ] |

## Open questions
- [ ] Is the respawn interval real-time or game-time? Does it only count while nobody is nearby?
- [ ] Does a partly looted container refill, or only a fully empty one?
- [ ] Does higher scarcity mean fewer rolls, worse items, or both?
- [ ] Do containers players have put items into ever respawn (overwriting their stash)?
- [ ] Are dropped items ever cleaned up (despawn), e.g. on server restart?

## Our model (`sim/loot.py`)
- `LootTable` of weighted `LootEntry`s; `roll()` scales the number of rolls by scarcity (0 = ×1.5 … 4 = ×0.3, our numbers).
- `LootSettings` validates the same ranges as the real cvars.
- `Container` — generated on first open; only a **fully emptied** container refills, and only after the interval; putting items in cancels the respawn timer.
- `World` — items on the ground keep their exact position; `snapshot()`/`restore()` round-trips through JSON (a stand-in until we know the `.vns` format).

## Vein's real settings for this system
From published server configs — see [research/vein-server-settings.md](../../research/vein-server-settings.md) for sources and conflicts.

| Setting | Default | Wired into |
|---|---|---|
| `vein.Scarcity.Difficulty` | 2 (0–4; 4 = "impossible") | `LootSettings.scarcity` |
| `vein.ContainersRespawn.Enabled` | 1 | `LootSettings.respawn_enabled` |
| `vein.ContainersRespawn.Interval` | 10800 s (600–43200) | `LootSettings.respawn_interval_s` |

## Sources
- https://wabbanode.com/help/vein/how-to-change-zombie-settings-on-your-vein-server
- https://www.hostbyte.net/billing/knowledgebase/103/Full-VEIN-Server-Configuration-Guide-Game.ini.html
- https://citadelservers.com/client/knowledgebase/1002/Citadel-Servers---VEIN-Dedicated-Server-Configuration-Guide..html
- https://pastebin.com/KC1EwpmR
- https://www.doomhosting.com/tools/vein-server-config-generator
