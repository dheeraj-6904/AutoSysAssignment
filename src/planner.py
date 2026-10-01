from typing import Dict, List, Optional, Tuple

from .agent import RobotAgent
from .grid import GridMap
from .reservation_table import ReservationTable
from .spacetime_astar import space_time_astar

Position = Tuple[int, int]


def initial_global_planning(agents: List[RobotAgent], grid: GridMap, max_time: int = 300) -> Optional[Dict[int, List[Position]]]:
    reservations = ReservationTable()
    plans: Dict[int, List[Position]] = {}

    for agent in sorted(agents, key=lambda a: (-a.priority, a.robot_id)):
        start = agent.current_position
        full = [start]
        t = 0
        for wp in agent.remaining_waypoints():
            seg = space_time_astar(grid, start, wp, t, reservations, max_time=max_time)
            if seg is None:
                return None
            if len(seg) > 1:
                full.extend(seg[1:])
            t = len(full) - 1
            start = wp
        plans[agent.robot_id] = full
        reservations.reserve_path(full, 0)

    return plans


def apply_plans(agents: List[RobotAgent], plans: Dict[int, List[Position]]) -> None:
    for a in agents:
        if a.robot_id in plans:
            a.current_path = plans[a.robot_id]
            a.path_execution_index = 0
            a.status = "PLANNED"
