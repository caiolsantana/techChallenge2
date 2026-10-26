"""Generate both visualizations from a saved scenario."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from ..data.scenario import load_scenario
from ..ga_vrp.ga import GAConfig, run_ga
from .convergence import save_convergence
from .routes_map import save_routes_map


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the GA convergence plot and route map")
    parser.add_argument("--scenario", default="data/scenarios/sp_default.json")
    parser.add_argument("--output-dir", default="results/figures")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    scenario = load_scenario(args.scenario)
    result = run_ga(scenario.delivery_points, scenario.vehicles, scenario.depot, GAConfig())
    output_dir = Path(args.output_dir)
    print(save_convergence(result.best_fitness_history, output_dir / "convergence.png"))
    print(save_routes_map(result.best_solution, scenario.depot, output_dir / "routes.html"))
    print(f"Unrouted points: {len(result.best_solution.unrouted_points)}")


if __name__ == "__main__":
    main()
