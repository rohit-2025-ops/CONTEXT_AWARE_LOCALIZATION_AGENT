from datetime import datetime


def get_time_context():

    now = datetime.now()

    hour = now.hour

    if 5 <= hour < 12:
        period = "morning"
        greeting = "Good morning"

    elif 12 <= hour < 17:
        period = "afternoon"
        greeting = "Good afternoon"

    elif 17 <= hour < 21:
        period = "evening"
        greeting = "Good evening"

    else:
        period = "night"
        greeting = "Good night"

    return {
        "current_time": now.strftime("%I:%M %p"),
        "hour": hour,
        "period": period,
        "greeting": greeting
    }