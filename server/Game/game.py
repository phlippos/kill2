import sys, os
import time
sys.path.append(os.path.dirname(__file__))
import random
from enum import Enum
from player import Player
from bullet import Bullet
from Utils.protocol import Protocol


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
    GAME_DURATION = 180.0

    STARTING_POSITIONS = [

        {"position": (104, 450), "direction": (0, 0)},      
        {"position": (552, 125), "direction": (0, 0)},  
        {"position": (800, 320), "direction": (0, 0)},   
        {"position": (1040, 512), "direction": (0, 0)}  
    ]
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
        self.player_count = 0
        self.platforms = None
        self.bullets = []
        self.protocol = Protocol()
        self.start_time = None
        self.game_ended = False
        self.winner_info = None
        self.winner_broadcasted = False

        
    def add_player(self, player_id, username , connection):
        """
        Adds a player to the game state.

        Parameters:
            player_id (str/int): Unique ID of the player.
            initial_data (dict): Contains initial position, health, team, etc.

        Usage:
            - Called when a player joins a room and game starts.
            - Initializes their score, health, and position.
        """
        player = Player(player_id, username, connection)
        self.players[player_id] = player
        self.player_count += 1
        self.assign_position_to_new_player(player_id)
        
    def start_game(self):
        self.status = Status.STARTED.value
        self.start_time = time.time()
        self.game_ended = False
        self.winner_info = None
        self.winner_broadcasted = False
        print("[Game] Game started!")

    def get_remaining_time(self):
        if self.start_time is None:
            print("[Debug] start_time is None!")
            return self.GAME_DURATION
        elapsed = time.time() - self.start_time
        remaining = self.GAME_DURATION - elapsed
        print(f"[Debug] elapsed: {elapsed:.2f}, remaining: {remaining:.2f}")
        return max(0, remaining)
    
    def broadcast_remaining_time(self):
        
        return self.protocol.serialize_remaining_time(self)

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
            self.player_count -= 1
            return True
        return False


    def assign_starting_positions(self):
        """
        Assigns starting positions and directions directly to players in the room.
        Assumes self.players is a dict {player_id: player_obj}.
        """
        
        for i, player in enumerate(self.players.values()):
            if i >= len(self.STARTING_POSITIONS):
                break  # max 4 player
            pos_info = self.STARTING_POSITIONS[i]
            player.position = pos_info["position"]
            player.direction = pos_info["direction"]
            player.side = "left" if pos_info["direction"][0] > 0 else "right"
    
    def assign_position_to_new_player(self, player_id):
        """
        Assigns a starting position to a newly joined player.
        Finds the first unused STARTING_POSITION and assigns it.
        """
        used_positions = {tuple(p.position) for p in self.players.values() if p.id != player_id}
        
        for pos_info in self.STARTING_POSITIONS:
            if tuple(pos_info["position"]) not in used_positions:
                player = self.players[player_id]
                player.position = pos_info["position"]
                player.direction = pos_info["direction"]
                player.side = "left" if pos_info["direction"][0] > 0 else "right"
                return True
  
        return False

    def assign_position_to_respawned_player(self,player):
        if not player.is_alive:
            random_spawn_point_idx = random.randint(0,3)
            return self.STARTING_POSITIONS[random_spawn_point_idx]["position"]

            
    def update_player_position(self, player_id, direction):
        """
        Buffer player input instead of immediately applying it
        """
        if player_id not in self.players:
            return
            
        player = self.players[player_id]
        
        # Add input to buffer instead of immediately applying
        player.add_input_to_buffer(direction)
        #print(f"Buffered input for player {player_id}: {direction}")
        
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
        if self.players[player_id].is_alive:
            bullet = Bullet(
                owner_id=player_id,
                pos=position,
                dir_vec=direction,
                speed=500,
                damage=10,
                radius=5.0
            )
            self.bullets.append(bullet)
            print(f"[Game] Bullet spawned by Player {player_id} at {position} with dir {direction}")
        
    def update_bullets(self, delta_time):
        """
        Updates all bullets in the game:
            - Moves bullets according to their direction and speed.
            - Checks for collisions with players.
            - Removes bullets that are no longer alive.
        
        Parameters:
            delta (float): Time elapsed since last tick (seconds).
        """
        collision_events = set()

        self.bullets = [b for b in self.bullets if b.alive]
        for bullet in list(self.bullets):  
            bullet.update(delta_time,self.platforms)

            for player in self.players.values():
                if player.id != bullet.owner_id and player.is_alive:
                    if bullet.check_collision(player.position, player_radius=20):
                        player.health -= bullet.damage * player.attack_multiplier()
                        print(player.username," ",player.health," ",player.is_alive)
                        if player.health <= 0:
                            player.is_alive = False
                            collision_events.add(bullet.owner_id)
                        bullet.alive = False
                        break  
                    
            if not ((0 < bullet.pos["x"] and bullet.pos["x"] < self.MAP_WIDTH) and (0 < bullet.pos["y"] and bullet.pos["y"] < self.MAP_HEIGHT)):
                bullet.alive = False

        self.update_scores(collision_events)

    def respawn_player(self,player_id):
        print("respawn_player")
        player = self.players[player_id]
        spawn_point = self.assign_position_to_respawned_player(player)
        print(spawn_point)
        player.respawn(spawn_point)
        

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
        for owner_id in collision_events:
            if owner_id in self.players and self.players[owner_id].is_alive:
                self.players[owner_id].score += 1
                print(f"[Score Update] Player {self.players[owner_id].username} (ID: {owner_id}) new score: {self.players[owner_id].score}")

    
    def check_win_condition(self):
        """
        Checks if the game should end.

        Returns:
            bool: True if win/loss condition is met, otherwise False.

        Usage:
            - Called every tick.
            - Example: all enemies killed, or time expired.
        """
        if self.game_ended:
            return self.winner_info
        
        if self.get_remaining_time() > 0:
            return None 

        self.game_ended = True
        self.status = Status.FINISHED.value

        max_score = 0
        winner = None
        for player in self.players.values():
            if player.score > max_score:
                max_score = player.score
                winner = player

        tied_players = [p for p in self.players.values() if p.score == max_score]

        if len(tied_players) > 1:
            self.winner_info = {
                "result": "tie",
                "message": f"Berabere! {len(tied_players)} oyuncu {max_score} puanla berabere kaldı"
            }
        else:
            self.winner_info = {
                "result": "win",
                "winner": winner.username,
                "winner_id": winner.id,
                "score": max_score,
                "message": f"{winner.username} kazandı! Puan: {max_score}"
            }

        print(f"[Game] Winner Info: {self.winner_info}")
        return self.winner_info

    def get_game_state(self):
        """
        Returns the current game state for broadcasting.

        Returns:
            dict: Contains player positions, scores, bullet positions, etc.

        Usage:
            - Called by GameRoom.broadcast_game_state() to send to clients.
        """
        bullets_data = []
        for bullet in self.bullets:
            bullets_data.append(self.protocol.serialize_shoot(bullet))  
            
        players_data = []
        for player in self.players.values():
            players_data.append(self.protocol.serialize_player(player))

        return self.protocol.serialize_game_state(players_data, bullets_data)
    
   
    
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
        if self.status == Status.STARTED.value:
            for player in self.players.values():
                player.update_physics(delta_time, self.platforms)
                player.position = self.clamp_position(player.position[0],player.position[1])
                
            for bullet in self.bullets:
                self.update_bullets(delta_time)


        # Oyun bitiş kontrolü
        winner_info = self.check_win_condition()
        if winner_info:
            print(f"[Game] Game ended! {winner_info}")


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