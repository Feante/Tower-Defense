import os
import warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*avx2.*")
import pygame as pg

# Placeholder for bullet texture
bullet_img = None
rocket_img = None

def load_bullet_assets():
    global bullet_img
    if bullet_img is not None:
        return
        
    script_dir = os.path.dirname(__file__)
    bullet_path = os.path.join(script_dir, "assets", "bullet.png")
    try:
        bullet_img = pg.image.load(bullet_path).convert_alpha()
        # Scale bullet to a reasonable size (e.g., 40x20)
        bullet_img = pg.transform.scale(bullet_img, (40, 20))
    except Exception as e:
        print(f"Error loading bullet.png: {e}")
        bullet_img = None
def load_rocket_assets():
    global rocket_img
    if rocket_img is not None:
        return
    script_dir = os.path.dirname(__file__)
    rocket_path = os.path.join(script_dir, "assets", "rocket.png")
    try:
        rocket_img = pg.image.load(rocket_path).convert_alpha()
        rocket_img = pg.transform.scale(rocket_img, (80, 40))
    except Exception as e:
        print(f"Error loading rocket.png: {e}")
        rocket_img = None

class Follower:
    def __init__(self, path):
        self.path = path
        self.current_point_idx = 0
        self.pos = pg.Vector2(path[0])
        self.speed = 3

    def update(self):
        if self.current_point_idx < len(self.path):
            target = pg.Vector2(self.path[self.current_point_idx])
            direction = target - self.pos
            if direction.length() < self.speed:
                self.pos = target
                self.current_point_idx += 1
            else:
                self.pos += direction.normalize() * self.speed

    def draw(self, surface):
        pg.draw.circle(surface, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 10)

class Attacker:
    def __init__(self, path, health=20):
        self.path = path
        self.current_point_idx = 0
        self.pos = pg.Vector2(path[0])
        self.speed = 1.5
        self.health = health
        self.max_health = health
        self.alive = True
        self.radius = 12
        self.has_damaged_player = False
 
    def get_rect(self):
        rect = pg.Rect(0, 0, self.radius * 2, self.radius * 2)
        rect.center = (int(self.pos.x), int(self.pos.y))
        return rect
 
    def update(self):
        if not self.alive:
            return
 
        if self.current_point_idx < len(self.path):
            target = pg.Vector2(self.path[self.current_point_idx])
            direction = target - self.pos
 
            if direction.length() < self.speed:
                self.pos = target
                self.current_point_idx += 1
            else:
                self.pos += direction.normalize() * self.speed
        else:
            self.alive = False
 
    def draw(self, screen, image):
        rect = image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        screen.blit(image, rect)
 
    def damage_player(self, player):
        if not self.has_damaged_player and self.current_point_idx >= len(self.path):
            player.health -= self.health
            self.has_damaged_player = True
            self.alive = False
    
  
class Bullet:
    def __init__(self, start_pos, target_obj):
        self.pos = pg.Vector2(start_pos)
        self.target = target_obj
        self.speed = 12
        self.active = True
        
    def update(self):
        if not self.target or not self.target.alive:
            self.active = False
            return
            
        direction = self.target.pos - self.pos
        if direction.length() < self.speed:
            self.pos = pg.Vector2(self.target.pos)
            self.target.health -= 1
            if self.target.health <= 0:
                self.target.alive = False
            self.active = False
        else:
            self.pos += direction.normalize() * self.speed
            
    def draw(self, surface):
        if not self.active:
            return

        global bullet_img
        if bullet_img is None:
            load_bullet_assets()
            
        direction = self.target.pos - self.pos
        if direction.length() > 0:
            angle = direction.angle_to(pg.Vector2(1, 0))
            if bullet_img:
                # Rotate the bullet texture
                rotated_surf = pg.transform.rotate(bullet_img, angle)
                surface.blit(rotated_surf, rotated_surf.get_rect(center=(int(self.pos.x), int(self.pos.y))))
            else:
                # Fallback to green rectangle
                bullet_surf = pg.Surface((12, 6), pg.SRCALPHA)
                pg.draw.rect(bullet_surf, (0, 255, 0), (0, 0, 12, 6))
                rotated_surf = pg.transform.rotate(bullet_surf, angle)
                surface.blit(rotated_surf, rotated_surf.get_rect(center=(int(self.pos.x), int(self.pos.y))))

class Rocket:
    def __init__(self, start_pos, target_obj):
        self.pos = pg.Vector2(start_pos)
        self.target = target_obj
        self.speed = 12
        self.active = True
        
    def update(self, attackers=None):
        if not self.target or not self.target.alive:
            self.active = False
            return
            
        direction = self.target.pos - self.pos
        if direction.length() < self.speed:
            self.pos = pg.Vector2(self.target.pos)
            
            if attackers is not None:
                # Area of effect damage
                aoe_radius = 80
                for enemy in attackers:
                    if enemy.alive and (self.pos - enemy.pos).length() <= aoe_radius:
                        enemy.health -= 5  # AoE damage
                        if enemy.health <= 0:
                            enemy.alive = False
            else:
                self.target.health -= 1
                if self.target.health <= 0:
                    self.target.alive = False
                    
            self.active = False
        else:
            self.pos += direction.normalize() * self.speed
            
    def draw(self, surface):
        if not self.active:
            return

        global rocket_img
        if rocket_img is None:
            load_rocket_assets()
            
        direction = self.target.pos - self.pos
        if direction.length() > 0:
            angle = direction.angle_to(pg.Vector2(1, 0))
            if rocket_img:
                # Rotate the bullet texture
                rotated_surf = pg.transform.rotate(rocket_img, angle)
                surface.blit(rotated_surf, rotated_surf.get_rect(center=(int(self.pos.x), int(self.pos.y))))
            else:
                # Fallback to green rectangle
                rocket_surf = pg.Surface((12, 6), pg.SRCALPHA)
                pg.draw.rect(rocket_surf, (0, 255, 0), (0, 0, 12, 6))
                rotated_surf = pg.transform.rotate(rocket_surf, angle)
                surface.blit(rotated_surf, rotated_surf.get_rect(center=(int(self.pos.x), int(self.pos.y))))

