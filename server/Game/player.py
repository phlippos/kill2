import math
import random

class Player:
    
    def __init__(self, id, username, connection):
        self.id = id
        self.username = username
        self.connection = connection
        self.position = tuple([0,0]) # tuple(x,y)
        self.direction = tuple([0,0]) # (dx,dy)
        self.health = 100.0
        self.is_alive = True
        self.score = 0.0
        self.speed = 200
        self.bullets = list()
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.gravity = 800.0
        self.jump_force = 400.0
        self.is_on_ground = False
        self.player_width = 34
        self.player_height = 68
        self.input_buffer = []
        self.max_jumps = 2
        self.jump_count = 0

    def add_input_to_buffer(self, direction, timestamp=None):
        """
        Add input to buffer for processing on next physics tick
        """
        if not hasattr(self, 'input_buffer'):
            self.input_buffer = []
        
        import time
        if timestamp is None:
            timestamp = time.time()
        
        self.input_buffer.append((direction, timestamp))
        #print(f"Player {self.id} buffered input: {direction}")

    def process_buffered_inputs(self, delta_time):
        """Process all buffered inputs this tick"""
        jump_triggered = False
        current_movement = (0, 0)
        
        for direction, timestamp in self.input_buffer:
            dx, dy = direction
            # Check for jump input
            if dy < 0 and self.is_on_ground:
                jump_triggered = True
            # Use latest movement input
            current_movement = (dx, 0)  # Don't override Y for continuous movement
        
        # Apply jump if triggered
        if jump_triggered:
            self.velocity_y = -self.jump_force
            self.is_on_ground = False
        
        # Apply horizontal movement
        self.direction = current_movement
        self.input_buffer.clear()  # Clear after processing

    def update_physics(self, delta_time, platforms):
        """
        Platform physics with input buffering and double jump support
        """
        if not self.can_move():
            return
        
        # Initialize input buffer and current direction if they don't exist
        if not hasattr(self, 'input_buffer'):
            self.input_buffer = []
        if not hasattr(self, 'current_direction'):
            self.current_direction = (0, 0)
        
        # Process all buffered inputs from this tick
        jump_triggered = False
        
        # Process all inputs received since last tick
        for direction, timestamp in self.input_buffer:
            dx, dy = direction

            if dy < 0:  
                if self.is_on_ground:
                    # First jump from ground
                    jump_triggered = True
                    self.jump_count = 0 
                    #print(f"Player {self.id} first jump from ground")
                elif self.jump_count < self.max_jumps:
                    jump_triggered = True
                    #print(f"Player {self.id} air jump #{self.jump_count + 1}")
            
            # Update current direction (keep the most recent)
            self.current_direction = (dx, dy)
        
        # Clear the buffer after processing
        self.input_buffer.clear()
        
        # Get horizontal input from current direction
        horizontal_input = self.current_direction[0]
        
        # Calculate velocity_x for client synchronization
        self.velocity_x = horizontal_input * self.speed
        
        # Apply jump if it was triggered
        if jump_triggered:
            self.velocity_y = -self.jump_force
            self.is_on_ground = False
            self.jump_count += 1
            #print(f"Player {self.id} jumping! velocity_y: {self.velocity_y}, jump_count: {self.jump_count}")
        
        # Apply gravity if not on ground
        if not self.is_on_ground:
            self.velocity_y += self.gravity * delta_time
        
        # Calculate new positions using velocities
        new_x = self.position[0] + self.velocity_x * delta_time
        new_y = self.position[1] + self.velocity_y * delta_time
        
        # Check platform collisions
        collision_result = self.check_platform_collisions(new_x, new_y, platforms)
        
        if collision_result:
            new_y = collision_result["ground_y"]
            self.velocity_y = 0.0
            self.is_on_ground = True
            self.jump_count = 0 
            #print(f"Player {self.id} landed on platform at y: {new_y}, jump_count reset")
        else:
            self.is_on_ground = False
        
        self.position = (new_x, new_y)
        #print(f"Player {self.id} - pos: {self.position}, velocity: ({self.velocity_x}, {self.velocity_y}), on_ground: {self.is_on_ground}, jumps: {self.jump_count}/{self.max_jumps}")


    def rotate(self, new_direction):
        """
        Change the player's facing direction.

        Args:
            new_direction (tuple): A normalized (dx, dy) vector indicating the new facing direction.
        
        Purpose:
            - Used to aim bullets or determine movement orientation.
            - Typically updated when the player rotates the camera or changes direction.
        """
        dx, dy = new_direction
        length = math.sqrt(dx**2 + dy**2)
        if length == 0:
            self.direction = (dx,dy)
            return
        self.direction = (dx / length, dy / length)
    
    def take_damage(self, amount):
        """
        Apply damage to the player and check if they are still alive.

        Args:
            amount (float): Amount of health to subtract.
        
        Purpose:
            - Decrease player's health.
            - If health <= 0, set is_alive to False and trigger death/respawn logic.
        """
        pass
    
    def respawn(self, spawn_point):
        """
        Respawn the player at a given location with default state.

        Args:
            spawn_point (tuple): A tuple (x, y) for the respawn position.
        
        Purpose:
            - Reset player's position, health, and status.
            - Typically called after player death with a safe spawn point.
        """
        self.position = spawn_point
        self.health = 100.0
        self.is_alive = True
    
    def increase_score(self, points):
        """
        Increase the player's score by a given number of points.

        Args:
            points (float): Amount to add to the player's score.
        
        Purpose:
            - Used when the player achieves something (e.g., killing an enemy).
        """
        pass
    
    def check_platform_collisions(self, x, y, platforms):
        """
        Platform collision detection
        """
        player_bottom = y + self.player_height
        player_left = x
        player_right = x + self.player_width
        
        for platform in platforms:
            if (player_right > platform["x"] and 
                player_left < platform["x"] + platform["width"] and
                self.velocity_y >= 0 and  # Düşüyor
                player_bottom >= platform["y"] and
                player_bottom <= platform["y"] + platform["height"] + 5):
                
                return {"ground_y": platform["y"] - self.player_height}
        
        return None
    
    def attack_multiplier(self):
        return random.choices([0, 1, 3, 5], weights=[10, 80, 8, 2], k=1 )[0]
        
    def can_move(self):
        if self.is_alive:
            return True
        return False
        