from utils import SpriteSheet, test_floor
from pygame.rect import Rect
from objects.level import Level


class Mario:
    def __init__(self, level):
        self._small_sprite_wh = 16
        self._big_sprite_wh = 32
        self._sprites = SpriteSheet('sprites/mario.png')
        self._level: Level = level
        self._animations = self._init_sprites()
        self._animation_state = 'stand_right'
        self._animation_advance = 0
        self._animation_frame = 0
        self._animation_direction = 'right'

        # self._position = {'x': 16, 'y': 240-16-8, 'floor': 1}
        self._position = {'x': 16, 'y': 240-24, 'floor': 1}
        self._state = 'stand'
        self._last_state = self._state
        self._walk_speed = 1
        self._climb_speed = 0.5
        self._x_speed = 0
        self._x_advance = 0

        self._y_speed = 0
        self._y_velocity = 0
        self._y_initial_velocity = 1.4
        self._y_gravity = 0.08
        self._y_advance = 0
        self._move_state = 'run'  # on_ladder

        self._state_transitions = {
            ('stand', 'go_right'): self._go_right,
            ('stand', 'go_left'): self._go_left,
            ('stand', 'jump'): self._jump,
            ('go_left', 'jump'): self._jump,
            ('go_right', 'jump'): self._jump,
            ('jump', 'stand'): self._set_stand,
            ('jump', 'go_left'): self._set_go_left,
            ('jump', 'go_right'): self._set_go_right,
            ('go_left', 'go_right'): self._go_right,
            ('go_right', 'go_left'): self._go_left,
            ('go_left', 'stand'): self._stand,
            ('go_right', 'stand'): self._stand,
            ('stand', 'stand'): self._stand,
            ('stand', 'on_ladder'): self._on_ladder,
            ('jump', 'on_ladder'): self._on_ladder,
            ('down', 'on_ladder'): self._on_ladder,
            ('down', 'go_left'): self._go_left,
            ('down', 'go_right'): self._go_right,
            ('on_ladder', 'go_left'): self._go_left,
            ('on_ladder', 'go_right'): self._go_right,
            ('on_ladder', 'down'): self._down,
            ('stand', 'down'): self._down,
            ('go_left', 'down'): self._down,
            ('go_right', 'down'): self._down,
            ('on_ladder', 'jump'): self._jump,
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

    def move(self):
        # x movement
        self._x_advance += self._x_speed
        if abs(self._x_advance) >= 1:
            self._move_state = 'run'
            if self._x_advance >= 0:
                if not self._position['x'] >= 240 - 16:  # left boundary
                    self._position['x'] += 1
                self._x_advance -= 1

            else:
                if not self._position['x'] <= 16:  # right boundary
                    self._position['x'] -= 1
                self._x_advance += 1

        # y movement
        if self._move_state == 'run':
            self._y_advance += self._y_velocity
            if (not test_floor(self._position)) or (self._y_velocity > 0):
                if not test_floor(self._position):
                        pos = self._position.copy()
                        pos['y'] -= 1
                        if test_floor(pos):
                            self._position['y'] -= 1
                            return

                self._y_velocity -= self._y_gravity
                if abs(self._y_advance) >= 1:
                    if self._y_advance >= 0:
                        self._position['y'] -= 1
                        self._y_advance -= 1
                    else:
                        self._y_velocity -= self._y_gravity
                        self._position['y'] += 1
                        self._y_advance += 1
                        if test_floor(self._position):
                            self._state = 'stand'
                            self._y_velocity = 0
                            self._y_advance = 0
                            self.next_state(self._last_state)
        else:
            self._y_advance += self._y_speed
            if abs(self._y_advance) >= 1:
                if self._y_advance >= 0:
                    self._position['y'] -= 1
                    self._y_advance -= 1

                else:
                    self._position['y'] += 1
                    self._y_advance += 1

                if test_floor(self._position):
                    self._y_speed = 0
                    self._y_advance = 0
                    self._move_state = 'run'
                    self._stand()

    def _set_stand(self):
        self._last_state = 'stand'

    def _set_go_left(self):
        self._last_state = 'go_left'

    def _set_go_right(self):
        self._last_state = 'go_right'

    def _stand(self):
        self._x_speed = 0
        self._y_velocity = 0
        self._y_advance = 0
        self._set_sprite('stand_left' if self._animation_direction == 'left' else 'stand_right')
        self._state = 'stand'
        self._last_state = self._state

    def _on_ladder(self):
        self._y_speed = 0
        self._y_advance = 0
        self._state = 'on_ladder'
        self._set_sprite('hanging')

    def _down(self):
        if self._state == 'on_ladder':
            self._y_speed = -self._climb_speed
            self._state = 'down'
        else:
            for ladder in self._level.get_ladders():
                if ladder['y_end'] == self._position['y'] and ladder['x'] - 7 <= self._position['x'] <= ladder['x']:
                    self._position['y'] += 1
                    self._position['x'] = ladder['x'] - 4
                    self._y_speed = -self._climb_speed
                    self._move_state = 'on_ladder'
                    self._state = 'jump'
                    self._set_sprite('climbing')
                    break

    def _go_left(self):
        self._animation_direction = 'left'
        if self._position['x'] <= 16:  # left boundary
            self.next_state('stand')
        else:
            self._set_sprite('walk_left')
            self._x_speed = -self._walk_speed
            self._state = 'go_left'
            self._last_state = self._state

    def _go_right(self):
        self._animation_direction = 'right'
        if self._position['x'] >= 256 - 16:  # right boundary
            self.next_state('stand')
        else:
            self._set_sprite('walk_right')
            self._x_speed = self._walk_speed
            self._state = 'go_right'
            self._last_state = self._state

    def _jump(self):
        if self._move_state == 'run':
            ladder_found = False
            for ladder in self._level.get_ladders():
                if ladder['y_start'] == self._position['y'] and ladder['x'] - 7 <= self._position['x'] <= ladder['x']:
                    self._position['y'] -= 1
                    self._position['x'] = ladder['x'] - 4
                    self._y_speed = self._climb_speed
                    self._move_state = 'on_ladder'
                    ladder_found = True
                    self._state = 'jump'
                    self._set_sprite('climbing')
                    break
            if not ladder_found:
                self._set_sprite('jump_right' if self._animation_direction == 'right' else 'jump_left')
                self._y_velocity = self._y_initial_velocity
                self._state = 'jump'
        elif self._move_state == 'on_ladder':
            self._y_speed = self._climb_speed
            self._state = 'jump'

    def _get_sprite(self, num, wh):
        block_wh = 40
        return self._sprites.image_at(Rect(block_wh * (num % 8), block_wh * (num // 8), wh, wh), 0)

    def _set_sprite(self, sprite_name):
        self._animation_state = sprite_name
        self._animation_frame = 0
        self._animation_advance = 0

    def get_position(self):
        return self._position['x'], self._position['y']

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
            'jump_left': [
                {'sprite': self._get_sprite(1, 16), 'duration': 0.01},
            ],
            'jump_right': [
                {'sprite': self._get_sprite(6, 16), 'duration': 0.01},
            ],
            'hanging': [
                {'sprite': self._get_sprite(11, 16), 'duration': 0.01},
            ],
            'climbing': [
                {'sprite': self._get_sprite(11, 16), 'duration': 0.5},
                {'sprite': self._get_sprite(12, 16), 'duration': 0.5},
            ],
        }
