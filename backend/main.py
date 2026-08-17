import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rush_hour import RushHourError, classify_rush_hours, fetch_hourly_ratios, format_windows
from weather import WeatherError, fetch_weather

load_dotenv()

app = FastAPI(title="Rush Hour Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


class RushHourRequest(BaseModel):
    origin: str
    destination: str
    threshold: float = 1.15


class HourlyPoint(BaseModel):
    hour: int
    ratio: float
    congested: bool


class RushHourResponse(BaseModel):
    summary: str
    hourly: list[HourlyPoint]
    weather: dict | None = None


@app.post("/api/rush-hours", response_model=RushHourResponse)
def rush_hours(req: RushHourRequest):
    api_key = os.environ.get("TOMTOM_API_KEY")
    if not api_key:
        raise HTTPException(500, "Server is missing TOMTOM_API_KEY")

    try:
        ratios = fetch_hourly_ratios(req.origin, req.destination, api_key)
    except RushHourError as e:
        raise HTTPException(502, str(e))

    if not ratios:
        raise HTTPException(422, "No traffic data returned — check the addresses are valid and reachable by road.")

    windows = classify_rush_hours(ratios, req.threshold)

    weather = None
    weather_key = os.environ.get("OPENWEATHER_API_KEY")
    if weather_key:
        try:
            weather = fetch_weather(req.origin, weather_key)
        except WeatherError:
            pass  # weather is a bonus, not worth failing the whole request over

    return RushHourResponse(
        summary=format_windows(windows),
        hourly=[
            HourlyPoint(hour=hour, ratio=ratio, congested=ratio > req.threshold)
            for hour, ratio in ratios
        ],
        weather=weather,
    )
