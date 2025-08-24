import math

class Player:
    
    def __init__(self, id, username, connection, start_position, team):
        self.id = id
        self.username = username
        self.connection = connection
        self.position = start_position # tuple(x,y)
        self.direction = tuple() # (dx,dy)
        self.health = 100.0
        self.is_alive = True
        self.score = 0.0
        self.speed = 200
        self.bullets = list()
        self.team = team
        
    def move(self, new_position):
        """
        Update the player's position in the game world.

        Args:
            new_position (tuple): A tuple (x, y) representing the player's new position.
        
        Purpose:
            - Called each frame or upon input to move the player.
            - Should include checks for map boundaries and collisions in implementation.
        """
        if self.can_move():
            self.position = new_position
        
    
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
            return  # ignore invalid direction
        self.direction = (dx / length, dy / length)
    
    def shoot(self):
        """
        Create and fire a new bullet from the player's position.

        Purpose:
            - Instantiate a bullet object with the player's position and facing direction.
            - Add the bullet to self.bullets for tracking.
            - Could include cooldown checks to prevent spam.
        """
        pass
    
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
        pass
    
    def increase_score(self, points):
        """
        Increase the player's score by a given number of points.

        Args:
            points (float): Amount to add to the player's score.
        
        Purpose:
            - Used when the player achieves something (e.g., killing an enemy).
        """
        pass
    
    def update_bullets(self):
        """
        Update the positions and states of all bullets fired by the player.

        Purpose:
            - Move bullets forward based on their direction and speed.
            - Check for collisions with enemies or obstacles.
            - Remove bullets that go out of bounds or hit a target.
        """
        pass
    
    
    def can_move(self,direction):
        if self.is_alive:
            return True
        return False
        