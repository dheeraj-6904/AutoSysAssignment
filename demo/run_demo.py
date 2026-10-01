import argparse

from src.disruptions import breakdown_event, cell_blockage_event, emergency_task_event
from src.simulator import SimulationConfig, WarehouseSimulator
from src.visualization import animate_simulation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--save", type=str, default="demo/demo.gif")
    args = parser.parse_args()

    sim = WarehouseSimulator(SimulationConfig(seed=args.seed, num_agents=6, max_steps=220, dynamic_obstacle_density=0.02))
    events = [
        cell_blockage_event(15, (4, 4)),
        breakdown_event(40, 1),
        emergency_task_event(60, 2, (2, 2), (15, 15), priority=9),
    ]
    metrics = sim.run(disruptions=events, repair_strategy="local")
    animate_simulation(sim, args.save)
    print(metrics)


if __name__ == "__main__":
    main()
