import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK,ConnectionClosedError
from Utils.logger import Logger, LogType
from Utils.protocol import Protocol, MessageType
import json
from GameRoom import GameRoom, GameRoomState
import time

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
        self.tick_rate = 30
        self.running = True
        self.last_time = time.time()
        self.map_platforms = [{'x': 8.0, 'y': 533.0, 'width': 1152.0, 'height': 16.0, 'tile_count': 72}, {'x': 8.0, 'y': 549.0, 'width': 1152.0, 'height': 16.0, 'tile_count': 72}, {'x': 8.0, 'y': 565.0, 'width': 1152.0, 'height': 16.0, 'tile_count': 72}, {'x': 8.0, 'y': 581.0, 'width': 1152.0, 'height': 16.0, 'tile_count': 72}, {'x': 8.0, 'y': 597.0, 'width': 1152.0, 'height': 16.0, 'tile_count': 72}, {'x': 8.0, 'y': 613.0, 'width': 1152.0, 'height': 16.0, 'tile_count': 72}, {'x': 8.0, 'y': 629.0, 'width': 1152.0, 'height': 16.0, 'tile_count': 72}, {'x': 8.0, 'y': 645.0, 'width': 1152.0, 'height': 16.0, 'tile_count': 72}, {'x': 376.0, 'y': 197.0, 'width': 384.0, 'height': 16.0, 'tile_count': 24}, {'x': 376.0, 'y': 213.0, 'width': 384.0, 'height': 16.0, 'tile_count': 24}, {'x': 376.0, 'y': 229.0, 'width': 384.0, 'height': 16.0, 'tile_count': 24}, {'x': 376.0, 'y': 245.0, 'width': 384.0, 'height': 16.0, 'tile_count': 24}, {'x': 376.0, 'y': 261.0, 'width': 384.0, 'height': 16.0, 'tile_count': 24}, {'x': 232.0, 'y': 341.0, 'width': 64.0, 'height': 16.0, 'tile_count': 4}, {'x': 232.0, 'y': 357.0, 'width': 64.0, 'height': 16.0, 'tile_count': 4}, {'x': 104.0, 'y': 405.0, 'width': 64.0, 'height': 16.0, 'tile_count': 4}, {'x': 104.0, 'y': 421.0, 'width': 64.0, 'height': 16.0, 'tile_count': 4}, {'x': 776.0, 'y': 341.0, 'width': 64.0, 'height': 16.0, 'tile_count': 4}, {'x': 776.0, 'y': 357.0, 'width': 64.0, 'height': 16.0, 'tile_count': 4}, {'x': 920.0, 'y': 421.0, 'width': 64.0, 'height': 16.0, 'tile_count': 4}, {'x': 920.0, 'y': 437.0, 'width': 64.0, 'height': 16.0, 'tile_count': 4}]

        self.max_player_for_game_room = 2
    async def start_server(self):
        """
        Starts the WebSocket server and listens for incoming connections.
        
        This method should:
            - Initialize the WebSocket server.
            - Register `handle_client` as the connection handler.
            - Begin listening for clients.
        """
        #print("server başlatılıyor")
        async with serve(self.handle_client, self.host, self.port) as server:
            #print("server başlatıldı")
            await asyncio.gather(self.game_loop())
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
        Logger.send_log(LogType.CLIENT_INFO,f"Client connected : {websocket.remote_address}")
        self.clients[GameServer.player_counter] = {"websocket": websocket}
        message = self.protocol.serialize_connect(GameServer.player_counter)
        GameServer.player_counter += 1
        await websocket.send(message)
        try: 
            async for message in websocket:
                #Logger.send_log(LogType.CLIENT_INFO ,f"Received message from client : {message}")
                decoded_message = self.protocol.decode_message(message)
                await self.process_client_message(websocket,decoded_message)
        except ConnectionClosedOK:
            Logger.send_log(LogType.CLIENT_INFO, f"Client disconnected")
        except ConnectionClosedError:
            Logger.send_log(LogType.CLIENT_INFO, f"Client disconnected")
        finally:
            for client in self.clients.keys():
                if self.clients[client]["websocket"] == websocket:
                    self.clients.pop(client)
                    await self.remove_player_from_room(websocket)
                    self.remove_empty_rooms()
                    break
                
    async def process_client_message(self,websocket,message):
        try:
            message_type = message["type"]
            if message_type == MessageType.JOIN.value:
                await self.handle_client_join(websocket,message)
            elif message_type == MessageType.MOVE.value:
                await self.handle_client_move(websocket, message)
            elif message_type == MessageType.MAP.value:
       #         await self.handle_map_data(websocket,message)
                pass
            elif message_type == MessageType.SHOOT.value:
                await self.handle_client_shoot(websocket,message)
            elif message_type == MessageType.RESPAWN.value:
                await self.handle_client_respawn(websocket,message)
                
        except Exception as e:
            print("Message connection {e}")
                   
    async def handle_client_join(self,websocket,message):
        try:
            player_data = message.get("data")
            if self.check_username(player_data["username"]) or self.is_already_player(websocket, player_data["username"], player_data["player_id"]):
                self.clients[message["data"]["player_id"]]["username"] = message["data"]["username"]
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
                    if room.min_player_reached() and room.status == GameRoomState.WAITING.value:
                        print(f"Room is full {room.room_id}")
                        await room.start_game()
            else:
                response = {
                    "type" : "error",
                    "data" : {
                        "message" : "username in used"
                    }
                }
                await websocket.send(json.dumps(response))

        except Exception as e:
            print(f"player join : {e}")      
    
    async def handle_client_move(self, websocket, message):
        try:
            #print(f"Raw move message received: {message}")
            
            move_data = self.protocol.deserialize_move(message)
            #print(f"Deserialized move data: {move_data}")
            
            if move_data:
                room = self.find_room_by_player(websocket)
                room.apply_player_move(move_data)      
            else:
                print("Move data is None - deserialization failed")
                
        except Exception as e:
            print(f"Move handling error: {e}")
            
    async def handle_client_shoot(self,websocket,message):
        try:
            print(message)
            shoot_data = self.protocol.deserialize_shoot(message)
            print(f"deserialized shoot data: {shoot_data}")
            
            if shoot_data:
                room = self.find_room_by_player(websocket)
                client_id = self.find_client_id(websocket)
                if room:
                    room.apply_player_shoot(client_id,shoot_data)
                else:
                    print("room cant find")
            else:
                print("shoot data is None")                 
        except Exception as e:
            print(f"Shoot handling error: {e}")
    
    async def handle_client_respawn(self,websocket,message):
        try:
            client_id = self.find_client_id(websocket)
            room = self.find_room_by_player(websocket)
            
            if room :
                room.apply_player_respawn(client_id)
        except Exception as e:
            print(f"respawn handling error {e}")
    
    
    async def handle_map_data(self, websocket, message):
        """
        Godot'dan gelen map/platform verilerini işler
        """
        try:
            # Protocol ile deserialize et
            map_data = self.protocol.deserialize_map_data(message)
            if not map_data:
                return
            
            self.map_platforms = map_data["platforms"]
            print(self.map_platforms)
                
        except Exception as e:
            Logger.send_log(LogType.ERROR, f"Map data handling error: {e}")
                
    def create_room(self, max_players=4):
        """
        Creates a new GameRoom if capacity allows.
        
        Args:
            max_players (int): Max players allowed in the room.
            
        Returns:
            GameRoom: The newly created room instance, or None if max room limit reached.
        """
        gameroom = GameRoom(max_players)
        if self.map_platforms:
            gameroom.load_map_data(self.map_platforms)
            gameroom.map_loaded = True
        self.rooms[gameroom.room_id] = gameroom
        return gameroom
    
    def remove_empty_rooms(self):
        empty_rooms = [room_id for room_id, room in self.rooms.items() if not room.players]
        for room_id in empty_rooms:
            del self.rooms[room_id]
            print(f"Room {room_id} deleted (no players left).")
            
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
        for room in list(self.rooms.values()):
            if not room.is_room_full():
                print("added")
                room.add_player(websocket, player_info)
                return room

        # No available room -> create new
        new_room = self.create_room(self.max_player_for_game_room)
        self.rooms[new_room.room_id] = new_room
        new_room.add_player(websocket, player_info)
        #print(f"Yeni room oluşturuldu: {new_room.room_id}")
        return new_room
            
    async def remove_player_from_room(self, websocket):
        """
        Removes a player from its current room.
        
        Args:
            websocket: Player's WebSocket.
        
        Should:
            - Find which room the player is in.
            - Remove them from that room.
            - If room is empty after removal, consider deleting the room.
        """
        for room in list(self.rooms.values()):
            await room.remove_player(websocket)
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
        while self.running: 
            start = time.time()
            delta = start - self.last_time
            for room in list(self.rooms.values()):
                await room.tick(1/self.tick_rate)
            self.last_time = start
            
            await asyncio.sleep(max(0, 1/self.tick_rate - (time.time() - start)))
            self.remove_empty_rooms()

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
        for room in list(self.rooms.values()):
            for player in room.players:
                if player["websocket"] == websocket:
                    return room
        return None
    def find_client_id(self, websocket):
        for client in self.clients.keys():
            if self.clients[client]["websocket"] == websocket:
                return client
        return None
            
    async def shutdown(self):
        """
        Gracefully shuts down the server.
        
        Should:
            - Close all WebSocket connections.
            - Stop the game loop.
            - Perform any necessary cleanup.
        """
        pass
    
    def check_username(self,username):
        for client in self.clients.values():
            if client.get("username","")== username :
                return False
        return True
    
    def is_already_player(self, websocket, username, player_id):
        print("username" in self.clients[player_id])
        if "username" in self.clients[player_id] and self.clients[player_id].get("username") == username:
            return True
        return False
    
async def main():
    gameserver = GameServer()
    await gameserver.start_server()
if __name__ =="__main__":
    asyncio.run(main())
    