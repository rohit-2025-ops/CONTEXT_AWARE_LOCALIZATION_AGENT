import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation

from api_client import (
    check_backend,
    get_context,
    get_location,
    get_tourist_places,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Context-Aware Localization Agent",
    page_icon="🌍",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "latitude" not in st.session_state:
    st.session_state.latitude = None

if "longitude" not in st.session_state:
    st.session_state.longitude = None

if "location_data" not in st.session_state:
    st.session_state.location_data = None

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

if "assistant_history" not in st.session_state:
    st.session_state.assistant_history = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_value(value, default="--"):

    if value is None or value == "":
        return default

    return value


def number(value, digits=1):

    if value is None:
        return "--"

    try:
        return f"{float(value):.{digits}f}"

    except (ValueError, TypeError):
        return str(value)


def get_location_text(location):

    if not location:
        return "Location unavailable"

    parts = []

    for key in ["area", "city", "state"]:

        value = location.get(key)

        if value:
            parts.append(str(value))

    return ", ".join(parts) or "Location unavailable"


def get_local_language(location):

    if not location:
        return "English"

    state = str(
        location.get("state", "")
    ).lower().strip()

    languages = {
        "odisha": "Odia",
        "west bengal": "Bengali",
        "bihar": "Hindi",
        "jharkhand": "Hindi",
        "uttar pradesh": "Hindi",
        "madhya pradesh": "Hindi",
        "rajasthan": "Hindi",
        "haryana": "Hindi",
        "punjab": "Punjabi",
        "gujarat": "Gujarati",
        "maharashtra": "Marathi",
        "karnataka": "Kannada",
        "tamil nadu": "Tamil",
        "kerala": "Malayalam",
        "andhra pradesh": "Telugu",
        "telangana": "Telugu",
        "assam": "Assamese",
    }

    return languages.get(
        state,
        "English",
    )


def translate_text(
    text,
    target_language,
    source_language="Auto Detect",
):

    try:

        response = requests.post(
            "http://127.0.0.1:8000/translate",
            params={
                "text": text,
                "target_language": target_language,
                "source_language": source_language,
            },
            timeout=30,
        )

        if response.status_code == 200:

            return {
                "success": True,
                "data": response.json(),
            }

        return {
            "success": False,
            "error": response.text,
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": str(error),
        }


# ============================================================
# HEADER
# ============================================================

st.title("🌍 Context-Aware Localization Agent")

st.write(
    "Your intelligent local assistant for places, "
    "weather, language, culture, travel and everyday needs."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📍 Your Location")

    # --------------------------------------------------------
    # Browser GPS
    # --------------------------------------------------------

    location_result = streamlit_geolocation()

    if location_result:

        latitude = location_result.get("latitude")
        longitude = location_result.get("longitude")

        if (
            latitude is not None
            and longitude is not None
        ):

            st.session_state.latitude = float(latitude)
            st.session_state.longitude = float(longitude)

            st.success(
                "📍 Location detected successfully!"
            )

        else:

            st.warning(
                "Browser did not return coordinates."
            )

    else:

        st.info(
            "Click the location permission button "
            "in the browser and allow location access."
        )

    latitude = st.session_state.latitude
    longitude = st.session_state.longitude

    # --------------------------------------------------------
    # Show coordinates
    # --------------------------------------------------------

    if (
        latitude is not None
        and longitude is not None
    ):

        st.success("GPS coordinates available")

        st.write(
            f"Latitude: `{latitude:.6f}`"
        )

        st.write(
            f"Longitude: `{longitude:.6f}`"
        )

    else:

        st.warning(
            "Waiting for browser location..."
        )

    st.divider()

    # --------------------------------------------------------
    # Backend status
    # --------------------------------------------------------

    backend = check_backend()

    if backend.get("status"):

        st.success(
            "🟢 Backend Connected"
        )

    else:

        st.error(
            "🔴 Backend Offline"
        )

        st.code(
            "uvicorn APP.main:app --reload"
        )

    st.divider()

    if st.button(
        "🔄 Refresh Location",
        use_container_width=True,
    ):

        st.session_state.location_data = None
        st.session_state.weather_data = None
        st.rerun()


# ============================================================
# REVERSE GEOCODING
# ============================================================

if (
    latitude is not None
    and longitude is not None
):

    if st.session_state.location_data is None:

        result = get_location(
            latitude,
            longitude,
        )

        if result.get("success"):

            st.session_state.location_data = (
                result.get("data")
            )


location = st.session_state.location_data


# ============================================================
# LOCATION SUMMARY
# ============================================================

if location:

    city = get_location_text(location)

    language = get_local_language(location)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📍 Location",
            city,
        )

    with col2:

        st.metric(
            "🗣️ Local Language",
            language,
        )

    with col3:

        st.metric(
            "🌐 Country",
            safe_value(
                location.get("country")
            ),
        )


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "🧭 Explore",
        "🌤️ Weather",
        "🌍 Translate",
        "🏛️ Tourist Guide",
        "🎭 Culture",
        "💬 Ask Assistant",
    ]
)


