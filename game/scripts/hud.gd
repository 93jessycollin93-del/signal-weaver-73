extends CanvasLayer
## Survival HUD. F1 switches between the full debug view and the minimal view
## that only shows stats at extremes.

var full := true
var _bars := {}
var _info: Label
var _status: Label
var _prompt: Label
var _log: Label
var _death: Label
var _messages: Array[String] = []


func _ready() -> void:
	var panel := PanelContainer.new()
	panel.position = Vector2(16, 16)
	add_child(panel)
	var box := VBoxContainer.new()
	box.custom_minimum_size = Vector2(300, 0)
	panel.add_child(box)
	_info = Label.new()
	box.add_child(_info)
	for stat in ["hunger", "thirst", "energy", "stamina", "health", "infection"]:
		var row := HBoxContainer.new()
		var name_label := Label.new()
		name_label.text = stat.capitalize()
		name_label.custom_minimum_size = Vector2(80, 0)
		row.add_child(name_label)
		var bar := ProgressBar.new()
		bar.max_value = 100  # stuffed / overhydrated show as a status line instead
		bar.custom_minimum_size = Vector2(200, 18)
		bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(bar)
		box.add_child(row)
		_bars[stat] = {"row": row, "bar": bar}
	_status = Label.new()
	box.add_child(_status)

	_prompt = Label.new()
	_prompt.anchor_left = 0.5
	_prompt.anchor_right = 0.5
	_prompt.anchor_top = 0.62
	_prompt.offset_left = -200
	_prompt.offset_right = 200
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(_prompt)

	_log = Label.new()
	_log.anchor_top = 1.0
	_log.anchor_bottom = 1.0
	_log.offset_left = 16
	_log.offset_top = -150
	_log.offset_right = 700
	add_child(_log)

	_death = Label.new()
	_death.set_anchors_preset(Control.PRESET_CENTER)
	_death.add_theme_font_size_override("font_size", 40)
	_death.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_death.visible = false
	add_child(_death)

	var help := Label.new()
	help.text = "WASD move · Mouse look · Shift sprint · E use\nSpace jump · F1 HUD · F5 skip day · R restart"
	help.anchor_left = 1.0
	help.anchor_right = 1.0
	help.offset_left = -640
	help.offset_top = 16
	help.offset_right = -16
	help.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(help)


func message(text: String) -> void:
	_messages.append("[%s] %s" % [GameClock.time_text().substr(0, 5), text])
	if _messages.size() > 6:
		_messages.pop_front()
	_log.text = "\n".join(_messages)


func set_prompt(text: String) -> void:
	_prompt.text = text


func refresh() -> void:
	var s: Survivor = GameClock.survivor
	var b: Body = s.body
	var w: WeatherSystem = GameClock.weather
	_info.text = "%s\n%s  %.0f °C %s" % [GameClock.time_text(), w.kind_name(),
			w.temperature(GameClock.indoors), "(indoors)" if GameClock.indoors else ""]
	var values := {"hunger": s.hunger(), "thirst": s.thirst(), "energy": s.energy,
			"stamina": s.stamina, "health": s.health, "infection": s.infection}
	var extremes := s.hud_visible()
	for stat in _bars:
		_bars[stat]["bar"].value = values[stat]
		var show: bool = full or extremes.has(stat) or (stat == "health" and s.health < 100) \
				or (stat == "infection" and s.infection > 0) or (stat == "stamina" and s.stamina < 100)
		_bars[stat]["row"].visible = show
	var lines: Array[String] = []
	if b.needs_pee():
		lines.append("Need to pee")
	if b.needs_poo():
		lines.append("Need the toilet")
	if s.hunger() > 110:
		lines.append("Stuffed")
	if s.heat_exhausted():
		lines.append("Heat exhaustion")
	if b.glycogen_fraction() < b.config.low_glycogen:
		lines.append("Out of energy reserves")
	if GameClock.is_sleeping():
		lines.append("Sleeping… (E to wake)")
	if full:
		lines.append("Stomach %.0f ml · Glycogen %.0f g · Fat %.1f kg · Body water %.1f L" % [
				b.stomach.volume(), b.glycogen, b.fat_store / 1000.0, b.body_water / 1000.0])
		lines.append("City water %s · Power %s" % [
				"on" if GameClock.calendar.city_water_on() else "OFF",
				"on" if GameClock.calendar.city_power_on() else "OFF"])
	_status.text = "\n".join(lines)
	if not s.alive():
		_death.visible = true
		_death.text = "You died on day %d.\nPress R to restart." % (int(GameClock.calendar.day()) + 1)
	else:
		_death.visible = false
