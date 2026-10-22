# 01b — Digestion, metabolism and hydration (realistic model)

Our own design, built from human physiology, not from Vein. It replaces the simple hunger/thirst meters from 01: the HUD values are now *read out* of the body instead of being counters.

## The chain
```
mouth → STOMACH ──(water: fast; food: ~2 kcal/min, slower when fatty)──→ SMALL INTESTINE
                                                                         │ absorbs carbs, protein, fat, water
                                                                         │ (what isn't absorbed moves on)
                                                                         ▼
                                                                       COLON ── reabsorbs water ──→ stool → toilet
absorbed carbs  → GLYCOGEN (max 500 g) ── overflow ──→ FAT
absorbed fat    → FAT STORE (~12 kg)
absorbed protein→ MUSCLE repair, rest burned like carbs
absorbed water  → BODY WATER (~42 L) ──→ kidneys ──→ BLADDER → toilet
                                       └─→ breath, skin, sweat
energy burned   = BMR × activity (MET) × fever + shivering
                  paid from glycogen + fat (mix depends on activity);
                  muscle once glycogen is low; only muscle once fat is gone
```

## What the player feels
| HUD value | Comes from |
|---|---|
| Hunger (satiety) | 50% stomach stretch + 10% food still being absorbed + 40% glycogen stores. >100 = stuffed |
| Thirst (hydration) | Body water: 100 normal, 0 = 10% lost, >100 = overhydrated |
| Toilet urges | Bladder ≥ 300 ml; colon ≥ 250 g. Ignore them too long → accident |
| Stamina recovery | Slower with empty glycogen |
| Fatigue | Drains faster with empty glycogen ("hitting the wall") |
| Health damage | Dehydration past 8% (lethal at 15%); muscle loss past 25% (lethal at 45%) |

## Checked against real physiology (from `tests/`)
| Scenario | Model | Reality |
|---|---|---|
| 400 kcal meal leaves stomach | ~3 h | 2–4 h |
| No food, no water | dies day 4 | ~3–4 days |
| Dry food, no water | dies day 4 | ~3–4 days |
| Water only | dies ~day 32 (fat 12 → 4 kg, ~30% muscle lost) | ~30–60 days |
| Sprinting 1 h at 35 °C | ~1.1 L sweat | 1–1.5 L/h |
| Stomach limit before vomiting | ~3 L | 1–1.5 L comfortable, ~4 L extreme |

## Efficiency
Every stage uses exact exponential/linear solutions; long ticks are split into 15-min steps. **~25 µs per survivor per in-game hour.** One big tick matches 180 one-minute ticks within 2%.

## Deliberate differences from Vein
- **Overeating/overdrinking → vomiting, not death.** Vein 0.008 makes overeating fatal; we chose realism. Change `vomit_stomach_ml` or add a rule if the Vein behaviour is wanted.
- **Infection raises hunger through fever** (+30% metabolism at infection 100), which is the real mechanism behind the "insatiable appetite" players report.
- **Canned food contains water.** Eating wet food delays dehydration, as in real life.

## Not modelled yet (ideas)
- Vitamins and minerals (scurvy etc.), electrolytes/salt, hyponatremia from huge water intake.
- Hunger fading after ~3 days of fasting (ketosis).
- Food spoilage over time feeding `contaminated`; alcohol and caffeine; diarrhoea from food poisoning.
- Body weight changing movement speed or carry capacity.

## Code
`sim/digestion.py` (`Body`, `Food`, `FOODS`, `DigestionConfig`) · used by `sim/survival.py` · tests in `tests/test_digestion.py`, `tests/test_survival.py`.
