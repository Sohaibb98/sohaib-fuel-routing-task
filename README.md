# Fuel Route Planner API

## Overview

This Django REST API calculates an optimal fuel plan for a road trip within the USA.

Given a start and destination location, the API:

* Calculates the driving route
* Identifies cities along the route
* Finds cost-effective fuel stations from the provided fuel price dataset
* Estimates total fuel cost assuming 10 MPG
* Supports multiple fuel stops for trips longer than 500 miles

---

## Tech Stack

* Python 3.13+
* Django 6
* Django REST Framework
* SQLite
* OpenRouteService (routing)
* OpenStreetMap Nominatim (geocoding / reverse geocoding)

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd fuel-route-planner
```

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

or on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create .env file

```env
ORS_API_KEY=your_openrouteservice_api_key
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Load fuel station data

```bash
python manage.py import_fuel_data fuel-prices-for-be-assessment.csv
```

### 7. Start server

```bash
python manage.py runserver
```

---

## API

### POST /api/route/

Request:

```json
{
  "start": "Dallas, TX",
  "finish": "Los Angeles, CA"
}
```

Response:

```json
{
  "distance_miles": 1436.01,
  "fuel_stops": [
    {
      "stop_number": 1,
      "suggested_stop_mile": 500,
      "name": "TRAVELING TIGER CENTER",
      "city": "Sierra Blanca",
      "state": "TX",
      "price": 3.156
    }
  ],
  "estimated_fuel_cost": 451.98,
  "route_points_count": 20798,
	"route_geometry": "...BeB?uE@?fDA|@Ab@Ar@"
}
```

---

## Routing Strategy

1. Start and destination are geocoded using OpenStreetMap Nominatim.
2. OpenRouteService is called once to generate the route.
3. Route geometry is sampled and reverse geocoded to determine cities along the route.
4. Fuel stations are selected from the provided fuel-price dataset based on cities encountered along the route.
5. Fuel cost is calculated assuming:

   * Vehicle range: 500 miles
   * Fuel efficiency: 10 MPG

---

## Performance

To reduce external API usage and improve response times, the application caches:

* Geocoding results
* Routing results
* Route city extraction results
