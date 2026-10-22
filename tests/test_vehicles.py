from collections import Counter

import pytest

from sim.vehicles import Car, FuelCan, Part, charge_battery


def good_car(**kw):
    parts = {"battery": Part("battery"), "spark plugs": Part("spark plugs"),
             "engine": Part("engine", mechanic_level=3)}
    return Car(parts=parts, fuel=20, has_key=True, **kw)


def test_working_car_starts_and_drives():
    car = good_car()
    assert car.why_wont_it_start() == []
    assert car.start()
    assert car.drive(10) == 10
    assert car.fuel == pytest.approx(19)


def test_each_classic_fault_stops_the_car():
    flat = good_car(battery_charge=0)
    dry = good_car()
    dry.fuel = 0
    no_plugs = good_car()
    no_plugs.parts["spark plugs"] = None
    wrecked = good_car()
    wrecked.parts["engine"].condition = 5
    for car, problem in ((flat, "battery flat"), (dry, "no fuel"),
                         (no_plugs, "missing spark plugs"), (wrecked, "engine too damaged")):
        assert problem in car.why_wont_it_start()
        assert not car.start()


def test_failed_starts_drain_the_battery():
    car = good_car()
    car.fuel = 0
    for _ in range(3):
        car.start()
    assert car.battery_charge == 85


def test_no_key_needs_hotwire_with_skill():
    car = good_car()
    car.has_key = False
    assert not car.start()
    assert not car.hotwire(mechanic_level=0, required=1)
    assert car.hotwire(mechanic_level=1, required=1)
    assert car.start()


def test_siphon_needs_hose_and_moves_fuel():
    wreck, mine, can = good_car(), good_car(), FuelCan(capacity=20)
    mine.fuel = 0
    with pytest.raises(ValueError):
        wreck.siphon(can, Counter())
    assert wreck.siphon(can, Counter({"siphon hose": 1})) == 20
    assert mine.refuel(can) == 20
    assert mine.start()


def test_running_out_of_fuel_stops_the_car_partway():
    car = good_car()
    car.fuel = 1  # 10 km at 0.1 L/km
    car.start()
    assert car.drive(50) == pytest.approx(10)
    assert not car.running


def test_swapping_parts_respects_mechanic_level():
    car, donor = good_car(), good_car()
    with pytest.raises(PermissionError):
        donor.remove_part("engine", mechanic_level=1)
    car.parts["engine"].condition = 0
    old = car.remove_part("engine", mechanic_level=3)
    assert old.condition == 0
    car.install_part("engine", donor.remove_part("engine", mechanic_level=3), mechanic_level=3)
    assert car.start()


def test_charger_needs_power():
    car = good_car(battery_charge=0)
    charge_battery(car, 2, powered=False)
    assert car.battery_charge == 0
    charge_battery(car, 2)
    assert car.battery_charge == 40
    assert car.start()
