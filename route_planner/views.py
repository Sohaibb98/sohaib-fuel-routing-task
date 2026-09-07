from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from route_planner.services.route_city_service import (
    RouteCityService
)

from .serializers import (
    RouteRequestSerializer
)

from .services.geocoding import (
    GeocodingService
)

from .services.routing import (
    RoutingService
)

from .services.fuel_optimizer import (
    FuelOptimizer
)

from .services.cost_calculator import (
    CostCalculator
)


class RouteAPIView(APIView):

    @staticmethod
    def _validate_us_location(location_name, coordinates):
        latitude, longitude = coordinates

        if not (-18.0 <= latitude <= 72.0 and -170.0 <= longitude <= -65.0):
            raise ValidationError(
                {"detail": f"'{location_name}' is not in the USA."}
            )

    def post(self, request):

        serializer = (
            RouteRequestSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        start = (
            serializer.validated_data["start"]
        )

        finish = (
            serializer.validated_data["finish"]
        )

        geocoder = GeocodingService()

        try:
            start_coords = geocoder.get_coordinates(start)
            finish_coords = geocoder.get_coordinates(finish)
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc

        self._validate_us_location(start, start_coords)
        self._validate_us_location(finish, finish_coords)

        start_lat, start_lon = start_coords
        end_lat, end_lon = finish_coords

        route = (
            RoutingService().get_route(
                start_lat,
                start_lon,
                end_lat,
                end_lon,
            )
        )

        cities = (
            RouteCityService()
            .get_route_cities(
                route["geometry"]
            )
        )

        fuel_stops = (
            FuelOptimizer().find_stops(
                route["distance_miles"],
                cities,
            )
        )

        total_cost = (
            CostCalculator().calculate(
                route["distance_miles"],
                fuel_stops,
            )
        )

        return Response({
            "distance_miles":
                route["distance_miles"],

            "fuel_stops": [
                {
                    "stop_number": idx + 1,

                    "suggested_stop_mile":
                        (idx + 1) * 500,

                    "name": s.name,

                    "city": s.city,

                    "state": s.state,

                    "price": float(
                        s.retail_price
                    ),
                }

                for idx, s in enumerate(
                    fuel_stops
                )
            ],

            "estimated_fuel_cost":
                total_cost,

            "route_points_count": len(
                route["geometry"]
            ),

            "route_geometry":
                route["geometry"],

        })