import os, requests
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/weather", tags=["Weather"])

@router.get("")
def weather(city: str = Query("Hyderabad")):
    key=os.getenv("WEATHER_API_KEY")
    if key:
        r=requests.get("https://api.openweathermap.org/data/2.5/weather",params={"q":city,"appid":key,"units":"metric"},timeout=8)
        r.raise_for_status(); d=r.json()
        return {"city":city,"temperature":d["main"]["temp"],"humidity":d["main"]["humidity"],"description":d["weather"][0]["description"]}
    return {"city":city,"temperature":30,"humidity":65,"description":"Demo weather (set WEATHER_API_KEY for live data)"}
