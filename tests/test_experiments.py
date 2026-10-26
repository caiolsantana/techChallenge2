from __future__ import annotations

import unittest

from src.data.scenario import GeneratedScenario
from src.experiments.baseline import nearest_neighbor
from src.experiments.runner import solution_metrics
from src.ga_vrp.models import Depot, DeliveryPoint, Priority, Vehicle


class ExperimentTests(unittest.TestCase):
    def test_nearest_neighbor_obeys_limits_and_accounts_for_every_point(self) -> None:
        depot = Depot(0, 0)
        points = [
            DeliveryPoint("near", 1, 0, Priority.REGULAR, 1),
            DeliveryPoint("middle", 2, 0, Priority.CRITICAL, 1),
            DeliveryPoint("far", 10, 0, Priority.REGULAR, 1),
        ]
        vehicles = [Vehicle("v1", 2, 5)]
        scenario = GeneratedScenario(depot, points, vehicles)
        solution = nearest_neighbor(points, vehicles, depot)
        metrics = solution_metrics(solution, scenario)
        self.assertEqual([point.id for point in solution.routes[0].points], ["near", "middle"])
        self.assertEqual([point.id for point in solution.unrouted_points], ["far"])
        self.assertEqual(metrics["capacity_violations"], 0)
        self.assertEqual(metrics["autonomy_violations"], 0)
        self.assertTrue(metrics["all_points_accounted_for"])
