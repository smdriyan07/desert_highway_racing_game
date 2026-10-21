
import pygame
import random
import math
from array import array

# ==================================================
# DESERT HIGHWAY - ARCADE EDITION
# Python 3.13 + Pygame 2.6.1
# ==================================================

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

WIDTH = 500
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Desert Highway - Arcade Edition")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------
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

FONT = pygame.font.SysFont("arial", 24, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 17, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 38, bold=True)

ROAD_LEFT = 80
ROAD_RIGHT = 420
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

PLAYER_WIDTH = 42
PLAYER_HEIGHT = 70
PLAYER_SPEED = 6

# ---------------- AUDIO SYSTEM ----------------
# Sounds are created in Python. No audio files needed.

audio_enabled = pygame.mixer.get_init() is not None
sounds = {}
engine_channel = None


def make_tone(frequency, duration, volume=0.4, wave="sine"):
    """Create a short sound from a mathematical waveform."""
    if not audio_enabled:
        return None

    sample_rate = 22050
    sample_count = int(sample_rate * duration)
    samples = array("h")

    for i in range(sample_count):
        t = i / sample_rate
        envelope = min(1.0, i / 250, (sample_count - i) / 500)
        envelope = max(0.0, envelope)

        if wave == "square":
            value = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
        elif wave == "noise":
            value = random.uniform(-1.0, 1.0)
        else:
            value = math.sin(2 * math.pi * frequency * t)

        samples.append(int(32767 * volume * envelope * value))

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


def create_engine_sound():
    """Create a looping, low engine-like sound."""
    if not audio_enabled:
        return None

    sample_rate = 22050
    samples = array("h")

    for i in range(sample_rate // 2):
        t = i / sample_rate
        value = (
            math.sin(2 * math.pi * 75 * t) * 0.55
            + math.sin(2 * math.pi * 115 * t) * 0.25
            + random.uniform(-0.2, 0.2)
        )
        samples.append(int(32767 * 0.20 * value))

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


if audio_enabled:
    sounds["coin"] = make_tone(1100, 0.12, 0.45)
    sounds["coin2"] = make_tone(1500, 0.16, 0.40)
    sounds["nitro"] = make_tone(180, 0.50, 0.55, "square")
    sounds["shield"] = make_tone(650, 0.35, 0.40)
    sounds["crash"] = make_tone(90, 0.55, 0.65, "noise")
    sounds["start"] = make_tone(500, 0.25, 0.35)
    sounds["engine"] = create_engine_sound()


def play_sound(name):
    sound = sounds.get(name)
    if sound is not None:
        try:
            sound.play()
        except pygame.error:
            pass


# ---------------- GAME OBJECTS ----------------
player = pygame.Rect(
    WIDTH // 2 - PLAYER_WIDTH // 2,
    HEIGHT - 115,
    PLAYER_WIDTH,
    PLAYER_HEIGHT
)

traffic = []
pickups = []
particles = []
speed_lines = []

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

shake_timer = 0
flash_timer = 0
game_state = "menu"


# ---------------- TEXT HELPER ----------------
def draw_text(text, font, color, x, y, center=True):
    image = font.render(str(text), True, color)

    if center:
        screen.blit(image, image.get_rect(center=(x, y)))
    else:
        screen.blit(image, (x, y))


# ---------------- PARTICLE EFFECTS ----------------
def create_particles(x, y, color, amount=18):
    """Create sparks or sparkles at a position."""
    for _ in range(amount):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.0, 5.0)
        lifetime = random.randint(15, 35)

        particles.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": lifetime,
            "max_life": lifetime,
            "color": color,
            "size": random.randint(2, 5)
        })


def update_particles():
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["vx"] *= 0.96
        particle["vy"] *= 0.96
        particle["life"] -= 1

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_particles():
    for particle in particles:
        size = max(1, int(
            particle["size"] *
            particle["life"] / particle["max_life"]
        ))

        pygame.draw.circle(
            screen,
            particle["color"],
            (int(particle["x"]), int(particle["y"])),
            size
        )


