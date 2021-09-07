import pygame
import os


class GameLoop:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        self._screen = pygame.display.set_mode((512, 480))
        self._clock = pygame.time.Clock()

    def run(self):
        try:
            pygame.display.flip()
            pygame.display.set_caption("Donkey Kong")

            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    break
                self._clock.tick(60)

        finally:
            pygame.quit()
