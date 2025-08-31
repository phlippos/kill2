extends CharacterBody2D
@export var speed: int = 200
@export var gravity: int = 800
@export var jump_force: int = 400
@export var max_jumps: int = 2 
@onready var health_bar = $HealthBar
var screen_size: Vector2
var hp: int = 100
var player_id: int
var status: bool = true
var jump_count: int = 0 

func _ready() -> void:
	screen_size = get_viewport_rect().size
	position = Vector2(screen_size.x / 2, screen_size.y / 2)
	$AnimatedSprite2D.play("idle")
	health_bar._setup_health_bar(100.0, true)

func handle_input() -> void:
	var dir_x := 0
	
	if Input.is_action_pressed("move_left"):
		dir_x -= 1
	if Input.is_action_pressed("move_right"):
		dir_x += 1
	

	if Input.is_action_just_pressed("jump"):
		if is_on_floor():

			velocity.y = -jump_force
			jump_count = 1
			$AnimatedSprite2D.play("jump")
		elif jump_count < max_jumps:

			velocity.y = -jump_force
			jump_count += 1
			$AnimatedSprite2D.play("jump")
	
	if is_on_floor():
		jump_count = 0
	
	velocity.x = dir_x * speed
	if dir_x != 0:
		$AnimatedSprite2D.flip_h = dir_x < 0
	
	if is_on_floor():
		if dir_x != 0:
			$AnimatedSprite2D.play("walk", 2.0)
		else:
			$AnimatedSprite2D.play("idle")
	else:
		if $AnimatedSprite2D.animation != "jump":
			$AnimatedSprite2D.play("jump")

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

func fire() -> void:
	pass
	
func _on_bullet_body_entered(body: Node2D) -> void:
	take_damage(20)

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	handle_input()
	move_and_slide()
