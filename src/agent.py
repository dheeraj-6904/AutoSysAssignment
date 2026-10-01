from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .task import Task

Position = Tuple[int, int]


@dataclass
class RobotAgent:
    robot_id: int
    start_position: Position
    current_position: Position
    task_list: List[Task]
    current_task_index: int = 0
    current_path: List[Position] = field(default_factory=list)
    path_execution_index: int = 0
    status: str = "IDLE"
    priority: int = 1
    active: bool = True

    @property
    def current_task(self) -> Optional[Task]:
        if self.current_task_index >= len(self.task_list):
            return None
        return self.task_list[self.current_task_index]

    def remaining_waypoints(self) -> List[Position]:
        waypoints: List[Position] = []
        for i in range(self.current_task_index, len(self.task_list)):
            task = self.task_list[i]
            if not task.picked:
                waypoints.append(task.pickup)
            waypoints.append(task.delivery)
        return waypoints

    def all_tasks_completed(self) -> bool:
        return all(t.completed for t in self.task_list)
