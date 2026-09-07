"""Extract route cities from encoded route geometry."""

import polyline

from django.core.cache import cache

from .reverse_geocoding import ReverseGeocodingService


class RouteCityService:

    def get_route_cities(
        self,
        encoded_geometry,
    ):
        """Decode route geometry and map sampled points to cities.

        This service samples the route polyline to reduce reverse geocoding
        calls, then returns a deduplicated sequence of city/state pairs.
        """

        cache_key = f"route_cities:{hash(encoded_geometry)}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        coordinates = polyline.decode(encoded_geometry)
        sampled = coordinates[::1000]

        if coordinates:
            sampled.append(coordinates[-1])

        cities = []
        reverse_service = ReverseGeocodingService()

        for lat, lon in sampled:
            location = reverse_service.get_city_state(lat, lon)
            if location["city"]:
                cities.append(
                    (
                        location["city"].strip().lower(),
                        location["state"].strip().lower()
                        if location["state"]
                        else ""
                    )
                )

        result = list(dict.fromkeys(cities))
        cache.set(cache_key, result, timeout=86400)
        return result
