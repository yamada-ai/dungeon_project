import json
import datetime
import random

from Room import Room
from Agent import Friend, Enemy
from Dungeon import Dungeon, CellInfo
from util import FOUR_DIRECTION_VECTOR
from heapq import heappush, heappop
import numpy as np


class Simulator:
    def reset(self):
        pass

    def info(self):
        pass

    def action(self, action):
        pass


class RoomGraphSimulator(Simulator):
    def __init__(self, dungeon=None):
        if dungeon is None:
            self.dungeon = Dungeon(30, 40)
        else:
            self.dungeon = dungeon
        self.is_end = False

        # 部屋のグラフを指す隣接行列
        self.map = [[0]*5 for _ in range(5)]
        for road in self.dungeon.roads:
            room1_id = road.connected_rooms[0].id
            room2_id = road.connected_rooms[1].id
            self.map[room1_id][room2_id] = len(road.cells)
            self.map[room2_id][room1_id] = len(road.cells)

        self.goal_room_id = self.dungeon.goal_room_index

        self.first_room_index_candidate = list(range(5))
        self.first_room_index_candidate.remove(self.goal_room_id)
        self.agent_room_id = random.choice(self.first_room_index_candidate)

    def reset(self):
        self.is_end = False
        self.agent_room_id = random.choice(self.first_room_index_candidate)

    def info(self):
        return {
            "roomId": self.agent_room_id,
            "map": self.map
        }

    def action(self, action):
        if self.map[self.agent_room_id][action] == 0:
            return -100
        elif action == self.goal_room_id:
            self.agent_room_id = action
            return 100
        reward = -self.map[self.agent_room_id][action]
        self.agent_room_id = action
        return reward


