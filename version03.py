
import pygame
import random
import math

pygame.init()

# -------------------- SETTINGS --------------------
WIDTH = 500
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Desert Highway - Ultimate Racer")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 17, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 38, bold=True)

# -------------------- COLORS --------------------
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
YELLOW = (255, 220, 40)
GOLD = (255, 190, 0)
RED = (235, 55, 55)
BLUE = (40, 145, 255)
GREEN = (45, 220, 100)
PURPLE = (170, 70, 255)
SAND = (218, 183, 115)
DARK_SAND = (185, 146, 83)
ROAD = (65, 67, 72)
ROAD_LINE = (235, 235, 220)
GLASS = (155, 225, 245)

# -------------------- GAME SETTINGS --------------------
ROAD_LEFT = 80
ROAD_RIGHT = 420
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

PLAYER_WIDTH = 42
PLAYER_HEIGHT = 70
PLAYER_SPEED = 6

player = pygame.Rect(
    WIDTH // 2 - PLAYER_WIDTH // 2,
    HEIGHT - 115,
    PLAYER_WIDTH,
    PLAYER_HEIGHT
)

traffic = []
pickups = []

score = 0
coins = 0
best_score = 0

game_speed = 5
road_offset = 0
traffic_timer = 0
pickup_timer = 0

shield_active = False
nitro_timer = 0
nitro_bonus_pending = False

game_state = "menu"


# -------------------- DRAWING HELPERS --------------------
def draw_text(text, font, color, x, y, center=True):
    image = font.render(str(text), True, color)

    if center:
        position = image.get_rect(center=(x, y))
    else:
        position = (x, y)

    screen.blit(image, position)


def draw_car(rect, color, is_player=False):
    """Draw a simple car sprite using Pygame shapes."""
    # Wheels
    pygame.draw.rect(
        screen, BLACK,
        (rect.x - 4, rect.y + 12, 7, 17),
        border_radius=3
    )
    pygame.draw.rect(
        screen, BLACK,
        (rect.right - 3, rect.y + 12, 7, 17),
        border_radius=3
    )
    pygame.draw.rect(
        screen, BLACK,
        (rect.x - 4, rect.y + 43, 7, 17),
        border_radius=3
    )
    pygame.draw.rect(
        screen, BLACK,
        (rect.right - 3, rect.y + 43, 7, 17),
        border_radius=3
    )

    # Car body
    pygame.draw.rect(
        screen, color, rect,
        border_radius=9
    )

    # Front and rear details
    pygame.draw.rect(
        screen, GLASS,
        (rect.x + 7, rect.y + 12, rect.width - 14, 15),
        border_radius=4
    )

    pygame.draw.rect(
        screen, (35, 60, 85),
        (rect.x + 8, rect.y + 39, rect.width - 16, 13),
        border_radius=3
    )

    pygame.draw.rect(
        screen, (255, 245, 180),
        (rect.x + 5, rect.y + 3, 8, 5),
        border_radius=2
    )
    pygame.draw.rect(
        screen, (255, 245, 180),
        (rect.right - 13, rect.y + 3, 8, 5),
        border_radius=2
    )

    pygame.draw.rect(
        screen, RED,
        (rect.x + 5, rect.bottom - 7, 8, 4),
        border_radius=2
    )
    pygame.draw.rect(
        screen, RED,
        (rect.right - 13, rect.bottom - 7, 8, 4),
        border_radius=2
    )

    # Player shield effect
    if is_player and shield_active:
        pygame.draw.ellipse(
            screen, GREEN,
            (rect.x - 10, rect.y - 10,
             rect.width + 20, rect.height + 20),
            3
        )


def draw_truck(rect, color):
    """Draw a larger traffic truck."""
    pygame.draw.rect(
        screen, BLACK,
        (rect.x - 4, rect.y + 15, 7, 20),
        border_radius=2
    )
    pygame.draw.rect(
        screen, BLACK,
        (rect.right - 3, rect.y + 15, 7, 20),
        border_radius=2
    )
    pygame.draw.rect(
        screen, color, rect,
        border_radius=5
    )
    pygame.draw.rect(
        screen, (190, 220, 230),
        (rect.x + 6, rect.y + 7, rect.width - 12, 17),
        border_radius=3
    )
    pygame.draw.rect(
        screen, (80, 85, 90),
        (rect.x + 5, rect.y + 33, rect.width - 10, 10),
        border_radius=2
    )


