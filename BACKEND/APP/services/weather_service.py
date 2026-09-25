import requests


# --------------------------------------------------
# Weather Code Description
# --------------------------------------------------

def get_weather_description(weather_code: int | None):

    weather_descriptions = {

        0: "Clear sky",

        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",

        45: "Fog",
        48: "Depositing rime fog",

        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",

        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",

        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",

        66: "Light freezing rain",
        67: "Heavy freezing rain",

        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",

        77: "Snow grains",

        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",

        85: "Slight snow showers",
        86: "Heavy snow showers",

        95: "Thunderstorm",

        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    return weather_descriptions.get(
        weather_code,
        "Unknown weather"
    )


# --------------------------------------------------
# Coordinate Validation
# --------------------------------------------------

def validate_coordinates(
    latitude: float,
    longitude: float
):

    if not isinstance(latitude, (int, float)):
        return False

    if not isinstance(longitude, (int, float)):
        return False

    if not (-90 <= latitude <= 90):
        return False

    if not (-180 <= longitude <= 180):
        return False

    return True


# --------------------------------------------------
# Main Weather Service
# --------------------------------------------------

def get_weather(
    latitude: float,
    longitude: float
):

    # ----------------------------------------------
    # Validate coordinates
    # ----------------------------------------------

    if not validate_coordinates(
        latitude,
        longitude
    ):
        return None

    url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    # ----------------------------------------------
    # Current Weather
    # ----------------------------------------------

    current_variables = ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "weather_code",
        "wind_speed_10m",
        "wind_direction_10m",
        "cloud_cover",
        "pressure_msl",
        "surface_pressure",
        "precipitation",
        "rain",
        "visibility",
        "uv_index",
    ])

    # ----------------------------------------------
    # Hourly Weather
    # ----------------------------------------------

    hourly_variables = ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "weather_code",
        "precipitation_probability",
        "precipitation",
        "rain",
        "cloud_cover",
        "wind_speed_10m",
        "wind_direction_10m",
        "uv_index",
    ])

    # ----------------------------------------------
    # Daily Weather
    # ----------------------------------------------

    daily_variables = ",".join([
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min",
        "sunrise",
        "sunset",
        "uv_index_max",
        "precipitation_sum",
        "rain_sum",
        "precipitation_probability_max",
        "wind_speed_10m_max",
        "wind_direction_10m_dominant",
    ])

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": current_variables,

        "hourly": hourly_variables,

        "daily": daily_variables,

        "forecast_days": 7,

        "timezone": "auto",
    }

    # ----------------------------------------------
    # API Request
    # ----------------------------------------------

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

    except (
        requests.RequestException,
        ValueError,
        TypeError
    ) as error:

        print(
            f"Weather API request failed: {error}"
        )

        return None

    # ----------------------------------------------
    # Extract sections
    # ----------------------------------------------

    current = data.get(
        "current",
        {}
    )

    hourly = data.get(
        "hourly",
        {}
    )

    daily = data.get(
        "daily",
        {}
    )

    if not current:

        return None

    # ----------------------------------------------
    # Current Weather
    # ----------------------------------------------

    weather_code = current.get(
        "weather_code"
    )

    weather = {

        # Current temperature
        "temperature": current.get(
            "temperature_2m"
        ),

        # Humidity
        "humidity": current.get(
            "relative_humidity_2m"
        ),

        # Feels like
        "apparent_temperature": current.get(
            "apparent_temperature"
        ),

        # Weather condition
        "weather_code": weather_code,

        "weather_description":
            get_weather_description(
                weather_code
            ),

        # Wind
        "wind_speed": current.get(
            "wind_speed_10m"
        ),

        "wind_direction": current.get(
            "wind_direction_10m"
        ),

        # Clouds
        "cloud_cover": current.get(
            "cloud_cover"
        ),

        # Pressure
        "pressure": current.get(
            "pressure_msl"
        ),

        "surface_pressure": current.get(
            "surface_pressure"
        ),

        # Rain / precipitation
        "precipitation": current.get(
            "precipitation"
        ),

        "rain": current.get(
            "rain"
        ),

        # Visibility
        "visibility": current.get(
            "visibility"
        ),

        # UV
        "uv_index": current.get(
            "uv_index"
        ),

        # Timezone
        "timezone": data.get(
            "timezone"
        ),

        # Today's forecast
        "today_max_temperature": None,

        "today_min_temperature": None,

        "today_precipitation_probability": None,

        "sunrise": None,

        "sunset": None,

        # Forecast arrays
        "hourly_forecast": [],

        "daily_forecast": [],
    }

    # ----------------------------------------------
    # Today's Daily Data
    # ----------------------------------------------

    daily_times = daily.get(
        "time",
        []
    )

    if daily_times:

        weather["today_max_temperature"] = (
            daily.get(
                "temperature_2m_max",
                [None]
            )[0]
        )

        weather["today_min_temperature"] = (
            daily.get(
                "temperature_2m_min",
                [None]
            )[0]
        )

        weather[
            "today_precipitation_probability"
        ] = (
            daily.get(
                "precipitation_probability_max",
                [None]
            )[0]
        )

        weather["sunrise"] = (
            daily.get(
                "sunrise",
                [None]
            )[0]
        )

        weather["sunset"] = (
            daily.get(
                "sunset",
                [None]
            )[0]
        )

    # ----------------------------------------------
    # Hourly Forecast
    # ----------------------------------------------

    hourly_times = hourly.get(
        "time",
        []
    )

    for index, time in enumerate(
        hourly_times
    ):

        hourly_item = {

            "time": time,

            "temperature": (
                hourly.get(
                    "temperature_2m",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "temperature_2m",
                        []
                    )
                )
                else None
            ),

            "humidity": (
                hourly.get(
                    "relative_humidity_2m",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "relative_humidity_2m",
                        []
                    )
                )
                else None
            ),

            "apparent_temperature": (
                hourly.get(
                    "apparent_temperature",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "apparent_temperature",
                        []
                    )
                )
                else None
            ),

            "weather_code": (
                hourly.get(
                    "weather_code",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "weather_code",
                        []
                    )
                )
                else None
            ),

            "weather_description": (
                get_weather_description(
                    hourly.get(
                        "weather_code",
                        []
                    )[index]
                )
                if index < len(
                    hourly.get(
                        "weather_code",
                        []
                    )
                )
                else "Unknown weather"
            ),

            "precipitation_probability": (
                hourly.get(
                    "precipitation_probability",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "precipitation_probability",
                        []
                    )
                )
                else None
            ),

            "precipitation": (
                hourly.get(
                    "precipitation",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "precipitation",
                        []
                    )
                )
                else None
            ),

            "rain": (
                hourly.get(
                    "rain",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "rain",
                        []
                    )
                )
                else None
            ),

            "cloud_cover": (
                hourly.get(
                    "cloud_cover",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "cloud_cover",
                        []
                    )
                )
                else None
            ),

            "wind_speed": (
                hourly.get(
                    "wind_speed_10m",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "wind_speed_10m",
                        []
                    )
                )
                else None
            ),

            "wind_direction": (
                hourly.get(
                    "wind_direction_10m",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "wind_direction_10m",
                        []
                    )
                )
                else None
            ),

            "uv_index": (
                hourly.get(
                    "uv_index",
                    []
                )[index]
                if index < len(
                    hourly.get(
                        "uv_index",
                        []
                    )
                )
                else None
            ),
        }

        weather[
            "hourly_forecast"
        ].append(hourly_item)

    # ----------------------------------------------
    # Daily Forecast
    # ----------------------------------------------

    for index, date in enumerate(
        daily_times
    ):

        daily_item = {

            "date": date,

            "weather_code": (
                daily.get(
                    "weather_code",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "weather_code",
                        []
                    )
                )
                else None
            ),

            "weather_description": (
                get_weather_description(
                    daily.get(
                        "weather_code",
                        []
                    )[index]
                )
                if index < len(
                    daily.get(
                        "weather_code",
                        []
                    )
                )
                else "Unknown weather"
            ),

            "max_temperature": (
                daily.get(
                    "temperature_2m_max",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "temperature_2m_max",
                        []
                    )
                )
                else None
            ),

            "min_temperature": (
                daily.get(
                    "temperature_2m_min",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "temperature_2m_min",
                        []
                    )
                )
                else None
            ),

            "apparent_max_temperature": (
                daily.get(
                    "apparent_temperature_max",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "apparent_temperature_max",
                        []
                    )
                )
                else None
            ),

            "apparent_min_temperature": (
                daily.get(
                    "apparent_temperature_min",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "apparent_temperature_min",
                        []
                    )
                )
                else None
            ),

            "sunrise": (
                daily.get(
                    "sunrise",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "sunrise",
                        []
                    )
                )
                else None
            ),

            "sunset": (
                daily.get(
                    "sunset",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "sunset",
                        []
                    )
                )
                else None
            ),

            "uv_index_max": (
                daily.get(
                    "uv_index_max",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "uv_index_max",
                        []
                    )
                )
                else None
            ),

            "precipitation_sum": (
                daily.get(
                    "precipitation_sum",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "precipitation_sum",
                        []
                    )
                )
                else None
            ),

            "rain_sum": (
                daily.get(
                    "rain_sum",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "rain_sum",
                        []
                    )
                )
                else None
            ),

            "precipitation_probability": (
                daily.get(
                    "precipitation_probability_max",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "precipitation_probability_max",
                        []
                    )
                )
                else None
            ),

            "max_wind_speed": (
                daily.get(
                    "wind_speed_10m_max",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "wind_speed_10m_max",
                        []
                    )
                )
                else None
            ),

            "dominant_wind_direction": (
                daily.get(
                    "wind_direction_10m_dominant",
                    []
                )[index]
                if index < len(
                    daily.get(
                        "wind_direction_10m_dominant",
                        []
                    )
                )
                else None
            ),
        }

        weather[
            "daily_forecast"
        ].append(daily_item)

    return weather