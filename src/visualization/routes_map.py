"""Render a decoded VRP solution as an interactive Folium map."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..ga_vrp.models import Depot, Priority, Solution

COLORS = ("blue", "green", "purple", "orange", "darkred", "cadetblue", "darkgreen")


def save_routes_map(solution: Solution, depot: Depot, output: str | Path) -> Path:
    import folium

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    route_map = folium.Map(location=[depot.lat, depot.lon], zoom_start=11, control_scale=True)
    folium.Marker(
        [depot.lat, depot.lon], tooltip="Depósito", icon=folium.Icon(color="black", icon="home")
    ).add_to(route_map)
    bounds = [[depot.lat, depot.lon]]

    for index, route in enumerate(solution.routes):
        color = COLORS[index % len(COLORS)]
        coordinates = [[depot.lat, depot.lon]]
        for order, point in enumerate(route.points, start=1):
            location = [point.lat, point.lon]
            coordinates.append(location)
            bounds.append(location)
            priority = "CRÍTICA" if point.priority == Priority.CRITICAL else "Regular"
            tooltip = f"{escape(route.vehicle.id)} · parada {order} · {escape(point.id)} · {priority}"
            popup = f"Demanda: {point.demand:g} unidades"
            folium.CircleMarker(
                location,
                radius=8 if point.priority == Priority.CRITICAL else 5,
                color=color,
                fill=True,
                fill_opacity=0.9,
                tooltip=tooltip,
                popup=popup,
            ).add_to(route_map)
        coordinates.append([depot.lat, depot.lon])
        folium.PolyLine(
            coordinates,
            color=color,
            weight=4,
            opacity=0.8,
            tooltip=f"{escape(route.vehicle.id)} · {len(route.points)} paradas · distância {route.distance:.4f} unidades de coordenada",
        ).add_to(route_map)

    for point in solution.unrouted_points:
        location = [point.lat, point.lon]
        bounds.append(location)
        folium.Marker(
            location,
            tooltip=f"NÃO ROTEADO · {escape(point.id)}",
            icon=folium.Icon(color="red", icon="exclamation-sign"),
        ).add_to(route_map)

    if len(bounds) > 1:
        route_map.fit_bounds(bounds)
    route_map.save(str(output))
    return output
