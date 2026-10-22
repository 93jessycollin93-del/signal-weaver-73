# REA playbook — tested, not guessed

Learned by running REA 6.7.0 + Ghidra 12.1.4 on a practice target (Oct 22, 2026): a **stripped** C binary of my own with a scrambled, checksummed save format — the same kind of problem as Vein's `.vns`. Result: full format recovered and a working decoder written in ~45 s of tool time.

## Setup facts (verified)
| Thing | Fact |
|---|---|
| Install | `npm install rea-agents` (or `npx rea-agents …`), Node 22.19+ |
| Ghidra | **Must be 12.1.x** (`rea doctor` rejects others). Point `GHIDRA_INSTALL_DIR` at the extracted folder |
| Java | Full **JDK 21+** (not a JRE) |
| Linux | needs `ps` (procps) on PATH |
| Check | `rea doctor --format json` → `providerInspections[ghidra].available: true` |
| Agent | `npx rea-agents setup` registers the MCP server; the agent must **restart** before the tools appear |

## Costs (measured on a 14 KB binary)
| Step | Time |
|---|---|
| `inspect-artifact` (no engine) | ~1 s |
| Any Ghidra-backed CLI call | ~10–13 s **each** — every CLI call restarts Ghidra |
| `--snapshot` file | stores annotations only (8 KB); **does not** skip re-analysis |

➡ **Efficiency rule:** one-off question → CLI. Multi-step investigation → REA as an **MCP server** (one live session), or batch several questions per CLI call. A large game exe (100 MB+) will take far longer per analysis — do the cheap steps first.

## The workflow that worked
1. **Fingerprint** — `rea inspect-artifact <file>` (1 s): format, hashes, what's inside.
2. **Overview** — `rea inspect <file> --provider ghidra`: sections, counts.
3. **Find the I/O** — `rea search <file> fopen --kind procedures --provider ghidra`. Short strings like `"wb"` are **not indexed**; search imports instead (Linux `fopen`/`fwrite`; Windows `CreateFileW`/`WriteFile`; Unreal `SaveGameToSlot`, `GVAS`).
4. **Who calls it** — `rea xrefs <file> <import address> --provider ghidra` → caller address.
5. **Read it** — `rea decompile <file> <caller address> --provider ghidra` → pseudocode. Look for constants and the write order.
6. **Write a decoder from the evidence**, then **verify** on several saves (checksums must match).

Output is Evidence JSON; the answer is in `normalized_result`. Use `--filter-output normalized_result` / `--token-limit` to keep it small.

## The cheapest method of all: diff two saves
Change one known value in-game, save, copy the file, `cmp -l a.sav b.sav`. In the practice target, item count 37→38 changed **only** that byte **plus the last 4 bytes** (checksum) — even though the body was XOR-scrambled. Diffs locate fields before any decompiling.

## Constants worth recognising
| Bytes / value | Means |
|---|---|
| `GVAS` | Unreal SaveGame (property tags like `IntProperty` follow — readable without Ghidra) |
| `78 9C` / `78 DA` | zlib stream |
| `28 B5 2F FD` | zstd |
| `SQLite format 3` | SQLite → `rea inspect-sqlite-database` |
| `0x811C9DC5`, `0x01000193` | FNV-1a hash |
| `0xEDB88320` / `0x04C11DB7` | CRC-32 |
| `key = key*a + b` inside a byte loop | rolling XOR scramble |

## Applying it to Vein (when a save file / server build is available)
1. Hex-dump the first 64 bytes of a `.vns` copy → match against the table above.
2. Diff two save copies around one in-game change.
3. Only then: Ghidra on the **dedicated server** binary (smaller than the client), searching for the save path/extension and following xrefs to the writer.
4. Our decoder lives in our repo; never paste decompiled game code into it.

Practice decoder: [research/practice/decode_practice_save.py](../research/practice/decode_practice_save.py) (for my own test program, not Vein).
