import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK
from Utils.logger import Logger
from Utils.protocol import Protocol, MessageType
import json
from GameRoom import GameRoom

class GameServer: 
    """
        GameServer class manages all networking and high-level game logic.
        It handles incoming connections, assigns players to game rooms,
        processes messages, and coordinates broadcasts.
    """
    player_counter = 0
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
        self.rooms = {}
        self.clients = {}
        self.max_rooms = max_rooms
        self.server = None
        self.protocol = Protocol()
        
    async def start_server(self):
        """
        Starts the WebSocket server and listens for incoming connections.
        
        This method should:
            - Initialize the WebSocket server.
            - Register `handle_client` as the connection handler.
            - Begin listening for clients.
        """
        print("server başlatılıyor")
        async with serve(self.handle_client, self.host, self.port) as server:
            print("server başlatıldı")
            await asyncio.Future()
           
    async def handle_client(self, websocket):
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
        Logger.send_log("client_info",f"Client connected : {websocket.remote_address}")
        self.clients[GameServer.player_counter] = {"websocket": websocket}
        message = self.protocol.serialize_connect(GameServer.player_counter)
        GameServer.player_counter += 1
        await websocket.send(message)
        try: 
            async for message in websocket:
                Logger.send_log("client_info",f"Received message from client : {message}")
                decoded_message = self.protocol.decode_message(message)
                await self.process_client_message(websocket,decoded_message)
        except ConnectionClosedOK:
            Logger.send_log("client_info", f"Client disconnected")
        finally:
            for client in self.clients.keys():
                if self.clients[client]["websocket"] == websocket:
                    self.clients.pop(client)
                    self.remove_player_from_room(websocket)
                    
    async def process_client_message(self,websocket,message):
        print("1")
        try:
            message_type = message["type"]
            if message_type == MessageType.JOIN.value:
                await self.handle_client_join(websocket,message)
        except Exception as e:
            print("Message connection {e}")
                   
    async def handle_client_join(self,websocket,message):
        print("2")
        try:
            player_data = message.get("data")

            room = self.assign_player_to_room(websocket, player_data)

            if room:  
                waiting_message = {
                    "type": "join",
                    "data": {
                        "room_id": room.room_id,
                        "players_in_room": len(room.players),
                        "status": room.status
                    }
                }
                await websocket.send(json.dumps(waiting_message))

                if room.is_room_full():
                    print(f"Room is full {room.room_id}")
                    await room.start_game()

        except Exception as e:
            print(f"player join : {e}")      
        
    def create_room(self, max_players=4):
        """
        Creates a new GameRoom if capacity allows.
        
        Args:
            max_players (int): Max players allowed in the room.
            
        Returns:
            GameRoom: The newly created room instance, or None if max room limit reached.
        """
        gameroom = GameRoom(max_players)
        self.rooms[gameroom.room_id] = gameroom
        return gameroom
    
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
        for room in self.rooms.values():
            if not room.is_room_full():
                room.add_player(websocket, player_info)
                return room

        # No available room -> create new
        new_room = self.create_room(1)
        self.rooms[new_room.room_id] = new_room
        new_room.add_player(websocket, player_info)
        print(f"Yeni room oluşturuldu: {new_room.room_id}")
        return new_room
            
    
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
        for room in self.rooms.values():
            room.remove_player(websocket)
            if len(room.players) == 0:
                del room
        
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


async def main():
    gameserver = GameServer()
    await gameserver.start_server()
    
if __name__ =="__main__":
    asyncio.run(main())
    