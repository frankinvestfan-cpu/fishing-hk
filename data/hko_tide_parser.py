#!/usr/bin/env python3
"""
HKO Tide Data Parser v2
Parses official HKO Tide Table PDF with robust handling of split lines.
"""

import fitz
import json
import re
from datetime import date
from pathlib import Path

# 10 HKO tide stations (6 available in current 82-page PDF; 4 need full 130+ page PDF)
STATIONS = {
    "CLK_E": {"name": "Chek Lap Kok (East)", "name_zh": "赤鱲角(東)", "pages": (11, 22)},
    "CC":     {"name": "Cheung Chau", "name_zh": "長洲", "pages": (23, 34)},
    "KLW":    {"name": "Ko Lau Wan", "name_zh": "高流灣", "pages": (35, 46)},
    "KC":      {"name": "Kwai Chung", "name_zh": "葵涌", "pages": (47, 58)},
    "MW":      {"name": "Ma Wan", "name_zh": "馬灣", "pages": (59, 70)},
    "QB":      {"name": "Quarry Bay", "name_zh": "鰂魚涌", "pages": (71, 82)},
    # Below 4 stations need the full HKO PDF (130+ pages); placeholders for now
    "SP":      {"name": "Sha Po", "name_zh": "沙婆", "pages": (0, 0)},
    "TMW":     {"name": "Tai Miu Wan", "name_zh": "大廟灣", "pages": (0, 0)},
    "TBT":     {"name": "Tsim Bei Tsui", "name_zh": "尖鼻嘴", "pages": (0, 0)},
    "TP":      {"name": "Tai Po", "name_zh": "大埔", "pages": (0, 0)},
}

# Note: The 2026 PDF at /tmp has only 82 pages (6 stations: CLK_E, CC, KLW, KC, MW, QB)
# Full PDF with all 10+ stations would need re-download from HKO

MONTH_MAP = {
    11: 1, 12: 2, 13: 3, 14: 4, 15: 5, 16: 6,
    17: 7, 18: 8, 19: 9, 20: 10, 21: 11, 22: 12,
}

def parse_station(pdf_path, station="QB"):
    """Parse tide data for a station from HKO PDF."""
    doc = fitz.open(pdf_path)
    info = STATIONS[station]
    start_pg, end_pg = info["pages"]
    
    # Check for placeholder pages (station not available in current PDF)
    if start_pg == 0 and end_pg == 0:
        print(f"⚠️  Station {station} ({info['name_zh']}) not available in current PDF. Need full HKO tide table.")
        doc.close()
        return {}
    
    # Adjust: pages are 0-indexed in PyMuPDF
    start_pg -= 1
    end_pg -= 1
    
    all_tides = {}
    current_month = None
    current_day = None
    
    for page_idx in range(start_pg, min(end_pg + 1, doc.page_count)):
        text = doc[page_idx].get_text()
        lines = text.strip().split('\n')
        
        # Determine month from page position within station
        # First page of station = January, etc.
        page_offset = page_idx - start_pg
        estimated_month = page_offset + 1  # 1-12
        
        # Clean and process lines
        clean_lines = []
        for line in lines:
            cleaned = line.replace('\xa0', ' ').replace('\u2009', ' ').strip()
            if cleaned:
                clean_lines.append(cleaned)
        
        i = 0
        while i < len(clean_lines):
            line = clean_lines[i]
            
            # Skip header lines
            if line.startswith('星期') or line.startswith('TIME') or line.startswith('時間') or line.startswith('M'):
                i += 1
                continue
            
            # Match day number (standalone)
            day_match = re.match(r'^(\d{1,2})$', line)
            if day_match:
                current_day = int(day_match.group(1))
                if current_day == 1:
                    current_month = estimated_month
                i += 1
                continue
            
            # Match day+time combo like "10 1518  2.0"
            day_time_match = re.match(r'^(\d{1,2})\s+(\d{4})\s+([\d.]+)$', line)
            if day_time_match:
                current_day = int(day_time_match.group(1))
                if current_day == 1:
                    current_month = estimated_month
                time_str = day_time_match.group(2)
                height = float(day_time_match.group(3))
                _add_tide_event(all_tides, current_month, current_day, time_str, height, station)
                i += 1
                continue
            
            # Match time+height on same line: "0325  0.9" or "0921  2.3"
            time_match = re.match(r'^(\d{4})\s+([\d.]+)$', line)
            if time_match and current_day and current_month:
                time_str = time_match.group(1)
                height = float(time_match.group(2))
                _add_tide_event(all_tides, current_month, current_day, time_str, height, station)
                i += 1
                continue
            
            # Match time only (height on next line): "0009" then "1.5"
            time_only = re.match(r'^(\d{4})$', line)
            if time_only and current_day and current_month:
                time_str = time_only.group(1)
                # Check next line for height
                if i + 1 < len(clean_lines):
                    next_line = clean_lines[i + 1]
                    height_match = re.match(r'^([\d.]+)$', next_line)
                    if height_match:
                        height = float(height_match.group(1))
                        _add_tide_event(all_tides, current_month, current_day, time_str, height, station)
                        i += 2
                        continue
                i += 1
                continue
            
            i += 1
    
    doc.close()
    
    # Fix high/low classification
    _classify_tides(all_tides)
    
    return all_tides


