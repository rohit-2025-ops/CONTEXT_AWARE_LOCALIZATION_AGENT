from APP.services.geoapify_service import search_geoapify_places


def get_tourist_places(
    latitude: float,
    longitude: float,
    radius: int = 15000,
    limit: int = 10,
):
    """
    Get real tourist attractions near the user's location.

    Geoapify is used as the primary source.
    No fake/static tourist places are generated.
    """

    places = search_geoapify_places(
        latitude=latitude,
        longitude=longitude,
        category="tourist_attraction",
        radius=radius,
        limit=limit,
    )

    if not places:
        return {
            "success": False,
            "count": 0,
            "places": [],
            "message": (
                "No tourist attractions were found "
                "near the current location."
            ),
        }

    return {
        "success": True,
        "count": len(places),
        "places": places,
        "message": (
            f"Found {len(places)} tourist attractions "
            "near the current location."
        ),
    }