extends CharacterBody3D
## Third-person survivor: WASD to move, mouse to look, Shift to sprint,
## E to use the nearest thing. Movement drives GameClock.activity.

signal interact_requested(target: Interactable)

const WALK_SPEED := 2.2
const SPRINT_SPEED := 5.5
const JUMP_VELOCITY := 4.0
const MOUSE_SENSITIVITY := 0.003

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity", 9.8)
var yaw := 0.0
var pitch := -0.25
var nearby: Array[Interactable] = []

var _pivot: Node3D
var _arm: SpringArm3D
var _model: Node3D
var _reach: Area3D


func _ready() -> void:
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.3
	capsule.height = 1.75
	shape.shape = capsule
	shape.position.y = 0.875
	add_child(shape)

	_model = Node3D.new()
	add_child(_model)
	var body_mesh := MeshInstance3D.new()
	var cap := CapsuleMesh.new()
	cap.radius = 0.3
	cap.height = 1.75
	body_mesh.mesh = cap
	body_mesh.position.y = 0.875
	body_mesh.material_override = _material(Color(0.35, 0.45, 0.3))
	_model.add_child(body_mesh)
	var nose := MeshInstance3D.new()  # shows which way you face
	var nose_box := BoxMesh.new()
	nose_box.size = Vector3(0.18, 0.12, 0.25)
	nose.mesh = nose_box
	nose.position = Vector3(0, 1.5, -0.32)
	nose.material_override = _material(Color(0.8, 0.65, 0.5))
	_model.add_child(nose)

	_pivot = Node3D.new()
	_pivot.position.y = 1.6
	add_child(_pivot)
	_arm = SpringArm3D.new()
	_arm.spring_length = 3.2
	_arm.margin = 0.2
	_arm.add_excluded_object(get_rid())
	_pivot.add_child(_arm)
	var cam := Camera3D.new()
	cam.position = Vector3(0.45, 0.1, 0)  # over-the-shoulder
	_arm.add_child(cam)
	cam.current = true

	_reach = Area3D.new()
	_reach.collision_layer = 0
	_reach.collision_mask = 2
	var reach_shape := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = 0.6
	reach_shape.shape = sphere
	reach_shape.position.y = 1.0
	_reach.add_child(reach_shape)
	add_child(_reach)
	_reach.area_entered.connect(func(a): if a is Interactable: nearby.append(a))
	_reach.area_exited.connect(func(a): nearby.erase(a))

	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		yaw -= event.relative.x * MOUSE_SENSITIVITY
		pitch = clampf(pitch - event.relative.y * MOUSE_SENSITIVITY, -1.2, 0.6)
	elif event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	elif event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event.is_action_pressed("interact"):
		var target := nearest()
		if target:
			interact_requested.emit(target)


func _physics_process(delta: float) -> void:
	_pivot.rotation = Vector3(pitch, yaw, 0)
	if not is_on_floor():
		velocity.y -= gravity * delta

	var s: Survivor = GameClock.survivor
	if GameClock.is_sleeping() or not s.alive():
		velocity.x = 0
		velocity.z = 0
		move_and_slide()
		return

	if Input.is_action_just_pressed("jump") and is_on_floor() and s.stamina > 5:
		velocity.y = JUMP_VELOCITY
		s.stamina -= 5

	var input := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var dir := (Basis(Vector3.UP, yaw) * Vector3(input.x, 0, input.y)).normalized()
	var sprinting := Input.is_action_pressed("sprint") and s.stamina > 1.0 and dir != Vector3.ZERO
	var speed := SPRINT_SPEED if sprinting else WALK_SPEED
	if s.energy < 15:
		speed *= 0.6  # exhausted: you shuffle
	velocity.x = dir.x * speed
	velocity.z = dir.z * speed
	if dir != Vector3.ZERO:
		_model.rotation.y = lerp_angle(_model.rotation.y, atan2(-dir.x, -dir.z), 10 * delta)
	move_and_slide()

	if sprinting:
		GameClock.activity = Survivor.Activity.SPRINT
	elif dir != Vector3.ZERO:
		GameClock.activity = Survivor.Activity.WALK
	else:
		GameClock.activity = Survivor.Activity.IDLE


func nearest() -> Interactable:
	var best: Interactable = null
	var best_d := INF
	for a in nearby:
		var d := global_position.distance_squared_to(a.global_position)
		if d < best_d:
			best_d = d
			best = a
	return best


func _material(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	return m
