# Dynamic Multi-Agent Path Planning and Local Plan Repair

## 1. Title
Dynamic Multi-Agent Path Planning and Plan Repair for Automated Warehouses.

## 2. Abstract
This project implements a full, runnable Python framework for dynamic MAPF in a warehouse grid. Initial plans are generated with reservation-based Space-Time A*. Runtime disruptions are handled by a **local plan repair** algorithm that preserves unaffected trajectories and negotiates with neighboring robots only when needed.

## 3. Introduction
Warehouse robots operate in changing environments, where static one-shot planning is insufficient. This project studies local repair under disruptions.

## 4. Problem Definition
Agents move on a 2D grid, execute sequential pickup/delivery tasks, and must avoid space-time collisions.

## 5. Objectives
1. Build collision-free initial MAPF plans.
2. Handle breakdown/cell blockage/emergency task disruptions.
3. Repair locally without rerunning full MAPF.
4. Quantify changed plans, time impact, and failures.

## 6. System Architecture
`src/` includes: `grid.py`, `agent.py`, `task.py`, `spacetime_astar.py`, `reservation_table.py`, `planner.py`, `repair.py`, `negotiation.py`, `disruptions.py`, `simulator.py`, `metrics.py`, `visualization.py`.

## 7. Environment Representation
Grid cell types: free, static obstacle, dynamic obstacle, robot occupancy.

## 8. Robot and Task Model
Task model is explicitly START→PICKUP→DELIVERY. Each robot executes multiple such tasks sequentially.

## 9. Initial MAPF Algorithm
`initial_global_planning()` does prioritized planning over all agents with a shared reservation table.

## 10. Space-Time A*
State `(x,y,t)`, actions `{N,S,E,W,WAIT}`, heuristic Manhattan distance, and goal reachability under reservations.

## 11. Reservation Table
Prevents vertex collisions and edge swaps by reserving occupied `(cell,time)` and traversed `(u,v,time)` transitions.

## 12. Dynamic Environment Model
Discrete simulator updates at each time step: disruptions, move proposals, collision checks, execution, and task updates.

## 13. Disruption Model
Implemented disruptions:
- Robot breakdown
- Sudden cell blockage
- High-priority emergency task

## 14. Plan Repair Algorithm
`local_plan_repair()`:
1. Detect directly affected agents.
2. Build local conflict component.
3. Keep outside-agent trajectories fixed as reservations.
4. Try candidate sets in increasing changed-agent count.
5. Negotiate with neighboring robots.
6. Replan local suffix paths only.
7. Commit first feasible repair.

## 15. Agent Communication / Negotiation
Centralized simulation of agent messages: `REPAIR_REQUEST`, `ACCEPT`, `REJECT`, with interval/cost/priority metadata.

## 16. Changed-Agent Minimization
Lexicographic objective:
1) minimize changed agents, 2) minimize additional completion time, 3) minimize trajectory deviation.

## 17. Failure Handling
Simulation returns `SUCCESS`/`FAILURE` and records reason, time horizon status, and unresolved situation.

## 18. Experimental Setup
Quick mode run used here:
```bash
python -m experiments.run_experiments --quick
```
(3 seeds per setting.)

## 19. Evaluation Metrics
`success`, `total_time`, `additional_time`, `changed_agents`, `changed_steps`, `repair_time`, `failure_reason`.

## 20. Results (from generated CSV)
### Experiment A (agent count)
Mean by `num_agents` (quick mode):
- 2 agents: time 85.33, changed 0.33, success 1.00
- 4 agents: time 89.00, changed 0.33, success 1.00
- 6 agents: time 92.67, changed 0.33, success 0.67
- 8 agents: time 95.00, changed 1.00, success 0.67

### Experiment B (dynamic obstacle density)
For densities 0.00/0.05/0.10/0.15, success remained 0.67 in this quick sample; repair time increased slightly with density.

### Experiment C (disruption type)
- Breakdown: success 1.00, changed_agents 0.33
- Cell blockage: success 1.00, changed_agents 1.00
- Emergency task: success 0.00, changed_agents 1.67, high additional time

### Experiment D (local vs global replanning)
- Local repair: changed_agents 2.33, mean repair_time 0.0012s
- Global replanning: changed_agents 9.67, mean repair_time 0.0047s

## 21. Graphs
Saved in `results/plots/` with labels, legends, titles, grids, and error bars.

## 22. Discussion
Local repair preserves significantly more original plans than global replanning in tested settings.

## 23. Failure Cases and Limitations (observed)
Observed failures from experiment outputs:
1. `grid=20x20, static=10%, dynamic=5%, agents=6, seed=2` → FAILURE (`No feasible local repair found`).
2. `grid=20x20, static=10%, dynamic=5%, agents=8, seed=2` → FAILURE (`No feasible local repair found`).
3. Emergency-task scenarios (seeds 0/1/2) in disruption experiment all failed in quick mode.

## 24. Limitations
Negotiation is centralized (simulated), not network-distributed. Motion model is grid-based and synchronous.

## 25. Future Work
Add richer local-search bounds, asynchronous communication delays, and tighter deadlock-resolution policies.

## 26. Conclusion
The implementation separates `initial_global_planning()` from `local_plan_repair()` and enforces local-only repair behavior after disruptions.

## 27. References
- Silver, D. (2005). Cooperative Pathfinding.
- Standley, T. S. (2010). Finding optimal solutions to cooperative pathfinding problems.
- Stern et al. (2019). Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks.
