import pygame
import os
import time

pygame.init()

screen_width, screen_height = 900, 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Maze Game - 10 Enemies")
font = pygame.font.SysFont(None, 20)
clock = pygame.time.Clock()


pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

dragon_sound = pygame.mixer.Sound("dragon_sound.mp3")
dragon_sound.play(-1)

logo = pygame.image.load("logo.png").convert_alpha()
logo = pygame.transform.scale(logo, (150, 75))

background = pygame.image.load("prision_background.png").convert()
image = pygame.image.load("prision.png").convert_alpha()
image_rect = image.get_rect(topleft=(0, 0))
image_mask = pygame.mask.from_surface(image)

player_images = [pygame.image.load(f"player_{i}.png").convert_alpha() for i in range(1, 6)]
player_index = 0
player_direction = "up"
ANIMATION_DELAY = 5
animation_counter = 0

enemy_images = [pygame.image.load(f"enemy_{i}.png").convert_alpha() for i in range(1, 7)]
ENEMY_ANIMATION_DELAY = 10

Red = (255, 0, 0)

FOLLOW_DURATION = 300
ZOOM = 5
CAMERA_WIDTH, CAMERA_HEIGHT = int(screen_width / ZOOM), int(screen_height / ZOOM)
WORLD_WIDTH, WORLD_HEIGHT = image_rect.width, image_rect.height
ENEMY_SIZE = 300
ENEMY_COLLISION_BOX = pygame.Rect(0, 0, 30, 30)  # Adjustable size

target_rect = pygame.Rect(1280, 600, 100, 130)

info_areas = [
    {"rect": pygame.Rect(780, 310, 100, 100), "text": "Temple - 1"},
    {"rect": pygame.Rect(710, 710, 75, 75), "text": "Temple - 2"},
    {"rect": pygame.Rect(25, 10, 100, 75), "text": "Temple - 3"},
    {"rect": pygame.Rect(1260, 320, 75, 75), "text": "Temple- 4"},
]

visited_areas = [False] * len(info_areas)

blocked_rect = pygame.Rect(1400, 600, 10, 130)
block_active = True

def reset_game():
    global player, enemies, enemy_animation_counter, enemy_frame_indices, visited_areas, block_active
    player = pygame.Rect(25, 850, 15, 15)
    enemy_animation_counter = 0
    enemy_frame_indices = {}
    visited_areas = [False] * len(info_areas)
    block_active = True

    base_enemies = [
        (220, 760, 150, 600, 150, 200),
        
        
        (1400, 400, 1300, 500, 200, 200),
        (400, 500, 200, 50, 200, 200),
        (1000, 300, 750, 650, 200, 200),
     
        (1500, 100, 1400, 50, 200, 200),
        (300, 300, 50, 350, 200, 200),
        (1600, 0, 1500, 700, 200, 200),
    ]

    enemies.clear()
    for i, (x, y, rx, ry, rw, rh) in enumerate(base_enemies):
        enemies[f"enemy_{i+1}"] = {
            "x": x, "y": y, "ox": x, "oy": y,
            "up": False, "down": True,
            "move": True, "follow": False,
            "range": pygame.Rect(rx, ry, rw, rh),
            "timer": 0,
            "angle": 0,
            "facing": "up"
        }
        enemy_frame_indices[f"enemy_{i+1}"] = 0

enemies = {}
reset_game()



def draw_grid(camera_x, camera_y):
    grid_color = (220, 220, 220)
    for x in range(0, WORLD_WIDTH, 100):
        pygame.draw.line(screen, grid_color, ((x - camera_x) * ZOOM, 0), ((x - camera_x) * ZOOM, screen_height), 1)
        screen.blit(font.render(str(x), True, (0, 0, 0)), ((x - camera_x) * ZOOM + 2, 2))
    for y in range(0, WORLD_HEIGHT, 100):
        pygame.draw.line(screen, grid_color, (0, (y - camera_y) * ZOOM), (screen_width, (y - camera_y) * ZOOM), 1)
        screen.blit(font.render(str(y), True, (0, 0, 0)), (2, (y - camera_y) * ZOOM + 2))

