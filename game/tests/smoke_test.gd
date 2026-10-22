extends SceneTree
## Loads the real S1 scene headless and plays it:
##   godot --headless --path game --script res://tests/smoke_test.gd

var failures := 0
var checks := 0


func _init() -> void:
	_run.call_deferred()


func _run() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await _frames(5)
	var clock = root.get_node("GameClock")
	var s: Survivor = clock.survivor
	var player: CharacterBody3D = main.player

	# Walking up to the fridge offers "Eat something".
	player.global_position = Vector3(-4.2, 0.1, -2.3)
	await _frames(10)
	var target: Interactable = player.nearest()
	_check(target != null and target.kind == "fridge", "fridge is the nearest thing")
	var hunger_before := s.hunger()
	player.interact_requested.emit(target)
	_check(s.hunger() > hunger_before, "eating raises satiety")
	_check(main.pantry["canned beans"] == 5, "a can was taken from the pantry")

	# Indoors detection.
	_check(clock.indoors, "player counts as indoors in the kitchen")

	# Tap works while city water is on.
	player.global_position = Vector3(-2.6, 0.1, -2.4)
	await _frames(10)
	target = player.nearest()
	_check(target != null and target.kind == "sink", "sink is the nearest thing")
	var water_before := s.body.stomach.water
	player.interact_requested.emit(target)
	_check(s.body.stomach.water > water_before, "drinking puts water in the stomach")

	# Sleeping fast-forwards and wakes you when rested.
	s.energy = 40.0
	player.global_position = Vector3(3.6, 0.1, -1.2)
	await _frames(10)
	target = player.nearest()
	_check(target != null and target.kind == "bed", "bed is the nearest thing")
	player.interact_requested.emit(target)
	_check(clock.is_sleeping(), "using the bed starts sleep")
	var hours_before: float = clock.calendar.hours
	clock.advance(5.0)
	main._process(0.0)
	_check(not clock.is_sleeping() and s.energy >= 99.0, "you wake up rested")
	_check(clock.calendar.hours > hours_before, "time passed while sleeping")

	# F5 skip: a day passes and the body keeps simulating.
	var kcal_before := s.body.kcal_burned
	main.skip_hours(24)
	_check(s.body.kcal_burned > kcal_before + 1500, "a skipped day burns a day of energy")

	# Jump the calendar (not the body) to the water shutoff: the tap stops.
	clock.calendar.hours = 24.0 * 30 + 9.0
	clock._last_hour = int(clock.calendar.hours)
	_check(not clock.calendar.city_water_on(), "city water is off after day 30")
	player.global_position = Vector3(-2.6, 0.1, -2.4)
	await _frames(10)
	_check(s.alive(), "survivor is alive for the tap test")
	water_before = s.body.stomach.water
	player.interact_requested.emit(player.nearest())
	_check(s.body.stomach.water == water_before, "the dead tap gives no water")

	# Walking outside leaves the house.
	player.global_position = Vector3(0, 0.1, 12)
	await _frames(10)
	_check(not clock.indoors, "outside is not indoors")

	print("%d checks, %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)


func _frames(n: int) -> void:
	for _i in n:
		await physics_frame


func _check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + message)
