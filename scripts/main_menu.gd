extends Panel


func _on_start_button_pressed() -> void:
	get_tree().get_root().print_tree()
	
	$"../MainMenu".hide()
	$"../SearchPanel".show()
	
	# Bekleme simülasyonu
	await get_tree().create_timer(7.0).timeout
	
	$"../SearchPanel".hide()
	$"../Game".show()


func _on_exit_button_pressed() -> void:
	get_tree().quit()
	
