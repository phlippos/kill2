import sys, os
sys.path.append(os.path.dirname(__file__))

from enum import Enum
import time
import json
from validation import Validation

class MessageType(Enum):
    MOVE = "move"
    SHOOT = "shoot"
    GAME_STATE = "game_state"
    HIT = "hit"
    RESPAWN = "respawn"
    SCORE = "score"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GAME_START = "game_start"
    GAME_END = "game_end"
    CHAT = "chat"
    WELCOME = "welcome"
    WAITING = "waiting"
    JOIN = "join"
    MAP = "map_data"
    REMAINING_TIME = "remaining_time"
    

class Protocol:
    """
    Handles encoding, decoding, validation, and type-specific message handling
    between clients and server.
    """

    def __init__(self):
        # Example: could hold protocol version or other configurations
        self.version = "1.0"

    # ------------------------------
    # General-purpose methods
    # ------------------------------

    def decode_message(self, raw_message):
        """
        Deserialize raw incoming data into a Python dict.

        Args:
            raw_message (bytes/str): Raw network data.

        Returns:
            dict: Decoded message { "type": "MOVE", "data": {...} }
        """
        try:
            message = json.loads(raw_message)
            
            if not isinstance(message,dict):
                raise ValueError("Message must be dict")
            if "type" not in message:
                raise ValueError("Message must include type")
            if "data" not in message:
                raise ValueError("Message must include data")
            
            message_type = message.get("type")
            if not any(message_type == msg_type.value for msg_type in MessageType):
                raise ValueError("Message type is invalid")
            
            return message
        
        except json.JSONDecodeError as e:
            print(f"JSON parse hatası: {e}")
            return None
        except ValueError as e:
            print(f"Mesaj format hatası: {e}")
            return None
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")
            return None

    def create_error_response(self, error_type, details=""):
        """
        Create a standardized error message.

        Args:
            error_type (str): Type of error.
            details (str): Optional details.

        Returns:
            dict: Error message structure.
        """
        pass

    # ------------------------------
    # Type-specific serialization/deserialization
    # ------------------------------
    def serialize_player(self,player):
        return {
                    "player_id" : player.id,
                    "username" : player.username,
                    "player_position" : player.position,
                    "player_direction" : player.direction,
                    "player_health" : player.health,
                    "player_is_alive" : player.is_alive,
                    "player_score" : player.score,
                    "player_velocity": [player.velocity_x, player.velocity_y],  
                    "is_on_ground": player.is_on_ground       
            }
    # MOVE message
    @staticmethod
    def serialize_move(self, x, y, direction, player):
        """
        Create a MOVE message structure.

        Args:
            x (float): New x-position.
            y (float): New y-position.
            direction (str): Direction (e.g., 'up', 'down', 'left', 'right').

        Returns:
            dict: { "type": "MOVE", "data": { "x": x, "y": y, "dir": direction },"player_id" : player.id}
        """
        message = {
            "type" : MessageType.MOVE.value,
            "timestamp" : time.time(),
            "x" : x,
            "y" : y,
            "direction" : direction,
            "player_id" : player.id
        }
        return message
    
    def deserialize_move(self, message):
        """
        Parse MOVE message data.

        Args:
            data (dict): The 'data' field from MOVE message.

        Returns:
            tuple: (x, y, direction,player_id)
        """
        if message and message.get("type") == MessageType.MOVE.value:
            data = message.get("data",{})
            return (
                data.get("x"),
                data.get("y"),
                data.get("direction"),
                data.get("player_id")
                )
        return None
    # SHOOT message
    def serialize_shoot(self, bullet):
        """
        Create a SHOOT message structure.

        Args:
            target_id (str/int): ID of the target.
            weapon_type (str): Weapon type (e.g., 'laser', 'bullet').

        Returns:
            dict: { "type": "SHOOT", "data": { "target_id": ..., "weapon": ... } }
        """
        return {
            "id": bullet.id,
            "owner": bullet.owner_id,
            "pos": bullet.pos,
            "dir": bullet.dir,
            "alive": bullet.alive
        }

    def deserialize_shoot(self, message):
        """
        Parse SHOOT message data.

        Args:
            message (dict): The 'data' field from SHOOT message.

        Returns:
            tuple: (muzzle_dir_x,muzzle_dir_y, muzzle_pos_x, muzzle_pos_y)
        """
        if message and message.get("type") == MessageType.SHOOT.value:
            data = message.get("data")
            return (
                data.get("direction"),
                data.get("position")
            )

    # CHAT message
    def serialize_chat(self, sender_id, text):
        """
        Create a CHAT message structure.

        Args:
            sender_id (str): ID of the sender.
            text (str): Chat text.

        Returns:
            dict: { "type": "CHAT", "data": { "sender": sender_id, "text": text } }
        """
        pass

    def deserialize_chat(self, data):
        """
        Parse CHAT message data.

        Args:
            data (dict): The 'data' field from CHAT message.

        Returns:
            tuple: (sender_id, text)
        """
        pass

    # JOIN message
    def serialize_join(self, player_id, username, game_room_id):
        """
        Create a JOIN message structure.

        Args:
            player_id (str): ID of the new player.
            username (str): Player's username.

        Returns:
            dict: { "type": "JOIN", "data": { "player_id": ..., "username": ... } }
        """
        return json.dumps(
            {
                "type": "join",
                "data":{
                    "player_id": player_id,
                    "username": username,
                    "game_room_id": game_room_id,
                }
            }
        )

    def deserialize_join(self, data):
        """
        Parse JOIN message data.

        Args:
            data (dict): The 'data' field from JOIN message.

        Returns:
            tuple: (player_id, username)
        """
        return (
            data.get("player_id"),
            data.get("username")
            )
    

    # LEAVE message
    def serialize_leave(self, player_id):
        """
        Create a LEAVE message structure.

        Args:
            player_id (str): ID of the leaving player.

        Returns:
            dict: { "type": "LEAVE", "data": { "player_id": ... } }
        """
        return {
            "type":"leave",
            "data": {
                "player_id": player_id
            }
        }

    def deserialize_leave(self, data):
        """
        Parse LEAVE message data.

        Args:
            data (dict): The 'data' field from LEAVE message.

        Returns:
            str: player_id
        """
        pass

    def serialize_connect(self, player_id):
        """_summary_

        Args:
            player_id (int): 
        Returns:
            dict: {"type": "CONNECT", "data": {"player_id": ...}}
        """
        return json.dumps({"type":"connect",
                "data": {
                    "player_id" : player_id,
                    "status" : "CONNECTED"
                    }
                })

    
    def serialize_game_state(self,game_state):
        return json.dumps(
            {
                "type": MessageType.GAME_STATE.value,
                "data": game_state
            }
        )
    
    def deserialize_map_data(self, message):
        try:
            data = message.get("data", {})
            
            # Platform verilerini validate et
            platforms = data.get("platforms", [])
            validated_platforms = []
            
            for platform in platforms:
                validated_platform = Validation.validate_platform_data(platform)
                if validated_platform:
                    validated_platforms.append(validated_platform)
            
            # Tile size bilgisini parse et
            tile_size = data.get("tile_size", {})
            if isinstance(tile_size, dict):
                tile_width = tile_size.get("x", 32)
                tile_height = tile_size.get("y", 32)
            else:
                tile_width = tile_height = 32
            
            return {
                "type": "map_data",
                "platforms": validated_platforms,
                "map_name": data.get("map_name", "unknown_map"),
                "tile_size": {
                    "width": tile_width,
                    "height": tile_height
                },
                "platform_count": len(validated_platforms),
                "timestamp": data.get("timestamp", time.time())
            }
            
        except Exception as e:
            print(f"Map data deserialization error: {e}")
            return None
    
    def serialize_game_state(self,players_data,bullets_data):
        return {
            "players" : players_data,
            "bullets" : bullets_data
        }
    
    def serialize_remaining_time(self, game):
         
            remaining_time = game.get_remaining_time()
            return {
                "type": MessageType.REMAINING_TIME.value,
                "data": {
                    "timestamp" : time.time(),
                    "remaining_time": remaining_time
                }
            }
          

    def deserialize_remaining_time(self, message):
       
        if not message:
            return None
        return message.get("remaining_time")

    
    