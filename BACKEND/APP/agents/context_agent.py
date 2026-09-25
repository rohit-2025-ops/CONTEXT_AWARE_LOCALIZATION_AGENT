from APP.services.time_service import get_time_context
from APP.services.location_service import get_location, get_nearby_places
from APP.services.weather_service import get_weather
from APP.services.rag_service import retrieve_knowledge
from APP.services.response_service import generate_response
from APP.services.llm_service import (
    build_llm_context,
    generate_llm_response,
)
from APP.services.history_service import add_history
from APP.services.geoapify_service import search_geoapify_places
from APP.agents.recommendation_agent import get_recommendations


# --------------------------------------------------
# Natural Language Place Category Detection
# --------------------------------------------------

def detect_place_category(query: str):
    """
    Convert a natural-language location request into
    a normalized application category.
    """

    query_lower = query.lower().strip()

    category_keywords = {

        "atm": [
            "atm",
            "cash machine",
            "cashpoint",
            "withdraw cash",
            "withdraw money",
            "withdraw",
            "get cash",
            "get money",
            "need cash",
            "need money",
            "some cash",
            "need some cash",
            "cash withdrawal",
            "take out cash",
            "take out money",
            "where can i get cash",
            "where can i get money",
            "where can i withdraw",
        ],

        "bank": [
            "bank",
            "bank branch",
            "banking",
            "send money",
            "deposit money",
            "open bank account",
        ],

        "restaurant": [
            "restaurant",
            "food",
            "eat",
            "eating",
            "meal",
            "hungry",
            "lunch",
            "dinner",
            "breakfast",
            "place to eat",
            "something to eat",
            "food place",
        ],

        "cafe": [
            "cafe",
            "cafes",
            "coffee",
            "coffee shop",
            "tea shop",
            "tea",
            "snacks",
            "beverage",
        ],

        "hospital": [
            "hospital",
            "emergency",
            "medical emergency",
            "medical care",
            "healthcare",
        ],

        "pharmacy": [
            "pharmacy",
            "chemist",
            "medicine",
            "medicines",
            "medical store",
            "drug store",
        ],

        "police": [
            "police",
            "police station",
            "cop",
            "law enforcement",
        ],

        "fuel": [
            "fuel",
            "petrol",
            "petrol pump",
            "petrol station",
            "gas station",
            "diesel",
            "fill fuel",
            "need petrol",
            "need fuel",
        ],

        "hotel": [
            "hotel",
            "stay",
            "place to stay",
            "where can i stay",
            "need a place to stay",
            "accommodation",
            "lodging",
            "hotel room",
            "need a room",
        ],

        "school": [
            "school",
            "schools",
        ],

        "supermarket": [
            "supermarket",
            "grocery",
            "grocery store",
            "groceries",
            "shopping for food",
        ],

        "parking": [
            "parking",
            "car parking",
            "parking lot",
            "park my car",
            "place to park",
            "where can i park",
            "need parking",
        ],

        "mechanic": [
            "mechanic",
            "car repair",
            "car needs repair",
            "my car needs repair",
            "bike repair",
            "vehicle repair",
            "vehicle needs repair",
            "auto repair",
            "repair my car",
            "repair my vehicle",
            "garage",
        ],

        "ev_charging": [
            "ev",
            "ev charging",
            "ev charger",
            "electric vehicle",
            "electric vehicle charging",
            "electric car charging",
            "charging station",
            "charge my car",
            "charge my ev",
            "where can i charge my ev",
            "where can i charge my car",
            "need to charge my ev",
        ],

        "bus_station": [
            "bus station",
            "bus stand",
            "bus stop",
            "bus terminal",
        ],

        "train_station": [
            "train station",
            "railway station",
            "rail station",
        ],

        "airport": [
            "airport",
            "air terminal",
        ],

        "post_office": [
            "post office",
            "postal office",
            "send parcel",
            "send a letter",
        ],

        "doctor": [
            "doctor",
            "clinic",
            "doctor's clinic",
            "medical doctor",
        ],

        "dentist": [
            "dentist",
            "dental clinic",
            "teeth doctor",
            "tooth doctor",
        ],

        "park": [
            "public park",
            "nearby park",
            "find a park",
            "playground",
            "garden",
            "place to walk",
            "walking area",
        ],

        "shopping_mall": [
            "shopping mall",
            "mall",
            "shopping center",
            "shopping centre",
        ],

        "bakery": [
            "bakery",
            "bread shop",
            "cake shop",
            "cakes",
        ],

        "laundry": [
            "laundry",
            "laundromat",
            "wash clothes",
            "clothes washing",
        ],

        "veterinary": [
            "veterinary",
            "vet",
            "animal doctor",
            "pet doctor",
            "pet clinic",
        ],
    }

    matches = []

    for category, keywords in category_keywords.items():

        for keyword in keywords:

            if keyword in query_lower:
                matches.append(
                    (len(keyword), category)
                )

    if matches:

        # Longer/more specific phrase wins.
        matches.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return matches[0][1]

    return None


