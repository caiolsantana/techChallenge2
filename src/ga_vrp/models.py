"""Domain model for the VRP (Vehicle Routing Problem) used by the genetic algorithm.

These are plain dataclasses — no GA logic lives here. `Solution` is the decoded output of
`split.split_into_routes()`, not the GA chromosome itself (the chromosome is just
`List[DeliveryPoint]`, see `operators.py`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    CRITICAL = "critical"
    REGULAR = "regular"


@dataclass(frozen=True)
class DeliveryPoint:
    """A single hospital unit / delivery address to be visited."""

    id: str
    lat: float
    lon: float
    priority: Priority
    demand: float  # units of cargo consumed from the vehicle's capacity


@dataclass(frozen=True)
class Depot:
    """Central hospital / warehouse where every route starts and ends."""

    lat: float
    lon: float


@dataclass(frozen=True)
class Vehicle:
    """A delivery vehicle available in the fleet."""

    id: str
    capacity: float  # max total demand it can carry
    max_range: float  # max total route distance (round trip from the depot)


@dataclass
class Route:
    """One vehicle's decoded route: depot -> points... -> depot."""

    vehicle: Vehicle
    points: list[DeliveryPoint] = field(default_factory=list)
    distance: float = 0.0
    load: float = 0.0


@dataclass
class Solution:
    """Full decoded VRP solution: one Route per vehicle actually used."""

    routes: list[Route] = field(default_factory=list)
    unrouted_points: list[DeliveryPoint] = field(default_factory=list)

    @property
    def total_distance(self) -> float:
        return sum(route.distance for route in self.routes)
