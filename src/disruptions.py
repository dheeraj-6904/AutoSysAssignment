from dataclasses import dataclass
from typing import Dict, Tuple

Position = Tuple[int, int]


@dataclass
class DisruptionEvent:
    time_step: int
    event_type: str
    payload: Dict


def breakdown_event(time_step: int, robot_id: int) -> DisruptionEvent:
    return DisruptionEvent(time_step, "BREAKDOWN", {"robot_id": robot_id})


def cell_blockage_event(time_step: int, cell: Position) -> DisruptionEvent:
    return DisruptionEvent(time_step, "CELL_BLOCKAGE", {"cell": cell})


def emergency_task_event(time_step: int, robot_id: int, pickup: Position, delivery: Position, priority: int = 10) -> DisruptionEvent:
    return DisruptionEvent(time_step, "EMERGENCY_TASK", {"robot_id": robot_id, "pickup": pickup, "delivery": delivery, "priority": priority})
