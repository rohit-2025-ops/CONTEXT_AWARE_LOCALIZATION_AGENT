import requests
from math import radians, sin, cos, sqrt, atan2


PLACE_CATEGORIES = {
    "cafe": {"osm_key": "amenity", "osm_value": "cafe"},
    "restaurant": {"osm_key": "amenity", "osm_value": "restaurant"},
    "hospital": {"osm_key": "amenity", "osm_value": "hospital"},
    "pharmacy": {"osm_key": "amenity", "osm_value": "pharmacy"},
    "police": {"osm_key": "amenity", "osm_value": "police"},
    "bank": {"osm_key": "amenity", "osm_value": "bank"},
    "fuel": {"osm_key": "amenity", "osm_value": "fuel"},
    "school": {"osm_key": "amenity", "osm_value": "school"},
    "hotel": {"osm_key": "tourism", "osm_value": "hotel"},
    "atm": {"osm_key": "amenity", "osm_value": "atm"},
}

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
]

SEARCH_RADII = [1500, 3000, 5000, 10000]


def get_location(latitude: float, longitude: float):
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return {
            "area": "Unknown area", "city": "Unknown city",
            "district": "Unknown district", "state": "Unknown state",
            "country": "Unknown country", "postcode": None,
            "road": None, "house_number": None, "display_name": None,
            "latitude": latitude, "longitude": longitude,
        }

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": latitude, "lon": longitude,
                "format": "jsonv2", "addressdetails": 1,
                "zoom": 18, "layer": "address",
            },
            headers={"User-Agent": "Context-Aware-Localization-Agent/1.0"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})

        area = (
            address.get("neighbourhood") or address.get("suburb")
            or address.get("quarter") or address.get("residential")
            or address.get("hamlet") or address.get("village")
        )
        city = (
            address.get("city") or address.get("town")
            or address.get("municipality") or address.get("village")
        )
        district = (
            address.get("county") or address.get("state_district")
            or address.get("district") or address.get("region")
        )

        return {
            "area": area or city or "Unknown area",
            "city": city or "Unknown city",
            "district": district or "Unknown district",
            "state": address.get("state") or "Unknown state",
            "country": address.get("country") or "Unknown country",
            "postcode": (
                address.get("postcode")
                or address.get("postalcode")
                or address.get("postal_code")
            ),
            "road": (
                address.get("road") or address.get("pedestrian")
                or address.get("street")
            ),
            "house_number": address.get("house_number"),
            "display_name": data.get("display_name"),
            "latitude": latitude,
            "longitude": longitude,
        }

    except (requests.RequestException, ValueError, TypeError):
        return {
            "area": "Unknown area", "city": "Unknown city",
            "district": "Unknown district", "state": "Unknown state",
            "country": "Unknown country", "postcode": None,
            "road": None, "house_number": None, "display_name": None,
            "latitude": latitude, "longitude": longitude,
        }


