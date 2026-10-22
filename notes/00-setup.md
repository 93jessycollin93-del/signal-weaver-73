# Toolchain setup

Vein runs on Unreal Engine 5. The standard UE toolchain applies.

## Assets (`.pak` / IoStore `.utoc` + `.ucas`)
- **FModel** — browse and export packaged assets. Needs the right UE version and, if the paks are encrypted, the AES key.
- **UEViewer (umodel)** — alternative viewer for meshes and textures.
- **Mappings (`.usmap`)** — UE5 games use unversioned properties; generate a mappings file (e.g. with UE4SS) so FModel can parse them.

## Runtime / code
- **UE4SS** — injects into the running game: dumps the SDK (classes, structs, offsets), Lua scripting, live property viewer.
- **Ghidra** or **IDA** — static analysis of the game executable.
- **x64dbg** / **Cheat Engine** — dynamic debugging and memory inspection.

## Before you start
- [ ] Find the exact UE version (check the exe's file properties or UE4SS output) → write it in `builds.md`
- [ ] Check whether paks are encrypted
- [ ] Generate a `.usmap` mappings file
- [ ] Dump the SDK with UE4SS into `research/structs/` (headers only, no binaries)