def _add_tide_event(all_tides, month, day, time_str, height, station):
    """Add a tide event to the data structure."""
    if not month or not day:
        return
    
    year = 2026
    date_key = f"{year}-{month:02d}-{day:02d}"
    
    if date_key not in all_tides:
        all_tides[date_key] = []
    
    hour = int(time_str[:2])
    minute = int(time_str[2:])
    
    all_tides[date_key].append({
        "date": date_key,
        "time": f"{hour:02d}:{minute:02d}",
        "height": height,
        "type": "unknown",  # Will be classified later
        "station": station,
    })


def _classify_tides(all_tides):
    """Fix high/low tide classification based on height patterns."""
    for date_key in sorted(all_tides.keys()):
        events = all_tides[date_key]
        if len(events) < 2:
            continue
        
        # Sort by time
        events.sort(key=lambda x: x["time"])
        
        # Remove duplicates (events within 30 min with similar height)
        cleaned = [events[0]]
        for e in events[1:]:
            prev = cleaned[-1]
            prev_mins = int(prev["time"][:2]) * 60 + int(prev["time"][3:])
            curr_mins = int(e["time"][:2]) * 60 + int(e["time"][3:])
            time_diff = abs(curr_mins - prev_mins)
            height_diff = abs(e["height"] - prev["height"])
            
            # Skip if too close in time AND similar height (likely duplicate)
            if time_diff < 30 and height_diff < 0.3:
                # Keep the more extreme one
                continue
            cleaned.append(e)
        
        all_tides[date_key] = cleaned
        events = cleaned
        
        # Classify: heights should alternate high/low
        # Start by finding if first is high or low
        if len(events) >= 3:
            # Use overall pattern: find local maxima = high, local minima = low
            for i in range(len(events)):
                if i == 0:
                    events[i]["type"] = "high" if events[i]["height"] > events[i+1]["height"] else "low"
                elif i == len(events) - 1:
                    events[i]["type"] = "high" if events[i]["height"] > events[i-1]["height"] else "low"
                else:
                    if events[i]["height"] > events[i-1]["height"] and events[i]["height"] > events[i+1]["height"]:
                        events[i]["type"] = "high"
                    elif events[i]["height"] < events[i-1]["height"] and events[i]["height"] < events[i+1]["height"]:
                        events[i]["type"] = "low"
                    elif events[i]["height"] > events[i-1]["height"]:
                        events[i]["type"] = "high"
                    else:
                        events[i]["type"] = "low"
            
            # Verify alternation and fix
            for i in range(1, len(events)):
                if events[i]["type"] == events[i-1]["type"]:
                    # Two same types in a row - flip the one with less extreme height
                    if events[i]["type"] == "high":
                        # One should be low
                        if events[i]["height"] < events[i-1]["height"]:
                            events[i]["type"] = "low"
                        else:
                            events[i-1]["type"] = "low"
                    else:
                        # One should be high
                        if events[i]["height"] > events[i-1]["height"]:
                            events[i]["type"] = "high"
                        else:
                            events[i-1]["type"] = "high"
        elif len(events) == 2:
            if events[0]["height"] > events[1]["height"]:
                events[0]["type"] = "high"
                events[1]["type"] = "low"
            else:
                events[0]["type"] = "low"
                events[1]["type"] = "high"


