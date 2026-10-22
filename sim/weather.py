"""Clean-room weather, seasons and temperature.

See notes/systems/07-weather.md. Public info on Vein's weather is thin
(seasons are a planned feature), so most numbers here are our own. The
output temperature feeds Survivor.tick(temperature=...).
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum

from sim.calendar import Calendar


class Weather(Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"


# Mean daily temperature (°C) per season — loosely a cold-winter, warm-summer
# northern climate. Ours, not Vein's.
SEASON_MEAN = {"spring": 8.0, "summer": 22.0, "autumn": 9.0, "winter": -8.0}
DAY_NIGHT_SWING = 6.0  # ± °C around the mean, warmest at 15:00

WEATHER_OFFSET = {
    Weather.CLEAR: 0.0,
    Weather.CLOUDY: -1.0,
    Weather.RAIN: -3.0,
    Weather.STORM: -5.0,
    Weather.SNOW: -4.0,
}

# Chance of each weather the next hour, by season. Snow only when cold.
SEASON_WEIGHTS = {
    "spring": {Weather.CLEAR: 4, Weather.CLOUDY: 3, Weather.RAIN: 3, Weather.STORM: 1},
    "summer": {Weather.CLEAR: 6, Weather.CLOUDY: 2, Weather.RAIN: 1, Weather.STORM: 1},
    "autumn": {Weather.CLEAR: 3, Weather.CLOUDY: 4, Weather.RAIN: 4, Weather.STORM: 1},
    "winter": {Weather.CLEAR: 3, Weather.CLOUDY: 3, Weather.SNOW: 4, Weather.STORM: 1},
}


@dataclass
class WeatherSystem:
    calendar: Calendar = field(default_factory=Calendar)
    current: Weather = Weather.CLEAR
    persistence: float = 0.85  # chance the weather stays the same each hour
    rng: random.Random = field(default_factory=random.Random)

    def temperature(self, indoors: bool = False, heated: bool = False) -> float:
        cal = self.calendar
        mean = SEASON_MEAN[cal.season]
        swing = DAY_NIGHT_SWING * math.cos((cal.hour_of_day - 15.0) / 24.0 * 2 * math.pi)
        outside = mean + swing + WEATHER_OFFSET[self.current]
        if heated:
            return max(outside, 20.0)
        if indoors:
            return outside + 0.5 * (15.0 - outside)  # walls halve the gap to 15 °C
        return outside

    def _next(self) -> Weather:
        weights = SEASON_WEIGHTS[self.calendar.season]
        if self.current in weights and self.rng.random() < self.persistence:
            return self.current
        options = list(weights)
        return self.rng.choices(options, [weights[w] for w in options])[0]

    def advance(self, hours: int) -> None:
        """Step the world forward hour by hour."""
        for _ in range(int(hours)):
            self.calendar.advance(1)
            self.current = self._next()

    @property
    def solar_factor(self) -> float:
        """Assumption: cloud and storms cut solar output. Not confirmed in Vein."""
        return {Weather.CLEAR: 1.0, Weather.CLOUDY: 0.5, Weather.RAIN: 0.3,
                Weather.STORM: 0.1, Weather.SNOW: 0.3}[self.current]
