"""Fuel station selection logic for a planned route."""

from math import ceil
import us

from route_planner.models import FuelStation


class FuelOptimizer:

    VEHICLE_RANGE = 500  # miles the vehicle can travel before a refuel stop as given by the problem statement

    def find_stops(
        self,
        distance_miles,
        route_cities,
    ):
        """Choose fuel stops based on route distance and nearby cities.

        The method estimates how many refuel stops are needed, then searches
        for the cheapest station in cities sampled from the route geometry.
        """

        stop_count = max(
            0,
            ceil(
                distance_miles /
                self.VEHICLE_RANGE
            ) - 1
        )

        if stop_count == 0:
            return []

        usable_cities = []

        for city, state in route_cities:
            if not city:
                continue

            if "county" in city.lower():
                continue

            usable_cities.append((city, state))

        if len(usable_cities) < 2:
            return []

        selected = []
        used_station_ids = set()

        for stop_num in range(1, stop_count + 1):
            ratio = stop_num / (stop_count + 1)
            city_index = int(ratio * (len(usable_cities) - 1))
            approx_mile = round(ratio * distance_miles)

            chosen_station = None
            search_order = []

            # Search bidirectionally from the ideal city position along the route.
            for offset in range(len(usable_cities)):
                forward = city_index + offset
                if forward < len(usable_cities):
                    search_order.append(usable_cities[forward])

                if offset > 0:
                    backward = city_index - offset
                    if backward >= 0:
                        search_order.append(usable_cities[backward])

            for city_name, state_name in search_order:
                state_obj = us.states.lookup(state_name)
                if not state_obj:
                    continue

                station = (
                    FuelStation.objects
                    .filter(
                        city__iexact=city_name,
                        state=state_obj.abbr,
                    )
                    .order_by("retail_price")
                    .first()
                )

                if station and station.id not in used_station_ids:
                    chosen_station = station
                    break

            if chosen_station:
                selected.append(chosen_station)
                used_station_ids.add(chosen_station.id)

        return selected
