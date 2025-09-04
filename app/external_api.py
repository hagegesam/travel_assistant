# app/external_api.py
from __future__ import annotations
import requests, math
from typing import Optional, Dict, Any

# Very light geocoding using Open-Meteo's free geocoding (no key)
def geocode_city(city: str) -> Optional[Dict[str, Any]]:
    if not city:
        return None
    try:
        resp = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1})
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data.get("results"):
            return None
        r = data["results"][0]
        return {"name": r["name"], "lat": r["latitude"], "lon": r["longitude"], "country": r.get("country")}
    except Exception:
        return None

def fetch_weather_summary(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Fetch a basic daily forecast (next 7 days) and return a compact summary (min/max temps & precip prob)."""
    try:
        params = {
            "latitude": lat, "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "forecast_days": 7, "timezone": "auto",
        }
        resp = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=20)
        if resp.status_code != 200:
            return None
        data = resp.json()
        daily = data.get("daily", {})
        # Build a compact summary
        days = []
        for i, date in enumerate(daily.get("time", [])[:5]):
            days.append({
                "date": date,
                "t_min": daily.get("temperature_2m_min", [None])[i],
                "t_max": daily.get("temperature_2m_max", [None])[i],
                "precip_prob": daily.get("precipitation_probability_max", [None])[i],
            })
        return {"lat": lat, "lon": lon, "days": days}
    except Exception:
        return None

def country_info_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Query REST Countries for basic info: name, capital, currencies, languages."""
    try:
        resp = requests.get(f"https://restcountries.com/v3.1/name/{name}", params={"fields": "name,capital,currencies,languages,cca2,region"}, timeout=20)
        if resp.status_code != 200:
            return None
        arr = resp.json()
        if not isinstance(arr, list) or not arr:
            return None
        c = arr[0]
        return {
            "name": c.get("name", {}).get("common"),
            "capital": c.get("capital", [None])[0] if c.get("capital") else None,
            "currencies": list((c.get("currencies") or {}).keys()),
            "languages": list((c.get("languages") or {}).values()),
            "cca2": c.get("cca2"),
            "region": c.get("region"),
        }
    except Exception:
        return None
