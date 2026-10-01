from dataclasses import dataclass
from typing import Dict, List, Tuple

Position = Tuple[int, int]


@dataclass
class SimulationMetrics:
    success: bool
    total_time: int
    additional_time: int
    changed_agents: int
    changed_steps: int
    additional_waiting: int
    repair_time: float
    failure_reason: str


def count_changed_agents(original_paths: Dict[int, List[Position]], repaired_paths: Dict[int, List[Position]]) -> int:
    return sum(1 for aid, p in original_paths.items() if repaired_paths.get(aid, p) != p)


def count_changed_steps(original_paths: Dict[int, List[Position]], repaired_paths: Dict[int, List[Position]]) -> int:
    total = 0
    for aid, original in original_paths.items():
        repaired = repaired_paths.get(aid, original)
        horizon = max(len(original), len(repaired))
        for i in range(horizon):
            a = original[i] if i < len(original) else original[-1]
            b = repaired[i] if i < len(repaired) else repaired[-1]
            if a != b:
                total += 1
    return total