class CellMoveSimulator(Simulator):
    def __init__(self, param, dungeon=None):
        self.random_enemy = param.get('randomEnemy', False)
        if dungeon is None:
            self.dungeon = Dungeon(30, 40, no_generate_enemy=self.random_enemy)
        else:
            self.dungeon = dungeon
        self.is_end = False
        self.friend_agent: Friend = None
        self.turn = 0

        self.first_room = param.get('firstRoom', None)
        self.no_enemy = param.get('noEnemy', False)
        self.max_turn = param.get('maxTurn', 1500)

        self.map = self.dungeon.floor_map.copy()
        self.map[self.map == CellInfo.PROTECTED] = CellInfo.ROOM
        self.map[self.map == CellInfo.ENEMY] = CellInfo.ROOM

        self.enemy_list = [
            Enemy(-1, -1),
            Enemy(-1, -1)
        ]
        self.reset()

    def reset(self):
        self.is_end = False
        self.turn = 0
        if self.first_room is None or self.first_room < 0:
            first_room: Room = random.choice(self.dungeon.rooms)
        else:
            first_room: Room = self.dungeon.rooms[self.first_room]
        first_room_map = self.dungeon.get_room_map(first_room)
        index = random.choice(np.where(first_room_map.reshape(-1) == CellInfo.ROOM)[0])
        y = int(index / first_room_map.shape[1] + first_room.origin[0])
        x = int(index % first_room_map.shape[1] + first_room.origin[1])
        self.friend_agent = Friend(y, x, first_room.id)
        self._load_enemy(first_room.id)

    def action(self, action):
        self.turn += 1
        next_room_id = -1
        if type(action) == dict:
            next_room_id = action['nextRoomId']
            action = action['action']
        before_point = (self.friend_agent.x, self.friend_agent.y)

        if action == 0:
            for v in FOUR_DIRECTION_VECTOR:
                x = self.friend_agent.x + v[0]
                y = self.friend_agent.y + v[1]
                e = [enemy for enemy in self.enemy_list if enemy.x == x and enemy.y == y]
                if len(e) >= 1:
                    e[0].x = -1
                    e[0].y = -1
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

        if any([(enemy.x, enemy.y) == (self.friend_agent.x, self.friend_agent.y) for enemy in self.enemy_list]):
            self.friend_agent.x = before_point[0]
            self.friend_agent.y = before_point[1]

        self._enemy_action()

        if self.turn > self.max_turn:
            self.is_end = True
            return -100

        if self.is_end:
            return -100

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
            self._load_enemy(self.friend_agent.room_id)
            if self.friend_agent.room_id == next_room_id:
                return 100
            else:
                return -100

        if self.map[self.friend_agent.y][self.friend_agent.x] == CellInfo.GOAL:
            self.is_end = True
            return 100

        return -1

    def _load_enemy(self, room_id):
        if self.no_enemy:
            return
        if self.random_enemy:
            room = self.dungeon.rooms[room_id]
            for e in self.enemy_list:
                room_map = self.dungeon.get_room_map(room)
                index = random.choice(np.where(room_map.reshape(-1) == CellInfo.ROOM)[0])
                y = int(index / room_map.shape[1] + room.origin[0])
                x = int(index % room_map.shape[1] + room.origin[1])
                e.x = x
                e.y = y
        else:
            for p, e in zip(self.dungeon.rooms[room_id].initial_enemy_positions, self.enemy_list):
                e.x = p[0]
                e.y = p[1]

    def _enemy_action(self):
        enemy_positions = set()
        for enemy in self.enemy_list:
            action_candidates = self._search(enemy.x, enemy.y)
            next_position_list = []
            distance = 1000000
            for _ in range(len(action_candidates)):
                action_candidate = heappop(action_candidates)
                if action_candidate[0] == 0:
                    self.is_end = True
                    return
                else:
                    next_position = (action_candidate[1], action_candidate[2])
                    if action_candidate[0] > distance:
                        break
                    distance = action_candidate[0]
                    if next_position in enemy_positions:
                        continue
                    next_position_list.append(next_position)
            if next_position_list:
                next_position = random.choice(next_position_list)
                enemy.x = next_position[0]
                enemy.y = next_position[1]
                enemy_positions.add(next_position)

    def _search(self, x, y):
        list_ = []
        for v in FOUR_DIRECTION_VECTOR:
            x2 = x + v[0]
            y2 = y + v[1]
            if self.map[y2][x2] != CellInfo.ROOM:
                continue
            distance = abs(self.friend_agent.x - x2) + abs(self.friend_agent.y - y2)
            heappush(list_, (distance, x2, y2))
        return list_

    def info(self):
        agent_position_inner_room = self._get_agent_position_inner_room()
        return {
            "isEnd": self.is_end,
            "roomId": self.friend_agent.room_id,
            "x": agent_position_inner_room[0],
            "y": agent_position_inner_room[1],
            "enemies": [
                {
                    "x": max(e.x - self.dungeon.rooms[self.friend_agent.room_id].origin[1], -1),
                    "y": max(e.y - self.dungeon.rooms[self.friend_agent.room_id].origin[0], -1),
                } for e in self.enemy_list
            ],
            "map": {
                "cells": [[e.value for e in line] for line in self.map],
                "rooms": [room.info() for room in self.dungeon.rooms],
            }
        }

    def _get_agent_position_inner_room(self):
        x = self.friend_agent.x - self.dungeon.rooms[self.friend_agent.room_id].origin[1]
        y = self.friend_agent.y - self.dungeon.rooms[self.friend_agent.room_id].origin[0]
        return x, y


class Simulator2(CellMoveSimulator):
    def __init__(self, param, dungeon=None):
        self.log = []
        self.reward_sum = 0
        super().__init__(param, dungeon=dungeon)

    def action(self, action):
        reward = super().action(action)
        self.reward_sum += reward
        self.log.append({
            'agent': self.friend_agent.__dict__.copy(),
            'enemies': [enemy.__dict__.copy() for enemy in self.enemy_list],
            'action': action,
        })

        if self.is_end:
            self.save()
        return reward

    def save(self):
        now = datetime.datetime.now()
        with open(f'log/{now.strftime("%Y%m%d_%H%M%S")}.log', 'w') as file:
            json.dump({
                'rewardSum': self.reward_sum,
                'cellMap': [[e.value for e in line] for line in self.map],
                'moveLog': self.log
            }, file)

    def reset(self):
        super().reset()
        self.reward_sum = 0
        self.log.clear()
        self.log.append({
            'agent': self.friend_agent.__dict__.copy(),
            'enemies': [enemy.__dict__.copy() for enemy in self.enemy_list],
            'action': -1,
        })
