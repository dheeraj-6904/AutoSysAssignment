from dataclasses import dataclass
from time import perf_counter
from typing import Dict, List, Optional, Set, Tuple
import random

from .agent import RobotAgent
from .disruptions import DisruptionEvent
from .grid import GridMap
from .metrics import SimulationMetrics, count_changed_agents, count_changed_steps
from .planner import apply_plans, initial_global_planning
from .repair import LocalRepairPlanner
from .task import Task

Position = Tuple[int, int]


@dataclass
class SimulationConfig:
    width: int = 20
    height: int = 20
    static_obstacle_density: float = 0.1
    dynamic_obstacle_density: float = 0.03
    num_agents: int = 6
    tasks_per_agent: int = 2
    seed: int = 42
    max_steps: int = 300
    dynamic_refresh_period: int = 0


class WarehouseSimulator:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
        self.grid = GridMap(config.width, config.height, config.static_obstacle_density, config.dynamic_obstacle_density, config.seed)
        self.agents = self._spawn_agents()
        self.original_paths: Dict[int, List[Position]] = {}
        self.history: List[Dict] = []
        self.repair_planner = LocalRepairPlanner()

    def _spawn_agents(self) -> List[RobotAgent]:
        used = set(self.grid.static_obstacles)
        agents: List[RobotAgent] = []
        for aid in range(self.config.num_agents):
            start = self.grid.find_free_cell(used)
            if start is None:
                raise ValueError("No free start cell")
            used.add(start)
            tasks: List[Task] = []
            for _ in range(self.config.tasks_per_agent):
                pickup = self.grid.find_free_cell(used)
                delivery = self.grid.find_free_cell(used | {pickup} if pickup else used)
                if pickup is None or delivery is None:
                    raise ValueError("No free task cell")
                tasks.append(Task(pickup, delivery, priority=1))
            agents.append(RobotAgent(aid, start, start, tasks, priority=self.rng.randint(1, 5)))
        return agents

    def _init_plans(self) -> bool:
        plans = initial_global_planning(self.agents, self.grid, max_time=self.config.max_steps)
        if plans is None:
            return False
        apply_plans(self.agents, plans)
        self.original_paths = {aid: list(path) for aid, path in plans.items()}
        return True

    def _update_task(self, agent: RobotAgent) -> None:
        task = agent.current_task
        if task is None:
            return
        if not task.picked and agent.current_position == task.pickup:
            task.picked = True
            agent.status = "PICKED"
        if task.picked and not task.completed and agent.current_position == task.delivery:
            task.completed = True
            agent.status = "DELIVERED"
            agent.current_task_index += 1

    def _advance(self, t: int) -> List[int]:
        blocked: List[int] = []
        proposed: Dict[int, Position] = {}
        for a in self.agents:
            if not a.active:
                continue
            idx = min(t + 1, len(a.current_path) - 1)
            nxt = a.current_path[idx]
            if self.grid.is_blocked(nxt):
                blocked.append(a.robot_id)
                proposed[a.robot_id] = a.current_position
            else:
                proposed[a.robot_id] = nxt

        occupancy: Dict[Position, List[int]] = {}
        for aid, pos in proposed.items():
            occupancy.setdefault(pos, []).append(aid)
        for pos, ids in occupancy.items():
            if len(ids) > 1:
                blocked.extend(ids)
                for aid in ids:
                    proposed[aid] = next(a.current_position for a in self.agents if a.robot_id == aid)

        for a in self.agents:
            if not a.active:
                continue
            a.current_position = proposed.get(a.robot_id, a.current_position)
            a.path_execution_index = min(t + 1, len(a.current_path) - 1)
            self._update_task(a)
            if a.all_tasks_completed():
                a.status = "DONE"

        return sorted(set(blocked))

    def _apply_event(self, ev: DisruptionEvent, t: int) -> Set[int]:
        affected: Set[int] = set()
        if ev.event_type == "BREAKDOWN":
            rid = ev.payload["robot_id"]
            ag = next(a for a in self.agents if a.robot_id == rid)
            ag.active = False
            ag.status = "FAILED"
            self.grid.dynamic_obstacles.add(ag.current_position)
            for a in self.agents:
                if a.active and ag.current_position in a.current_path[t:]:
                    affected.add(a.robot_id)
        elif ev.event_type == "CELL_BLOCKAGE":
            cell = tuple(ev.payload["cell"])
            self.grid.force_block_cell(cell)
            for a in self.agents:
                if a.active and cell in a.current_path[t:]:
                    affected.add(a.robot_id)
        elif ev.event_type == "EMERGENCY_TASK":
            rid = ev.payload["robot_id"]
            ag = next(a for a in self.agents if a.robot_id == rid)
            ag.task_list.insert(ag.current_task_index, Task(ev.payload["pickup"], ev.payload["delivery"], ev.payload.get("priority", 10)))
            ag.priority = max(ag.priority, ev.payload.get("priority", 10))
            affected.add(rid)
        return affected

    def _global_replan(self, t: int) -> Optional[Dict[int, List[Position]]]:
        active = [a for a in self.agents if a.active]
        plans = initial_global_planning(active, self.grid, max_time=self.config.max_steps)
        if plans is None:
            return None
        merged: Dict[int, List[Position]] = {}
        for a in self.agents:
            if a.active:
                merged[a.robot_id] = a.current_path[:t] + plans[a.robot_id]
            else:
                merged[a.robot_id] = a.current_path
        return merged

    def run(self, disruptions: Optional[List[DisruptionEvent]] = None, repair_strategy: str = "local", enable_dynamic_updates: bool = False) -> SimulationMetrics:
        disruptions = disruptions or []
        if not self._init_plans():
            return SimulationMetrics(False, 0, 0, 0, 0, 0, 0.0, "Initial planning failed")

        total_repair = 0.0
        base_completion = max(len(p) for p in self.original_paths.values())
        repaired = {aid: list(p) for aid, p in self.original_paths.items()}

        for t in range(self.config.max_steps):
            if enable_dynamic_updates and self.config.dynamic_refresh_period and t % self.config.dynamic_refresh_period == 0:
                occupied = {a.current_position for a in self.agents if a.active}
                self.grid.refresh_dynamic_obstacles(occupied, occupied)

            event_name = "NONE"
            affected: Set[int] = set()
            for ev in disruptions:
                if ev.time_step == t:
                    event_name = ev.event_type
                    affected |= self._apply_event(ev, t)

            affected |= set(self._advance(t))

            if affected:
                if repair_strategy == "local":
                    ok, new_paths, rt, reason = self.repair_planner.local_plan_repair(self.agents, self.grid, affected, t)
                else:
                    start = perf_counter()
                    new_paths = self._global_replan(t)
                    rt = perf_counter() - start
                    ok = new_paths is not None
                    reason = "Global replanning failed" if not ok else ""
                total_repair += rt
                if not ok:
                    return SimulationMetrics(False, t, max(0, t - base_completion), count_changed_agents(self.original_paths, repaired), count_changed_steps(self.original_paths, repaired), 0, total_repair, reason)
                repaired = new_paths
                for a in self.agents:
                    a.current_path = repaired[a.robot_id]

            self.history.append({
                "time": t,
                "positions": {a.robot_id: a.current_position for a in self.agents},
                "event": event_name,
                "affected": sorted(affected),
                "changed_agents": [aid for aid in repaired if repaired[aid] != self.original_paths.get(aid, [])],
            })

            if all((not a.active) or a.all_tasks_completed() for a in self.agents):
                total_time = t + 1
                return SimulationMetrics(True, total_time, max(0, total_time - base_completion), count_changed_agents(self.original_paths, repaired), count_changed_steps(self.original_paths, repaired), 0, total_repair, "")

        return SimulationMetrics(False, self.config.max_steps, max(0, self.config.max_steps - base_completion), count_changed_agents(self.original_paths, repaired), count_changed_steps(self.original_paths, repaired), 0, total_repair, "Max steps exceeded")
