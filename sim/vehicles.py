"""Clean-room vehicle system, built from Vein's observed behaviour.

See notes/systems/08-vehicles.md. A car starts only with a charged battery,
fuel in the tank, a working engine and spark plugs, plus a key or a hotwire.
Fuel is siphoned from wrecks; parts are swapped, some needing mechanic skill.
"""

from collections import Counter
from dataclasses import dataclass, field

REQUIRED_PARTS = ("battery", "spark plugs", "engine")


@dataclass
class Part:
    name: str
    condition: float = 100.0  # 0..100
    mechanic_level: int = 0   # skill needed to install/remove

    @property
    def working(self) -> bool:
        return self.condition > 20.0


@dataclass
class Car:
    parts: dict = field(default_factory=dict)  # slot -> Part or None
    fuel: float = 0.0
    tank: float = 50.0
    battery_charge: float = 100.0              # % of the battery part
    has_key: bool = False
    hotwired: bool = False
    running: bool = False
    litres_per_km: float = 0.1
    start_cost: float = 5.0                    # battery % per start attempt

    def why_wont_it_start(self) -> list:
        problems = []
        for slot in REQUIRED_PARTS:
            part = self.parts.get(slot)
            if part is None:
                problems.append(f"missing {slot}")
            elif not part.working:
                problems.append(f"{slot} too damaged")
        if self.parts.get("battery") and self.battery_charge < self.start_cost:
            problems.append("battery flat")
        if self.fuel <= 0:
            problems.append("no fuel")
        if not (self.has_key or self.hotwired):
            problems.append("no key and not hotwired")
        return problems

    def start(self) -> bool:
        """Turn the key. Every attempt with a battery fitted drains it a little."""
        problems = self.why_wont_it_start()
        battery_ok = not any(p.startswith(("missing battery", "battery")) for p in problems)
        if battery_ok:
            self.battery_charge -= self.start_cost
        self.running = not problems
        return self.running

    def hotwire(self, mechanic_level: int, required: int = 1) -> bool:
        if mechanic_level >= required:
            self.hotwired = True
        return self.hotwired

    def drive(self, km: float) -> float:
        """Drive up to `km`. Returns distance actually covered."""
        if not self.running:
            return 0.0
        possible = self.fuel / self.litres_per_km
        covered = min(km, possible)
        self.fuel -= covered * self.litres_per_km
        engine = self.parts["engine"]
        engine.condition = max(0.0, engine.condition - covered * 0.05)
        self.battery_charge = min(100.0, self.battery_charge + covered * 0.5)  # alternator
        if self.fuel <= 0 or not engine.working:
            self.running = False
        return covered

    def siphon(self, into: "FuelCan", inventory: Counter) -> float:
        """Siphon fuel out of this car into a can. Needs a siphon hose."""
        if inventory["siphon hose"] < 1:
            raise ValueError("need a siphon hose")
        moved = min(self.fuel, into.capacity - into.litres)
        self.fuel -= moved
        into.litres += moved
        return moved

    def refuel(self, can: "FuelCan") -> float:
        moved = min(can.litres, self.tank - self.fuel)
        can.litres -= moved
        self.fuel += moved
        return moved

    def remove_part(self, slot: str, mechanic_level: int) -> Part:
        part = self.parts.get(slot)
        if part is None:
            raise ValueError(f"no {slot} fitted")
        if mechanic_level < part.mechanic_level:
            raise PermissionError(f"{slot} needs mechanic level {part.mechanic_level}")
        self.parts[slot] = None
        self.running = False
        return part

    def install_part(self, slot: str, part: Part, mechanic_level: int) -> None:
        if self.parts.get(slot) is not None:
            raise ValueError(f"{slot} slot is occupied")
        if mechanic_level < part.mechanic_level:
            raise PermissionError(f"{slot} needs mechanic level {part.mechanic_level}")
        self.parts[slot] = part


@dataclass
class FuelCan:
    capacity: float = 20.0
    litres: float = 0.0


def charge_battery(car: Car, hours: float, pct_per_hour: float = 20.0,
                   powered: bool = True) -> None:
    """A battery charger (found in auto shops) needs power — see sim/power.py."""
    if powered and car.parts.get("battery"):
        car.battery_charge = min(100.0, car.battery_charge + pct_per_hour * hours)
