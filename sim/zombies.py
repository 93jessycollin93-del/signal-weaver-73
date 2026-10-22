"""Clean-room zombie senses and combat, built from Vein's observed behaviour.

See notes/systems/06-zombies.md. Zombies notice you by sight, hearing and
smell. Busy idle zombies notice less. Sneaking masks your noise, gunfire is
extra loud, and every hit has a chance to infect you.
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum

from sim.survival import Survivor


class State(Enum):
    IDLE = "idle"              # doing an idle task
    INVESTIGATING = "investigating"
    CHASING = "chasing"
    DEAD = "dead"


@dataclass
class ZombieSettings:
    health: float = 40.0              # community-reported default
    sight_range: float = 25.0         # metres in daylight
    sight_multiplier: float = 1.0
    hearing_multiplier: float = 1.0
    smell_range: float = 3.0
    idle_awareness: float = 0.5       # idle zombies see/hear at half range
    darkness_sight: float = 0.4       # sight range multiplier at night
    firearm_multiplier: float = 2.0   # gunfire is twice as audible (0.021)
    infection_chance: float = 0.01    # per hit; 0 disables infection
    hit_damage: float = 10.0
    lose_interest_hours: float = 0.1  # stop investigating after this long


@dataclass
class Noise:
    position: tuple
    radius: float       # metres it carries at multiplier 1
    firearm: bool = False


@dataclass
class Player:
    position: tuple
    sneaking: bool = False
    sneak_skill: float = 0.0  # 0..1; how much of your noise sneaking hides
    survivor: Survivor = field(default_factory=Survivor)

    def footstep_noise(self) -> Noise:
        radius = 8.0
        if self.sneaking:
            radius *= 1.0 - 0.6 * (0.5 + 0.5 * self.sneak_skill)
        return Noise(self.position, radius)


@dataclass
class Zombie:
    position: tuple
    settings: ZombieSettings = field(default_factory=ZombieSettings)
    state: State = State.IDLE
    health: float = None
    target: tuple = None
    _investigate_left: float = 0.0

    def __post_init__(self):
        if self.health is None:
            self.health = self.settings.health

    def _awareness(self) -> float:
        return self.settings.idle_awareness if self.state is State.IDLE else 1.0

    def can_see(self, player: Player, daylight: bool) -> bool:
        s = self.settings
        rng = s.sight_range * s.sight_multiplier * self._awareness()
        if not daylight:
            rng *= s.darkness_sight
        return math.dist(self.position, player.position) <= rng

    def can_hear(self, noise: Noise) -> bool:
        s = self.settings
        radius = noise.radius * s.hearing_multiplier * self._awareness()
        if noise.firearm:
            radius *= s.firearm_multiplier
        return math.dist(self.position, noise.position) <= radius

    def can_smell(self, player: Player) -> bool:
        return math.dist(self.position, player.position) <= self.settings.smell_range

    def update(self, hours: float, player: Player, noises=(), daylight: bool = True) -> State:
        if self.state is State.DEAD:
            return self.state
        if self.can_see(player, daylight) or self.can_smell(player):
            self.state, self.target = State.CHASING, player.position
            return self.state
        heard = [n for n in (player.footstep_noise(), *noises) if self.can_hear(n)]
        if heard:
            loudest = max(heard, key=lambda n: n.radius)
            self.state, self.target = State.INVESTIGATING, loudest.position
            self._investigate_left = self.settings.lose_interest_hours
            return self.state
        if self.state is not State.IDLE:
            self._investigate_left -= hours
            if self._investigate_left <= 0:
                self.state, self.target = State.IDLE, None
        return self.state

    def attack(self, player: Player, rng: random.Random) -> bool:
        """One hit. Returns True if this hit infected the player."""
        player.survivor.health = max(0.0, player.survivor.health - self.settings.hit_damage)
        if rng.random() < self.settings.infection_chance:
            player.survivor.infection = min(100.0, player.survivor.infection + 25.0)
            return True
        return False

    def take_damage(self, amount: float) -> None:
        self.health -= amount
        if self.health <= 0:
            self.health, self.state = 0.0, State.DEAD
