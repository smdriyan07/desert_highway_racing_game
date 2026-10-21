
import pygame
import random

pygame.init()

# -------------------- WINDOW --------------------

WIDTH = 500
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Desert Highway - Endless Racer")

clock = pygame.time.Clock()

# -------------------- COLOURS --------------------

SAND = (218, 174, 105)
LIGHT_SAND = (237, 199, 132)
DARK_SAND = (191, 144, 79)
ROAD = (65, 65, 68)
ROAD_EDGE = (230, 210, 170)
WHITE = (245, 245, 235)
YELLOW = (255, 205, 65)
BLACK = (25, 25, 28)

font = pygame.font.Font(None, 38)
small_font = pygame.font.Font(None, 27)
big_font = pygame.font.Font(None, 58)

# -------------------- ROAD --------------------

ROAD_LEFT = 75
ROAD_RIGHT = 425
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

LANES = [
    ROAD_LEFT + ROAD_WIDTH // 6,
    ROAD_LEFT + ROAD_WIDTH // 2,
    ROAD_LEFT + 5 * ROAD_WIDTH // 6
]

# -------------------- SPRITE CREATION --------------------

def make_car(colour, vehicle_type="car"):
    # Transparent image surface for the vehicle sprite
    sprite = pygame.Surface((50, 82), pygame.SRCALPHA)

    # Tyres
    pygame.draw.rect(sprite, BLACK, (3, 15, 9, 20), border_radius=3)
    pygame.draw.rect(sprite, BLACK, (38, 15, 9, 20), border_radius=3)
    pygame.draw.rect(sprite, BLACK, (3, 52, 9, 20), border_radius=3)
    pygame.draw.rect(sprite, BLACK, (38, 52, 9, 20), border_radius=3)

    if vehicle_type == "truck":
        # Truck body and cargo section
        pygame.draw.rect(
            sprite, colour, (8, 3, 34, 76), border_radius=5
        )
        pygame.draw.rect(
            sprite, (190, 190, 185), (11, 7, 28, 39),
            border_radius=3
        )
        pygame.draw.rect(
            sprite, colour, (11, 47, 28, 25), border_radius=3
        )
    else:
        # Main car body
        pygame.draw.rect(
            sprite, colour, (7, 3, 36, 76), border_radius=10
        )

        # Windscreen
        pygame.draw.polygon(
            sprite, (115, 180, 205),
            [(12, 19), (38, 19), (35, 32), (15, 32)]
        )

        # Rear window
        pygame.draw.polygon(
            sprite, (55, 85, 105),
            [(15, 49), (35, 49), (38, 59), (12, 59)]
        )

        # Bonnet highlight
        pygame.draw.line(
            sprite, (245, 245, 245),
            (14, 9), (36, 9), 2
        )

    # Headlights
    pygame.draw.rect(sprite, YELLOW, (9, 4, 8, 4), border_radius=2)
    pygame.draw.rect(sprite, YELLOW, (33, 4, 8, 4), border_radius=2)

    # Rear lights
    pygame.draw.rect(sprite, (235, 45, 40), (10, 73, 8, 4))
    pygame.draw.rect(sprite, (235, 45, 40), (32, 73, 8, 4))

    return sprite


player_sprite = make_car((35, 115, 235))

traffic_sprites = [
    make_car((220, 55, 45)),
    make_car((235, 205, 55)),
    make_car((55, 180, 95)),
    make_car((175, 75, 210)),
    make_car((235, 235, 225)),
    make_car((100, 105, 115)),
    make_car((175, 150, 115), "truck")
]

# -------------------- DESERT SCENERY --------------------

def draw_cactus(x, y):
    # Simple cactus decoration
    pygame.draw.rect(screen, (38, 105, 55), (x + 8, y, 8, 32))
    pygame.draw.rect(screen, (38, 105, 55), (x, y + 10, 8, 15))
    pygame.draw.rect(screen, (38, 105, 55), (x, y + 10, 13, 7))
    pygame.draw.rect(screen, (38, 105, 55), (x + 16, y + 16, 8, 14))
    pygame.draw.rect(screen, (38, 105, 55), (x + 11, y + 16, 13, 7))


# -------------------- GAME VARIABLES --------------------

player = pygame.Rect(0, 0, 42, 72)
player.centerx = LANES[1]
player.bottom = HEIGHT - 35

traffic = []
scenery = []

score = 0
best_score = 0
road_offset = 0
spawn_timer = 0

game_speed = 5
game_state = "start"

# Generate some desert decorations
for i in range(8):
    scenery.append({
        "x": random.choice([20, 35, 440, 455]),
        "y": i * 110,
        "type": "cactus"
    })


# -------------------- RESET GAME --------------------

def reset_game():
    global player, traffic, scenery
    global score, road_offset, spawn_timer, game_speed

    player.centerx = LANES[1]
    player.bottom = HEIGHT - 35

    traffic = []
    score = 0
    road_offset = 0
    spawn_timer = 0
    game_speed = 5

    scenery = []

    for i in range(8):
        scenery.append({
            "x": random.choice([20, 35, 440, 455]),
            "y": i * 110,
            "type": "cactus"
        })


# -------------------- DRAW BACKGROUND --------------------

