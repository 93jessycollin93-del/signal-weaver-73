"""Clean-room power system, built from Vein's observed behaviour.

See notes/systems/03-power.md. City power runs until the shutoff day. After
that a base runs on generators (burn fuel, power anything in their radius),
solar panels (daytime only) and batteries (store the surplus).
"""

import math
from dataclasses import dataclass, field

from sim.calendar import Calendar


@dataclass
class Device:
    name: str
    watts: float
    position: tuple = (0.0, 0.0)
    priority: int = 0  # higher is served first when power is short
    powered: bool = False


@dataclass
class Generator:
    watts: float = 3000.0
    fuel: float = 0.0              # litres
    fuel_capacity: float = 20.0
    litres_per_kwh: float = 0.4
    radius: float = 15.0           # metres; devices inside need no wiring
    position: tuple = (0.0, 0.0)
    running: bool = True

    def refuel(self, litres: float) -> float:
        added = min(litres, self.fuel_capacity - self.fuel)
        self.fuel += added
        return added

    def max_output(self, hours: float) -> float:
        """Watt-hours this generator can supply over `hours`."""
        if not self.running or self.fuel <= 0:
            return 0.0
        by_fuel = self.fuel / self.litres_per_kwh * 1000.0
        return min(self.watts * hours, by_fuel)

    def burn(self, watt_hours: float) -> None:
        self.fuel = max(0.0, self.fuel - watt_hours / 1000.0 * self.litres_per_kwh)

    def covers(self, device: Device) -> bool:
        return math.dist(self.position, device.position) <= self.radius


@dataclass
class SolarPanel:
    watts: float = 400.0

    def output(self, hours: float, calendar: Calendar) -> float:
        return self.watts * hours if calendar.is_daytime else 0.0


@dataclass
class Battery:
    capacity: float = 50_000.0  # Wh — matches the community figure for a makeshift battery
    charge: float = 0.0

    def store(self, watt_hours: float) -> float:
        stored = min(watt_hours, self.capacity - self.charge)
        self.charge += stored
        return stored

    def take(self, watt_hours: float) -> float:
        taken = min(watt_hours, self.charge)
        self.charge -= taken
        return taken


@dataclass
class PowerNetwork:
    """Everything wired together at one base.

    A device is on the network if it is wired in, or sits inside a running
    generator's radius. Supply order each tick: solar, city grid, batteries,
    then generators (fuel is the scarce resource). Spare solar or city power
    charges the batteries.
    """
    generators: list = field(default_factory=list)
    panels: list = field(default_factory=list)
    batteries: list = field(default_factory=list)
    wired: list = field(default_factory=list)
    nearby: list = field(default_factory=list)  # placed, but not wired
    on_city_grid: bool = True

    def connected_devices(self) -> list:
        devices = list(self.wired)
        for d in self.nearby:
            if d not in devices and any(g.running and g.covers(d) for g in self.generators):
                devices.append(d)
        return devices

    def tick(self, hours: float, calendar: Calendar) -> dict:
        devices = sorted(self.connected_devices(), key=lambda d: -d.priority)
        for d in self.wired + self.nearby:
            d.powered = False

        free = sum(p.output(hours, calendar) for p in self.panels)
        city = self.on_city_grid and calendar.city_power_on
        stored = sum(b.charge for b in self.batteries)
        gen_max = sum(g.max_output(hours) for g in self.generators)

        demand_served = 0.0
        if city:
            for d in devices:
                d.powered = True
            demand_served = sum(d.watts * hours for d in devices)
            free = float("inf")
        else:
            budget = free + stored + gen_max
            for d in devices:
                need = d.watts * hours
                if need <= budget - demand_served:
                    d.powered = True
                    demand_served += need

        # Pay for what was served: solar first, then batteries, then fuel.
        remaining = demand_served
        from_solar = min(remaining, free)
        remaining -= from_solar
        for b in self.batteries:
            remaining -= b.take(remaining)
        for g in self.generators:
            if remaining <= 0:
                break
            use = min(remaining, g.max_output(hours))
            g.burn(use)
            remaining -= use

        if city:
            for b in self.batteries:  # the grid tops batteries up
                b.store(b.capacity)
        else:
            surplus = sum(p.output(hours, calendar) for p in self.panels) - from_solar
            for b in self.batteries:
                surplus -= b.store(max(surplus, 0.0))

        return {d.name: d.powered for d in devices}
