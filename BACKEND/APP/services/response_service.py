def generate_response(
    query: str,
    intent: str,
    location: dict,
    weather: dict | None,
    recommendations: list,
    knowledge: list[str],
):
    """
    Generate a grounded response using only the context
    already collected by the application.

    Place names and distances come from real place-search
    results. This service does not invent places.
    """

    # --------------------------------------------------
    # GENERAL QUERY
    # --------------------------------------------------

    if intent == "general":

        return (
            "I can help you with nearby places, weather, "
            "location-aware searches, and recommendations."
        )

    # --------------------------------------------------
    # WEATHER
    # --------------------------------------------------

    if intent == "weather":

        if not weather:

            return (
                "I couldn't retrieve the current weather "
                "for your location."
            )

        city = (
            location.get("city")
            or "your location"
        )

        temperature = weather.get(
            "temperature"
        )

        apparent_temperature = weather.get(
            "apparent_temperature"
        )

        description = weather.get(
            "weather_description"
        )

        humidity = weather.get(
            "humidity"
        )

        wind_speed = weather.get(
            "wind_speed"
        )

        response = (
            f"Currently in {city}, the temperature is "
            f"{temperature}°C and it feels like "
            f"{apparent_temperature}°C. "
            f"The weather is {description}, with "
            f"{humidity}% humidity."
        )

        if wind_speed is not None:

            response += (
                f" Wind speed is "
                f"{wind_speed} km/h."
            )

        if knowledge:

            response += (
                f" {knowledge[0]}"
            )

        return response

    # --------------------------------------------------
    # PLACE SEARCH
    # --------------------------------------------------

    if intent in [
        "search_place",
        "nearby_search",
    ]:

        city = (
            location.get("city")
            or "your current location"
        )

        # --------------------------------------------------
        # NO REAL RESULTS
        # --------------------------------------------------

        if not recommendations:

            if knowledge:

                return (
                    "I couldn't find any suitable places "
                    f"near {city}. "
                    f"{knowledge[0]}"
                )

            return (
                "I couldn't find any suitable places "
                f"near {city}."
            )

        # --------------------------------------------------
        # PLACE LABELS
        # --------------------------------------------------

        place_labels = {

            "cafe": "cafe",

            "restaurant": "restaurant",

            "fast_food": "fast-food place",

            "bakery": "bakery",

            "police": "police station",

            "hospital": "hospital",

            "pharmacy": "pharmacy",

            "doctor": "doctor",

            "dentist": "dentist",

            "bank": "bank",

            "atm": "ATM",

            "fuel": "fuel station",

            "mechanic": "mechanic",

            "car_repair": "car repair shop",

            "bike_repair": "bike repair shop",

            "car_wash": "car wash",

            "ev_charging": "EV charging station",

            "school": "school",

            "college": "college",

            "university": "university",

            "library": "library",

            "hotel": "hotel",

            "hostel": "hostel",

            "guest_house": "guest house",

            "motel": "motel",

            "supermarket": "supermarket",

            "shopping_mall": "shopping mall",

            "parking": "parking location",

            "bus_station": "bus station",

            "train_station": "train station",

            "airport": "airport",

            "taxi": "taxi service",

            "post_office": "post office",

            "park": "park",

            "playground": "playground",

            "cinema": "cinema",

            "museum": "museum",

            "zoo": "zoo",

            "aquarium": "aquarium",

            "laundry": "laundry",

            "dry_cleaning": "dry-cleaning service",

            "hairdresser": "hairdresser",

            "spa": "spa",

            "veterinary": "veterinary clinic",
        }

        # --------------------------------------------------
        # FIRST REAL RECOMMENDATION
        # --------------------------------------------------

        first_place = recommendations[0]

        place_name = (
            first_place.get("name")
            or "the closest option"
        )

        distance = first_place.get(
            "distance_km"
        )

        place_type = first_place.get(
            "type"
        )

        place_description = place_labels.get(
            place_type,
            "place"
        )

        # --------------------------------------------------
        # RESULT COUNT
        # --------------------------------------------------

        count = len(recommendations)

        if count == 1:

            count_text = (
                f"I found 1 {place_description}"
            )

        else:

            # Simple pluralization for common labels.
            plural_labels = {
                "ATM": "ATMs",
                "police station": "police stations",
                "fuel station": "fuel stations",
                "EV charging station": "EV charging stations",
                "parking location": "parking locations",
                "shopping mall": "shopping malls",
                "bus station": "bus stations",
                "train station": "train stations",
                "post office": "post offices",
                "guest house": "guest houses",
                "car repair shop": "car repair shops",
                "bike repair shop": "bike repair shops",
                "car wash": "car washes",
                "dry-cleaning service": "dry-cleaning services",
                "veterinary clinic": "veterinary clinics",
            }

            plural = plural_labels.get(
                place_description,
                f"{place_description}s"
            )

            count_text = (
                f"I found {count} {plural}"
            )

        response = (
            f"{count_text} near {city}. "
        )

        # --------------------------------------------------
        # REAL PLACE NAME + DISTANCE
        # --------------------------------------------------

        if distance is not None:

            response += (
                f"The closest option is "
                f"{place_name}, "
                f"about {distance} km away."
            )

        else:

            response += (
                f"The closest option is "
                f"{place_name}."
            )

        # --------------------------------------------------
        # KNOWLEDGE CONTEXT
        # --------------------------------------------------

        if knowledge:

            response += (
                f" {knowledge[0]}"
            )

        return response

    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------

    return (
        "I can help you with nearby places, weather, "
        "location-aware searches, and recommendations."
    )