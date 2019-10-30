from dataclasses import dataclass
from typing import Tuple

import numpy as np
import random


class Room:
    min_room_size: Tuple[int, int]
    max_room_size: Tuple[int, int]

    def __init__(self, row_s, column_s, row_e, column_e):
        """
            origin(list) : フロアに対してこの部屋の左上の座標
            size(list): 部屋のサイズ
                [0] : height(row)
                [1] : width(column)
        """
        self._make_room(row_s, column_s, row_e, column_e)

    def _decide_length(self, min_l, start, end, max_l):
        """
            min_l : 部屋一辺の最小の長さ
            start : 部屋の座標の始まり
            end : 部屋の座標の終わり
            max_l : 一辺の限界
        """
        while 1:
            length = random.randint(min_l, end - start - 1)
            length = length if (end - start - length) % 2 == 0 else length - 1
            if length <= max_l:
                return length

    def _make_room(self, row_s, column_s, row_e, column_e):
        min_row = self.min_room_size[0]
        max_row = self.max_room_size[0]
        min_column = self.min_room_size[1]
        max_column = self.max_room_size[1]

        print("{0}, {1}".format(min_column, column_e - column_s - 1))

        height = self._decide_length(min_row, row_s, row_e, max_row)
        width = self._decide_length(min_column, column_s, column_e, max_column)

        center = [((row_e - row_s) - height) / 2, ((column_e - column_s) - width) / 2]
        center = (np.ceil(center)).astype(np.int32)

        self.origin = [row_s + center[0], column_s + center[1]]
        self.size = [height, width]
        # print(self.origin)

    def print_to_map(self, floor_map: np.ndarray):
        floor_map[self.origin[0]:self.origin[0]+self.size[0], self.origin[1]:self.origin[1]+self.size[1]] = 2


@dataclass
class RoomInfo:
    top: int
    left: int
    bottom: int
    right: int
