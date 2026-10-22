"""Clean-room building system, built from Vein's observed behaviour.

See notes/systems/04-building.md. You need the materials and tools on you to
build. A utility cabinet claims an area: pieces inside it are repaired from
the cabinet's stock, pieces outside it (or when the stock runs out) decay.
"""

import math
from collections import Counter
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Blueprint:
    name: str
    materials: tuple          # ((item, count), ...)
    tools: tuple = ()         # items needed but not used up
    max_health: float = 100.0


@dataclass
class Piece:
    blueprint: Blueprint
    position: tuple
    health: float = 0.0

    def __post_init__(self):
        if self.health == 0.0:
            self.health = self.blueprint.max_health

    @property
    def destroyed(self) -> bool:
        return self.health <= 0


@dataclass
class UtilityCabinet:
    position: tuple = (0.0, 0.0)
    radius: float = 30.0
    stock: Counter = field(default_factory=Counter)

    def covers(self, piece: Piece) -> bool:
        return math.dist(self.position, piece.position) <= self.radius


@dataclass
class BuildConfig:
    decay_per_hour: float = 0.5           # health lost outside a cabinet's area
    repair_per_hour: float = 5.0          # health restored inside it
    repair_cost_fraction: float = 0.1     # share of a piece's materials per 100% repaired


class MissingItems(Exception):
    pass


@dataclass
class Base:
    pieces: list = field(default_factory=list)
    cabinets: list = field(default_factory=list)
    config: BuildConfig = field(default_factory=BuildConfig)

    def build(self, blueprint: Blueprint, position: tuple, inventory: Counter) -> Piece:
        missing = [t for t in blueprint.tools if inventory[t] < 1]
        missing += [m for m, n in blueprint.materials if inventory[m] < n]
        if missing:
            raise MissingItems(", ".join(missing))
        for item, count in blueprint.materials:
            inventory[item] -= count
        piece = Piece(blueprint, position)
        self.pieces.append(piece)
        return piece

    def damage(self, piece: Piece, amount: float) -> None:
        piece.health = max(0.0, piece.health - amount)
        if piece.destroyed:
            self.pieces.remove(piece)

    def tick(self, hours: float) -> None:
        c = self.config
        for piece in list(self.pieces):
            cabinet = next((cab for cab in self.cabinets if cab.covers(piece)), None)
            if cabinet is None:
                self.damage(piece, c.decay_per_hour * hours)
                continue
            missing_hp = piece.blueprint.max_health - piece.health
            if missing_hp <= 0:
                continue
            repair = min(missing_hp, c.repair_per_hour * hours)
            if self._pay_for_repair(cabinet, piece, repair):
                piece.health += repair
            else:
                self.damage(piece, c.decay_per_hour * hours)

    def _pay_for_repair(self, cabinet: UtilityCabinet, piece: Piece, repair: float) -> bool:
        share = repair / piece.blueprint.max_health * self.config.repair_cost_fraction
        cost = {m: math.ceil(n * share) for m, n in piece.blueprint.materials}
        if any(cabinet.stock[m] < n for m, n in cost.items()):
            return False
        for m, n in cost.items():
            cabinet.stock[m] -= n
        return True
