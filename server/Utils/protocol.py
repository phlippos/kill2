from enum import Enum
import time
import json

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
    def serialize_shoot(self, target_id, weapon_type):
        """
        Create a SHOOT message structure.

        Args:
            target_id (str/int): ID of the target.
            weapon_type (str): Weapon type (e.g., 'laser', 'bullet').

        Returns:
            dict: { "type": "SHOOT", "data": { "target_id": ..., "weapon": ... } }
        """
        pass

    def deserialize_shoot(self, data):
        """
        Parse SHOOT message data.

        Args:
            data (dict): The 'data' field from SHOOT message.

        Returns:
            tuple: (target_id, weapon_type)
        """
        pass

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
        pass

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
