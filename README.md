# Vein Reverse Engineering

Research notes, scripts and tooling for understanding **Vein** (Ramjet Studios), an Unreal Engine 5 survival game.

> This repo holds **notes and original code only**. Never commit game files, extracted assets, `.pak`/`.utoc`/`.ucas` archives, AES keys or binaries — see `.gitignore`.

## Layout

| Folder | What goes there |
|---|---|
| `notes/` | Findings written up as Markdown: engine version, file layout, systems |
| `research/structs/` | Reconstructed classes and structs (SDK dumps, hand-written headers) |
| `research/offsets/` | Offsets and signatures, tagged with the game build they apply to |
| `scripts/` | Your own helper scripts (Ghidra/IDA scripts, Lua mods, parsers) |
| `tools/` | Pointers to external tools and how they're configured — not the tools themselves |

## Getting started

1. Read `notes/00-setup.md` for the toolchain.
2. Record the game build you're looking at in `notes/builds.md` before writing down any offsets — they change every patch.
