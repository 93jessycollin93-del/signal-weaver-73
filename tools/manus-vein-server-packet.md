# Packet for Manus: run Vein's free dedicated server

FROM: Claude (coding operator) via Jessy · TO: Manus · **Needs Jessy's approval before starting.**

## Task
Install Vein's free dedicated server, collect its real settings and a fresh save file, report text facts back.

## Rules
- SteamCMD **anonymous** login only. Never log in with anyone's Steam account.
- Read-only analysis; don't modify game files; don't connect to other people's servers.
- Send back **text facts only** — no binaries, paks or assets. Exception: the `Server.vns` your own server creates (attach if under 20 MB).

## Steps (cheapest first)
1. `steamcmd +force_install_dir ~/vein-server +login anonymous +app_update 2131400 validate +quit`
   Linux: link `steamclient.so` into `Vein/Binaries/Linux/` (Ramjet's guide: https://ramjet.notion.site/Dedicated-Servers-17ef9ec29f1780aa8b6cc84bf31c2634).
   Start: `./Vein/Binaries/Linux/VeinServer-Linux-Test -Port=7777 -QueryPort=27015 -log`
2. **In the server console run `PrintAllVeinSettings`** and report the complete output. This is the most valuable step.
3. Report the generated `Vein/Saved/Config/LinuxServer/Game.ini` and `Engine.ini` in full (plain text).
4. Let the server save once (5–10 min), stop it, report path, size and the **first 256 bytes as hex** of `Vein/Saved/SaveGames/Server.vns`; attach the file if small.
5. Report build ID, total install size, 2-level folder tree, names and sizes of files in `Content/Paks`.
6. Optional: `strings` on the server binary → every unique string starting `vein.`, one per line.

## Return format
1. Period + sources 2. Completed with evidence 3. Decisions Jessy approved 4. Blockers / UNVERIFIED items 5. Next decision needed

## What it unlocks
- Step 2 replaces every ⚠️ default in [research/vein-server-settings.md](../research/vein-server-settings.md) with the official value.
- Step 4 unblocks system 09 (save format) — see the save-diff method in [rea-playbook.md](rea-playbook.md).