# ============================================================
# EXPLORE
# ============================================================

with tabs[0]:

    st.header("🧭 Explore Nearby")

    st.write(
        "Find useful real places around your current location."
    )

    categories = [
        ("☕ Cafe", "cafe"),
        ("🍽️ Restaurant", "restaurant"),
        ("💵 ATM", "atm"),
        ("🏥 Hospital", "hospital"),
        ("⛽ Fuel", "fuel"),
        ("🅿️ Parking", "parking"),
        ("🏨 Hotel", "hotel"),
        ("👮 Police", "police"),
        ("💊 Pharmacy", "pharmacy"),
        ("🏦 Bank", "bank"),
        ("🔧 Mechanic", "mechanic"),
        ("📚 Library", "library"),
    ]

    columns = st.columns(4)

    for index, (label, category) in enumerate(categories):

        with columns[index % 4]:

            if st.button(
                label,
                key=f"category_{category}",
                use_container_width=True,
            ):

                st.session_state.selected_category = category

    category = st.session_state.selected_category

    if category:

        if (
            latitude is None
            or longitude is None
        ):

            st.warning(
                "📍 Location is required. "
                "Please allow browser location access."
            )

        else:

            queries = {

                "cafe":
                    "Find cafes near me",

                "restaurant":
                    "Find restaurants near me",

                "atm":
                    "Find ATMs near me",

                "hospital":
                    "Find hospitals near me",

                "fuel":
                    "Find fuel stations near me",

                "parking":
                    "Find parking near me",

                "hotel":
                    "Find hotels near me",

                "police":
                    "Find police stations near me",

                "pharmacy":
                    "Find pharmacies near me",

                "bank":
                    "Find banks near me",

                "mechanic":
                    "Find mechanics near me",

                "library":
                    "Find libraries near me",
            }

            with st.spinner(
                "Searching nearby places..."
            ):

                result = get_context(
                    queries[category],
                    latitude,
                    longitude,
                )

            if result.get("success"):

                data = result.get(
                    "data",
                    {},
                )

                places = data.get(
                    "recommendations",
                    [],
                )

                if not places:

                    places = data.get(
                        "nearby_places",
                        [],
                    )

                if places:

                    for place in places:

                        st.subheader(
                            f"📍 {safe_value(place.get('name'))}"
                        )

                        st.write(
                            f"📏 "
                            f"{number(place.get('distance_km'), 2)} km away"
                        )

                        st.write(
                            safe_value(
                                place.get("address"),
                                "Address unavailable",
                            )
                        )

                        st.divider()

                else:

                    st.info(
                        "No nearby places found."
                    )

            else:

                st.error(
                    result.get(
                        "error",
                        "Search failed.",
                    )
                )


# ============================================================
# WEATHER
# ============================================================

