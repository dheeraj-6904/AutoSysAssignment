import pandas as pd

from .common import CSV_DIR
from src.disruptions import cell_blockage_event
from src.simulator import SimulationConfig, WarehouseSimulator


def run(quick: bool = False):
    seeds = [0, 1, 2] if quick else list(range(10))
    rows = []
    for s in seeds:
        cfg = SimulationConfig(seed=s, width=20, height=20, num_agents=10, static_obstacle_density=0.1, dynamic_obstacle_density=0.1, max_steps=400)
        events = [cell_blockage_event(40, (5 + s % 4, 5))]
        for strategy in ["local", "global"]:
            sim = WarehouseSimulator(cfg)
            m = sim.run(disruptions=events, repair_strategy=strategy)
            rows.append({
                "seed": s,
                "strategy": strategy,
                "success": int(m.success),
                "changed_agents": m.changed_agents,
                "total_time": m.total_time,
                "additional_time": m.additional_time,
                "repair_time": m.repair_time,
            })
    df = pd.DataFrame(rows)
    df.to_csv(CSV_DIR / "baseline_comparison_results.csv", index=False)
    return df
