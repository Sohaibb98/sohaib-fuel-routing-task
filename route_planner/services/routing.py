"""Routing service that requests driving directions from OpenRouteService."""

import os
import requests

from django.core.cache import cache


class RoutingService:

    BASE_URL = (
        "https://api.openrouteservice.org/v2/"
        "directions/driving-car"
    )

    def __init__(self):
        self.api_key = os.getenv("ORS_API_KEY")

    def get_route(
        self,
        start_lat,
        start_lon,
        end_lat,
        end_lon,
    ):
        """Request route details and normalize the response.

        Returns a dictionary containing distance in miles and the encoded
        route geometry returned by OpenRouteService.
        """

        cache_key = (
            f"route:{round(start_lat, 4)}:"
            f"{round(start_lon, 4)}:"
            f"{round(end_lat, 4)}:"
            f"{round(end_lon, 4)}"
        )

        cached = cache.get(cache_key)
        if cached:
            return cached

        response = requests.post(
            self.BASE_URL,
            headers={
                "Authorization": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "coordinates": [
                    [start_lon, start_lat],
                    [end_lon, end_lat],
                ]
            },
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()

        summary = data["routes"][0]["summary"]
        distance_meters = summary["distance"]
        distance_miles = distance_meters * 0.000621371

        route = {
            "distance_miles": round(distance_miles, 2),
            "geometry": data["routes"][0]["geometry"],
        }

        cache.set(cache_key, route, timeout=86400)
        return route