def draw_coin(rect):
    center = rect.center

    pygame.draw.circle(screen, (180, 115, 0), center, 13)
    pygame.draw.circle(screen, GOLD, center, 10)
    pygame.draw.circle(screen, (255, 230, 100), center, 7)
    draw_text("$", SMALL_FONT, (155, 95, 0),
              center[0], center[1])


def draw_pickup(item):
    rect = item["rect"]
    kind = item["kind"]

    if kind == "coin":
        draw_coin(rect)

    elif kind == "nitro":
        pygame.draw.circle(screen, PURPLE, rect.center, 16)
        pygame.draw.circle(screen, (225, 190, 255),
                           rect.center, 12)
        # Lightning bolt
        points = [
            (rect.centerx + 2, rect.y + 3),
            (rect.centerx - 5, rect.centery),
            (rect.centerx, rect.centery),
            (rect.centerx - 3, rect.bottom - 3),
            (rect.centerx + 6, rect.centery - 2),
            (rect.centerx + 1, rect.centery - 2)
        ]
        pygame.draw.polygon(screen, WHITE, points)

    elif kind == "shield":
        pygame.draw.circle(screen, GREEN, rect.center, 16)
        pygame.draw.circle(screen, (180, 255, 195),
                           rect.center, 12)
        # Shield emblem
        points = [
            (rect.centerx, rect.y + 4),
            (rect.x + 6, rect.y + 8),
            (rect.x + 8, rect.y + 18),
            (rect.centerx, rect.bottom - 3),
            (rect.right - 8, rect.y + 18),
            (rect.right - 6, rect.y + 8)
        ]
        pygame.draw.polygon(screen, (20, 145, 65), points)


