extends SceneTree
## Headless test runner:
##   godot --headless --path game --script res://tests/run_tests.gd
## Checks the GDScript port against golden values from the Python models,
## plus a few behaviour tests. Exits with code 1 on any failure.

const TOLERANCE := 1e-6  # relative

var failures := 0
var checks := 0


func _init() -> void:
	var golden: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/golden.json"))
	_compare("meal", _meal(), golden["meal"])
	_compare("mixed_activity", _mixed_activity(), golden["mixed_activity"])
	_compare("water_only_days", _water_only_days(), golden["water_only_days"])
	_behaviour_tests()
	print("%d checks, %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)


func _body_state(b: Body) -> Dictionary:
	return {"stomach": b.stomach.volume(), "glycogen": b.glycogen, "fat": b.fat_store,
			"muscle": b.muscle_protein, "water": b.body_water, "bladder": b.bladder,
			"colon": b.colon_solids + b.colon_water, "satiety": b.satiety(),
			"kcal_burned": b.kcal_burned}


func _survivor_state(s: Survivor) -> Dictionary:
	var d := _body_state(s.body)
	d.merge({"energy": s.energy, "stamina": s.stamina, "health": s.health, "infection": s.infection})
	return d


func _meal() -> Array:
	var foods := Food.catalog()
	var b := Body.new()
	b.eat(foods["canned beans"])
	b.eat(foods["bread slice"])
	b.drink(300)
	var snaps := []
	for _i in 8:
		b.tick(1)
		snaps.append(_body_state(b))
	return snaps


func _mixed_activity() -> Array:
	var A := Survivor.Activity
	var s := Survivor.new()
	var plan := [[0.5, A.SPRINT, 35.0], [2.0, A.WALK, -5.0], [1.0, A.IDLE, 20.0],
			[8.0, A.SLEEP, 12.0], [3.0, A.IDLE, 20.0]]
	s.eat(Food.catalog()["chocolate bar"])
	s.drink(500, Survivor.WaterQuality.DIRTY)
	var snaps := []
	for step in plan:
		s.tick(step[0], step[1], step[2])
		snaps.append(_survivor_state(s))
	return snaps


func _water_only_days() -> Array:
	var s := Survivor.new()
	var snaps := []
	for _d in 5:
		for hour in 24:
			var asleep := hour < 8
			if not asleep:
				s.drink(150)
			s.tick(1, Survivor.Activity.SLEEP if asleep else Survivor.Activity.IDLE)
			if s.body.needs_pee():
				s.body.urinate()
		snaps.append(_survivor_state(s))
	return snaps


func _compare(label: String, got: Array, want: Array) -> void:
	_check(got.size() == want.size(), "%s: %d snapshots, expected %d" % [label, got.size(), want.size()])
	for i in min(got.size(), want.size()):
		for key in want[i]:
			var a: float = got[i][key]
			var b: float = want[i][key]
			var ok: bool = absf(a - b) <= TOLERANCE * max(1.0, absf(b))
			_check(ok, "%s[%d].%s = %.9f, python %.9f" % [label, i, key, a, b])


func _behaviour_tests() -> void:
	var foods := Food.catalog()
	# Overeating makes you vomit, not die.
	var s := Survivor.new()
	var cans := 0
	while s.body.vomit_count == 0 and cans < 20:
		s.eat(foods["canned beans"])
		cans += 1
	_check(cans >= 6 and cans <= 9 and s.alive(), "vomit after 6-9 cans, got %d" % cans)
	# City water shuts off on day 30.
	var cal := SimCalendar.new()
	_check(cal.city_water_on(), "water on at start")
	cal.advance(24 * 30)
	_check(not cal.city_water_on(), "water off on day 30")
	# Winter is colder than summer.
	var w := WeatherSystem.new(SimCalendar.new())
	w.calendar.hours = 95 * 24 + 12
	var winter := w.temperature()
	w.calendar.hours = 35 * 24 + 12
	_check(winter < w.temperature(), "winter colder than summer")
	# Indoors is milder than outside on a winter night.
	w.calendar.hours = 95 * 24 + 3
	_check(w.temperature(true) > w.temperature(), "indoors warmer on a winter night")


func _check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + message)
