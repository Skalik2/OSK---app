import httpx
from datetime import datetime, date
from typing import Optional, Dict, Any

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    95: "Thunderstorm"
}

def get_weather_description(code: int) -> str:
    return WEATHER_DESCRIPTIONS.get(code, "Unknown")


async def get_weather_for_date(lat: float, lon: float, target_date: date) -> Optional[Dict[str, Any]]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,weather_code",
        "timezone": "Europe/Warsaw",
        "start_date": target_date.isoformat(),
        "end_date": target_date.isoformat()
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            temps = daily.get("temperature_2m_max", [])
            codes = daily.get("weather_code", [])

            if temps and codes:
                code = codes[0]
                return {
                    "max_temp": temps[0],
                    "weather_code": code,
                    "description": get_weather_description(code)
                }
            return None

    except httpx.HTTPError:
        return None