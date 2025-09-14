extends CharacterBody2D
@export var speed: int = 200
@export var gravity: int = 800
@export var jump_force: int = 400
@export var max_jumps: int = 2 
@onready var health_bar = $HealthBar
@export var username = ""


var screen_size: Vector2
var health: int = 100
var player_id: int
var is_alive: bool = true
var jump_count: int = 0 
var is_shooting: bool = false
var shot_timer: Timer  
var direction
var score
var last_dir_x := 0
var last_dir_y := 0

func _ready() -> void:
	$AnimatedSprite2D.play("idle")
	health_bar._setup_health_bar(100.0, true)
	shot_timer = Timer.new()
	shot_timer.wait_time = 0.5
	shot_timer.one_shot = true
	shot_timer.timeout.connect(_on_shot_timer_timeout)
	add_child(shot_timer)
	
	$"/root/Main/Game".connect("kill", _on_kill_signal)

func load_player(player_id: int, username: String, pos: Vector2, dir: Vector2, health: int, is_alive: bool, score: int):
		self.player_id = player_id
		self.username = username
		position = pos
		self.direction = dir
		self.health = health
		self.is_alive = is_alive
		self.score = score
		show()
		
func handle_input() -> void:
	if Input.is_action_just_pressed("respawn"):
		print("respawn")
		self.respawn()
	if is_alive:
		var dir_x := 0
		var dir_y := 0
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
			dir_y = -1
			if is_on_floor():
				velocity.y = -jump_force
				jump_count = 0
			elif jump_count < max_jumps - 1:
				velocity.y = -jump_force
				jump_count += 1

		if is_on_floor():
			jump_count = 0

		#velocity.x = dir_x * speed

		if dir_x != 0 or dir_y != 0 or (dir_x != last_dir_x or dir_y != last_dir_y):
			Network.send_movement_data(position.x,position.y,dir_x, dir_y)  # pozisyon değil, direction gönder
			last_dir_x = dir_x
			last_dir_y = dir_y

		if dir_x != 0:
			$AnimatedSprite2D.flip_h = dir_x < 0

func _on_shot_timer_timeout() -> void:
	is_shooting = false

func fire() -> void:
	$AnimatedSprite2D.play("shot")
	var muzzle_global_pos = $"Gun/Muzzle".global_position
	var muzzle_pos_x = muzzle_global_pos.x
	var muzzle_pos_y = muzzle_global_pos.y
	var dir_vector = (get_global_mouse_position() - global_position).normalized()
	var muzzle_dir_x
	var muzzle_dir_y
	if dir_vector.x >=0:
		muzzle_dir_x = Vector2.RIGHT.x
		muzzle_dir_y = Vector2.RIGHT.y
	else:
		muzzle_dir_x = Vector2.LEFT.x
		muzzle_dir_y = Vector2.LEFT.y
	Network.send_fire_request(muzzle_dir_x,muzzle_dir_y,muzzle_pos_x,muzzle_pos_y)
	

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	handle_input()
	#move_and_slide()

func set_username(username: String) -> void:
	self.username = username
	$UserNameLabel.text = self.username
	#print(self.username)
	#print($UserNameLabel.text)

func update_from_server(server_position: Vector2, server_velocity: Vector2, is_on_ground: bool):
	"""
	Update player position based on server calculations
	"""
	# Smooth interpolation to server position (optional)
	#print("server_position : ",server_position)
	var distance_to_server = position.distance_to(server_position)
	
	if distance_to_server > 5.0:  # Teleport if too far (lag compensation)
		position = server_position
	else:
		# Smooth interpolation for small corrections
		position = position.lerp(server_position, 0.5)
	
	# Update velocity for animation purposes
	velocity = server_velocity
	if abs(velocity.x) <= 0:
		var mouse_pos = get_global_mouse_position()
		var mouse_direction = mouse_pos.x - global_position.x
		$AnimatedSprite2D.flip_h = mouse_direction < 0
	# Update ground state for animations
	if is_on_ground and not $AnimatedSprite2D.animation == "walk":
		if velocity.x != 0:
			$AnimatedSprite2D.play("walk")
		else:
			$AnimatedSprite2D.play("idle")
	elif not is_on_ground:
		$AnimatedSprite2D.play("jump")
		
func set_health(health):
	health_bar._change_value(health)
	self.health = health

func set_is_alive(is_alive):
	self.is_alive = is_alive
	if !is_alive:
		$AnimatedSprite2D.play("dead")
		await $AnimatedSprite2D.animation_finished
		
func set_score(score):
	self.score = score
	
func update_critical_info(health, is_alive, score):
	self.set_health(health)
	self.set_is_alive(is_alive)
	self.set_score(score)
	
	
func respawn():
	if !is_alive:
		Network.send_respawn_request()
		
func mark_for_deletion():
	queue_free()

func _on_kill_signal():
	mark_for_deletion()
