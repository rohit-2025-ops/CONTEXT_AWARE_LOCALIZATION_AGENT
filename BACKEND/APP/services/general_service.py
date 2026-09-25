def get_general_response(query: str):
    query_lower = query.lower().strip()

    if query_lower in ["hello", "hi", "hey"]:
        return "Hello! How can I help you?"

    if "good morning" in query_lower:
        return "Good morning! How can I help you?"

    if "good afternoon" in query_lower:
        return "Good afternoon! How can I help you?"

    if "good evening" in query_lower:
        return "Good evening! How can I help you?"

    if (
        "what can you do" in query_lower
        or "what do you do" in query_lower
    ):
        return (
            "I can understand your query, detect your intent, "
            "use your location, find nearby places, check weather, "
            "and provide context-aware recommendations."
        )

    if (
        "who are you" in query_lower
        or "what are you" in query_lower
    ):
        return (
            "I am a Context-Aware Localization Agent "
            "designed to provide location-aware and "
            "context-aware assistance."
        )

    return (
        "I can help you with nearby places, weather, "
        "location-aware searches, and recommendations."
    )