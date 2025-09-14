import math

class Bullet:
    bullet_counter = 0

    def __init__(self, owner_id, pos, dir_vec, speed=600, damage=10.0, radius=2.0):
        self.id = Bullet.bullet_counter
        Bullet.bullet_counter += 1

        self.owner_id = owner_id
        self.pos = {"x": float(pos[0]), "y": float(pos[1])}
        self.dir = self._normalize({"x": float(dir_vec[0]), "y": float(dir_vec[1])})
        self.speed = float(speed)
        self.damage = float(damage)
        self.radius = float(radius)
        self.alive = True

    def _normalize(self, v):
        length = math.hypot(v["x"], v["y"])
        if length == 0.0:
            return {"x": 0.0, "y": 0.0}
        return {"x": v["x"]/length, "y": v["y"]/length}

    def update(self, delta_time, map_platforms=None):
        if not self.alive:
            return

        # pozisyonu güncelle
        self.pos["x"] += self.dir["x"] * self.speed * delta_time
        self.pos["y"] += self.dir["y"] * self.speed * delta_time

        # platform çarpışma kontrolü
        if map_platforms:
            if self.check_collision_platforms(map_platforms):
                self.alive = False

    def check_collision(self, player_pos, player_radius=20):
        dx = self.pos["x"] - float(player_pos[0])
        dy = self.pos["y"] - float(player_pos[1])
        distance_sq = dx*dx + dy*dy
        return distance_sq <= (self.radius + float(player_radius)) ** 2

    def check_collision_platforms(self, platforms):
        """Platformlardan herhangi birine çarptıysa True döner."""
        for rect in platforms:
            if self._circle_rect_collision(rect):
                return True
        return False

    def _circle_rect_collision(self, rect):
        """Çember (mermi) - dikdörtgen (platform) çarpışması"""
        cx, cy, r = self.pos["x"], self.pos["y"], self.radius
        rx, ry = rect["x"], rect["y"]
        rw, rh = rect["width"], rect["height"]

        # Çembere en yakın noktayı bul
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))

        dx = cx - closest_x
        dy = cy - closest_y
        return (dx*dx + dy*dy) <= r*r
