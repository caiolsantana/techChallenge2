from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from src.ga_vrp.models import Depot, DeliveryPoint, Priority, Route, Solution, Vehicle
from src.visualization.convergence import save_convergence
from src.visualization.routes_map import save_routes_map


class VisualizationTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "matplotlib is not installed")
    def test_convergence_png(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            output = save_convergence([10, 8, 7], Path(directory) / "plot.png")
            self.assertTrue(output.read_bytes().startswith(b"\x89PNG"))

    @unittest.skipUnless(importlib.util.find_spec("folium"), "folium is not installed")
    def test_map_contains_routes_and_priority(self) -> None:
        point = DeliveryPoint("dp1", -23.5, -46.6, Priority.CRITICAL, 2)
        solution = Solution([Route(Vehicle("v1", 10, 1), [point], 0.25, 2)])
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            output = save_routes_map(solution, Depot(-23.55, -46.63), Path(directory) / "routes.html")
            content = output.read_text(encoding="utf-8")
            self.assertIn("dp1", content)
            self.assertIn("CRÍTICA", content)
