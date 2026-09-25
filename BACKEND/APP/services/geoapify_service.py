import os
import math
import requests

from dotenv import load_dotenv

load_dotenv()


GEOAPIFY_API_URL = "https://api.geoapify.com/v2/places"


# --------------------------------------------------
# DISTANCE
# --------------------------------------------------

def calculate_distance_km(lat1, lon1, lat2, lon2):
    """Calculate straight-line distance using the Haversine formula."""

    earth_radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return round(
        earth_radius_km * c,
        2
    )


# --------------------------------------------------
# GEOAPIFY CATEGORY MAPPING
# --------------------------------------------------

def get_geoapify_category(category):

    categories = {

        # Financial
        "bank": "service.financial.bank",
        "atm": "service.financial.atm",

        # Food
        "restaurant": "catering.restaurant",
        "cafe": "catering.cafe",
        "fast_food": "catering.fast_food",
        "bakery": "catering.cafe.cake",

        # Healthcare
        "hospital": "healthcare.hospital",
        "pharmacy": "healthcare.pharmacy",
        "doctor": "healthcare.doctor",
        "dentist": "healthcare.dentist",

        # Emergency / Services
        "police": "service.police",
        "ambulance": "service.ambulance_station",

        # Vehicle
        "fuel": "service.vehicle.fuel",
        "mechanic": "service.vehicle.repair",
        "car_repair": "service.vehicle.repair.car",
        "bike_repair": "service.vehicle.repair.motorcycle",
        "car_wash": "service.vehicle.car_wash",
        "ev_charging": "service.vehicle.charging_station",

        # Accommodation
        "hotel": "accommodation.hotel",
        "hostel": "accommodation.hostel",
        "guest_house": "accommodation.guest_house",
        "motel": "accommodation.motel",

        # Shopping
        "supermarket": "commercial.supermarket",
        "shopping_mall": "commercial.shopping_mall",

        # Education
        "school": "education.school",
        "college": "education.college",
        "university": "education.university",
        "library": "education.library",

        # Transport
        "airport": "airport",
        "bus_station": "public_transport.bus",
        "train_station": "public_transport.train",
        "taxi": "service.taxi",

        # Other services
        "parking": "parking",
        "laundry": "service.cleaning.laundry",
        "dry_cleaning": "service.cleaning.dry_cleaning",
        "hairdresser": "service.beauty.hairdresser",
        "spa": "service.beauty.spa",
        "post_office": "service.post",

        # Recreation
        "park": "leisure.park",
        "playground": "leisure.playground",

        # Tourism / Entertainment
        "tourist_attraction": "tourism.attraction",
        "cinema": "entertainment.cinema",
        "museum": "entertainment.museum",
        "zoo": "entertainment.zoo",
        "aquarium": "entertainment.aquarium",

        # Other
        "veterinary": "healthcare.veterinary",
    }

    return categories.get(category)


# --------------------------------------------------
# PLACE VALIDATION
# --------------------------------------------------

def is_valid_place(properties, category):

    name = (
        properties.get("name")
        or properties.get("brand")
        or properties.get("operator")
        or ""
    ).strip()

    if not name:
        return False

    excluded_words = [
        "main road",
        "highway",
        "road",
        "street",
        "junction",
        "crossing",
        "flyover",
        "bridge",
    ]

    name_lower = name.lower()

    for word in excluded_words:

        if (
            name_lower == word
            or name_lower.endswith(f" {word}")
        ):
            return False

    result_categories = properties.get(
        "categories",
        []
    )

    if result_categories:

        category_text = (
            " ".join(result_categories)
            .lower()
        )

        expected_category = get_geoapify_category(
            category
        )

        if expected_category:

            expected_root = (
                expected_category.split(".")[0]
            )

            if expected_root not in category_text:

                # Tourist fallback can contain
                # several valid tourism categories.
                if category == "tourist_attraction":

                    tourist_words = [
                        "tourism",
                        "attraction",
                        "museum",
                        "zoo",
                        "aquarium",
                        "sights",
                        "monument",
                        "memorial",
                        "viewpoint",
                        "historic",
                        "heritage",
                        "entertainment",
                    ]

                    if not any(
                        word in category_text
                        for word in tourist_words
                    ):
                        return False

                else:
                    return False

    return True


