from .common import CSV_DIR, run_batch, summarize_plot


def run(quick: bool = False):
    counts = [2, 4, 6, 8] if quick else [2, 4, 6, 8, 10, 12, 16, 20]
    seeds = [0, 1, 2] if quick else list(range(10))
    configs = [
        dict(width=20, height=20, static_obstacle_density=0.1, dynamic_obstacle_density=0.05, num_agents=n, tasks_per_agent=2, seed=s, max_steps=350)
        for n in counts
        for s in seeds
    ]
    df = run_batch(configs, "local")
    df.to_csv(CSV_DIR / "agent_count_results.csv", index=False)
    summarize_plot(df, "num_agents", "total_time", "Agents vs Total Completion Time", "agents_total_time.png", "time steps")
    summarize_plot(df, "num_agents", "changed_agents", "Agents vs Changed Agents", "agents_changed_agents.png", "changed agents")
    summarize_plot(df, "num_agents", "success", "Agents vs Success Rate", "agents_success_rate.png", "success rate")
    summarize_plot(df, "num_agents", "repair_time", "Agents vs Repair Time", "agents_repair_time.png", "seconds")
    return df
