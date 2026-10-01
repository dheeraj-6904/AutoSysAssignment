# AutoSysAssignment: Dynamic MAPF and Local Plan Repair

## Project overview
This repository implements dynamic multi-agent warehouse planning with:
- reservation-based Space-Time A* initial MAPF
- local plan repair (without rerunning global planning)
- disruption handling (breakdown, cell blockage, emergency task)
- experiments, plots, tests, and animation demo

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run a basic simulation
```bash
python - <<'PY'
from src.simulator import SimulationConfig, WarehouseSimulator
sim = WarehouseSimulator(SimulationConfig())
print(sim.run())
PY
```

## Run graphical demo
```bash
python -m demo.run_demo
```

## Run quick experiments
```bash
python -m experiments.run_experiments --quick
```

## Run full experiments
```bash
python -m experiments.run_experiments --full
```

## Run tests
```bash
pytest
```

## Output locations
- Raw results: `results/csv/`
- Plots: `results/plots/`
- Report: `report/report.md`
- Demo animation: `demo/demo.gif`

## Reproduce report
1. Install dependencies.
2. Run quick/full experiments.
3. Use produced CSV and plots.
4. Run demo and tests.

## References
- Silver, D. (2005). Cooperative Pathfinding.
- Standley, T. S. (2010). Cooperative pathfinding optimality.
- Stern et al. (2019). MAPF definitions and benchmarks.
