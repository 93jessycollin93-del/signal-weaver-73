from collections import Counter

import pytest

from sim.building import Base, Blueprint, MissingItems, UtilityCabinet

WALL = Blueprint("wood wall", materials=(("plank", 10), ("nail", 20)), tools=("hammer",))


def test_build_needs_tools_and_materials():
    base = Base()
    with pytest.raises(MissingItems, match="hammer"):
        base.build(WALL, (0, 0), Counter(plank=10, nail=20))
    with pytest.raises(MissingItems, match="plank"):
        base.build(WALL, (0, 0), Counter(hammer=1, plank=5, nail=20))


def test_build_uses_materials_but_keeps_tools():
    inv = Counter(hammer=1, plank=12, nail=20)
    Base().build(WALL, (0, 0), inv)
    assert inv == Counter(hammer=1, plank=2, nail=0)


def test_pieces_outside_cabinet_decay_and_fall_apart():
    base = Base()
    piece = base.build(WALL, (100, 0), Counter(hammer=1, plank=10, nail=20))
    base.tick(10)
    assert piece.health < 100
    base.tick(1000)
    assert piece not in base.pieces


def test_cabinet_repairs_pieces_in_range_using_its_stock():
    cab = UtilityCabinet(position=(0, 0), radius=30, stock=Counter(plank=50, nail=50))
    base = Base(cabinets=[cab])
    piece = base.build(WALL, (5, 0), Counter(hammer=1, plank=10, nail=20))
    piece.health = 50
    base.tick(4)
    assert piece.health == 70
    assert cab.stock["plank"] < 50


def test_cabinet_with_empty_stock_cannot_stop_decay():
    cab = UtilityCabinet(position=(0, 0), radius=30)
    base = Base(cabinets=[cab])
    piece = base.build(WALL, (5, 0), Counter(hammer=1, plank=10, nail=20))
    piece.health = 50
    base.tick(4)
    assert piece.health < 50


def test_full_health_pieces_in_range_cost_nothing():
    cab = UtilityCabinet(stock=Counter(plank=5, nail=5))
    base = Base(cabinets=[cab])
    base.build(WALL, (1, 1), Counter(hammer=1, plank=10, nail=20))
    base.tick(24)
    assert cab.stock == Counter(plank=5, nail=5)
