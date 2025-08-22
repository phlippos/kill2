extends Area2D

@export var speed = 200
var screen_size
var hp: int = 100
var player_id: int
var status: bool = true # dead : False or alive : True

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
		
	if velocity.x != 0:
		$AnimatedSprite2D.animation = "walk"
		$AnimatedSprite2D.flip_v = false
		$AnimatedSprite2D.flip_h = velocity.x < 0
		
	if velocity.length() > 0:
		velocity = velocity.normalized() * speed
		$AnimatedSprite2D.play("walk", 2.0)	
	else : 
		$AnimatedSprite2D.play("idle")
		
	return velocity
	
func _move(delta: float) -> void:
	position += delta * _handle_input()
	position = position.clamp(Vector2.ZERO,screen_size)


func _take_damage(amount: int) -> void:
	hp -= amount

func _is_dead() -> void:
	status = hp == 0
	
func _respawn(position: Vector2):
	# if the player is dead, then he respawns in a random field in the map
	# dont forget the boundaries
	# status = True -> if player respawns then alive !!!!!!!!!!!!!!!!!!!!!
	pass

func fire():
	# 1) Local efektleri tetikle (animasyon, ses vs.)
	# 2) Mermi node’unu sahneye ekle (Bullet.gd instance)
	# 3) Network.gd’ye ateş bilgisi gönder (owner_id, yön, hız)
	pass
	
func _on_bullet_body_entered(body: Node2D) -> void:
	pass # Replace with function body.
	
	
	

func _process(delta: float) -> void:
	_move(delta)
	#_is_dead()
