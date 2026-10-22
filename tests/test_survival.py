from sim.survival import Activity, Survivor, WaterQuality


def test_idle_drain_over_a_day():
    s = Survivor()
    s.tick(10)
    assert s.hunger < 80 and s.thirst < 80 and s.energy < 100
    assert s.alive


def test_sprinting_drains_faster_than_idle():
    idle, sprint = Survivor(), Survivor()
    idle.tick(1, Activity.IDLE)
    sprint.tick(1, Activity.SPRINT)
    assert sprint.hunger < idle.hunger
    assert sprint.thirst < idle.thirst


def test_starvation_damages_then_kills():
    s = Survivor(hunger=0, thirst=0)
    s.tick(1)
    assert s.health < 100
    s.tick(100)
    assert not s.alive


def test_overfill_limit_is_fatal():
    s = Survivor(hunger=80)
    s.eat(45)  # 125, below the 130 limit
    assert s.alive
    s.eat(10)  # 135, over the limit
    assert not s.alive


def test_overdrinking_hurts_while_above_100():
    s = Survivor(thirst=80)
    s.drink(30)  # 110
    s.tick(0.5)
    assert s.health < 100


def test_dirty_water_infects_clean_does_not():
    clean, dirty = Survivor(), Survivor()
    clean.drink(10, WaterQuality.CLEAN)
    dirty.drink(10, WaterQuality.DIRTY)
    assert clean.infection == 0
    assert dirty.infection > 0


def test_infection_increases_appetite():
    healthy, sick = Survivor(), Survivor(infection=100)
    healthy.tick(2)
    sick.tick(2)
    assert sick.hunger < healthy.hunger


def test_cold_drains_energy_heat_drains_water():
    mild, cold, hot = Survivor(), Survivor(), Survivor()
    mild.tick(2, temperature=20)
    cold.tick(2, temperature=-10)
    hot.tick(2, temperature=40)
    assert cold.energy < mild.energy
    assert hot.thirst < mild.thirst
    assert hot.heat_exhausted and not mild.heat_exhausted


def test_sleep_restores_energy():
    s = Survivor(energy=30)
    s.tick(4, Activity.SLEEP)
    assert s.energy > 30


def test_exhaustion_makes_sprinting_costlier():
    rested, tired = Survivor(energy=100), Survivor(energy=10)
    rested.tick(0.05, Activity.SPRINT)
    tired.tick(0.05, Activity.SPRINT)
    assert tired.stamina < rested.stamina


def test_hud_only_shows_extremes():
    s = Survivor(hunger=60, thirst=10, energy=100)
    assert s.hud_visible() == {"thirst": 10}
    s.eat(50)  # 110
    assert "hunger" in s.hud_visible()
