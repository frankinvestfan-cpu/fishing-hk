#!/usr/bin/env python3
"""
Solunar Theory Implementation for Hong Kong Fishing
Based on the same theory used by tides4fishing.com

Solunar theory (John Alden Knight, 1926):
- Fish are most active during "major periods" when moon is overhead or underfoot
- Fish are moderately active during "minor periods" at moonrise/moonset
- Activity is enhanced during new/full moon (spring tides)
- Best fishing = major period + good tide + favorable weather

Reference: https://tides4fishing.com uses this same theory
"""

import math
from datetime import datetime, date, timedelta

# Moon overhead/underfoot calculation
# Moon transit times can be approximated from moonrise/moonset

def calculate_moon_transit(date_obj, lng=114.17):
    """
    Approximate moon transit (overhead) and anti-transit (underfoot) times.
    Based on the moon's position relative to the observer's meridian.
    
    For Hong Kong: lng=114.17°E, lat=22.28°N
    """
    # Calculate approximate moon transit using synodic period
    # Reference new moon: 2024-01-11
    known_new_moon = date(2024, 1, 11)
    days_since_new = (date_obj - known_new_moon).days
    
    SYNODIC_MONTH = 29.53058867
    
    # Moon's approximate position in orbit
    cycle_pos = (days_since_new % SYNODIC_MONTH) / SYNODIC_MONTH
    
    # Approximate moon transit time (upper culmination)
    # Moon transits ~50 minutes later each day
    # At new moon, transit ≈ noon (12:00)
    base_transit = 12.0 + cycle_pos * 24.0  # hours
    
    # Adjust for longitude (simplified)
    # Hong Kong is ~7.6 hours ahead of UTC
    transit_utc = base_transit - lng / 15.0
    transit_hkt = transit_utc + 8.0  # UTC+8
    
    # Normalize to 0-24
    transit_hkt = transit_hkt % 24
    
    # Anti-transit (underfoot) is ~12 hours later
    anti_transit_hkt = (transit_hkt + 12.4) % 24
    
    # Moonrise/moonset (approximate)
    moonrise = (transit_hkt - 6.2) % 24
    moonset = (transit_hkt + 6.2) % 24
    
    return {
        "overhead": transit_hkt,      # Major period
        "underfoot": anti_transit_hkt,  # Major period
        "moonrise": moonrise,           # Minor period
        "moonset": moonset,             # Minor period
    }

def solunar_periods(date_obj):
    """
    Calculate solunar major and minor periods for a given date.
    
    Major periods: moon overhead + moon underfoot (±1 hour)
    Minor periods: moonrise + moonset (±30 min)
    
    Each major period lasts ~2 hours, minor ~1 hour.
    """
    transits = calculate_moon_transit(date_obj)
    
    periods = []
    
    # Major period 1: Moon overhead (±1 hour)
    h = int(transits["overhead"])
    m = int((transits["overhead"] - h) * 60)
    periods.append({
        "type": "major",
        "start": f"{(h-1)%24:02d}:{m:02d}",
        "peak": f"{h:02d}:{m:02d}",
        "end": f"{(h+1)%24:02d}:{m:02d}",
        "description": "月球正上方 (Moon Overhead)",
        "duration_hours": 2,
    })
    
    # Major period 2: Moon underfoot (±1 hour)
    h2 = int(transits["underfoot"])
    m2 = int((transits["underfoot"] - h2) * 60)
    periods.append({
        "type": "major",
        "start": f"{(h2-1)%24:02d}:{m2:02d}",
        "peak": f"{h2:02d}:{m2:02d}",
        "end": f"{(h2+1)%24:02d}:{m2:02d}",
        "description": "月球正下方 (Moon Underfoot)",
        "duration_hours": 2,
    })
    
    # Minor period 1: Moonrise (±30 min)
    h3 = int(transits["moonrise"])
    m3 = int((transits["moonrise"] - h3) * 60)
    periods.append({
        "type": "minor",
        "start": f"{h3:02d}:{max(0,m3-30):02d}",
        "peak": f"{h3:02d}:{m3:02d}",
        "end": f"{h3:02d}:{min(59,m3+30):02d}",
        "description": "月出 (Moonrise)",
        "duration_hours": 1,
    })
    
    # Minor period 2: Moonset (±30 min)
    h4 = int(transits["moonset"])
    m4 = int((transits["moonset"] - h4) * 60)
    periods.append({
        "type": "minor",
        "start": f"{h4:02d}:{max(0,m4-30):02d}",
        "peak": f"{h4:02d}:{m4:02d}",
        "end": f"{h4:02d}:{min(59,m4+30):02d}",
        "description": "月落 (Moonset)",
        "duration_hours": 1,
    })
    
    # Sort by peak time
    periods.sort(key=lambda x: x["peak"])
    return periods

