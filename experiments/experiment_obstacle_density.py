from .common import CSV_DIR, run_batch, summarize_plot


def run(quick: bool = False):
    densities = [0.0, 0.05, 0.1, 0.15] if quick else [0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.25]
    seeds = [0, 1, 2] if quick else list(range(10))
    configs = [
        dict(width=20, height=20, static_obstacle_density=0.1, dynamic_obstacle_density=d, num_agents=8, tasks_per_agent=2, seed=s, max_steps=350)
        for d in densities
        for s in seeds
    ]
    df = run_batch(configs, "local")
    df.to_csv(CSV_DIR / "obstacle_density_results.csv", index=False)
    summarize_plot(df, "dynamic_obstacle_density", "total_time", "Density vs Total Completion Time", "density_total_time.png", "time steps")
    summarize_plot(df, "dynamic_obstacle_density", "changed_agents", "Density vs Changed Agents", "density_changed_agents.png", "changed agents")
    summarize_plot(df, "dynamic_obstacle_density", "success", "Density vs Success Rate", "density_success_rate.png", "success rate")
    summarize_plot(df, "dynamic_obstacle_density", "repair_time", "Density vs Repair Time", "density_repair_time.png", "seconds")
    return df
