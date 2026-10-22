class_name Food
extends RefCounted
## A food or drink, by nutrition. Port of Food in sim/digestion.py.

const KCAL_PER_G := {"carbs": 4.0, "protein": 4.0, "fat": 9.0}

var name: String
var water: float
var carbs: float
var protein: float
var fat: float
var fibre: float
var contaminated: bool


func _init(p_name: String, p_water := 0.0, p_carbs := 0.0, p_protein := 0.0,
		p_fat := 0.0, p_fibre := 0.0, p_contaminated := false) -> void:
	name = p_name
	water = p_water
	carbs = p_carbs
	protein = p_protein
	fat = p_fat
	fibre = p_fibre
	contaminated = p_contaminated


func kcal() -> float:
	return carbs * 4.0 + protein * 4.0 + fat * 9.0


func mass() -> float:
	return water + carbs + protein + fat + fibre


## Reference foods, per typical serving (generic nutrition values).
static func catalog() -> Dictionary:
	return {
		"water 500ml": Food.new("water 500ml", 500),
		"canned beans": Food.new("canned beans", 300, 45, 20, 2, 15),
		"apple": Food.new("apple", 150, 22, 0.5, 0.3, 4),
		"bread slice": Food.new("bread slice", 12, 14, 3, 1, 1),
		"beef jerky": Food.new("beef jerky", 12, 5, 17, 4),
		"chocolate bar": Food.new("chocolate bar", 1, 30, 4, 15, 3),
		"cooked rice": Food.new("cooked rice", 140, 56, 5, 0.5, 1),
		"canned tuna": Food.new("canned tuna", 110, 0, 40, 8),
		"soda": Food.new("soda", 320, 39),
	}
