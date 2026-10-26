from __future__ import annotations

import unittest

from src.ga_vrp.models import DeliveryPoint, Priority, Route, Solution, Vehicle
from src.llm.evaluation import collect_responses
from src.llm.prompts import build_messages
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

    def test_question_is_required(self) -> None:
        with self.assertRaises(ValueError):
            build_messages("ask", self.solution)

    def test_provider_falls_back(self) -> None:
        self.assertEqual(FallbackProvider(_FailingProvider(), _WorkingProvider()).complete([]), "fallback response")

    def test_evaluation_collects_all_three_tasks(self) -> None:
        record = collect_responses(self.solution, _WorkingProvider())
        self.assertEqual([case["task"] for case in record["cases"]], ["instructions", "report", "ask"])
        self.assertTrue(all(case["response"] == "fallback response" for case in record["cases"]))
        self.assertTrue(all(case["ratings"]["factual_accuracy"] is None for case in record["cases"]))
