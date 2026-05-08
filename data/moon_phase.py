#!/usr/bin/env python3
"""
Moon Phase Calculator
Calculates moon phase for any date using astronomical formulas.
"""

import math
from datetime import datetime, date, timedelta

def moon_phase_calc(target_date=None):
    """
    Calculate moon phase using synodic month formula.
    Returns phase name, illumination %, and days since new moon.
    """
    if target_date is None:
        target_date = date.today()
    
    # Known new moon reference: 2024-01-11 11:57 UTC
    known_new_moon = date(2024, 1, 11)
    
    # Synodic month length
    SYNODIC_MONTH = 29.53058867
    
    # Calculate days since known new moon
    days_since = (target_date - known_new_moon).days
    
    # Current position in cycle (0-1)
    cycle_pos = (days_since % SYNODIC_MONTH) / SYNODIC_MONTH
    
    # Days since new moon
    days_since_new = days_since % SYNODIC_MONTH
    
    # Illumination (approximation using cosine)
    illumination = (1 - math.cos(2 * math.pi * cycle_pos)) / 2 * 100
    
    # Phase name
    if cycle_pos < 0.03 or cycle_pos > 0.97:
        phase_name = "新月 🌑"
        phase_en = "New Moon"
    elif cycle_pos < 0.22:
        phase_name = "蛾眉月 🌒"
        phase_en = "Waxing Crescent"
    elif cycle_pos < 0.28:
        phase_name = "上弦月 🌓"
        phase_en = "First Quarter"
    elif cycle_pos < 0.47:
        phase_name = "盈凸月 🌔"
        phase_en = "Waxing Gibbous"
    elif cycle_pos < 0.53:
        phase_name = "滿月 🌕"
        phase_en = "Full Moon"
    elif cycle_pos < 0.72:
        phase_name = "虧凸月 🌖"
        phase_en = "Waning Gibbous"
    elif cycle_pos < 0.78:
        phase_name = "下弦月 🌗"
        phase_en = "Last Quarter"
    else:
        phase_name = "殘月 🌘"
        phase_en = "Waning Crescent"
    
    # Tide quality: new/full moon = spring tide (大潮), quarter = neap tide (小潮)
    if cycle_pos < 0.06 or cycle_pos > 0.94 or 0.44 < cycle_pos < 0.56:
        tide_type = "大潮 (Spring Tide)"
        tide_score = 10
    elif 0.19 < cycle_pos < 0.31 or 0.69 < cycle_pos < 0.81:
        tide_type = "小潮 (Neap Tide)"
        tide_score = 4
    else:
        tide_type = "中潮 (Normal Tide)"
        tide_score = 7
    
    return {
        "date": target_date.isoformat(),
        "phase_name": phase_name,
        "phase_en": phase_en,
        "illumination": round(illumination, 1),
        "days_since_new": round(days_since_new, 1),
        "tide_type": tide_type,
        "tide_score": tide_score,  # 1-10
        "cycle_position": round(cycle_pos, 3),
    }

def next_best_fishing_days(days_ahead=14):
    """Find the best fishing days in the next N days based on moon phase."""
    today = date.today()
    results = []
    
    for i in range(days_ahead):
        d = today + timedelta(days=i)
        moon = moon_phase_calc(d)
        results.append({
            "date": d.isoformat(),
            "phase": moon["phase_name"],
            "illumination": moon["illumination"],
            "tide_type": moon["tide_type"],
            "tide_score": moon["tide_score"],
        })
    
    # Sort by tide_score descending
    results.sort(key=lambda x: x["tide_score"], reverse=True)
    return results

if __name__ == "__main__":
    from datetime import timedelta
    
    today = date.today()
    moon = moon_phase_calc(today)
    
    print(f"🌙 今日月相: {today.isoformat()}")
    print(f"   {moon['phase_name']} ({moon['phase_en']})")
    print(f"   光照: {moon['illumination']}%")
    print(f"   新月後: {moon['days_since_new']}日")
    print(f"   潮汐類型: {moon['tide_type']}")
    print(f"   釣魚潮水分: {moon['tide_score']}/10")
    
    print(f"\n📅 未來14日最佳釣魚日:")
    best = next_best_fishing_days(14)
    for b in best[:7]:
        print(f"   {b['date']} {b['phase']} {b['tide_type']} 分數:{b['tide_score']}/10")