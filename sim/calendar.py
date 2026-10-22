"""Shared world clock: game days, utility shutoff dates, seasons.

Mirrors the role of Vein's vein.Calendar.* settings. Defaults come from
community server guides (water off day 30, power off day 46).
"""

from dataclasses import dataclass

SEASONS = ("spring", "summer", "autumn", "winter")


@dataclass
class Calendar:
    hours: float = 0.0
    water_shutoff_day: float = 30.0
    power_shutoff_day: float = 46.0
    days_per_season: int = 30
    start_season: int = 0  # index into SEASONS

    @property
    def day(self) -> float:
        return self.hours / 24.0

    @property
    def hour_of_day(self) -> float:
        return self.hours % 24.0

    @property
    def is_daytime(self) -> bool:
        return 6.0 <= self.hour_of_day < 20.0

    @property
    def season(self) -> str:
        index = (int(self.day // self.days_per_season) + self.start_season) % len(SEASONS)
        return SEASONS[index]

    @property
    def city_water_on(self) -> bool:
        return self.day < self.water_shutoff_day

    @property
    def city_power_on(self) -> bool:
        return self.day < self.power_shutoff_day

    def advance(self, hours: float) -> None:
        self.hours += hours
