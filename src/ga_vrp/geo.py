"""Small geometry helper shared by split.py (route distance) and anything else that needs it.

Coordinates are treated as plane (x=lon, y=lat) for a simple Euclidean distance — accurate
enough for the synthetic, city-scale scenarios used in this project (same simplification the
FIAP base_code uses for pixel coordinates). Not meant for real-world great-circle distances.
"""

from __future__ import annotations

import math
from typing import Union

from .models import DeliveryPoint, Depot

Point = Union[DeliveryPoint, Depot]


def distance(a: Point, b: Point) -> float:
    return math.sqrt((a.lat - b.lat) ** 2 + (a.lon - b.lon) ** 2)
