from sim.calendar import Calendar
from sim.power import Battery, Device, Generator, PowerNetwork, SolarPanel


def night_after_shutoff():
    cal = Calendar()
    cal.advance(24 * 46 + 22)  # day 46, 22:00
    return cal


def test_city_power_runs_until_shutoff_day():
    cal = Calendar()
    lamp = Device("lamp", 60)
    net = PowerNetwork(wired=[lamp])
    assert net.tick(1, cal) == {"lamp": True}
    cal.advance(24 * 46)
    assert net.tick(1, cal) == {"lamp": False}


def test_generator_powers_devices_in_radius_without_wiring():
    cal = night_after_shutoff()
    gen = Generator(fuel=10, radius=15, position=(0, 0))
    near = Device("street light", 100, position=(10, 0))
    far = Device("fridge", 100, position=(40, 0))
    net = PowerNetwork(generators=[gen], nearby=[near, far])
    result = net.tick(1, cal)
    assert result == {"street light": True}
    assert not far.powered


def test_generator_burns_fuel_and_stops_when_empty():
    cal = night_after_shutoff()
    gen = Generator(watts=3000, fuel=0.4, litres_per_kwh=0.4)  # exactly 1 kWh
    heater = Device("heater", 1000)
    net = PowerNetwork(generators=[gen], wired=[heater])
    assert net.tick(1, cal) == {"heater": True}
    assert gen.fuel == 0
    assert net.tick(1, cal) == {"heater": False}


def test_solar_only_works_in_daytime():
    panel = SolarPanel(watts=400)
    lamp = Device("lamp", 100)
    net = PowerNetwork(panels=[panel], wired=[lamp], on_city_grid=False)
    noon = Calendar(hours=12)
    midnight = Calendar(hours=0)
    assert net.tick(1, noon) == {"lamp": True}
    assert net.tick(1, midnight) == {"lamp": False}


def test_battery_stores_daytime_surplus_for_the_night():
    panel = SolarPanel(watts=400)
    battery = Battery(capacity=50_000)
    lamp = Device("lamp", 100)
    net = PowerNetwork(panels=[panel], batteries=[battery], wired=[lamp], on_city_grid=False)
    net.tick(10, Calendar(hours=8))   # 4000 Wh in, 1000 Wh used
    assert battery.charge == 3000
    assert net.tick(5, Calendar(hours=22)) == {"lamp": True}
    assert battery.charge == 2500


def test_short_power_serves_high_priority_first():
    cal = night_after_shutoff()
    gen = Generator(watts=500, fuel=10)
    fridge = Device("fridge", 400, priority=10)
    tv = Device("tv", 300, priority=0)
    net = PowerNetwork(generators=[gen], wired=[tv, fridge])
    assert net.tick(1, cal) == {"fridge": True, "tv": False}


def test_refuel_respects_tank_size():
    gen = Generator(fuel_capacity=20, fuel=15)
    assert gen.refuel(10) == 5
    assert gen.fuel == 20
