knowledge_base = [
    {
        "topic": "coffee",
        "keywords": [
            "coffee",
            "cafe",
            "cafÃ©",
            "tea",
            "drink",
            "beverage"
        ],
        "content": (
            "Coffee shops are suitable places for coffee, tea, "
            "beverages, snacks, and casual meetings."
        )
    },
    {
        "topic": "restaurant",
        "keywords": [
            "restaurant",
            "food",
            "eat",
            "eating",
            "lunch",
            "dinner",
            "breakfast",
            "meal",
            "hungry"
        ],
        "content": (
            "Restaurants are suitable places for meals such as "
            "breakfast, lunch, and dinner."
        )
    },
    {
        "topic": "weather",
        "keywords": [
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
            "storm"
        ],
        "content": (
            "Weather information can include temperature, humidity, "
            "rain, wind, clouds, and general weather conditions."
        )
    },
    {
        "topic": "nearby",
        "keywords": [
            "near",
            "nearby",
            "around",
            "close",
            "location"
        ],
        "content": (
            "Nearby places can be selected based on the user's "
            "current location and distance."
        )
    }
]


def retrieve_knowledge(query: str):
    query_lower = query.lower()

    results = []

    for item in knowledge_base:

        for keyword in item["keywords"]:

            if keyword in query_lower:
                results.append(item["content"])
                break

    return results