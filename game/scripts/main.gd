extends Node3D
## S1 "One house": builds the level in code (no imported art), wires the
## player to the fridge, sink, bed and toilet, and runs day/night.

const HOUSE_SIZE := Vector3(10, 3, 8)

## What's in the kitchen when you arrive. Finite: eat it and it's gone.
var pantry := {"canned beans": 6, "canned tuna": 4, "cooked rice": 3, "apple": 5,
		"bread slice": 8, "chocolate bar": 3, "soda": 4, "beef jerky": 4}

var player: CharacterBody3D
var hud: CanvasLayer
var sun: DirectionalLight3D
var env: Environment
var _foods := Food.catalog()
var _house_area: Area3D


func _ready() -> void:
	_build_environment()
	_build_ground()
	_build_house()
	player = preload("res://scripts/player.gd").new()
	player.position = Vector3(0, 0.1, 7)
	add_child(player)
	player.interact_requested.connect(_on_interact)
	hud = preload("res://scripts/hud.gd").new()
	add_child(hud)
	hud.message("You wake up in an empty house. The power and water still work… for now.")
	GameClock.hour_passed.connect(_on_hour)


func _process(_delta: float) -> void:
	_update_sun()
	GameClock.indoors = _house_area.overlaps_body(player)
	var s: Survivor = GameClock.survivor
	if GameClock.is_sleeping() and (s.energy >= 100.0 or not s.alive()):
		GameClock.set_sleeping(false)
		hud.message("You wake up rested.")
	var target: Interactable = player.nearest()
	hud.set_prompt("E: " + target.prompt if target and s.alive() else "")
	hud.refresh()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_hud"):
		hud.full = not hud.full
	elif event.is_action_pressed("skip_day"):
		skip_hours(24)
	elif event is InputEventKey and event.pressed and event.physical_keycode == KEY_R:
		restart()


func skip_hours(hours: int) -> void:
	for _i in hours:
		GameClock.advance(1.0)
	hud.message("Skipped %d hours." % hours)


func restart() -> void:
	GameClock.calendar = SimCalendar.new()
	GameClock.calendar.hours = 8.0
	GameClock.weather = WeatherSystem.new(GameClock.calendar)
	GameClock.weather.rng.randomize()
	GameClock.survivor = Survivor.new()
	GameClock.set_sleeping(false)
	GameClock._last_hour = 8
	get_tree().reload_current_scene()


# ---- interactions -------------------------------------------------------------
func _on_interact(target: Interactable) -> void:
	var s: Survivor = GameClock.survivor
	if not s.alive():
		return
	match target.kind:
		"fridge":
			eat_next()
		"sink":
			if not GameClock.calendar.city_water_on():
				hud.message("The tap coughs. Nothing. The city water is off.")
				return
			var kept := s.drink(250)
			hud.message("You drink a glass of water." if kept else "You drank too much and threw up.")
		"bed":
			if GameClock.is_sleeping():
				GameClock.set_sleeping(false)
				hud.message("You get up.")
			else:
				GameClock.set_sleeping(true)
				hud.message("You lie down to sleep.")
		"toilet":
			var pee := s.body.urinate()
			var poo := s.body.defecate()
			if pee + poo < 50:
				hud.message("You don't really need to go.")
			else:
				hud.message("Relief. (%.0f ml, %.0f g)" % [pee, poo])


## Eat the first thing left in the pantry, in the order listed.
func eat_next() -> void:
	for item in pantry:
		if pantry[item] > 0:
			pantry[item] -= 1
			var food: Food = _foods[item]
			var kept: bool = GameClock.survivor.eat(food)
			if kept:
				hud.message("You eat: %s (%.0f kcal). %d left." % [item, food.kcal(), pantry[item]])
			else:
				hud.message("You force down %s and throw up." % item)
			return
	hud.message("The kitchen is empty.")


func _on_hour(day: int, hour: int) -> void:
	if hour == 0 and day == int(GameClock.calendar.water_shutoff_day):
		hud.message("The pipes go quiet. City water is off.")
	if hour == 0 and day == int(GameClock.calendar.power_shutoff_day):
		hud.message("The lights die. City power is off.")


# ---- world building -----------------------------------------------------------
func _build_environment() -> void:
	var sky_mat := ProceduralSkyMaterial.new()
	var sky := Sky.new()
	sky.sky_material = sky_mat
	env = Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	add_child(world_env)
	sun = DirectionalLight3D.new()
	sun.shadow_enabled = true
	add_child(sun)


