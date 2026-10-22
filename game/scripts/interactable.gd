class_name Interactable
extends Area3D
## Something the player can use with E. `kind` picks the behaviour in main.gd.

@export var kind := ""
@export var prompt := ""


static func make(p_kind: String, p_prompt: String, size: Vector3) -> Interactable:
	var area := Interactable.new()
	area.kind = p_kind
	area.prompt = p_prompt
	area.collision_layer = 2
	area.collision_mask = 0
	area.monitorable = true
	area.monitoring = false
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size + Vector3(1.2, 0.6, 1.2)  # reach a little around the object
	shape.shape = box
	area.add_child(shape)
	return area
