import random

from sim.zombies import Noise, Player, State, Zombie, ZombieSettings


def test_zombie_chases_player_it_can_see():
    z = Zombie((0, 0), state=State.INVESTIGATING)
    assert z.update(0.01, Player((20, 0))) is State.CHASING


def test_idle_zombies_notice_less():
    busy = Zombie((0, 0), state=State.IDLE)
    alert = Zombie((0, 0), state=State.INVESTIGATING)
    player = Player((20, 0), sneaking=True)
    assert not busy.can_see(player, daylight=True)
    assert alert.can_see(player, daylight=True)


def test_night_cuts_sight_range():
    z = Zombie((0, 0), state=State.INVESTIGATING)
    p = Player((20, 0))
    assert z.can_see(p, daylight=True)
    assert not z.can_see(p, daylight=False)


def test_sneaking_masks_footsteps_and_skill_helps():
    z = Zombie((0, 0), state=State.INVESTIGATING)
    walking = Player((7, 0))
    sneaking = Player((7, 0), sneaking=True)
    assert z.can_hear(walking.footstep_noise())
    assert not z.can_hear(sneaking.footstep_noise())
    novice = Player((0, 0), sneaking=True, sneak_skill=0).footstep_noise().radius
    expert = Player((0, 0), sneaking=True, sneak_skill=1).footstep_noise().radius
    assert expert < novice


def test_gunfire_is_twice_as_audible():
    z = Zombie((0, 0), state=State.INVESTIGATING)
    shot_far = Noise((50, 0), radius=30, firearm=True)
    bang_far = Noise((50, 0), radius=30, firearm=False)
    assert z.can_hear(shot_far)
    assert not z.can_hear(bang_far)


def test_heard_noise_makes_zombie_investigate_then_lose_interest():
    z = Zombie((0, 0))
    far_player = Player((500, 0))
    shot = Noise((25, 0), radius=30, firearm=True)  # idle: heard at half range
    assert z.update(0.01, far_player, [shot], daylight=False) is State.INVESTIGATING
    assert z.target == (25, 0)
    z.update(0.2, far_player, daylight=False)
    assert z.state is State.IDLE


def test_smell_works_in_the_dark_at_close_range():
    z = Zombie((0, 0), settings=ZombieSettings(sight_range=0))
    assert z.update(0.01, Player((2, 0)), daylight=False) is State.CHASING


def test_infection_chance_per_hit():
    always = Zombie((0, 0), settings=ZombieSettings(infection_chance=1.0))
    never = Zombie((0, 0), settings=ZombieSettings(infection_chance=0.0))
    p = Player((1, 0))
    assert always.attack(p, random.Random(0)) and p.survivor.infection > 0
    q = Player((1, 0))
    assert not never.attack(q, random.Random(0)) and q.survivor.infection == 0
    assert q.survivor.health < 100


def test_default_infection_is_rare():
    z, rng = Zombie((0, 0)), random.Random(42)
    infections = sum(z.attack(Player((1, 0)), rng) for _ in range(10_000))
    assert 50 < infections < 150  # about 1%


def test_zombie_dies_at_zero_health():
    z = Zombie((0, 0))
    assert z.health == 40
    z.take_damage(40)
    assert z.state is State.DEAD
    assert z.update(1, Player((0, 0))) is State.DEAD