def draw_background():

    global road_offset

    # Desert sand
    screen.fill(SAND)

    # Alternating sandy patches
    for y in range(-100, HEIGHT + 100, 140):
        patch_y = (y + road_offset // 2) % (HEIGHT + 140) - 70

        pygame.draw.ellipse(
            screen, LIGHT_SAND,
            (5, patch_y, 55, 28)
        )

        pygame.draw.ellipse(
            screen, DARK_SAND,
            (438, patch_y + 40, 48, 23)
        )

    # Road surface
    pygame.draw.rect(
        screen, ROAD,
        (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT)
    )

    # Road shoulders
    pygame.draw.rect(
        screen, ROAD_EDGE,
        (ROAD_LEFT, 0, 7, HEIGHT)
    )
    pygame.draw.rect(
        screen, ROAD_EDGE,
        (ROAD_RIGHT - 7, 0, 7, HEIGHT)
    )

    # Road edge warning stripes
    for y in range(-50, HEIGHT, 50):
        stripe_y = (y + road_offset) % (HEIGHT + 50) - 25

        pygame.draw.rect(
            screen, YELLOW,
            (ROAD_LEFT + 9, stripe_y, 4, 25)
        )
        pygame.draw.rect(
            screen, YELLOW,
            (ROAD_RIGHT - 13, stripe_y, 4, 25)
        )

    # Dashed lane markings
    for lane_x in [
        ROAD_LEFT + ROAD_WIDTH // 3,
        ROAD_LEFT + 2 * ROAD_WIDTH // 3
    ]:
        for y in range(-80, HEIGHT + 80, 80):
            line_y = (y + road_offset) % (HEIGHT + 80) - 40

            pygame.draw.rect(
                screen, WHITE,
                (lane_x - 2, line_y, 4, 40)
            )

    # Cactus decorations
    for item in scenery:
        draw_cactus(item["x"], item["y"])


# -------------------- MAIN GAME LOOP --------------------

running = True

while running:

    clock.tick(60)

    # Read events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "start":
                if event.key == pygame.K_s:
                    reset_game()
                    game_state = "playing"

            elif game_state == "gameover":
                if event.key == pygame.K_s:
                    reset_game()
                    game_state = "playing"

            elif game_state == "playing":

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player.x -= 100

                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.x += 100

    # -------------------- UPDATE GAME --------------------

    if game_state == "playing":

        # Keep player inside the road
        if player.left < ROAD_LEFT + 8:
            game_state = "gameover"

        if player.right > ROAD_RIGHT - 8:
            game_state = "gameover"

        # Increase score and speed over time
        score += 1

        game_speed = min(5 + score // 500, 13)

        road_offset = (road_offset + game_speed) % 80

        # Move scenery
        for item in scenery:
            item["y"] += game_speed

            if item["y"] > HEIGHT:
                item["y"] = random.randint(-150, -30)
                item["x"] = random.choice([20, 35, 440, 455])

        # Spawn traffic
        spawn_timer += 1

        spawn_interval = max(28, 65 - score // 250)

        if spawn_timer >= spawn_interval:
            spawn_timer = 0

            lane = random.choice(LANES)

            sprite = random.choice(traffic_sprites)

            other_car = {
                "rect": pygame.Rect(0, -90, 42, 72),
                "sprite": sprite
            }

            other_car["rect"].centerx = lane
            traffic.append(other_car)

        # Move traffic
        for other_car in traffic:
            other_car["rect"].y += game_speed

        # Remove traffic that has passed
        traffic = [
            item for item in traffic
            if item["rect"].top < HEIGHT + 100
        ]

        # Collision detection
        for other_car in traffic:
            if player.colliderect(other_car["rect"]):
                game_state = "gameover"
                best_score = max(best_score, score // 10)

    # -------------------- DRAW EVERYTHING --------------------

    draw_background()

    # Draw traffic vehicles
    for other_car in traffic:
        screen.blit(
            other_car["sprite"],
            other_car["rect"]
        )

    # Draw player
    screen.blit(player_sprite, player)

    # Score display
    score_text = small_font.render(
        "SCORE: " + str(score // 10), True, WHITE
    )
    screen.blit(score_text, (15, 15))

    speed_text = small_font.render(
        "SPEED: " + str(game_speed), True, WHITE
    )
    screen.blit(speed_text, (15, 43))

    # -------------------- START SCREEN --------------------

    if game_state == "start":

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((25, 20, 15, 190))
        screen.blit(overlay, (0, 0))

        title = big_font.render("DESERT RACER", True, YELLOW)
        subtitle = font.render("ENDLESS HIGHWAY", True, WHITE)

        instruction = small_font.render(
            "Press S to start", True, WHITE
        )
        controls = small_font.render(
            "A / D or Arrow Keys to steer", True, WHITE
        )

        screen.blit(title, title.get_rect(center=(WIDTH // 2, 260)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 315)))
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, 390)))
        screen.blit(controls, controls.get_rect(center=(WIDTH // 2, 430)))

    # -------------------- GAME OVER SCREEN --------------------

    if game_state == "gameover":

        best_score = max(best_score, score // 10)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 15, 10, 205))
        screen.blit(overlay, (0, 0))

        title = big_font.render("CRASHED!", True, (255, 80, 60))

        final_score = font.render(
            "Score: " + str(score // 10), True, WHITE
        )

        best = small_font.render(
            "Best this session: " + str(best_score), True, YELLOW
        )

        restart = small_font.render(
            "Press S to race again", True, WHITE
        )

        quit_text = small_font.render(
            "Close the window to quit", True, WHITE
        )

        screen.blit(title, title.get_rect(center=(WIDTH // 2, 280)))
        screen.blit(final_score, final_score.get_rect(center=(WIDTH // 2, 345)))
        screen.blit(best, best.get_rect(center=(WIDTH // 2, 390)))
        screen.blit(restart, restart.get_rect(center=(WIDTH // 2, 445)))
        screen.blit(quit_text, quit_text.get_rect(center=(WIDTH // 2, 485)))

    # Update screen
    pygame.display.flip()

pygame.quit()
