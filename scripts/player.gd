extends CharacterBody2D
@export var speed: int = 200
@export var gravity: int = 800
@export var jump_force: int = 400
@export var max_jumps: int = 2 
@onready var health_bar = $HealthBar
@export var username = ""

var screen_size: Vector2
var hp: int = 100
var player_id: int
var status: bool = true
var jump_count: int = 0 
var is_shooting: bool = false
var shot_timer: Timer  
var bullet_scene = preload("res://scenes/bullet.tscn")
func _ready() -> void:
	screen_size = get_viewport_rect().size
	position = Vector2(screen_size.x / 2, screen_size.y / 2)
	$AnimatedSprite2D.play("idle")
	health_bar._setup_health_bar(100.0, true)
	
	shot_timer = Timer.new()
	shot_timer.wait_time = 0.5
	shot_timer.one_shot = true
	shot_timer.timeout.connect(_on_shot_timer_timeout)
	add_child(shot_timer)

func handle_input() -> void:
	var dir_x := 0
	
	var mouse_pos = get_global_mouse_position()
	var mouse_direction = mouse_pos.x - global_position.x
	
	if Input.is_action_just_pressed("shot") and not is_shooting:
		fire()
		is_shooting = true
		shot_timer.start()  
	
	if Input.is_action_pressed("move_left"):
		dir_x -= 1
	if Input.is_action_pressed("move_right"):
		dir_x += 1
	
	if Input.is_action_just_pressed("jump"):
		if is_on_floor():
			velocity.y = -jump_force
			jump_count = 0
			if not is_shooting:
				$AnimatedSprite2D.play("jump")
		elif jump_count < max_jumps - 1:
			velocity.y = -jump_force
			jump_count += 1
			if not is_shooting:
				$AnimatedSprite2D.play("jump")
	
	if is_on_floor():
		jump_count = 0
	
	velocity.x = dir_x * speed
	
	if dir_x != 0:
		$AnimatedSprite2D.flip_h = dir_x < 0
	else:
		$AnimatedSprite2D.flip_h = mouse_direction < 0
	
	if not is_shooting:
		if is_on_floor():
			if dir_x != 0:
				$AnimatedSprite2D.play("walk", 2.0)
			else:
				$AnimatedSprite2D.play("idle")
		else:
			if $AnimatedSprite2D.animation != "jump":
				$AnimatedSprite2D.play("jump")

func _on_shot_timer_timeout() -> void:
	is_shooting = false

func take_damage(amount: int) -> void:
	hp -= amount
	if hp <= 0:
		hp = 0
		is_dead()

func is_dead() -> void:
	status = hp <= 0

func respawn(new_position: Vector2) -> void:
	if not status:
		position = new_position.clamp(Vector2.ZERO, screen_size)
		hp = 100
		status = true
		jump_count = 0  
		is_shooting = false

func fire() -> void:
	$AnimatedSprite2D.play("shot")
	print(global_position)
	var bullet_scene_instance = bullet_scene.instantiate()
	bullet_scene_instance.position = $"Gun/Muzzle".global_position
	var dir_vector = (get_global_mouse_position() - global_position).normalized()
	if dir_vector.x >=0:
		bullet_scene_instance.direction = Vector2.RIGHT
	else:
		bullet_scene_instance.direction = Vector2.LEFT
	get_parent().add_child(bullet_scene_instance)
	
func _on_bullet_body_entered(body: Node2D) -> void:
	take_damage(20)

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	handle_input()
	move_and_slide()

func set_username(username: String) -> void:
	self.username = username
	$UserNameLabel.text = self.username
	print(self.username)
	print($UserNameLabel.text)
