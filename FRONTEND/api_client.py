import requests


BACKEND_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# Check Backend
# --------------------------------------------------

def check_backend():

    try:

        response = requests.get(
            f"{BACKEND_URL}/",
            timeout=5
        )

        if response.status_code == 200:

            return {
                "status": True,
                "message": "Backend is running"
            }

        return {
            "status": False,
            "message": (
                f"Backend returned "
                f"HTTP {response.status_code}"
            )
        }

    except requests.exceptions.RequestException as e:

        return {
            "status": False,
            "message": str(e)
        }


# --------------------------------------------------
# Get Context
# --------------------------------------------------

def get_context(
    query,
    latitude,
    longitude
):

    try:

        response = requests.post(
            f"{BACKEND_URL}/context",
            json={
                "query": query,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                }
            },
            timeout=60
        )

        if response.status_code == 200:

            return {
                "success": True,
                "data": response.json()
            }

        return {
            "success": False,
            "error": (
                f"Backend returned "
                f"HTTP {response.status_code}: "
                f"{response.text}"
            )
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "error": str(e)
        }


# --------------------------------------------------
# Get Current Location
# --------------------------------------------------

def get_location(
    latitude,
    longitude
):

    try:

        response = requests.get(
            f"{BACKEND_URL}/location",
            params={
                "latitude": latitude,
                "longitude": longitude
            },
            timeout=30
        )

        if response.status_code == 200:

            return {
                "success": True,
                "data": response.json()
            }

        return {
            "success": False,
            "error": (
                f"Backend returned "
                f"HTTP {response.status_code}: "
                f"{response.text}"
            )
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "error": str(e)
        }


# --------------------------------------------------
# Get Conversation History
# --------------------------------------------------

def get_history():

    try:

        response = requests.get(
            f"{BACKEND_URL}/history",
            timeout=10
        )

        if response.status_code == 200:

            return {
                "success": True,
                "data": response.json()
            }

        return {
            "success": False,
            "error": (
                f"Backend returned "
                f"HTTP {response.status_code}: "
                f"{response.text}"
            )
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "error": str(e)
        }
def get_tourist_places(
    latitude,
    longitude,
    radius=15000,
    limit=10,
):
    try:
        response = requests.get(
            f"{BACKEND_URL}/tourist",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
                "limit": limit,
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
            "error": (
                f"Backend returned HTTP "
                f"{response.status_code}: "
                f"{response.text}"
            ),
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
        }