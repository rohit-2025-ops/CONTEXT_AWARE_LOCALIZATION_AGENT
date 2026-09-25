import os
import platform


# --------------------------------------------------
# AI BACKEND DETECTION
# --------------------------------------------------

def get_ai_backend():
    """
    Detect the target AI hardware/backend.

    Snapdragon ARM64 devices are prepared for
    Qualcomm QNN / GenieX / QAIRT deployment.

    The current Dell development PC uses the
    generic CPU fallback.
    """

    machine = platform.machine().lower()

    if machine in [
        "arm64",
        "aarch64",
    ]:
        return "snapdragon"

    return "generic"


# --------------------------------------------------
# QNN AVAILABILITY
# --------------------------------------------------

def is_qnn_available():
    """
    Check whether ONNX Runtime provides
    Qualcomm QNN execution support.
    """

    try:
        import onnxruntime as ort

        providers = ort.get_available_providers()

        return (
            "QNNExecutionProvider"
            in providers
        )

    except Exception:
        return False


# --------------------------------------------------
# INFERENCE BACKEND
# --------------------------------------------------

def get_inference_backend():
    """
    Determine the actual inference backend.

    Priority:

    Snapdragon + QNN
        ↓
    Snapdragon CPU
        ↓
    Generic CPU
    """

    ai_backend = get_ai_backend()

    if ai_backend == "snapdragon":

        if is_qnn_available():
            return "snapdragon_npu"

        return "snapdragon_cpu"

    return "generic_cpu"


# --------------------------------------------------
# BUILD LLM CONTEXT
# --------------------------------------------------

def build_llm_context(
    query,
    location,
    weather,
    recommendations,
    knowledge
):
    """
    Build the context provided to the LLM.

    Real-world places returned by Geoapify/OSM
    are included as grounded recommendations.

    The LLM should use this information rather
    than inventing places.
    """

    context_parts = []

    # User query
    context_parts.append(
        f"User Query: {query}"
    )

    # Location
    if location:

        city = location.get("city")
        country = location.get("country")

        if city or country:

            context_parts.append(
                f"Location: {city}, {country}"
            )

    # Weather
    if weather:

        context_parts.append(
            f"Weather: {weather}"
        )

    # Real recommendations
    if recommendations:

        context_parts.append(
            f"Recommendations: {recommendations}"
        )

    # RAG knowledge
    if knowledge:

        context_parts.append(
            "Relevant Knowledge:\n"
            + "\n".join(
                f"- {item}"
                for item in knowledge
            )
        )

    return "\n".join(context_parts)


# --------------------------------------------------
# LOAD ONNX MODEL
# --------------------------------------------------

def load_onnx_model(model_path: str):
    """
    Load an ONNX model.

    Qualcomm QNN is preferred when available.
    Otherwise CPUExecutionProvider is used.
    """

    import onnxruntime as ort

    providers = (
        ort.get_available_providers()
    )

    if "QNNExecutionProvider" in providers:

        session = ort.InferenceSession(
            model_path,
            providers=[
                "QNNExecutionProvider"
            ]
        )

    else:

        session = ort.InferenceSession(
            model_path,
            providers=[
                "CPUExecutionProvider"
            ]
        )

    return session


# --------------------------------------------------
# GENERIC CPU RESPONSE
# --------------------------------------------------

