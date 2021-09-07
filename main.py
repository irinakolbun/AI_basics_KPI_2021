import pygame
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

try:
    screen = pygame.display.set_mode((512, 480))
    # This should show a blank 200 by 200 window centered on the screen
    pygame.display.flip()
    pygame.display.set_caption("Donkey Kong")

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            break
finally:
    pygame.quit()  # Keep this IDLE friendly
