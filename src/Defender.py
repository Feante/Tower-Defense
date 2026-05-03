import os
import warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*avx2.*")
import pygame as pg

# Global image variables for legacy compatibility
pistolguy_img = None
rocketguy_img = None
sniper_img = None

# Module exports
__all__ = [
    'DefenderAssets',
    'Defender',
    'PistolDefender',
    'RocketDefender',
    'SniperDefender',
    'Defendgui',
    'Defend_1',
    'Defend_2',
    'Defend_3',
    'load_defender_assets'
]

class DefenderAssets:
    """Lazy-loaded singleton for all defender images"""
    _loaded = False
    pistolguy_img = None
    rocketguy_img = None
    sniper_img = None
    
    @staticmethod
    def ensure_loaded():
        if not DefenderAssets._loaded:
            script_dir = os.path.dirname(__file__)
            
            try:
                DefenderAssets.pistolguy_img = pg.image.load(
                    os.path.join(script_dir, "assets", "Pistolguy.png")
                ).convert_alpha()
                bbox = DefenderAssets.pistolguy_img.get_bounding_rect()
                if bbox.width > 0 and bbox.height > 0:
                    DefenderAssets.pistolguy_img = DefenderAssets.pistolguy_img.subsurface(bbox)
                DefenderAssets.pistolguy_img = pg.transform.scale(DefenderAssets.pistolguy_img, (80, 80))
            except Exception as e:
                print(f"Error loading Pistolguy.png in DefenderAssets: {e}")
                
            try:
                DefenderAssets.rocketguy_img = pg.image.load(
                    os.path.join(script_dir, "assets", "Rocketguy.png")
                ).convert_alpha()
                bbox = DefenderAssets.rocketguy_img.get_bounding_rect()
                if bbox.width > 0 and bbox.height > 0:
                    DefenderAssets.rocketguy_img = DefenderAssets.rocketguy_img.subsurface(bbox)
                DefenderAssets.rocketguy_img = pg.transform.scale(DefenderAssets.rocketguy_img, (60, 60))
            except Exception as e:
                print(f"Error loading Rocketguy.png in DefenderAssets: {e}")
            
            try:
                DefenderAssets.sniper_img = pg.image.load(
                    os.path.join(script_dir, "assets", "Sniper.png")
                ).convert_alpha()
                bbox = DefenderAssets.sniper_img.get_bounding_rect()
                if bbox.width > 0 and bbox.height > 0:
                    DefenderAssets.sniper_img = DefenderAssets.sniper_img.subsurface(bbox)
                DefenderAssets.sniper_img = pg.transform.scale(DefenderAssets.sniper_img, (50, 50))
            except Exception as e:
                print(f"Error loading Sniper.png in DefenderAssets: {e}")
                
            DefenderAssets._loaded = True

class Defender:
    """Base defender class with pre-loading integration"""
    def __init__(self, defender_type, pos, range_val, cooldown, fire_rate):
        self.type = defender_type
        self.pos = pg.math.Vector2(pos)
        self.range = range_val
        self.cooldown = cooldown
        self.fire_rate = fire_rate
        self.last_shot = 0
        self._ensure_assets_loaded()
    
    def _ensure_assets_loaded(self):
        """Guarantees assets are loaded before use"""
        DefenderAssets.ensure_loaded()
    
    def get_image(self):
        """Returns the appropriate image for this defender type"""
        images = {
            "pistol": DefenderAssets.pistolguy_img,
            "rocket": DefenderAssets.rocketguy_img,
            "sniper": DefenderAssets.sniper_img
        }
        return images.get(self.type, None)
    
    def update(self, current_time, attackers):
        """Updates defender and returns target if in range"""
        if current_time - self.last_shot > self.fire_rate:
            for enemy in attackers:
                if enemy.alive and (self.pos - enemy.pos).length() < self.range:
                    self.last_shot = current_time
                    return enemy
        return None
    
    def draw_range(self, screen):
        """Draws defender range circle only"""
        range_surf = pg.Surface((self.range * 2, self.range * 2), pg.SRCALPHA)
        pg.draw.circle(range_surf, (150, 150, 150, 60), (self.range, self.range), self.range)
        screen.blit(range_surf, (int(self.pos.x) - self.range, int(self.pos.y) - self.range))
    
    def draw_sprite(self, screen):
        """Draws defender sprite only"""
        img = self.get_image()
        if img:
            rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            screen.blit(img, rect)
        else:
            # Fallback circle
            surf = pg.Surface((30, 30), pg.SRCALPHA)
            pg.draw.circle(surf, (0, 255, 0, 255), (15, 15), 15)
            screen.blit(surf, (int(self.pos.x) - 15, int(self.pos.y) - 15))
    
    def draw(self, screen):
        """Draws defender range and sprite"""
        self.draw_range(screen)
        self.draw_sprite(screen)

