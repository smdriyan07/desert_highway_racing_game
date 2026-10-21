
import pygame

print("1. Starting Pygame...", flush=True)
pygame.init()

print("2. Pygame initialized:", pygame.get_init(), flush=True)
print("3. Video driver:", pygame.display.get_driver(), flush=True)

print("4. Opening window...", flush=True)
screen = pygame.display.set_mode((500, 400))

print("5. Window created!", flush=True)

screen.fill((30, 140, 60))

font = pygame.font.Font(None, 36)
message = font.render("Pygame is working!", True, (255, 255, 255))
screen.blit(message, (100, 180))

pygame.display.flip()
print("6. Screen drawn!", flush=True)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(30)

pygame.quit()
print("7. Pygame closed.", flush=True)