with tabs[1]:

    st.header("🌤️ Weather")

    if (
        latitude is None
        or longitude is None
    ):

        st.warning(
            "📍 Allow browser location access "
            "to see local weather."
        )

    else:

        if st.button(
            "🌤️ Load / Refresh Weather",
            use_container_width=True,
        ):

            with st.spinner(
                "Getting weather information..."
            ):

                result = get_context(
                    "What is the weather here?",
                    latitude,
                    longitude,
                )

            if result.get("success"):

                data = result.get(
                    "data",
                    {},
                )

                st.session_state.weather_data = (
                    data.get("weather")
                )

            else:

                st.error(
                    result.get(
                        "error",
                        "Weather request failed.",
                    )
                )

        weather = st.session_state.weather_data

        if weather:

            st.subheader(
                safe_value(
                    weather.get(
                        "weather_description"
                    )
                )
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "🌡️ Temperature",
                    f"{number(weather.get('temperature'))} °C",
                )

            with col2:

                st.metric(
                    "🤒 Feels Like",
                    f"{number(weather.get('apparent_temperature'))} °C",
                )

            with col3:

                st.metric(
                    "💧 Humidity",
                    f"{safe_value(weather.get('humidity'))} %",
                )

            with col4:

                st.metric(
                    "☁️ Cloud Cover",
                    f"{safe_value(weather.get('cloud_cover'))} %",
                )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💨 Wind",
                    f"{number(weather.get('wind_speed'))} km/h",
                )

            with col2:

                st.metric(
                    "🧭 Wind Direction",
                    f"{safe_value(weather.get('wind_direction'))}°",
                )

            with col3:

                st.metric(
                    "🌧️ Rain",
                    f"{safe_value(weather.get('rain'))} mm",
                )

            with col4:

                st.metric(
                    "🌧️ Precipitation",
                    f"{safe_value(weather.get('precipitation'))} mm",
                )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "👁️ Visibility",
                    f"{safe_value(weather.get('visibility'))} m",
                )

            with col2:

                st.metric(
                    "🔆 UV Index",
                    safe_value(weather.get("uv_index")),
                )

            with col3:

                st.metric(
                    "Pressure",
                    f"{safe_value(weather.get('pressure'))} hPa",
                )

            with col4:

                st.metric(
                    "🌐 Timezone",
                    safe_value(weather.get("timezone")),
                )

            st.subheader(
                "📅 Today's Forecast"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Maximum",
                    f"{number(weather.get('today_max_temperature'))} °C",
                )

            with col2:

                st.metric(
                    "Minimum",
                    f"{number(weather.get('today_min_temperature'))} °C",
                )

            with col3:

                st.metric(
                    "Rain Probability",
                    f"{safe_value(weather.get('today_precipitation_probability'))} %",
                )

            with col4:

                st.metric(
                    "UV Index",
                    safe_value(weather.get("uv_index")),
                )

            st.subheader(
                "🌅 Sunrise / Sunset"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.info(
                    f"🌅 Sunrise\n\n"
                    f"{safe_value(weather.get('sunrise'))}"
                )

            with col2:

                st.info(
                    f"🌇 Sunset\n\n"
                    f"{safe_value(weather.get('sunset'))}"
                )

            hourly = weather.get(
                "hourly_forecast",
                [],
            )

            if hourly:

                st.subheader(
                    "⏰ Hourly Forecast"
                )

                rows = []

                for item in hourly[:24]:

                    rows.append(
                        {
                            "Time":
                                item.get(
                                    "time",
                                    "--",
                                ),

                            "Temperature °C":
                                item.get(
                                    "temperature",
                                    "--",
                                ),

                            "Condition":
                                item.get(
                                    "weather_description",
                                    "--",
                                ),

                            "Rain Chance %":
                                item.get(
                                    "precipitation_probability",
                                    "--",
                                ),

                            "Humidity %":
                                item.get(
                                    "humidity",
                                    "--",
                                ),

                            "Wind km/h":
                                item.get(
                                    "wind_speed",
                                    "--",
                                ),

                            "Cloud %":
                                item.get(
                                    "cloud_cover",
                                    "--",
                                ),

                            "UV":
                                item.get(
                                    "uv_index",
                                    "--",
                                ),
                        }
                    )

                st.dataframe(
                    rows,
                    use_container_width=True,
                    hide_index=True,
                )

            daily = weather.get(
                "daily_forecast",
                [],
            )

            if daily:

                st.subheader(
                    "📆 7-Day Forecast"
                )

                rows = []

                for item in daily:

                    rows.append(
                        {
                            "Date":
                                item.get(
                                    "date",
                                    "--",
                                ),

                            "Condition":
                                item.get(
                                    "weather_description",
                                    "--",
                                ),

                            "Min °C":
                                item.get(
                                    "min_temperature",
                                    "--",
                                ),

                            "Max °C":
                                item.get(
                                    "max_temperature",
                                    "--",
                                ),

                            "Rain Chance %":
                                item.get(
                                    "precipitation_probability",
                                    "--",
                                ),

                            "Rain mm":
                                item.get(
                                    "rain_sum",
                                    "--",
                                ),

                            "UV Max":
                                item.get(
                                    "uv_index_max",
                                    "--",
                                ),

                            "Wind km/h":
                                item.get(
                                    "max_wind_speed",
                                    "--",
                                ),
                        }
                    )

                st.dataframe(
                    rows,
                    use_container_width=True,
                    hide_index=True,
                )

        else:

            st.info(
                "Click 'Load / Refresh Weather' "
                "to load weather information."
            )


# ============================================================
# TRANSLATE
# ============================================================

with tabs[2]:

    st.header("🌍 Translation")

    languages = [
        "English",
        "Hindi",
        "Bengali",
        "Odia",
        "Telugu",
        "Tamil",
        "Kannada",
        "Malayalam",
        "Marathi",
        "Gujarati",
        "Punjabi",
        "Urdu",
    ]

    col1, col2 = st.columns(2)

    with col1:

        source_language = st.selectbox(
            "Source Language",
            ["Auto Detect"] + languages,
        )

    with col2:

        target_language = st.selectbox(
            "Target Language",
            languages,
        )

    text = st.text_area(
        "Text",
        placeholder=(
            "Example: Where is the railway station?"
        ),
        height=130,
    )

    if st.button(
        "🌐 Translate",
        use_container_width=True,
    ):

        if not text.strip():

            st.warning(
                "Please enter text."
            )

        else:

            with st.spinner(
                "Translating..."
            ):

                result = translate_text(
                    text,
                    target_language,
                    source_language,
                )

            if result.get("success"):

                data = result.get(
                    "data",
                    {},
                )

                translation = data.get(
                    "translation"
                )

                if translation:

                    st.success(
                        "Translation completed."
                    )

                    st.subheader(
                        "Translation"
                    )

                    st.write(
                        translation
                    )

                else:

                    st.info(
                        data.get(
                            "message",
                            "Translation unavailable.",
                        )
                    )

            else:

                st.error(
                    result.get(
                        "error",
                        "Translation failed.",
                    )
                )


# ============================================================
# TOURIST GUIDE
# ============================================================

with tabs[3]:

    st.header("🏛️ Tourist Guide")

    if (
        latitude is None
        or longitude is None
    ):

        st.warning(
            "Allow location access first."
        )

    else:

        radius = st.slider(
            "Search Radius",
            5,
            30,
            15,
            5,
        )

        if st.button(
            "🔎 Find Tourist Attractions",
            use_container_width=True,
        ):

            with st.spinner(
                "Searching tourist attractions..."
            ):

                result = get_tourist_places(
                    latitude,
                    longitude,
                    radius=radius * 1000,
                    limit=10,
                )

            if result.get("success"):

                data = result.get(
                    "data",
                    {},
                )

                places = data.get(
                    "places",
                    [],
                )

                if places:

                    for place in places:

                        st.subheader(
                            f"🏛️ {safe_value(place.get('name'))}"
                        )

                        st.write(
                            f"📏 "
                            f"{number(place.get('distance_km'), 2)} km away"
                        )

                        st.write(
                            safe_value(
                                place.get(
                                    "address"
                                ),
                                "Address unavailable",
                            )
                        )

                        st.divider()

                else:

                    st.info(
                        "No tourist attractions found."
                    )

            else:

                st.error(
                    result.get(
                        "error",
                        "Tourist search failed.",
                    )
                )


# ============================================================
# CULTURE
# ============================================================

with tabs[4]:

    st.header("🎭 Local Culture")

    if location:

        city = safe_value(
            location.get("city"),
            "this city",
        )

        state = safe_value(
            location.get("state"),
            "this region",
        )

        language = get_local_language(
            location
        )

        st.info(
            f"📍 {city}, {state}\n\n"
            f"🗣️ Local language: {language}"
        )

        topics = [
            "What local food should a newcomer try here?",
            "What festivals are celebrated here?",
            "What local language should I learn?",
            "What local etiquette should visitors know?",
            "Tell me about the history and culture of this place.",
        ]

        topic = st.selectbox(
            "Choose a topic",
            topics,
        )

        if st.button(
            "🎭 Explore Local Culture",
            use_container_width=True,
        ):

            if (
                latitude is not None
                and longitude is not None
            ):

                with st.spinner(
                    "Learning about the local area..."
                ):

                    result = get_context(
                        topic,
                        latitude,
                        longitude,
                    )

                if result.get("success"):

                    data = result.get(
                        "data",
                        {},
                    )

                    answer = (
                        data.get("response")
                        or
                        data.get("general_response")
                        or
                        data.get("llm_response")
                    )

                    if answer:

                        st.write(
                            answer
                        )

                    else:

                        st.info(
                            "No culture information returned."
                        )

                else:

                    st.error(
                        result.get(
                            "error",
                            "Culture request failed.",
                        )
                    )

    else:

        st.info(
            "Allow location access to discover local culture."
        )


# ============================================================
# ASK ASSISTANT
# ============================================================

with tabs[5]:

    st.header("💬 Ask Assistant")

    st.write(
        "Ask anything about your current location."
    )

    examples = [
        "Where can I find some cash?",
        "Find a restaurant near me",
        "Where is the nearest hospital?",
        "What is the weather here?",
        "Where can I stay?",
        "What tourist places are nearby?",
        "What language do people speak here?",
        "Tell me about the local culture.",
    ]

    example = st.selectbox(
        "Example questions",
        ["Select an example..."] + examples,
    )

    query = st.text_area(
        "Your question",
        value=(
            ""
            if example == "Select an example..."
            else example
        ),
        height=120,
    )

    if st.button(
        "🚀 Ask Assistant",
        use_container_width=True,
    ):

        if not query.strip():

            st.warning(
                "Please enter a question."
            )

        elif (
            latitude is None
            or longitude is None
        ):

            st.warning(
                "Please allow location access first."
            )

        else:

            with st.spinner(
                "Understanding your request..."
            ):

                result = get_context(
                    query,
                    latitude,
                    longitude,
                )

            if result.get("success"):

                data = result.get(
                    "data",
                    {},
                )

                answer = (
                    data.get("response")
                    or data.get("general_response")
                    or data.get("llm_response")
                    or "No response available."
                )

                st.session_state.assistant_history.append(
                    {
                        "query": query,
                        "response": answer,
                    }
                )

                st.subheader(
                    "🤖 Assistant"
                )

                st.write(
                    answer
                )

                intent = data.get(
                    "intent"
                )

                if intent:

                    st.caption(
                        f"Detected intent: {intent}"
                    )

                recommendations = data.get(
                    "recommendations",
                    [],
                )

                if recommendations:

                    st.subheader(
                        "📍 Related Places"
                    )

                    for place in recommendations:

                        st.write(
                            f"📍 "
                            f"{safe_value(place.get('name'))}"
                        )

                        st.write(
                            f"📏 "
                            f"{number(place.get('distance_km'), 2)} km away"
                        )

                        st.write(
                            safe_value(
                                place.get("address"),
                                "Address unavailable",
                            )
                        )

                        st.divider()

            else:

                st.error(
                    result.get(
                        "error",
                        "Assistant request failed.",
                    )
                )

    # --------------------------------------------------------
    # History
    # --------------------------------------------------------

    if st.session_state.assistant_history:

        st.subheader(
            "🕘 Conversation History"
        )

        for item in reversed(
            st.session_state.assistant_history
        ):

            st.markdown(
                f"**You:** {item['query']}"
            )

            st.markdown(
                f"**Assistant:** {item['response']}"
            )

            st.divider()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Context-Aware Localization Agent • "
    "FastAPI + Streamlit • "
    "Open-Meteo • Geoapify • OpenStreetMap"
)