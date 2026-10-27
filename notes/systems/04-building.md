# 04 — Building

## What Vein does (public sources, verify in-game)
| Behaviour | Source | Verified? |
|---|---|---|
| Build menu opens with **B**; you need the materials **and tools** in your inventory | Official wiki: Building | [ ] |
| The **Utility Cabinet** is the base's centre: it auto-repairs anything built inside its area, as long as you stock it with the right resources | Official wiki: Building | [ ] |
| Structures **outside** its range, or without enough materials, **decay over time** | Official wiki: Building | [ ] |
| Base guides cover wells, solar panels, generators, water connections and fortifications as part of building | veingame.net guides | [ ] |

## Open questions
- [ ] Cabinet radius, and does it extend vertically?
- [ ] Decay rate per piece type; does decay stop at some minimum?
- [ ] What does a repair cost — a share of the original materials, or a flat item?
- [ ] Can you build inside existing (pre-placed) houses, and do those decay?
- [ ] Is there structural support / collapse when a supporting piece is removed?
- [ ] Do zombies damage structures? Is base damage a server setting? (players mention "base damage off")

## Our model (`sim/building.py`)
- `Blueprint` — materials (used up) + tools (kept) + max health.
- `Base.build` — refuses with `MissingItems` if any tool or material is missing.
- `UtilityCabinet` — position, radius, its own `stock` of materials.
- `Base.tick` — pieces in a cabinet's range repair from its stock (10% of the piece's materials per full repair, our number); pieces outside it, or when the stock is short, decay; destroyed pieces are removed.

## Vein's real settings for this system
From published server configs — see [research/vein-server-settings.md](../../research/vein-server-settings.md) for sources and conflicts.

| Setting | Default | Wired into |
|---|---|---|
| `vein.BuildObjectDecay` | 1 (on) | `BuildConfig.decay_enabled` |
| `vein.BaseDamage` | 1.0 (0 disables) | `BuildConfig.base_damage_multiplier` → `Base.attack()` |

## Sources
- https://vein.wiki.gg/wiki/Building
- https://veingame.net/vein-guides
- https://steamcommunity.com/app/1857950/discussions/0/603018200150469927/
