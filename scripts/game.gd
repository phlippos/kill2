extends Node2D

@onready var score_list: ItemList = $UI/ScoreBoard/ItemList 
var player_id_to_index: Dictionary = {}
var players: Dictionary = {} #player_id : OtherPlayer instance
var local_player
var other_player_scene = preload("res://scenes/other_player.tscn")
var player_scene = preload("res://scenes/player.tscn")
var bullet_scene = preload("res://scenes/bullet.tscn")
var game_room_id: int 
var status: String
var bullets: Dictionary = {}
signal kill()

func _ready() -> void:
	Network.connect("message_received", _on_network_message_received)

func _on_network_message_received(message: Dictionary) -> void:
	if message["type"] == "game_start":
		load_game_state_to_start(message)
	elif message["type"] == "game_state":
		update_game_state(message)
	elif message["type"] == "game_end":
		game_end(message)
	elif message["type"] == "remaining_time":
		get_remaining_time(message)
	elif message["type"] == "leave":
		remove_player_from_list(message)

func load_game_state_to_start(message: Dictionary) -> void:
	var data = message["data"]
	game_room_id = data["room_id"]
	status = data["status"]
	var players_info = data["game_state"]["players"]

	for player in players_info:
		var player_id = int(player["player_id"])
		if player_id == Network.player_id:
			add_player(player, player_scene)
			local_player = players[player_id]
		else:
			add_player(player, other_player_scene)
	
	initialize_scoreboard()
	$"/root/Main/Game/UI/ScoreBoard".visible = true

func add_player(player: Dictionary, scene):
	var p = scene.instantiate()
	p.load_player(
		player["player_id"],
		player["username"],
		Vector2(player["player_position"][0], player["player_position"][1]),
		Vector2(player["player_direction"][0], player["player_direction"][1]),
		player["player_health"],
		player["player_is_alive"],
		player["player_score"]
	)
	add_child(p)
	players[p.player_id] = p

func update_game_state(game_state: Dictionary) -> void:
	var players_new_states = game_state["data"]["players"]
	var bullets_new_states = game_state["data"]["bullets"]
	
	for player_new_state in players_new_states:
		var player_id: int = player_new_state["player_id"]
		
		# Check if new player joined
		if player_id not in self.players.keys():
			if Network.player_id == player_id:
				add_player(player_new_state, player_scene)
				local_player = players[player_id]
			else:
				add_player(player_new_state, other_player_scene)
			
			# Add new player to scoreboard
			add_player_to_scoreboard(player_id)
		
		if player_id != Network.player_id:
			var player = players[player_id]
			player.update_position(Vector2(player_new_state["player_position"][0], player_new_state["player_position"][1]))
			player.update_critical_info(player_new_state["player_health"], player_new_state["player_is_alive"], player_new_state["player_score"])
			
			# Update scoreboard for other players
			update_player_score_display(player_id)
		else:
			update_players_from_server(player_new_state)
			update_critical_info_from_server(player_new_state)
	
	for bullet_new_state in bullets_new_states:
		update_bullet_from_server(bullet_new_state)

func update_players_from_server(game_data: Dictionary):
	var server_position = Vector2(
		game_data.player_position[0], 
		game_data.player_position[1]
	)
	
	if local_player:
		# Get additional server data
		var server_velocity = Vector2.ZERO
		var is_on_ground = game_data.get("is_on_ground", true)
		
		# Update player with server position
		local_player.update_from_server(server_position, server_velocity, is_on_ground)

func update_critical_info_from_server(player_new_state: Dictionary):
	var health = player_new_state.get("player_health")
	var is_alive = player_new_state.get("player_is_alive")
	var score = player_new_state.get("player_score")
	if local_player:
		local_player.update_critical_info(health, is_alive, score)
		if !local_player.is_alive:
			$"/root/Main/Game/GrayScreen".visible = true
		else:
			$"/root/Main/Game/GrayScreen".visible = false
		
		update_player_score_display(Network.player_id)

