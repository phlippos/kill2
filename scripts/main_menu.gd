extends Panel

@export var username : String = ""
var player_scene = preload("res://scenes/player.tscn")
var player_scene_instance
func _ready() -> void:
	player_scene_instance = player_scene.instantiate()
func _on_start_button_pressed() -> void:
	get_tree().get_root().print_tree()
	
	$"../MainMenu".hide()
	$"../SearchPanel".show()
	
	# Bekleme simülasyonu
	await get_tree().create_timer(1.0).timeout
	player_scene_instance.set_username($UsernameTextField.text)
	$"../SearchPanel".hide()
	$"../Game".show()


func _on_exit_button_pressed() -> void:
	get_tree().quit()
	
