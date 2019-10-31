import random

from Agent import Friend
from Dungeon import Dungeon
import numpy as np


class Simulator:
    def __init__(self, row=30, column=40):
        self.dungeon = Dungeon(row, column)
        index = random.choice(np.where(self.dungeon.floor_map.reshape(-1) == 1)[0])
        self.fried_agent = Friend(int(index/self.dungeon.floor_map.shape[1]), int(index%self.dungeon.floor_map.shape[1]))

    def action(self, action):
        if action == 0:
            pass
        elif action == 1:
            self.fried_agent.y -= 1
        elif action == 2:
            self.fried_agent.x += 1
        elif action == 3:
            self.fried_agent.y += 1
        elif action == 4:
            self.fried_agent.x -= 1

        print(self.fried_agent)

    def dump2json(self):
        return {
            'map': self.dungeon.dump2json(),
            'agent': {
                'x': self.fried_agent.x,
                'y': self.fried_agent.y,
            }
        }