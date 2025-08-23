


class GameServer: 
    """
        GameServer class manages all networking and high-level game logic.
        It handles incoming connections, assigns players to game rooms,
        processes messages, and coordinates broadcasts.
    """
    def __init__(self, host = "localhost", port = 8765, max_rooms = 10):
        """
        Initializes the GameServer.
        
        Args:
            host (str): The IP or hostname to bind the server to.
            port (int): The port number for incoming WebSocket connections.
            max_rooms (int): Maximum number of active rooms allowed.
        
        Attributes:
            clients (set): Stores connected client websockets.
            rooms (list): List of active GameRoom instances.
            host (str): Server IP/hostname.
            port (int): Server port.
            server (WebSocketServer): Reference to the running WebSocket server.
        """
        self.host = host
        self.port = port
        self.rooms = []
        self.clients = {}
        self.max_rooms = max_rooms
        self.server = None
        
    async def start_server(self):
        """
        Starts the WebSocket server and listens for incoming connections.
        
        This method should:
            - Initialize the WebSocket server.
            - Register `handle_client` as the connection handler.
            - Begin listening for clients.
        """
        pass

    async def handle_client(self, websocket, path):
        """
        Handles a new client connection.
        
        Args:
            websocket: WebSocket object for the connected client.
            path (str): URL path for WebSocket connection.
        
        Should:
            - Add the client to the `clients` set.
            - Wait for messages from the client.
            - Parse messages and call relevant handlers.
            - Remove client on disconnect.
        """
        pass

    def create_room(self, max_players=4):
        """
        Creates a new GameRoom if capacity allows.
        
        Args:
            max_players (int): Max players allowed in the room.
            
        Returns:
            GameRoom: The newly created room instance, or None if max room limit reached.
        """
        pass
    
    def list_rooms(self):
        """
        Get a list of all available rooms and their statuses.
        
        Returns:
            list: A list of dictionaries containing room details (ID, players, max players).
        
        Use Case:
            Display available rooms in a game lobby UI.
        """
        pass
    
    def get_room(self, room_id: int):
        """
        Retrieve a GameRoom by its ID.
        
        Args:
            room_id (int): The ID of the room.
        
        Returns:
            GameRoom instance or None if not found.
        
        Use Case:
            When players want to join or interact with a specific room.
        """
        pass

    def assign_player_to_room(self, websocket, player_info):
        """
        Assigns a player to an available room or creates a new one.
        
        Args:
            websocket: Player's WebSocket connection.
            player_info (dict): Contains player ID, username, etc.
        
        Should:
            - Check for an available non-full room.
            - If no available room, create a new one.
            - Add the player to the room.
        """
        pass
    
    def remove_player_from_room(self, websocket):
        """
        Removes a player from its current room.
        
        Args:
            websocket: Player's WebSocket.
        
        Should:
            - Find which room the player is in.
            - Remove them from that room.
            - If room is empty after removal, consider deleting the room.
        """
        pass

        
    async def broadcast_to_all(self, message):
        """
        Broadcasts a message to all connected clients.
        
        Args:
            message (str/dict): Data to send to all players.
        """
        pass
    
    async def broadcast_to_room(self, room_id, message):
        """
        Sends a message to all players in a specific room.
        
        Args:
            room_id (int): ID of the room to broadcast to.
            message (str/dict): The data to send.
        """
        pass
    

    
    
    async def game_loop(self):
        """
        Main server loop that updates rooms and handles periodic events.
        
        Should:
            - Iterate over rooms and call their `tick` methods.
            - Handle server-wide events like cleanup.
        """
        pass

    def log_event(self, event_type, details):
        """
        Logs server events for debugging/monitoring.
        
        Args:
            event_type (str): Type of event (e.g., "connection", "error", "message").
            details (dict/str): Additional information about the event.
        """
        pass
    
    def find_room_by_player(self, websocket):
        """
        Finds the room in which a player is currently located.
        
        Args:
            websocket: Player's WebSocket.
        
        Returns:
            GameRoom or None: The room the player belongs to.
        """
        pass
    
    
    async def shutdown(self):
        """
        Gracefully shuts down the server.
        
        Should:
            - Close all WebSocket connections.
            - Stop the game loop.
            - Perform any necessary cleanup.
        """
        pass
