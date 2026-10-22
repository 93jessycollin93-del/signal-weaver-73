# REA — Reverse Engineer Anything

Studied from source: `morluto/rea` at commit `c537c52` (2026-10-21), npm package `rea-agents` 6.7.0, MIT licence. Read only — not installed or run here.

## What it is
An **MCP server** (plus a `rea` CLI) written in TypeScript/Node. It doesn't do the thinking — your AI agent (Claude Code, Codex, Cursor…) does. REA gives the agent ~138 tools that open a target, pull out facts, and return each conclusion with **evidence** (file offsets, byte ranges, SHA-256 hashes) and a list of **unknowns**.

```
You ──ask──▶ Agent (Claude Code) ──MCP tool call──▶ REA server ──drives──▶ Ghidra / IDA / Hopper /
   ◀─answer─        ◀─evidence + unknowns─────────            ◀─results─    Frida / ADB / Chrome / built-in parsers
```

- `npx rea-agents setup` registers the MCP server with your agent and installs a workflow "skill" (instructions telling the agent which tool to use for which target). Shows a dry-run plan with backups before changing anything.
- Runs locally. Native code analysis is delegated to an engine **you install** (Ghidra free, or IDA/Hopper). REA never installs Java/Ghidra itself.
- Needs Node.js 22.19+ / 24.11+ / 26+.

## Main tool families
| Family | Examples | Engine |
|---|---|---|
| Native binaries (.exe/.dll/ELF/Mach-O) | `open_binary`, pseudocode, assembly, strings, symbols, xrefs, `read_bytes`, `search_bytes` | Ghidra / IDA / Hopper / rizin |
| Desktop install folders | `inspect_desktop_application` — fingerprints engine, runtimes, mod loaders | built-in |
| Game engines | Unity IL2CPP metadata decode, Godot PCK extract, GameMaker detect, **Unreal detect only** | built-in |
| .NET / Android / Electron / JS / websites | ILSpy, JADX, ASAR, source maps, Chrome | various |
| Runtime | Frida instrumentation, GDB, packet captures | Frida, GDB, mitmproxy |
| Rebuilding | `investigate_feature`, `trace_application_feature`, `build_reconstruction_obligation_ledger`, `verify_reconstruction` | — |

The "reconstruction ledger" turns findings into a checklist of behaviours your own version must satisfy, then checks them off — the same idea as our `notes/systems/` tables + tests.

## What it can do for Vein (Unreal Engine 5)
| Goal | REA? | How |
|---|---|---|
| Confirm engine, find paks, spot UE4SS/anti-cheat | ✅ | `inspect_desktop_application` on the Vein install folder. Detects Unreal from `Content/Paks` or the IoStore TOC signature |
| Open `.pak`/`.utoc` assets | ❌ | Not supported. Use FModel |
| Class/struct names, live values | ❌ | Use UE4SS (SDK dump, live property viewer) |
| Look at `Vein-Win64-Shipping.exe` code | ✅ | `open_binary` with Ghidra — strings, functions, pseudocode. Huge binary: slow, and needs a focused question |
| **Work out the `.vns` save format** | ✅ partly | `read_bytes` / `search_bytes` to look at headers and known values; `inspect_sqlite_database` if it turns out to be SQLite |
| Help rebuild a system | ✅ | `investigate_feature` + reconstruction ledger, alongside our `sim/` modules |

## Rules REA sets (and we follow)
From its `DISCLAIMER.md`: no bypassing DRM, licence checks or **anti-cheat**; no game cheats or tampering with online services; no **copying proprietary code or assets**. Interoperability, education and preservation are its stated purposes. Our clean-room approach (behaviour notes → our own code) fits inside that. Don't point it at Easy Anti-Cheat/BattlEye components, and don't paste decompiled Vein code into this repo.

## Setup on your PC (Windows)
1. Install **Node.js 24 LTS**.
2. Install **Ghidra** (needs a Java JDK 21). Optional if you only want folder inspection and save-file bytes.
3. Run `npx rea-agents setup`, pick **Claude Code**, review the plan, approve, restart Claude Code.
4. In Claude Code, from a clone of this repo:
   `Use REA's inspect_desktop_application on "C:\Program Files (x86)\Steam\steamapps\common\VEIN" and summarise what it finds.`
5. Then, with a **copy** of your save:
   `Use REA to read the first 256 bytes of C:\path\to\copy\Server.vns and tell me if it's GVAS, compressed, SQLite or custom.`
6. Commit what it reports to `research/` (text only — no game files).

## Sources
- https://github.com/morluto/rea (README, DISCLAIMER.md, docs/desktop-applications.md, docs/raw-binary.md, docs/mcp-prompts.md, .agents/skills/reverse-engineer-anything/SKILL.md)
- https://rea.tools/
