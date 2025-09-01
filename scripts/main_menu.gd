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
	var username = $UsernameTextField.text
	if check_username(username):
		Network.send_join_request($UsernameTextField.text)
		# Bekleme simülasyonu
		player_scene_instance.set_username($UsernameTextField.text)
	else:
		$UsernameTextField.text = "Name length is invalid min 3 character"

func _on_exit_button_pressed() -> void:
	get_tree().quit()
	
func check_username(username: String) -> bool:
	if username.length() >= 3:
		return true
	return false
	
