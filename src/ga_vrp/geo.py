"""Small geometry helper shared by split.py (route distance) and anything else that needs it.

Coordinates are treated as plane (x=lon, y=lat) for a simple Euclidean distance — accurate
enough for the synthetic, city-scale scenarios used in this project (same simplification the
FIAP base_code uses for pixel coordinates). Not meant for real-world great-circle distances.

`haversine_km` / `route_km` give the straight-line kilometres for reporting only (LLM layer);
the GA itself keeps optimizing `distance`.
"""

from __future__ import annotations

import math
from typing import Union

from .models import DeliveryPoint, Depot

Point = Union[DeliveryPoint, Depot]

EARTH_RADIUS_KM = 6371.0


def distance(a: Point, b: Point) -> float:
    return math.sqrt((a.lat - b.lat) ** 2 + (a.lon - b.lon) ** 2)


def haversine_km(a: Point, b: Point) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a.lat, a.lon, b.lat, b.lon))
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))


def route_km(depot: Depot, points: list[DeliveryPoint]) -> float:
    """Straight-line km of depot -> points -> depot; streets make the real trip longer."""
    path = [depot, *points, depot] if points else []
    return sum(haversine_km(a, b) for a, b in zip(path, path[1:]))
