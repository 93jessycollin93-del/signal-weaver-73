"""Write game/tests/golden.json: reference values from the Python models.

The Godot port (game/sim/*.gd) must reproduce these numbers. Run from the
repo root:  python tools/scripts/gen_golden.py
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from sim.digestion import FOODS, Body  # noqa: E402
from sim.survival import Activity, Survivor, WaterQuality  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[2] / "game" / "tests" / "golden.json"


def body_state(b):
    return {"stomach": b.stomach.volume, "glycogen": b.glycogen, "fat": b.fat_store,
            "muscle": b.muscle_protein, "water": b.body_water, "bladder": b.bladder,
            "colon": b.colon_solids + b.colon_water, "satiety": b.satiety,
            "kcal_burned": b.kcal_burned}


def survivor_state(s):
    return {**body_state(s.body), "energy": s.energy, "stamina": s.stamina,
            "health": s.health, "infection": s.infection}


def meal():
    b = Body()
    b.eat(FOODS["canned beans"])
    b.eat(FOODS["bread slice"])
    b.drink(300)
    snaps = []
    for _ in range(8):
        b.tick(1)
        snaps.append(body_state(b))
    return snaps


def mixed_activity():
    s = Survivor()
    plan = [(0.5, Activity.SPRINT, 35), (2, Activity.WALK, -5), (1, Activity.IDLE, 20),
            (8, Activity.SLEEP, 12), (3, Activity.IDLE, 20)]
    s.eat(FOODS["chocolate bar"])
    s.drink(500, WaterQuality.DIRTY)
    snaps = []
    for hours, act, temp in plan:
        s.tick(hours, act, temp)
        snaps.append(survivor_state(s))
    return snaps


def water_only_days():
    s = Survivor()
    snaps = []
    for _ in range(5):
        for hour in range(24):
            asleep = hour < 8
            if not asleep:
                s.drink(150)
            s.tick(1, Activity.SLEEP if asleep else Activity.IDLE)
            if s.body.needs_toilet["pee"]:
                s.body.urinate()
        snaps.append(survivor_state(s))
    return snaps


if __name__ == "__main__":
    data = {"meal": meal(), "mixed_activity": mixed_activity(), "water_only_days": water_only_days()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print(f"wrote {OUT}")
