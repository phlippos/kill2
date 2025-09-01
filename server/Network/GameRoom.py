from Game.game import Game
import json
import asyncio




class GameRoom:
    room_counter = 0
    def __init__(self,max_player = 4):
        self.room_id = GameRoom.room_counter
        self.players = list()
        self.max_player = max_player
        self.game = Game()
        GameRoom.room_counter += 1 
        self.status = "waiting"
        
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
            return True
        return False
    
    def remove_player(self, ws):
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
        pass
    
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
        if len(self.players) >= 1:
            self.status = "in_progress"
        
        await self.broadcast({
            "type": "join",
            "data": {
                "room_id": self.room_id,
                "players": self.get_player_list(),
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
        pass
    
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
    
    def tick(self):
        """
        Parameters: None.

        Purpose: Represents the server’s game loop tick.
        
        What it should do:
            Update game state (self.game.update_game_state()).
            Perform hit detection, score updates.
            Call broadcast_game_state() to sync with clients.

        Usage:
            Called periodically (e.g., 60 times per second) by the server.
        """
        pass
    
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