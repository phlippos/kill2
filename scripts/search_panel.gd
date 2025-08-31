extends Panel


var dots = 0
var base_text = "Searching for Game"
var interval = 1.0  # seconds
var timer = 0.0

func _ready() -> void:
	hide()
	var tween = get_tree().create_tween()
	$SearchingGameLabel.text = base_text
	
func _process(delta: float) -> void:
	timer += delta
	if timer >= interval:
		timer = 0
		dots += 1
		if dots > 3:
			dots = 0
		$SearchingGameLabel.text = base_text + ".".repeat(dots)
	
