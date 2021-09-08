from utils import SpriteSheet
from pygame.rect import Rect


class Mario:
    def __init__(self):
        block_wh = 40
        small_sprite_wh = 16
        big_sprite_wh = 32

        mario_sprites = SpriteSheet('sprites/mario.png')
        self._mario_standing_l =\
            mario_sprites.image_at(Rect(block_wh * 3, block_wh * 0, small_sprite_wh, small_sprite_wh))

    def get_standing(self):
        return self._mario_standing_l
