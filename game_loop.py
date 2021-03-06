import csv
import random
import time

import pygame
import os

from pygame.surfarray import array3d, make_surface

from objects.level import Level
from objects.mario import Mario
from objects.kong import Kong
from search import bfs, dfs, ucs, a_star_search

from utils import test_floor


class GameLoop:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        font = pygame.font.SysFont('Comic Sans MS', 30)
        self._gameover_text = font.render('Game Over!', False, (0xFF, 0xA5, 0x00))
        self._win_text = font.render('Win!', False, (0xFF, 0xA5, 0x00))
        font = pygame.font.SysFont('Comic Sans MS', 24)
        self._info_font = pygame.font.SysFont('Comic Sans MS', 12)
        self._space_text = font.render('Press Space to restart', False, (0xFF, 0xA5, 0x00))
        self._score = 0
        self._levels = 1
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
        self._move_advance = 0
        self._in_cheat_menu = False
        self._cheats_text = ''
        self._god = False

        pygame.display.flip()
        pygame.display.set_caption("Donkey Kong")

        level_map = [['#' for y in range(12)] for x in range(self._levels)]
        for ladder in self._level.get_ladders():
            try:
                level_map[self._levels - ladder['level'] - 1][ladder['block']] = '|'
            except IndexError:
                pass
        print('\n'.join(str(x) for x in level_map), self._level.get_ladders(), '\n')
        print(self._level._adj_list)
        print(self._level._weights)

        self._start = time.time()

    def stats(self, row):
        f = open('stats.csv', 'a', newline='')
        writer = csv.writer(f)
        writer.writerow(row)
        f.close()

    def restart(self):
        self.__init__()
        self.run()

    def _key_handler(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if self._in_cheat_menu:
                if event.key == pygame.K_TAB:
                    self._in_cheat_menu = not self._in_cheat_menu
                elif event.key == pygame.K_BACKSPACE:
                    self._cheats_text = self._cheats_text[:-1]
                elif event.key == pygame.K_RETURN:
                    self._in_cheat_menu = False
                    try:
                        self.handle_cheat()
                    except Exception as e:
                        print(f'Failed to use cheat {self._cheats_text}: {e}')
                else:
                    self._cheats_text += event.unicode
                return

            if event.key == pygame.K_TAB:
                self._in_cheat_menu = not self._in_cheat_menu

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

    def run(self, action=None):
        if action == 0:  # left
            self._mario.next_state('stand')
            self._mario.next_state('go_left')
        elif action == 1:  # right
            self._mario.next_state('stand')
            self._mario.next_state('go_right')
        elif action == 2:  # jump
            self._mario.next_state('stand')
            self._mario.next_state('jump')

        start = self._start
        level = self._level.get_level()
        end = max(self._level._adj_list.keys())
        if (end + 1) % 24 == 0:
            end -= 11

        if time.time() - start > 150:
            self.stats(['loose', round((time.time() - start) * 100) / 100, self._score, 'minimax'])
            return self._score, True
            # self.restart()

        event = pygame.event.wait(10)
        if event.type == pygame.QUIT:
            exit()

        if event.type in [pygame.KEYUP, pygame.KEYDOWN]:
            self._key_handler(event)

        if self._in_cheat_menu:
            pygame.draw.rect(self._surface, (0, 0, 0), pygame.Rect(0, 224, 256, 240))
            self._surface.blit(
                self._info_font.render('> ' + self._cheats_text + '_', False, (0x0, 0xff, 0x00)), (0, 224))
            self._screen.blit(pygame.transform.scale(self._surface, self._screen.get_rect().size), (0, 0))
            return

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

        mario_pos = self._mario.get_position()

        # update barrels
        for barrel in self._kong.get_barrels():
            if self._running:
                barrel.move(self._mario.get_cur_block())
            barrel_pos = barrel.get_position()
            self._surface.blit(barrel.get_cur_sprite(self._clock.get_time()), barrel_pos)

            if self._running and not self._god:
                if barrel_pos[0] <= mario_pos[0] + 8 <= barrel_pos[0] + 11 \
                        and barrel_pos[1] <= mario_pos[1] + 10 <= barrel_pos[1] + 11:
                    self._running = False
                    level.blit(self._gameover_text, (40, 10))
                    level.blit(self._space_text, (0, 60))
                    fin = time.time()
                    self.stats(['loose', round((fin - start) * 100) / 100, self._score, 'minimax'])
                    self._mario.fail()
                    return self._score - 100, True
                    # self.restart()

            if self._debug_lines:
                pygame.draw.line(self._surface, 'white', barrel_pos, (barrel_pos[0] + 11, barrel_pos[1]))
                pygame.draw.line(self._surface, 'white', barrel_pos, (barrel_pos[0], barrel_pos[1] + 11))
                pygame.draw.line(self._surface, 'white', (barrel_pos[0] + 11, barrel_pos[1]),
                                 (barrel_pos[0] + 11, barrel_pos[1] + 11))
                pygame.draw.line(self._surface, 'white', (barrel_pos[0], barrel_pos[1] + 11),
                                 (barrel_pos[0] + 11, barrel_pos[1] + 11))

        # update Mario's sprite
        if self._running:
            self._mario.move()
        self._surface.blit(self._mario.get_cur_sprite(self._clock.get_time()), mario_pos)

        if (mario_pos, self._levels) in [((224, 74), 4), ((16, 107), 3), ((224, 138), 2),
                                         ((16, 171), 1)]:
            self._running = False
            level.blit(self._win_text, (80, 10))
            level.blit(self._space_text, (0, 60))
            fin = time.time()
            self._score += max([0, ((60 * 3 - round((fin - start)))) * 10])
            self.stats(['win', round((fin - start) * 100) / 100, self._score, 'minimax'])
            return self._score, True
        # debug lines
        if self._debug_lines:
            for x in range(8, 240 - 8):
                for y in range(240):
                    if test_floor({'x': x, 'y': y}):
                        pygame.draw.line(self._surface, 'orange', (x + 8, y + 16), (x + 8, y + 16))
            mario_pos = list(self._mario.get_position())
            mario_pos[0] += 8
            mario_pos[1] += 10
            pygame.draw.line(self._surface, 'green', mario_pos, mario_pos)
            ladders = self._level.get_ladders()
            for ladder in ladders:
                pygame.draw.line(self._surface, 'green', (ladder['x'], ladder['y_start'] + 16),
                                 (ladder['x'], ladder['y_end'] + 16))
                pygame.draw.line(self._surface, 'green', (ladder['x'] + 7, ladder['y_start'] + 16),
                                 (ladder['x'] + 7, ladder['y_end'] + 16))

        # here we use the algorithms
        path = []
        text = ''
        if self._search_mode == 1:
            text, path, weight = bfs(self._level._adj_list, self._mario.get_cur_block(), end, self._level._weights)
        elif self._search_mode == 2:
            text, path, weight = dfs(self._level._adj_list, self._mario.get_cur_block(), end, self._level._weights)
        elif self._search_mode == 3:
            text, path, weight = ucs(self._level._adj_list, self._mario.get_cur_block(), end, self._level._weights)
        if text:
            text += f' {weight}px'

        # make Mario move by path
        self._move_advance += self._clock.get_time()

        jumped = False
        for barrel in self._kong.get_barrels():

            if abs(barrel.get_position()[0] - mario_pos[0]) + abs(barrel.get_position()[1] - mario_pos[1] - 8) < 32:
                jumped = True
                self._score += 100 if self._mario._state != 'jump' else 0
                # self._mario.next_state('jump')

                break

        if path and self._move_advance >= 150 and not jumped and False:
            self._move_advance = 0
            try:
                if path[0] - path[1] == -1:
                    self._mario.next_state('stand')
                    self._mario.next_state('go_right')
                elif path[0] - path[1] == 1:
                    self._mario.next_state('stand')
                    self._mario.next_state('go_left')
                elif path[0] - path[1] < 1:
                    if self._mario.get_position()[0] == 16:
                        self._mario.next_state('stand')
                        self._mario.next_state('go_right')
                    else:
                        self._mario.next_state('stand')
                        self._mario.next_state('jump')
                elif path[0] - path[1] > 1:
                    self._mario.next_state('stand')
                    self._mario.next_state('down')
            except IndexError:
                if path[0] == 0:
                    self._mario.next_state('stand')
                    self._mario.next_state('go_left')
                else:
                    self._mario.next_state('stand')
                    self._mario.next_state('go_right')

        # self._draw_path(path)
        for barrel in self._kong.get_barrels():
            pass
            # self._draw_path(barrel._last_path, 'blue')

        self._surface.blit(self._info_font.render(text, False, (0x0, 0xff, 0x00)), (20, 16))

        # for block in range(60):
        #     self._surface.blit(self._info_font.render(str(block), False, (0x0, 0xff, 0x00)), self._get_block_coords(block))

        # copy buffer contents to screen
        self._screen.blit(pygame.transform.scale(self._surface, self._screen.get_rect().size), (0, 0))

        # self._screen.blit(pygame.transform.scale(make_surface(self.current_display_img), self._screen.get_rect().size), (0,0))
        # print(make_surface(self.current_display_img))

        # pygame.quit()
        return self._score, False

    @property
    def current_display_img(self):
        return array3d(pygame.transform.scale(make_surface(array3d(self._surface)[16:-16, 150 + 8:-8, :]),
                                              (int(224 // 1.5), int(74 // 1.5))))

    def _get_block_coords(self, block):
        skips = block // 12 + 1
        x = 44 + (block % 12) * 16
        # draw line between blocks
        for y in range(240, 0, -1):
            if skips:
                if test_floor({'x': x - 8, 'y': y}):
                    skips -= 1
            if not skips:
                return x - 4, y + 16
        return x - 4, 256

    def _draw_path(self, path, color='yellow'):
        for i in range(len(path) - 1):
            try:
                pygame.draw.line(self._surface, color, self._get_block_coords(path[i]),
                                 self._get_block_coords(path[i + 1]))
            except TypeError:
                pass

    def handle_cheat(self):
        if self._cheats_text.startswith('god'):
            self._god = not self._god
        elif self._cheats_text.startswith('mspeed'):
            self._mario._walk_speed = float(self._cheats_text.split(' ', 1)[1])
            self._mario._climb_speed = float(self._cheats_text.split(' ', 1)[1])/2
        elif self._cheats_text.startswith('bcount'):
            self._kong._max_barrels = int(self._cheats_text.split(' ', 1)[1])
        elif self._cheats_text.startswith('brate'):
            self._kong._barrel_rate = int(self._cheats_text.split(' ', 1)[1])
        elif self._cheats_text.startswith('mvelocity'):
            self._mario._y_initial_velocity = int(self._cheats_text.split(' ', 1)[1])
        elif self._cheats_text.startswith('mgravity'):
            self._mario._y_gravity = float(self._cheats_text.split(' ', 1)[1])
        elif self._cheats_text.startswith('tp'):
            self._mario._position = {'x': int(self._cheats_text.split(' ', 2)[1]),
                                     'y': int(self._cheats_text.split(' ', 2)[2])}

        self._cheats_text = ''
