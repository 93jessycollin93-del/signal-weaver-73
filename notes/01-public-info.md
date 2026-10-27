# What's already known publicly

Gathered from community/host guides (Oct 2026, game ~0.025). These are second-hand — verify each against your own install and tick it off.

## Engine
- [x] Unreal Engine **5.6** per the UE4SS game profile for Vein (`EngineVersionOverride 5.6`); CUE4Parse mapped an earlier build to 5.4. Still worth confirming in `UE4SS.log`.

## Modding scene
- Nexus Mods has a VEIN section with a packaged **UE4SS** build (v3.0.1-599, *experimental* branch — the stable release reportedly doesn't work).
- UE4SS goes in `Vein/Binaries/Win64/`, next to the game exe. Script mods go in `ue4ss/Mods/`.
- Two mod types exist: **pak mods** (`Content/Paks/~mods`) and **UE4SS Lua/C++ mods**.
- Ramjet treats mods as unofficial; old mods break on updates.
- Multiplayer: UE4SS mods reportedly need every client to have them; pak mods mostly untested online. Paks touching the same item/container conflict.

## Saves
- Save file: `Vein/Saved/SaveGames/Server.vns` (custom `.vns` format — a good first RE target).
- [ ] Is it a standard UE `SaveGame` (GVAS header) or custom/compressed? Check the first bytes with a hex editor.

## Dedicated server / config
- Ports: UDP 7777 (game), 27015 (query).
- Since 0.016 Hotfix 5, gameplay settings live in `vein.*` console variables (admin menu or `[ConsoleVariables]` in `Engine.ini`), not in the save.
- `Game.ini` holds admins (SteamID64) and Discord chat settings. Linux path: `Vein/Saved/Config/LinuxServer/`.
- [~] Partial list from public configs in [research/vein-server-settings.md](../research/vein-server-settings.md). Full official list: run `PrintAllVeinSettings` on a server.

## Sources
- https://www.nexusmods.com/vein/mods/15
- https://www.gameserverkings.com/knowledge-base/vein/vein-dedicated-server/
- https://www.gameserverkings.com/knowledge-base/vein/vein-mods/
- https://supercraft.host/wiki/vein/world_settings/
- https://xgamingserver.com/docs/vein/upload-save
