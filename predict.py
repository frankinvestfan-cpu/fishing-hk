#!/usr/bin/env python3
"""
Hong Kong Fishing Predictor
Combines tide, moon, weather, and spot data to predict best fishing times and locations.

Feeding Score = Tide(30%) + Moon(20%) + Time(20%) + Pressure(15%) + Temp(10%) + Wind(5%)
"""

import sys
import json
from datetime import datetime, date, timedelta
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data.moon_phase import moon_phase_calc, next_best_fishing_days
from data.fishing_spots import FISHING_SPOTS, FISH_SPECIES, get_seasonal_fish, get_spots_by_fish
from data.weather_data import get_weather, weather_score, pressure_score, wind_score
from data.solunar import solunar_periods, solunar_activity_score, daily_solunar_rating
from data.hko_tide_parser import parse_station, get_tide_for_date, get_tide_range, find_best_fishing_tides, STATIONS, get_tide_station_for_spot
from data.terrain import get_terrain_info
from data.water_quality import WATER_EDIBILITY

import os

# Cache for tide data (per station)
_tide_cache = {}

def _find_tide_pdf():
    """Find tide PDF - check bundled location first, then /tmp."""
    bundled = os.path.join(os.path.dirname(__file__), 'data', 'TideTable2026.pdf')
    if os.path.exists(bundled):
        return bundled
    tmp_path = '/tmp/TideTable2026.pdf'
    if os.path.exists(tmp_path):
        return tmp_path
    return None