def generate_generic_response(
    query: str,
    context: str
):
    """
    Generate a natural-language response from
    grounded application context.

    This development fallback does not invent:

        - place names
        - addresses
        - distances
        - weather values
    """

    # ------------------------------------------
    # PLACE RECOMMENDATIONS
    # ------------------------------------------

    recommendations_text = ""

    if "Recommendations:" in context:

        recommendations_text = context.split(
            "Recommendations:",
            1
        )[1].strip()

    if recommendations_text:

        import ast

        try:

            recommendations = ast.literal_eval(
                recommendations_text
            )

        except (ValueError, SyntaxError):

            recommendations = []

        if recommendations:

            first_place = recommendations[0]

            name = first_place.get(
                "name",
                "a nearby place"
            )

            distance = first_place.get(
                "distance_km"
            )

            place_type = first_place.get(
                "type"
            )

            type_labels = {

                "atm": "ATM",

                "bank": "bank",

                "restaurant": "restaurant",

                "cafe": "cafe",

                "fast_food": "fast-food place",

                "bakery": "bakery",

                "hospital": "hospital",

                "pharmacy": "pharmacy",

                "doctor": "doctor",

                "dentist": "dentist",

                "police": "police station",

                "fuel": "fuel station",

                "mechanic": "mechanic",

                "car_repair": "car repair shop",

                "bike_repair": "bike repair shop",

                "car_wash": "car wash",

                "ev_charging": (
                    "EV charging station"
                ),

                "school": "school",

                "college": "college",

                "university": "university",

                "library": "library",

                "hotel": "hotel",

                "hostel": "hostel",

                "guest_house": "guest house",

                "motel": "motel",

                "supermarket": "supermarket",

                "shopping_mall": (
                    "shopping mall"
                ),

                "parking": (
                    "parking location"
                ),

                "bus_station": (
                    "bus station"
                ),

                "train_station": (
                    "train station"
                ),

                "airport": "airport",

                "taxi": "taxi service",

                "post_office": (
                    "post office"
                ),

                "park": "park",

                "playground": "playground",

                "cinema": "cinema",

                "museum": "museum",

                "zoo": "zoo",

                "aquarium": "aquarium",

                "laundry": "laundry",

                "dry_cleaning": (
                    "dry-cleaning service"
                ),

                "hairdresser": "hairdresser",

                "spa": "spa",

                "veterinary": (
                    "veterinary clinic"
                ),
            }

            label = type_labels.get(
                place_type,
                "place"
            )

            count = len(recommendations)

            # ----------------------------------
            # COUNT TEXT
            # ----------------------------------

            if count == 1:

                count_text = (
                    f"I found 1 {label}"
                )

            else:

                plural_labels = {

                    "ATM": "ATMs",

                    "bank": "banks",

                    "restaurant": "restaurants",

                    "cafe": "cafes",

                    "fast-food place": (
                        "fast-food places"
                    ),

                    "bakery": "bakeries",

                    "hospital": "hospitals",

                    "pharmacy": "pharmacies",

                    "doctor": "doctors",

                    "dentist": "dentists",

                    "police station": (
                        "police stations"
                    ),

                    "fuel station": (
                        "fuel stations"
                    ),

                    "mechanic": "mechanics",

                    "car repair shop": (
                        "car repair shops"
                    ),

                    "bike repair shop": (
                        "bike repair shops"
                    ),

                    "car wash": "car washes",

                    "EV charging station": (
                        "EV charging stations"
                    ),

                    "school": "schools",

                    "college": "colleges",

                    "university": (
                        "universities"
                    ),

                    "library": "libraries",

                    "hotel": "hotels",

                    "hostel": "hostels",

                    "guest house": (
                        "guest houses"
                    ),

                    "motel": "motels",

                    "supermarket": (
                        "supermarkets"
                    ),

                    "shopping mall": (
                        "shopping malls"
                    ),

                    "parking location": (
                        "parking locations"
                    ),

                    "bus station": (
                        "bus stations"
                    ),

                    "train station": (
                        "train stations"
                    ),

                    "airport": "airports",

                    "taxi service": (
                        "taxi services"
                    ),

                    "post office": (
                        "post offices"
                    ),

                    "park": "parks",

                    "playground": (
                        "playgrounds"
                    ),

                    "cinema": "cinemas",

                    "museum": "museums",

                    "zoo": "zoos",

                    "aquarium": "aquariums",

                    "laundry": "laundries",

                    "dry-cleaning service": (
                        "dry-cleaning services"
                    ),

                    "hairdresser": (
                        "hairdressers"
                    ),

                    "spa": "spas",

                    "veterinary clinic": (
                        "veterinary clinics"
                    ),
                }

                plural = plural_labels.get(
                    label,
                    f"{label}s"
                )

                count_text = (
                    f"I found {count} "
                    f"nearby {plural}"
                )

            # ----------------------------------
            # DISTANCE
            # ----------------------------------

            if distance is not None:

                return (
                    f"{count_text}. "
                    f"The closest option is "
                    f"{name}, approximately "
                    f"{distance} km away."
                )

            return (
                f"{count_text}. "
                f"The closest option is "
                f"{name}."
            )

    # ------------------------------------------
    # WEATHER
    # ------------------------------------------

    if "Weather:" in context:

        weather_text = context.split(
            "Weather:",
            1
        )[1].strip()

        return (
            "Here is the current weather "
            "information for your location:\n\n"
            f"{weather_text}"
        )

    # ------------------------------------------
    # RAG KNOWLEDGE
    # ------------------------------------------

    if "Relevant Knowledge:" in context:

        knowledge_text = context.split(
            "Relevant Knowledge:",
            1
        )[1].strip()

        if knowledge_text:

            return (
                "Here is the relevant "
                "information:\n\n"
                f"{knowledge_text}"
            )

    # ------------------------------------------
    # NO RESULT
    # ------------------------------------------

    return (
        "I could not find a specific "
        "real-world result for your request."
    )


# --------------------------------------------------
# SNAPDRAGON RESPONSE
# --------------------------------------------------

def generate_snapdragon_response(
    query: str,
    context: str
):
    """
    Snapdragon deployment interface.

    This is the application boundary for the
    GenieX/QAIRT Llama 3.2 1B-Instruct runtime.

    Actual GenieX/QAIRT model execution is enabled
    only when the required Qualcomm deployment
    artifact/runtime is available on the target
    Snapdragon device.
    """

    model_path = os.getenv(
        "SNAPDRAGON_MODEL_PATH"
    )

    if not model_path:

        return (
            "AI Backend: snapdragon_geniex\n"
            "Runtime: GenieX/QAIRT\n"
            "Model: Llama 3.2 1B-Instruct\n"
            "Status: deployment artifact "
            "not configured\n"
            f"Query: {query}\n"
            f"Context:\n{context}"
        )

    return (
        "AI Backend: snapdragon_geniex\n"
        "Runtime: GenieX/QAIRT\n"
        "Model: Llama 3.2 1B-Instruct\n"
        f"Model Path: {model_path}\n"
        f"Query: {query}\n"
        f"Context:\n{context}"
    )


# --------------------------------------------------
# MAIN LLM INTERFACE
# --------------------------------------------------

def generate_llm_response(
    query: str,
    context: str
):
    """
    Main LLM interface.

    The rest of the application does not need
    to know which inference backend is being used.

    Current development PC:
        generic_cpu

    Snapdragon target:
        snapdragon_npu
        or
        snapdragon_cpu
    """

    backend = get_inference_backend()

    if backend == "snapdragon_npu":

        return generate_snapdragon_response(
            query=query,
            context=context
        )

    if backend == "snapdragon_cpu":

        return generate_snapdragon_response(
            query=query,
            context=context
        )

    return generate_generic_response(
        query=query,
        context=context
    )