# --------------------------------------------------
# GEOAPIFY API REQUEST
# --------------------------------------------------

def _request_geoapify(
    latitude,
    longitude,
    geoapify_category,
    radius,
    limit,
):

    api_key = os.getenv(
        "GEOAPIFY_API_KEY"
    )

    if not api_key:

        print(
            "GEOAPIFY_API_KEY not found."
        )

        return []

    params = {
        "categories": geoapify_category,
        "filter": (
            f"circle:{longitude},"
            f"{latitude},"
            f"{radius}"
        ),
        "bias": (
            f"proximity:{longitude},"
            f"{latitude}"
        ),
        "limit": limit,
        "lang": "en",
        "apiKey": api_key,
    }

    try:

        response = requests.get(
            GEOAPIFY_API_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "features",
            []
        )

    except requests.RequestException as error:

        print(
            f"Geoapify request failed: {error}"
        )

        if (
            hasattr(error, "response")
            and error.response is not None
        ):

            print(
                "Geoapify response:",
                error.response.text[:1000],
            )

        return []


# --------------------------------------------------
# CONVERT GEOAPIFY FEATURES
# --------------------------------------------------

def _convert_features_to_places(
    features,
    latitude,
    longitude,
    category,
):

    places = []

    for feature in features:

        properties = feature.get(
            "properties",
            {}
        )

        geometry = feature.get(
            "geometry",
            {}
        )

        if not is_valid_place(
            properties,
            category,
        ):
            continue

        coordinates = geometry.get(
            "coordinates",
            []
        )

        if len(coordinates) < 2:
            continue

        place_longitude = coordinates[0]
        place_latitude = coordinates[1]

        name = (
            properties.get("name")
            or properties.get("brand")
            or properties.get("operator")
        )

        if not name:
            continue

        distance_km = calculate_distance_km(
            latitude,
            longitude,
            place_latitude,
            place_longitude,
        )

        places.append(
            {
                "name": name,
                "brand": properties.get(
                    "brand"
                ),
                "operator": properties.get(
                    "operator"
                ),
                "type": category,
                "address": properties.get(
                    "formatted"
                ),
                "phone": properties.get(
                    "phone"
                ),
                "website": properties.get(
                    "website"
                ),
                "latitude": place_latitude,
                "longitude": place_longitude,
                "distance_km": distance_km,
                "osm_id": properties.get(
                    "osm_id"
                ),
                "osm_type": "geoapify",
            }
        )

    places.sort(
        key=lambda place: place[
            "distance_km"
        ]
    )

    return places


# --------------------------------------------------
# ATM FALLBACK
# --------------------------------------------------

def _search_atm_fallback(
    latitude,
    longitude,
    radius,
    limit,
):

    features = _request_geoapify(
        latitude=latitude,
        longitude=longitude,
        geoapify_category=(
            "service.financial.bank"
        ),
        radius=radius,
        limit=50,
    )

    atm_features = []

    for feature in features:

        properties = feature.get(
            "properties",
            {}
        )

        name = (
            properties.get("name")
            or properties.get("brand")
            or properties.get("operator")
            or ""
        ).strip()

        name_lower = name.lower()

        if (
            "atm" in name_lower
            or "cash machine" in name_lower
            or "cashpoint" in name_lower
        ):

            atm_features.append(
                feature
            )

    places = _convert_features_to_places(
        features=atm_features,
        latitude=latitude,
        longitude=longitude,
        category="atm",
    )

    return places[:limit]


# --------------------------------------------------
# TOURIST ATTRACTION FALLBACK
# --------------------------------------------------

