#!/usr/bin/env python3
"""
Hong Kong Tidal Data Fetcher
Scrapes tide predictions from Hong Kong Observatory (HKO)
"""

import requests
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# HKO tidal stations
TIDAL_STATIONS = {
    "QB": "Quarry Bay (鰂魚涌)",
    "TP": "Tai Po (大埔)",
    "TBT": "Tsim Bei Tsui (尖鼻嘴)",
    "WL": "Waglan Island (橫瀾島)",
    "CCH": "Chi Ma Wan (芝麻灣)",
    "LPC": "Lo Tik Park (老鴉洲)",
    "NMW": "North Point (北角)",
}

# HKO tidal prediction URL
HKO_TIDE_URL = "https://www.hko.gov.hk/tide/{}{}{}_tide.csv"

def fetch_tide_data(station="QB", year=None, month=None):
    """
    Fetch tide data from HKO for a given station, year and month.
    Returns list of tide events with datetime, height (m), and type.
    """
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    url = HKO_TIDE_URL.format(station, year, f"{month:02d}")
    
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching tide data: {e}")
        return []
    
    return parse_hko_csv(resp.text, station)

def parse_hko_csv(text, station):
    """
    Parse HKO tide CSV format.
    Format: Date, Time, Height(m), Type (H=High, L=Low)
    """
    tides = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('Date'):
            continue
        parts = line.split(',')
        if len(parts) < 4:
            continue
        try:
            date_str = parts[0].strip()
            time_str = parts[1].strip()
            height = float(parts[2].strip())
            tide_type = parts[3].strip()  # H or L
            
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            tides.append({
                "datetime": dt.isoformat(),
                "height": height,
                "type": "high" if tide_type == "H" else "low",
                "station": station,
                "station_name": TIDAL_STATIONS.get(station, station)
            })
        except (ValueError, IndexError):
            continue
    
    return tides

def get_tide_events(date, station="QB"):
    """Get tide events for a specific date."""
    year = date.year
    month = date.month
    all_tides = fetch_tide_data(station, year, month)
    
    date_str = date.strftime("%Y-%m-%d")
    return [t for t in all_tides if t["datetime"].startswith(date_str)]

def get_tide_range(date, station="QB"):
    """Calculate tide range (difference between high and low) for a date."""
    events = get_tide_events(date, station)
    highs = [e for e in events if e["type"] == "high"]
    lows = [e for e in events if e["type"] == "low"]
    
    if not highs or not lows:
        return None
    
    max_high = max(h["height"] for h in highs)
    min_low = min(l["height"] for l in lows)
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "station": station,
        "high": max_high,
        "low": min_low,
        "range": round(max_high - min_low, 2),
        "high_times": [h["datetime"].split("T")[1][:5] for h in highs],
        "low_times": [l["datetime"].split("T")[1][:5] for l in lows],
    }

def save_tide_data(tides, filename):
    """Save tide data to JSON file."""
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tides, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(tides)} tide events to {filename}")

if __name__ == "__main__":
    import sys
    
    date = datetime.now()
    station = "QB"
    
    if len(sys.argv) > 1:
        try:
            date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        except ValueError:
            station = sys.argv[1]
    
    if len(sys.argv) > 2:
        station = sys.argv[2]
    
    print(f"Fetching tide data for {station} ({TIDAL_STATIONS.get(station, station)}) - {date.strftime('%Y-%m')}")
    
    tides = fetch_tide_data(station, date.year, date.month)
    if tides:
        save_tide_data(tides, f"data/tides_{station}_{date.strftime('%Y%m')}.json")
        
        # Show today's summary
        today_events = get_tide_events(date, station)
        range_data = get_tide_range(date, station)
        
        if range_data:
            print(f"\n📊 {date.strftime('%Y-%m-%d')} Tide Summary:")
            print(f"   High: {range_data['high']}m at {', '.join(range_data['high_times'])}")
            print(f"   Low:  {range_data['low']}m at {', '.join(range_data['low_times'])}")
            print(f"   Range: {range_data['range']}m")
    else:
        print("No data retrieved. Trying alternative source...")