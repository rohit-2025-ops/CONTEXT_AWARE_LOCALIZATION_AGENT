import streamlit as st


# --------------------------------------------------
# Location
# --------------------------------------------------

def show_location(location):
    """
    Display detected location information.
    """

    st.subheader("📍 Location")

    if not location:

        st.info(
            "Location information is not available."
        )

        return

    area = location.get(
        "area"
    ) or "Unknown area"

    city = location.get(
        "city"
    ) or "Unknown city"

    state = location.get(
        "state"
    ) or "Unknown state"

    country = location.get(
        "country"
    ) or "Unknown country"

    # ----------------------------------------------
    # Full Location
    # ----------------------------------------------

    st.success(
        f"📍 {area}, {city}, {state}, {country}"
    )

    # ----------------------------------------------
    # Location Details
    # ----------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Area",
            area
        )

    with col2:

        st.metric(
            "City",
            city
        )

    with col3:

        st.metric(
            "State",
            state
        )


# --------------------------------------------------
# Weather
# --------------------------------------------------

def show_weather(weather):
    """
    Display current weather information.
    """

    st.subheader("🌤️ Weather")

    if not weather:

        st.info(
            "Weather information is not available."
        )

        return

    col1, col2, col3 = st.columns(3)

    with col1:

        temperature = weather.get(
            "temperature"
        )

        if temperature is not None:

            st.metric(
                "Temperature",
                f"{temperature} °C"
            )

        else:

            st.metric(
                "Temperature",
                "N/A"
            )

    with col2:

        feels_like = weather.get(
            "apparent_temperature"
        )

        if feels_like is not None:

            st.metric(
                "Feels Like",
                f"{feels_like} °C"
            )

        else:

            st.metric(
                "Feels Like",
                "N/A"
            )

    with col3:

        humidity = weather.get(
            "humidity"
        )

        if humidity is not None:

            st.metric(
                "Humidity",
                f"{humidity}%"
            )

        else:

            st.metric(
                "Humidity",
                "N/A"
            )

    description = weather.get(
        "weather_description"
    )

    wind_speed = weather.get(
        "wind_speed"
    )

    if description:

        st.write(
            f"**Condition:** {description}"
        )

    if wind_speed is not None:

        st.write(
            f"**Wind Speed:** {wind_speed} km/h"
        )


# --------------------------------------------------
# Intent
# --------------------------------------------------

def show_intent(intent):
    """
    Display detected user intent.
    """

    st.subheader("🧠 Detected Intent")

    if intent:

        st.info(
            intent
        )

    else:

        st.info(
            "Intent not available."
        )


# --------------------------------------------------
# Recommendations
# --------------------------------------------------

def show_recommendations(recommendations):
    """
    Display recommended nearby places.
    """

    st.subheader("⭐ Recommendations")

    if not recommendations:

        st.info(
            "No recommendations were found."
        )

        return

    for index, place in enumerate(
        recommendations,
        start=1
    ):

        name = place.get(
            "name",
            "Unnamed place"
        )

        place_type = place.get(
            "type",
            "place"
        )

        distance = place.get(
            "distance_km"
        )

        st.markdown(
            f"### {index}. {name}"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Type:** {place_type}"
            )

        with col2:

            if distance is not None:

                st.write(
                    f"**Distance:** {distance} km"
                )

        st.divider()


# --------------------------------------------------
# AI Response
# --------------------------------------------------

def show_ai_response(response):
    """
    Display the main AI-generated response.
    """

    st.subheader("🤖 AI Response")

    if response:

        st.success(
            response
        )

    else:

        st.info(
            "No AI response available."
        )


# --------------------------------------------------
# LLM Response
# --------------------------------------------------

def show_llm_response(llm_response):
    """
    Display the LLM backend response.
    """

    st.subheader("🧩 AI Backend")

    if llm_response:

        st.code(
            llm_response,
            language="text"
        )

    else:

        st.info(
            "LLM response is not available."
        )


# --------------------------------------------------
# RAG Knowledge
# --------------------------------------------------

def show_rag_knowledge(knowledge):
    """
    Display retrieved RAG knowledge.
    """

    st.subheader("📚 RAG Knowledge")

    if not knowledge:

        st.info(
            "No relevant knowledge was retrieved."
        )

        return

    for item in knowledge:

        st.write(
            f"• {item}"
        )


# --------------------------------------------------
# Conversation History
# --------------------------------------------------

def show_history(history):
    """
    Display conversation history.
    """

    st.subheader("🕘 Conversation History")

    if not history:

        st.info(
            "No conversation history available."
        )

        return

    for item in reversed(
        history
    ):

        query = item.get(
            "query",
            "Unknown query"
        )

        intent = item.get(
            "intent",
            "Unknown"
        )

        response = item.get(
            "response",
            "No response"
        )

        with st.expander(
            query
        ):

            st.write(
                f"**Intent:** {intent}"
            )

            st.write(
                f"**Response:** {response}"
            )