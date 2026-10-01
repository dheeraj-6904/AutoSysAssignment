from dataclasses import dataclass
from typing import Tuple

Position = Tuple[int, int]


@dataclass
class Task:
    pickup: Position
    delivery: Position
    priority: int = 1
    picked: bool = False
    completed: bool = False