func update_bullet_from_server(bullet_state: Dictionary) -> void:
	var bullet_id = bullet_state["id"]
	var bullet
	if bullet_id not in bullets.keys():
		bullet = bullet_scene.instantiate()
		add_child(bullet)
	else:
		bullet = bullets[bullet_id]
	if bullet_state["alive"] == false:
		bullet.mark_for_deletion()
		bullets.erase(bullet_id)	
	print(bullet_state)
	bullet.set_position_from_server(
		Vector2(bullet_state["pos"]["x"], bullet_state["pos"]["y"])
	)
	bullets[bullet_id] = bullet

func remove_player_from_list(message: Dictionary):
	var data = message["data"]
	var player_id = int(data["player_id"])
	var player = self.players.get(player_id)
	if player:
		player.mark_for_deletion()
		self.players.erase(player_id)
		remove_player_from_scoreboard(player_id)

func initialize_scoreboard():
	score_list.clear()
	player_id_to_index.clear()
	
	var sorted_players = get_sorted_players()
	
	for i in range(sorted_players.size()):
		var player_data = sorted_players[i]
		var display_text = "%s - Score: %d" % [player_data.username, player_data.score]
		
		if not player_data.is_alive:
			display_text += " (Dead)"
		
		score_list.add_item(display_text)
		player_id_to_index[player_data.id] = i

func get_sorted_players() -> Array:
	var sorted_players = []
	for player_id in players.keys():
		var player = players[player_id]
		sorted_players.append({
			"id": player_id,
			"username": player.username,
			"score": player.score,
			"is_alive": player.is_alive
		})
	
	sorted_players.sort_custom(func(a, b): return a.score > b.score)
	return sorted_players

func add_player_to_scoreboard(player_id: int):
	if player_id in players:
		var player = players[player_id]
		var display_text = "%s - Score: %d" % [player.username, player.score]
		
		if not player.is_alive:
			display_text += " (Dead)"
		
		var index = score_list.get_item_count()
		score_list.add_item(display_text)
		player_id_to_index[player_id] = index

func update_player_score_display(player_id: int):
	if player_id in players and player_id in player_id_to_index:
		var player = players[player_id]
		var index = player_id_to_index[player_id]
		
		var display_text = "%s - Score: %d" % [player.username, player.score]
		
		if not player.is_alive:
			display_text += " (Dead)"
		
		score_list.set_item_text(index, display_text)

func remove_player_from_scoreboard(player_id: int):
	if player_id in player_id_to_index:
		var index = player_id_to_index[player_id]
		score_list.remove_item(index)
		
		player_id_to_index.erase(player_id)
		for pid in player_id_to_index.keys():
			if player_id_to_index[pid] > index:
				player_id_to_index[pid] -= 1
				
func game_end(message: Dictionary):
	var data = message.get("data")
	var result = data.get("result")
	if result == "tie":
		$"/root/Main/Game/UI/Tie".visible = true
	elif result == "win":
		var winner = data.get("winner")
		$"/root/Main/Game/UI/Win/Label".text = winner
		$"/root/Main/Game/UI/Win".visible = true
		
	await get_tree().create_timer(3.0).timeout
	
	reset_self()
	$"/root/Main/MainMenu".show()
		
	
func get_remaining_time(message: Dictionary):
	var data = message.get("data")
	var remaining_time = "%.2f" % data.get("remaining_time")
	
	$"/root/Main/Game/UI/Clock/ClockDigit".text = remaining_time
	$"/root/Main/Game/UI/Clock".visible = true
	print(data)
	
func reset_self():
	player_id_to_index.clear()
	players.clear()
	local_player = null
	game_room_id = -1
	status = ""
	bullets.clear()
	emit_signal("kill")
	
	$"/root/Main/Game/UI/Tie".hide()
	$"/root/Main/Game/UI/Win".hide()
	$"/root/Main/Game/UI".hide()
	$"/root/Main/Game".hide()
	$"/root/Main/Game/GrayScreen".hide()
	
	
	

				
