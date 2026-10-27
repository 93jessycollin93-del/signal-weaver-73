class_name Body
extends RefCounted
## Physiological food, water and energy model. Port of sim/digestion.py.
## Food moves stomach -> small intestine -> colon; absorbed carbs fill
## glycogen (overflow becomes fat), fat goes to fat stores, protein repairs
## muscle. Units: grams, millilitres, kcal, hours of game time.
## Golden-tested against the Python model (tests/test_parity.gd).

const LN2 := 0.6931471805599453
const MACROS := ["carbs", "protein", "fat"]
const SOLIDS := ["carbs", "protein", "fat", "fibre"]
const KCAL := {"carbs": 4.0, "protein": 4.0, "fat": 9.0}


class Config:
	var max_step_hours := 0.25
	var hunger_rate := 1.0  # Vein: GS_HungerMultiplier
	var thirst_rate := 1.0  # Vein: GS_ThirstMultiplier
	var normal_body_water := 42000.0
	var max_glycogen := 500.0
	var baseline_muscle_protein := 10000.0
	var bmr_kcal_per_day := 1750.0
	var fever_bmr_per_unit_infection := 0.003
	var comfortable_stomach_ml := 1000.0
	var vomit_stomach_ml := 3000.0
	var stomach_kcal_per_hour := 130.0
	var fat_slowing := 0.5
	var stomach_water_half_life := 0.33
	var meal_water_slowing_kcal := 200.0
	var fibre_only_g_per_hour := 60.0
	var absorb_half_life := {"carbs": 0.4, "protein": 0.8, "fat": 1.5, "water": 0.3}
	var transit_half_life := 4.0
	var colon_water_half_life := 5.0
	var stool_water_per_solid := 3.0
	var bowel_urge_g := 250.0
	var bowel_accident_g := 600.0
	var obligatory_urine_ml_per_day := 500.0
	var excess_water_half_life := 1.0
	var bladder_urge_ml := 300.0
	var bladder_accident_ml := 650.0
	var insensible_ml_per_day := 800.0
	var sweat_ml_per_met_hour := 80.0
	var sweat_ml_per_degree_hour := 40.0
	var vomit_water_loss_ml := 300.0
	var metabolic_water_ml_per_kcal := 0.12
	var carb_share_rest := 0.4
	var carb_share_max := 0.85
	var starving_protein_share := 0.15
	var low_glycogen := 0.15
	var carb_to_fat_efficiency := 0.8
	var shiver_below := 15.0
	var shiver_kcal_per_degree_hour := 8.0
	var dehydration_damage_from := 0.08
	var dehydration_lethal := 0.15
	var muscle_damage_below := 0.75
	var muscle_lethal := 0.55


class Gut:
	var water := 0.0
	var carbs := 0.0
	var protein := 0.0
	var fat := 0.0
	var fibre := 0.0

	func kcal() -> float:
		return carbs * 4.0 + protein * 4.0 + fat * 9.0

	func volume() -> float:
		return water + carbs + protein + fat + fibre

	func add(other) -> void:
		water += other.water
		carbs += other.carbs
		protein += other.protein
		fat += other.fat
		fibre += other.fibre

	func take_solids(f: float) -> Gut:
		var out := Gut.new()
		out.carbs = carbs * f; carbs -= out.carbs
		out.protein = protein * f; protein -= out.protein
		out.fat = fat * f; fat -= out.fat
		out.fibre = fibre * f; fibre -= out.fibre
		return out


var config := Config.new()
var stomach := Gut.new()
var intestine := Gut.new()
var colon_solids := 0.0
var colon_water := 0.0
var bladder := 0.0
var glycogen := 350.0
var fat_store := 12000.0
var muscle_protein := 10000.0
var body_water := 42000.0
var vomit_count := 0
var accidents := 0
var kcal_burned := 0.0


static func _exp_left(half_life: float, h: float) -> float:
	return exp(-LN2 / half_life * h)


# ---- input / output ---------------------------------------------------------
## Swallow food or drink. Returns false if you threw it all back up.
func eat(food: Food) -> bool:
	stomach.add(food)
	if stomach.volume() > config.vomit_stomach_ml:
		vomit()
		return false
	return true


func drink(ml: float) -> bool:
	return eat(Food.new("water", ml))


func vomit() -> void:
	stomach = Gut.new()
	body_water -= config.vomit_water_loss_ml
	vomit_count += 1


func urinate() -> float:
	var amount := bladder
	bladder = 0.0
	return amount


func defecate() -> float:
	var amount := colon_solids + colon_water
	colon_solids = 0.0
	colon_water = 0.0
	return amount


# ---- simulation ---------------------------------------------------------------
func tick(h: float, met := 1.3, temperature := 20.0, infection := 0.0) -> void:
	var steps: int = max(1, ceili(h / config.max_step_hours))
	var dt := h / steps
	for _i in steps:
		_empty_stomach(dt)
		var absorbed := _small_intestine(dt)
		_colon(dt)
		_store(absorbed)
		_spend_energy(dt, met, temperature, infection)
		_water_balance(dt, met, temperature)


func _empty_stomach(h: float) -> void:
	var c := config
	var s := stomach
	var half_life := c.stomach_water_half_life * (1.0 + s.kcal() / c.meal_water_slowing_kcal)
	var water_out := s.water * (1.0 - _exp_left(half_life, h))
	s.water -= water_out
	intestine.water += water_out
	var f: float
	var k := s.kcal()
	if k > 0.0:
		var fat_share := s.fat * 9.0 / k
		var rate := c.stomach_kcal_per_hour * (1.0 - c.fat_slowing * fat_share)
		f = min(1.0, rate * h / k)
	elif s.fibre > 0.0:
		f = min(1.0, c.fibre_only_g_per_hour * h / s.fibre)
	else:
		return
	intestine.add(s.take_solids(f))