def get_tide_for_date(tide_data, target_date):
    """Get tide events for a specific date."""
    date_key = target_date.strftime("%Y-%m-%d")
    return tide_data.get(date_key, [])


# Spot-to-station mapping (nearest station)
SPOT_TIDE_STATION = {
    # HK Island → QB / TMW
    "aberdeen": "QB", "causeway_bay": "QB", "shek_o": "TMW", "big_wave_bay": "TMW",
    # Kowloon
    "lei_yue_mun": "TMW", "cha_kwo_ling": "QB", "sam_dip_wong": "KC",
    # Sai Kung → KLW (Ko Lau Wan is in Mirs Bay, same waters as Sai Kung)
    "sai_kung_town": "KLW", "sai_kung_pier": "KLW", "tui_min_chau": "KLW",
    "sharp_island": "KLW", "pak_sha_chau": "KLW", "sham_chuk_tsuen": "KLW",
    "clear_water_bay": "KLW", "clear_water_bay_1": "KLW", "lobster_bay": "KLW",
    "palm_beach": "KLW", "tai_a_chau": "KLW", "po_toi_au": "CC",
    "tin_hau_temple_bay": "KLW", "tai_chong_ting": "KLW", "high_island": "KLW",
    # NT East → TP (Tai Po station for Tolo Harbour area) / KLW
    "tolo_harbour": "TP", "tai_mei_tuk": "TP", "three_fathoms_cove": "TP",
    "ma_on_shan_waterfront": "TP", "wu_kai_sha": "TP", "wu_kai_sha_pier": "TP",
    "pak_shek_kok": "TP", "tolo_harbour_front": "TP", "fo_tan": "TP",
    "shing_mun_river": "TP", "ma_on_shan_rocky": "TP",
    # NT West → MW / TBT
    "sham_tseng": "MW", "castle_peak_bay": "MW", "ting_kau": "MW",
    "anglers_beach": "MW", "lido_beach": "MW", "tsuen_wan_waterfront": "KC",
    "ma_wan": "MW", "tsing_yi_waterfront": "KC", "tuen_mun_waterfront": "MW",
    "sam_shing": "MW", "lau_fau_shan": "TBT", "lau_fau_shan_rocky": "TBT",
    "pak_kong": "MW", "ha_tsuen": "TBT", "tsim_be_tsui_west": "TBT", "lung_kwu_tan": "MW",
    # Islands
    "cheung_chau": "CC", "lamma_island": "CC", "lantau_tung_chung": "CLK_E",
    "ping_chau": "KLW", "crooked_island": "KLW",
    "tai_long_wan_west": "KLW", "long_ke": "KLW", "leung_shuen_wan": "KLW",
    "ham_tin_wan": "KLW", "chek_keng": "KLW",
    "pui_o": "CC",
    # Central
    "victoria_harbour": "QB",
}


def get_tide_station_for_spot(spot_id):
    """Get the nearest tide station for a fishing spot."""
    return SPOT_TIDE_STATION.get(spot_id.strip(), "QB")  # Default to QB



def get_tide_range(tide_data, target_date):
    """Calculate tide range for a date."""
    events = get_tide_for_date(tide_data, target_date)
    if not events:
        return None
    
    highs = [e for e in events if e["type"] == "high"]
    lows = [e for e in events if e["type"] == "low"]
    
    if not highs or not lows:
        return None
    
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "max_high": max(h["height"] for h in highs),
        "min_low": min(l["height"] for l in lows),
        "range": round(max(h["height"] for h in highs) - min(l["height"] for l in lows), 2),
        "high_times": [h["time"] for h in highs],
        "low_times": [l["time"] for l in lows],
    }