def solunar_activity_score(date_obj, hour=None):
    """
    Calculate solunar activity score (1-10) for a specific hour.
    
    Based on tides4fishing methodology:
    - Major period = peak activity (8-10)
    - Minor period = moderate activity (5-7)
    - Near major/minor = slightly elevated (4-6)
    - Otherwise = low activity (2-4)
    """
    if hour is None:
        hour = datetime.now().hour
    
    periods = solunar_periods(date_obj)
    
    for period in periods:
        peak_hour = int(period["peak"].split(":")[0])
        peak_min = int(period["peak"].split(":")[1])
        peak_decimal = peak_hour + peak_min / 60
        
        if period["type"] == "major":
            # Major period: ±1 hour from peak = 8-10
            if abs(hour + 0 - peak_decimal) < 0.5:
                return 10  # Right at peak
            elif abs(hour + 0 - peak_decimal) < 1.0:
                return 8   # Within major period
            elif abs(hour + 0 - peak_decimal) < 1.5:
                return 6   # Near major period
        
        elif period["type"] == "minor":
            # Minor period: ±0.5 hour from peak = 5-7
            if abs(hour + 0 - peak_decimal) < 0.3:
                return 7   # At peak
            elif abs(hour + 0 - peak_decimal) < 0.6:
                return 5   # Within minor period
    
    # Check if near dawn/dusk (universal fishing truth)
    if 5 <= hour <= 7 or 17 <= hour <= 19:
        return 4  # Dawn/dusk bonus
    elif 11 <= hour <= 14:
        return 2  # Midday low
    
    return 3  # Default low activity

def daily_solunar_rating(date_obj):
    """
    Calculate overall daily solunar rating (1-10).
    Based on moon phase and tidal coefficient.
    
    tides4fishing uses:
    - Tidal coefficient (based on moon-sun alignment)
    - Average of today's activity scores
    """
    from data.moon_phase import moon_phase_calc
    
    moon = moon_phase_calc(date_obj)
    
    # Tidal coefficient (similar to tides4fishing)
    # Spring tide (new/full moon) = coefficient 90-120
    # Neap tide (quarter moon) = coefficient 20-45
    # Normal = coefficient 45-90
    
    illumination = moon["illumination"]
    cycle_pos = moon["cycle_position"]
    
    # Approximate tidal coefficient
    # At new/full moon, coefficient is highest
    # coefficient ∝ |cos(2π * cycle_pos)| near 0 or 0.5
    if cycle_pos < 0.06 or cycle_pos > 0.94 or 0.44 < cycle_pos < 0.56:
        coefficient = 90 + (10 - abs(cycle_pos - 0.5) * 20) * 3  # 90-120
        coefficient = min(120, coefficient)
    elif 0.19 < cycle_pos < 0.31 or 0.69 < cycle_pos < 0.81:
        coefficient = 30 + abs(cycle_pos - 0.25) * 100  # 30-45
        coefficient = max(20, min(45, coefficient))
    else:
        coefficient = 50 + abs(illumination - 50) * 0.5  # 50-75
    
    # Daily rating based on coefficient
    if coefficient >= 100:
        rating = 10
        label = "🔥🔥🔥 極佳"
    elif coefficient >= 85:
        rating = 8
        label = "🔥🔥 很好"
    elif coefficient >= 70:
        rating = 7
        label = "✅ 好"
    elif coefficient >= 55:
        rating = 6
        label = "✅ 不錯"
    elif coefficient >= 45:
        rating = 5
        label = "😐 一般"
    elif coefficient >= 35:
        rating = 3
        label = "👎 較差"
    else:
        rating = 2
        label = "👎 差"
    
    return {
        "date": date_obj.isoformat(),
        "moon_phase": moon["phase_name"],
        "illumination": moon["illumination"],
        "tidal_coefficient": round(coefficient, 1),
        "rating": rating,
        "label": label,
        "tide_type": moon["tide_type"],
    }

if __name__ == "__main__":
    today = date.today()
    
    print(f"🎣 Solunar 預測 — {today.strftime('%Y-%m-%d')}")
    print(f"   (基於太陰太陽論，同 tides4fishing.com 相同理論)\n")
    
    # Daily rating
    rating = daily_solunar_rating(today)
    print(f"📊 今日評分: {rating['rating']}/10 {rating['label']}")
    print(f"   潮汐係數: {rating['tidal_coefficient']}")
    print(f"   月相: {rating['moon_phase']} 光照:{rating['illumination']}%")
    print(f"   潮汐類型: {rating['tide_type']}")
    
    # Solunar periods
    print(f"\n🕐 Solunar 時段:")
    periods = solunar_periods(today)
    for p in periods:
        emoji = "🔴" if p["type"] == "major" else "🟡"
        print(f"   {emoji} {p['peak']} {p['description']} ({p['type']}) {p['start']}-{p['end']}")
    
    # Hourly activity
    print(f"\n⏰ 逐時活動預測:")
    for hour in range(0, 24, 2):
        score = solunar_activity_score(today, hour)
        bar = "█" * score + "░" * (10 - score)
        print(f"   {hour:02d}:00  {bar} {score}/10")
    
    # Next 7 days
    print(f"\n📅 未來7日預測:")
    for i in range(7):
        d = today + timedelta(days=i)
        r = daily_solunar_rating(d)
        print(f"   {d.isoformat()} {r['moon_phase']} 係數:{r['tidal_coefficient']} {r['label']}")