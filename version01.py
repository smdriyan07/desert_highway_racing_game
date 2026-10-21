
import pygame
import random

pygame.init()

# Game window
screen = pygame.display.set_mode((500, 700))
pygame.display.set_caption("Endless Car Game")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 28)

# Colours
BLACK = (25, 25, 25)
WHITE = (255, 255, 255)
GREEN = (30, 130, 50)
RED = (220, 40, 40)
BLUE = (40, 100, 230)
YELLOW = (255, 220, 0)
GREY = (90, 90, 90)

# Road boundaries and lanes
road_left = 100
road_right = 400
lane_centres = [150, 250, 350]

# Player car
car = pygame.Rect(230, 560, 40, 70)

# Traffic
traffic = []
traffic_timer = 0

score = 0
road_line_y = 0
game_state = "start"

running = True

while running:

    clock.tick(60)

    # Handle keyboard and window events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "start" and event.key == pygame.K_s:
                game_state = "playing"

            elif game_state == "gameover" and event.key == pygame.K_s:
                car.x = 230
                traffic = []
                traffic_timer = 0
                score = 0
                game_state = "playing"

            elif game_state == "playing":

                if event.key == pygame.K_LEFT:
                    car.x -= 100

                if event.key == pygame.K_RIGHT:
                    car.x += 100

    # Draw background
    screen.fill(GREEN)

    # Draw road
    pygame.draw.rect(screen, GREY, (road_left, 0, 300, 700))

    # Road edges
    pygame.draw.line(screen, WHITE, (road_left, 0),
                     (road_left, 700), 5)
    pygame.draw.line(screen, WHITE, (road_right, 0),
                     (road_right, 700), 5)

    # Moving lane markings
    if game_state == "playing":
        road_line_y += 6

    if road_line_y >= 80:
        road_line_y = 0

    for y in range(-80, 700, 80):
        line_y = y + road_line_y

        pygame.draw.line(screen, YELLOW, (200, line_y),
                         (200, line_y + 40), 4)
        pygame.draw.line(screen, YELLOW, (300, line_y),
                         (300, line_y + 40), 4)

    # Game is running
    if game_state == "playing":

        # Create traffic cars
        traffic_timer += 1

        if traffic_timer >= 45:
            traffic_x = random.choice(lane_centres) - 20
            traffic_car = pygame.Rect(traffic_x, -80, 40, 70)
            traffic.append(traffic_car)
            traffic_timer = 0

        # Move traffic
        for other_car in traffic:
            other_car.y += 6

        # Remove cars that have passed
        traffic = [other_car for other_car in traffic
                   if other_car.y < 750]

        # Increase score
        score += 1

        # Check road boundaries
        if car.left < road_left or car.right > road_right:
            game_state = "gameover"

        # Check collisions
        for other_car in traffic:
            if car.colliderect(other_car):
                game_state = "gameover"

    # Draw player car
    pygame.draw.rect(screen, BLUE, car, border_radius=6)
    pygame.draw.rect(screen, WHITE, (car.x + 7, car.y + 10, 26, 18))

    # Draw traffic cars
    for other_car in traffic:
        pygame.draw.rect(screen, RED, other_car, border_radius=6)
        pygame.draw.rect(
            screen, WHITE,
            (other_car.x + 7, other_car.y + 10, 26, 18)
        )

    # Display score
    score_text = font.render("Score: " + str(score // 10), True, WHITE)
    screen.blit(score_text, (15, 15))

    # Start screen
    if game_state == "start":
        title = font.render("ENDLESS CAR GAME", True, WHITE)
        instruction = small_font.render("Press S to Start", True, WHITE)
        controls = small_font.render("Arrow keys to move", True, WHITE)

        screen.blit(title, (95, 280))
        screen.blit(instruction, (165, 340))
        screen.blit(controls, (155, 375))

    # Game over screen
    if game_state == "gameover":
        message = font.render("GAME OVER", True, WHITE)
        final_score = small_font.render(
            "Your score: " + str(score // 10), True, WHITE
        )
        restart = small_font.render("Press S to Restart", True, WHITE)

        screen.blit(message, (155, 300))
        screen.blit(final_score, (180, 350))
        screen.blit(restart, (160, 390))

    # Update the game window
    pygame.display.flip()

pygame.quit()
