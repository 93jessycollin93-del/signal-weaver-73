# Playtest checklist

Every open question from notes/systems/, in one place. Tick them off while playing (or with the UE4SS live property viewer), then I'll update the models with real numbers.

## 01 — Survival stats
- [ ] [VERIFY] Exact hunger/thirst drop rates per in-game hour while idle, and do they change with activity?
- [ ] [VERIFY] Is there a separate sleep/tiredness bar, and what does it affect?
- [ ] How does "too full" work — a separate threshold above 100%, or vomiting?
- [ ] What raises infection, and can it be cured?
- [ ] Does body temperature exist as a number, or only as cold/hot states?
- [ ] Which property names show up in the UE4SS dump for the player character's stats?

## 02 — Water
- [ ] Is well water dirty, or clean? Does a well need power to pump?
- [ ] Barrel capacity, jug capacity, litres per sink/shower/toilet use.
- [ ] Does rain fill barrels? Do barrels or pipes freeze in winter?
- [ ] When several sources hang off one fuse box, which is used first?
- [ ] Does dirty water from a tap show a warning in the UI?

## 03 — Power
- [ ] Generator wattage, tank size, burn rate (litres per hour, and does it depend on load?).
- [ ] Exact power radius in metres, and the hookup-range setting's name/unit.
- [ ] Device wattages (fridge, lights, heater, freezer, well pump, electric stove).
- [ ] What happens when demand exceeds supply — everything off, or some devices stay on?
- [ ] Does solar output change with weather or season?
- [ ] Does the city grid charge batteries before shutoff?

## 04 — Building
- [ ] Cabinet radius, and does it extend vertically?
- [ ] Decay rate per piece type; does decay stop at some minimum?
- [ ] What does a repair cost — a share of the original materials, or a flat item?
- [ ] Can you build inside existing (pre-placed) houses, and do those decay?
- [ ] Is there structural support / collapse when a supporting piece is removed?
- [ ] Do zombies damage structures? Is base damage a server setting? (players mention "base damage off")

## 05 — Loot & world persistence
- [ ] Is the respawn interval real-time or game-time? Does it only count while nobody is nearby?
- [ ] Does a partly looted container refill, or only a fully empty one?
- [ ] Does higher scarcity mean fewer rolls, worse items, or both?
- [ ] Do containers players have put items into ever respawn (overwriting their stash)?
- [ ] Are dropped items ever cleaned up (despawn), e.g. on server restart?

## 06 — Zombies: senses, AI, infection
- [ ] Actual sight range by day/night, and is there a vision cone?
- [ ] Footstep noise radius walking vs sprinting vs sneaking; how the sneak skill scales.
- [ ] Does infection on a hit add a fixed amount, or start a progressing sickness?
- [ ] How do hordes form and move? Do zombies respawn in cleared areas?
- [ ] Do zombies break doors or walls (link to 04 building)?

## 07 — Weather, seasons, day/night
- [ ] Are seasons in the current build, and how many days is each?
- [ ] Is there a temperature number anywhere (UI, UE4SS property), or only cold/hot states?
- [ ] Which weather types exist (rain, fog, snow, storms)? Does rain fill barrels (02) or cut solar (03)?
- [ ] Does being indoors or near a fire/heater change body temperature?
- [x] Day length: 65 real minutes at defaults (`vein.Time.*`, see below).

## 08 — Vehicles
- [ ] Full list of part slots (tyres, radiator, alternator, doors, windows?).
- [ ] Does hotwiring need a skill level or a tool, and can it fail?
- [ ] Fuel use per km and tank size; does fuel go stale over time?
- [ ] Does the battery recharge while driving?
- [ ] Mechanic level needed per part; how mechanic XP is earned.
- [ ] Do engine noise and headlights attract zombies (link to 06)?