def find_best_fishing_tides(tide_data, target_date):
    """
    Find best fishing times based on tide movement.
    Best fishing: during tide change (rising or falling most rapidly).
    """
    events = get_tide_for_date(tide_data, target_date)
    if len(events) < 2:
        return []
    
    events.sort(key=lambda x: x["time"])
    
    fishing_windows = []
    for i in range(len(events) - 1):
        current = events[i]
        next_event = events[i + 1]
        
        # Time between events
        curr_h, curr_m = int(current["time"].split(":")[0]), int(current["time"].split(":")[1])
        next_h, next_m = int(next_event["time"].split(":")[0]), int(next_event["time"].split(":")[1])
        
        duration_hours = (next_h * 60 + next_m - curr_h * 60 - curr_m) / 60
        if duration_hours < 0:
            duration_hours += 24
        
        height_diff = abs(next_event["height"] - current["height"])
        
        # Tide is moving fastest in the middle of the transition
        mid_h = (curr_h + next_h) // 2 if next_h >= curr_h else ((curr_h + next_h + 24) // 2) % 24
        mid_m = (curr_m + next_m) // 2
        
        if current["type"] == "low" and next_event["type"] == "high":
            tide_dir = "漲潮 (Rising)"
            score = min(10, int(height_diff * 5))  # More change = more fish
        elif current["type"] == "high" and next_event["type"] == "low":
            tide_dir = "退潮 (Falling)"
            score = min(10, int(height_diff * 4))  # Rising slightly better
        else:
            tide_dir = "過渡"
            score = 5
        
        fishing_windows.append({
            "start": current["time"],
            "end": next_event["time"],
            "mid": f"{mid_h:02d}:{mid_m:02d}",
            "direction": tide_dir,
            "height_change": round(height_diff, 2),
            "duration_hours": round(duration_hours, 1),
            "score": score,
            "from_type": current["type"],
            "to_type": next_event["type"],
        })
    
    return fishing_windows


if __name__ == "__main__":
    import sys
    
    # Find PDF: bundled first, then /tmp
    pdf_path = os.path.join(os.path.dirname(__file__), 'TideTable2026.pdf')
    if not os.path.exists(pdf_path):
        pdf_path = '/tmp/TideTable2026.pdf'
    station = sys.argv[1] if len(sys.argv) > 1 else "QB"
    
    print(f"Parsing HKO Tide Table 2026 - Station: {STATIONS[station]['name']}")
    
    tide_data = parse_station(pdf_path, station)
    
    total_days = len(tide_data)
    total_events = sum(len(v) for v in tide_data.values())
    print(f"Result: {total_days} days, {total_events} tide events")
    
    # Show today
    today = date.today()
    events = get_tide_for_date(tide_data, today)
    if events:
        print(f"\n📊 {today.strftime('%Y-%m-%d')} 潮汐預報 ({STATIONS[station]['name']}):")
        for e in sorted(events, key=lambda x: x["time"]):
            emoji = "🔺" if e["type"] == "high" else "🔻"
            print(f"   {emoji} {e['time']}  {e['height']}m  ({'高潮' if e['type']=='high' else '低潮'})")
        
        # Tide range
        r = get_tide_range(tide_data, today)
        if r:
            print(f"\n   潮差: {r['range']}m  最高:{r['max_high']}m  最低:{r['min_low']}m")
        
        # Fishing windows
        windows = find_best_fishing_tides(tide_data, today)
        print(f"\n🎣 釣魚潮水時窗:")
        for w in windows:
            print(f"   {w['start']}-{w['end']} {w['direction']} 變化:{w['height_change']}m 評分:{w['score']}/10")
    
    # Save
    output = f"data/hko_tides_{station}_2026.json"
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(tide_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved to {output}")