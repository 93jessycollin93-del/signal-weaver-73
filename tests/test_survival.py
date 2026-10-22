from sim.digestion import FOODS, Body
from sim.survival import Activity, Survivor, WaterQuality


def live_day(s, meals=(), drink_ml=0):
    """16 h awake, 8 h asleep; eat at 8, 13, 19; use the toilet when needed."""
    for hour in range(24):
        asleep = hour < 8
        if drink_ml and not asleep:
            s.drink(drink_ml)
        if hour in (8, 13, 19):
            for name in meals:
                s.eat(FOODS[name])
        s.tick(1, Activity.SLEEP if asleep else Activity.IDLE)
        if s.body.needs_toilet["pee"]:
            s.body.urinate()
        if s.body.needs_toilet["poo"]:
            s.body.defecate()


def test_fed_and_watered_survivor_stays_healthy_for_weeks():
    s = Survivor()
    for _ in range(30):
        live_day(s, meals=("canned beans", "cooked rice", "canned tuna"), drink_ml=150)
    assert s.alive and s.health == 100


def test_no_water_kills_in_about_three_to_four_days():
    s = Survivor()
    days = 0
    while s.alive:
        live_day(s, meals=("beef jerky",))
        days += 1
    assert 3 <= days <= 5


def test_water_only_lasts_weeks_not_days():
    s = Survivor()
    days = 0
    while s.alive and days < 100:
        live_day(s, drink_ml=150)
        days += 1
    assert 25 <= days <= 70


def test_sprinting_drains_faster_than_idle():
    idle, sprint = Survivor(), Survivor()
    idle.tick(1, Activity.IDLE)
    sprint.tick(1, Activity.SPRINT)
    assert sprint.hunger < idle.hunger
    assert sprint.thirst < idle.thirst


def test_overeating_makes_you_vomit_not_die():
    s = Survivor()
    cans = 0
    while s.body.vomit_count == 0:
        s.eat(FOODS["canned beans"])
        cans += 1
    assert 6 <= cans <= 9  # ~3 L of food before it comes back up
    assert s.alive


def test_dirty_water_and_spoiled_food_infect():
    clean, dirty = Survivor(), Survivor()
    clean.drink(250, WaterQuality.CLEAN)
    dirty.drink(250, WaterQuality.DIRTY)
    assert clean.infection == 0 and dirty.infection > 0
    spoiled = Survivor()
    spoiled.eat(FOODS["canned tuna"].__class__(**{**FOODS["canned tuna"].__dict__, "contaminated": True}))
    assert spoiled.infection > 0


def test_infection_makes_you_hungrier():
    healthy, sick = Survivor(), Survivor(infection=100)
    healthy.tick(6)
    sick.tick(6)
    assert sick.body.kcal_burned > healthy.body.kcal_burned
    assert sick.hunger < healthy.hunger


def test_cold_drains_energy():
    mild, cold = Survivor(), Survivor()
    mild.tick(2, temperature=20)
    cold.tick(2, temperature=-10)
    assert cold.energy < mild.energy


def test_heat_exhaustion_flag():
    s = Survivor()
    s.tick(1, temperature=40)
    assert s.heat_exhausted


def test_sleep_restores_energy():
    s = Survivor(energy=30)
    s.tick(4, Activity.SLEEP)
    assert s.energy > 30


def test_empty_glycogen_slows_stamina_recovery():
    fed, empty = Survivor(stamina=0), Survivor(stamina=0, body=Body(glycogen=0))
    fed.tick(0.1)
    empty.tick(0.1)
    assert empty.stamina < fed.stamina


def test_exhaustion_makes_sprinting_costlier():
    rested, tired = Survivor(energy=100), Survivor(energy=10)
    rested.tick(0.05, Activity.SPRINT)
    tired.tick(0.05, Activity.SPRINT)
    assert tired.stamina < rested.stamina


def test_hud_only_shows_extremes():
    s = Survivor(body=Body(body_water=42_000 * 0.92))
    assert set(s.hud_visible()) == {"thirst"}
    s.drink(1500)
    s.eat(FOODS["canned beans"])
    assert "hunger" in s.hud_visible()  # stuffed
