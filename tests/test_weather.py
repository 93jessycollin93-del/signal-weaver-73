import random

from sim.calendar import Calendar
from sim.survival import Survivor
from sim.weather import Weather, WeatherSystem


def at(day, hour, weather=Weather.CLEAR):
    return WeatherSystem(Calendar(hours=day * 24 + hour), weather, rng=random.Random(0))


def test_seasons_follow_the_calendar():
    assert Calendar(hours=0).season == "spring"
    assert Calendar(hours=24 * 30).season == "summer"
    assert Calendar(hours=24 * 95).season == "winter"
    assert Calendar(hours=24 * 120).season == "spring"


def test_winter_is_colder_than_summer():
    assert at(95, 12).temperature() < at(35, 12).temperature()


def test_afternoon_is_warmer_than_night():
    assert at(35, 15).temperature() > at(35, 3).temperature()


def test_bad_weather_is_colder():
    assert at(35, 12, Weather.STORM).temperature() < at(35, 12, Weather.CLEAR).temperature()


def test_shelter_and_heating():
    w = at(95, 3)
    outside = w.temperature()
    assert outside < w.temperature(indoors=True) < 15
    assert w.temperature(heated=True) >= 20


def test_snow_only_in_winter():
    for start_day in (0, 30, 60):
        w = at(start_day, 0)
        w.rng = random.Random(start_day)
        seen = set()
        for _ in range(24 * 25):
            w.advance(1)
            seen.add(w.current)
        assert Weather.SNOW not in seen
    w = at(90, 0)
    seen = set()
    for _ in range(24 * 25):
        w.advance(1)
        seen.add(w.current)
    assert Weather.SNOW in seen


def test_weather_drives_survival():
    cold, mild = Survivor(), Survivor()
    cold.tick(4, temperature=at(95, 3, Weather.STORM).temperature())
    mild.tick(4, temperature=at(35, 15).temperature())
    assert cold.energy < mild.energy


def test_vein_default_day_lasts_about_65_real_minutes():
    from sim.calendar import VeinClock
    clock = VeinClock()
    # day 06-20 at 16x = 52.5 min, night 20-06 at 48x = 12.5 min
    assert abs(clock.real_minutes_per_day() - 65.0) < 1e-9
    assert VeinClock(time_multiplier=1, night_multiplier=1).real_minutes_per_day() == 24 * 60


def test_vein_clock_runs_faster_at_night():
    from sim.calendar import VeinClock
    clock = VeinClock()
    assert clock.speed(12) == 16 and clock.speed(23) == 48 and clock.speed(3) == 48
    assert clock.speed(6) == 16 and clock.speed(20) == 48


def test_vein_clock_full_day_in_real_time():
    from sim.calendar import Calendar, VeinClock
    cal, clock = Calendar(hours=8.0), VeinClock()
    clock.advance_real(cal, 65.0 * 60)
    assert abs(cal.hours - 32.0) < 1e-6  # exactly one game day later


def test_vein_clock_many_small_steps_match_one_big_step():
    from sim.calendar import Calendar, VeinClock
    one, many, clock = Calendar(hours=19.5), Calendar(hours=19.5), VeinClock()
    clock.advance_real(one, 3000.0)
    for _ in range(3000):
        clock.advance_real(many, 1.0)
    assert abs(one.hours - many.hours) < 1e-6
