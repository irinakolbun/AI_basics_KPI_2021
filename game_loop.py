import pygame
import os
from objects.level import Level
from objects.mario import Mario
from objects.kong import Kong

from utils import test_floor


class GameLoop:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        self._screen = pygame.display.set_mode((512, 480), pygame.RESIZABLE)
        self._clock = pygame.time.Clock()
        self._level = Level(4)
        self._mario = Mario(self._level)
        self._kong = Kong()
        self._surface = pygame.surface.Surface((256, 240))
        self._debug_lines = False

    def _key_handler(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
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
            if event.key == pygame.K_SPACE:
                self.__init__()
                self.run()

        elif event.type == pygame.KEYUP:
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

                # update Mario's sprite
                self._mario.move()
                self._surface.blit(self._mario.get_cur_sprite(self._clock.get_time()), self._mario.get_position())

                # debug lines
                if self._debug_lines:
                    for x in range(8, 240-8):
                        for y in range(240):
                            if test_floor({'x': x, 'y': y}):
                                pygame.draw.line(self._surface, 'orange', (x+8, y+16), (x+8, y+16))
                    mario_pos = list(self._mario.get_position())
                    mario_pos[0] += 8
                    mario_pos[1] += 16
                    pygame.draw.line(self._surface, 'red', mario_pos, mario_pos)
                    ladders = self._level.get_ladders()
                    for ladder in ladders:
                        pygame.draw.line(self._surface, 'green', (ladder['x'], ladder['y_start']+16), (ladder['x'], ladder['y_end']+16))
                        pygame.draw.line(self._surface, 'green', (ladder['x']+7, ladder['y_start']+16), (ladder['x']+7, ladder['y_end']+16))


                # copy buffer contents to screen
                self._screen.blit(pygame.transform.scale(self._surface, self._screen.get_rect().size), (0, 0))
                pygame.display.flip()
                self._clock.tick(60)

        finally:
            pygame.quit()
