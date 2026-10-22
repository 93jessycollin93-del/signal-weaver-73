class_name Survivor
extends RefCounted
## Fatigue, stamina, health and infection on top of Body. Port of sim/survival.py.

enum Activity { IDLE, WALK, SPRINT, SLEEP }
enum WaterQuality { CLEAN, DIRTY }

## Metabolic equivalents (multiples of resting metabolic rate).
const MET := {Activity.SLEEP: 0.95, Activity.IDLE: 1.3, Activity.WALK: 3.5, Activity.SPRINT: 10.0}


class Config:
	var energy_drain := 3.0
	var sleep_energy_gain := 12.5
	var walk_energy_multiplier := 1.5
	var sprint_energy_multiplier := 3.0
	var low_glycogen_energy_multiplier := 1.3
	var stamina_regen := 300.0
	var stamina_sprint_cost := 600.0
	var exhausted_stamina_penalty := 1.5
	var comfort_min := 10.0
	var comfort_max := 28.0
	var cold_energy_per_degree := 0.3
	var heat_exhaustion_temp := 38.0
	var exhausted_damage := 5.0
	var infection_damage := 3.0
	var dirty_water_infection := 8.0
	var contaminated_food_infection := 10.0
	var infection_recovery := 0.5
	var hud_low := 25.0
	var hud_high := 100.0


var energy := 100.0
var stamina := 100.0
var health := 100.0
var infection := 0.0
var body := Body.new()
var config := Config.new()
var _last_temp := 20.0


func alive() -> bool:
	return health > 0.0


## Satiety on the HUD scale: 100 = comfortably full, >100 stuffed, 0 = starving.
func hunger() -> float:
	return max(0.0, 100.0 * body.satiety())


## Hydration on the HUD scale: 100 = normal, 0 = 10% body water lost.
func thirst() -> float:
	return max(0.0, 100.0 * body.hydration())


func heat_exhausted() -> bool:
	return _last_temp >= config.heat_exhaustion_temp


func tick(h: float, activity := Activity.IDLE, temperature := 20.0) -> void:
	if not alive():
		return
	var c := config
	_last_temp = temperature
	body.tick(h, MET[activity], temperature, infection)

	if activity == Activity.SLEEP:
		energy += c.sleep_energy_gain * h
	else:
		var mult := 1.0
		if activity == Activity.WALK:
			mult = c.walk_energy_multiplier
		elif activity == Activity.SPRINT:
			mult = c.sprint_energy_multiplier
		if body.glycogen_fraction() < body.config.low_glycogen:
			mult *= c.low_glycogen_energy_multiplier
		var rate := c.energy_drain * mult
		if temperature < c.comfort_min:
			rate += (c.comfort_min - temperature) * c.cold_energy_per_degree
		energy -= rate * h

	if activity == Activity.SPRINT:
		var cost := c.stamina_sprint_cost
		if energy < 20.0:
			cost *= c.exhausted_stamina_penalty
		stamina -= cost * h
	else:
		stamina += c.stamina_regen * h * min(1.0, 0.3 + body.glycogen_fraction())

	var damage := body.damage_per_hour()
	if energy <= 0.0:
		damage += c.exhausted_damage
	damage += c.infection_damage * infection / 100.0
	health -= damage * h

	if body.satiety() > 0.5 and body.hydration() > 0.5 and infection > 0.0:
		infection -= c.infection_recovery * h
	_clamp()


## Eat something. Returns false if you threw it back up.
func eat(food: Food) -> bool:
	if food.contaminated:
		infection += config.contaminated_food_infection
	var kept := body.eat(food)
	_clamp()
	return kept


func drink(ml: float, quality := WaterQuality.CLEAN) -> bool:
	if quality == WaterQuality.DIRTY:
		infection += config.dirty_water_infection
	var kept := body.drink(ml)
	_clamp()
	return kept


## Stats the HUD should show: only those at extremes.
func hud_visible() -> Dictionary:
	var out := {}
	for pair in [["hunger", hunger()], ["thirst", thirst()], ["energy", energy]]:
		if pair[1] < config.hud_low or pair[1] > config.hud_high:
			out[pair[0]] = pair[1]
	return out


func _clamp() -> void:
	energy = clampf(energy, 0.0, 100.0)
	stamina = clampf(stamina, 0.0, 100.0)
	health = clampf(health, 0.0, 100.0)
	infection = clampf(infection, 0.0, 100.0)
