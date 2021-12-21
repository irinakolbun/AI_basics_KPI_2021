import numpy as np
import gym
import pygame
from gym import spaces
from game_loop import GameLoop


N_ACTIONS = 3


class KongEnv(gym.Env):
    def __init__(self):
        pygame.init()
        super(KongEnv, self).__init__()

        self.game = GameLoop()
        self.action_space = spaces.Discrete(N_ACTIONS)
        self.observation_space = spaces.Box(
            low=0, high=255,
            shape=(149, 49, 3),
            dtype=np.uint8
        )
        self.prev_img = None

    def reset(self):
        self.game.__init__()
        return self.game.current_display_img

    def step(self, action):
        reward, done = self.game.run(action=action)
        return self.game.current_display_img, reward, done, {}

    def render(self, **kwargs):
        pygame.display.flip()
        pygame.event.pump()
        self.game._clock.tick(60)

    def close(self):
        pygame.quit()
