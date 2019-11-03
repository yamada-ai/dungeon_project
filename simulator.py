import random

from Room import Room
from Agent import Friend, Enemy
from Dungeon import Dungeon, CellInfo
from util import FOUR_DIRECTION_VECTOR
from heapq import heappush, heappop
import numpy as np


class Simulator:
    def __init__(self, row=30, column=40):
        self.dungeon = Dungeon(row, column)
        self.is_end = False
        first_room: Room = random.choice(self.dungeon.rooms)
        first_room_map = self.dungeon.floor_map[
                         first_room.origin[0]:first_room.origin[0] + first_room.size[0],
                         first_room.origin[1]:first_room.origin[1] + first_room.size[1]]
        index = random.choice(np.where(first_room_map.reshape(-1) == CellInfo.ROOM)[0])
        y = int(index / first_room_map.shape[1] + first_room.origin[0])
        x = int(index % first_room_map.shape[1] + first_room.origin[1])
        self.friend_agent = Friend(y, x, first_room.id)

        # 保護解除したマップ
        self.map = self.dungeon.floor_map.copy()
        self.map[self.map == CellInfo.PROTECTED] = CellInfo.ROOM
        self.map[self.map == CellInfo.ENEMY] = CellInfo.ROOM

        self.enemy_list = []
        self.load_enemy(first_room.id)

    def action(self, action):
        before_point = (self.friend_agent.x, self.friend_agent.y)

        if action == 0:
            for v in FOUR_DIRECTION_VECTOR:
                x = self.friend_agent.x + v[0]
                y = self.friend_agent.y + v[1]
                e = [enemy for enemy in self.enemy_list if enemy.x == x and enemy.y == y]
                if len(e) >= 1:
                    self.enemy_list.remove(e[0])
                    break
        elif action == 1:
            self.friend_agent.y -= 1
        elif action == 2:
            self.friend_agent.x += 1
        elif action == 3:
            self.friend_agent.y += 1
        elif action == 4:
            self.friend_agent.x -= 1

        if self.map[self.friend_agent.y][self.friend_agent.x] == CellInfo.WALL:
            self.friend_agent.x = before_point[0]
            self.friend_agent.y = before_point[1]

        self.enemy_action()

        if self.map[self.friend_agent.y][self.friend_agent.x] == CellInfo.ROAD:
            road = [road for road in self.dungeon.rooms[self.friend_agent.room_id].roads if
                    (self.friend_agent.x, self.friend_agent.y) in road.ends][0]
            end_position = [end for end in road.ends if end != (self.friend_agent.x, self.friend_agent.y)][0]
            for v in FOUR_DIRECTION_VECTOR:
                if self.map[end_position[1] + v[1], end_position[0] + v[0]] == CellInfo.ROOM:
                    self.friend_agent.x = end_position[0] + v[0]
                    self.friend_agent.y = end_position[1] + v[1]
                    self.friend_agent.room_id = \
                        [room for room in road.connected_rooms if room.id != self.friend_agent.room_id][0].id
                    break
            self.load_enemy(self.friend_agent.room_id)

    # 部屋の敵をロード
    def load_enemy(self, room_id):
        self.enemy_list.clear()
        for enemy_position in self.dungeon.rooms[room_id].initial_enemy_positions:
            self.enemy_list.append(Enemy(enemy_position[0], enemy_position[1]))

    def enemy_action(self):
        enemy_positions = set()
        for enemy in self.enemy_list:
            action_candidates = self.search(enemy.x, enemy.y)
            next_position_list = []
            next_next_position_list = []
            distance = 1000000
            for _ in range(len(action_candidates)):
                action_candidate = heappop(action_candidates)
                if action_candidate[0] == 0:
                    self.is_end = True
                    return
                else:
                    next_position = (action_candidate[1], action_candidate[2])
                    if action_candidate[0] > distance:
                        next_next_position_list.append(next_position)
                        continue
                    distance = action_candidate[0]
                    if next_position in enemy_positions:
                        continue
                    next_position_list.append(next_position)
            if next_position_list:
                next_position = random.choice(next_position_list)
            else:
                print('skip')
                next_position = random.choice(next_next_position_list)
            enemy.x = next_position[0]
            enemy.y = next_position[1]
            enemy_positions.add(next_position)

    def search(self, x, y):
        list_ = []
        for v in FOUR_DIRECTION_VECTOR:
            x2 = x + v[0]
            y2 = y + v[1]
            if self.map[y2][x2] != CellInfo.ROOM:
                continue
            distance = abs(self.friend_agent.x - x2) + abs(self.friend_agent.y - y2)
            heappush(list_, (distance, x2, y2))
        return list_

    def dump2json(self):
        return {
            'map': [[e.value for e in line] for line in self.map],
            'isEnd': self.is_end,
            'agent': {
                'x': self.friend_agent.x,
                'y': self.friend_agent.y,
            },
            'enemies': [{'x': enemy.x, 'y': enemy.y} for enemy in self.enemy_list]
        }
