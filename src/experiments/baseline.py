"""A feasible nearest-neighbor baseline using the same fleet and constraints as the GA."""

from __future__ import annotations

from ..ga_vrp.geo import distance
from ..ga_vrp.models import Depot, DeliveryPoint, Route, Solution, Vehicle


def nearest_neighbor(
    delivery_points: list[DeliveryPoint], vehicles: list[Vehicle], depot: Depot
) -> Solution:
    remaining = list(delivery_points)
    routes: list[Route] = []
    for vehicle in vehicles:
        points: list[DeliveryPoint] = []
        load = 0.0
        traveled = 0.0
        current = depot
        while remaining:
            candidates = [
                point
                for point in remaining
                if load + point.demand <= vehicle.capacity
                and traveled + distance(current, point) + distance(point, depot) <= vehicle.max_range
            ]
            if not candidates:
                break
            point = min(candidates, key=lambda item: (distance(current, item), item.id))
            traveled += distance(current, point)
            load += point.demand
            points.append(point)
            remaining.remove(point)
            current = point
        if points:
            routes.append(Route(vehicle, points, traveled + distance(current, depot), load))
    return Solution(routes=routes, unrouted_points=remaining)