def _search_tourist_fallback(
    latitude,
    longitude,
    radius,
    limit,
):

    """
    Broader tourism search.

    Geoapify may return zero results for
    tourism.attraction in some locations.

    We therefore query several real tourism-
    related categories and combine the results.
    """

    tourism_categories = [

        "tourism",

        "tourism.attraction",

        "tourism.sights",

        "tourism.information",

        "entertainment.museum",

        "entertainment.zoo",

        "entertainment.aquarium",
    ]

    all_features = []

    for category in tourism_categories:

        features = _request_geoapify(
            latitude=latitude,
            longitude=longitude,
            geoapify_category=category,
            radius=radius,
            limit=50,
        )

        all_features.extend(
            features
        )

    # Remove duplicate places
    unique_features = {}

    for feature in all_features:

        properties = feature.get(
            "properties",
            {}
        )

        osm_id = properties.get(
            "osm_id"
        )

        name = (
            properties.get("name")
            or properties.get("brand")
            or properties.get("operator")
            or ""
        ).strip()

        if not name:
            continue

        if osm_id:

            key = str(osm_id)

        else:

            coordinates = (
                feature
                .get("geometry", {})
                .get("coordinates", [])
            )

            key = (
                f"{name.lower()}|"
                f"{coordinates}"
            )

        if key not in unique_features:

            unique_features[key] = feature

    # Keep tourism-related places
    tourist_features = []

    tourism_words = [

        "tourism",
        "attraction",
        "museum",
        "zoo",
        "aquarium",
        "sights",
        "monument",
        "memorial",
        "viewpoint",
        "historic",
        "heritage",
        "entertainment",
    ]

    for feature in unique_features.values():

        properties = feature.get(
            "properties",
            {}
        )

        categories = properties.get(
            "categories",
            []
        )

        category_text = (
            " ".join(categories)
            .lower()
        )

        if any(
            word in category_text
            for word in tourism_words
        ):

            tourist_features.append(
                feature
            )

    places = _convert_features_to_places(
        features=tourist_features,
        latitude=latitude,
        longitude=longitude,
        category="tourist_attraction",
    )

    places.sort(
        key=lambda place: place[
            "distance_km"
        ]
    )

    return places[:limit]


# --------------------------------------------------
# MAIN SEARCH FUNCTION
# --------------------------------------------------

def search_geoapify_places(
    latitude,
    longitude,
    category,
    radius=10000,
    limit=20,
):

    api_key = os.getenv(
        "GEOAPIFY_API_KEY"
    )

    if not api_key:

        print(
            "GEOAPIFY_API_KEY not found."
        )

        return []

    geoapify_category = get_geoapify_category(
        category
    )

    if not geoapify_category:

        print(
            f"Unsupported Geoapify category: "
            f"{category}"
        )

        return []

    # --------------------------------------------------
    # PRIMARY SEARCH
    # --------------------------------------------------

    features = _request_geoapify(
        latitude=latitude,
        longitude=longitude,
        geoapify_category=geoapify_category,
        radius=radius,
        limit=limit,
    )

    places = _convert_features_to_places(
        features=features,
        latitude=latitude,
        longitude=longitude,
        category=category,
    )

    # --------------------------------------------------
    # ATM FALLBACK
    # --------------------------------------------------

    if category == "atm" and not places:

        print(
            "Dedicated ATM search returned "
            "no results. Trying bank-category "
            "ATM fallback..."
        )

        places = _search_atm_fallback(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            limit=limit,
        )

    # --------------------------------------------------
    # TOURIST FALLBACK
    # --------------------------------------------------

    if (
        category == "tourist_attraction"
        and not places
    ):

        print(
            "Dedicated tourist search returned "
            "no results. Trying broader "
            "tourism categories..."
        )

        places = _search_tourist_fallback(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            limit=limit,
        )

    # --------------------------------------------------
    # FINAL SORT
    # --------------------------------------------------

    places.sort(
        key=lambda place: place[
            "distance_km"
        ]
    )

    return places