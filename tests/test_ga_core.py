from __future__ import annotations

import random
import unittest

from src.data.scenario import ScenarioConfig, generate_scenario
from src.ga_vrp.fitness import evaluate
from src.ga_vrp.ga import GAConfig, run_ga
from src.ga_vrp.models import Depot, DeliveryPoint, Priority, Route, Solution, Vehicle
from src.ga_vrp.operators import inversion_mutate, order_crossover, swap_mutate
from src.ga_vrp.split import split_into_routes
from src.ga_vrp.validators import all_points_visited_once, is_autonomy_respected, is_capacity_respected


class GACoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.depot = Depot(0, 0)
        self.points = [
            DeliveryPoint(f"p{i}", float(i), 0, Priority.CRITICAL if i == 1 else Priority.REGULAR, 1)
            for i in range(1, 5)
        ]
        self.vehicles = [Vehicle("v1", 2, 12), Vehicle("v2", 2, 12)]

    def test_operators_preserve_each_point_once(self) -> None:
        random.seed(9)
        parents = [self.points, list(reversed(self.points))]
        for child in (
            order_crossover(*parents),
            swap_mutate(self.points, 1),
            inversion_mutate(self.points, 1),
        ):
            self.assertEqual(sorted(point.id for point in child), sorted(point.id for point in self.points))

    def test_split_and_validators(self) -> None:
        solution = split_into_routes(self.points, self.vehicles, self.depot)
        self.assertTrue(all_points_visited_once(solution, self.points))
        self.assertEqual(len(solution.unrouted_points), 0)
        self.assertTrue(all(is_capacity_respected(route) and is_autonomy_respected(route) for route in solution.routes))

    def test_unrouted_penalty_and_priority(self) -> None:
        vehicle = self.vehicles[0]
        critical, regular = self.points[:2]
        early = Solution([Route(vehicle, [critical, regular], 4, 2)])
        late = Solution([Route(vehicle, [regular, critical], 4, 2)])
        self.assertLess(evaluate(early), evaluate(late))
        self.assertGreater(evaluate(Solution(unrouted_points=[critical])), evaluate(early))

    def test_ga_history_and_accounting(self) -> None:
        random.seed(5)
        result = run_ga(self.points, self.vehicles, self.depot, GAConfig(population_size=12, n_generations=8, crossover_probability=0))
        self.assertEqual(len(result.best_fitness_history), 8)
        self.assertTrue(all_points_visited_once(result.best_solution, self.points))
        self.assertTrue(all(is_capacity_respected(route) and is_autonomy_respected(route) for route in result.best_solution.routes))

    def test_scenario_is_reproducible(self) -> None:
        config = ScenarioConfig(seed=7, n_points=10, n_vehicles=2)
        self.assertEqual(generate_scenario(config), generate_scenario(config))
