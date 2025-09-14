extends CharacterBody2D

@onready var health_bar = $HealthBar
@export var player_id: int = -1
@export var username: String 
@export var direction: Vector2
@export var health: int = 100
@export var is_alive: bool
@export var score: int
var target_position: Vector2

func _ready() -> void:
	health_bar._setup_health_bar(health,true)
	$"/root/Main/Game".connect("kill", _on_kill_signal)
	
func update_position(new_position: Vector2):
	target_position = new_position

func _physics_process(delta):
	velocity = (target_position - position) / delta
	move_and_slide()

func load_player(player_id: int, username: String, pos: Vector2, direction: Vector2, health: int, is_alive: bool, score: int):
		self.player_id = player_id
		self.username = username
		self.position = pos
		self.direction = direction
		self.health = health
		self.is_alive = is_alive
		self.score = score

func set_health(health):
	health_bar._change_value(health)
	self.health = health

func set_is_alive(is_alive):
	self.is_alive = is_alive
	if !is_alive:
		$AnimatedSprite2D.play("dead")

func set_score(score):
	self.score = score

func update_critical_info(health, is_alive, score):
	self.set_health(health)
	self.set_is_alive(is_alive)
	self.set_score(score)


func mark_for_deletion():
	queue_free()

func _on_kill_signal():
	mark_for_deletion()
