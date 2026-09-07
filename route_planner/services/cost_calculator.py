"""Fuel cost estimation for a planned route."""


class CostCalculator:

    MPG = 10  # assumed average vehicle fuel efficiency in miles per gallon

    def calculate(
        self,
        distance_miles,
        fuel_stops,
    ):
        """Estimate the fuel cost for the given route distance.

        The calculation uses a fixed MPG assumption and the average
        retail price of the suggested fuel stops.
        """

        gallons_needed = distance_miles / self.MPG

        if not fuel_stops:
            return 0

        avg_price = (
            sum(
                float(s.retail_price)
                for s in fuel_stops
            )
            / len(fuel_stops)
        )

        return round(gallons_needed * avg_price, 2)
