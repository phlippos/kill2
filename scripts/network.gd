extends Node

@export var websocket_url = "ws://localhost:8765"
var websocket:= WebSocketPeer.new()
var sent = false
var player_id
var player_status
var game_room_id: int
signal message_received(message: Dictionary)

func _ready():
	if !establish_connection_with_server():
		set_process(false)
		print("connection failed")
		
func _process(delta: float) -> void:
	websocket.poll()
	match websocket.get_ready_state():
		WebSocketPeer.STATE_OPEN:
			if not sent:
				await send_first_message_to_server()
			while websocket.get_available_packet_count() > 0:
				var packet = websocket.get_packet().get_string_from_utf8()
				var raw_data = JSON.parse_string(packet)
				if raw_data != null:
					if player_id == null and player_status == null:
						if raw_data["data"].has("player_id"):
							player_id = int(raw_data["data"]["player_id"])
						if raw_data["data"].has("status"):
							player_status = raw_data["data"]["status"]
					emit_signal("message_received",raw_data)
				#print("Received: ", packet)
		WebSocketPeer.STATE_CLOSED:
			print("connection closed")
			set_process(false)

func establish_connection_with_server() -> bool:
	var err = websocket.connect_to_url(websocket_url)
	if err != OK:
		return false
	else:
		return true
		
func send_first_message_to_server() -> void:
	match websocket.get_ready_state():
		WebSocketPeer.STATE_OPEN:
			websocket.send_text("hi barbie :))")
			sent = true
			while websocket.get_available_packet_count() > 0:
				var packet = websocket.get_packet().get_string_from_utf8()
				var raw_data = JSON.parse_string(packet)
				player_id = int(raw_data["data"]["player_id"])
				player_status = raw_data["data"]["status"]
				#print("Received: ", packet)
		WebSocketPeer.STATE_CLOSED:
			print("connection closed")
			set_process(false)
			
func send_join_request(username: String) -> void:
	if websocket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		var data = {
			"type" : "join",
			"data" : {
				"player_id": player_id,
				"username" : username
			}
		}
		websocket.send_text(JSON.stringify(data))


func send_movement_data(pos_x: float, pos_y: float, direction_x: float, direction_y: float):
	#print("Sending movement: ", pos_x, pos_y, direction_x, direction_y)  
	if websocket.get_ready_state() == WebSocketPeer.STATE_OPEN and player_id != null:
		var data = {
			"type": "move",
			"data": {
				"x": pos_x,
				"y": pos_y,
				"direction": [direction_x, direction_y],
				"player_id": player_id
			}
		}
		websocket.send_text(JSON.stringify(data))
		
func send_map_data (map_data: Dictionary):
	if websocket.get_ready_state() != WebSocketPeer.STATE_OPEN:
		await get_tree().create_timer(3.0).timeout
	if websocket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		var json_string = JSON.stringify(map_data)
		websocket.send_text(json_string)
		print("Map data gönderildi: ", map_data.data.platforms.size(), " platform")
	else:
		print("WebSocket bağlantısı yok!")
		
func send_fire_request(dir_x: float, dir_y: float, muzzle_pos_x: float, muzzle_pos_y: float)-> void:
	if websocket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		var data = {
			"type": "shoot",
			"data": {
				"direction" : [dir_x,dir_y],
				"position" : [muzzle_pos_x,muzzle_pos_y]
			}
		}
		var json_string = JSON.stringify(data)
		websocket.send_text(json_string)
		print("bullet data gönderildi")
	else:
		print("WebSocket bağlantısı yok!")


func send_respawn_request():
	if websocket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		var data = {
			"type" : "respawn",
			"data" : {
				"player_id": player_id
			}
		}
		websocket.send_text(JSON.stringify(data))
	else:
		print("WebSocket bağlantısı yok!")
