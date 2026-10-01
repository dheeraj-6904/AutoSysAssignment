import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .grid import GridMap
from .reservation_table import ReservationTable

Position = Tuple[int, int]


@dataclass(order=True)
class Node:
    f: int
    g: int
    pos: Position
    t: int


def manhattan(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct(came_from: Dict[Tuple[Position, int], Tuple[Position, int]], end: Tuple[Position, int]) -> List[Position]:
    path = [end[0]]
    cur = end
    while cur in came_from:
        cur = came_from[cur]
        path.append(cur[0])
    return list(reversed(path))


def space_time_astar(grid: GridMap, start: Position, goal: Position, start_time: int, reservations: ReservationTable, max_time: int = 300) -> Optional[List[Position]]:
    open_heap: List[Node] = [Node(manhattan(start, goal), 0, start, start_time)]
    came_from: Dict[Tuple[Position, int], Tuple[Position, int]] = {}
    best_g: Dict[Tuple[Position, int], int] = {(start, start_time): 0}

    while open_heap:
        node = heapq.heappop(open_heap)
        if node.pos == goal:
            return reconstruct(came_from, (node.pos, node.t))

        if node.t - start_time > max_time:
            continue

        for nxt in grid.neighbors(node.pos):
            nt = node.t + 1
            if grid.is_blocked(nxt):
                continue
            if reservations.is_vertex_reserved(nxt, nt):
                continue
            if reservations.is_edge_reserved(node.pos, nxt, node.t):
                continue
            g = node.g + 1
            state = (nxt, nt)
            if g >= best_g.get(state, 10**9):
                continue
            best_g[state] = g
            came_from[state] = (node.pos, node.t)
            heapq.heappush(open_heap, Node(g + manhattan(nxt, goal), g, nxt, nt))

    return None
