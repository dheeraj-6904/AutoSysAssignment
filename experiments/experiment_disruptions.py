import pandas as pd

from .common import CSV_DIR
from src.disruptions import breakdown_event, cell_blockage_event, emergency_task_event
from src.simulator import SimulationConfig, WarehouseSimulator


def run(quick: bool = False):
    seeds = [0, 1, 2] if quick else list(range(10))
    rows = []
    for s in seeds:
        cfg = SimulationConfig(seed=s, width=20, height=20, num_agents=8, static_obstacle_density=0.1, dynamic_obstacle_density=0.08, max_steps=350)
        cases = {
            "breakdown": [breakdown_event(35, s % 4)],
            "cell_blockage": [cell_blockage_event(35, (6 + s % 3, 6))],
            "emergency_task": [emergency_task_event(35, s % 4, (1, 1), (16, 16), priority=10)],
        }
        for name, events in cases.items():
            sim = WarehouseSimulator(cfg)
            m = sim.run(disruptions=events, repair_strategy="local")
            rows.append({
                "seed": s,
                "disruption_type": name,
                "success": int(m.success),
                "changed_agents": m.changed_agents,
                "additional_time": m.additional_time,
                "repair_time": m.repair_time,
            })
    df = pd.DataFrame(rows)
    df.to_csv(CSV_DIR / "disruption_results.csv", index=False)
    return df
