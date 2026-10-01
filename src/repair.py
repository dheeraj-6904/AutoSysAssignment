from itertools import combinations
from time import perf_counter
from typing import Dict, List, Set, Tuple

from .agent import RobotAgent
from .grid import GridMap
from .negotiation import Negotiator
from .reservation_table import ReservationTable
from .spacetime_astar import space_time_astar

Position = Tuple[int, int]


class LocalRepairPlanner:
    def __init__(self, max_subset_neighbors: int = 3, max_time: int = 200) -> None:
        self.max_subset_neighbors = max_subset_neighbors
        self.max_time = max_time
        self.negotiator = Negotiator()

    def _conflict(self, p1: List[Position], p2: List[Position]) -> bool:
        horizon = max(len(p1), len(p2))
        for i in range(horizon):
            a = p1[i] if i < len(p1) else p1[-1]
            b = p2[i] if i < len(p2) else p2[-1]
            if a == b:
                return True
            if i > 0:
                a0 = p1[i - 1] if i - 1 < len(p1) else p1[-1]
                b0 = p2[i - 1] if i - 1 < len(p2) else p2[-1]
                if a0 == b and b0 == a:
                    return True
        return False

    def _build_component(self, agents: List[RobotAgent], affected: Set[int], current_time: int) -> Set[int]:
        suffixes = {a.robot_id: (a.current_path[current_time:] or [a.current_position]) for a in agents if a.active}
        component = {aid for aid in affected if aid in suffixes}
        changed = True
        while changed:
            changed = False
            for a in list(component):
                for b, path in suffixes.items():
                    if b in component:
                        continue
                    if self._conflict(suffixes[a], path):
                        component.add(b)
                        changed = True
        return component

    def _fixed_reservations(self, agents: List[RobotAgent], excluded: Set[int], current_time: int) -> ReservationTable:
        rt = ReservationTable()
        for a in agents:
            if not a.active or a.robot_id in excluded:
                continue
            suffix = a.current_path[current_time:] if current_time < len(a.current_path) else [a.current_position]
            rt.reserve_path(suffix, current_time)
        return rt

    def _replan_agent(self, agent: RobotAgent, grid: GridMap, reservations: ReservationTable, current_time: int) -> List[Position] | None:
        path = [agent.current_position]
        start = agent.current_position
        t = current_time
        for wp in agent.remaining_waypoints():
            seg = space_time_astar(grid, start, wp, t, reservations, max_time=self.max_time)
            if seg is None:
                return None
            if len(seg) > 1:
                path.extend(seg[1:])
            t = current_time + len(path) - 1
            start = wp
        return path

    def local_plan_repair(self, agents: List[RobotAgent], grid: GridMap, affected_agents: Set[int], current_time: int):
        start_t = perf_counter()
        component = self._build_component(agents, affected_agents, current_time)
        if not component:
            return True, {a.robot_id: a.current_path for a in agents}, perf_counter() - start_t, ""
        neighbors = list(component - affected_agents)

        for k in range(min(self.max_subset_neighbors, len(neighbors)) + 1):
            for subset in combinations(neighbors, k):
                changed = set(affected_agents) | set(subset)
                reservations = self._fixed_reservations(agents, changed, current_time)
                new_suffixes: Dict[int, List[Position]] = {}
                feasible = True
                order = sorted(changed, key=lambda rid: next(a.priority for a in agents if a.robot_id == rid), reverse=True)

                for rid in order:
                    agent = next(a for a in agents if a.robot_id == rid)
                    if rid not in affected_agents:
                        if not self.negotiator.request_repair(min(affected_agents), rid, (current_time, current_time + 50), 5, agent.priority):
                            feasible = False
                            break
                    suffix = self._replan_agent(agent, grid, reservations, current_time)
                    if suffix is None:
                        feasible = False
                        break
                    new_suffixes[rid] = suffix
                    reservations.reserve_path(suffix, current_time)

                if feasible:
                    repaired = {}
                    for a in agents:
                        if a.robot_id in new_suffixes:
                            repaired[a.robot_id] = a.current_path[:current_time] + new_suffixes[a.robot_id]
                        else:
                            repaired[a.robot_id] = a.current_path
                    return True, repaired, perf_counter() - start_t, ""

        return False, {}, perf_counter() - start_t, "No feasible local repair found"
