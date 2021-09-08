import pygame


class Level:
    def __init__(self, level: int):
        self._bridge_sprite = pygame.image.load('sprites/bridge.png').convert_alpha()
        self._level = self._generate(level)

    def _generate(self, level):
        surface = pygame.surface.Surface((256, 240))

        # box
        for i in range(32):
            surface.blit(pygame.transform.rotate(self._bridge_sprite, 90), (0, i*8))
            surface.blit(self._bridge_sprite, (i * 8, 0))
            surface.blit(pygame.transform.rotate(self._bridge_sprite, -90), (256-8, i * 8))

        # first floor
        for i in range(2, 16):
            surface.blit(self._bridge_sprite, (i*8, 240-8))

        j = 1
        for i in range(16, 30):
            if not i % 2:
                j += 1
            surface.blit(self._bridge_sprite, (i * 8, 240 - 8 - j))

        # even floors
        for floor in range(1, 3):
            j = 1
            for i in range(4, 30):
                if not i % 2:
                    j += 1
                surface.blit(self._bridge_sprite, (i*8, 240-8-j-(floor * 64)))

        # odd floors
        for floor in range(3):
            j = 0
            for i in range(27, 1, -1):
                if i % 2:
                    j += 1
                surface.blit(self._bridge_sprite, (i*8, 240-8-32-j-(floor * 64)))


        return surface

    def get_level(self):
        return self._level
