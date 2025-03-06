import pygame
import random
import os
import sys

# Initialize pygame with error handling
try:
    pygame.init()
except pygame.error as e:
    print(f"Failed to initialize pygame: {e}")
    sys.exit(1)

# Game Constants
WIDTH, HEIGHT = 400, 600
TILE_WIDTH, TILE_HEIGHT = 100, 150
FPS = 60
BACKGROUND_COLOR = (200, 230, 250)
TILE_COLOR = (50, 50, 50)

# Create the game window
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rhythmic Tap Game")
    clock = pygame.time.Clock()
except pygame.error as e:
    print(f"Failed to create game window: {e}")
    pygame.quit()
    sys.exit(1)

# Load Sounds with error handling
try:
    pygame.mixer.init()
    # Check if sound file exists, if not create a default sound
    if not os.path.exists("tap.wav"):
        print("tap.wav not found, using default sound")
        # Create a simple beep sound
        pygame.mixer.Sound(bytes([128] * 44100))  # 1 second beep
        tap_sound = pygame.mixer.Sound(bytes([128] * 44100))
    else:
        tap_sound = pygame.mixer.Sound("tap.wav")
except pygame.error as e:
    print(f"Sound initialization failed: {e}")
    tap_sound = None

def create_tiles():
    return [{'x': random.choice([0, 100, 200, 300]), 'y': -TILE_HEIGHT}]

tiles = create_tiles()
speed = 5
score = 0
running = True

while running:
    screen.fill(BACKGROUND_COLOR)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            for tile in tiles:
                if tile['x'] < x < tile['x'] + TILE_WIDTH and tile['y'] < y < tile['y'] + TILE_HEIGHT:
                    tiles.remove(tile)
                    tiles.append({'x': random.choice([0, 100, 200, 300]), 'y': -TILE_HEIGHT})
                    if tap_sound:
                        pygame.mixer.Sound.play(tap_sound)
                    score += 1
                    break
    
    for tile in tiles:
        pygame.draw.rect(screen, TILE_COLOR, (tile['x'], tile['y'], TILE_WIDTH, TILE_HEIGHT))
        tile['y'] += speed
        if tile['y'] > HEIGHT:
            tiles.remove(tile)
            tiles.append({'x': random.choice([0, 100, 200, 300]), 'y': -TILE_HEIGHT})

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
