#!/usr/bin/env python3
"""
Hong Kong Fishing Predictor - Web Interface
Lightweight Flask app for mobile-friendly fishing predictions.
"""

import sys
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, redirect, url_for, request

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data.moon_phase import moon_phase_calc, next_best_fishing_days
from data.fishing_spots import FISHING_SPOTS, get_seasonal_fish
from data.weather_data import get_weather, pressure_score, wind_score, estimate_sea_state, estimate_spot_sea_state
from data.solunar import solunar_periods, solunar_activity_score, daily_solunar_rating
from data.hko_tide_parser import get_tide_for_date, get_tide_range, find_best_fishing_tides, STATIONS, get_tide_station_for_spot
from data.terrain import get_terrain_info
from data.water_quality import WATER_EDIBILITY
from data.catch_log import log_catch, get_catches, get_spot_stats
from predict import (
    get_tide_data, calculate_feeding_score, time_score, tide_score_from_range,
    find_spot, get_all_tide_data
)

app = Flask(__name__)

# Cache weather data for 30 minutes
_weather_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 30 * 60  # 30 minutes in seconds


def get_cached_weather():
    """Get weather data with 30-minute cache."""
    import time
    now = time.time()
    if _weather_cache["data"] is None or (now - _weather_cache["timestamp"]) > CACHE_DURATION:
        _weather_cache["data"] = get_weather()
        _weather_cache["timestamp"] = now
    return _weather_cache["data"]


def get_spot_data(spot_id, target_date=None):
    """Get comprehensive spot data for rendering."""
    if target_date is None:
        target_date = date.today()

    spot = next((s for s in FISHING_SPOTS if s['id'].strip() == spot_id), None)
    if not spot:
        return None

    hour = datetime.now().hour
    station = get_tide_station_for_spot(spot_id)
    station_name_zh = STATIONS.get(station, {}).get('name_zh', station)
    station_name_en = STATIONS.get(station, {}).get('name', station)
    tide = get_tide_data(station)
    events = get_tide_for_date(tide, target_date) if tide else []
    tide_range = get_tide_range(tide, target_date) if tide else None
    windows = find_best_fishing_tides(tide, target_date) if tide else []
    moon = moon_phase_calc(target_date)
    weather = get_cached_weather()
    terrain = get_terrain_info(spot_id)
    wq = WATER_EDIBILITY.get(spot_id, {})
    periods = solunar_periods(target_date)

    score, breakdown = calculate_feeding_score(moon, weather, hour)

    # Hourly scores
    hourly = []
    for h in range(0, 24, 2):
        solunar_s = solunar_activity_score(target_date, h)
        tide_bonus = 0
        for w in windows:
            w_start = int(w['start'][:2])
            w_end = int(w['end'][:2])
            if w_start <= h <= w_end or (w_end < w_start and (h >= w_start or h <= w_end)):
                tide_bonus = 2
                break
        combined = min(10, solunar_s + tide_bonus)
        is_now = h <= datetime.now().hour < h + 2
        hourly.append({
            "hour": h,
            "score": combined,
            "is_now": is_now,
        })

    # 7-day tide preview
    cn_days = ['一', '二', '三', '四', '五', '六', '日']
    week_preview = []
    for i in range(7):
        d = target_date + timedelta(days=i)
        d_range = get_tide_range(tide, d) if tide else None
        d_windows = find_best_fishing_tides(tide, d) if tide else []
        d_moon = moon_phase_calc(d)
        solunar_r = daily_solunar_rating(d)
        best_win = None
        if d_windows:
            best_win = sorted(d_windows, key=lambda x: x['score'], reverse=True)[0]
        week_preview.append({
            "date": d,
            "day_zh": cn_days[d.weekday()],
            "tide_range": d_range,
            "best_window": best_win,
            "moon_phase": d_moon['phase_name'],
            "solunar_rating": solunar_r,
        })

    # Seasonal fish
    month = str(target_date.month)
    seasonal = get_seasonal_fish(month)
    spot_fish_seasonal = {k: v for k, v in seasonal.items() if k in spot['fish']}

    # Spot-specific sea state (considers wind direction + terrain exposure)
    sea_state = None
    if weather and 'current' in weather:
        sea_state = estimate_spot_sea_state(
            weather['current'].get('wind_kmph', 0),
            weather['current'].get('wind_dir', ''),
            spot_id
        )

    return {
        "spot": spot,
        "station": station,
        "station_name_zh": station_name_zh,
        "station_name_en": station_name_en,
        "tide_events": events,
        "tide_range": tide_range,
        "tide_windows": windows,
        "moon": moon,
        "weather": weather,
        "terrain": terrain,
        "water_quality": wq,
        "solunar_periods": periods,
        "score": score,
        "breakdown": breakdown,
        "hourly_scores": hourly,
        "week_preview": week_preview,
        "seasonal_fish": spot_fish_seasonal,
        "target_date": target_date,
        "sea_state": sea_state,
    }


def score_label(score):
    """Get label and emoji for a score."""
    if score >= 8:
        return "🔥🔥🔥 極佳！", "excellent"
    elif score >= 6:
        return "✅ 不錯！", "good"
    elif score >= 4:
        return "😐 一般", "moderate"
    else:
        return "👎 差", "poor"


