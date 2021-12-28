import pygame

from game_loop import GameLoop

if __name__ == '__main__':
    while True:
        pygame.init()
        pygame.font.init()

        loop = GameLoop()

        while loop._running:
            loop.run()
            pygame.display.flip()
            loop._clock.tick(60)
