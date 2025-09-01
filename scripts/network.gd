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
				send_first_message_to_server()
			while websocket.get_available_packet_count() > 0:
				var packet = websocket.get_packet().get_string_from_utf8()
				var raw_data = JSON.parse_string(packet)
				print(raw_data)
				emit_signal("message_received",raw_data)
				if raw_data != null:
					if raw_data["data"].has("player_id"):
						player_id = raw_data["data"]["player_id"]
					if raw_data["data"].has("status"):
						player_status = raw_data["data"]["status"]
					
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
				player_id = raw_data["data"]["player_id"]
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
