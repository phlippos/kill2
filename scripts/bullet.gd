extends Area2D

@export var speed: float = 500
var direction: Vector2 = Vector2.ZERO

func _ready():
	pass
	
func _process(delta: float) -> void:
	await get_tree().create_timer(3.0).timeout
	mark_for_deletion()
	
func set_position_from_server(pos: Vector2) -> void:
	position = pos



func mark_for_deletion() -> void:
	queue_free()
