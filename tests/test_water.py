from sim.calendar import Calendar
from sim.survival import WaterQuality
from sim.water import Barrel, CityMains, Container, Fixture, FuseBox, Well


def make_house(*sources):
    box = FuseBox()
    for s in sources:
        box.connect_source(s)
    sink = Fixture("sink", 2.0)
    box.connect_fixture(sink)
    return box, sink


def test_city_water_runs_until_shutoff_day():
    cal = Calendar()
    box, sink = make_house(CityMains())
    assert box.use(sink, cal) == (2.0, WaterQuality.CLEAN)
    cal.advance(24 * 30)
    assert box.use(sink, cal) == (0.0, None)


def test_shutoff_day_is_configurable():
    cal = Calendar(water_shutoff_day=999)
    cal.advance(24 * 100)
    assert cal.city_water_on


def test_well_never_runs_dry_but_is_dirty():
    cal = Calendar()
    cal.advance(24 * 200)
    box, sink = make_house(Well())
    assert box.use(sink, cal) == (2.0, WaterQuality.DIRTY)


def test_barrel_only_gives_what_was_poured_in():
    cal = Calendar()
    barrel = Barrel(capacity=200)
    box, sink = make_house(barrel)
    assert box.use(sink, cal) == (0.0, None)
    jug = Container(capacity=4, litres=4)
    jug.pour_into(barrel)
    assert box.use(sink, cal) == (2.0, WaterQuality.CLEAN)
    assert box.use(sink, cal) == (2.0, WaterQuality.CLEAN)
    assert box.use(sink, cal) == (0.0, None)


def test_dirty_jug_taints_barrel_until_emptied():
    cal = Calendar()
    barrel = Barrel()
    barrel.fill(2, WaterQuality.CLEAN)
    barrel.fill(2, WaterQuality.DIRTY)
    box, sink = make_house(barrel)
    assert box.use(sink, cal)[1] is WaterQuality.DIRTY
    barrel.fill(2, WaterQuality.CLEAN)  # 2 left + 2 clean, still tainted
    assert box.use(sink, cal)[1] is WaterQuality.DIRTY


def test_fuse_box_feeds_all_fixtures_and_falls_back_in_order():
    cal = Calendar()
    barrel = Barrel()
    barrel.fill(1, WaterQuality.CLEAN)
    box, sink = make_house(barrel, Well())
    shower = Fixture("shower", 10.0)
    box.connect_fixture(shower)
    litres, quality = box.use(shower, cal)
    assert litres == 10.0
    assert quality is WaterQuality.DIRTY  # 1 L clean + 9 L well water


def test_unconnected_fixture_is_rejected():
    box, _ = make_house(Well())
    try:
        box.use(Fixture("toilet", 6), Calendar())
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_boiling_makes_well_water_safe():
    cal = Calendar()
    box, sink = make_house(Well())
    jug = Container()
    jug.fill_from(box, sink, cal)
    assert jug.quality is WaterQuality.DIRTY
    jug.boil()
    assert jug.quality is WaterQuality.CLEAN