running = True
while running:
    camera_x = max(0, min(player.x - CAMERA_WIDTH // 2, WORLD_WIDTH - CAMERA_WIDTH))
    camera_y = max(0, min(player.y - CAMERA_HEIGHT // 2, WORLD_HEIGHT - CAMERA_HEIGHT))
    pygame.draw.rect(screen, Red, target_rect)
    screen.fill((255, 255, 255))
    background_scaled = pygame.transform.smoothscale(background.subsurface((camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT)), (screen_width, screen_height))
    screen.blit(background_scaled, (0, 0))
    scaled_image = pygame.transform.smoothscale(image.subsurface((camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT)), (screen_width, screen_height))
    screen.blit(scaled_image, (0, 0))

    keys = pygame.key.get_pressed()
    move_x = -2 if keys[pygame.K_LEFT] else 2 if keys[pygame.K_RIGHT] else 0
    move_y = -2 if keys[pygame.K_UP] else 2 if keys[pygame.K_DOWN] else 0
    new_player = player.move(move_x, move_y)
    
    

    if move_x != 0 or move_y != 0:
        animation_counter += 1
        if animation_counter >= ANIMATION_DELAY:
            animation_counter = 0
            player_index = (player_index + 1) % len(player_images)
        if move_y < 0: player_direction = "up"
        elif move_y > 0: player_direction = "down"
        elif move_x < 0: player_direction = "left"
        elif move_x > 0: player_direction = "right"

    blocked_collision = block_active and new_player.colliderect(blocked_rect)

    if 0 <= new_player.x <= WORLD_WIDTH - player.width and 0 <= new_player.y <= WORLD_HEIGHT - player.height:
        offset = (new_player.x - image_rect.x, new_player.y - image_rect.y)
        player_mask = pygame.mask.Mask((player.width, player.height), fill=True)
        if not image_mask.overlap(player_mask, offset) and not blocked_collision:
            player = new_player

    image_to_draw = player_images[player_index]
    angle_map = {"up": 0, "right": -90, "down": 180, "left": 90}
    rotated_image = pygame.transform.rotate(image_to_draw, angle_map[player_direction])
    scaled_player = pygame.transform.smoothscale(rotated_image, (int(player.width * ZOOM), int(player.height * ZOOM)))
    screen.blit(scaled_player, ((player.x - camera_x) * ZOOM, (player.y - camera_y) * ZOOM))

    player_in_safe_zone = False
    for i, area in enumerate(info_areas):
        if player.colliderect(area["rect"]):
            if not visited_areas[i]:
                visited_areas[i] = True
            player_in_safe_zone = True
            text_surface = font.render(area["text"], True, (255, 255, 0))
            screen.blit(text_surface, (20, 20))

    if all(visited_areas):
        block_active = False

    if block_active:
        pygame.draw.rect(screen, (0, 0, 255), ((blocked_rect.x - camera_x) * ZOOM, (blocked_rect.y - camera_y) * ZOOM, blocked_rect.width * ZOOM, blocked_rect.height * ZOOM))

    enemy_animation_counter += 1
    advance_enemy_frame = enemy_animation_counter >= ENEMY_ANIMATION_DELAY
    if advance_enemy_frame:
        enemy_animation_counter = 0

    for name, e in enemies.items():
        enemy_rect = pygame.Rect(e["x"], e["y"], ENEMY_SIZE, ENEMY_SIZE)
        collision_rect = pygame.Rect(e["x"] + 10, e["y"] + 10, ENEMY_COLLISION_BOX.width, ENEMY_COLLISION_BOX.height)

        if collision_rect.colliderect(player):
            pygame.display.flip()
            time.sleep(1)
            reset_game()
            break

        if player_in_safe_zone:
            e["follow"] = False
            e["move"] = False
        else:
            if e["range"].colliderect(player) and not e["follow"]:
                e["move"] = False
                e["follow"] = True
                e["timer"] = FOLLOW_DURATION

        if not player_in_safe_zone:
            if e["follow"]:
                dx = player.x - e["x"]
                dy = player.y - e["y"]
                if abs(dx) > abs(dy):
                    e["facing"] = "right" if dx > 0 else "left"
                else:
                    e["facing"] = "down" if dy > 0 else "up"
                e["x"] += 1 if dx > 0 else -1 if dx < 0 else 0
                e["y"] += 1 if dy > 0 else -1 if dy < 0 else 0
                e["timer"] -= 1
                if e["timer"] <= 0:
                    e["follow"] = False
            elif not e["move"]:
                if e["x"] < e["ox"]: e["x"] += 1
                elif e["x"] > e["ox"]: e["x"] -= 1
                if e["y"] < e["oy"]: e["y"] += 1
                elif e["y"] > e["oy"]: e["y"] -= 1
                if e["x"] == e["ox"] and e["y"] == e["oy"]:
                    e["move"] = True
            elif e["move"]:
                e["facing"] = "down" if e["down"] else "up"
                e["y"] += 1 if e["down"] else -1
                patrol_top = e["oy"] - 80
                patrol_bottom = e["oy"] + 80
                if e["y"] >= patrol_bottom: e["up"], e["down"] = True, False
                if e["y"] <= patrol_top: e["down"], e["up"] = True, False

        if advance_enemy_frame:
            enemy_frame_indices[name] = (enemy_frame_indices[name] + 1) % len(enemy_images)

        enemy_image = enemy_images[enemy_frame_indices[name]]
        rotated_enemy = pygame.transform.rotate(enemy_image, angle_map[e["facing"]])
        scaled_enemy = pygame.transform.smoothscale(rotated_enemy, (ENEMY_SIZE, ENEMY_SIZE))
        screen.blit(scaled_enemy, ((e["x"] - camera_x) * ZOOM, (e["y"] - camera_y) * ZOOM))
        
    for area in info_areas:
        pygame.draw.rect(
            screen, (255, 0, 0),
            pygame.Rect((area["rect"].x - camera_x) * ZOOM, (area["rect"].y - camera_y) * ZOOM, area["rect"].width * ZOOM, area["rect"].height * ZOOM),
            2
        )

    #draw_grid(camera_x, camera_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    if target_rect.colliderect(player):
       text = font.render("Princess - is your flag", True, Red)
       screen.blit(text, (200, 50))
    screen.blit(logo, (750, 50))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
