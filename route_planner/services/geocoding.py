"""Forward geocoding service for address lookup."""

import requests
from django.core.cache import cache


class GeocodingService:

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def get_coordinates(self, location: str):
        """Resolve a text location into latitude/longitude using Nominatim."""

        cache_key = f"geo:{location.strip().lower()}"
        cached = cache.get(cache_key)

        if cached:
            return cached

        response = requests.get(
            self.BASE_URL,
            params={
                "q": location,
                "format": "json",
                "limit": 1,
            },
            headers={
                "User-Agent": "fuel-route-api"
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        if not data:
            raise ValueError(f"Could not geocode '{location}'")

        coords = (float(data[0]["lat"]), float(data[0]["lon"]))

        cache.set(cache_key, coords, timeout=86400)
        return coords

    