# -------------------- BACKGROUND --------------------
def draw_background():
    global road_offset

    screen.fill(SAND)

    # Desert dunes
    pygame.draw.ellipse(
        screen, DARK_SAND,
        (-100, 80, 260, 170)
    )
    pygame.draw.ellipse(
        screen, (230, 199, 135),
        (320, 240, 270, 190)
    )
    pygame.draw.ellipse(
        screen, (202, 165, 98),
        (-120, 440, 280, 200)
    )

    # Road
    pygame.draw.rect(
        screen, ROAD,
        (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT)
    )

    # Road edges
    pygame.draw.rect(
        screen, YELLOW,
        (ROAD_LEFT, 0, 5, HEIGHT)
    )
    pygame.draw.rect(
        screen, YELLOW,
        (ROAD_RIGHT - 5, 0, 5, HEIGHT)
    )

    # Dashed lane markings
    dash_height = 40
    gap = 30

    for lane_x in (ROAD_LEFT + ROAD_WIDTH // 3,
                   ROAD_LEFT + 2 * ROAD_WIDTH // 3):
        for y in range(-dash_height, HEIGHT, dash_height + gap):
            draw_y = (y + road_offset) % (HEIGHT + dash_height)
            pygame.draw.rect(
                screen, ROAD_LINE,
                (lane_x - 3, draw_y, 6, dash_height)
            )

    # Cacti on the desert sides
    for y in range(-100, HEIGHT + 100, 180):
        cactus_y = (y + road_offset * 2) % (HEIGHT + 180) - 90

        for cactus_x in (30, 455):
            pygame.draw.rect(
                screen, (30, 115, 55),
                (cactus_x, cactus_y, 10, 30),
                border_radius=4
            )
            pygame.draw.rect(
                screen, (30, 115, 55),
                (cactus_x - 7, cactus_y + 9, 8, 5),
                border_radius=2
            )
            pygame.draw.rect(
                screen, (30, 115, 55),
                (cactus_x + 8, cactus_y + 17, 8, 5),
                border_radius=2
            )


# -------------------- RESET GAME --------------------
def reset_game():
    global traffic, pickups
    global score, coins, game_speed, road_offset
    global traffic_timer, pickup_timer
    global shield_active, nitro_timer
    global nitro_bonus_pending, player, game_state

    traffic = []
    pickups = []

    score = 0
    coins = 0
    game_speed = 5
    road_offset = 0

    traffic_timer = 0
    pickup_timer = 0

    shield_active = False
    nitro_timer = 0
    nitro_bonus_pending = False

    player.x = WIDTH // 2 - PLAYER_WIDTH // 2
    player.y = HEIGHT - 115

    game_state = "playing"


# -------------------- SPAWNING --------------------
def spawn_traffic():
    lane_centers = [
        ROAD_LEFT + ROAD_WIDTH // 6,
        ROAD_LEFT + ROAD_WIDTH // 2,
        ROAD_LEFT + 5 * ROAD_WIDTH // 6
    ]

    lane_x = random.choice(lane_centers)
    is_truck = random.random() < 0.2

    if is_truck:
        width, height = 48, 88
    else:
        width, height = PLAYER_WIDTH, PLAYER_HEIGHT

    rect = pygame.Rect(
        lane_x - width // 2,
        -height,
        width,
        height
    )

    # Avoid spawning a new vehicle directly on top of another
    for vehicle in traffic:
        if abs(vehicle["rect"].centerx - rect.centerx) < 55:
            if vehicle["rect"].y < 120:
                return

    traffic.append({
        "rect": rect,
        "color": random.choice([
            RED, (240, 145, 30),
            (230, 230, 230), (235, 90, 155),
            (80, 200, 190)
        ]),
        "truck": is_truck
    })


def spawn_pickup():
    lane_centers = [
        ROAD_LEFT + ROAD_WIDTH // 6,
        ROAD_LEFT + ROAD_WIDTH // 2,
        ROAD_LEFT + 5 * ROAD_WIDTH // 6
    ]

    kind = random.choices(
        ["coin", "nitro", "shield"],
        weights=[70, 18, 12],
        k=1
    )[0]

    size = 26 if kind == "coin" else 32
    x = random.choice(lane_centers)

    rect = pygame.Rect(
        x - size // 2,
        -size,
        size,
        size
    )

    pickups.append({
        "rect": rect,
        "kind": kind
    })


# -------------------- MAIN LOOP --------------------
running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if game_state in ("menu", "game_over"):
                if event.key in (pygame.K_s, pygame.K_RETURN,
                                 pygame.K_SPACE):
                    reset_game()

    keys = pygame.key.get_pressed()

    if game_state == "playing":
        # Increasing difficulty
        game_speed = min(5 + score // 500, 13)

        # Nitro makes the game faster temporarily
        current_speed = game_speed

        if nitro_timer > 0:
            current_speed += 4
            nitro_timer -= 1

            if nitro_timer == 0 and nitro_bonus_pending:
                score += 100
                nitro_bonus_pending = False

        # Player movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= PLAYER_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += PLAYER_SPEED

        # Keep the player on the road
        player.left = max(ROAD_LEFT + 8, player.left)
        player.right = min(ROAD_RIGHT - 8, player.right)

        # Move road markings
        road_offset = (road_offset + current_speed) % 70

        # Traffic spawning gets faster as score increases
        traffic_timer += 1
        spawn_interval = max(25, 65 - score // 250)

        if traffic_timer >= spawn_interval:
            spawn_traffic()
            traffic_timer = 0

        # Power-up and coin spawning
        pickup_timer += 1

        if pickup_timer >= 85:
            if random.random() < 0.8:
                spawn_pickup()
            pickup_timer = 0

        # Move traffic
        for vehicle in traffic[:]:
            vehicle["rect"].y += current_speed

            if vehicle["rect"].top > HEIGHT:
                traffic.remove(vehicle)
                score += 10

        # Move pickups
        for item in pickups[:]:
            item["rect"].y += current_speed

            if item["rect"].top > HEIGHT:
                pickups.remove(item)

        # Collect coins and power-ups
        for item in pickups[:]:
            if player.colliderect(item["rect"]):
                kind = item["kind"]

                if kind == "coin":
                    coins += 1
                    score += 25

                elif kind == "nitro":
                    # Give 3 seconds of extra speed
                    nitro_timer = FPS * 3
                    nitro_bonus_pending = True

                elif kind == "shield":
                    # One shield protects against one crash
                    shield_active = True

                pickups.remove(item)

        # Traffic collisions
        for vehicle in traffic[:]:
            if player.colliderect(vehicle["rect"]):
                if shield_active:
                    shield_active = False
                    traffic.remove(vehicle)
                    score += 50
                else:
                    best_score = max(best_score, score)
                    game_state = "game_over"
                break

        # Survival score
        score += 1

    # -------------------- DRAW FRAME --------------------
    draw_background()

    if game_state == "playing":
        # Draw traffic
        for vehicle in traffic:
            if vehicle["truck"]:
                draw_truck(vehicle["rect"], vehicle["color"])
            else:
                draw_car(vehicle["rect"], vehicle["color"])

        # Draw coins and power-ups
        for item in pickups:
            draw_pickup(item)

        # Draw player
        draw_car(player, BLUE, is_player=True)

        # HUD background
        pygame.draw.rect(
            screen, (20, 25, 30),
            (8, 8, 195, 92),
            border_radius=10
        )

        draw_text(f"Score: {score}", SMALL_FONT, WHITE, 20, 15,
                  center=False)
        draw_text(f"Coins: {coins}", SMALL_FONT, GOLD, 20, 40,
                  center=False)

        if shield_active:
            draw_text("SHIELD: READY", SMALL_FONT, GREEN,
                      20, 65, center=False)
        elif nitro_timer > 0:
            seconds = math.ceil(nitro_timer / FPS)
            draw_text(f"NITRO: {seconds}s", SMALL_FONT,
                      PURPLE, 20, 65, center=False)
        else:
            draw_text("Power-ups: collect them!", SMALL_FONT,
                      WHITE, 20, 65, center=False)

        draw_text(f"Speed: {game_speed}", SMALL_FONT,
                  WHITE, WIDTH - 70, 25)

    elif game_state == "menu":
        # Dim overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        screen.blit(overlay, (0, 0))

        draw_text("DESERT HIGHWAY", BIG_FONT, GOLD,
                  WIDTH // 2, 190)
        draw_text("ULTIMATE RACER", FONT, WHITE,
                  WIDTH // 2, 235)

        draw_text("Dodge traffic. Collect rewards!", SMALL_FONT,
                  WHITE, WIDTH // 2, 300)

        draw_text("GOLD COIN  =  +25 POINTS", SMALL_FONT,
                  GOLD, WIDTH // 2, 350)
        draw_text("PURPLE ORB =  NITRO BOOST", SMALL_FONT,
                  (220, 160, 255), WIDTH // 2, 385)
        draw_text("GREEN ORB  =  ONE CRASH SHIELD", SMALL_FONT,
                  GREEN, WIDTH // 2, 420)

        draw_text("A / D or LEFT / RIGHT to drive",
                  SMALL_FONT, WHITE, WIDTH // 2, 485)
        draw_text("Press S, ENTER or SPACE to start",
                  FONT, YELLOW, WIDTH // 2, 545)

    elif game_state == "game_over":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        draw_text("CRASH!", BIG_FONT, RED,
                  WIDTH // 2, 235)
        draw_text(f"Final Score: {score}", FONT, WHITE,
                  WIDTH // 2, 305)
        draw_text(f"Coins Collected: {coins}", FONT, GOLD,
                  WIDTH // 2, 345)
        draw_text(f"Best This Session: {best_score}",
                  SMALL_FONT, WHITE, WIDTH // 2, 385)

        draw_text("Press S, ENTER or SPACE",
                  FONT, YELLOW, WIDTH // 2, 465)
        draw_text("to race again!", FONT, YELLOW,
                  WIDTH // 2, 505)

    pygame.display.flip()

pygame.quit()

