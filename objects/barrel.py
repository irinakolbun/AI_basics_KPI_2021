import random

import pygame

from search import a_star_search
from utils import SpriteSheet, test_floor
from pygame.rect import Rect
from objects.level import Level


class Barrel:
    def __init__(self, level):
        self._last_path = []
        self._small_sprite_wh = 16
        self._big_sprite_wh = 32
        self._sprites = SpriteSheet('sprites/enemies.png')
        self._level: Level = level

        self._rolling_1 = self._sprites.image_at(Rect(27, 7, 12, 12))
        self._rolling_1.set_colorkey(0, pygame.RLEACCEL)
        self._rolling_2 = self._sprites.image_at(Rect(27, 27, 12, 12))
        self._rolling_2.set_colorkey(0, pygame.RLEACCEL)

        self._animations = self._init_sprites()
        self._animation_state = 'rolling'
        self._animation_advance = 0
        self._animation_frame = 0

        self._position = {'x': 200, 'y': 64} if not level._level_num % 2 else {'x': 32, 'y': 64}
        self._state = 'stand'
        self._last_state = self._state
        self._walk_speed = 0.8
        self._x_speed = 0
        self._x_advance = 0
        self._direction = True  # right
        self._fall_chance = 0.33

        self._y_speed = 0
        self._y_velocity = 0
        self._y_initial_velocity = 1.4
        self._y_gravity = 0.08
        self._y_advance = 0
        self._move_state = 'run'  # on_ladder

        self._state_transitions = {
        }

    def next_state(self, state):
        self._state_transitions.get((self._state, state),
                                    lambda: print(f'No state transition "{self._state} => {state}"'))()

    def get_moving_state(self):
        return self._move_state

    def get_cur_sprite(self, advance):
        advance /= 1000

        if self._animations[self._animation_state][self._animation_frame]['duration'] <= self._animation_advance + advance:
            self._animation_advance = max(advance - self._animation_advance, 0)
            self._animation_frame = (self._animation_frame + 1) % len(self._animations[self._animation_state])
        else:
            self._animation_advance += advance
        return self._animations[self._animation_state][self._animation_frame]['sprite']

    def move(self, mario_block):
        if self.get_position() == (16, 224):
            self._position['y'] += 1

        for ladder in self._level.get_ladders():
            if self._position['x'] == ladder['x']:
                if ladder['y_end'] - 1 <= self._position['y'] <= ladder['y_end']:
                    path_to_mario = a_star_search(self._level._barrel_adj_list, self.get_cur_block(), mario_block, self._level._barrel_weights)[1]
                    print(path_to_mario)
                    self._last_path = path_to_mario
                    if path_to_mario and len(path_to_mario) > 1:
                        # if random.random() <= self._fall_chance:
                        if abs(path_to_mario[0] - path_to_mario[1]) != 1:
                            self._x_speed = 0
                            self._x_advance = 0
                            self._position['y'] += 2

        # x movement
        self._x_advance += self._x_speed
        if abs(self._x_advance) >= 1:
            if self._x_advance >= 0:
                if not self._position['x'] >= 240 - 16:  # left boundary
                    self._position['x'] += 1
                self._x_advance -= 1
            else:
                if not self._position['x'] <= 16:  # right boundary
                    self._position['x'] -= 1
                self._x_advance += 1

        # y movement
        self._y_advance += self._y_velocity
        if (not (test_floor(self._position) and self._position['y'] >= [171, 138, 107, 74][self._level._level_num - 1])) or (self._y_velocity > 0):
            self._y_velocity -= self._y_gravity
            if abs(self._y_advance) >= 1:
                if self._y_advance >= 0:
                    self._position['y'] -= 1
                    self._y_advance -= 1
                else:
                    self._y_velocity -= self._y_gravity
                    self._position['y'] += 1
                    self._y_advance += 1
                    if test_floor(self._position) and self._position['y'] >= [171, 138, 107, 74][self._level._level_num - 1]:
                        self._state = 'stand'
                        self._direction = self._test_direction()
                        self._y_velocity = 0
                        self._y_advance = 0
                        self._x_speed = self._walk_speed * 1 if self._direction else -1

    def _test_direction(self):
        return (self._position['y'] % 64) >= 32

    def get_position(self):
        return self._position['x'], self._position['y'] + 8

    def _init_sprites(self):
        return {
            'rolling': [
                {'sprite': self._rolling_1, 'duration': 0.1},
                {'sprite': self._rolling_2, 'duration': 0.1},
            ],
        }

    def get_cur_block(self):
        block = (self._position['x'] - 8) // 16 - 1
        if block < 0:
            return 0 + self._get_cur_level() * 12
        elif block > 11:
            return 11 + self._get_cur_level() * 12
        return block + self._get_cur_level() * 12

    def _get_cur_level(self):
        return 0 if self._position['y'] > (240-57) else (240 - (self._position['y'] + 8)) // 32


