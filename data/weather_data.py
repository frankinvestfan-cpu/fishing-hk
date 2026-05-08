#!/usr/bin/env python3
"""
Weather Data Fetcher for Fishing
Gets atmospheric pressure, wind, temperature from wttr.in
"""

import requests
import json
from datetime import datetime

def get_weather(location="Hong+Kong"):
    """Fetch weather data from wttr.in in JSON format."""
    try:
        resp = requests.get(f"https://wttr.in/{location}?format=j1", timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None
    
    current = data.get("current_condition", [{}])[0]
    weather = data.get("weather", [{}])
    
    result = {
        "location": location,
        "fetched_at": datetime.now().isoformat(),
        "current": {
            "temp_c": int(current.get("temp_C", 0)),
            "feels_like_c": int(current.get("FeelsLikeC", 0)),
            "humidity": int(current.get("humidity", 0)),
            "pressure_hpa": int(current.get("pressure", 0)),
            "wind_kmph": int(current.get("windspeedKmph", 0)),
            "wind_dir": current.get("winddir16Point", ""),
            "weather_desc": current.get("weatherDesc", [{}])[0].get("value", ""),
            "precip_mm": float(current.get("precipMM", 0)),
            "visibility_km": float(current.get("visibility", 0)),
            "wind_kmph": int(current.get("windspeedKmph", 0)),
            "wind_dir": current.get("winddir16Point", ""),
        },
        "sea_state": estimate_sea_state(int(current.get("windspeedKmph", 0))),
        "forecast": [],
    }
    
    for day in weather[:3]:
        result["forecast"].append({
            "date": day.get("date", ""),
            "max_temp_c": int(day.get("maxtempC", 0)),
            "min_temp_c": int(day.get("mintempC", 0)),
            "avg_pressure": int(day.get("hourly", [{}])[0].get("pressure", 0)) if day.get("hourly") else 0,
            "sunrise": day.get("astronomy", [{}])[0].get("sunrise", "") if day.get("astronomy") else "",
            "sunset": day.get("astronomy", [{}])[0].get("sunset", "") if day.get("astronomy") else "",
            "moon_phase": day.get("astronomy", [{}])[0].get("moon_phase", "") if day.get("astronomy") else "",
        })
    
    return result

def pressure_score(pressure_hpa):
    """
    Score atmospheric pressure for fishing (1-10).
    Falling/dropping pressure = fish more active.
    """
    # Normal sea level pressure: 1013 hPa
    if pressure_hpa >= 1020:
        return 3  # High pressure = less active
    elif pressure_hpa >= 1015:
        return 5
    elif pressure_hpa >= 1010:
        return 7  # Normal
    elif pressure_hpa >= 1005:
        return 9  # Falling = good
    else:
        return 8  # Very low, might storm

def wind_score(wind_kmph):
    """
    Score wind speed for fishing (1-10).
    Light wind = good, strong wind = bad.
    """
    if wind_kmph <= 10:
        return 9  # Calm - excellent
    elif wind_kmph <= 20:
        return 7  # Light breeze - good
    elif wind_kmph <= 30:
        return 5  # Moderate - ok
    elif wind_kmph <= 40:
        return 3  # Strong - difficult
    else:
        return 1  # Gale - stay home

def weather_score(weather_data):
    """Calculate overall weather fishing score (1-10)."""
    if not weather_data:
        return 5
    
    current = weather_data["current"]
    p_score = pressure_score(current["pressure_hpa"])
    w_score = wind_score(current["wind_kmph"])
    
    # Rain penalty
    precip = current["precip_mm"]
    if precip > 5:
        rain_score = 2
    elif precip > 1:
        rain_score = 4
    elif precip > 0:
        rain_score = 6
    else:
        rain_score = 8
    
    # Combined score
    total = (p_score * 0.4 + w_score * 0.35 + rain_score * 0.25)
    return round(total, 1)

def estimate_sea_state(wind_kmph):
    """Estimate sea state based on wind speed (Beaufort scale simplified)."""
    if wind_kmph <= 11:
        return {"state": "平靜 (Calm)", "state_zh": "平靜", "wave": "<0.5m", "beaufort": 0-3, "risk": "✅ 安全", "risk_level": 1}
    elif wind_kmph <= 19:
        return {"state": "小浪 (Slight)", "state_zh": "小浪", "wave": "0.5-1.0m", "beaufort": 4, "risk": "✅ 一般注意", "risk_level": 2}
    elif wind_kmph <= 28:
        return {"state": "中浪 (Moderate)", "state_zh": "中浪", "wave": "1.0-2.0m", "beaufort": 5, "risk": "⚠️ 小心", "risk_level": 3}
    elif wind_kmph <= 38:
        return {"state": "大浪 (Rough)", "state_zh": "大浪", "wave": "2.0-3.0m", "beaufort": 6, "risk": "⚠️ 大浪危險", "risk_level": 4}
    elif wind_kmph <= 49:
        return {"state": "巨浪 (Very Rough)", "state_zh": "巨浪", "wave": "3.0-5.0m", "beaufort": 7, "risk": "❌ 不建議出海", "risk_level": 5}
    else:
        return {"state": "極巨浪 (High)", "state_zh": "極巨浪", "wave": ">5.0m", "beaufort": "8+", "risk": "❌ 禁止出海", "risk_level": 6}

if __name__ == "__main__":
    data = get_weather()
    if data:
        print(f"🌤️ 香港天氣 ({data['fetched_at'][:16]})\n")
        c = data["current"]
        print(f"   溫度: {c['temp_c']}°C (體感 {c['feels_like_c']}°C)")
        print(f"   氣壓: {c['pressure_hpa']} hPa")
        print(f"   風速: {c['wind_kmph']} km/h {c['wind_dir']}")
        print(f"   濕度: {c['humidity']}%")
        print(f"   降雨: {c['precip_mm']}mm")
        print(f"   天氣: {c['weather_desc']}")
        
        print(f"\n📊 釣魚天氣評分:")
        print(f"   氣壓分: {pressure_score(c['pressure_hpa'])}/10")
        print(f"   風速分: {wind_score(c['wind_kmph'])}/10")
        print(f"   綜合分: {weather_score(data)}/10")