import os
import warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*avx2.*")
import pygame as pg
from pygame.draw import circle
from submodule import *
from Defender import DefenderAssets, PistolDefender, RocketDefender, SniperDefender, Defendgui, Defend_1, Defend_2, Defend_3

# ____SETUP____
pg.init()
WIDTH,HEIGHT =  1536,1024
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
script_dir = os.path.dirname(__file__)
bg_path = os.path.join(script_dir, "assets", "Background.jpg")
background = pg.image.load(bg_path)
CIRCLE_ORIGIN = pg.math.Vector2(1500, 30)
circle_def = CIRCLE_ORIGIN.copy()
zombie_walking_path = os.path.join(script_dir, "assets", "zombie_walking.png")
zombie_walking_image = pg.image.load(zombie_walking_path)
zombie_walking_image = pg.transform.scale(zombie_walking_image, (80, 80))
zombie_walking_fast_path = os.path.join(script_dir, "assets", "zombie_walking_fast.png")
zombie_walking_fast_image = pg.image.load(zombie_walking_fast_path).convert_alpha()
zombie_walking_fast_image = pg.transform.scale(zombie_walking_fast_image, (80, 80))
last_anim_time = 0
current_zombie_frame = 0

# ____coordinates____Road____Attackers____
ROAD_PATH = [
    (1293,1024),
    (1162,852),
    (1162,803),
    (1225,718),
    (1346,628),
    (1383,500),
    (1300,420),
    (1160,430),
    (1015,500),
    (940,625),
    (875,740),
    (770,810),
    (580,905),
    (340,965),
    (345,900),
    (350,845),
    (370,750),
    (430,685),
    (510,650),
    (630,635),
    (720,600),
    (740,540),
    (700,470),
    (465,380),
    (300,315),
    (275,265),
    (285,210),
    (370,130),
    (475,125),
    (590,170),
    (700,230),
    (830,225),
    (950,180),
    (1055,170),
    (1175,150),
    (1205,50)
]
defenders = []
# ___Colours___
white = (255, 255, 255)
red = (255, 0, 0)
black = (0,0,0)
blue = (0, 0, 255)
green = (0, 255, 0)
brown = (181, 122, 0)

# ___INSTANTIATE___
health_pl = 200
money = 500
attackers = []
spawn_queue = 0
current_round = 0
round_start = False
current_attacker_health = 20
last_spawn_time = 0
spawn_delay = 100  # 100 milliseconds between spawns
drag_offset = pg.math.Vector2(0,0)
bullets = []
rockets = []
sniper_bullets = []
last_shot_time_p = 0
last_shot_time_r = 0
rect_gui = pg.Rect(1468,0,200,1024)
dragging = False
dragging_type = None
running = True
i = 2

# ___Text___
font = pg.font.SysFont('arial', 24)

