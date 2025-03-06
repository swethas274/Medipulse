import pygame
import time
import pygame.mixer

def render_text(text, timer):
    text_surface = font.render(f"{text}", True, (0, 0, 0))  # Black text
    text_rect = text_surface.get_rect(center=(200, 100))  # Move text higher
    screen.blit(text_surface, text_rect)
    
    timer_surface = timer_font.render(f"{timer}", True, (0, 0, 0))  # Larger Black timer
    timer_rect = timer_surface.get_rect(center=(200, 200))  # Center timer
    screen.blit(timer_surface, timer_rect)

def breathing_cycle():
    pygame.mixer.music.load("breathe_music.mp3")  # Load background music
    pygame.mixer.music.play(-1)  # Loop indefinitely
    
    # Breathe In (4 sec with gradient effect)
    for i in range(1, 41):  # Smooth Expansion
        color = (255 - i * 3, 255, 255)  # Gradient from white to light blue
        screen.fill(color)
        pygame.draw.circle(screen, (173, 216, 230), (200, 200), 50 + i * 3)
        render_text("Breathe In", 4 - i // 10)
        pygame.display.flip()
        time.sleep(0.1)
    
    # Hold (7 sec)
    for t in range(7, 0, -1):
        screen.fill((200, 230, 255))  # Soft blue background
        render_text("Hold...", t)
        pygame.display.flip()
        time.sleep(1)
    
    # Breathe Out (8 sec with gradient effect)
    for i in range(40, 0, -1):  # Smooth Contraction
        color = (255, 230 - i * 3, 230 - i * 3)  # Gradient from blue back to white
        screen.fill(color)
        pygame.draw.circle(screen, (173, 216, 230), (200, 200), 50 + i * 3)
        render_text("Breathe Out", 8 - (40 - i) // 5)
        pygame.display.flip()
        time.sleep(0.1)
    
    # Buffer before restart (2 sec)
    for t in range(2, 0, -1):
        screen.fill((255, 255, 255))
        render_text("Relax...", t)
        pygame.display.flip()
        time.sleep(1)
    
    breathing_cycle()

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Breathing Exercise")
font = pygame.font.Font("Ubuntu-R.ttf", 36)  # Use Ubuntu font with original size
timer_font = pygame.font.Font("Ubuntu-R.ttf", 48)  # Larger font for timer

time.sleep(1)  # Initial delay
breathing_cycle()

pygame.quit()