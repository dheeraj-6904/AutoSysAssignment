from src.disruptions import breakdown_event, cell_blockage_event, emergency_task_event
from src.simulator import SimulationConfig, WarehouseSimulator


def test_simulation_runs():
    cfg = SimulationConfig(width=12, height=12, static_obstacle_density=0.05, dynamic_obstacle_density=0.01, num_agents=4, tasks_per_agent=1, seed=2, max_steps=180)
    sim = WarehouseSimulator(cfg)
    events = [
        cell_blockage_event(12, (3, 3)),
        breakdown_event(20, 1),
        emergency_task_event(30, 2, (1, 1), (8, 8), priority=9),
    ]
    m = sim.run(disruptions=events, repair_strategy="local")
    assert isinstance(m.success, bool)
    assert m.total_time >= 0


def test_failure_detection_exists():
    cfg = SimulationConfig(width=10, height=10, static_obstacle_density=0.3, dynamic_obstacle_density=0.2, num_agents=6, tasks_per_agent=2, seed=11, max_steps=80)
    sim = WarehouseSimulator(cfg)
    m = sim.run(disruptions=[cell_blockage_event(10, (5, 5))], repair_strategy="local")
    assert isinstance(m.failure_reason, str)
