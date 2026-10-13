"""Pure, isolated constraint-checking functions — no GA/fitness logic here.

These are written to be trivially unit-testable in isolation (Fase 5 / @andersonmares adds
the pytest suite around these). Each function takes already-decoded data and returns a bool,
so a test only needs to construct a `Route`/`Solution` fixture, no GA run required.
"""

from __future__ import annotations

from .models import DeliveryPoint, Route, Solution


def is_capacity_respected(route: Route) -> bool:
    return route.load <= route.vehicle.capacity


def is_autonomy_respected(route: Route) -> bool:
    return route.distance <= route.vehicle.max_range


def all_points_visited_once(solution: Solution, all_points: list[DeliveryPoint]) -> bool:
    """True if every point in `all_points` appears exactly once across the solution's
    routes + unrouted points (no duplicates, nothing missing)."""
    visited_ids = [point.id for route in solution.routes for point in route.points]
    visited_ids += [point.id for point in solution.unrouted_points]

    expected_ids = sorted(point.id for point in all_points)
    return sorted(visited_ids) == expected_ids