def calculate_distance(latitude1, longitude1, latitude2, longitude2):
    earth_radius = 6371.0
    lat1 = radians(latitude1)
    lat2 = radians(latitude2)
    delta_lat = radians(latitude2 - latitude1)
    delta_lon = radians(longitude2 - longitude1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(earth_radius * c, 2)


def build_tag_filter(category):
    config = PLACE_CATEGORIES.get(category)
    if not config:
        return None
    return config["osm_key"], config["osm_value"]


def get_element_coordinates(element):
    if element.get("type") == "node":
        return element.get("lat"), element.get("lon")

    center = element.get("center", {})
    return center.get("lat"), center.get("lon")


def get_place_name(tags):
    return (
        tags.get("name")
        or tags.get("official_name")
        or tags.get("brand")
        or tags.get("operator")
        or tags.get("short_name")
        or "Unnamed place"
    )


def get_place_address(tags):
    parts = []

    for key in ["addr:housenumber", "addr:street",
                "addr:neighbourhood", "addr:suburb",
                "addr:place", "addr:city", "addr:town",
                "addr:village", "addr:postcode"]:
        value = tags.get(key)
        if value and value not in parts:
            parts.append(value)

    return ", ".join(parts) if parts else None


def build_category_query(latitude, longitude, category, radius):
    tag_filter = build_tag_filter(category)
    if not tag_filter:
        return None

    key, value = tag_filter

    return (
        f'[out:json][timeout:40];'
        f'(nwr["{key}"="{value}"]'
        f'(around:{radius},{latitude},{longitude}););'
        f'out center tags;'
    )


def build_all_categories_query(latitude, longitude, radius):
    query_parts = []

    for category in PLACE_CATEGORIES:
        key, value = build_tag_filter(category)
        query_parts.append(
            f'nwr["{key}"="{value}"]'
            f'(around:{radius},{latitude},{longitude});'
        )

    return (
        '[out:json][timeout:60];'
        f'({"".join(query_parts)});'
        'out center tags;'
    )


def query_overpass(query):
    headers = {
        "User-Agent": "ContextAwareLocalizationAgent/1.0"
    }

    for url in OVERPASS_SERVERS:
        try:
            response = requests.post(
                url,
                data={"data": query},
                headers=headers,
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and "elements" in data:
                return data

        except (requests.RequestException, ValueError, TypeError):
            continue

    return None


def process_places(
    data,
    latitude,
    longitude,
    requested_category=None,
):
    if not data:
        return []

    places = []

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        place_lat, place_lon = get_element_coordinates(element)

        if place_lat is None or place_lon is None:
            continue

        if requested_category:
            category = requested_category
        else:
            category = None
            for possible_category in PLACE_CATEGORIES:
                key, value = build_tag_filter(possible_category)
                if tags.get(key) == value:
                    category = possible_category
                    break

            if category is None:
                continue

        places.append({
            "name": get_place_name(tags),
            "brand": tags.get("brand"),
            "operator": tags.get("operator"),
            "type": category,
            "latitude": place_lat,
            "longitude": place_lon,
            "distance_km": calculate_distance(
                latitude, longitude, place_lat, place_lon
            ),
            "address": get_place_address(tags),
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "website": tags.get("website") or tags.get("contact:website"),
            "osm_id": element.get("id"),
            "osm_type": element.get("type"),
        })

    places.sort(key=lambda place: place["distance_km"])
    return places


def remove_duplicate_places(places):
    unique = {}

    for place in places:
        osm_type = place.get("osm_type")
        osm_id = place.get("osm_id")

        if osm_type and osm_id:
            key = f"{osm_type}:{osm_id}"
        else:
            key = (
                f'{place.get("name","").lower()}|'
                f'{round(place.get("latitude", 0), 5)}|'
                f'{round(place.get("longitude", 0), 5)}'
            )

        if key not in unique:
            unique[key] = place

    result = list(unique.values())
    result.sort(key=lambda place: place["distance_km"])
    return result


def get_nearby_places(latitude, longitude, place_type="all"):
    if (
        not (-90 <= latitude <= 90)
        or not (-180 <= longitude <= 180)
    ):
        return []

    all_places = []

    for radius in SEARCH_RADII:
        if place_type in PLACE_CATEGORIES:
            query = build_category_query(
                latitude, longitude, place_type, radius
            )
            data = query_overpass(query)
            places = process_places(
                data, latitude, longitude, place_type
            )
        else:
            query = build_all_categories_query(
                latitude, longitude, radius
            )
            data = query_overpass(query)
            places = process_places(
                data, latitude, longitude
            )

        all_places.extend(places)

    return remove_duplicate_places(all_places)


def get_nearby_places_by_category(
    latitude,
    longitude,
    radius=3000,
):
    results = {
        category: []
        for category in PLACE_CATEGORIES
    }

    for current_radius in SEARCH_RADII:
        query = build_all_categories_query(
            latitude, longitude, current_radius
        )
        data = query_overpass(query)

        places = process_places(
            data, latitude, longitude
        )

        for place in places:
            category = place.get("type")
            if category in results:
                results[category].append(place)

    for category in results:
        results[category] = remove_duplicate_places(
            results[category]
        )

    return results
