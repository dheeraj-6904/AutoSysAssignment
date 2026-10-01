# Dynamic Multi-Agent Path Planning and Local Plan Repair

## 1. Title
Dynamic Multi-Agent Path Planning and Local Plan Repair in an Automated Warehouse.

## 2. Abstract
We implement a complete Python simulation for dynamic warehouse MAPF. Initial paths are built with reservation-based space-time planning; disruptions are handled with local repair that minimizes changed agents before minimizing delay.

## 3. Introduction
Warehouse robots need robust plans in dynamic environments with breakdowns, blocked cells, and urgent insertions.

## 4. Problem Definition
Robots move on a 2D grid, execute sequential pickup→delivery tasks, and avoid vertex/edge collisions over space-time.

## 5. Objectives
- collision-free initial MAPF
- explicit local repair (not global rerun)
- negotiation between neighboring agents
- measured impact under varying agents/obstacles

## 6. System Architecture
Modules: `grid`, `agent`, `task`, `spacetime_astar`, `reservation_table`, `planner`, `repair`, `negotiation`, `simulator`, `metrics`, `visualization`.

## 7. Environment Representation
Configurable width/height/static and dynamic obstacle densities/seed/agent count.

## 8. Robot and Task Model
Task model: START→PICKUP→DELIVERY, repeated sequentially per robot.

## 9. Initial MAPF Algorithm
`initial_global_planning()` plans all agents in priority order with a reservation table.

## 10. Space-Time A*
State: `(x,y,t)`; actions: NSEW+wait; heuristic: Manhattan distance.

## 11. Reservation Table
Prevents vertex conflicts and edge swaps via time-indexed vertex and edge reservations.

## 12. Dynamic Environment Model
Discrete time-step simulation with optional dynamic obstacle refresh and scheduled disruptions.

## 13. Disruption Model
Implemented: robot breakdown, sudden cell blockage, emergency high-priority task insertion.

## 14. Plan Repair Algorithm
`local_plan_repair()`:
1. detect directly affected agents,
2. build local conflict component,
3. hold unaffected trajectories fixed,
4. negotiate with neighbors,
5. replan only selected local suffixes,
6. choose first feasible solution in increasing changed-agent count.

## 15. Agent Communication / Negotiation
Simulated messages (`REPAIR_REQUEST`, `ACCEPT`, `REJECT`) in centralized simulator.

## 16. Changed-Agent Minimization
Primary: minimize changed agents.
Secondary: minimize additional completion time.
Tertiary: reduce trajectory deviation.

## 17. Failure Handling
Failure reasons include no feasible repair and max-step exceedance, captured in metrics.

## 18. Experimental Setup
`experiments/run_experiments.py` provides quick/full modes.

## 19. Evaluation Metrics
`success`, `total_time`, `additional_time`, `changed_agents`, `changed_steps`, `repair_time`, `failure_reason`.

## 20. Results
Generated CSV and plots are saved under `results/` from real runs.

## 21. Graphs
Error-bar plots (mean ± std) are produced for agent count and obstacle density analyses.

## 22. Discussion
Local repair keeps unaffected plans fixed and typically changes fewer agents than global replanning.

## 23. Failure Cases and Limitations
Use rows with `success=0` in CSV output to report actual failed settings (grid size, density, seed, disruption, reason).

## 24. Limitations
Negotiation is centralized; robot kinematics and uncertainty are simplified.

## 25. Future Work
Add richer constraints, distributed communication delay, and stronger local-optimal search.

## 26. Conclusion
The project demonstrates complete dynamic MAPF with explicit local-only repair behavior.

## 27. References
- Silver (2005)
- Standley (2010)
- Stern et al. (2019)
