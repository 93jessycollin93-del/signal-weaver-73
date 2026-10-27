# Vein server settings — what's publicly known

Collected Oct 27, 2026 from server-hosting guides, config templates and Docker projects (sources at the bottom). These are **Vein's real setting names**, not our guesses. Defaults marked ⚠️ disagree between sources — confirm on a live server.

> **Fastest way to get the official list:** on a dedicated server console, run `PrintAllVeinSettings` (reported to print every setting and its current value). This is step 1 of the Manus packet in [tools/manus-vein-server-packet.md](../tools/manus-vein-server-packet.md).

## Where settings live
| File | Section | What goes there |
|---|---|---|
| `Vein/Saved/Config/LinuxServer/Game.ini` (Windows: `WindowsServer`) | `[/Script/Engine.GameSession]` | `MaxPlayers` |
| same | `[/Script/Vein.VeinGameSession]` | `bPublic`, `bAntiCheatProtected`, `ServerName`, `BindAddr`, `HeartbeatInterval`, `AdminSteamIDs`, `Password` |
| same | `[/Script/Vein.ServerSettings]` | survival balance `GS_*` keys (e.g. `GS_HungerMultiplier`), `GS_ShowScoreboardBadges` |
| same | `[OnlineSubsystemSteam]` | `GameServerQueryPort`, `bVACEnabled` |
| `Engine.ini` | `[ConsoleVariables]` | all `vein.*` cvars |

Quirks reported by hosts: Unreal deletes lines that equal the default (so `vein.PvP=1` can "vanish"); `vein.*` lines placed in Game.ini can be ignored or crash the server; making the files read-only causes a rewrite loop. One template warns editing Engine.ini can break the server console — keep a backup.

## Known settings
| Setting | File | Default | Range / meaning | Agreement | Our model |
|---|---|---|---|---|---|
| `vein.Time.TimeMultiplier` | Engine.ini | **16** | game time ÷ real time (1 ≈ real time) | consistent (some guides write `vein.TimeMultiplier`) | `sim/calendar.py: VeinClock` |
| `vein.Time.NightTimeMultiplier` | Engine.ini | **3** | night runs this many times faster than day | consistent | `VeinClock` |
| `vein.Time.NightTimeMultiplierStart` / `End` | Engine.ini | **20** / **6** | night window, 24-h clock | consistent | `VeinClock` |
| `vein.Calendar.WaterShutoffTimeDays` | Engine.ini | 30 ⚠️ (one guide: 20) | 1–999 | conflicting | `Calendar.water_shutoff_day` |
| `vein.Calendar.ElectricalShutoffTimeDays` | Engine.ini | 46 ⚠️ (one guide: 30) | 1–999 | conflicting | `Calendar.power_shutoff_day` |
| `vein.Scarcity.Difficulty` | Engine.ini | **2** | 0–4: 0 = no restriction/most, 2 = standard, 4 = "impossible" | consistent | `LootSettings.scarcity` |
| `vein.ContainersRespawn.Enabled` | Engine.ini | **1** | on/off | consistent | `LootSettings.respawn_enabled` |
| `vein.ContainersRespawn.Interval` | Engine.ini | **10800** s | 600–43200 | consistent | `LootSettings.respawn_interval_s` |
| `vein.AISpawner.Enabled` | Engine.ini | **1** | zombie spawning on/off | consistent | `HordeDirector.enabled` |
| `vein.AISpawner.HordeMode` | Engine.ini | **0** | horde attacks off/on | consistent | `HordeDirector.horde_mode` |
| `vein.AISpawner.Hordes.ChancePerMinute` | Engine.ini | **0.05** | chance per minute (one server used 0.06) | mostly consistent | `HordeDirector.chance_per_minute` |
| `vein.AISpawner.Hordes.Duration` | Engine.ini | **120** | length of a horde event (unit unconfirmed; seconds assumed) | single source | `HordeDirector.duration_s` |
| `vein.AISpawner.Hordes.MaxDistance` | Engine.ini | 25000 ⚠️ (one post: 20000) | Unreal units are cm → ~250 m | conflicting | `HordeDirector.max_distance_m` |
| `vein.AISpawner.Hordes.ScentEffect` | Engine.ini | 0.5 | scent's pull on hordes | single source | `HordeDirector.scent_effect` |
| `vein.AISpawner.Hordes.NoiseEffect` (name ⚠️) | Engine.ini | 0.1 | "bigger means more likely hordes from noise" | single source | `HordeDirector.noise_effect` |
| `vein.ZombieInfectionChance` | Engine.ini | 0.01 ⚠️ (one table: 0.25) | 0–1 per hit; 0 disables | conflicting | `ZombieSettings.infection_chance` |
| `vein.BaseDamage` | Engine.ini | **1.0** | damage multiplier to bases; 0 disables | consistent | `BuildConfig.base_damage_multiplier` |
| `vein.BuildObjectDecay` | Engine.ini | **1** | structure decay on/off | consistent | `BuildConfig.decay_enabled` |
| `vein.PvP` | Engine.ini | ⚠️ | on/off; one host says not fully hooked up yet | — | — |
| `GS_HungerMultiplier` / `GS_ThirstMultiplier` | Game.ini `[/Script/Vein.ServerSettings]` | **1.0** | <1 slower drain, >1 faster; presets 0.6 casual / 1.8–2.0 hardcore | names from one host; a generator calls them "Hunger Rate"/"Thirst Rate" | `DigestionConfig.hunger_rate` / `thirst_rate` |