func _update_sun() -> void:
	var h := GameClock.calendar.hour_of_day()
	var angle := (h - 6.0) / 24.0 * TAU  # rises at 06:00, sets at 18:00
	sun.rotation = Vector3(-sin(angle) * 1.3 - 0.05, deg_to_rad(30), 0)
	var daylight := clampf(sin(angle) * 1.5 + 0.2, 0.0, 1.0)
	var overcast: float = {WeatherSystem.Kind.CLEAR: 1.0, WeatherSystem.Kind.CLOUDY: 0.6,
			WeatherSystem.Kind.RAIN: 0.45, WeatherSystem.Kind.STORM: 0.3,
			WeatherSystem.Kind.SNOW: 0.55}[GameClock.weather.current]
	sun.light_energy = maxf(daylight * overcast, 0.06)  # moonlight floor
	sun.light_color = Color(1, 0.97, 0.9).lerp(Color(0.55, 0.65, 1.0), 1.0 - daylight)
	env.ambient_light_energy = 0.15 + 0.45 * daylight * overcast
	env.background_energy_multiplier = 0.05 + 0.95 * daylight


func _build_ground() -> void:
	var ground := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(80, 1, 80)
	shape.shape = box
	shape.position.y = -0.5
	ground.add_child(shape)
	var mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(80, 80)
	mesh.mesh = plane
	mesh.material_override = _mat(Color(0.28, 0.36, 0.2))
	ground.add_child(mesh)
	add_child(ground)


func _build_house() -> void:
	var s := HOUSE_SIZE
	var house := CSGCombiner3D.new()
	house.use_collision = true
	add_child(house)
	var shell := CSGBox3D.new()
	shell.size = Vector3(s.x, s.y + 0.2, s.z)
	shell.position.y = s.y / 2.0
	shell.material = _mat(Color(0.72, 0.68, 0.6))
	house.add_child(shell)
	var hollow := CSGBox3D.new()
	hollow.operation = CSGShape3D.OPERATION_SUBTRACTION
	hollow.size = Vector3(s.x - 0.4, s.y, s.z - 0.4)
	hollow.position.y = s.y / 2.0 - 0.1
	house.add_child(hollow)
	var door := CSGBox3D.new()
	door.operation = CSGShape3D.OPERATION_SUBTRACTION
	door.size = Vector3(1.1, 2.1, 1.0)
	door.position = Vector3(0, 1.05, s.z / 2.0)
	house.add_child(door)
	for x in [-3.0, 3.0]:
		var window := CSGBox3D.new()
		window.operation = CSGShape3D.OPERATION_SUBTRACTION
		window.size = Vector3(1.2, 0.9, 1.0)
		window.position = Vector3(x, 1.5, s.z / 2.0)
		house.add_child(window)
	var floor_box := CSGBox3D.new()  # wooden floor inside
	floor_box.size = Vector3(s.x - 0.4, 0.05, s.z - 0.4)
	floor_box.position.y = 0.025
	floor_box.material = _mat(Color(0.45, 0.33, 0.22))
	house.add_child(floor_box)

	# Furniture: [kind, prompt, size, position, colour]
	var furniture := [
		["fridge", "Eat something", Vector3(0.8, 1.8, 0.7), Vector3(-4.2, 0.9, -3.3), Color(0.9, 0.9, 0.92)],
		["sink", "Drink from the tap", Vector3(1.2, 0.9, 0.6), Vector3(-2.6, 0.45, -3.4), Color(0.6, 0.62, 0.66)],
		["bed", "Sleep", Vector3(1.5, 0.5, 2.1), Vector3(3.6, 0.25, -2.6), Color(0.35, 0.4, 0.6)],
		["toilet", "Use the toilet", Vector3(0.5, 0.45, 0.7), Vector3(4.4, 0.23, 2.8), Color(0.95, 0.95, 0.95)],
	]
	for f in furniture:
		var block := CSGBox3D.new()
		block.size = f[2]
		block.position = f[3]
		block.material = _mat(f[4])
		house.add_child(block)
		var area := Interactable.make(f[0], f[1], f[2])
		area.position = f[3]
		add_child(area)
		var label := Label3D.new()
		label.text = f[0].capitalize()
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.font_size = 40
		label.position = f[3] + Vector3(0, f[2].y / 2.0 + 0.3, 0)
		add_child(label)

	var roof := MeshInstance3D.new()
	var prism := PrismMesh.new()
	prism.size = Vector3(s.x + 0.8, 1.6, s.z + 0.8)
	roof.mesh = prism
	roof.position.y = s.y + 0.9
	roof.material_override = _mat(Color(0.4, 0.18, 0.15))
	add_child(roof)

	var lamp := OmniLight3D.new()  # works while the city power is on
	lamp.position = Vector3(0, 2.6, 0)
	lamp.omni_range = 9.0
	lamp.light_energy = 1.2
	lamp.name = "Lamp"
	add_child(lamp)

	_house_area = Area3D.new()  # "indoors" for temperature
	_house_area.collision_mask = 1
	var inside := CollisionShape3D.new()
	var inside_box := BoxShape3D.new()
	inside_box.size = Vector3(s.x - 0.4, s.y, s.z - 0.4)
	inside.shape = inside_box
	inside.position.y = s.y / 2.0
	_house_area.add_child(inside)
	add_child(_house_area)


func _physics_process(_delta: float) -> void:
	var lamp: OmniLight3D = get_node("Lamp")
	lamp.visible = GameClock.calendar.city_power_on()


func _mat(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	return m
