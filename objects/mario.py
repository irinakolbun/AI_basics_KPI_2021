from utils import SpriteSheet
from pygame.rect import Rect


class Mario:
    def __init__(self):
        self._small_sprite_wh = 16
        self._big_sprite_wh = 32
        self._sprites = SpriteSheet('sprites/mario.png')

        self._animations = self._init_sprites()
        self._animation_state = 'walk_right'
        self._animation_advance = 0
        self._animation_frame = 0

        self._position = {'x': 0, 'y': 240-16}

    def _get_sprite(self, num, wh):
        block_wh = 40
        return self._sprites.image_at(Rect(block_wh * (num % 8), block_wh * (num // 8), wh, wh))

    def _init_sprites(self):
        return {
            'walk_left': [
                {'sprite': self._get_sprite(2, 16), 'duration': 0.1},
                {'sprite': self._get_sprite(3, 16), 'duration': 0.1},
                {'sprite': self._get_sprite(1, 16), 'duration': 0.1},
                {'sprite': self._get_sprite(3, 16), 'duration': 0.1},
            ],
            'walk_right': [
                {'sprite': self._get_sprite(5, 16), 'duration': 0.1},
                {'sprite': self._get_sprite(4, 16), 'duration': 0.1},
                {'sprite': self._get_sprite(6, 16), 'duration': 0.1},
                {'sprite': self._get_sprite(4, 16), 'duration': 0.1},

            ],
            'stand_left': [
                {'sprite': self._get_sprite(3, 16), 'duration': 0.01},
            ],
            'stand_right': [
                {'sprite': self._get_sprite(4, 16), 'duration': 0.01},
            ],
        }

    def get_cur_sprite(self, advance):
        advance /= 1000

        if self._animations[self._animation_state][self._animation_frame]['duration'] <= self._animation_advance + advance:
            self._animation_advance = max(advance - self._animation_advance, 0)
            self._animation_frame = (self._animation_frame + 1) % len(self._animations[self._animation_state])
        else:
            self._animation_advance += advance
        return self._animations[self._animation_state][self._animation_frame]['sprite']

    def set_sprite(self, sprite_name):
        self._animation_state = sprite_name
        self._animation_frame = 0
        self._animation_advance = 0

    def get_position(self):
        return self._position['x'], self._position['y']
