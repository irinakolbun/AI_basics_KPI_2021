import os
import random
from collections import defaultdict

import pygame
from utils import test_floor, SpriteSheet


class Level:
    def __init__(self, level: int):
        print(os.getcwd())
        self._bridge_sprite = pygame.image.load('sprites/bridge.png').convert_alpha()
        self._ladder_sprite = pygame.image.load('sprites/ladder.png').convert_alpha()
        self._barrel_sprite = SpriteSheet('sprites/enemies.png').image_at(pygame.Rect(0, 24, 24, 24), 0).convert_alpha()
        self._ladders = []
        self._adj_list = defaultdict(list)
        self._barrel_adj_list = defaultdict(list)
        self._weights = defaultdict(lambda: float('+inf'))
        self._barrel_weights = defaultdict(lambda: float('+inf'))
        self._level_num = level
        self._level = self._generate(level)

    def _generate(self, level):
        surface = pygame.surface.Surface((256, 240))
        self._ladders.clear()

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
                        self._ladders.append({'x': x, 'y_start': ladder_start, 'y_end': ladder_end, 'level': floor, 'block': (x - 4) // 16 - 2, 'distance': ladder_start - ladder_end})
                        break

        # here we add nodes to the adjacency list and to the weight list
        for i in range((self._level_num + 1) * 12):
            self._barrel_adj_list[i] = [i - 1] if (i % 24) <= 11 else [i + 1]
            self._barrel_weights[(i, i + 1)] = 16
            self._barrel_weights[(i, i - 1)] = 16
            if i % 12 == 0:
                self._adj_list[i] = [i+1]
                self._weights[(i, i+1)] = 16
            elif i % 12 == 11:
                self._adj_list[i] = [i-1]
                self._weights[(i, i-1)] = 16
            else:
                self._adj_list[i] = [i-1, i+1]
                self._weights[(i, i+1)] = 16
                self._weights[(i, i-1)] = 16




        # here we calculate the position of the ladder in the graph and add ladders to adjacency list and weight matrix
        for ladder in self._ladders:
            self._adj_list[ladder['level'] * 12 + ladder['block']].append((ladder['level'] + 1) * 12 + ladder['block'])
            self._weights[(ladder['level'] * 12 + ladder['block'], (ladder['level'] + 1) * 12 + ladder['block'])] = ladder['distance']
            self._weights[((ladder['level'] + 1) * 12 + ladder['block']), ladder['level'] * 12 + ladder['block']] = ladder['distance']

            self._barrel_adj_list[(ladder['level'] + 1) * 12 + ladder['block']].append(ladder['level'] * 12 + ladder['block'])
            self._barrel_weights[(ladder['level'] * 12 + ladder['block'], (ladder['level'] + 1) * 12 + ladder['block'])] = ladder['distance']
            self._barrel_weights[((ladder['level'] + 1) * 12 + ladder['block'], ladder['level'] * 12 + ladder['block'])] = ladder['distance']

        # adding ledges for barrels
        self._barrel_adj_list[23].append(11)
        self._barrel_adj_list[24].append(12)
        self._barrel_adj_list[47].append(35)
        self._barrel_adj_list[48].append(36)
        for i, j in ((0, 23), (23, 24), (24, 47), (47, 48)):
            try:
                self._barrel_adj_list[i].remove(j)
            except:
                pass


        self._barrel_weights[(11, 23)] = 1
        self._barrel_weights[(12, 24)] = 1
        self._barrel_weights[(35, 47)] = 1
        self._barrel_weights[(36, 48)] = 1
        self._barrel_weights[(23, 11)] = 1
        self._barrel_weights[(24, 12)] = 1
        self._barrel_weights[(47, 35)] = 1
        self._barrel_weights[(48, 36)] = 1
        # Kong supports
        for i in range(9):
            surface.blit(self._bridge_sprite, (i * 8 + 139, 24+40) if not self._level_num % 2 else (256 - (i * 8 + 139), 24+40))

        for i in range(2):
            for j in range(2):
                surface.blit(pygame.transform.rotate(self._barrel_sprite, 90), (i*11 + 137, 30+j*15) if not self._level_num % 2 else ((i*11 + 96), 30+j*15))

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
