"""Run three GA configurations on identical scenarios and compare with a greedy baseline."""

from __future__ import annotations

import csv
import json
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from ..data.scenario import GeneratedScenario, load_scenario
from ..ga_vrp.fitness import evaluate
from ..ga_vrp.ga import GAConfig, run_ga
from ..ga_vrp.models import Solution
from ..ga_vrp.validators import all_points_visited_once, is_autonomy_respected, is_capacity_respected
from .baseline import nearest_neighbor


@dataclass(frozen=True)
class Experiment:
    name: str
    population_size: int
    n_generations: int
    crossover_probability: float
    mutation_probability: float
    mutation_operator: str


EXPERIMENTS = (
    Experiment("small_swap", 40, 50, 0.6, 0.10, "swap"),
    Experiment("medium_swap", 70, 80, 0.8, 0.30, "swap"),
    Experiment("large_inversion", 100, 100, 1.0, 0.50, "inversion"),
)


def solution_metrics(solution: Solution, scenario: GeneratedScenario) -> dict:
    return {
        "distance": round(solution.total_distance, 6),
        "fitness": round(evaluate(solution), 6),
        "routes": len(solution.routes),
        "routed_points": sum(len(route.points) for route in solution.routes),
        "unrouted_points": len(solution.unrouted_points),
        "capacity_violations": sum(not is_capacity_respected(route) for route in solution.routes),
        "autonomy_violations": sum(not is_autonomy_respected(route) for route in solution.routes),
        "all_points_accounted_for": all_points_visited_once(solution, scenario.delivery_points),
    }


def run_experiments(scenario: GeneratedScenario, seeds: tuple[int, ...] = (42, 73, 101)) -> dict:
    if not seeds:
        raise ValueError("At least one seed is required")
    baseline_start = time.perf_counter()
    baseline = nearest_neighbor(scenario.delivery_points, scenario.vehicles, scenario.depot)
    baseline_metrics = solution_metrics(baseline, scenario)
    baseline_metrics["elapsed_seconds"] = round(time.perf_counter() - baseline_start, 4)

    runs = []
    for experiment in EXPERIMENTS:
        config = GAConfig(
            population_size=experiment.population_size,
            n_generations=experiment.n_generations,
            crossover_probability=experiment.crossover_probability,
            mutation_probability=experiment.mutation_probability,
            mutation_operator=experiment.mutation_operator,
        )
        for seed in seeds:
            random.seed(seed)
            started = time.perf_counter()
            result = run_ga(scenario.delivery_points, scenario.vehicles, scenario.depot, config)
            metrics = solution_metrics(result.best_solution, scenario)
            metrics.update(
                experiment=experiment.name,
                seed=seed,
                elapsed_seconds=round(time.perf_counter() - started, 4),
                first_fitness=round(result.best_fitness_history[0], 6),
                last_fitness=round(result.best_fitness_history[-1], 6),
                generations=len(result.best_fitness_history),
                convergence_generation=next(
                    index
                    for index, value in enumerate(result.best_fitness_history, start=1)
                    if value == result.best_fitness_history[-1]
                ),
                distance_change_vs_baseline_percent=(
                    round(100 * (metrics["distance"] / baseline_metrics["distance"] - 1), 2)
                    if baseline_metrics["distance"] > 0
                    and metrics["unrouted_points"] == baseline_metrics["unrouted_points"] == 0
                    else None
                ),
                fitness_change_vs_baseline_percent=(
                    round(100 * (metrics["fitness"] / baseline_metrics["fitness"] - 1), 2)
                    if baseline_metrics["fitness"] > 0
                    and metrics["unrouted_points"] == baseline_metrics["unrouted_points"] == 0
                    else None
                ),
            )
            runs.append(metrics)
    return {
        "scenario": {
            "delivery_points": len(scenario.delivery_points),
            "vehicles": len(scenario.vehicles),
            "distance_unit": "Euclidean latitude/longitude coordinate units (not km)",
        },
        "baseline": baseline_metrics,
        "configurations": [asdict(experiment) for experiment in EXPERIMENTS],
        "runs": runs,
    }


def save_experiments(report: dict, output: str | Path) -> tuple[Path, Path]:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path = output.with_suffix(".csv")
    runs = report["runs"]
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(runs[0]))
        writer.writeheader()
        writer.writerows(runs)
    return output, csv_path


def run_from_file(path: str | Path, output: str | Path, seeds: tuple[int, ...] = (42, 73, 101)) -> dict:
    report = run_experiments(load_scenario(path), seeds)
    save_experiments(report, output)
    return report
