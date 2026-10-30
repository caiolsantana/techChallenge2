"""Decode a GA chromosome (giant tour) into actual vehicle routes.

This is the piece that turns a flat permutation of `DeliveryPoint` into a VRP solution: it
walks the permutation once (greedy / first-fit, left to right) and assigns points to the
current vehicle's route as long as capacity and max_range (autonomy) are respected. When a
point would break either limit, the current route is closed (vehicle returns to the depot)
and the next vehicle in the fleet starts a new route with that point.

This greedy "sequential split" is simpler than the optimal shortest-path split used in some
VRP-GA literature (Prins' Split procedure), which would consider every possible cut point
and pick the cheapest combination. We use the greedy version to keep the implementation
straightforward; swapping in an optimal split later would not require changing the GA loop,
fitness function, or chromosome representation — only this module.
"""

from __future__ import annotations

from .geo import distance
from .models import Depot, DeliveryPoint, Route, Solution, Vehicle


def _route_distance(depot: Depot, points: list[DeliveryPoint]) -> float:
    if not points:
        return 0.0
    total = distance(depot, points[0])
    for a, b in zip(points, points[1:]):
        total += distance(a, b)
    total += distance(points[-1], depot)
    return total


def split_into_routes(
    giant_tour: list[DeliveryPoint], vehicles: list[Vehicle], depot: Depot
) -> Solution:
    routes: list[Route] = []
    unrouted: list[DeliveryPoint] = []

    vehicle_iter = iter(vehicles)
    current_vehicle = next(vehicle_iter, None)
    current_points: list[DeliveryPoint] = []
    current_load = 0.0

    def close_current_route() -> None:
        if current_points:
            routes.append(
                Route(
                    vehicle=current_vehicle,
                    points=list(current_points),
                    distance=_route_distance(depot, current_points),
                    load=current_load,
                )
            )

    for point in giant_tour:
        if current_vehicle is None:
            unrouted.append(point)
            continue

        candidate_points = current_points + [point]
        candidate_load = current_load + point.demand
        candidate_distance = _route_distance(depot, candidate_points)

        fits_current_vehicle = (
            candidate_load <= current_vehicle.capacity
            and candidate_distance <= current_vehicle.max_range
        )

        if fits_current_vehicle:
            current_points = candidate_points
            current_load = candidate_load
            continue

        close_current_route()
        current_vehicle = next(vehicle_iter, None)
        current_points = []
        current_load = 0.0

        if current_vehicle is None:
            unrouted.append(point)
            continue

        alone_fits = (
            point.demand <= current_vehicle.capacity
            and _route_distance(depot, [point]) <= current_vehicle.max_range
        )
        if alone_fits:
            current_points = [point]
            current_load = point.demand
        else:
            # Point is infeasible even alone (demand or distance too large for any
            # remaining vehicle) — leave the new vehicle's route empty and flag it.
            unrouted.append(point)

    close_current_route()

    return Solution(routes=routes, unrouted_points=unrouted)
