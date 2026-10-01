from src.disruptions import cell_blockage_event
from src.metrics import count_changed_agents
from src.simulator import SimulationConfig, WarehouseSimulator


def test_single_agent_or_local_change():
    cfg = SimulationConfig(width=10, height=10, static_obstacle_density=0.0, dynamic_obstacle_density=0.0, num_agents=3, tasks_per_agent=1, seed=3, max_steps=120)
    sim = WarehouseSimulator(cfg)
    m = sim.run(disruptions=[cell_blockage_event(8, (4, 4))], repair_strategy="local")
    assert m.changed_agents >= 1


def test_changed_agent_counter():
    original = {0: [(0, 0), (1, 0)], 1: [(1, 1)]}
    repaired = {0: [(0, 0), (0, 1)], 1: [(1, 1)]}
    assert count_changed_agents(original, repaired) == 1
