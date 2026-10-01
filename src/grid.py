from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
import random

Position = Tuple[int, int]


@dataclass
class GridMap:
    width: int
    height: int
    static_obstacle_density: float
    dynamic_obstacle_density: float
    seed: int = 0
    rng: random.Random = field(init=False)
    static_obstacles: Set[Position] = field(default_factory=set)
    dynamic_obstacles: Set[Position] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        for x in range(self.width):
            for y in range(self.height):
                if self.rng.random() < self.static_obstacle_density:
                    self.static_obstacles.add((x, y))

    def in_bounds(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, pos: Position) -> bool:
        return pos in self.static_obstacles or pos in self.dynamic_obstacles

    def neighbors(self, pos: Position) -> List[Position]:
        x, y = pos
        candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x, y)]
        return [p for p in candidates if self.in_bounds(p) and not self.is_blocked(p)]

    def refresh_dynamic_obstacles(self, occupied: Set[Position], protected: Optional[Set[Position]] = None) -> None:
        protected = protected or set()
        new_dyn: Set[Position] = set()
        for x in range(self.width):
            for y in range(self.height):
                pos = (x, y)
                if pos in self.static_obstacles or pos in occupied or pos in protected:
                    continue
                if self.rng.random() < self.dynamic_obstacle_density:
                    new_dyn.add(pos)
        self.dynamic_obstacles = new_dyn

    def force_block_cell(self, pos: Position) -> bool:
        if not self.in_bounds(pos) or pos in self.static_obstacles:
            return False
        self.dynamic_obstacles.add(pos)
        return True

    def find_free_cell(self, forbidden: Set[Position]) -> Optional[Position]:
        cells = [(x, y) for x in range(self.width) for y in range(self.height)]
        self.rng.shuffle(cells)
        for c in cells:
            if c in forbidden or c in self.static_obstacles or c in self.dynamic_obstacles:
                continue
            return c
        return None
