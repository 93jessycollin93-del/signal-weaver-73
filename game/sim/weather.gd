class_name WeatherSystem
extends RefCounted
## Seasons, day/night temperature and hourly weather. Port of sim/weather.py.

enum Kind { CLEAR, CLOUDY, RAIN, STORM, SNOW }

const NAMES := {Kind.CLEAR: "clear", Kind.CLOUDY: "cloudy", Kind.RAIN: "rain",
		Kind.STORM: "storm", Kind.SNOW: "snow"}
const SEASON_MEAN := {"spring": 8.0, "summer": 22.0, "autumn": 9.0, "winter": -8.0}
const DAY_NIGHT_SWING := 6.0
const OFFSET := {Kind.CLEAR: 0.0, Kind.CLOUDY: -1.0, Kind.RAIN: -3.0, Kind.STORM: -5.0, Kind.SNOW: -4.0}
const SEASON_WEIGHTS := {
	"spring": {Kind.CLEAR: 4, Kind.CLOUDY: 3, Kind.RAIN: 3, Kind.STORM: 1},
	"summer": {Kind.CLEAR: 6, Kind.CLOUDY: 2, Kind.RAIN: 1, Kind.STORM: 1},
	"autumn": {Kind.CLEAR: 3, Kind.CLOUDY: 4, Kind.RAIN: 4, Kind.STORM: 1},
	"winter": {Kind.CLEAR: 3, Kind.CLOUDY: 3, Kind.SNOW: 4, Kind.STORM: 1},
}

var calendar: SimCalendar
var current: Kind = Kind.CLEAR
var persistence := 0.85
var rng := RandomNumberGenerator.new()


func _init(p_calendar: SimCalendar) -> void:
	calendar = p_calendar


func temperature(indoors := false, heated := false) -> float:
	var mean: float = SEASON_MEAN[calendar.season()]
	var swing := DAY_NIGHT_SWING * cos((calendar.hour_of_day() - 15.0) / 24.0 * TAU)
	var outside: float = mean + swing + OFFSET[current]
	if heated:
		return max(outside, 20.0)
	if indoors:
		return outside + 0.5 * (15.0 - outside)
	return outside


## Roll the weather for the next hour. Call once per game hour.
func roll_hour() -> void:
	var weights: Dictionary = SEASON_WEIGHTS[calendar.season()]
	if weights.has(current) and rng.randf() < persistence:
		return
	var total := 0
	for w in weights.values():
		total += w
	var pick := rng.randi_range(1, total)
	for kind in weights:
		pick -= weights[kind]
		if pick <= 0:
			current = kind
			return


func kind_name() -> String:
	return NAMES[current]
