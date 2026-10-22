# Recreating Vein's gameplay — without copying it

Goal: a game of our own that *plays* like Vein (persistent, systems-heavy zombie survival), built the cheapest way, with nothing taken from Vein except ideas.

## The legal line, in one table
| Free to recreate | Never copy |
|---|---|
| Mechanics & rules (hunger, power grids, loot respawn, utility cabinet repair area) | Code — decompiled or otherwise |
| Genre, setting type (rural North America, post-collapse) | Art, models, textures, sounds, music, UI layout & icons |
| Numbers you *measured* by playing (balance values) | Data tables lifted from game files |
| Generic item names (generator, well, canned beans) | The name "Vein", Ramjet branding, its map layout, unique item/NPC names, story text |

Mechanics can't be copyrighted; expression can. Our process already enforces this: **behaviour notes → our own code** (`notes/systems/` → `sim/`).

## Most efficient path
**1. Keep the brain separate from the engine (done).**
`sim/` is plain, tested logic with no graphics. It's the expensive, unique part — and it stays reusable whatever engine we pick. 84 tests guard it.

**2. Pick an engine — recommendation: Godot 4.**
| | Godot 4 | Unreal 5 (what Vein uses) | Unity |
|---|---|---|---|
| Cost | Free, MIT, no royalties | Free, 5% royalty over $1M | Free tier, licence rules |
| Fit with our Python `sim/` | GDScript is Python-like: near line-by-line port | C++/Blueprints: full rewrite | C#: rewrite |
| Runs on a modest PC / laptop | Yes | Heavy | Medium |
| Third-person controller, day/night, navmesh | Built in | Built in, best visuals | Built in |
| Solo-dev speed | Fastest | Slowest | Medium |

Unreal only wins on graphics. For a one-person systems game, Godot is the efficient choice.

**3. Free art that's legally ours to use.**
CC0 / free-licence packs: Kenney, Quaternius (characters, zombies, buildings), Poly Haven (textures, HDRIs), KayKit, Mixamo (animations, free with an Adobe account). Original look = no asset risk.

**4. Build in thin vertical slices — each one playable.**
| Slice | What you can do | Systems used |
|---|---|---|
| S1 — "One house" ✅ built (`game/`) | Walk around a house in third person, eat from cans, drink from the tap until it shuts off, sleep, day/night | 01, 01b, 02 (mains only), 07 |
| S2 — "Something's outside" | One zombie that hears/sees/smells you; get hit → infection | 06 |
| S3 — "Stay alive" | Loot containers, items stay where dropped, save & quit & load | 05, 09 (our own save format) |
| S4 — "Off grid" | Well, barrels, generator, solar, fuse box | 02, 03 |
| S5 — "Make it home" | Build walls, utility cabinet repair area | 04 |
| S6 — "Road trip" | A car: siphon fuel, swap parts, drive to the next house | 08 |

Each slice ports only the `sim/` modules it needs to GDScript, with the same tests.

**5. Keep learning from Vein in parallel — without touching our code.**
Manus dedicated-server packet (setting names, save file) and playtests feed **numbers** into `notes/` → `sim/*Config`. Nothing else crosses over.

## Decisions
- Engine: **Godot 4** (Jessy, Oct 22).

## What I need from Jessy
- A working name for *our* game (not "Vein").
