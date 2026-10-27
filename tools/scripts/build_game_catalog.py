"""Render notes/game-catalog.md from research/game-catalog.json.

Run from the repo root: python tools/scripts/build_game_catalog.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "research" / "game-catalog.json"
OUT = ROOT / "notes" / "game-catalog.md"

CHECK = {True: "✅ fact-checked", False: "⚠️ single-pass", "spot-checked": "☑️ spot-checked",
         "licence-verified": "✅ licence read from repo"}

TIERS = [
    ("A", "Source code available: read it, fork it (no reverse engineering needed)",
     lambda r: r["feasibility"] == "fork_open_source" or r["rea_fit"] == "not_needed_open_source"),
    ("B", "REA works best: .NET / Unity Mono (decompiles to near-original C#)",
     lambda r: r["rea_fit"] == "excellent_managed_dotnet"),
    ("C", "Unity IL2CPP: REA recovers class and method names; code needs Ghidra",
     lambda r: r["rea_fit"] == "good_il2cpp_metadata"),
    ("D", "Unreal Engine: REA only detects it; code means Ghidra on a huge exe",
     lambda r: r["rea_fit"] == "unreal_detect_plus_native" and r["feasibility"] != "too_little_info"),
    ("E", "Custom native or Java: Ghidra only, or outside REA's scope",
     lambda r: r["rea_fit"] in ("native_ghidra_only", "none_or_unclear") and r["feasibility"] != "too_little_info"),
    ("F", "Unreleased, too new, or not found",
     lambda r: r["feasibility"] == "too_little_info"),
]

INTRO = """# Game catalog: what REA can actually do with each game

{total} games from Jessy's lists, researched Oct 2026 by parallel agents with web search.
{checked} rows were re-checked by a separate fact-checking agent ({corrections} corrections, mostly dates and server details, rarely the engine) or verified by hand; the rest (⚠️) are single-pass research — likely, not proven.
Every row's sources are in [research/game-catalog.json](../research/game-catalog.json). Rebuild this page with `python tools/scripts/build_game_catalog.py`.

## The honest version of "super easy"
REA's showcase is the **Touhou Reconstruction Factory**: AI agents rebuilt old 2D Touhou games into playable ports — **starting from the original game files**, over **~2–3 weeks and ~1,000 commits per game**, for games whose executables are around 1 MB. The games below are 100–1000× bigger, and REA's own rules forbid copying proprietary code or assets. REA doesn't *create* games; it explains how a game you have on disk works, and you rebuild the ideas yourself. The tiers show where that's cheap and where it isn't.

## Summary
"""

OUTRO = """## How to use this
1. **Learn how survival systems are built, legally and free:** tier A — real source code, no REA needed. Cataclysm: DDA is the deepest survival sim; Luanti and Veloren for engines; Unturned is non-commercial only.
2. **See how a commercial game's system works:** tier B games you own — point REA at the game's managed assemblies (e.g. `Assembly-CSharp.dll`). Learn the idea, write your own code; don't copy theirs.
3. **Tier D (Unreal — Vein included):** free dedicated servers, config files, save-file diffs and playtesting beat decompiling. See [tools/rea-playbook.md](../tools/rea-playbook.md).
4. Never point REA at anti-cheat (EAC, BattlEye), DRM or online services.
"""


def cell(s, n=150):
    s = (s or "").replace("|", "/").replace("\n", " ")
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"


def main():
    data = json.loads(DATA.read_text())
    rows = data["rows"]
    placed, sections, summary = set(), [], []
    for key, title, pred in TIERS:
        sel = sorted((r for r in rows if r["name"] not in placed and pred(r)), key=lambda r: r["name"].lower())
        placed |= {r["name"] for r in sel}
        summary.append(f"| **{key}** | {title} | {len(sel)} | {', '.join(r['name'] for r in sel)} |")
        lines = [f"## {key} — {title}\n", "| Game | Engine | Legal way to study it | System worth recreating | Checked |",
                 "|---|---|---|---|---|"]
        lines += [f"| **{cell(r['name'])}** | {cell(r['engine'], 90)} | {cell(r['legal_route'])} | "
                  f"{cell(r['signature_system'])} | {CHECK[r['fact_checked']]} |" for r in sel]
        sections.append("\n".join(lines) + "\n")
    missing = [r["name"] for r in rows if r["name"] not in placed]
    assert not missing, f"rows in no tier: {missing}"
    checked = sum(1 for r in rows if r["fact_checked"] is not False)
    text = INTRO.format(total=len(rows), checked=checked, corrections=len(data["corrections"]))
    text += "| Tier | What it means | Games | Which |\n|---|---|---|---|\n" + "\n".join(summary) + "\n\n"
    text += "\n".join(sections) + OUTRO
    OUT.write_text(text)
    print(f"wrote {OUT} ({len(rows)} games)")


if __name__ == "__main__":
    main()
