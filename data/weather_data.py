#!/usr/bin/env python3
"""
Weather Data Fetcher for Fishing
Gets atmospheric pressure, wind, temperature from wttr.in
HKO 9-day forecast for extended wind data
"""

import requests
import json
import re
from datetime import datetime, date, timedelta
from collections import Counter

# Beaufort force to average wind speed (km/h)
_BEAUFORT_KMH = {0: 0, 1: 3, 2: 8, 3: 15, 4: 25, 5: 35, 6: 45, 7: 55, 8: 68, 9: 80, 10: 95, 11: 110, 12: 125}

# 16-point wind direction to degrees
_WIND_DIR_DEG = {
    'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
    'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
    'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
    'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5,
}


def parse_hko_wind(wind_str):
    """Parse HKO wind string like 'East force 4 to 5' into (km/h, direction)."""
    if not wind_str:
        return None, None
    
    dir_map = {
        'north to northeast': 'NNE', 'south to southeast': 'SSE',
        'east to southeast': 'ESE', 'west to southwest': 'WSW',
        'south to southwest': 'SSW', 'east to northeast': 'ENE',
        'north to northwest': 'NNW', 'west to northwest': 'WNW',
        'north': 'N', 'south': 'S', 'east': 'E', 'west': 'W',
        'northeast': 'NE', 'northwest': 'NW', 'southeast': 'SE', 'southwest': 'SW',
    }
    direction = None
    for name, code in sorted(dir_map.items(), key=lambda x: -len(x[0])):
        if name in wind_str.lower():
            direction = code
            break
    
    forces = [int(x) for x in re.findall(r'force\s+(\d+)', wind_str.lower())]
    if forces:
        avg_force = sum(forces) / len(forces)
        wind_kmh = _BEAUFORT_KMH.get(round(avg_force), 0)
    else:
        wind_kmh = None
    
    return wind_kmh, direction