def get_tide_data(station="QB"):
    """Get tide data for a specific station. Cached per station."""
    global _tide_cache
    if station not in _tide_cache:
        # Try JSON first (works without PyMuPDF)
        json_path = os.path.join(os.path.dirname(__file__), 'data', f'hko_tides_{station}_2026.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                _tide_cache[station] = json.load(f)
        else:
            # Fallback to PDF
            pdf_path = _find_tide_pdf()
            if pdf_path:
                _tide_cache[station] = parse_station(pdf_path, station)
            else:
                _tide_cache[station] = {}
    return _tide_cache[station]

def get_all_tide_data():
    """Load tide data for all available stations."""
    results = {}
    for st in STATIONS:
        results[st] = get_tide_data(st)
    return results

def time_score(hour=None):
    """
    Score time of day for fishing (1-10).
    Dawn and dusk are best.
    """
    if hour is None:
        hour = datetime.now().hour
    
    # Best fishing times
    if 5 <= hour <= 7:     # Dawn
        return 10
    elif 17 <= hour <= 19:  # Dusk
        return 9
    elif 7 <= hour <= 9:    # Morning
        return 8
    elif 19 <= hour <= 21:  # Evening
        return 7
    elif 21 <= hour <= 23:  # Night
        return 6
    elif 9 <= hour <= 11:   # Late morning
        return 5
    elif 15 <= hour <= 17:  # Afternoon
        return 4
    elif 11 <= hour <= 15:  # Midday (worst)
        return 3
    else:                   # After midnight
        return 4

def tide_score_from_range(tide_range):
    """
    Score tide range for fishing (1-10).
    Larger range = more water movement = more fish activity.
    """
    if tide_range is None:
        return 5  # Default if no data
    
    # HK typical range: 0.5m (neap) to 2.5m+ (spring)
    if tide_range >= 2.0:
        return 10  # Big spring tide
    elif tide_range >= 1.5:
        return 8
    elif tide_range >= 1.0:
        return 6
    elif tide_range >= 0.7:
        return 4   # Small neap tide
    else:
        return 3

def calculate_feeding_score(moon_data, weather_data, hour=None, tide_range=None):
    """
    Calculate overall feeding score (1-10).
    Feeding Score = Tide(30%) + Moon(20%) + Time(20%) + Pressure(15%) + Temp(10%) + Wind(5%)
    
    Uses HKO real tide data when available.
    """
    moon_s = moon_data["tide_score"]
    time_s = time_score(hour)
    
    # Use real tide data (default to QB for overall score)
    tide_data = get_tide_data("QB")
    today = date.today()
    real_tide = get_tide_range(tide_data, today)
    
    if real_tide:
        tide_s = tide_score_from_range(real_tide["range"])
        tide_range = real_tide["range"]
    elif tide_range is not None:
        tide_s = tide_score_from_range(tide_range)
    else:
        tide_s = moon_s  # Fallback to moon estimate
    
    if weather_data:
        pressure_s = pressure_score(weather_data["current"]["pressure_hpa"])
        wind_s = wind_score(weather_data["current"]["wind_kmph"])
        temp = weather_data["current"]["temp_c"]
        
        # Temperature score (20-28°C optimal for HK fish)
        if 22 <= temp <= 28:
            temp_s = 10
        elif 18 <= temp < 22 or 28 < temp <= 32:
            temp_s = 7
        elif 14 <= temp < 18 or 32 < temp <= 35:
            temp_s = 4
        else:
            temp_s = 2
    else:
        pressure_s = 5
        wind_s = 5
        temp_s = 5
    
    # Weighted combination
    feeding = (
        tide_s * 0.30 +
        moon_s * 0.20 +
        time_s * 0.20 +
        pressure_s * 0.15 +
        temp_s * 0.10 +
        wind_s * 0.05
    )
    
    return round(min(10, max(1, feeding)), 1), {
        "tide": tide_s,
        "moon": moon_s,
        "time": time_s,
        "pressure": pressure_s,
        "temp": temp_s,
        "wind": wind_s,
    }

def get_best_time_slots(feeding_score_func, moon_data, weather_data, tide_range=None):
    """Find best time slots for today."""
    slots = []
    for hour in range(0, 24, 2):  # Every 2 hours
        score, breakdown = feeding_score_func(moon_data, weather_data, hour, tide_range)
        slots.append({
            "hour": f"{hour:02d}:00",
            "score": score,
            "breakdown": breakdown,
        })
    return sorted(slots, key=lambda x: x["score"], reverse=True)

def recommend_spots(feeding_score, month=None, fish_target=None, difficulty=None):
    """Recommend fishing spots based on conditions."""
    spots = FISHING_SPOTS.copy()
    
    # Filter by seasonal fish
    if month is None:
        month = str(date.today().month)
    seasonal_fish = get_seasonal_fish(month)
    
    # Filter by target fish
    if fish_target:
        spots = [s for s in spots if fish_target in s["fish"]]
    
    # Filter by difficulty
    if difficulty:
        spots = [s for s in spots if s["difficulty"] == difficulty]
    
    # Adjust rating based on feeding score
    for spot in spots:
        # Higher feeding score = spots with matching fish get bonus
        seasonal_bonus = sum(1 for f in spot["fish"] if f in seasonal_fish) / len(spot["fish"]) * 2
        spot["adjusted_rating"] = round(spot["rating"] * 0.6 + feeding_score * 0.3 + seasonal_bonus, 1)
    
    # Sort by adjusted rating
    spots.sort(key=lambda x: x["adjusted_rating"], reverse=True)
    return spots[:10]

def format_fishing_report(target_date=None, fish_target=None):
    """Generate a complete fishing report."""
    if target_date is None:
        target_date = date.today()
    
    hour = datetime.now().hour
    
    print("=" * 55)
    print(f"🎣 香港釣魚預測報告")
    print(f"📅 {target_date.strftime('%Y年%m月%d日')} {['一','二','三','四','五','六','日'][target_date.weekday()]}曜日")
    print("=" * 55)
    
    # Moon
    moon = moon_phase_calc(target_date)
    print(f"\n🌙 月相: {moon['phase_name']} 光照:{moon['illumination']}%")
    print(f"   潮汐類型: {moon['tide_type']} 潮水分:{moon['tide_score']}/10")
    
    # HKO Real Tide Data — show all stations with spots
    all_tide = get_all_tide_data()
    
    # Build station → spot count mapping
    station_spots = {}
    for s in FISHING_SPOTS:
        st = get_tide_station_for_spot(s["id"])
        station_spots.setdefault(st, []).append(s["name_zh"])
    
    # Show tide for each station that has spots
    print(f"\n🌊 HKO 真實潮汐:")
    for st_code in ["QB", "KLW", "MW", "KC", "CC", "CLK_E"]:
        if st_code not in station_spots:
            continue
        st_tide = all_tide.get(st_code, {})
        st_events = get_tide_for_date(st_tide, target_date) if st_tide else []
        st_range = get_tide_range(st_tide, target_date) if st_tide else None
        st_name = STATIONS.get(st_code, {}).get("name", st_code)
        st_name_zh = STATIONS.get(st_code, {}).get("name_zh", st_code)
        spot_count = len(station_spots[st_code])
        
        if st_events:
            print(f"   📍 {st_name_zh} ({st_name}) [{spot_count}釣點]:")
            for e in sorted(st_events, key=lambda x: x["time"]):
                emoji = "🔺" if e["type"] == "high" else "🔻"
                label = "高潮" if e["type"] == "high" else "低潮"
                print(f"      {emoji} {e['time']}  {e['height']}m  ({label})")
            if st_range:
                print(f"      潮差: {st_range['range']}m  最高:{st_range['max_high']}m  最低:{st_range['min_low']}m")
            
            # Best fishing tide windows
            windows = find_best_fishing_tides(st_tide, target_date)
            if windows:
                top_w = sorted(windows, key=lambda x: x["score"], reverse=True)[0]
                print(f"      🎣 最佳時窗: {top_w['start']}-{top_w['end']} {top_w['direction']} 變化:{top_w['height_change']}m")
        else:
            print(f"   📍 {st_name_zh} ({st_name}) [{spot_count}釣點]: ⚠️ 無數據")
    
    # Use QB as default for overall tide score
    tide_data = all_tide.get("QB", {})
    real_tide = get_tide_range(tide_data, target_date) if tide_data else None
    
    if not tide_data:
        print(f"\n⚠️ 未找到HKO潮汐數據，使用月相估算")
    
    # Weather
    print(f"\n🌤️ 正在獲取天氣...")
    weather = get_weather()
    if weather:
        c = weather["current"]
        print(f"   溫度: {c['temp_c']}°C (體感 {c['feels_like_c']}°C)")
        print(f"   氣壓: {c['pressure_hpa']} hPa")
        print(f"   風速: {c['wind_kmph']}km/h {c['wind_dir']}")
        print(f"   天氣: {c['weather_desc']}")
    else:
        print("   ⚠️ 未能獲取天氣數據")
    
    # Feeding Score
    score, breakdown = calculate_feeding_score(moon, weather, hour)
    print(f"\n🐟 今日釣魚指數: {score}/10", end=" ")
    if score >= 8:
        print("🔥🔥🔥 極佳！")
    elif score >= 6:
        print("✅ 不錯！")
    elif score >= 4:
        print("😐 一般")
    else:
        print("👎 差")
    
    print(f"   潮水:{breakdown['tide']}/10  月相:{breakdown['moon']}/10  時段:{breakdown['time']}/10")
    print(f"   氣壓:{breakdown['pressure']}/10  溫度:{breakdown['temp']}/10  風速:{breakdown['wind']}/10")
    
    # Solunar periods (from tides4fishing theory)
    print(f"\n🕐 Solunar 時段 (太陰太陽論):")
    periods = solunar_periods(target_date)
    for p in periods:
        emoji = "🔴" if p["type"] == "major" else "🟡"
        label = "Major (大活動期)" if p["type"] == "major" else "Minor (小活動期)"
        print(f"   {emoji} {p['start']}-{p['end']} {p['description']} [{label}]")
    
    # Hourly solunar activity
    print(f"\n⏰ 逐時活動預測 (Solunar + 潮汐 + 天氣):")
    for hour in range(0, 24, 2):
        # Combine solunar score with feeding score
        solunar_s = solunar_activity_score(target_date, hour)
        _, breakdown = calculate_feeding_score(moon, weather, hour)
        combined = round(solunar_s * 0.5 + breakdown["tide"] * 0.2 + breakdown["pressure"] * 0.15 + breakdown["temp"] * 0.1 + breakdown["wind"] * 0.05, 1)
        # Per-spot tide: use spot's station for hourly score
        # (overall breakdown still uses QB default)
        combined = min(10, max(1, combined))
        bar = "█" * int(combined) + "░" * (10 - int(combined))
        print(f"   {hour:02d}:00  {bar} {combined}/10")
    
    # Best fishing days ahead (Solunar + tide)
    cn_days = ['一', '二', '三', '四', '五', '六', '日']
    default_tide = get_tide_data("QB")
    print(f"\n📅 未來7日釣魚預測 (Solunar + 潮汐):")
    for i in range(7):
        d = target_date + timedelta(days=i)
        r = daily_solunar_rating(d)
        d_range = get_tide_range(default_tide, d) if default_tide else None
        tide_str = f'潮差{d_range["range"]}m' if d_range else '潮差?'
        rng = d_range['range'] if d_range else 0
        tide_emoji = '🔥' if rng >= 2.3 else ('✅' if rng >= 1.8 else '  ')
        print(f"   {d.month}/{d.day} {cn_days[d.weekday()]}  {r['moon_phase']} 係數:{r['tidal_coefficient']} {tide_str} {tide_emoji} {r['label']}")
    
    # Seasonal fish
    month = str(target_date.month)
    seasonal = get_seasonal_fish(month)
    print(f"\n🐟 當季魚種 ({target_date.strftime('%B')}):")
    for name, info in seasonal.items():
        best_time = "/".join(info["best_time"])
        print(f"   {name} ({info['en']}) {info['avg_size']} 最佳時段:{best_time}")
    
    # Recommended spots with terrain (use per-spot tide station)
    print(f"\n📍 推薦釣點:")
    spots = recommend_spots(score, month, fish_target)
    for s in spots[:5]:
        spot_id = s["id"].strip()
        spot_station = get_tide_station_for_spot(spot_id)
        spot_tide = get_tide_data(spot_station)
        spot_tide_range = get_tide_range(spot_tide, target_date) if spot_tide else None
        station_name_zh = STATIONS.get(spot_station, {}).get("name_zh", spot_station)
        
        fish_str = "、".join(s["fish"][:3])
        terrain = get_terrain_info(spot_id)
        wq = WATER_EDIBILITY.get(spot_id, {})
        wq_icons = {"excellent": "✅✅", "good": "✅", "moderate": "⚠️", "poor": "❌"}
        wq_icon = wq_icons.get(wq.get("water_quality", ""), "❓")
        print(f"   {s['rating']}/10 ⭐{s['adjusted_rating']} {s['name_zh']} ({s['name_en']})")
        print(f"         {s['district']} | {s['difficulty']} | {fish_str}")
        if spot_tide_range:
            print(f"         🌊 {station_name_zh} 潮差:{spot_tide_range['range']}m 最高:{spot_tide_range['max_high']}m 最低:{spot_tide_range['min_low']}m")
        if terrain:
            print(f"         🏖️ {terrain.get('terrain', '')} | 🌊 {terrain.get('seabed', '')} | 📏 {terrain.get('depth', '')}")
            print(f"         🎣 釣法: {terrain.get('best_method', '')} | 🪱 魚餌: {terrain.get('best_bait', '')}")
            print(f"         🌊 潮水: {terrain.get('tide_preference', '')}")
        if wq:
            print(f"         🚰 水質: {wq_icon} {wq.get('water_quality_zh', '')}")
            edible_str = ', '.join([f"{k}✅" if v=='yes' else f"{k}⚠️" if v=='limit' else f"{k}❌" for k,v in wq.get('edible', {}).items()])
            print(f"         🍴 可食: {edible_str}")
        if terrain:
            if terrain.get('night_fishing'):
                print(f"         🌙 可夜釣 | {terrain.get('tips', '')}")
            else:
                print(f"         ☀️ 只限日釣 | {terrain.get('tips', '')}")
        else:
            print(f"         {s['notes']}")
    
    print(f"\n" + "=" * 55)

def find_spot(query):
    """Find a spot by id, name (zh/en), or partial match."""
    query = query.strip().lower().replace(' ', '_')
    # Map common aliases
    aliases = {
        '龍蝦灣': 'lobster_bay', '清水灣': 'clear_water_bay',
        '三門仔': 'sam mun_tsai', '大美督': 'tai_mei_tuk',
        '萬宜': 'high_island', '東壩': 'high_island',
        '白沙洲': 'pak_sha_chau', '東平洲': 'ping_chau',
        '吉澳': 'crooked_island', '長洲': 'cheung_chau',
        '南丫島': 'lamma_island', '馬灣': 'ma_wan',
        '深井': 'sham_tseng', '流浮山': 'lau_fau_shan',
        '香港仔': 'aberdeen', '石澳': 'shek_o',
        '鯉魚門': 'lei_yue_mun', '布袋澳': 'po_toi_au',
        '西貢': 'sai_kung_town', '屯門': 'tuen_mun_waterfront',
        '青衣': 'tsing_yi_waterfront', '荃灣': 'tsuen_wan_waterfront',
        '大浪灣': 'big_wave_bay', '橋咀洲': 'sharp_island',
        '汀九': 'ting_kau', '釣魚翁': 'tui_min_chau',
        '大美督': 'tai_mei_tuk', '烏溪沙': 'wu_kai_sha',
        '馬鞍山': 'ma_on_shan_waterfront',
        '龍鼓灘': 'lung_kwu_tan',
        '大浪西灣': 'tai_long_wan_west', '浪茄': 'long_ke',
        '糧船灣': 'leung_shuen_wan', '貝澳': 'pui_o',
        '鹹田灣': 'ham_tin_wan', '赤徑': 'chek_keng',
    }
    # Direct alias match
    if query in aliases:
        return aliases[query]
    # Match by id
    for s in FISHING_SPOTS:
        if s['id'].strip() == query:
            return s['id'].strip()
    # Match by Chinese name
    for s in FISHING_SPOTS:
    	if query in s['name_zh'] or s['name_zh'] in query:
    	    return s['id'].strip()
    # Match by English name
    for s in FISHING_SPOTS:
        if query in s['name_en'].lower() or s['name_en'].lower() in query:
            return s['id'].strip()
    # Fuzzy: partial match any field
    for s in FISHING_SPOTS:
        searchable = f"{s['id']} {s['name_zh']} {s['name_en']}"
        if query in searchable.lower() or any(c in searchable for c in query if ord(c) > 127):
            return s['id'].strip()
    return None


def format_spot_guide(spot_id, target_date=None, fish_target=None):
    """Generate a detailed fishing guide for a specific spot."""
    if target_date is None:
        target_date = date.today()
    hour = datetime.now().hour
    
    spot = next((s for s in FISHING_SPOTS if s['id'].strip() == spot_id), None)
    if not spot:
        print(f"❌ 找不到釣點: {spot_id}")
        return
    
    station = get_tide_station_for_spot(spot_id)
    station_name_zh = STATIONS.get(station, {}).get('name_zh', station)
    tide = get_tide_data(station)
    events = get_tide_for_date(tide, target_date) if tide else []
    tide_range = get_tide_range(tide, target_date) if tide else None
    windows = find_best_fishing_tides(tide, target_date) if tide else []
    moon = moon_phase_calc(target_date)
    weather = get_weather()
    terrain = get_terrain_info(spot_id)
    wq = WATER_EDIBILITY.get(spot_id, {})
    periods = solunar_periods(target_date)
    
    # Scores
    score, breakdown = calculate_feeding_score(moon, weather, hour)
    
    print('=' * 55)
    print(f'🎣 {spot["name_zh"]} ({spot["name_en"]}) 釣魚指南')
    print(f'📅 {target_date.strftime("%Y年%m月%d日")}')
    print('=' * 55)
    
    # === Spot Info ===
    print(f'\n📍 釣點資料:')
    print(f'   區域: {spot["district"]} | 難度: {spot["difficulty"]} | 類型: {spot["type"]}')
    print(f'   目標魚: {"、".join(spot["fish"])}')
    print(f'   潮汐站: {station_name_zh} ({STATIONS.get(station, {}).get("name", station)})')
    
    if terrain:
        print(f'\n🏖️ 地形:')
        print(f'   地形: {terrain.get("terrain", "")}')
        print(f'   海床: {terrain.get("seabed", "")}')
        print(f'   水深: {terrain.get("depth", "")}')
        print(f'   最佳釣法: {terrain.get("best_method", "")}')
        print(f'   最佳魚餌: {terrain.get("best_bait", "")}')
        print(f'   潮水偏好: {terrain.get("tide_preference", "")}')
        hazards = terrain.get('hazards', '')
        if hazards:
            print(f'   ⚠️ 危險: {hazards}')
        print(f'   夜釣: {"✅ 可以" if terrain.get("night_fishing") else "❌ 不建議"}')
        facilities = terrain.get('facilities', '')
        if facilities:
            print(f'   設施: {facilities}')
        parking = terrain.get('parking', '')
        if parking:
            print(f'   停車: {parking}')
        tips = terrain.get('tips', '')
        if tips:
            print(f'   💡 貼士: {tips}')
    
    # Water quality
    wq_icons = {'excellent': '✅✅', 'good': '✅', 'moderate': '⚠️', 'poor': '❌'}
    if wq:
        wq_icon = wq_icons.get(wq.get('water_quality', ''), '❓')
        print(f'\n🚰 水質: {wq_icon} {wq.get("water_quality_zh", "")}')
        edible = wq.get('edible', {})
        if edible:
            print(f'   食用建議:')
            for fish, v in edible.items():
                icon = '✅放心食' if v == 'yes' else ('⚠️少量' if v == 'limit' else '❌放生')
                print(f'      {fish}: {icon}')
    
    # === Tide ===
    print(f'\n🌊 潮汐 ({station_name_zh}):')
    if events:
        for e in sorted(events, key=lambda x: x['time']):
            emoji = '🔺' if e['type'] == 'high' else '🔻'
            label = '高潮' if e['type'] == 'high' else '低潮'
            print(f'   {emoji} {e["time"]}  {e["height"]}m  ({label})')
        if tide_range:
            print(f'   潮差: {tide_range["range"]}m  最高:{tide_range["max_high"]}m  最低:{tide_range["min_low"]}m')
    else:
        print('   ⚠️ 無潮汐數據')
    
    # === Tide windows ===
    if windows:
        print(f'\n🎣 最佳潮水時窗:')
        for w in sorted(windows, key=lambda x: x['score'], reverse=True)[:3]:
            score_emoji = '🔥' if w['score'] >= 7 else ('✅' if w['score'] >= 5 else '  ')
            print(f'   {score_emoji} {w["start"]}-{w["end"]} {w["direction"]} 變化:{w["height_change"]}m 評分:{w["score"]}/10')
    
    # === 7-day tide preview ===
    cn_days = ['一', '二', '三', '四', '五', '六', '日']
    print(f'\n📅 未來7日潮汐預覽 ({station_name_zh}):')
    # Collect ranges first to find best 2 days
    day_ranges = []
    for i in range(7):
        d = target_date + timedelta(days=i)
        d_range = get_tide_range(tide, d) if tide else None
        day_ranges.append((i, d, d_range))
    # Find top 2 days by tide range
    valid_days = [(i, rng['range']) for i, _, rng in day_ranges if rng]
    top2 = sorted(valid_days, key=lambda x: x[1], reverse=True)[:2]
    top2_indices = set(idx for idx, _ in top2)
    for i, d, d_range in day_ranges:
        d_windows = find_best_fishing_tides(tide, d) if tide else []
        if not d_range:
            print(f'   {d.month}/{d.day} {cn_days[d.weekday()]}  ⚠️ 無數據')
            continue
        rng = d_range['range']
        # Best window
        if d_windows:
            best_w = sorted(d_windows, key=lambda x: x['score'], reverse=True)[0]
            win_str = f'{best_w["start"]}-{best_w["end"]} {best_w["direction"].split()[0]}'
        else:
            win_str = '無時窗'
        # Emoji: 🔥 for top 2, or based on range
        if i in top2_indices:
            emoji = '🔥'
        elif rng >= 2.3:
            emoji = '🔥'
        elif rng >= 1.8:
            emoji = '✅'
        else:
            emoji = '  '
        annotation = ' ← 大潮！' if rng >= 2.3 else ''
        print(f'   {d.month}/{d.day} {cn_days[d.weekday()]}  潮差{rng}m  {emoji} {win_str}{annotation}')

    # === Moon ===
    print(f'\n🌙 月相: {moon["phase_name"]} 光照:{moon["illumination"]}% 潮水:{moon["tide_type"]}')
    
    # === Solunar ===
    print(f'\n🕐 Solunar 時段:')
    for p in periods:
        emoji = '🔴' if p['type'] == 'major' else '🟡'
        label = 'Major (大活動期)' if p['type'] == 'major' else 'Minor (小活動期)'
        print(f'   {emoji} {p["start"]}-{p["end"]} {p["description"]} [{label}]')
    
    # === Hourly recommendation ===
    print(f'\n⏰ 今日逐時建議:')
    for hour in range(0, 24, 2):
        solunar_s = solunar_activity_score(target_date, hour)
        tide_bonus = 0
        for w in windows:
            w_start = int(w['start'][:2])
            w_end = int(w['end'][:2])
            if w_start <= hour <= w_end or (w_end < w_start and (hour >= w_start or hour <= w_end)):
                tide_bonus = 2
                break
        combined = min(10, solunar_s + tide_bonus)
        bar = '█' * int(combined) + '░' * (10 - int(combined))
        now_marker = ' 👈 你' if hour <= datetime.now().hour < hour + 2 else ''
        go = ' 🎣去!' if combined >= 8 else (' ✅可以' if combined >= 6 else '')
        print(f'   {hour:02d}:00  {bar} {combined}/10{go}{now_marker}')
    
    # === Weather ===
    if weather:
        c = weather['current']
        print(f'\n🌤️ 即時天氣:')
        print(f'   {c["temp_c"]}°C (體感{c["feels_like_c"]}°C) | {c["weather_desc"]}')
        print(f'   氣壓: {c["pressure_hpa"]}hPa | 風: {c["wind_kmph"]}km/h {c["wind_dir"]}')
    
    # Sea state estimate
    from data.weather_data import estimate_sea_state
    if weather and 'current' in weather:
        sea = estimate_sea_state(weather['current'].get('wind_kmph', 0))
        print(f'   🌊 海浪: {sea["state_zh"]} 浪高約{sea["wave"]} {sea["risk"]}')
    
    # === Today's fish ===
    month = str(target_date.month)
    seasonal = get_seasonal_fish(month)
    spot_fish_seasonal = {k: v for k, v in seasonal.items() if k in spot['fish']}
    if spot_fish_seasonal:
        print(f'\n🐟 今日當季魚:')
        for name, info in spot_fish_seasonal.items():
            best_time = "/".join(info['best_time'])
            print(f"   {name} ({info["en"]}) {info["avg_size"]} 最佳:{best_time}")
    
    # === Action advice ===
    print(f'\n💡 出發建議:')
    if windows:
        best_w = sorted(windows, key=lambda x: x['score'], reverse=True)[0]
        print(f'   🕐 最佳出發: {best_w["start"]} 開始 ({best_w["direction"]})')
    if terrain:
        print(f'   📦 魚餌: {terrain.get("best_bait", "活蝦、青蟲")}')
        print(f'   🎣 釣法: {terrain.get("best_method", "磯釣")}')
        hazards = terrain.get('hazards', '')
        if hazards:
            print(f'   ⚠️ 安全: {hazards}')
        if terrain.get('night_fishing'):
            print(f'   🌙 可以夜釣！帶頭燈同充足裝備')
        else:
            print(f'   ☀️ 唔建議夜釣')
    # Overall score
    print(f'   🐟 整體指數: {score}/10', end='')
    if score >= 8:
        print(' 🔥值得去！')
    elif score >= 6:
        print(' ✅可以一試')
    elif score >= 4:
        print(' 😐一般')
    else:
        print(' 👎唔建議')
    
    print('=' * 55)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Hong Kong Fishing Predictor')
    parser.add_argument('spot', nargs='?', default=None, help='Spot name (zh/en/id), e.g. 龍蝦灣, lobster_bay, shek_o')
    parser.add_argument('--fish', default=None, help='Target fish name')
    parser.add_argument('--list', action='store_true', help='List all spots')
    parser.add_argument('--log', action='store_true', help='Show catch history for the spot')
    args = parser.parse_args()
    
    if args.list:
        print('🎣 所有釣點:')
        for s in FISHING_SPOTS:
            station = get_tide_station_for_spot(s['id'].strip())
            st_zh = STATIONS.get(station, {}).get('name_zh', station)
            print(f'   {s["id"]:25s} {s["name_zh"]:10s} ({s["name_en"]:30s}) [{st_zh}]')
        print(f'\n用法: python3 predict.py <釣點名>  或  python3 predict.py --spot <id>')
    elif args.spot:
        spot_id = find_spot(args.spot)
        if spot_id:
            format_spot_guide(spot_id, fish_target=args.fish)
            if args.log:
                from data.catch_log import format_catch_report
                print()
                format_catch_report(spot_id=spot_id)
        else:
            print(f'❌ 找不到釣點: {args.spot}')
            print(f'💡 用 python3 predict.py --list 查看所有釣點')
    else:
        format_fishing_report(fish_target=args.fish)