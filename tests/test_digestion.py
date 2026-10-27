import pytest

from sim.digestion import FOODS, Body, Food


def test_food_energy_from_macros():
    assert FOODS["beef jerky"].kcal == pytest.approx(5 * 4 + 17 * 4 + 4 * 9)


def test_meal_leaves_stomach_in_hours_not_minutes():
    b = Body()
    b.eat(FOODS["canned beans"])
    b.eat(FOODS["bread slice"])
    b.tick(1)
    assert b.stomach.kcal > 0
    b.tick(4)
    assert b.stomach.kcal == 0


def test_plain_water_empties_faster_than_with_a_meal():
    plain, meal = Body(), Body()
    plain.drink(500)
    meal.drink(500)
    meal.eat(FOODS["chocolate bar"])
    plain.tick(0.5)
    meal.tick(0.5)
    assert plain.stomach.water < meal.stomach.water


def test_fat_slows_stomach_emptying():
    lean, fatty = Body(), Body()
    lean.eat(Food("sugar", carbs=50))
    fatty.eat(Food("oil", fat=200 / 9))  # same 200 kcal
    lean.tick(1)
    fatty.tick(1)
    assert fatty.stomach.kcal > lean.stomach.kcal


def test_one_big_tick_equals_many_small_ones():
    big, small = Body(), Body()
    for b in (big, small):
        b.eat(FOODS["canned beans"])
        b.drink(300)
    big.tick(3)
    for _ in range(180):
        small.tick(1 / 60)
    assert big.glycogen == pytest.approx(small.glycogen, rel=0.02)
    assert big.body_water == pytest.approx(small.body_water, rel=0.001)
    assert big.stomach.volume == pytest.approx(small.stomach.volume, abs=15)


def test_carbs_fill_glycogen_then_spill_into_fat():
    fed, fasted = Body(glycogen=490), Body(glycogen=490)
    fed.eat(Food("sugar", carbs=200))
    fed.tick(8)
    fasted.tick(8)
    assert fed.glycogen > 480
    assert fed.fat_store > fasted.fat_store + 30  # overflow became fat


def test_fibre_and_leftovers_end_up_in_the_colon():
    b = Body()
    b.eat(FOODS["canned beans"])
    b.tick(12)
    assert b.colon_solids >= 14
    assert b.defecate() > 0
    assert b.colon_solids == 0


def test_drinking_a_lot_fills_the_bladder():
    b = Body()
    b.drink(1000)
    b.tick(2)
    assert b.needs_toilet["pee"]
    assert b.urinate() > 300


def test_ignoring_the_bladder_causes_an_accident():
    b = Body()
    b.drink(1500)
    b.tick(4)
    assert b.accidents >= 1


def test_overfilling_the_stomach_makes_you_vomit():
    b = Body()
    assert b.drink(2000)
    assert not b.drink(1500)
    assert b.vomit_count == 1
    assert b.stomach.volume == 0
    assert b.dehydration > 0


def test_satiety_tracks_stomach_and_stores():
    b = Body()
    hungry = b.satiety
    b.eat(FOODS["canned beans"])
    b.eat(FOODS["cooked rice"])
    assert b.satiety > hungry
    stuffed = Body()
    stuffed.drink(2500)
    assert stuffed.satiety > 1


def test_activity_and_heat_cause_sweating():
    rest, sprint, hot = Body(), Body(), Body()
    rest.tick(1, met=1.3)
    sprint.tick(1, met=10)
    hot.tick(1, met=1.3, temperature=38)
    assert sprint.body_water < rest.body_water
    assert hot.body_water < rest.body_water


def test_sprinting_burns_glycogen_faster_than_resting():
    rest, sprint = Body(), Body()
    rest.tick(1, met=1.3)
    sprint.tick(1, met=10)
    assert sprint.glycogen < rest.glycogen - 50


def test_cold_makes_you_shiver_and_burn_more():
    warm, cold = Body(), Body()
    warm.tick(4, temperature=20)
    cold.tick(4, temperature=-10)
    assert cold.kcal_burned > warm.kcal_burned


def test_fever_raises_metabolism():
    well, sick = Body(), Body()
    well.tick(4)
    sick.tick(4, infection=100)
    assert sick.kcal_burned == pytest.approx(well.kcal_burned * 1.3)


def test_starvation_burns_fat_then_muscle():
    b = Body(glycogen=0)
    b.tick(24 * 7)
    assert b.fat_store < 12_000 - 1000
    assert b.muscle_fraction < 1


def test_no_fat_left_means_the_body_eats_muscle_fast():
    lean, empty = Body(glycogen=0), Body(glycogen=0, fat_store=0)
    lean.tick(24)
    empty.tick(24)
    assert empty.muscle_protein < lean.muscle_protein - 300


def test_severe_dehydration_and_starvation_are_lethal():
    assert Body(body_water=42_000 * 0.84).damage_per_hour() == float("inf")
    assert Body(muscle_protein=5000).damage_per_hour() == float("inf")
    assert Body(body_water=42_000 * 0.9).damage_per_hour() > 0
    assert Body().damage_per_hour() == 0


def test_vein_hunger_and_thirst_multipliers():
    from sim.digestion import DigestionConfig
    normal, hard = Body(), Body(config=DigestionConfig(hunger_rate=2.0, thirst_rate=2.0))
    easy = Body(config=DigestionConfig(hunger_rate=0.5, thirst_rate=0.5))
    for b in (normal, hard, easy):
        b.tick(10)
    assert hard.kcal_burned == pytest.approx(normal.kcal_burned * 2)
    assert easy.kcal_burned == pytest.approx(normal.kcal_burned * 0.5)
    assert hard.body_water < normal.body_water < easy.body_water
