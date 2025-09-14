import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Game.game import Game
import json
import asyncio
from Utils.protocol import Protocol
import time
from enum import Enum

class GameRoomState(Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class GameRoom:
    room_counter = 0
    def __init__(self,max_player = 4):
        self.room_id = GameRoom.room_counter
        self.players = list()
        self.max_player = max_player
        self.game = Game()
        GameRoom.room_counter += 1 
        self.status = GameRoomState.WAITING.value
        self.protocol = Protocol()
        self.map_loaded = False
        self.platforms = None
        self.minimum_player_num = 2
        
    def min_player_reached(self):
        return len(self.players) >= self.minimum_player_num
    
    def is_room_full(self):
        """
            Purpose: Checks if the room has reached its maximum capacity.
            What it should do: Compare len(self.players) with self.max_player.
            Usage:
                Before calling add_player() to ensure the room is not full.
                To display the lobby room status.
        """
        return len(self.players) == self.max_player 
        
    def add_player(self, ws, player_info):
        """
        Parameters:
            ws: WebSocket object of the connecting player.
            player_info: A dictionary containing player info (id, username, etc.).

        Purpose: Adds a new player to the room’s self.players list.
        
        What it should do:
            Check room capacity.
            Append the player with their ID, websocket, and info.
            Return a success/failure status.

        Usage:
            Called when a new client connects to the server.
            During lobby joining.
        """
        
        if ws and player_info and not self.is_room_full():
            self.players.append(
                {
                    "id" : player_info["player_id"],
                    "websocket" : ws,
                    "player_info" : player_info
                }
            )
            self.game.add_player(player_info["player_id"],player_info["username"],ws)
            return True
        return False
    
    async def remove_player(self, ws):
        """
        Parameters:
            ws: WebSocket of the player leaving or disconnecting.
            
        Purpose: Removes the player from the room.
        
        What it should do:
            Find and remove the player with the matching websocket.
            Return status and optionally a message.
            
        Usage:
            When a player disconnects or voluntarily leaves the game.
        """
        if ws:
            for player in self.players:
                if player["websocket"] == ws:
                    self.players.remove(player)
                    self.game.remove_player(player["id"])
                    message = self.protocol.serialize_leave(player["id"])
                    await self.broadcast(message)
                    return True
        return False
    
    async def broadcast(self, message, exclude_ws = None):
        """
        Parameters:
            message: The data/message to broadcast (string/JSON).

            exclude_ws (optional): If provided, exclude that websocket from receiving the message.

        Purpose: Sends a message to all players in the room.

        What it should do:
            Iterate over self.players and send the message to each websocket (except excluded).

        Usage:
            To broadcast game updates, chat, or notifications to all players.
        """
        if not self.players:
            return

        data = json.dumps(message)

        websockets_to_send = [
            player["websocket"]
            for player in self.players
            if player["websocket"] != exclude_ws
        ]

        if websockets_to_send:
            await asyncio.gather(
                *(ws.send(data) for ws in websockets_to_send),
                return_exceptions=True
            )
    
    
    async def broadcast_game_state(self, game_state):
        """
        Parameters:
            game_state: The current game state data (positions, scores, etc.).

        Purpose: Sends the entire game state to all connected players.

        What it should do:
            Serialize and broadcast the latest game state each tick.

        Usage:
            Called inside the game loop to synchronize clients with the server state.
        """
        await self.broadcast(
            {
                "type": "game_state",
                "data": game_state
            }
        )
    
    async def broadcast_winner_info(self):
        """
        Parameters: None.

        Purpose: Broadcasts the winner information to all players when the game ends.

        What it should do:
            Send winner information including winner name, score, and result type.

        Usage:
            Called when the game ends to notify all players about the final result.
        """
        await self.broadcast(
            {
                "type": "game_end",
                "data": self.game.winner_info
            }
        )
        # Change room status to finished
        self.status = GameRoomState.FINISHED.value
        print(f"[GameRoom] Winner info broadcasted: {self.game.winner_info}")
            
    
    def find_player_by_id(self, player_id):
        """
        Parameters:
            player_id: ID of the player to search for.

        Purpose: Finds and returns a player’s info from self.players.

        Usage:
            When sending a private message.
            When checking if a player exists in this room.
        """
        pass
    
    
    def get_player_list(self):
        """
        Parameters: None.

        Purpose: Returns a list of all players in the room.

        What it should do:
            Return IDs, usernames, or relevant public info.

        Usage:
            When showing the lobby or sending player list updates to clients.
            For debugging.
        """
        players = []
        for player in self.players:
            players.append(player["player_info"]["username"])
        return players
    
    async def start_game(self):
        """
        Parameters: None.
        
        Purpose: Starts the match/game in this room.

        What it should do:
            Change self.status to "in_progress".
            Initialize game state, positions, and possibly start timers.
        
        Usage:
            When the required number of players join.
            When an admin/host triggers the game start.
        """   
        self.game.assign_starting_positions()
        self.status = "in_progress"
        self.game.status = 2
        self.game.start_time = time.time()
        await self.broadcast({
            "type": "game_start",
            "data": {
                "room_id": self.room_id,
                "game_state": self.game.get_game_state(),
                "status": self.status,
            }
        })
        
        

    def end_game(self):
        """
        Parameters: None.

        Purpose: Ends the game.

        What it should do:
            Change self.status to "finished".
            Send final scores to all players.
            Stop the game loop.

        Usage:
            When the match ends due to score/time.
            Triggered by server logic.
        """

        self.players.clear()
        print("jdfkgred")
    
    def reset_room(self):
        """
        Parameters: None.

        Purpose: Resets the room for a new game.

        What it should do:
            Clear game state and scores.
            Keep players in the room but reset status to waiting.

        Usage:
            Between rounds if the same players want to play again.
        """
        pass
    
    async def tick(self,delta_time):
        """
        Parameters: None.

        Purpose: Represents the server's game loop tick.
        
        What it should do:
            Update game state (self.game.update_game_state()).
            Perform hit detection, score updates.
            Call broadcast_game_state() to sync with clients.

        Usage:
            Called periodically (e.g., 60 times per second) by the server.
        """



        if self.status == GameRoomState.IN_PROGRESS.value:
            if self.game.game_ended and self.game.winner_info and not self.game.winner_broadcasted:
                await self.broadcast_winner_info()
                self.game.winner_broadcasted = True
                self.status = GameRoomState.FINISHED.value
                self.end_game()
                return

            self.game.tick(delta_time)
            game_state = self.game.get_game_state()
            #perform hit detection
            #update health
            #update score
            await self.broadcast_game_state(game_state)
            await self.broadcast(self.game.broadcast_remaining_time())
            

    
    def send_private_message(self, player_id, message):
        """
        Parameters:
            player_id: The recipient player’s ID.
            message: The content to send.

        Purpose: Sends a private message to one specific player.

        Usage:
            For individual notifications (errors, private chat, personal updates).
        """
        pass
    def broadcast_except(self, exclude_id, message):
        """
        Parameters:
            exclude_id: The player ID to exclude.
            message: The message to broadcast.

        Purpose: Sends a message to all players except one.

        Usage:
            To notify all players about an action except the initiator (e.g., shooting, movement).
        """
        pass
    
    def log_event(self,evet_type,details):
        """
        Parameters:
            event_type: Type of event ("join", "kill", "disconnect", etc.).
            details: Additional info about the event.

        Purpose: Records significant events in the room.

        Usage:
            For debugging, analytics, or a replay system.
            Helps audit game activities.
        """
        pass
    
    def apply_player_move(self, move_data):
        x, y, direction, player_id = move_data
        #print("direction:", direction)

        self.game.update_player_position(int(player_id), direction)
        
    def apply_player_shoot(self, player_id,shoot_data):
        direction,position = shoot_data
        self.game.fire_bullet(player_id, position,direction)
    
    def apply_player_respawn(self,player_id):
        print("apply_player_respawn")
        self.game.respawn_player(player_id)
        
    def load_map_data(self, platforms, map_metadata=None):
        """
        Platform verilerini yükler - duplicate kontrolü ile
        """
        # Eğer zaten map yüklüyse, duplicate kontrolü yap
        if self.map_loaded and self.platforms:
            if self.is_same_map_data(platforms):
                #print(f"Room {self.room_id}: Aynı map data zaten yüklü, atlanıyor")
                return False  # Duplicate, yükleme
        print(platforms)
        # Yeni map data'sını yükle
        self.platforms = platforms
        self.map_loaded = True
        self.map_metadata = map_metadata or {}
        self.game.platforms = self.platforms
        print(f"Room {self.room_id}: {len(platforms)} platform yüklendi")
        
        # Platform verilerini optimize et
        self.optimize_platforms()
        return True
    
    def is_same_map_data(self, new_platforms):
        """
        Yeni gelen platform data'sının aynı olup olmadığını kontrol eder
        """
        # Platform sayısı farklı ise kesinlikle farklı
        if len(new_platforms) != len(self.platforms):
            return False
        
        # Platform sayısı aynı ise ilk 3 platformun koordinatlarını karşılaştır
        check_count = min(3, len(new_platforms))
        
        for i in range(check_count):
            old_p = self.platforms[i]
            new_p = new_platforms[i]
            
            # Koordinat farkı 1 pikselden fazla ise farklı map
            if (abs(old_p.get("x", 0) - new_p.get("x", 0)) > 1 or
                abs(old_p.get("y", 0) - new_p.get("y", 0)) > 1 or
                abs(old_p.get("width", 0) - new_p.get("width", 0)) > 1 or
                abs(old_p.get("height", 0) - new_p.get("height", 0)) > 1):
                return False
        
        # İlk 3 platform aynı ise muhtemelen aynı map
        #print(f"Room {self.room_id}: Map data duplicate detected")
        return True
    
    def optimize_platforms(self):
        """
        Platform verilerini optimize eder
        """
        original_count = len(self.platforms)
        
        # Çok küçük platformları filtrele
        min_size = 8
        self.platforms = [
            p for p in self.platforms 
            if p.get("width", 0) >= min_size and p.get("height", 0) >= min_size
        ]
        
        # Platformları Y koordinatına göre sırala (collision detection için)
        self.platforms.sort(key=lambda p: p.get("y", 0))
        
        # Duplicate platformları temizle
        unique_platforms = []
        for platform in self.platforms:
            is_duplicate = False
            for existing in unique_platforms:
                if (abs(existing["x"] - platform["x"]) < 1 and
                    abs(existing["y"] - platform["y"]) < 1 and
                    abs(existing["width"] - platform["width"]) < 1 and
                    abs(existing["height"] - platform["height"]) < 1):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_platforms.append(platform)
        
        self.platforms = unique_platforms
        
        #print(f"Platform optimization: {original_count} -> {len(self.platforms)} platforms")

def main():
    gameroom = GameRoom()
    gameroom.add_player("ws",{"player_id": 0,"username":"a"})
    gameroom.add_player("ws",{"player_id": 0,"username":"a"})
    gameroom.add_player("ws",{"player_id": 0,"username":"a"})
    gameroom.add_player("ws",{"player_id": 0,"username":"a"})
    gameroom.add_player("ws",{"player_id": 0,"username":"a"})
    gameroom.add_player("ws",{"player_id": 0,"username":"a"})
    gameroom.add_player("ws",{"player_id": 0,"username":"a"})
    
if __name__ =="__main__":
    main()