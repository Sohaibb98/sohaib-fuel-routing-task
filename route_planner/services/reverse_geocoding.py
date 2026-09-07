"""Reverse geocoding service to resolve coordinates into city and state."""

import requests
from django.core.cache import cache


class ReverseGeocodingService:

    BASE_URL = "https://nominatim.openstreetmap.org/reverse"

    def get_city_state(
        self,
        latitude,
        longitude,
    ):
        """Return the city and state for a latitude/longitude pair."""

        cache_key = (
            f"reverse:"
            f"{round(latitude, 4)}:"
            f"{round(longitude, 4)}"
        )

        cached = cache.get(cache_key)
        if cached:
            return cached

        response = requests.get(
            self.BASE_URL,
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
            },
            headers={
                "User-Agent": "fuel-route-api"
            },
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()

        address = data.get("address", {})
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
        )
        state = address.get("state")

        result = {"city": city, "state": state}
        cache.set(cache_key, result, timeout=86400)
        return result
