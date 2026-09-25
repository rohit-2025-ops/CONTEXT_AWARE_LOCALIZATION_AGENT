from fastapi import APIRouter
from APP.services.history_service import get_history
from APP.services.location_service import get_location
from APP.services.tourist_service import get_tourist_places
from APP.services.translation_service import translate_text
from APP.agents.context_agent import collect_context
from APP.schemas.context_schema import (
    ContextRequest,
    ContextResponse
)


router = APIRouter()


@router.post("/context", response_model=ContextResponse)
def get_context(request: ContextRequest):

    return collect_context(
        request.query,
        request.location.latitude,
        request.location.longitude
    )
@router.get("/history")
def history():
    return get_history()

@router.get("/location")
def get_current_location(
    latitude: float,
    longitude: float
):

    return get_location(
        latitude=latitude,
        longitude=longitude
    )
@router.post("/translate")
def translate(
    text: str,
    target_language: str,
    source_language: str = "Auto Detect",
):
    """
    Translate user-provided text into the
    requested target language.
    """

    return translate_text(
        text=text,
        target_language=target_language,
        source_language=source_language,
    )
@router.get("/tourist")
def tourist_places(
    latitude: float,
    longitude: float,
    radius: int = 15000,
    limit: int = 10,
):
    """
    Get real tourist attractions near the user's location.
    """

    return get_tourist_places(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        limit=limit,
    )