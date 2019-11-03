from dataclasses import dataclass


@dataclass
class Friend:
    y: int
    x: int
    room_id: int


@dataclass
class Enemy:
    x: int
    y: int
