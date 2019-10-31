from typing import List

import numpy as np
import random

from Road import Road
from Room import Room, RoomInfo


class Dungeon:

    def __init__(self, row: int, column: int):
        """
            row : マップの縦幅(壁)
            column : マップの横幅(壁)
            floor_map : フロアデータ row*column int64
            icon : フロアの各マスの役割のアイコン
                    0 → 壁
                    1 → 空間(歩ける)
            min_div_size : 分割する区画の最小サイズ(1/16)　 
        """

        self.row = row
        self.column = column
        # フロアマップの作成
        self.floor_map: np.ndarray = np.zeros((self.row, self.column), dtype="int32")
        self.icon = ["■", "　"]
        # 区画の最小サイズ(5分割)
        self.min_div_size = [row / 5 + 1, column / 5 + 1]
        self.div_max = 2
        self.div_count = 0

        # 部屋の最小サイズ
        self.min_room_size = [row / 5 - 2, column / 5 - 2]
        Room.min_room_size = self.min_room_size
        self.max_room_size = [row / 2, column / 2]
        Room.max_room_size = self.max_room_size
        # 部屋
        self.rooms: List[Room] = []
        # 部屋を作る際に必要な区画の座標を保持する変数
        self.room_info: List[RoomInfo] = []
        # 通路
        self.roads: List[Road] = []

        # 初期化
        self._div_floor(0, 0, row, column)
        self._make_rooms()
        self._print_rooms2map()
        self._connect_rooms()
        self._print_roads2map()
        self.floor_map[self.floor_map == 3] = 0
        self.print_floor_map()

    # フロアマップを分割する
    def _div_floor(self, row_s, column_s, row_e, column_e):
        self.div_count += 1
        # 縦に分割
        # 横方向に領域を取得
        p = random.randint(self.min_div_size[1], (column_e - column_s) - self.min_div_size[1])
        p = p if p % 2 == 0 else p + 1
        # 境界線を描く
        for row in range(row_s, row_e):
            self.floor_map[row][p + column_s] = 3

        # 左側が大きければ変わらない
        column_end = p + column_s

        # 領域の右側が大きい
        if p < (column_e - column_s) / 2:
            # 左側は区画が確定する
            self.room_info.append(RoomInfo(row_s, column_s, row_e, column_end))
            # 次の分割用に領域座標を更新
            column_s = p + column_s + 1
            column_end = column_e
        # 左側が大きい
        else:
            # 右側は区画が確定する
            self.room_info.append(RoomInfo(row_s, column_end + 1, row_e, column_e))

        # 縦方向に領域を取得
        q = random.randint(self.min_div_size[0], (row_e - row_s) - self.min_div_size[0])
        q = q if q % 2 == 0 else q + 1

        # 横方向に境界線を描く
        for column in range(column_s, column_end):
            self.floor_map[q + row_s][column] = 3

        # 上側が大きければ変わらない
        row_end = q + row_s
        # 領域の下側が大きい
        if q < (self.row - row_s) / 2:
            # 上側は区画が確定する
            self.room_info.append(RoomInfo(row_s, column_s, row_end, column_end))
            row_s = q + row_s + 1
            row_end = row_e
        else:
            # 下側は区画が確定する
            self.room_info.append(RoomInfo(row_end + 1, column_s, row_e, column_end))

        # print("{0}, {1}, {2}, {3}".format(row_s, column_s, row_end, column_end))
        if self.div_count == self.div_max:
            self.room_info.append(RoomInfo(row_s, column_s, row_end, column_end))
            return
        else:
            self._div_floor(row_s, column_s, row_end, column_end)

    # 区画内に部屋を作る
    def _make_rooms(self):
        for room_data in self.room_info:
            self.rooms.append(Room(room_data.top, room_data.left, room_data.bottom, room_data.right))

    def _print_rooms2map(self):
        for room in self.rooms:
            room.print_to_map(self.floor_map)

    # 部屋を通路で繋げる
    def _connect_rooms(self):
        for i in range(len(self.room_info)-1):
            self._create_road(self.room_info[i], self.rooms[i], self.room_info[i+1],  self.rooms[i+1])

            for j in range(i+2, len(self.room_info)-1):
                is_connected = self._create_road(self.room_info[i], self.rooms[i], self.room_info[j],  self.rooms[j])
                if is_connected:
                    break

    def _create_road(self, room1_info, room1, room2_info, room2):
        road = Road(room1, room1_info, room2, room2_info)
        if not road.can_connect:
            return False
        self.roads.append(road)
        return True

    def _print_roads2map(self):
        for road in self.roads:
            road.print2map(self.floor_map)

    def print_floor_map(self):
        color_format = (
            '\033[47m  \033[0m',    # 白
            '\033[44m  \033[0m',    # 青
            '\033[42m  \033[0m',    # 緑
            '\033[41m  \033[0m',    # 赤
            '\033[48m  \033[0m'     # 黒
        )
        for row in self.floor_map:
            for column in row:
                print(color_format[column], end="")
            print()

    def scaling(self):
        for row in range(self.row):
            for column in range(self.column):
                if column % 5 == 0 and row % 5 == 0:
                    # print("a")
                    self.floor_map[row][column] = 4
                    # print(self.floor_map[row][column])

    def dump2json(self):
        return {
            'row': self.row,
            'column': self.column,
            'floor_map': self.floor_map.tolist(),
            'rooms': [room.dump2json() for room in self.rooms]
        }


if __name__ == "__main__":
    # row, column は 4の倍数にしてください
    row = 30
    column = 40
    dungeon = Dungeon(row, column)
