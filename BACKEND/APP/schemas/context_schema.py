from pydantic import BaseModel


# --------------------------------------------------
# User Location
# --------------------------------------------------

class UserLocation(BaseModel):

    latitude: float

    longitude: float


# --------------------------------------------------
# Context Request
# --------------------------------------------------

class ContextRequest(BaseModel):

    query: str

    location: UserLocation


# --------------------------------------------------
# Location Context
# --------------------------------------------------

class LocationContext(BaseModel):

    area: str | None

    city: str | None

    district: str | None

    state: str | None

    country: str | None

    postcode: str | None

    road: str | None

    house_number: str | None

    display_name: str | None

    latitude: float | None

    longitude: float | None


# --------------------------------------------------
# Place Context
# --------------------------------------------------

class PlaceContext(BaseModel):
    name: str
    brand: str | None = None
    operator: str | None = None
    type: str | None = None
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_km: float
    osm_id: int | None = None
    osm_type: str | None = None

# --------------------------------------------------
# Weather Context
# --------------------------------------------------

# --------------------------------------------------
# Weather Context
# --------------------------------------------------

class WeatherContext(BaseModel):

    # Current weather
    temperature: float | None = None

    humidity: float | None = None

    apparent_temperature: float | None = None

    weather_code: int | None = None

    weather_description: str | None = None

    wind_speed: float | None = None

    wind_direction: float | None = None

    cloud_cover: float | None = None

    pressure: float | None = None

    precipitation: float | None = None

    rain: float | None = None

    visibility: float | None = None

    uv_index: float | None = None

    # Location/time information
    timezone: str | None = None

    # Today's forecast
    today_max_temperature: float | None = None

    today_min_temperature: float | None = None

    today_precipitation_probability: float | None = None

    sunrise: str | None = None

    sunset: str | None = None

    # Forecast
    hourly_forecast: list[dict] = []

    daily_forecast: list[dict] = []


# --------------------------------------------------
# Time Context
# --------------------------------------------------

class TimeContext(BaseModel):

    current_time: str

    hour: int

    period: str

    greeting: str


# --------------------------------------------------
# Context Response
# --------------------------------------------------

class ContextResponse(BaseModel):

    time: TimeContext

    location: LocationContext

    intent: str

    nearby_places: list[PlaceContext]

    weather: WeatherContext | None

    recommendations: list[PlaceContext]

    general_response: str | None

    response: str | None

    knowledge: list[str]

    llm_context: str

    llm_response: str