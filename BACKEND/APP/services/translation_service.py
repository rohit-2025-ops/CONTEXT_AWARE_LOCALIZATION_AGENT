# --------------------------------------------------
# TRANSLATION SERVICE
# --------------------------------------------------

SUPPORTED_LANGUAGES = {
    "english": "English",
    "hindi": "Hindi",
    "bengali": "Bengali",
    "odia": "Odia",
    "telugu": "Telugu",
    "tamil": "Tamil",
    "kannada": "Kannada",
    "malayalam": "Malayalam",
    "marathi": "Marathi",
    "gujarati": "Gujarati",
    "punjabi": "Punjabi",
    "urdu": "Urdu",
}


def normalize_language(language: str) -> str:
    """
    Normalize the requested language name.
    """

    if not language:
        return ""

    language_key = (
        language
        .strip()
        .lower()
    )

    return SUPPORTED_LANGUAGES.get(
        language_key,
        language.strip()
    )


def translate_text(
    text: str,
    target_language: str,
    source_language: str = "Auto Detect",
):
    """
    Translation service interface.

    The actual translation backend is kept
    behind this service so the frontend does
    not need to know which AI model is being used.
    """

    if not text or not text.strip():

        return {
            "success": False,
            "source_language": source_language,
            "target_language": target_language,
            "original_text": "",
            "translation": "",
            "message": "Please enter text to translate.",
        }

    target = normalize_language(
        target_language
    )

    if not target:

        return {
            "success": False,
            "source_language": source_language,
            "target_language": "",
            "original_text": text.strip(),
            "translation": "",
            "message": "Please select a target language.",
        }

    # --------------------------------------------------
    # DEVELOPMENT TRANSLATION BACKEND
    # --------------------------------------------------
    #
    # For now we use a small verified phrase
    # dictionary for development testing.
    #
    # This is NOT intended to be the final
    # production translation engine.
    #
    # The Snapdragon AI model will later replace
    # this section.
    # --------------------------------------------------

    translations = {

        (
            "where is the railway station?",
            "Odia",
        ): "ରେଳ ଷ୍ଟେସନ କେଉଁଠାରେ ଅଛି?",

        (
            "where is the railway station?",
            "Hindi",
        ): "रेलवे स्टेशन कहाँ है?",

        (
            "where is the railway station?",
            "Bengali",
        ): "রেলওয়ে স্টেশন কোথায়?",

        (
            "where is the railway station?",
            "Telugu",
        ): "రైల్వే స్టేషన్ ఎక్కడ ఉంది?",

        (
            "where is the railway station?",
            "Tamil",
        ): "ரயில் நிலையம் எங்கே உள்ளது?",

        (
            "thank you",
            "Odia",
        ): "ଧନ୍ୟବାଦ",

        (
            "thank you",
            "Hindi",
        ): "धन्यवाद",

        (
            "thank you",
            "Bengali",
        ): "ধন্যবাদ",

        (
            "hello",
            "Odia",
        ): "ନମସ୍କାର",

        (
            "hello",
            "Hindi",
        ): "नमस्ते",

        (
            "hello",
            "Bengali",
        ): "নমস্কার",
    }

    key = (
        text.strip().lower(),
        target,
    )

    translation = translations.get(key)

    if translation:

        return {
            "success": True,
            "source_language": source_language,
            "target_language": target,
            "original_text": text.strip(),
            "translation": translation,
            "message": "Translation completed.",
        }

    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------

    return {
        "success": False,
        "source_language": source_language,
        "target_language": target,
        "original_text": text.strip(),
        "translation": "",
        "message": (
            "This phrase is not available in the "
            "development translation dictionary yet. "
            "The production AI translation backend "
            "will handle arbitrary text."
        ),
    }