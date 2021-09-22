import random

import pygame
import os
from objects.level import Level
from objects.mario import Mario
from objects.kong import Kong
from search import bfs, dfs, ucs

from utils import test_floor


class GameLoop:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.font.init()
        font = pygame.font.SysFont('Comic Sans MS', 30)
        self._gameover_text = font.render('Game Over!', False, (0xFF, 0xA5, 0x00))
        self._win_text = font.render('Win!', False, (0xFF, 0xA5, 0x00))
        font = pygame.font.SysFont('Comic Sans MS', 24)
        self._space_text = font.render('Press Space to restart', False, (0xFF, 0xA5, 0x00))

        self._levels = random.choice([2, 3, 4])
        self._screen = pygame.display.set_mode((512, 480), pygame.RESIZABLE)
        self._clock = pygame.time.Clock()
        self._level = Level(self._levels)
        self._mario = Mario(self._level)
        self._kong = Kong(self._level)
        self._surface = pygame.surface.Surface((256, 240))
        self._debug_lines = False
        self._search_mode = 0
        self._running = True

    def _key_handler(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if self._running:
                if event.key == pygame.K_RIGHT:
                    self._mario.next_state('go_right')
                if event.key == pygame.K_LEFT:
                    self._mario.next_state('go_left')
                if event.key == pygame.K_UP:
                    self._mario.next_state('jump')
                if event.key == pygame.K_DOWN:
                    self._mario.next_state('down')
            if event.key == pygame.K_d:
                self._debug_lines = not self._debug_lines
            if event.key == pygame.K_z:
                self._search_mode = (self._search_mode + 1) % 4
            if event.key == pygame.K_SPACE:
                self.__init__()
                self.run()

        elif event.type == pygame.KEYUP:
            if self._running:
                if event.key == pygame.K_RIGHT:
                    self._mario.next_state('stand')
                if event.key == pygame.K_LEFT:
                    self._mario.next_state('stand')
                if event.key == pygame.K_DOWN:
                    if self._mario.get_moving_state() == 'on_ladder':
                        self._mario.next_state('on_ladder')
                if event.key == pygame.K_UP:
                    if self._mario.get_moving_state() == 'on_ladder':
                        self._mario.next_state('on_ladder')

    def run(self):
        try:
            pygame.display.flip()
            pygame.display.set_caption("Donkey Kong")

            level = self._level.get_level()

            level_map = [['#' for y in range(12)] for x in range(self._levels)]
            for ladder in self._level.get_ladders():
                try:
                    level_map[self._levels - ladder['level'] - 1][ladder['block']] = '|'
                except IndexError:
                    pass
            print('\n'.join(str(x) for x in level_map), self._level.get_ladders(), '\n')
            print(self._level._adj_list)
            print(self._level._weights)

            end = max(self._level._adj_list.keys())
            if (end + 1) % 24 == 0:
                end -= 11

            while True:
                event = pygame.event.wait(10)
                if event.type == pygame.QUIT:
                    break

                if event.type in [pygame.KEYUP, pygame.KEYDOWN]:
                    self._key_handler(event)

                if event.type == pygame.VIDEORESIZE:
                    # There's some code to add back window content here.
                    factor = max(min(round(event.w / 256 * 2) / 2., round(event.h / 240 * 2) / 2.), 1)
                    print(f'resized screen to {factor} factor')
                    self._screen = pygame.display.set_mode((round(256 * factor), round(240 * factor)), pygame.RESIZABLE)

                # draw level
                self._surface.blit(level, (0, 0))

                # update Kong's sprite
                if self._running:
                    self._kong.move(self._clock.get_time())
                self._surface.blit(self._kong.get_cur_sprite(self._clock.get_time()), self._kong.get_position())

                # update barrels
                for barrel in self._kong.get_barrels():
                    if self._running:
                        barrel.move()
                    barrel_pos = barrel.get_position()
                    self._surface.blit(barrel.get_cur_sprite(self._clock.get_time()), barrel_pos)

                    if self._running:
                        if barrel_pos[0] <= mario_pos[0] + 8 <= barrel_pos[0] + 11 \
                            and barrel_pos[1] <= mario_pos[1] + 10 <= barrel_pos[1] + 11:
                            self._running = False
                            level.blit(self._gameover_text, (40, 10))
                            level.blit(self._space_text, (0, 60))
                            self._mario.fail()

                    if self._debug_lines:
                        pygame.draw.line(self._surface, 'white', barrel_pos, (barrel_pos[0] + 11, barrel_pos[1]))
                        pygame.draw.line(self._surface, 'white', barrel_pos, (barrel_pos[0], barrel_pos[1] + 11))
                        pygame.draw.line(self._surface, 'white', (barrel_pos[0] + 11, barrel_pos[1]), (barrel_pos[0] + 11, barrel_pos[1] + 11))
                        pygame.draw.line(self._surface, 'white', (barrel_pos[0], barrel_pos[1] + 11), (barrel_pos[0] + 11, barrel_pos[1] + 11))

                # update Mario's sprite
                if self._running:
                    self._mario.move()
                mario_pos = self._mario.get_position()
                self._surface.blit(self._mario.get_cur_sprite(self._clock.get_time()), mario_pos)

                if (mario_pos, self._levels) in [((224, 74), 4), ((16, 107), 3), ((224, 138), 2),
                                                 ((16, 171), 1)]:
                    self._running = False
                    level.blit(self._win_text, (80, 10))
                    level.blit(self._space_text, (0, 60))

                # debug lines
                if self._debug_lines:
                    for x in range(8, 240-8):
                        for y in range(240):
                            if test_floor({'x': x, 'y': y}):
                                pygame.draw.line(self._surface, 'orange', (x+8, y+16), (x+8, y+16))
                    mario_pos = list(self._mario.get_position())
                    mario_pos[0] += 8
                    mario_pos[1] += 10
                    pygame.draw.line(self._surface, 'green', mario_pos, mario_pos)
                    ladders = self._level.get_ladders()
                    for ladder in ladders:
                        pygame.draw.line(self._surface, 'green', (ladder['x'], ladder['y_start']+16), (ladder['x'], ladder['y_end']+16))
                        pygame.draw.line(self._surface, 'green', (ladder['x']+7, ladder['y_start']+16), (ladder['x']+7, ladder['y_end']+16))

                path = []
                print(self._search_mode)
                if self._search_mode == 1:
                    _, path, weight = bfs(self._level._adj_list, self._mario.get_cur_block(), end, self._level._weights)
                elif self._search_mode == 2:
                    _, path, weight = dfs(self._level._adj_list, self._mario.get_cur_block(), end, self._level._weights)
                elif self._search_mode == 3:
                    _, path, weight = ucs(self._level._adj_list, self._mario.get_cur_block(), end, self._level._weights)

                self._draw_path(path)


                # copy buffer contents to screen
                self._screen.blit(pygame.transform.scale(self._surface, self._screen.get_rect().size), (0, 0))
                pygame.display.flip()
                self._clock.tick(60)

        finally:
            pygame.quit()

    def _get_block_coords(self, block):
        skips = block // 12
        x = 44 + (block % 12) * 16
        # draw line between blocks
        for y in range(240, 0, -1):
            if skips:
                if test_floor({'x': x, 'y': y}):
                    skips -= 1
            if not skips:
                return x - 4 if x - 4 >= 0 else 0, (y - 16) if (y - 16) >= 0 else 0

    def _draw_path(self, path):
        for i in range(len(path) - 1):
            try:
                pygame.draw.line(self._surface, 'yellow', self._get_block_coords(path[i]), self._get_block_coords(path[i+1]))
            except TypeError:
                pass

