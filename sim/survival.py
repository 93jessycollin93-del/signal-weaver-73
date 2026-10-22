"""Clean-room survival stats model, built from Vein's observed behaviour.

See notes/systems/01-survival-stats.md. Hunger and thirst come from the
physiological model in sim/digestion.py; this module adds fatigue, stamina,
health and infection on top. Numbers live in SurvivalConfig / DigestionConfig
so they can be retuned once real values are measured in-game.
"""

from dataclasses import dataclass, field
from enum import Enum

from sim.digestion import Body, Food


class Activity(Enum):
    IDLE = "idle"
    WALK = "walk"
    SPRINT = "sprint"
    SLEEP = "sleep"


class WaterQuality(Enum):
    CLEAN = "clean"  # boiled, filtered or bottled
    DIRTY = "dirty"


# Metabolic equivalents (multiples of resting metabolic rate).
MET = {Activity.SLEEP: 0.95, Activity.IDLE: 1.3, Activity.WALK: 3.5, Activity.SPRINT: 10.0}


@dataclass
class SurvivalConfig:
    # Fatigue (energy), per hour.
    energy_drain: float = 3.0
    sleep_energy_gain: float = 12.5
    walk_energy_multiplier: float = 1.5
    sprint_energy_multiplier: float = 3.0
    low_glycogen_energy_multiplier: float = 1.3  # "hitting the wall"

    # Stamina, per hour.
    stamina_regen: float = 300.0
    stamina_sprint_cost: float = 600.0
    exhausted_stamina_penalty: float = 1.5  # sprint cost multiplier when energy < 20

    # Temperature in °C; comfort band where nothing extra happens.
    comfort_min: float = 10.0
    comfort_max: float = 28.0
    cold_energy_per_degree: float = 0.3
    heat_exhaustion_temp: float = 38.0

    # Health.
    exhausted_damage: float = 5.0    # per hour at energy 0
    infection_damage: float = 3.0    # per hour at infection 100, scaled linearly
    dirty_water_infection: float = 8.0      # per dirty drink
    contaminated_food_infection: float = 10.0
    infection_recovery: float = 0.5  # per hour when fed and hydrated

    # HUD shows a stat only outside this band (Vein 0.021 behaviour).
    hud_low: float = 25.0
    hud_high: float = 100.0


@dataclass
class Survivor:
    energy: float = 100.0     # fatigue, 0 = exhausted
    stamina: float = 100.0
    health: float = 100.0
    infection: float = 0.0
    body: Body = field(default_factory=Body)
    config: SurvivalConfig = field(default_factory=SurvivalConfig)
    _last_temp: float = field(default=20.0, repr=False)

    @property
    def alive(self) -> bool:
        return self.health > 0

    @property
    def hunger(self) -> float:
        """Satiety on the HUD scale: 100 = comfortably full, >100 stuffed, 0 = starving."""
        return max(0.0, 100.0 * self.body.satiety)

    @property
    def thirst(self) -> float:
        """Hydration on the HUD scale: 100 = normal, 0 = 10% body water lost."""
        return max(0.0, 100.0 * self.body.hydration)

    @property
    def heat_exhausted(self) -> bool:
        return self._last_temp >= self.config.heat_exhaustion_temp

    def tick(self, hours: float, activity: Activity = Activity.IDLE,
             temperature: float = 20.0) -> None:
        """Advance the simulation by `hours` of game time."""
        if not self.alive:
            return
        c = self.config
        self._last_temp = temperature
        self.body.tick(hours, MET[activity], temperature, self.infection)

        if activity is Activity.SLEEP:
            self.energy += c.sleep_energy_gain * hours
        else:
            mult = {Activity.WALK: c.walk_energy_multiplier,
                    Activity.SPRINT: c.sprint_energy_multiplier}.get(activity, 1.0)
            if self.body.glycogen_fraction < self.body.config.low_glycogen:
                mult *= c.low_glycogen_energy_multiplier
            rate = c.energy_drain * mult
            if temperature < c.comfort_min:
                rate += (c.comfort_min - temperature) * c.cold_energy_per_degree
            self.energy -= rate * hours

        if activity is Activity.SPRINT:
            cost = c.stamina_sprint_cost
            if self.energy < 20:
                cost *= c.exhausted_stamina_penalty
            self.stamina -= cost * hours
        else:
            self.stamina += c.stamina_regen * hours * min(1.0, 0.3 + self.body.glycogen_fraction)

        damage = self.body.damage_per_hour()
        if self.energy <= 0:
            damage += c.exhausted_damage
        damage += c.infection_damage * self.infection / 100.0
        self.health -= damage * hours

        if self.body.satiety > 0.5 and self.body.hydration > 0.5 and self.infection > 0:
            self.infection -= c.infection_recovery * hours

        self._clamp()

    def eat(self, food: Food) -> bool:
        """Eat something. Returns False if you threw it back up."""
        if food.contaminated:
            self.infection += self.config.contaminated_food_infection
        kept = self.body.eat(food)
        self._clamp()
        return kept

    def drink(self, ml: float, quality: WaterQuality = WaterQuality.CLEAN) -> bool:
        if quality is WaterQuality.DIRTY:
            self.infection += self.config.dirty_water_infection
        kept = self.body.drink(ml)
        self._clamp()
        return kept

    def hud_visible(self) -> dict:
        """Stats the HUD should show: only those at extremes."""
        c = self.config
        return {
            name: value
            for name, value in (("hunger", self.hunger), ("thirst", self.thirst),
                                ("energy", self.energy))
            if value < c.hud_low or value > c.hud_high
        }

    def _clamp(self) -> None:
        self.energy = min(max(self.energy, 0.0), 100.0)
        self.stamina = min(max(self.stamina, 0.0), 100.0)
        self.health = min(max(self.health, 0.0), 100.0)
        self.infection = min(max(self.infection, 0.0), 100.0)
