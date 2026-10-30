from __future__ import annotations

import unittest

from src.ga_vrp.geo import haversine_km, route_km
from src.ga_vrp.models import DeliveryPoint, Depot, Priority, Route, Solution, Vehicle
from src.llm.evaluation import collect_responses
from src.llm.prompts import build_messages, solution_context
from src.llm.providers import FallbackProvider


class _FailingProvider:
    def complete(self, messages: list[dict[str, str]]) -> str:
        raise RuntimeError("unavailable")


class _WorkingProvider:
    def complete(self, messages: list[dict[str, str]]) -> str:
        return "fallback response"


class LLMTests(unittest.TestCase):
    def setUp(self) -> None:
        point = DeliveryPoint("dp1", -23.5, -46.6, Priority.CRITICAL, 2)
        self.solution = Solution(routes=[Route(Vehicle("v1", 10, 1), [point], 0.25, 2)])

    def test_prompts_include_actual_route_data_and_units(self) -> None:
        messages = build_messages("instructions", self.solution)
        self.assertIn("dp1", messages[1]["content"])
        self.assertIn("unidades de coordenada", messages[0]["content"])
        self.assertIn('"priority": "critical"', messages[1]["content"])

    def test_haversine_matches_one_degree_of_latitude(self) -> None:
        self.assertAlmostEqual(haversine_km(Depot(-23.0, -46.6), Depot(-24.0, -46.6)), 111.19, places=2)

    def test_context_adds_straight_line_km_when_depot_is_known(self) -> None:
        depot = Depot(-23.55, -46.63)
        expected_km = round(route_km(depot, self.solution.routes[0].points), 1)
        context = solution_context(self.solution, detail="summary", depot=depot)
        self.assertIn(f'"total_distance_km": {expected_km}', context)
        self.assertIn(f'"distance_km": {expected_km}', context)
        self.assertNotIn("distance_km", solution_context(self.solution, detail="summary"))

    def test_question_is_required(self) -> None:
        with self.assertRaises(ValueError):
            build_messages("ask", self.solution)

    def test_report_uses_precomputed_counts(self) -> None:
        context = solution_context(self.solution, detail="summary")
        self.assertIn('"total_stops": 1', context)
        self.assertIn('"stop_count": 1', context)
        self.assertNotIn('"stops":', context)

    def test_critical_question_uses_only_critical_index(self) -> None:
        messages = build_messages("ask", self.solution, "Quais entregas são críticas?")
        self.assertIn('"critical_stops"', messages[1]["content"])
        self.assertNotIn('"routes"', messages[1]["content"])

    def test_provider_falls_back(self) -> None:
        self.assertEqual(FallbackProvider(_FailingProvider(), _WorkingProvider()).complete([]), "fallback response")

    def test_evaluation_collects_all_three_tasks(self) -> None:
        record = collect_responses(self.solution, _WorkingProvider())
        self.assertEqual([case["task"] for case in record["cases"]], ["instructions", "report", "ask"])
        self.assertTrue(all(case["response"] == "fallback response" for case in record["cases"]))
        self.assertTrue(all(case["ratings"]["factual_accuracy"] is None for case in record["cases"]))
        self.assertEqual(record["reference"]["total_stops"], 1)
        self.assertEqual(record["reference"]["critical_stops"][0]["id"], "dp1")
