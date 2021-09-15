import random

import pygame
from utils import test_floor, SpriteSheet


class Level:
    def __init__(self, level: int):
        self._bridge_sprite = pygame.image.load('sprites/bridge.png').convert_alpha()
        self._ladder_sprite = pygame.image.load('sprites/ladder.png').convert_alpha()
        self._barrel_sprite = SpriteSheet('sprites/enemies.png').image_at(pygame.Rect(0, 24, 24, 24), 0).convert_alpha()
        self._ladders = []
        self._level = self._generate(level)

    def _generate(self, level):
        surface = pygame.surface.Surface((256, 240))

        # box
        for i in range(32):
            surface.blit(pygame.transform.rotate(self._bridge_sprite, 90), (0, i * 8))
            surface.blit(self._bridge_sprite, (i * 8, 0))
            surface.blit(pygame.transform.rotate(self._bridge_sprite, -90), (256 - 8, i * 8))

        # ladders
        for floor in range(level):
            for ladders in range(random.choice([1, 2, 3])):
                skips = floor + 1
                x = (random.randint(0, 192) + 32) // 16 * 16 + 4
                for y in range(240, 0, -1):
                    if skips:
                        if test_floor({'x': x, 'y': y}):
                            skips -= 1
                    if not skips:
                        ladder_start = y
                        while not (any(test_floor({'x': x, 'y': y}) for y in range(y - 4, y)) or y <= 0):
                            y -= 4
                            surface.blit(self._ladder_sprite, (x, y + 17))

                        try:
                            ladder_end = next(y for y in ((y if test_floor({'x': x, 'y': y}) else None) for y in range(y - 4, y)) if y is not None)
                        except StopIteration:
                            return self._generate(level)
                        self._ladders.append({'x': x, 'y_start': ladder_start, 'y_end': ladder_end})
                        break

        # Kong supports
        for i in range(9):
            surface.blit(self._bridge_sprite, (i * 8 + 139, 24+40))

        for i in range(2):
            for j in range(2):
                surface.blit(pygame.transform.rotate(self._barrel_sprite, 90), (i*11 + 137, 30+j*15))

        # first floor
        for i in range(2, 16):
            surface.blit(self._bridge_sprite, (i * 8, 240 - 8))

        j = 1
        for i in range(16, 30):
            if not i % 2:
                j += 1
            surface.blit(self._bridge_sprite, (i * 8, 240 - 7 - j))

        # even floors
        for floor in range(1, (level + 2) // 2):
            j = 1
            for i in range(4, 30):
                if not i % 2:
                    j += 1
                surface.blit(self._bridge_sprite, (i * 8, 240 - 8 - j - (floor * 64)))

        # odd floors
        for floor in range((level + 1) // 2):
            j = 0
            for i in range(27, 1, -1):
                if i % 2:
                    j += 1
                surface.blit(self._bridge_sprite, (i * 8, 240 - 8 - 32 - j - (floor * 64)))

        return surface

    def get_level(self):
        return self._level

    def get_ladders(self):
        return self._ladders
