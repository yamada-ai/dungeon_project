import numpy as np
import random
from Room import Room


class Dungeon:
    """
        
    """

    def __init__(self, row, column):
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
        self.room_info = []

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
            self.room_info.append([row_s, column_s, row_e, column_end])
            # 次の分割用に領域座標を更新
            column_s = p + column_s + 1
            column_end = column_e
        # 左側が大きい
        else:
            # 右側は区画が確定する
            self.room_info.append([row_s, column_end + 1, row_e, column_e])

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
            self.room_info.append([row_s, column_s, row_end, column_end])
            row_s = q + row_s + 1
            row_end = row_e
        else:
            # 下側は区画が確定する
            self.room_info.append([row_end + 1, column_s, row_e, column_end])

        # print("{0}, {1}, {2}, {3}".format(row_s, column_s, row_end, column_end))
        if self.div_count == self.div_max:
            self.room_info.append([row_s, column_s, row_end, column_end])
            return
        else:
            self._div_floor(row_s, column_s, row_end, column_end)

    # 区画内に部屋を作る
    def _make_rooms(self):
        for room_data in self.room_info:
            r = Room(self, room_data[0], room_data[1], room_data[2], room_data[3])

    # 部屋を通路で繋げる
    # def _connect_aisle(self, ):

    def print_floor_map(self):
        color_format = (
            '\033[47m  \033[0m', '\033[41m  \033[0m', '\033[44m  \033[0m', '\033[42m  \033[0m', '\033[48m  \033[0m')
        for row in self.floor_map:
            for column in row:
                print(color_format[column], end="")
            print()

    def scaling(self):
        for row in range(self.row):
            for column in range(self.column):
                if (column) % 5 == 0 and (row) % 5 == 0:
                    # print("a")
                    self.floor_map[row][column] = 4
                    # print(self.floor_map[row][column])


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
    dungeon.print_floor_map()