func _small_intestine(h: float) -> Gut:
	var c := config
	var gut := intestine
	var kt := LN2 / c.transit_half_life
	var absorbed := Gut.new()
	var passed := Gut.new()
	for nutrient in ["carbs", "protein", "fat", "water"]:
		var amount: float = gut.get(nutrient)
		if amount <= 0.0:
			continue
		var ka: float = LN2 / c.absorb_half_life[nutrient]
		var gone := amount * (1.0 - exp(-(ka + kt) * h))
		absorbed.set(nutrient, gone * ka / (ka + kt))
		passed.set(nutrient, gone * kt / (ka + kt))
		gut.set(nutrient, amount - gone)
	var fibre_out := gut.fibre * (1.0 - exp(-kt * h))
	gut.fibre -= fibre_out
	colon_solids += fibre_out + passed.carbs + passed.protein + passed.fat
	colon_water += passed.water
	return absorbed


func _colon(h: float) -> void:
	var c := config
	var keep := colon_solids * c.stool_water_per_solid
	if colon_water > keep:
		var back := (colon_water - keep) * (1.0 - _exp_left(c.colon_water_half_life, h))
		colon_water -= back
		body_water += back
	if colon_solids + colon_water >= c.bowel_accident_g:
		defecate()
		accidents += 1


func _store(absorbed: Gut) -> void:
	var c := config
	body_water += absorbed.water
	fat_store += absorbed.fat
	var to_muscle: float = min(absorbed.protein, max(0.0, c.baseline_muscle_protein - muscle_protein))
	muscle_protein += to_muscle
	var carbs := absorbed.carbs + (absorbed.protein - to_muscle)  # gluconeogenesis
	var into_glycogen: float = min(carbs, c.max_glycogen - glycogen)
	glycogen += into_glycogen
	var overflow_kcal := (carbs - into_glycogen) * 4.0
	fat_store += overflow_kcal * c.carb_to_fat_efficiency / 9.0


func _spend_energy(h: float, met: float, temperature: float, infection: float) -> void:
	var c := config
	var fever := 1.0 + c.fever_bmr_per_unit_infection * infection
	var need := c.bmr_kcal_per_day / 24.0 * met * fever * h
	if temperature < c.shiver_below:
		need += (c.shiver_below - temperature) * c.shiver_kcal_per_degree_hour * h
	need *= c.hunger_rate
	kcal_burned += need
	body_water += need * c.metabolic_water_ml_per_kcal

	var intensity := clampf((met - 1.0) / 9.0, 0.0, 1.0)
	var carb_share := c.carb_share_rest + (c.carb_share_max - c.carb_share_rest) * intensity
	var protein_kcal := 0.0
	if glycogen < c.low_glycogen * c.max_glycogen:
		protein_kcal = need * c.starving_protein_share
	var carb_kcal: float = min(need * carb_share, glycogen * 4.0)
	glycogen -= carb_kcal / 4.0
	var fat_kcal: float = min(need - carb_kcal - protein_kcal, fat_store * 9.0)
	fat_store -= fat_kcal / 9.0
	protein_kcal = need - carb_kcal - fat_kcal  # muscle covers whatever is left
	muscle_protein = max(0.0, muscle_protein - protein_kcal / 4.0)


func _water_balance(h: float, met: float, temperature: float) -> void:
	var c := config
	var loss := c.insensible_ml_per_day / 24.0 * h
	loss += max(0.0, met - 2.0) * c.sweat_ml_per_met_hour * h
	loss += max(0.0, temperature - 25.0) * c.sweat_ml_per_degree_hour * h
	body_water -= loss * c.thirst_rate
	var urine := c.obligatory_urine_ml_per_day / 24.0 * h
	var surplus := body_water - c.normal_body_water
	if surplus > 0.0:
		urine += surplus * (1.0 - _exp_left(c.excess_water_half_life, h))
	urine = min(urine, max(0.0, body_water - 0.5 * c.normal_body_water))
	body_water -= urine
	bladder += urine
	if bladder >= c.bladder_accident_ml:
		urinate()
		accidents += 1


# ---- what the player feels ----------------------------------------------------
func dehydration() -> float:
	return 1.0 - body_water / config.normal_body_water


func glycogen_fraction() -> float:
	return glycogen / config.max_glycogen


func muscle_fraction() -> float:
	return muscle_protein / config.baseline_muscle_protein


## 1 = comfortably full, >1 = stuffed, 0 = starving.
func satiety() -> float:
	var stretch := stomach.volume() / config.comfortable_stomach_ml
	var digesting: float = min(1.0, intestine.kcal() / 400.0)
	var stores: float = min(1.0, glycogen_fraction() / 0.8)
	return 0.5 * stretch + 0.1 * digesting + 0.4 * stores


## 1 = normal, 0 = 10% of body water lost, >1 = overhydrated.
func hydration() -> float:
	return 1.0 - dehydration() / 0.10


func needs_pee() -> bool:
	return bladder >= config.bladder_urge_ml


func needs_poo() -> bool:
	return colon_solids + colon_water >= config.bowel_urge_g


func damage_per_hour() -> float:
	var c := config
	var dmg := 0.0
	var d := dehydration()
	if d > c.dehydration_damage_from:
		dmg += 100.0 * (d - c.dehydration_damage_from) / (c.dehydration_lethal - c.dehydration_damage_from) / 6.0
	var m := muscle_fraction()
	if m < c.muscle_damage_below:
		dmg += 100.0 * (c.muscle_damage_below - m) / (c.muscle_damage_below - c.muscle_lethal) / 24.0
	if d >= c.dehydration_lethal or m <= c.muscle_lethal:
		dmg = INF
	return dmg
