extends Area2D

@export var speed = 200
var screen_size


func _ready():
	screen_size = get_viewport_rect().size
	position = Vector2(screen_size.x/2,screen_size.y/2)
	$AnimatedSprite2D.autoplay = "idle"
	

func _handle_input() -> Vector2:
	var velocity = Vector2.ZERO
	if Input.is_action_pressed("move_up"):
		velocity.y -= 1
	if Input.is_action_pressed("move_down"):
		velocity.y += 1
	if Input.is_action_pressed("move_left"):
		velocity.x -= 1
	if Input.is_action_pressed("move_right"):
		velocity.x += 1
	if velocity.length() > 0:
		velocity = velocity.normalized() * speed
		$AnimatedSprite2D.play("walk", 2.0)	
	else : 
		$AnimatedSprite2D.play("idle")
		
	return velocity
func _process(delta: float) -> void:
	
	position += delta * _handle_input()
	
