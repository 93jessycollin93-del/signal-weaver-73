class_name SimCalendar
extends RefCounted
## Shared world clock: game days, utility shutoff dates, seasons.
## Port of sim/calendar.py.

const SEASONS := ["spring", "summer", "autumn", "winter"]

var hours: float = 0.0
var water_shutoff_day: float = 30.0
var power_shutoff_day: float = 46.0
var days_per_season: int = 30
var start_season: int = 0


func day() -> float:
	return hours / 24.0


func hour_of_day() -> float:
	return fmod(hours, 24.0)


func is_daytime() -> bool:
	var h := hour_of_day()
	return h >= 6.0 and h < 20.0


func season() -> String:
	var index := (int(floor(day() / days_per_season)) + start_season) % SEASONS.size()
	return SEASONS[index]


func city_water_on() -> bool:
	return day() < water_shutoff_day


func city_power_on() -> bool:
	return day() < power_shutoff_day


func advance(h: float) -> void:
	hours += h