def get_hko_forecast():
    """Fetch HKO 9-day forecast for extended wind data."""
    try:
        resp = requests.get('https://www.hko.gov.hk/wxinfo/json/one_json.xml', timeout=10)
        resp.raise_for_status()
        data = resp.json()
        f9d = data.get('F9D', {})
        forecasts = f9d.get('WeatherForecast', [])
        
        result = {}
        for fc in forecasts:
            date_str = fc.get('ForecastDate', '')
            if not date_str:
                continue
            formatted = f'{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}'
            
            wind_str = fc.get('ForecastWind', '')
            wind_kmh, wind_dir = parse_hko_wind(wind_str)
            
            result[formatted] = {
                'wind_kmh': wind_kmh,
                'wind_dir': wind_dir,
                'wind_str': wind_str,
            }
        
        return result
    except Exception as e:
        print(f'Error fetching HKO forecast: {e}')
        return {}

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
        hourly = day.get("hourly", [])
        avg_wind = 0
        avg_wind_dir = ""
        if hourly:
            winds = [int(h.get("windspeedKmph", 0)) for h in hourly]
            dirs = [h.get("winddir16Point", "") for h in hourly]
            avg_wind = sum(winds) // len(winds) if winds else 0
            from collections import Counter
            dir_counts = Counter(dirs)
            avg_wind_dir = dir_counts.most_common(1)[0][0] if dir_counts else ""
        result["forecast"].append({
            "date": day.get("date", ""),
            "max_temp_c": int(day.get("maxtempC", 0)),
            "min_temp_c": int(day.get("mintempC", 0)),
            "avg_pressure": int(hourly[0].get("pressure", 0)) if hourly else 0,
            "avg_wind_kmph": avg_wind,
            "avg_wind_dir": avg_wind_dir,
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
        return {"state": "平靜 (Calm)", "state_zh": "平靜", "wave": "<0.5m", "beaufort": "0-3", "risk": "✅ 安全", "risk_level": 1}
    elif wind_kmph <= 19:
        return {"state": "小浪 (Slight)", "state_zh": "小浪", "wave": "0.5-1.0m", "beaufort": "4", "risk": "✅ 一般注意", "risk_level": 2}
    elif wind_kmph <= 28:
        return {"state": "中浪 (Moderate)", "state_zh": "中浪", "wave": "1.0-2.0m", "beaufort": "5", "risk": "⚠️ 小心", "risk_level": 3}
    elif wind_kmph <= 38:
        return {"state": "大浪 (Rough)", "state_zh": "大浪", "wave": "2.0-3.0m", "beaufort": "6", "risk": "⚠️ 大浪危險", "risk_level": 4}
    elif wind_kmph <= 49:
        return {"state": "巨浪 (Very Rough)", "state_zh": "巨浪", "wave": "3.0-5.0m", "beaufort": "7", "risk": "❌ 不建議出海", "risk_level": 5}
    else:
        return {"state": "極巨浪 (High)", "state_zh": "極巨浪", "wave": ">5.0m", "beaufort": "8+", "risk": "❌ 禁止出海", "risk_level": 6}

# 16-point wind direction to degrees
_WIND_DIR_DEG = {
    'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
    'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
    'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
    'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5,
}

def _angle_diff(a, b):
    """Smallest angle between two bearings (0-180)."""
    d = abs(a - b) % 360
    return min(d, 360 - d)

# Spot exposure: which wind directions make this spot rough
# Format: spot_id -> list of 16-point dirs that cause rough seas at that spot
# Based on HK geography + terrain type
_SPOT_EXPOSURE = {
    # HK Island - south/east facing = rough in SE/S/E winds
    'shek_o': ['SE', 'SSE', 'S', 'E', 'ENE'],
    'big_wave_bay': ['SE', 'SSE', 'S', 'E', 'ENE'],
    'aberdeen': ['S', 'SSW', 'SW'],  # sheltered harbour
    'causeway_bay': [],  # typhoon shelter, very sheltered

    # Kowloon - east facing
    'lei_yue_mun': ['E', 'ENE', 'NE', 'SE'],
    'cha_kwo_ling': ['E', 'ENE', 'NE'],
    'sam_dip_wong': ['E', 'ENE', 'NE', 'SE'],

    # NT East - Tolo Harbour (sheltered) vs Sai Kung (exposed)
    'tolo_harbour': ['N', 'NNE', 'NE'],  # sheltered except north
    'tai_mei_tuk': ['N', 'NNE', 'NE'],
    'three_fathoms_cove': ['E', 'ENE'],
    'ma_on_shan_waterfront': ['N', 'NNE', 'NE'],
    'wu_kai_sha': ['N', 'NNE', 'NE'],
    'wu_kai_sha_pier': ['N', 'NNE', 'NE'],
    'pak_shek_kok': ['N', 'NE', 'E'],
    'tolo_harbour_front': ['N', 'NNE', 'NE'],
    'fo_tan': [],  # river, sheltered
    'shing_mun_river': [],  # river, sheltered
    'ma_on_shan_rocky': ['E', 'ENE', 'NE', 'SE'],

    # NT West - Deep Bay area, west facing
    'sham_tseng': ['SW', 'WSW', 'W'],
    'castle_peak_bay': ['SW', 'WSW', 'W', 'SSW'],
    'ting_kau': ['SW', 'WSW', 'W', 'S'],
    'anglers_beach': ['SW', 'WSW', 'W'],
    'lido_beach': ['SW', 'WSW', 'W'],
    'tsuen_wan_waterfront': ['SW', 'W'],
    'ma_wan': ['SW', 'WSW', 'W', 'SE'],
    'tsing_yi_waterfront': ['SW', 'W', 'NW'],
    'tuen_mun_waterfront': ['SW', 'W', 'SSW'],
    'sam_shing': ['SW', 'W', 'SSW'],
    'lau_fau_shan': ['W', 'WNW', 'NW', 'SW'],
    'lau_fau_shan_rocky': ['W', 'WNW', 'NW'],
    'pak_kong': ['W', 'NW', 'N'],
    'ha_tsuen': ['W', 'NW', 'N'],
    'tsim_be_tsui_west': ['W', 'NW', 'SW'],
    'lung_kwu_tan': ['W', 'SW', 'SSW'],

    # Islands - exposed
    'cheung_chau': ['SE', 'S', 'SW', 'E', 'W'],
    'lamma_island': ['SE', 'S', 'SW', 'E'],
    'lantau_tung_chung': ['W', 'NW', 'N'],
    'ping_chau': ['NE', 'NNE', 'E', 'SE'],  # most exposed east
    'crooked_island': ['N', 'NNE', 'NE', 'E'],

    # Sai Kung - exposed to east/southeast
    'sai_kung_town': ['SE', 'SSE', 'E'],
    'sai_kung_pier': ['SE', 'SSE', 'E'],
    'tui_min_chau': ['SE', 'SSE', 'E', 'NE'],
    'sharp_island': ['SE', 'SSE', 'E', 'S'],
    'pak_sha_chau': ['SE', 'E', 'SSE'],
    'sham_chuk_tsuen': ['E', 'ENE', 'NE'],
    'clear_water_bay': ['SE', 'SSE', 'E', 'S'],
    'clear_water_bay_1': ['SE', 'SSE', 'E'],
    'lobster_bay': ['SE', 'SSE', 'E', 'S'],
    'palm_beach': ['SE', 'E', 'SSE'],
    'tai_a_chau': ['SE', 'E', 'NE'],
    'po_toi_au': ['SE', 'SSE', 'E', 'S'],
    'tin_hau_temple_bay': ['SE', 'SSE', 'E'],
    'tai_chong_ting': ['SE', 'E', 'NE'],
    'high_island': ['SE', 'SSE', 'E', 'NE', 'S'],  # very exposed
    'tai_long_wan_west': ['SE', 'SSE', 'E', 'S', 'NE'],  # very exposed
    'long_ke': ['SE', 'SSE', 'E', 'S', 'NE'],  # very exposed
    'leung_shuen_wan': ['SE', 'E', 'NE', 'SSE'],
    'ham_tin_wan': ['SE', 'SSE', 'E', 'S', 'NE'],  # very exposed
    'chek_keng': ['SE', 'E', 'NE', 'NNE'],

    # Central - sheltered harbour
    'victoria_harbour': [],  # very sheltered
}

def estimate_spot_sea_state(wind_kmph, wind_dir, spot_id):
    """
    Estimate sea state for a specific spot considering wind direction and exposure.
    
    Returns dict with spot-specific wave estimate.
    """
    base = estimate_sea_state(wind_kmph)
    
    # Get spot exposure
    exposed_dirs = _SPOT_EXPOSURE.get(spot_id.strip(), None)
    
    # Check if wind blows towards this spot
    wind_deg = _WIND_DIR_DEG.get(wind_dir, None)
    if exposed_dirs is not None and len(exposed_dirs) == 0:
        # Fully sheltered spot (typhoon shelter, river, harbour)
        base['spot_note'] = '🏗️ 避風塘/內港，海浪影響極小'
        base['state_zh'] = '平靜'
        base['wave'] = '<0.3m'
        base['risk'] = '✅ 安全'
        base['risk_level'] = 1
        return base
    elif exposed_dirs is None or wind_deg is None:
        # No exposure data or wind dir unknown -> return base estimate
        base['spot_note'] = '一般海浪估計（未考慮地形）'
        return base
    
    # Calculate max exposure alignment
    max_alignment = 0
    for exp_dir in exposed_dirs:
        exp_deg = _WIND_DIR_DEG.get(exp_dir, None)
        if exp_deg is not None:
            alignment = 1 - (_angle_diff(wind_deg, exp_deg) / 180)  # 1=direct hit, 0=opposite
            max_alignment = max(max_alignment, alignment)
    
    # Spot type modifier
    from data.fishing_spots import FISHING_SPOTS
    spot = next((s for s in FISHING_SPOTS if s['id'].strip() == spot_id), None)
    terrain_type = spot.get('type', 'pier_shore') if spot else 'pier_shore'
    
    # Rocky/sandy shores more affected, piers/typhoon shelters less
    terrain_modifier = {
        'rocky_shore': 1.3,
        'sandy_shore': 1.2,
        'pier_shore': 1.0,
        'pier': 0.7,
        'typhoon_shelter': 0.3,
    }.get(terrain_type, 1.0)
    
    # Effective wind = base wind * terrain modifier * exposure alignment
    effective_wind = wind_kmph * terrain_modifier * (0.5 + 0.5 * max_alignment)
    
    # Get spot-specific sea state
    spot_state = estimate_sea_state(int(effective_wind))
    
    # Add spot-specific notes
    if max_alignment > 0.7:
        spot_state['spot_note'] = f'⚠️ {wind_dir}風正面吹向此釣點，海浪較大'
    elif max_alignment > 0.3:
        spot_state['spot_note'] = f'{wind_dir}風部分影響此釣點'
    else:
        spot_state['spot_note'] = f'{wind_dir}風背向此釣點，海浪較平靜'
    
    # Keep original base for comparison
    spot_state['base_state'] = base
    
    return spot_state

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