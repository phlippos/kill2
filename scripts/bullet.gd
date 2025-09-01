extends Area2D


@export var speed: float = 500
var direction: Vector2 = Vector2.ZERO


func _ready():
	await get_tree().create_timer(2.0).timeout
	queue_free()
	
func _physics_process(delta: float) -> void:
	position += direction * speed * delta
	
func _on_body_entered(body: Node2D) -> void:
	queue_free()
