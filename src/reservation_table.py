from collections import defaultdict
from typing import Dict, Iterable, List, Set, Tuple

Position = Tuple[int, int]
Edge = Tuple[Position, Position]


class ReservationTable:
    def __init__(self) -> None:
        self.vertex: Dict[int, Set[Position]] = defaultdict(set)
        self.edges: Dict[int, Set[Edge]] = defaultdict(set)

    def reserve_path(self, path: List[Position], start_time: int = 0) -> None:
        for i, pos in enumerate(path):
            t = start_time + i
            self.vertex[t].add(pos)
            if i > 0:
                self.edges[t - 1].add((path[i - 1], pos))
        if path:
            goal = path[-1]
            for t in range(start_time + len(path), start_time + len(path) + 50):
                self.vertex[t].add(goal)

    def is_vertex_reserved(self, pos: Position, time_step: int) -> bool:
        return pos in self.vertex.get(time_step, set())

    def is_edge_reserved(self, u: Position, v: Position, time_step: int) -> bool:
        return (v, u) in self.edges.get(time_step, set())


def build_reservations(paths: Iterable[List[Position]], starts: Iterable[int]) -> ReservationTable:
    rt = ReservationTable()
    for p, s in zip(paths, starts):
        rt.reserve_path(p, s)
    return rt
