from fastapi import FastAPI

from APP.api.routes import router


app = FastAPI(
    title="Context-Aware Localization Agent",
    description="An AI agent that provides context-aware and location-aware responses.",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Context-Aware Localization Agent is running"
    }