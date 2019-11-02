import random

from Agent import Friend, Enemy
from Dungeon import Dungeon, CellInfo
from util import FOUR_DIRECTION_VECTOR
import numpy as np


class Simulator:
    def __init__(self, row=30, column=40):
        self.dungeon = Dungeon(row, column)
        index = random.choice(np.where(self.dungeon.floor_map.reshape(-1) == CellInfo.ROOM)[0])
        self.fried_agent = Friend(int(index/self.dungeon.floor_map.shape[1]), int(index % self.dungeon.floor_map.shape[1]))

        # 保護解除したマップ
        self.map = self.dungeon.floor_map.copy()
        self.map[self.map == CellInfo.PROTECTED] = CellInfo.ROOM

        self.enemy_list = []
        for room in self.dungeon.rooms:
            for p in room.initial_enemy_positions:
                self.enemy_list.append(Enemy(p[0], p[1]))

    def action(self, action):
        before_point = (self.fried_agent.x, self.fried_agent.y)

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

        if self.map[self.fried_agent.y][self.fried_agent.x] == CellInfo.WALL:
            self.fried_agent.x = before_point[0]
            self.fried_agent.y = before_point[1]

        self.enemy_action()

    def enemy_action(self):
        for enemy in self.enemy_list:
            distance, next_position = self.search(enemy.x, enemy.y)
            enemy.x = next_position[0]
            enemy.y = next_position[1]

    def search(self, x, y):
        list_ = []
        m = 1000000000  # 十分に大きな値
        for v in FOUR_DIRECTION_VECTOR:
            x2 = x + v[0]
            y2 = y + v[1]
            if self.map[y2][x2] != CellInfo.ROOM:
                continue
            distance = abs(self.fried_agent.x - x2) + abs(self.fried_agent.y - y2)
            if distance == m:
                list_.append((x2, y2))
            elif distance < m:
                list_ = [(x2, y2)]
                m = distance
        if list_:
            return m, random.choice(list_)
        return 0, (x, y)

    def dump2json(self):
        return {
            'map': self.dungeon.dump2json(),
            'agent': {
                'x': self.fried_agent.x,
                'y': self.fried_agent.y,
            },
            'enemies': [{'x': enemy.x, 'y': enemy.y} for enemy in self.enemy_list]
        }
