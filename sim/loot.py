"""Clean-room loot and world persistence, built from Vein's observed behaviour.

See notes/systems/05-loot.md. Containers roll from a loot table, scaled by a
scarcity level (0-4, like vein.Scarcity.Difficulty). Emptied containers
refill after an interval (like vein.ContainersRespawn.Interval). Anything
dropped in the world stays exactly where it was left.
"""

import random
from collections import Counter
from dataclasses import dataclass, field

# Multiplier on a container's rolls at each scarcity level (ours).
SCARCITY_KEEP = {0: 1.5, 1: 1.2, 2: 1.0, 3: 0.6, 4: 0.3}


@dataclass(frozen=True)
class LootEntry:
    item: str
    weight: float
    min_count: int = 1
    max_count: int = 1


@dataclass(frozen=True)
class LootTable:
    name: str
    entries: tuple
    rolls: int = 4


@dataclass
class LootSettings:
    scarcity: int = 2                  # 0 (plenty) .. 4 (scarce)
    respawn_enabled: bool = True
    respawn_interval_s: float = 10800  # 3 hours; allowed 600..43200

    def __post_init__(self):
        if not 0 <= self.scarcity <= 4:
            raise ValueError("scarcity must be 0..4")
        if not 600 <= self.respawn_interval_s <= 43200:
            raise ValueError("respawn interval must be 600..43200 seconds")


def roll(table: LootTable, settings: LootSettings, rng: random.Random) -> Counter:
    rolls = round(table.rolls * SCARCITY_KEEP[settings.scarcity])
    items = Counter()
    weights = [e.weight for e in table.entries]
    for _ in range(rolls):
        entry = rng.choices(table.entries, weights)[0]
        items[entry.item] += rng.randint(entry.min_count, entry.max_count)
    return items


@dataclass
class Container:
    table: LootTable
    items: Counter = field(default_factory=Counter)
    emptied_at: float = None  # world time in seconds when last emptied
    generated: bool = False

    def open(self, now: float, settings: LootSettings, rng: random.Random) -> Counter:
        """Look inside. First open generates loot; refills follow the respawn rule."""
        if not self.generated:
            self.items = roll(self.table, settings, rng)
            self.generated = True
        elif (not self.items and settings.respawn_enabled and self.emptied_at is not None
              and now - self.emptied_at >= settings.respawn_interval_s):
            self.items = roll(self.table, settings, rng)
            self.emptied_at = None
        return self.items

    def take(self, item: str, count: int, now: float) -> int:
        taken = min(count, self.items[item])
        self.items[item] -= taken
        self.items += Counter()  # drop zero counts
        if not self.items:
            self.emptied_at = now
        return taken

    def put(self, item: str, count: int) -> None:
        self.items[item] += count
        self.emptied_at = None


@dataclass
class World:
    """Every item on the ground keeps its exact position until picked up."""
    ground: dict = field(default_factory=dict)  # position -> Counter

    def drop(self, position: tuple, item: str, count: int = 1) -> None:
        self.ground.setdefault(position, Counter())[item] += count

    def pick_up(self, position: tuple, item: str, count: int = 1) -> int:
        pile = self.ground.get(position, Counter())
        taken = min(count, pile[item])
        pile[item] -= taken
        pile += Counter()
        if pile:
            self.ground[position] = pile
        else:
            self.ground.pop(position, None)
        return taken

    def snapshot(self) -> dict:
        """Plain data for saving: {"x,y": {item: count}}."""
        return {f"{x},{y}": dict(pile) for (x, y), pile in self.ground.items()}

    @classmethod
    def restore(cls, data: dict) -> "World":
        world = cls()
        for key, pile in data.items():
            x, y = (float(v) for v in key.split(","))
            world.ground[(x, y)] = Counter(pile)
        return world