# ---------------- CAR SPRITES ----------------
def draw_car(rect, color, is_player=False):
    # Wheels
    for wheel_y in (rect.y + 12, rect.y + 43):
        pygame.draw.rect(
            screen, BLACK,
            (rect.x - 4, wheel_y, 7, 17),
            border_radius=3
        )
        pygame.draw.rect(
            screen, BLACK,
            (rect.right - 3, wheel_y, 7, 17),
            border_radius=3
        )

    pygame.draw.rect(screen, color, rect, border_radius=9)

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

    # Headlights
    pygame.draw.rect(
        screen, WHITE,
        (rect.x + 5, rect.y + 3, 8, 5),
        border_radius=2
    )
    pygame.draw.rect(
        screen, WHITE,
        (rect.right - 13, rect.y + 3, 8, 5),
        border_radius=2
    )

    # Tail lights
    pygame.draw.rect(
        screen, RED,
        (rect.x + 5, rect.bottom - 7, 8, 4)
    )
    pygame.draw.rect(
        screen, RED,
        (rect.right - 13, rect.bottom - 7, 8, 4)
    )

    if is_player:
        # Nitro flames
        if nitro_timer > 0:
            for flame_x in (rect.x + 10, rect.right - 10):
                flame_length = random.randint(12, 26)

                points = [
                    (flame_x - 5, rect.bottom - 3),
                    (flame_x + 5, rect.bottom - 3),
                    (flame_x, rect.bottom + flame_length)
                ]

                pygame.draw.polygon(screen, RED, points)

                inner_points = [
                    (flame_x - 3, rect.bottom - 1),
                    (flame_x + 3, rect.bottom - 1),
                    (flame_x, rect.bottom + flame_length // 2)
                ]

                pygame.draw.polygon(screen, YELLOW, inner_points)

        # Shield glow
        if shield_active:
            pygame.draw.ellipse(
                screen, GREEN,
                (rect.x - 10, rect.y - 10,
                 rect.width + 20, rect.height + 20),
                3
            )


def draw_truck(rect, color):
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
    pygame.draw.rect(screen, color, rect, border_radius=5)
    pygame.draw.rect(
        screen, GLASS,
        (rect.x + 6, rect.y + 7, rect.width - 12, 17),
        border_radius=3
    )
    pygame.draw.rect(
        screen, (80, 85, 90),
        (rect.x + 5, rect.y + 33, rect.width - 10, 10),
        border_radius=2
    )


# ---------------- COINS AND POWER-UPS ----------------
def draw_coin(rect):
    pygame.draw.circle(screen, (180, 115, 0), rect.center, 13)
    pygame.draw.circle(screen, GOLD, rect.center, 10)
    pygame.draw.circle(screen, (255, 230, 100), rect.center, 7)
    draw_text("$", SMALL_FONT, (155, 95, 0),
              rect.centerx, rect.centery)


def draw_pickup(item):
    rect = item["rect"]
    kind = item["kind"]

    if kind == "coin":
        draw_coin(rect)

    elif kind == "nitro":
        pygame.draw.circle(screen, PURPLE, rect.center, 16)
        pygame.draw.circle(screen, (225, 190, 255), rect.center, 12)

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
        pygame.draw.circle(screen, (180, 255, 195), rect.center, 12)

        points = [
            (rect.centerx, rect.y + 4),
            (rect.x + 6, rect.y + 8),
            (rect.x + 8, rect.y + 18),
            (rect.centerx, rect.bottom - 3),
            (rect.right - 8, rect.y + 18),
            (rect.right - 6, rect.y + 8)
        ]

        pygame.draw.polygon(screen, (20, 145, 65), points)


# ---------------- BACKGROUND ----------------
def draw_background():
    screen.fill(SAND)

    # Desert dunes
    pygame.draw.ellipse(screen, DARK_SAND, (-100, 80, 260, 170))
    pygame.draw.ellipse(screen, (230, 199, 135), (320, 240, 270, 190))
    pygame.draw.ellipse(screen, (202, 165, 98), (-120, 440, 280, 200))

    # Road
    pygame.draw.rect(
        screen, ROAD,
        (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT)
    )

    pygame.draw.rect(
        screen, YELLOW,
        (ROAD_LEFT, 0, 5, HEIGHT)
    )
    pygame.draw.rect(
        screen, YELLOW,
        (ROAD_RIGHT - 5, 0, 5, HEIGHT)
    )

    # Moving lane markings
    dash_height = 40
    gap = 30

    for lane_x in (
        ROAD_LEFT + ROAD_WIDTH // 3,
        ROAD_LEFT + 2 * ROAD_WIDTH // 3
    ):
        for y in range(-dash_height, HEIGHT, dash_height + gap):
            draw_y = (y + road_offset) % (HEIGHT + dash_height)

            pygame.draw.rect(
                screen, ROAD_LINE,
                (lane_x - 3, draw_y, 6, dash_height)
            )

    # Cacti
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


# ---------------- SPAWNING ----------------
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
        lane_x - width // 2, -height, width, height
    )

    for vehicle in traffic:
        if abs(vehicle["rect"].centerx - rect.centerx) < 55:
            if vehicle["rect"].y < 120:
                return

    traffic.append({
        "rect": rect,
        "color": random.choice([
            RED, (240, 145, 30), (230, 230, 230),
            (235, 90, 155), (80, 200, 190)
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

    pickups.append({
        "rect": pygame.Rect(x - size // 2, -size, size, size),
        "kind": kind
    })


# ---------------- RESET GAME ----------------
def reset_game():
    global traffic, pickups, particles, speed_lines
    global score, coins, game_speed, road_offset
    global traffic_timer, pickup_timer
    global shield_active, nitro_timer, nitro_bonus_pending
    global shake_timer, flash_timer, player, game_state

    traffic = []
    pickups = []
    particles = []
    speed_lines = []

    score = 0
    coins = 0
    game_speed = 5
    road_offset = 0

    traffic_timer = 0
    pickup_timer = 0

    shield_active = False
    nitro_timer = 0
    nitro_bonus_pending = False

    shake_timer = 0
    flash_timer = 0

    player.x = WIDTH // 2 - PLAYER_WIDTH // 2
    player.y = HEIGHT - 115

    game_state = "playing"
    play_sound("start")


# ---------------- ENGINE AUDIO ----------------
def update_engine_sound():
    global engine_channel

    if not audio_enabled:
        return

    engine = sounds.get("engine")

    if engine is None:
        return

    if game_state == "playing":
        if engine_channel is None or not engine_channel.get_busy():
            engine_channel = engine.play(loops=-1)

        if engine_channel is not None:
            volume = 0.12 if nitro_timer > 0 else 0.045
            engine_channel.set_volume(volume)

    else:
        if engine_channel is not None:
            engine_channel.stop()
            engine_channel = None


# ---------------- MAIN LOOP ----------------
running = True

while running:
    clock.tick(FPS)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if game_state in ("menu", "game_over"):
                if event.key in (
                    pygame.K_s, pygame.K_RETURN, pygame.K_SPACE
                ):
                    reset_game()

    keys = pygame.key.get_pressed()

    # ---------------- GAME UPDATE ----------------
    if game_state == "playing":
        game_speed = min(5 + score // 500, 13)
        current_speed = game_speed

        # Nitro boost
        if nitro_timer > 0:
            current_speed += 4
            nitro_timer -= 1

            # Bonus for surviving the full boost
            if nitro_timer == 0 and nitro_bonus_pending:
                score += 100
                nitro_bonus_pending = False
                create_particles(
                    player.centerx, player.centery, GOLD, 25
                )
                play_sound("coin2")

        # Player movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= PLAYER_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += PLAYER_SPEED

        player.left = max(ROAD_LEFT + 8, player.left)
        player.right = min(ROAD_RIGHT - 8, player.right)

        # Road movement
        road_offset = (road_offset + current_speed) % 70

        # Nitro speed streaks
        if nitro_timer > 0:
            if random.random() < 0.65:
                speed_lines.append({
                    "x": random.randint(ROAD_LEFT + 10, ROAD_RIGHT - 10),
                    "y": -20,
                    "length": random.randint(12, 35)
                })

        for line in speed_lines[:]:
            line["y"] += current_speed + 5

            if line["y"] > HEIGHT:
                speed_lines.remove(line)

        # Spawn traffic
        traffic_timer += 1
        spawn_interval = max(25, 65 - score // 250)

        if traffic_timer >= spawn_interval:
            spawn_traffic()
            traffic_timer = 0

        # Spawn pickups
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
                    create_particles(
                        item["rect"].centerx,
                        item["rect"].centery,
                        GOLD, 14
                    )
                    play_sound("coin")

                elif kind == "nitro":
                    nitro_timer = FPS * 3
                    nitro_bonus_pending = True
                    create_particles(
                        player.centerx, player.centery,
                        PURPLE, 20
                    )
                    play_sound("nitro")

                elif kind == "shield":
                    shield_active = True
                    create_particles(
                        player.centerx, player.centery,
                        GREEN, 20
                    )
                    play_sound("shield")

                pickups.remove(item)

        # Traffic collisions
        for vehicle in traffic[:]:
            if player.colliderect(vehicle["rect"]):
                if shield_active:
                    shield_active = False
                    traffic.remove(vehicle)
                    score += 50

                    create_particles(
                        vehicle["rect"].centerx,
                        vehicle["rect"].centery,
                        GREEN, 28
                    )

                    flash_timer = 5
                    play_sound("shield")

                else:
                    best_score = max(best_score, score)

                    create_particles(
                        player.centerx, player.centery,
                        RED, 45
                    )

                    shake_timer = 14
                    flash_timer = 10
                    play_sound("crash")
                    game_state = "game_over"

                break

        score += 1

    # Update particles even after a crash
    update_particles()

    if shake_timer > 0:
        shake_timer -= 1

    if flash_timer > 0:
        flash_timer -= 1

    update_engine_sound()

    # ---------------- DRAW ----------------
    draw_background()

    # Speed streaks during nitro
    if game_state == "playing" and nitro_timer > 0:
        for line in speed_lines:
            pygame.draw.line(
                screen, (255, 245, 190),
                (line["x"], line["y"]),
                (line["x"], line["y"] + line["length"]),
                2
            )

    # Traffic
    for vehicle in traffic:
        if vehicle["truck"]:
            draw_truck(vehicle["rect"], vehicle["color"])
        else:
            draw_car(vehicle["rect"], vehicle["color"])

    # Power-ups
    for item in pickups:
        draw_pickup(item)

    # Player
    if game_state == "playing":
        draw_car(player, BLUE, is_player=True)

    # Sparks and particles
    draw_particles()

    # HUD
    if game_state == "playing":
        pygame.draw.rect(
            screen, (20, 25, 30),
            (8, 8, 205, 100),
            border_radius=10
        )

        draw_text(
            f"Score: {score}", SMALL_FONT, WHITE,
            20, 15, center=False
        )

        draw_text(
            f"Coins: {coins}", SMALL_FONT, GOLD,
            20, 40, center=False
        )

        if shield_active:
            status = "SHIELD: READY"
            status_color = GREEN
        elif nitro_timer > 0:
            status = f"NITRO: {math.ceil(nitro_timer / FPS)}s"
            status_color = PURPLE
        else:
            status = "Collect power-ups!"
            status_color = WHITE

        draw_text(
            status, SMALL_FONT, status_color,
            20, 65, center=False
        )

        draw_text(
            f"Speed: {game_speed}", SMALL_FONT,
            WHITE, WIDTH - 70, 25
        )

    # Start menu
    if game_state == "menu":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        screen.blit(overlay, (0, 0))

        draw_text("DESERT HIGHWAY", BIG_FONT, GOLD, 250, 190)
        draw_text("ARCADE EDITION", FONT, WHITE, 250, 235)

        draw_text("Sound + Visual Effects!", SMALL_FONT,
                  (255, 220, 150), 250, 290)

        draw_text("GOLD COIN = +25 POINTS", SMALL_FONT,
                  GOLD, 250, 340)
        draw_text("PURPLE ORB = NITRO BOOST", SMALL_FONT,
                  (220, 160, 255), 250, 375)
        draw_text("GREEN ORB = ONE CRASH SHIELD", SMALL_FONT,
                  GREEN, 250, 410)

        draw_text("A / D or LEFT / RIGHT to drive",
                  SMALL_FONT, WHITE, 250, 475)

        draw_text("Press S, ENTER or SPACE",
                  FONT, YELLOW, 250, 535)
        draw_text("to start racing!", FONT, YELLOW, 250, 570)

        if not audio_enabled:
            draw_text("Audio unavailable - game still works",
                      SMALL_FONT, WHITE, 250, 635)

    # Game over screen
    elif game_state == "game_over":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        draw_text("CRASH!", BIG_FONT, RED, 250, 230)
        draw_text(f"Final Score: {score}", FONT, WHITE, 250, 300)
        draw_text(f"Coins Collected: {coins}", FONT, GOLD, 250, 340)

        draw_text(
            f"Best This Session: {best_score}",
            SMALL_FONT, WHITE, 250, 385
        )

        draw_text("Press S, ENTER or SPACE",
                  FONT, YELLOW, 250, 465)
        draw_text("to race again!", FONT, YELLOW, 250, 505)

    # Screen flash on crash or shield collision
    if flash_timer > 0:
        if flash_timer % 2 == 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 65))
            screen.blit(flash, (0, 0))

    # Small screen shake
    if shake_timer > 0:
        frame = screen.copy()
        screen.fill(BLACK)

        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-4, 4)

        screen.blit(frame, (offset_x, offset_y))

    pygame.display.flip()

pygame.quit()