while running:
    # ___EVENTS___
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pg.math.Vector2(event.pos)
                if rect_gui.collidepoint(event.pos):
                    # Check distance to pistol guy (1468 + 34, 60)
                    pistol_center = pg.math.Vector2(1468 + 34, 60)
                    # Check distance to rocket guy (1468 + 34, 160)
                    rocket_center = pg.math.Vector2(1468 + 34, 160)
                    
                    if (mouse_pos - pistol_center).length() <= 40:
                        dragging = True
                        dragging_type = "pistol"
                        circle_def = pistol_center.copy()
                        drag_offset = mouse_pos - pistol_center
                    elif (mouse_pos - rocket_center).length() <= 40:
                        dragging = True
                        dragging_type = "rocket"
                        circle_def = rocket_center.copy()
                        drag_offset = mouse_pos - rocket_center
                    else:
                        # Check distance to sniper (1468 + 34, 260)
                        sniper_center = pg.math.Vector2(1468 + 34, 260)
                        if (mouse_pos - sniper_center).length() <= 40:
                            dragging = True
                            dragging_type = "sniper"
                            circle_def = sniper_center.copy()
                            drag_offset = mouse_pos - sniper_center
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1 and dragging:
                # Check if placement is within the GUI area
                mouse_x = pg.mouse.get_pos()[0]
                if 1468 <= mouse_x <= 1668:
                    # Placement would be inside GUI - reject
                    pass
                else:
                    # Placement is valid - instantiate based on what was dragged
                    if dragging_type == "pistol":
                        if money >= 100:
                            defenders.append(PistolDefender(circle_def.copy()))
                            money -= 100
                    elif dragging_type == "rocket":
                        if money >= 250:
                            defenders.append(RocketDefender(circle_def.copy()))
                            money -= 250
                    elif dragging_type == "sniper":
                        if money >= 500:
                            defenders.append(SniperDefender(circle_def.copy()))
                            money -= 500
                dragging = False
                dragging_type = None
                circle_def = CIRCLE_ORIGIN.copy()
    
    
    # ___LOGIC___
    # Spawn attackers from queue
    if spawn_queue > 0:
        current_time = pg.time.get_ticks()
        if current_time - last_spawn_time > spawn_delay:
            attackers.append(Attacker(ROAD_PATH, health=current_attacker_health))
            spawn_queue -= 1
            last_spawn_time = current_time
    
    # Update attackers
    for attacker in attackers[:]:
        attacker.update()
        if attacker.current_point_idx >= len(attacker.path):
            health_pl -= 2
            attacker.alive = False
        if not attacker.alive:
            if attacker.current_point_idx < len(attacker.path):
                money += 20
            attackers.remove(attacker)
    
    # Update bullets
    for bullet in bullets[:]:
        bullet.update()
        if not bullet.active:
            bullets.remove(bullet)
    for rocket in rockets[:]:
        rocket.update(attackers)
        if not rocket.active:
            rockets.remove(rocket)
    for sb in sniper_bullets[:]:
        sb.update()
        if not sb.active:
            sniper_bullets.remove(sb)
            
    # Defenders shoot
    current_time = pg.time.get_ticks()
    for defender in defenders:
        target = defender.update(current_time, attackers)
        if target:
            if defender.type == "pistol":
                bullets.append(Bullet(defender.pos, target))
            elif defender.type == "rocket":
                rockets.append(Rocket(defender.pos, target))
            elif defender.type == "sniper":
                sniper_bullets.append(SniperBullet(defender.pos, target))
        last_shot_time_p = current_time
   
    # Round progression
    if not attackers and spawn_queue == 0:
        if i == 0:
            current_round += 1
        else:
            i -= 1
        # Start next round
        if current_round > 5:
            current_attacker_health * 0.3
        elif current_round <= 40:
            spawn_queue = current_round
        elif current_round <= 60:
            spawn_queue = 40
            current_attacker_health *= 1.5
        elif current_round <= 80:
            spawn_queue = 50
            current_attacker_health *= 50 
        # Optional: reset last_spawn_time to trigger immediate first spawn
        last_spawn_time = pg.time.get_ticks() - spawn_delay
        
    if dragging:
        circle_def.x = pg.mouse.get_pos()[0] - drag_offset.x
        circle_def.y = pg.mouse.get_pos()[1] - drag_offset.y

    # ___RENDER___
    screen.blit(background, (0, 0))
    # Draw placed defenders - two passes so icons are always above range circles
    for defender in defenders:
        defender.draw_range(screen)
    for defender in defenders:
        defender.draw_sprite(screen)

    # Draw Health and Round
    draw_text(f"Health: {health_pl}", 10, 5,font,screen)
    draw_text(f"Money: {money}", 10, 35, font, screen, (255, 215, 0))
    draw_text(f"Round: {current_round}", 200, 5,font,screen)
    # Draw bullets
    for bullet in bullets:
        bullet.draw(screen)
    for rocket in rockets:
        rocket.draw(screen)
    for sb in sniper_bullets:
        sb.draw(screen)
        
    Defendgui(1468, 0, 200, 1024, screen, brown, red, circle_def)
    
    # Draw tower costs
    draw_text("$100", 1468 + 70, 48, font, screen, (255, 215, 0))
    draw_text("$250", 1468 + 70, 148, font, screen, (255, 215, 0))
    draw_text("$500", 1468 + 70, 248, font, screen, (255, 215, 0))
    
    if dragging:
        if dragging_type != "sniper":
            range_val = 100 if dragging_type == "pistol" else 500
            range_surf = pg.Surface((range_val * 2, range_val * 2), pg.SRCALPHA)
            pg.draw.circle(range_surf, (150, 150, 150, 60), (range_val, range_val), range_val)
            screen.blit(range_surf, (int(circle_def.x) - range_val, int(circle_def.y) - range_val))
        if dragging_type == "pistol":
            Defend_1(screen, red, circle_def)
        elif dragging_type == "rocket":
            Defend_2(screen, red, circle_def)
        elif dragging_type == "sniper":
            Defend_3(screen, red, circle_def)
            
    # Draw all attackers
    for attacker in attackers:
        attacker.draw(screen, current_zombie_image)
    current_time = pg.time.get_ticks()
 
    if current_time - last_anim_time > 250:
        current_zombie_frame = (current_zombie_frame + 1) % 2
        last_anim_time = current_time
 
    if current_zombie_frame == 0:
        current_zombie_image = zombie_walking_image
    else:
        current_zombie_image = zombie_walking_fast_image
    
    

    pg.display.update()
    clock.tick(60)

pg.quit()
