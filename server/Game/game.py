import sys, os
sys.path.append(os.path.dirname(__file__))

from enum import Enum
from player import Player

class Status(Enum):
    FINISHED = 1
    STARTED = 2
    WAITING = 3
    
class Game:
    """
    The Game class handles the core game logic:
    - Maintaining game state
    - Updating player and object positions
    - Detecting collisions (e.g., bullet vs enemy)
    - Managing scores and win conditions
    - Providing game data for broadcasting to clients
    """
    MAP_WIDTH = 1152
    MAP_HEIGHT = 648
    def __init__(self):
        """
        Initializes the game state.

        Attributes:
            players (dict): A mapping of player IDs to their game state 
                (position, health, score, team, etc.).
            bullets (list): Active bullets with positions, velocities, and owner IDs.
            enemies (list): Active enemies (if applicable) with positions and states.
            game_time (float): Tracks elapsed time since the start.
            status (str): Indicates current state (e.g., 'waiting', 'running', 'ended').
            map_data (object/dict): Stores map layout, boundaries, obstacles.
        """
        self.players = dict()
        self.status = Status.WAITING.value
        self.delta_time = 1/60
        
    def add_player(self, player_id, username ,initial_data, connection):
        """
        Adds a player to the game state.

        Parameters:
            player_id (str/int): Unique ID of the player.
            initial_data (dict): Contains initial position, health, team, etc.

        Usage:
            - Called when a player joins a room and game starts.
            - Initializes their score, health, and position.
        """
        
        player = Player(player_id,username, connection, initial_data.get("position"), initial_data.get("team"))
        self.players[player_id] = player
        
    def remove_player(self, player_id):
        """
        Removes a player from the game state.

        Parameters:
            player_id (str/int): ID of the player to remove.

        Usage:
            - Called when a player disconnects or leaves the game.
            - Removes their bullets and related state data.
        """
        if player_id in self.players.keys():
            self.players.pop(player_id)
            return True
        return False
            
    
    def update_player_position(self, player_id, direction):
        """
        Updates player position based on input.

        Parameters:
            player_id (str/int): The player whose position is being updated.
            direction (dict): Contains velocity vector or directional input.

        Usage:
            - Called on each tick/frame when the server processes player input.
        """
        player = self.players[player_id]
        dx, dy = direction
        new_x = player.position[0] + dx * player.speed * self.delta_time
        new_y = player.position[1] + dy * player.speed * self.delta_time
        new_x, new_y = self.clamp_position(new_x, new_y)
        player.position = (new_x, new_y)
    
    def fire_bullet(self, player_id, position, direction):
        """
        Spawns a bullet in the game world.

        Parameters:
            player_id (str/int): Owner of the bullet.
            position (tuple): Starting position (x, y).
            direction (tuple): Velocity vector or angle.

        Usage:
            - Called when a player shoots.
            - Bullet added to bullets list with owner_id for scoring.
        """
        pass
    
    def update_bullets(self, delta_time):
        """
        Updates bullet positions and removes out-of-bound bullets.

        Parameters:
            delta_time (float): Time elapsed since last update.

        Usage:
            - Called every tick to move bullets.
            - Checks for collisions with players or map obstacles.
        """
        pass
    
    def detect_collisions(self):
        """
        Detects collisions between:
            - Bullets and players
            - Bullets and enemies (if any)
            - Players and map boundaries or obstacles

        Returns:
            list of collision events (for scoring, removing bullets, etc.)

        Usage:
            - Called after bullets and players are updated each tick.
            - Triggers score updates and health reduction.
        """
        pass
    
    def clamp_position(self,x,y):
        """
        Clamp a given position within the boundaries of the game map.

        Args:
            x (float): The x-coordinate to clamp.
            y (float): The y-coordinate to clamp.

        Returns:
            tuple: A tuple (x, y) where both coordinates are constrained
                to be within the map dimensions [0, MAP_WIDTH] and [0, MAP_HEIGHT].

        Purpose:
            - Prevents the player or objects from moving outside the map boundaries.
        """
        x = max(0,min(x,Game.MAP_WIDTH))
        y = max(0,min(y,Game.MAP_HEIGHT))
        return x,y
    
    def update_scores(self, collision_events):
        """
        Updates scores based on collision events.

        Parameters:
            collision_events (list): List of collision details, 
                                    e.g., bullet hit info.

        Usage:
            - Called after detect_collisions().
            - Updates player scores and kills.
        """
        pass
    
    def check_win_condition(self):
        """
        Checks if the game should end.

        Returns:
            bool: True if win/loss condition is met, otherwise False.

        Usage:
            - Called every tick.
            - Example: all enemies killed, or time expired.
        """
        pass

    def get_game_state(self):
        """
        Returns the current game state for broadcasting.

        Returns:
            dict: Contains player positions, scores, bullet positions, etc.

        Usage:
            - Called by GameRoom.broadcast_game_state() to send to clients.
        """
        players_data = []
        
        for player in self.players.values():
            players_data.append(
                {
                    "player_id" : player.id,
                    "username" : player.username,
                    "player_position" : player.position,
                    "player_direction" : player.direction,
                    "player_health" : player.health,
                    "player_is_alive" : player.is_alive,
                    "player_score" : player.score
                }
            )
            
        return {
            "players" : players_data 
        }
    
    def reset(self):
        """
        Resets the game state for a new round.

        Usage:
            - Called when a new game starts in an existing room.
            - Clears bullets, resets scores and positions.
        """
        pass
    
    def tick(self, delta_time):
        """
        Advances the game logic by one tick/frame.

        Parameters:
            delta_time (float): Time since last tick.

        Usage:
            - Called by GameRoom.tick().
            - Updates player movements, bullets, collisions, and scores.
        """
        for player in self.players:
            self.update_player_position(player, delta_time)
            #player.update_bullets()


    def log_event(self, event_type, details):
        """
        Logs game-related events for debugging or analytics.

        Parameters:
            event_type (str): e.g., 'collision', 'score', 'disconnect'.
            details (dict): Relevant data for the event.

        Usage:
            - Useful for debugging and server analytics.
        """
        pass
    
    



