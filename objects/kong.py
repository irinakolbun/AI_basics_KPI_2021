import pygame
from utils import SpriteSheet
from pygame.rect import Rect
from objects.level import Level
from objects.barrel import Barrel


class Kong:
    def __init__(self, level):
        self._small_sprite_wh = 16
        self._big_sprite_wh = 32
        self._sprites = SpriteSheet('sprites/enemies.png')
        self._barrel_sprite = self._get_sprite(12, 24, 24)
        self._level: Level = level

        self._throwing_1 = self._sprites.image_at(Rect(100, 0, 48, 44))
        self._throwing_1.set_colorkey(0, pygame.RLEACCEL)
        self._throwing_2 = self._sprites.image_at(Rect(200, 48, 48, 48))
        self._throwing_2.set_colorkey(0, pygame.RLEACCEL)
        self._animations = self._init_sprites()

        self._animation_state = 'stand'
        self._animation_advance = 0
        self._animation_frame = 0
        self._position = {'x': 256-64-32, 'y': 24} if not level._level_num % 2 else {'x': 48, 'y': 24}
        self._state = 'stand'

        self._barrel_rate = 15
        self._time_advance = 0
        self._barrel_throw_time = 1.5
        self._barrel_throw_at = 1
        self._max_barrels = 4
        self._is_throwing_barrel = False
        self._barrel_thrown = True

        self._barrels = []

        self._state_transitions = {
        }

    def next_state(self, state):
        self._state_transitions.get((self._state, state),
                                    lambda: print(f'No state transition "{self._state} => {state}"'))()

    def move(self, advance):
        self._barrels = list(filter(lambda x: x.get_position()[1] < 240, self._barrels))
        advance /= 1000

        self._time_advance += advance

        if self._time_advance >= 60 / self._barrel_rate and self._max_barrels > len(self._barrels):
            self._set_sprite('throwing')
            self._is_throwing_barrel = True
            self._barrel_thrown = False
            self._time_advance = 0

        if not self._barrel_thrown and self._time_advance >= self._barrel_throw_at and self._max_barrels > len(self._barrels):
            self._throw_barrel()
            self._barrel_thrown = True

        if self._is_throwing_barrel and self._time_advance >= self._barrel_throw_time:
            self._set_sprite('stand')
            self._is_throwing_barrel = False

    def _throw_barrel(self):
        self._barrels.append(Barrel(self._level))

    def get_cur_sprite(self, advance):
        advance /= 1000
        if self._animations[self._animation_state][self._animation_frame]['duration'] <= self._animation_advance + advance:
            self._animation_advance = max(advance - self._animation_advance, 0)
            self._animation_frame = (self._animation_frame + 1) % len(self._animations[self._animation_state])
        else:
            self._animation_advance += advance
        return self._animations[self._animation_state][self._animation_frame]['sprite']

    def _get_sprite(self, num, wh, block_wh=48):
        return self._sprites.image_at(Rect(block_wh * (num % (288/block_wh)), block_wh * (num // (288/block_wh)), wh, wh), 0)

    def _set_sprite(self, sprite_name):
        self._animation_state = sprite_name
        self._animation_frame = 0
        self._animation_advance = 0

    def get_position(self):
        return self._position['x'], self._position['y']

    def _init_sprites(self):
        return {
            'stand': [
                {'sprite': self._get_sprite(7, 48), 'duration': 0.2},
                {'sprite': self._get_sprite(8, 48), 'duration': 0.2},
                {'sprite': self._get_sprite(9, 48), 'duration': 0.2},
                {'sprite': self._get_sprite(8, 48), 'duration': 0.2},
            ],
            'throwing': [
                {'sprite': self._get_sprite(6, 48) if not self._level._level_num % 2 else self._throwing_2, 'duration': 0.5},
                {'sprite': self._throwing_1, 'duration': 0.5},
                {'sprite': self._throwing_2 if not self._level._level_num % 2 else self._get_sprite(6, 48), 'duration': 0.5},
            ]
        }

    def get_barrels(self):
        return self._barrels