def get_week_overview():
    """Get 7-day overview for home page."""
    cn_days = ['一', '二', '三', '四', '五', '六', '日']
    today = date.today()
    weather = get_cached_weather()
    days = []
    for i in range(7):
        d = today + timedelta(days=i)
        moon = moon_phase_calc(d)
        solunar_r = daily_solunar_rating(d)
        solunar_score = solunar_r['rating'] if isinstance(solunar_r, dict) else solunar_r
        tide = get_tide_data('CLK_E')
        d_range = get_tide_range(tide, d) if tide else None
        d_windows = find_best_fishing_tides(tide, d) if tide else []
        score, _ = calculate_feeding_score(moon, weather, 9)

        if solunar_score >= 8:
            emoji = '🔥'
        elif solunar_score >= 6:
            emoji = '✅'
        else:
            emoji = '😐'

        days.append({
            "date": d,
            "day_zh": cn_days[d.weekday()],
            "tide_range": d_range,
            "solunar_rating": solunar_score,
            "moon_phase": moon['phase_name'],
            "moon_illumination": moon['illumination'],
            "emoji": emoji,
            "is_today": i == 0,
        })

    # Find best 2 days by solunar rating
    sorted_days = sorted(days, key=lambda x: x['solunar_rating'], reverse=True)
    best_dates = {d['date'] for d in sorted_days[:2]}
    for d in days:
        d['is_best'] = d['date'] in best_dates

    return days


@app.route('/')
def index():
    """Home page with spot selector."""
    # Group spots by district
    districts = {}
    for s in FISHING_SPOTS:
        d = s['district']
        if d not in districts:
            districts[d] = []
        districts[d].append(s)

    # Sort district names
    districts = dict(sorted(districts.items()))

    # Today's overview
    target_date = date.today()
    moon = moon_phase_calc(target_date)
    weather = get_cached_weather()
    hour = datetime.now().hour
    score, breakdown = calculate_feeding_score(moon, weather, hour)
    label, level = score_label(score)

    # 7-day overview
    week_overview = get_week_overview()

    # Recent catches
    recent_catches = get_catches()[:5]
    spot_map = {s['id'].strip(): s['name_zh'] for s in FISHING_SPOTS}

    return render_template('index.html',
        districts=districts,
        moon=moon,
        weather=weather,
        score=score,
        breakdown=breakdown,
        label=label,
        level=level,
        target_date=target_date,
        week_overview=week_overview,
        recent_catches=recent_catches,
        spot_map=spot_map,
        sea_state=estimate_sea_state(weather['current']['wind_kmph']) if weather else None,
    )


@app.route('/spot/<spot_id>')
def spot_page(spot_id):
    """Spot detail page."""
    # Handle Chinese name redirect
    resolved = find_spot(spot_id)
    if resolved and resolved != spot_id:
        return redirect(url_for('spot_page', spot_id=resolved))

    # Parse date parameter
    date_str = request.args.get('date', '')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    data = get_spot_data(spot_id, target_date)
    if not data:
        return render_template('index.html', error=f"找不到釣點: {spot_id}",
            districts={}, moon=None, weather=None, score=0, breakdown=None,
            label="", level="", target_date=date.today(),
            week_overview=[], recent_catches=[], spot_map={})

    label, level = score_label(data['score'])
    data['label'] = label
    data['level'] = level

    # Generate 7-day date list for selector
    cn_days = ['一', '二', '三', '四', '五', '六', '日']
    today = date.today()
    date_list = []
    for i in range(7):
        d = today + timedelta(days=i)
        date_list.append({
            "date": d,
            "day_zh": cn_days[d.weekday()],
            "is_today": i == 0,
            "is_selected": d == target_date,
        })
    data['date_list'] = date_list

    # Catch data for this spot
    spot_catches = get_catches(spot_id=spot_id)[:10]
    spot_stats = get_spot_stats(spot_id)
    data['spot_catches'] = spot_catches
    data['spot_stats'] = spot_stats

    # Build catch form options (Chinese + English)
    month = str(target_date.month)
    seasonal = get_seasonal_fish(month)
    fish_options = [f"{k} ({v['en']})" for k, v in seasonal.items()]
    method_options = ['磯釣 (Rock fishing)', '投釣 (Casting)', '沉底 (Bottom)', '浮波 (Float)']
    bait_options = ['活蝦 (Live shrimp)', '青蟲 (Sandworm)', '魚肉 (Fish meat)', '魚仔 (Small fish)', '蝦肉 (Shrimp meat)']
    tide_options = ['漲潮 (Rising)', '退潮 (Falling)', '高潮 (High)', '低潮 (Low)']
    data['fish_options'] = fish_options
    data['method_options'] = method_options
    data['bait_options'] = bait_options
    data['tide_options'] = tide_options

    return render_template('spot.html', **data)


