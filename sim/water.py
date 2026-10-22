"""Clean-room water system, built from Vein's observed behaviour.

See notes/systems/02-water.md. City water runs until the shutoff day; after
that a base needs its own sources (wells, rooftop barrels filled by hand).
Sources feed a fuse box that serves every connected fixture.
"""

from dataclasses import dataclass, field

from sim.calendar import Calendar
from sim.survival import WaterQuality


@dataclass
class WaterSource:
    """Base class. `draw` returns (litres actually drawn, quality)."""
    name: str = "source"

    def available(self, calendar: Calendar) -> float:
        raise NotImplementedError

    def draw(self, litres: float, calendar: Calendar) -> tuple:
        raise NotImplementedError


@dataclass
class CityMains(WaterSource):
    name: str = "city mains"

    def available(self, calendar: Calendar) -> float:
        return float("inf") if calendar.city_water_on else 0.0

    def draw(self, litres: float, calendar: Calendar) -> tuple:
        if not calendar.city_water_on:
            return 0.0, WaterQuality.CLEAN
        return litres, WaterQuality.CLEAN


@dataclass
class Well(WaterSource):
    """Unlimited ground water, but untreated, so it counts as dirty."""
    name: str = "well"

    def available(self, calendar: Calendar) -> float:
        return float("inf")

    def draw(self, litres: float, calendar: Calendar) -> tuple:
        return litres, WaterQuality.DIRTY


@dataclass
class Barrel(WaterSource):
    """Gravity-fed rooftop barrel. Only holds what you pour in."""
    name: str = "barrel"
    capacity: float = 200.0
    litres: float = 0.0
    quality: WaterQuality = WaterQuality.CLEAN

    def fill(self, litres: float, quality: WaterQuality) -> float:
        """Pour water in (e.g. from a jug). Returns litres that fit."""
        poured = min(litres, self.capacity - self.litres)
        if poured > 0 and quality is WaterQuality.DIRTY:
            self.quality = WaterQuality.DIRTY  # one dirty jug taints the barrel
        self.litres += poured
        return poured

    def available(self, calendar: Calendar) -> float:
        return self.litres

    def draw(self, litres: float, calendar: Calendar) -> tuple:
        drawn = min(litres, self.litres)
        self.litres -= drawn
        if self.litres == 0:
            self.quality = WaterQuality.CLEAN  # empty barrel resets
        return drawn, self.quality


@dataclass
class Fixture:
    """Sink, shower, toilet... Uses a fixed amount of water per use."""
    name: str
    litres_per_use: float


@dataclass
class FuseBox:
    """Central hub: every connected source feeds every connected fixture.

    Sources are drawn in the order they were connected, so put clean ones first.
    """
    sources: list = field(default_factory=list)
    fixtures: list = field(default_factory=list)

    def connect_source(self, source: WaterSource) -> None:
        self.sources.append(source)

    def connect_fixture(self, fixture: Fixture) -> None:
        self.fixtures.append(fixture)

    def use(self, fixture: Fixture, calendar: Calendar) -> tuple:
        """Use a fixture. Returns (litres delivered, quality) or (0, None)."""
        if fixture not in self.fixtures:
            raise ValueError(f"{fixture.name} is not connected to this fuse box")
        needed = fixture.litres_per_use
        delivered = 0.0
        quality = WaterQuality.CLEAN
        for source in self.sources:
            if delivered >= needed:
                break
            got, q = source.draw(needed - delivered, calendar)
            if got > 0:
                delivered += got
                if q is WaterQuality.DIRTY:
                    quality = WaterQuality.DIRTY
        if delivered == 0:
            return 0.0, None
        return delivered, quality


@dataclass
class Container:
    """A jug or bottle the player carries."""
    capacity: float = 4.0
    litres: float = 0.0
    quality: WaterQuality = WaterQuality.CLEAN

    def fill_from(self, box: FuseBox, sink: Fixture, calendar: Calendar) -> float:
        litres, quality = box.use(sink, calendar)
        if quality is None:
            return 0.0
        got = min(litres, self.capacity - self.litres)
        if got > 0 and quality is WaterQuality.DIRTY:
            self.quality = WaterQuality.DIRTY
        self.litres += got
        return got

    def boil(self) -> None:
        """Boiling (or filtering) makes any water safe."""
        if self.litres > 0:
            self.quality = WaterQuality.CLEAN

    def pour_into(self, barrel: Barrel) -> float:
        poured = barrel.fill(self.litres, self.quality)
        self.litres -= poured
        return poured
