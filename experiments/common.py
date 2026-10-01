from pathlib import Path
from typing import Dict, Iterable, List

import matplotlib.pyplot as plt
import pandas as pd

from src.disruptions import breakdown_event, cell_blockage_event, emergency_task_event
from src.simulator import SimulationConfig, WarehouseSimulator

CSV_DIR = Path("results/csv")
PLOT_DIR = Path("results/plots")
CSV_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)


def default_events(seed: int, num_agents: int):
    if num_agents <= 0:
        raise ValueError("num_agents must be positive")
    b1 = seed % num_agents
    b2 = (seed + 1) % num_agents
    return [
        cell_blockage_event(20, (3 + seed % 5, 3 + seed % 4)),
        breakdown_event(50, b1),
        emergency_task_event(80, b2, (1, 1), (12, 12), priority=10),
    ]


def run_batch(configs: Iterable[Dict], repair_strategy: str = "local") -> pd.DataFrame:
    rows: List[Dict] = []
    for cfg in configs:
        sim = WarehouseSimulator(SimulationConfig(**cfg))
        m = sim.run(disruptions=default_events(cfg["seed"], cfg["num_agents"]), repair_strategy=repair_strategy)
        rows.append({
            "seed": cfg["seed"],
            "num_agents": cfg["num_agents"],
            "dynamic_obstacle_density": cfg["dynamic_obstacle_density"],
            "repair_strategy": repair_strategy,
            "success": int(m.success),
            "total_time": m.total_time,
            "additional_time": m.additional_time,
            "changed_agents": m.changed_agents,
            "changed_steps": m.changed_steps,
            "repair_time": m.repair_time,
            "failure_reason": m.failure_reason,
        })
    return pd.DataFrame(rows)


def summarize_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str, out_name: str, y_label: str) -> None:
    stats = df.groupby(x_col)[y_col].agg(["mean", "std"]).reset_index()
    plt.figure(figsize=(7, 4))
    plt.errorbar(stats[x_col], stats["mean"], yerr=stats["std"].fillna(0), marker="o", capsize=4)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_label)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / out_name, dpi=180)
    plt.close()