@app.route('/api/catch', methods=['POST'])
def api_catch():
    """Log a catch via API."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    required = ['spot_id', 'fish', 'count']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        record = log_catch(
            spot_id=data['spot_id'],
            fish=data['fish'],
            count=int(data['count']),
            weight=data.get('weight'),
            method=data.get('method'),
            bait=data.get('bait'),
            tide_state=data.get('tide_state'),
            notes=data.get('notes'),
            rig=data.get('rig'),
            catch_date=data.get('date'),
        )
        return jsonify({"success": True, "record": record})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/catch/delete', methods=['POST'])
def api_catch_delete():
    """Delete catch records via API."""
    from data.catch_log import delete_catch, delete_catches_by_spot, delete_all_catches
    data = request.get_json(silent=True) or {}

    if data.get('all'):
        deleted = delete_all_catches()
        return jsonify({"success": True, "deleted": deleted})
    elif data.get('spot_id'):
        deleted = delete_catches_by_spot(data['spot_id'])
        return jsonify({"success": True, "deleted": deleted})
    elif data.get('catch_id'):
        ok = delete_catch(data['catch_id'])
        if ok:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Record not found"}), 404
    else:
        return jsonify({"error": "Specify catch_id, spot_id, or all"}), 400


@app.route('/api/catch/update', methods=['POST'])
def api_catch_update():
    """Update a catch record via API."""
    from data.catch_log import update_catch
    data = request.get_json(silent=True)
    if not data or not data.get('catch_id'):
        return jsonify({"error": "Missing catch_id"}), 400
    result = update_catch(
        catch_id=data['catch_id'],
        fish=data.get('fish'),
        count=data.get('count'),
        weight=data.get('weight'),
        method=data.get('method'),
        bait=data.get('bait'),
        tide_state=data.get('tide_state'),
        time=data.get('time'),
        notes=data.get('notes'),
        catch_date=data.get('date'),
    )
    if result:
        return jsonify({"success": True, "record": result})
    else:
        return jsonify({"error": "Record not found"}), 404


@app.route('/api/spots')
def api_spots():
    """JSON API listing all spots."""
    spots = []
    for s in FISHING_SPOTS:
        station = get_tide_station_for_spot(s['id'].strip())
        spots.append({
            "id": s['id'].strip(),
            "name_zh": s['name_zh'],
            "name_en": s['name_en'],
            "district": s['district'],
            "type": s['type'],
            "difficulty": s['difficulty'],
            "rating": s['rating'],
            "fish": s['fish'],
            "lat": s['lat'],
            "lng": s['lng'],
            "station": station,
        })
    return jsonify({"spots": spots, "count": len(spots)})


@app.route('/api/spot/<spot_id>')
def api_spot(spot_id):
    """JSON API for spot data."""
    resolved = find_spot(spot_id)
    if resolved:
        spot_id = resolved

    data = get_spot_data(spot_id)
    if not data:
        return jsonify({"error": f"找不到釣點: {spot_id}"}), 404

    # Convert date objects for JSON
    result = {
        "spot": data['spot'],
        "station": data['station'],
        "station_name_zh": data['station_name_zh'],
        "tide_events": data['tide_events'],
        "tide_range": data['tide_range'],
        "tide_windows": data['tide_windows'],
        "moon": data['moon'],
        "weather": data['weather'],
        "sea_state": data.get('sea_state', None),
        "terrain": data['terrain'],
        "water_quality": data['water_quality'],
        "solunar_periods": data['solunar_periods'],
        "score": data['score'],
        "breakdown": data['breakdown'],
        "hourly_scores": data['hourly_scores'],
        "seasonal_fish": data['seasonal_fish'],
        "target_date": data['target_date'].isoformat(),
    }
    return jsonify(result)


@app.route('/api/forecast/<spot_id>')
def api_forecast(spot_id):
    """JSON API with full forecast including hourly scores."""
    resolved = find_spot(spot_id)
    if resolved:
        spot_id = resolved

    data = get_spot_data(spot_id)
    if not data:
        return jsonify({"error": f"找不到釣點: {spot_id}"}), 404

    forecast = []
    for h in range(24):
        solunar_s = solunar_activity_score(data['target_date'], h)
        score, breakdown = calculate_feeding_score(data['moon'], data['weather'], h)
        tide_bonus = 0
        for w in data['tide_windows']:
            w_start = int(w['start'][:2])
            w_end = int(w['end'][:2])
            if w_start <= h <= w_end or (w_end < w_start and (h >= w_start or h <= w_end)):
                tide_bonus = 2
                break
        forecast.append({
            "hour": h,
            "feeding_score": score,
            "solunar_score": solunar_s,
            "combined_score": min(10, solunar_s + tide_bonus),
            "breakdown": breakdown,
        })

    return jsonify({
        "spot_id": spot_id,
        "spot_name_zh": data['spot']['name_zh'],
        "spot_name_en": data['spot']['name_en'],
        "date": data['target_date'].isoformat(),
        "overall_score": data['score'],
        "moon": data['moon'],
        "tide_events": data['tide_events'],
        "tide_range": data['tide_range'],
        "tide_windows": data['tide_windows'],
        "solunar_periods": data['solunar_periods'],
        "weather": data['weather'],
        "hourly_forecast": forecast,
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)