class PistolDefender(Defender):
    """Pistol guy - short range, slow fire rate"""
    def __init__(self, pos, cooldown=500, fire_rate=500):
        super().__init__("pistol", pos, 100, cooldown, fire_rate)

class RocketDefender(Defender):
    """Rocket guy - long range, very slow fire rate"""
    def __init__(self, pos, cooldown=2000, fire_rate=9000):
        super().__init__("rocket", pos, 500, cooldown, fire_rate)

class SniperDefender(Defender):
    """Sniper - global range, very slow fire rate, instant kill"""
    def __init__(self, pos, cooldown=5000, fire_rate=12000):
        super().__init__("sniper", pos, 10000, cooldown, fire_rate)
    
    def draw_range(self, screen):
        """Sniper has global range - no range circle drawn"""
        pass

def create_defenders(defender_list):
    """Factory function to create defenders with pre-loaded assets"""
    # Assets guaranteed loaded by Defender.__init__
    return [Defender(d["type"], d["pos"], d["range"], d["cooldown"], d["fire_rate"]) for d in defender_list]

def draw_defender_range(screen, defender):
    """Convenience function to draw range for any defender"""
    range_surf = pg.Surface((defender.range * 2, defender.range * 2), pg.SRCALPHA)
    pg.draw.circle(range_surf, (150, 150, 150, 60), (defender.range, defender.range), defender.range)
    screen.blit(range_surf, (int(defender.pos.x) - defender.range, int(defender.pos.y) - defender.range))

def Defendgui(pos_x, pos_y, width, height, screen, color, colordef, circle_pos):
    pg.draw.rect(screen, color, pg.Rect(pos_x, pos_y, width, height)) 
    
    # Pistol Guy icon at original position
    Defend_1(screen, colordef, (pos_x + 34, pos_y + 60))
    
    # Rocket Guy icon below Pistol Guy
    Defend_2(screen, colordef, (pos_x + 34, pos_y + 160))
    
    # Sniper icon below Rocket Guy
    Defend_3(screen, colordef, (pos_x + 34, pos_y + 260))

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

def Defend_3(screen, color, pos):
    global sniper_img
    if sniper_img is None:
        load_defender_assets()
    if sniper_img:
        rect = sniper_img.get_rect(center=(int(pos[0]), int(pos[1])))
        screen.blit(sniper_img, rect)
    else:
        surface = pg.Surface((30, 30), pg.SRCALPHA)
        pg.draw.circle(surface, (*color, 255), (15, 15), 15)
        screen.blit(surface, (pos[0] - 15, pos[1] - 15))

def load_defender_assets():
    global pistolguy_img
    global rocketguy_img
    global sniper_img
    if pistolguy_img is not None:
        return
    if rocketguy_img is not None:
        return
    script_dir = os.path.dirname(__file__)
    pistolguy_path = os.path.join(script_dir, "assets", "Pistolguy.png")
    rocketguy_path = os.path.join(script_dir, "assets", "Rocketguy.png")
    sniper_path = os.path.join(script_dir, "assets", "Sniper.png")
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

    try:
        sniper_img = pg.image.load(sniper_path).convert_alpha()
        bbox = sniper_img.get_bounding_rect()
        if bbox.width > 0 and bbox.height > 0:
            sniper_img = sniper_img.subsurface(bbox)
        sniper_img = pg.transform.scale(sniper_img, (50, 50))
    except Exception as e:
        print(f"Error loading Sniper.png: {e}")
        sniper_img = None
