"""Clean-room survival stats model, built from Vein's observed behaviour.

See notes/systems/01-survival-stats.md. All numbers are our own and live in
SurvivalConfig so they can be retuned once real values are measured in-game.
"""

from dataclasses import dataclass, field
from enum import Enum


class Activity(Enum):
    IDLE = "idle"
    WALK = "walk"
    SPRINT = "sprint"
    SLEEP = "sleep"


class WaterQuality(Enum):
    CLEAN = "clean"  # boiled, filtered or bottled
    DIRTY = "dirty"


@dataclass
class SurvivalConfig:
    # Per-hour drain at idle, in points out of 100.
    hunger_drain: float = 4.0
    thirst_drain: float = 6.0
    energy_drain: float = 3.0
    sleep_energy_gain: float = 12.5

    # Multipliers applied on top of the base drain.
    activity_multiplier: dict = field(default_factory=lambda: {
        Activity.IDLE: 1.0,
        Activity.WALK: 1.5,
        Activity.SPRINT: 3.0,
        Activity.SLEEP: 0.5,
    })
    infection_hunger_multiplier: float = 2.0  # at infection 100, scaled linearly

    # Stamina, per hour.
    stamina_regen: float = 300.0
    stamina_sprint_cost: float = 600.0
    exhausted_stamina_penalty: float = 1.5  # sprint cost multiplier when energy < 20

    # Temperature in °C; comfort band where nothing extra happens.
    comfort_min: float = 10.0
    comfort_max: float = 28.0
    cold_energy_per_degree: float = 0.3   # extra energy drain per degree below comfort
    heat_thirst_per_degree: float = 0.4   # extra thirst drain per degree above comfort
    heat_exhaustion_temp: float = 38.0

    # Overfilling: stats can go above 100 up to this limit, which is fatal.
    overfill_limit: float = 130.0
    overfill_health_damage: float = 20.0  # per hour while above 100

    # Health.
    starving_damage: float = 5.0     # per hour per empty stat
    infection_damage: float = 3.0    # per hour at infection 100, scaled linearly
    dirty_water_infection: float = 8.0  # per drink of dirty water
    infection_recovery: float = 0.5  # per hour when healthy and fed

    # HUD shows a stat only outside this band (Vein 0.021 behaviour).
    hud_low: float = 25.0
    hud_high: float = 100.0


@dataclass
class Survivor:
    hunger: float = 80.0      # fullness, 0 = starving
    thirst: float = 80.0      # hydration, 0 = dehydrated
    energy: float = 100.0     # 0 = exhausted
    stamina: float = 100.0
    health: float = 100.0
    infection: float = 0.0
    config: SurvivalConfig = field(default_factory=SurvivalConfig)

    @property
    def alive(self) -> bool:
        return self.health > 0

    @property
    def heat_exhausted(self) -> bool:
        return self._last_temp >= self.config.heat_exhaustion_temp

    _last_temp: float = field(default=20.0, repr=False)

    def tick(self, hours: float, activity: Activity = Activity.IDLE,
             temperature: float = 20.0) -> None:
        """Advance the simulation by `hours` of game time."""
        if not self.alive:
            return
        c = self.config
        self._last_temp = temperature
        act = c.activity_multiplier[activity]
        infection_frac = self.infection / 100.0

        hunger_mult = act * (1.0 + (c.infection_hunger_multiplier - 1.0) * infection_frac)
        self.hunger -= c.hunger_drain * hunger_mult * hours

        thirst_rate = c.thirst_drain * act
        if temperature > c.comfort_max:
            thirst_rate += (temperature - c.comfort_max) * c.heat_thirst_per_degree
        self.thirst -= thirst_rate * hours

        if activity is Activity.SLEEP:
            self.energy += c.sleep_energy_gain * hours
        else:
            energy_rate = c.energy_drain * act
            if temperature < c.comfort_min:
                energy_rate += (c.comfort_min - temperature) * c.cold_energy_per_degree
            self.energy -= energy_rate * hours

        if activity is Activity.SPRINT:
            cost = c.stamina_sprint_cost
            if self.energy < 20:
                cost *= c.exhausted_stamina_penalty
            self.stamina -= cost * hours
        else:
            self.stamina += c.stamina_regen * hours

        damage = 0.0
        for value in (self.hunger, self.thirst, self.energy):
            if value <= 0:
                damage += c.starving_damage
        for value in (self.hunger, self.thirst):
            if value > 100:
                damage += c.overfill_health_damage
        damage += c.infection_damage * infection_frac
        self.health -= damage * hours

        well_fed = self.hunger > 50 and self.thirst > 50
        if well_fed and self.infection > 0:
            self.infection -= c.infection_recovery * hours

        self._clamp()

    def eat(self, amount: float) -> None:
        self.hunger += amount
        self._check_overfill()

    def drink(self, amount: float, quality: WaterQuality = WaterQuality.CLEAN) -> None:
        self.thirst += amount
        if quality is WaterQuality.DIRTY:
            self.infection += self.config.dirty_water_infection
        self._check_overfill()

    def hud_visible(self) -> dict:
        """Stats the HUD should show: only those at extremes."""
        c = self.config
        return {
            name: value
            for name, value in (("hunger", self.hunger), ("thirst", self.thirst),
                                ("energy", self.energy))
            if value < c.hud_low or value > c.hud_high
        }

    def _check_overfill(self) -> None:
        if max(self.hunger, self.thirst) >= self.config.overfill_limit:
            self.health = 0.0
        self._clamp()

    def _clamp(self) -> None:
        limit = self.config.overfill_limit
        self.hunger = min(max(self.hunger, 0.0), limit)
        self.thirst = min(max(self.thirst, 0.0), limit)
        self.energy = min(max(self.energy, 0.0), 100.0)
        self.stamina = min(max(self.stamina, 0.0), 100.0)
        self.health = min(max(self.health, 0.0), 100.0)
        self.infection = min(max(self.infection, 0.0), 100.0)
