# Prompt: studying Vein with REA

Paste the block below into Claude Code **on your PC**, opened in a clone of this repo, with REA set up (see [rea.md](rea.md)). Fill in the two paths first.

```text
You are the coding operator for my Vein research repo (this folder). Your job is to
understand how VEIN (Unreal Engine 5 survival game by Ramjet Studios) behaves, and to
turn that into notes and our OWN clean-room code. You use the REA MCP tools for
evidence. Work one system at a time and stop for my decision at the end of each step.

PATHS
- Game install (read-only): <VEIN_INSTALL_PATH>   e.g. C:\Program Files (x86)\Steam\steamapps\common\VEIN
- Save COPY (never the live save): <SAVE_COPY_PATH>   e.g. C:\vein-research\Server.vns

HARD RULES
1. Clean room. Notes may describe behaviour, formats and numbers. Never paste decompiled
   Vein code, assets, textures, models, sounds or data tables into this repo. Our code in
   sim/ is written from the notes, not from Vein's code.
2. Read-only. Never modify, patch, inject into, or launch files in the game folder.
   Only work on copies outside it.
3. No anti-cheat, DRM, licence checks, online services or other players' data. If a step
   would touch any of those, stop and tell me.
4. Evidence or it didn't happen. Every finding gets: the REA tool used, file path, offset
   or address, and the evidence summary REA returned. Anything not proven is labelled
   UNVERIFIED. Keep "planned / attempted / completed / verified" separate.
5. Smallest step first. Prefer cheap checks (folder scan, file header bytes) before heavy
   ones (full Ghidra analysis of the game exe). Ask me before any step that will take
   more than ~10 minutes or download/install anything.

ORDER OF WORK
Step 1 - Fingerprint the install.
  Run REA inspect_desktop_application on the game install. Report: engine/version clues,
  Content/Paks or IoStore files, executables, anti-cheat folders (identify only), mod
  loaders (e.g. UE4SS). Write results to research/install-fingerprint.md.

Step 2 - Save file format (system 09).
  On the save COPY: read the first 256 bytes and search for obvious markers. Decide:
  Unreal GVAS, compressed (zlib/oodle/zstd magic), SQLite, or custom. Then find where a
  known value lives: I will tell you an in-game value (e.g. a stack of 37 nails) before
  and after a change, and you diff two save copies to locate it. Write the structure to
  notes/systems/09-save-format.md as a table: offset, size, type, meaning, evidence,
  verified?. Then write sim/savefile.py (our own reader for the fields we understand)
  with tests using small synthetic files, not my real save.

Step 3 - Check our models against the game.
  Read notes/playtest-checklist.md. For each open question, say which REA evidence or
  playtest measurement could answer it, cheapest first. Only use the game exe (Ghidra via
  REA) for questions that playing cannot answer, and only for named things such as a
  setting name from notes/ (e.g. vein.ZombieInfectionChance) - search strings, follow
  references, and report the behaviour in plain words.

Step 4 - Update the repo.
  Update the matching notes/systems/NN-*.md tables (tick Verified, add evidence), adjust
  numbers in sim/*Config classes, run `python -m pytest tests`, and commit each system
  separately with a clear message. Do not push until I say so.

REPORT FORMAT (after every step)
1. Period + sources (which REA tools, which files)
2. Completed work with evidence
3. Decisions I approved
4. Open questions / blockers / uncertainties (UNVERIFIED items listed)
5. Next decision needed from me
```

## Why not the generic prompt from the video
The Gemini prompt ("decompile the binary, identify business logic, map all external API requests, provide a rebuild plan") is fine for a small app, but for Vein:
- **Decompiling first is the most expensive step.** A UE5 game exe is enormous; most answers come faster from the folder scan, the save file, and playing.
- **"Map all external API requests"** means poking at online services — against REA's own rules and pointless for our goal.
- **No evidence or clean-room rules**, so an agent could paste Vein's code into your repo, which is exactly what gets takedowns.
- **No stopping points**, so it can't follow the Jacky/Jessy relay format.
