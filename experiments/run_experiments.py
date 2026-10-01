import argparse
import pandas as pd

from .experiment_agent_count import run as run_agent_count
from .experiment_baseline import run as run_baseline
from .experiment_disruptions import run as run_disruptions
from .experiment_obstacle_density import run as run_density


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    quick = True
    if args.full:
        quick = False
    if args.quick:
        quick = True

    a = run_agent_count(quick)
    b = run_density(quick)
    c = run_disruptions(quick)
    d = run_baseline(quick)

    summary = pd.DataFrame({"experiment": ["agent_count", "density", "disruptions", "baseline"], "rows": [len(a), len(b), len(c), len(d)]})
    summary.to_csv("results/csv/experiment_summary.csv", index=False)
    print(summary)


if __name__ == "__main__":
    main()
