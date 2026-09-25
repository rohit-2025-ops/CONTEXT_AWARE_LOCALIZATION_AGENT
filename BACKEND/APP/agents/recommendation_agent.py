from typing import List, Dict, Any


def get_recommendations(
    places: List[Dict[str, Any]],
    category: str | None = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Select and rank nearby places for the user.

    Places are expected to contain:
        - name
        - distance_km
        - type
        - address
        - latitude
        - longitude

    The places should already come from a real location provider
    such as Geoapify or OpenStreetMap.
    """

    if not places:
        return []

    valid_places = []

    for place in places:
        if not isinstance(place, dict):
            continue

        name = place.get("name")

        if not name:
            continue

        try:
            distance = float(place.get("distance_km", 999999))
        except (TypeError, ValueError):
            distance = 999999

        item = dict(place)

        item["distance_km"] = round(distance, 2)

        valid_places.append(item)

    if not valid_places:
        return []

    # ---------------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------------

    unique_places = {}

    for place in valid_places:

        osm_type = place.get("osm_type")
        osm_id = place.get("osm_id")

        if osm_type and osm_id:
            key = f"{osm_type}:{osm_id}"

        else:
            name = str(place.get("name", "")).strip().lower()

            latitude = place.get("latitude")
            longitude = place.get("longitude")

            key = (
                f"{name}|"
                f"{latitude}|"
                f"{longitude}"
            )

        if key not in unique_places:
            unique_places[key] = place

    valid_places = list(unique_places.values())

    # ---------------------------------------------------------
    # CATEGORY FILTER
    # ---------------------------------------------------------

    if category:
        category_lower = category.lower().strip()

        category_places = []

        for place in valid_places:

            place_type = str(
                place.get("type", "")
            ).lower().strip()

            if place_type == category_lower:
                category_places.append(place)

        # Only apply the filter when matching places exist.
        # This prevents an empty recommendation list when
        # the external provider uses a slightly different type.
        if category_places:
            valid_places = category_places

    # ---------------------------------------------------------
    # DISTANCE-BASED RANKING
    # ---------------------------------------------------------

    valid_places.sort(
        key=lambda place: place.get(
            "distance_km",
            999999
        )
    )

    # ---------------------------------------------------------
    # RETURN TOP RESULTS
    # ---------------------------------------------------------

    return valid_places[:limit]