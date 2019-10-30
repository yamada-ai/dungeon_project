from dataclasses import dataclass
from typing import List

import numpy as np
import random
from Room import Room


class Dungeon:
    """
        
    """

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
        self.floor_map = np.zeros((self.row, self.column), dtype="int32")
        self.icon = ["■", "　"]
        # 区画の最小サイズ(5分割)
        self.min_div_size = [row / 5 + 1, column / 5 + 1]
        self.div_max = 2
        self.div_count = 0

        # 部屋の最小サイズ
        self.min_room_size = [row / 5 - 2, column / 5 - 2]
        self.max_room_size = [row / 2, column / 2]
        # 部屋
        self.rooms = []
        # 部屋を作る際に必要な区画の座標を保持する変数
        self.room_info: List[RoomInfo] = []

    # フロアマップを分割する
    def _div_floor(self, row_s, column_s, row_e, column_e):
        self.div_count += 1
        # 縦に分割
        # 横方向に領域を取得
        p = random.randint(self.min_div_size[1], (column_e - column_s) - self.min_div_size[1])
        p = p if p % 2 == 0 else p + 1
        # 境界線を描く
        for row in range(row_s, row_e):
            self.floor_map[row][p + column_s] = 1

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
            self.floor_map[q + row_s][column] = 1

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
            self.rooms.append(Room(self, room_data.top, room_data.left, room_data.bottom, room_data.right))

    # 部屋を通路で繋げる
    def _connect_aisle(self):
        for i in range(len(self.room_info)-1):
            room1_info = self.room_info[i]
            room1 = self.rooms[i]
            room2_info = self.room_info[i+1]
            room2 = self.rooms[i+1]
            # 上下に接続している
            if room1_info.top == room2_info.bottom+1 or room1_info.bottom+1 == room2_info.top:
                x1 = random.randint(room1.origin[1], room1.origin[1] + room1.room_size[1] - 1)
                x2 = random.randint(room2.origin[1], room2.origin[1] + room2.room_size[1] - 1)
                # room1が上側
                if room1_info.top < room2_info.top:
                    y1 = room1.origin[0] + room1.room_size[0]
                    y2 = room2.origin[0]
                    # 縦方向に通路を引く
                    # room1
                    for j in range(y1, room1_info.bottom):
                        self.floor_map[j][x1] = 3
                    # room2
                    for j in range(y2-1, room2_info.top-1, -1):
                        self.floor_map[j][x2] = 3
                    # 縦方向の通路を結ぶ
                    for j in range(min(x1, x2), max(x1, x2)+1):
                        self.floor_map[room1_info.bottom][j] = 3
                # room2が上側
                else:
                    y1 = room1.origin[0]
                    y2 = room2.origin[0] + room2.room_size[0]
                    # 横方向に通路を引く
                    # room1
                    for j in range(y1-1, room1_info.top-1, -1):
                        self.floor_map[j][x1] = 3
                    # room2
                    for j in range(y2, room2_info.bottom):
                        self.floor_map[j][x2] = 3
                    # 縦方向の通路を結ぶ
                    for j in range(min(x1, x2), max(x1, x2)+1):
                        self.floor_map[room2_info.bottom][j] = 3

            # 左右に接続している
            if room1_info.left == room2_info.right+1 or room1_info.right+1 == room2_info.left:
                y1 = random.randint(room1.origin[0], room1.origin[0] + room1.room_size[0] - 1)
                y2 = random.randint(room2.origin[0], room2.origin[0] + room2.room_size[0] - 1)
                # room1が左側
                if room1_info.left < room2_info.left:
                    x1 = room1.origin[1] + room1.room_size[1]
                    x2 = room2.origin[1]
                    # 横方向に通路を引く
                    # room1
                    for j in range(x1, room1_info.right):
                        self.floor_map[y1][j] = 3
                    # room2
                    for j in range(x2-1, room2_info.left-1, -1):
                        self.floor_map[y2][j] = 3
                    # 横方向の通路を結ぶ
                    for j in range(min(y1, y2), max(y1, y2)+1):
                        self.floor_map[j][room1_info.right] = 3
                # room2が左側
                else:
                    x1 = room1.origin[1]
                    x2 = room2.origin[1] + room2.room_size[1]
                    # 横方向に通路を引く
                    # room1
                    for j in range(x1-1, room1_info.left-1, -1):
                        self.floor_map[y1][j] = 3
                    # room2
                    for j in range(x2, room2_info.right):
                        self.floor_map[y2][j] = 3
                    # 横方向の通路を結ぶ
                    for j in range(min(y1, y2), max(y1, y2)+1):
                        self.floor_map[j][room2_info.right] = 3

    def print_floor_map(self):
        color_format = (
            '\033[47m  \033[0m',    # 白
            '\033[41m  \033[0m',    # 赤
            '\033[44m  \033[0m',    # 青
            '\033[42m  \033[0m',    # 緑
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


@dataclass
class RoomInfo:
    top: int
    left: int
    bottom: int
    right: int


if __name__ == "__main__":
    # row, column は 4の倍数にしてください
    row = 30
    column = 40
    dungeon = Dungeon(row, column)
    dungeon._div_floor(0, 0, row, column)
    for room in dungeon.room_info:
        print(room)
    print()
    dungeon._make_rooms()
    dungeon.scaling()
    dungeon._connect_aisle()
    dungeon.print_floor_map()