## Facts about the build
| Fact | Source |
|---|---|
| Unreal Engine **5.6** (UE4SS game profile `EngineVersionOverride 5.6`); CUE4Parse maps an earlier build to 5.4 | RE-UE4SS `assets/CustomGameConfigs/Vein/UE4SS-settings.ini`, CUE4Parse `EGame.cs` |
| Dedicated server: SteamCMD app **2131400**, anonymous, no game ownership; Linux binary `Vein/Binaries/Linux/VeinServer-Linux-Test` | pelican-eggs `vein/egg-v-e-i-n.json` |
| Server needs 3–4 GB RAM, 6–8 GB disk; ports UDP 7777 (game), 27015 (query) | pelican-eggs `vein/README.md` |
| Item IDs exist for a `GiveItem` admin command (a third-party list covers 0.025) | gamesomg.com/vein-item-ids |

## Not found publicly
- A cvar for **power hookup range** (players talk about it; no name found).
- Exact **hunger/thirst drain per hour** — only the multipliers are exposed.
- A **sleep/fatigue** mechanic — no public mention found.

## Sources
- https://github.com/pelican-eggs/games-steamcmd/tree/main/vein (Game.ini, egg JSON, README)
- https://github.com/UE4SS-RE/RE-UE4SS/tree/main/assets/CustomGameConfigs/Vein
- https://github.com/FabianFG/CUE4Parse/blob/master/CUE4Parse/UE4/Versions/EGame.cs
- https://github.com/JMeta0/vein-docker-server · https://github.com/aggysoul/vein-server · https://github.com/Johnny-Knighten/vein-server
- https://wabbanode.com/help/vein/how-to-change-the-day-and-night-cycle-speed-on-your-vein-server
- https://www.doomhosting.com/help/articles/how-to-change-vein-server-day-night-cycle-speed
- https://www.doomhosting.com/tools/vein-server-config-generator
- https://www.hostbyte.net/billing/knowledgebase/103/Full-VEIN-Server-Configuration-Guide-Game.ini.html
- https://www.hostbyte.net/billing/knowledgebase/114/How-to-Change-VEIN-Server-Difficulty-and-Survival-Balance.html
- https://www.hostbyte.net/billing/knowledgebase/109/How-to-Fix-VEIN-Server-Crashing-or-Freezing-After-Editing-Config-Files.html
- https://citadelservers.com/client/knowledgebase/1002/Citadel-Servers---VEIN-Dedicated-Server-Configuration-Guide..html
- https://xgamingserver.com/docs/vein/server-config
- https://www.gameserverkings.com/knowledge-base/vein/vein-console-commands/
- https://gamesomg.com/vein-server-config-generator/
- https://wabbanode.com/help/vein/how-to-enable-or-disable-building-decay-on-your-vein-server
- https://help.bisecthosting.com/hc/en-us/articles/41779120891803-How-to-Disable-Base-Damage-on-a-VEIN-Server
- https://my.logicservers.com/knowledgebase/501/How-to-change-the-Hunger-and-Thirst-Multiplier-on-your-Vein-Server.html
- https://steamcommunity.com/app/1857950/discussions/0/689741058327790275/
- https://pastebin.com/KC1EwpmR (community cvar dump — blocked from this environment, cited via search results)
