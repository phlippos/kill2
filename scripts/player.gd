extends CharacterBody2D

@export var speed: int = 200
@export var gravity: int = 800
@export var jump_force: int = 400

var screen_size: Vector2
var hp: int = 100
var player_id: int
var status: bool = true # dead : False (ölü) or alive : True (yaşıyor)

func _ready() -> void:
	screen_size = get_viewport_rect().size
	position = Vector2(screen_size.x / 2, screen_size.y / 2)
	$AnimatedSprite2D.play("idle")

func _handle_input() -> void:
	var dir_x := 0
	
	if Input.is_action_pressed("move_left"):
		dir_x -= 1
	if Input.is_action_pressed("move_right"):
		dir_x += 1

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = -jump_force
		$AnimatedSprite2D.play("jump")

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

# Karakter hasar alır
func _take_damage(amount: int) -> void:
	hp -= amount
	if hp <= 0:
		hp = 0
		_is_dead()

# Öldü mü?
func _is_dead() -> void:
	status = hp <= 0

# Yeniden doğma
func _respawn(new_position: Vector2) -> void:
	if not status: # Eğer ölü ise
		position = new_position.clamp(Vector2.ZERO, screen_size)
		hp = 100
		status = true

# Ateş etme
func fire() -> void:
	pass
	
func _on_bullet_body_entered(body: Node2D) -> void:
	_take_damage(20) # Örnek: bir mermi değerse 20 can gitsin

func _physics_process(delta: float) -> void:

	if not is_on_floor():
		velocity.y += gravity * delta


	_handle_input()

	move_and_slide()
