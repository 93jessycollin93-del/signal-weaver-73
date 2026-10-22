extends Node
## Autoload: owns the world calendar, weather and the player's survivor, and
## advances them in game time. One real second = `game_minutes_per_second`
## game minutes; sleeping fast-forwards.

signal hour_passed(day: int, hour: int)

const NORMAL_SPEED := 1.0      # game minutes per real second -> 24 real minutes per day
const SLEEP_SPEED := 30.0      # 8 h of sleep in 16 real seconds

var calendar := SimCalendar.new()
var weather := WeatherSystem.new(calendar)
var survivor := Survivor.new()
var activity := Survivor.Activity.IDLE
var indoors := true
var game_minutes_per_second := NORMAL_SPEED
var paused := false
var _last_hour := -1


func _ready() -> void:
	calendar.hours = 8.0  # start the first morning at 08:00
	weather.rng.randomize()
	_last_hour = int(calendar.hours)


func _process(delta: float) -> void:
	if paused or not survivor.alive():
		return
	advance(delta * game_minutes_per_second / 60.0)


## Advance the whole world by `hours` of game time.
func advance(hours: float) -> void:
	calendar.advance(hours)
	survivor.tick(hours, activity, weather.temperature(indoors))
	while int(calendar.hours) > _last_hour:
		_last_hour += 1
		weather.roll_hour()
		hour_passed.emit(int(calendar.day()), _last_hour % 24)


func set_sleeping(sleeping: bool) -> void:
	activity = Survivor.Activity.SLEEP if sleeping else Survivor.Activity.IDLE
	game_minutes_per_second = SLEEP_SPEED if sleeping else NORMAL_SPEED


func is_sleeping() -> bool:
	return activity == Survivor.Activity.SLEEP


## "08:30, day 1"
func time_text() -> String:
	var h := calendar.hour_of_day()
	return "%02d:%02d  day %d  %s" % [int(h), int(fmod(h, 1.0) * 60.0), int(calendar.day()) + 1,
			calendar.season()]
