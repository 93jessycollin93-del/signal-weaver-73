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


@dataclass
class VeinClock:
    """How fast game time runs in real time, like Vein's vein.Time.* settings.

    Daytime runs `time_multiplier` times faster than real time; between
    `night_start` and `night_end` it runs `night_multiplier` times faster again.
    Defaults are Vein's published server defaults (16, 3, 20:00, 06:00).
    """
    time_multiplier: float = 16.0
    night_multiplier: float = 3.0
    night_start: float = 20.0
    night_end: float = 6.0

    def is_night(self, hour_of_day: float) -> bool:
        if self.night_start > self.night_end:  # window wraps past midnight
            return hour_of_day >= self.night_start or hour_of_day < self.night_end
        return self.night_start <= hour_of_day < self.night_end

    def speed(self, hour_of_day: float) -> float:
        """Game seconds per real second at this hour."""
        return self.time_multiplier * (self.night_multiplier if self.is_night(hour_of_day) else 1.0)

    def night_hours(self) -> float:
        return (self.night_end - self.night_start) % 24.0

    def real_minutes_per_day(self) -> float:
        night = self.night_hours()
        day = 24.0 - night
        return (day / self.time_multiplier + night / (self.time_multiplier * self.night_multiplier)) * 60.0

    def advance_real(self, calendar: Calendar, real_seconds: float) -> None:
        """Advance `calendar` by `real_seconds` of wall-clock time, crossing day/night exactly."""
        left = real_seconds
        while left > 1e-9:
            h = calendar.hour_of_day + 1e-9              # nudge past a boundary we just reached
            boundary = self.night_end if self.is_night(h) else self.night_start
            to_boundary = max((boundary - h) % 24.0, 1e-9)  # game hours until speed changes
            rate = self.speed(h) / 3600.0                # game hours per real second
            step = min(left, to_boundary / rate)
            calendar.advance(step * rate)
            left -= step
