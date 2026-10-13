"""Fitness function: turns a decoded `Solution` into a single score to minimize.

score = total_distance
      + priority_weight * priority_penalty      (critical points served late in their route)
      + infeasible_penalty * number_of_unrouted_points

`priority_penalty` is the sum, over every CRITICAL point, of its position in the route
divided by the route length (0 = served first, ~1 = served last) — so solutions that visit
critical points earlier in each route score better, without needing real delivery-time
simulation.

`infeasible_penalty` is deliberately large so that any solution leaving points unrouted
(fleet too small for the giant tour as split) always loses to a solution that routes
everyone, while still letting the GA explore those individuals instead of discarding them
outright (soft constraint, not a hard rejection).
"""

from __future__ import annotations

from .models import Priority, Solution

DEFAULT_PRIORITY_WEIGHT = 50.0
DEFAULT_INFEASIBLE_PENALTY = 10_000.0


def evaluate(
    solution: Solution,
    priority_weight: float = DEFAULT_PRIORITY_WEIGHT,
    infeasible_penalty: float = DEFAULT_INFEASIBLE_PENALTY,
) -> float:
    priority_penalty = 0.0
    for route in solution.routes:
        n = len(route.points)
        if n == 0:
            continue
        for index, point in enumerate(route.points):
            if point.priority == Priority.CRITICAL:
                priority_penalty += index / n

    return (
        solution.total_distance
        + priority_weight * priority_penalty
        + infeasible_penalty * len(solution.unrouted_points)
    )
