import json
import random

import pytest

from sim.loot import Container, LootEntry, LootSettings, LootTable, World, roll

KITCHEN = LootTable("kitchen", (
    LootEntry("canned food", 5, 1, 2),
    LootEntry("water bottle", 3),
    LootEntry("knife", 1),
), rolls=10)


def total(items):
    return sum(items.values())


def test_scarcity_changes_how_much_you_find():
    plenty = total(roll(KITCHEN, LootSettings(scarcity=0), random.Random(1)))
    scarce = total(roll(KITCHEN, LootSettings(scarcity=4), random.Random(1)))
    assert plenty > scarce


def test_settings_reject_out_of_range_values():
    with pytest.raises(ValueError):
        LootSettings(scarcity=5)
    with pytest.raises(ValueError):
        LootSettings(respawn_interval_s=60)


def test_container_contents_are_fixed_once_generated():
    rng = random.Random(2)
    box = Container(KITCHEN)
    first = dict(box.open(0, LootSettings(), rng))
    assert dict(box.open(100, LootSettings(), rng)) == first


def test_emptied_container_respawns_after_interval():
    rng, s = random.Random(3), LootSettings(respawn_interval_s=10800)
    box = Container(KITCHEN)
    for item, n in list(box.open(0, s, rng).items()):
        box.take(item, n, now=100)
    assert not box.open(100 + 10799, s, rng)
    assert box.open(100 + 10800, s, rng)


def test_respawn_can_be_disabled():
    rng, s = random.Random(4), LootSettings(respawn_enabled=False)
    box = Container(KITCHEN)
    for item, n in list(box.open(0, s, rng).items()):
        box.take(item, n, now=0)
    assert not box.open(10 ** 6, s, rng)


def test_partly_looted_container_does_not_refill():
    rng, s = random.Random(5), LootSettings()
    box = Container(KITCHEN)
    items = box.open(0, s, rng)
    item = next(iter(items))
    before = total(items)
    box.take(item, 1, now=0)
    assert total(box.open(10 ** 6, s, rng)) == before - 1


def test_dropped_items_stay_put_and_survive_save_load():
    world = World()
    world.drop((10.0, 5.0), "axe")
    world.drop((10.0, 5.0), "nail", 30)
    saved = json.dumps(world.snapshot())
    loaded = World.restore(json.loads(saved))
    assert loaded.pick_up((10.0, 5.0), "nail", 50) == 30
    assert loaded.pick_up((10.0, 5.0), "axe") == 1
    assert loaded.ground == {}
