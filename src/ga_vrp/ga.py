"""Main GA loop: evolves giant tours, decoding + scoring each one via split.py/fitness.py.

Same skeleton as base_code/tsp.py's main loop (elitism + roulette-wheel selection +
crossover + mutation), but operating on `DeliveryPoint` tours and using `fitness.evaluate()`
(distance + priority + infeasibility penalty) instead of plain TSP distance.

Fase 2's synthetic data generator (`src.data.scenario`) now provides real input, e.g.:
    from src.data.scenario import generate_scenario
    scenario = generate_scenario()
    result = run_ga(scenario.delivery_points, scenario.vehicles, scenario.depot, GAConfig())

`python -m src.ga_vrp.ga` still runs the small hardcoded demo below (8 points, 2 vehicles) —
kept as a fast, dependency-free smoke test of the GA loop itself.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from . import fitness as fitness_module
from .models import DeliveryPoint, Depot, Priority, Solution, Vehicle
from .operators import (
    generate_random_population,
    inversion_mutate,
    order_crossover,
    roulette_wheel_selection,
    swap_mutate,
)
from .split import split_into_routes


@dataclass
class GAConfig:
    population_size: int = 100
    n_generations: int = 100
    crossover_probability: float = 1.0
    mutation_probability: float = 0.3
    mutation_operator: str = "swap"  # "swap" (base_code default) or "inversion"
    priority_weight: float = fitness_module.DEFAULT_PRIORITY_WEIGHT
    infeasible_penalty: float = fitness_module.DEFAULT_INFEASIBLE_PENALTY


@dataclass
class GAResult:
    best_tour: list[DeliveryPoint]
    best_solution: Solution
    best_fitness_history: list[float] = field(default_factory=list)


def run_ga(
    delivery_points: list[DeliveryPoint],
    vehicles: list[Vehicle],
    depot: Depot,
    config: GAConfig | None = None,
) -> GAResult:
    config = config or GAConfig()
    mutate_fn = inversion_mutate if config.mutation_operator == "inversion" else swap_mutate

    population = generate_random_population(delivery_points, config.population_size)
    best_fitness_history: list[float] = []
    best_tour: list[DeliveryPoint] = population[0]
    best_solution: Solution = split_into_routes(best_tour, vehicles, depot)

    for _generation in range(config.n_generations):
        decoded_solutions = [split_into_routes(tour, vehicles, depot) for tour in population]
        fitness_values = [
            fitness_module.evaluate(solution, config.priority_weight, config.infeasible_penalty)
            for solution in decoded_solutions
        ]

        order = sorted(range(len(population)), key=lambda i: fitness_values[i])
        population = [population[i] for i in order]
        decoded_solutions = [decoded_solutions[i] for i in order]
        fitness_values = [fitness_values[i] for i in order]

        best_tour = population[0]
        best_solution = decoded_solutions[0]
        best_fitness_history.append(fitness_values[0])

        new_population = [population[0]]  # elitism: keep the best individual
        while len(new_population) < config.population_size:
            parent1, parent2 = roulette_wheel_selection(population, fitness_values, k=2)
            child = (
                order_crossover(parent1, parent2)
                if random.random() < config.crossover_probability
                else list(parent1)
            )
            child = mutate_fn(child, config.mutation_probability)
            new_population.append(child)

        population = new_population

    return GAResult(
        best_tour=best_tour,
        best_solution=best_solution,
        best_fitness_history=best_fitness_history,
    )


def _demo_scenario() -> tuple[list[DeliveryPoint], list[Vehicle], Depot]:
    """Small hardcoded scenario (8 points, 2 vehicles) used only to smoke-test the GA loop
    before Fase 2's real synthetic-data generator exists. Coordinates are arbitrary plane
    units, not real lat/lon — Fase 2 will replace this with São Paulo-scale coordinates.
    """
    random.seed(42)
    depot = Depot(lat=0.0, lon=0.0)
    delivery_points = [
        DeliveryPoint(id="p1", lat=2.0, lon=1.0, priority=Priority.CRITICAL, demand=2),
        DeliveryPoint(id="p2", lat=3.0, lon=4.0, priority=Priority.REGULAR, demand=2),
        DeliveryPoint(id="p3", lat=-1.0, lon=2.0, priority=Priority.REGULAR, demand=3),
        DeliveryPoint(id="p4", lat=-2.0, lon=-1.0, priority=Priority.CRITICAL, demand=1),
        DeliveryPoint(id="p5", lat=1.0, lon=-3.0, priority=Priority.REGULAR, demand=2),
        DeliveryPoint(id="p6", lat=4.0, lon=-2.0, priority=Priority.REGULAR, demand=2),
        DeliveryPoint(id="p7", lat=-3.0, lon=3.0, priority=Priority.CRITICAL, demand=2),
        DeliveryPoint(id="p8", lat=0.5, lon=4.5, priority=Priority.REGULAR, demand=2),
    ]
    vehicles = [
        Vehicle(id="v1", capacity=10, max_range=30),
        Vehicle(id="v2", capacity=10, max_range=30),
    ]
    return delivery_points, vehicles, depot


if __name__ == "__main__":
    points, fleet, depot = _demo_scenario()
    result = run_ga(points, fleet, depot, GAConfig(population_size=50, n_generations=60))

    print(f"Generations run: {len(result.best_fitness_history)}")
    print(f"Fitness - first generation: {result.best_fitness_history[0]:.2f}")
    print(f"Fitness - last generation:  {result.best_fitness_history[-1]:.2f}")
    print(f"Unrouted points: {len(result.best_solution.unrouted_points)}")

    for route in result.best_solution.routes:
        ordered_ids = [point.id for point in route.points]
        print(
            f"Vehicle {route.vehicle.id}: {ordered_ids} "
            f"(load={route.load}/{route.vehicle.capacity}, "
            f"distance={route.distance:.2f}/{route.vehicle.max_range})"
        )