class SniperBullet:
    def __init__(self, start_pos, target_obj):
        self.pos = pg.Vector2(start_pos)
        self.target = target_obj
        self.speed = 20
        self.active = True
        
    def update(self):
        if not self.target or not self.target.alive:
            self.active = False
            return
            
        direction = self.target.pos - self.pos
        if direction.length() < self.speed:
            self.pos = pg.Vector2(self.target.pos)
            # Instant kill
            self.target.health = 0
            self.target.alive = False
            self.active = False
        else:
            self.pos += direction.normalize() * self.speed
            
    def draw(self, surface):
        if not self.active:
            return

        global bullet_img
        if bullet_img is None:
            load_bullet_assets()
            
        direction = self.target.pos - self.pos
        if direction.length() > 0:
            angle = direction.angle_to(pg.Vector2(1, 0))
            if bullet_img:
                rotated_surf = pg.transform.rotate(bullet_img, angle)
                surface.blit(rotated_surf, rotated_surf.get_rect(center=(int(self.pos.x), int(self.pos.y))))
            else:
                bullet_surf = pg.Surface((12, 6), pg.SRCALPHA)
                pg.draw.rect(bullet_surf, (255, 0, 0), (0, 0, 12, 6))
                rotated_surf = pg.transform.rotate(bullet_surf, angle)
                surface.blit(rotated_surf, rotated_surf.get_rect(center=(int(self.pos.x), int(self.pos.y))))

# Print rounds + health
def draw_text(text, x,y,font,screen,color=(255,255,255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def loose_pl_health(health,path,screen):
    plhealth_rect = pg.draw.rect(screen, (255,255,255),pg.Rect(1205,50, 2,2))
    if plhealth_rect.colliderect():
        return health - 2

# Legacy compatibility functions - import from Defender.py
try:
    from Defender import Defendgui, Defend_1, Defend_2
except ImportError:
    # Fallback definitions if Defender.py hasn't loaded yet
    pistolguy_img = None
    rocketguy_img = None
    
    def load_defender_assets():
        global pistolguy_img, rocketguy_img
        if pistolguy_img is not None:
            return
        if rocketguy_img is not None:
            return
        script_dir = os.path.dirname(__file__)
        pistolguy_path = os.path.join(script_dir, "assets", "Pistolguy.png")
        rocketguy_path = os.path.join(script_dir, "assets", "Rocketguy.png")
        try:
            pistolguy_img = pg.image.load(pistolguy_path).convert_alpha()
            bbox = pistolguy_img.get_bounding_rect()
            if bbox.width > 0 and bbox.height > 0:
                pistolguy_img = pistolguy_img.subsurface(bbox)
            pistolguy_img = pg.transform.scale(pistolguy_img, (80, 80))
        except Exception as e:
            print(f"Error loading Pistolguy.png: {e}")
            pistolguy_img = None
            
        try:
            rocketguy_img = pg.image.load(rocketguy_path).convert_alpha()
            bbox = rocketguy_img.get_bounding_rect()
            if bbox.width > 0 and bbox.height > 0:
                rocketguy_img = rocketguy_img.subsurface(bbox)
            rocketguy_img = pg.transform.scale(rocketguy_img, (60, 60))
        except Exception as e:
            print(f"Error loading Rocketguy.png: {e}")
            rocketguy_img = None
    
    def Defendgui(pos_x, pos_y, width, height, screen, color, colordef, circle_pos):
        pg.draw.rect(screen, color, pg.Rect(pos_x, pos_y, width, height))
        Defend_1(screen, colordef, (pos_x + 34, pos_y + 60))
        Defend_2(screen, colordef, (pos_x + 34, pos_y + 160))
    
    def Defend_1(screen, color, pos):
        global pistolguy_img
        if pistolguy_img is None:
            load_defender_assets()
        if pistolguy_img:
            rect = pistolguy_img.get_rect(center=(int(pos[0]), int(pos[1])))
            screen.blit(pistolguy_img, rect)
        else:
            surface = pg.Surface((30, 30), pg.SRCALPHA)
            pg.draw.circle(surface, (*color, 255), (15, 15), 15)
            screen.blit(surface, (pos[0] - 15, pos[1] - 15))
    
    def Defend_2(screen, color, pos):
        global rocketguy_img
        if rocketguy_img is None:
            load_defender_assets()
        if rocketguy_img:
            rect = rocketguy_img.get_rect(center=(int(pos[0]), int(pos[1])))
            screen.blit(rocketguy_img, rect)
        else:
            surface = pg.Surface((30, 30), pg.SRCALPHA)
            pg.draw.circle(surface, (*color, 255), (15, 15), 15)
            screen.blit(surface, (pos[0] - 15, pos[1] - 15))
