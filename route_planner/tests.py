from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class RouteAPIViewTests(TestCase):
    def test_invalid_non_usa_city_returns_400(self):
        client = APIClient()

        with patch(
            "route_planner.views.GeocodingService.get_coordinates",
            side_effect=ValueError("'Paris' is not in the USA."),
        ):
            response = client.post(
                "/api/route/",
                {"start": "Paris", "finish": "Dallas, TX"},
                format="json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("not in the USA", response.json()["detail"])