# --------------------------------------------------
# Intent Detection
# --------------------------------------------------

def detect_intent(query: str):

    query_lower = query.lower().strip()

    # Weather questions
    weather_keywords = [
        "weather",
        "temperature",
        "rain",
        "raining",
        "rainy",
        "hot",
        "cold",
        "humidity",
        "humid",
        "wind",
        "windy",
        "cloud",
        "cloudy",
        "storm",
    ]

    for keyword in weather_keywords:

        if keyword in query_lower:
            return "weather"

    # Location/place search
    category = detect_place_category(query)

    if category:
        return "search_place"

    # Nearby questions
    nearby_keywords = [
        "near me",
        "nearby",
        "around me",
        "close to me",
        "closest",
        "nearest",
        "near here",
    ]

    for keyword in nearby_keywords:

        if keyword in query_lower:
            return "nearby_search"

    return "general"


# --------------------------------------------------
# Real Place Search
# --------------------------------------------------

def get_real_places(
    latitude: float,
    longitude: float,
    category=None
):

    if category:

        try:

            places = search_geoapify_places(
                latitude=latitude,
                longitude=longitude,
                category=category,
                radius=10000,
                limit=20,
            )

            if places:
                return places

        except Exception as error:

            print(
                f"Geoapify search failed: {error}"
            )

    # Fallback to existing OSM/Overpass service.
    try:

        return get_nearby_places(
            latitude=latitude,
            longitude=longitude,
            place_type=category or "all",
        )

    except Exception as error:

        print(
            f"Overpass fallback failed: {error}"
        )

        return []


# --------------------------------------------------
# Main Context Collector
# --------------------------------------------------

def collect_context(
    query: str,
    latitude: float,
    longitude: float,
):

    # ----------------------------------------------
    # Time
    # ----------------------------------------------

    time_context = get_time_context()

    # ----------------------------------------------
    # Location
    # ----------------------------------------------

    location_context = get_location(
        latitude,
        longitude
    )

    # ----------------------------------------------
    # Intent
    # ----------------------------------------------

    intent = detect_intent(query)

    category = detect_place_category(query)

    # ----------------------------------------------
    # Places
    # ----------------------------------------------

    nearby_places = []

    if intent in [
        "search_place",
        "nearby_search"
    ]:

        nearby_places = get_real_places(
            latitude=latitude,
            longitude=longitude,
            category=category,
        )

    # ----------------------------------------------
    # Weather
    # ----------------------------------------------

    weather = None

    if intent == "weather":

        try:

            weather = get_weather(
                latitude,
                longitude
            )

        except Exception as error:

            print(
                f"Weather service failed: {error}"
            )

    # ----------------------------------------------
    # Knowledge / RAG
    # ----------------------------------------------

    knowledge = retrieve_knowledge(
        query
    )

    # ----------------------------------------------
    # Recommendations
    # ----------------------------------------------

    recommendations = []

    if nearby_places:

        try:

            recommendations = get_recommendations(
                nearby_places
            )

        except Exception as error:

            print(
                f"Recommendation service failed: {error}"
            )

            recommendations = nearby_places[:5]

    # ----------------------------------------------
    # General Response
    # ----------------------------------------------

    general_response = None

    try:

        general_response = generate_response(
            query=query,
            intent=intent,
            location=location_context,
            weather=weather,
            recommendations=recommendations,
            knowledge=knowledge,
        )

    except Exception as error:

        print(
            f"Response service failed: {error}"
        )

    # ----------------------------------------------
    # LLM Context
    # ----------------------------------------------

    llm_context = build_llm_context(
        query=query,
        location=location_context,
        weather=weather,
        recommendations=recommendations,
        knowledge=knowledge,
    )

    # ----------------------------------------------
    # LLM Response
    # ----------------------------------------------

    llm_response = generate_llm_response(
        query=query,
        context=llm_context,
    )

    # ----------------------------------------------
    # Final Response
    # ----------------------------------------------

    response = general_response

    # ----------------------------------------------
    # History
    # ----------------------------------------------

    add_history(
        query=query,
        intent=intent,
        location=location_context,
        response=response,
    )

    return {
        "time": time_context,
        "location": location_context,
        "intent": intent,
        "nearby_places": nearby_places,
        "weather": weather,
        "recommendations": recommendations,
        "general_response": general_response,
        "response": response,
        "knowledge": knowledge,
        "llm_context": llm_context,
        "llm_response": llm_response,
    }