from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .simulator import WarehouseSimulator


def animate_simulation(sim: WarehouseSimulator, save_path: str = "demo/demo.gif") -> None:
    if not sim.history:
        raise ValueError("Run simulation first")

    grid = sim.grid
    fig, ax = plt.subplots(figsize=(7, 7))

    def draw(i: int) -> None:
        frame = sim.history[i]
        ax.clear()
        ax.set_xlim(-0.5, grid.width - 0.5)
        ax.set_ylim(-0.5, grid.height - 0.5)
        ax.set_xticks(range(grid.width))
        ax.set_yticks(range(grid.height))
        ax.grid(True, linewidth=0.3)
        ax.set_title(f"Time: {frame['time']} Event: {frame['event']} Affected: {frame['affected']}")

        if grid.static_obstacles:
            xs, ys = zip(*grid.static_obstacles)
            ax.scatter(xs, ys, c="black", marker="s", s=60, label="Static")
        if grid.dynamic_obstacles:
            xd, yd = zip(*grid.dynamic_obstacles)
            ax.scatter(xd, yd, c="gray", marker="s", s=60, label="Dynamic")

        for a in sim.agents:
            for t in a.task_list:
                ax.scatter(*t.pickup, c="green", marker="^", s=45)
                ax.scatter(*t.delivery, c="red", marker="v", s=45)

        for rid, pos in frame["positions"].items():
            ax.scatter(pos[0], pos[1], c="blue", s=70)
            ax.text(pos[0], pos[1], str(rid), color="white", fontsize=8, ha="center", va="center")

        if i == 0:
            ax.legend(loc="upper right", fontsize=8)

    anim = FuncAnimation(fig, draw, frames=len(sim.history), interval=250)
    p = Path(save_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        anim.save(str(p), writer="pillow")
    except Exception:
        pass
    plt.close(fig)
