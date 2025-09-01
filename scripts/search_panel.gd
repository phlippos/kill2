extends Panel


var dots = 0
var base_text = "Searching for Game"
var interval = 1.0  # seconds
var timer = 0.0

func _ready() -> void:
	hide()
	var tween = get_tree().create_tween()
	$SearchingGameLabel.text = base_text
	Network.connect("message_received",_on_network_message_received)
func _process(delta: float) -> void:
	timer += delta
	if timer >= interval:
		timer = 0
		dots += 1
		if dots > 3:
			dots = 0
		$SearchingGameLabel.text = base_text + ".".repeat(dots)
	

func _on_network_message_received(message: Dictionary) -> void:
	print("1")
	if message["type"] == "join":
		var data: Dictionary = message["data"]
		print(data)
		if data["status"] == "in_progress":
			Network.game_room_id = data["room_id"]
			$"../SearchPanel".hide()
			$"../Game".show()
