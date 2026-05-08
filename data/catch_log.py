#!/usr/bin/env python3
"""
Hong Kong Fishing Catch Log
Store and query catch records for fishing spots.
"""

import json
import sys
import argparse
from datetime import date, datetime
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent
CATCHES_FILE = DATA_DIR / "catches.json"


def _load_catches():
    """Load catch records from JSON file."""
    if not CATCHES_FILE.exists():
        return []
    try:
        with open(CATCHES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_catches(catches):
    """Save catch records to JSON file."""
    CATCHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CATCHES_FILE, "w", encoding="utf-8") as f:
        json.dump(catches, f, ensure_ascii=False, indent=2)


def _resolve_spot(query):
    """Resolve a spot name/id to a spot dict. Returns (spot_id, spot_zh_name) or None."""
    # Lazy import to avoid circular imports
    from data.fishing_spots import FISHING_SPOTS
    query_lower = query.strip().lower()
    for s in FISHING_SPOTS:
        if s["id"].lower() == query_lower:
            return s["id"], s["name_zh"]
        if s["name_zh"] == query.strip():
            return s["id"], s["name_zh"]
        if s["name_en"].lower() == query_lower:
            return s["id"], s["name_zh"]
        # Partial Chinese match
        if query.strip() in s["name_zh"]:
            return s["id"], s["name_zh"]
    return None


def log_catch(spot_id, fish, count, weight=None, method=None, bait=None,
              tide_state=None, time=None, notes=None, catch_date=None):
    """
    Add a catch record.
    
    Args:
        spot_id: Fishing spot ID (references fishing_spots)
        fish: Chinese name of fish (e.g. "石斑")
        count: Number caught
        weight: Weight in 斤 (optional)
        method: Fishing method (釣法, e.g. "磯釣", "投釣", "沉底")
        bait: Bait used (魚餌, e.g. "活蝦", "青蟲")
        tide_state: Tide state (漲潮/退潮/高潮/低潮)
        time: Time of catch (HH:MM)
        notes: Free text notes
        catch_date: Date string (YYYY-MM-DD), defaults to today
    """
    # Resolve spot name
    resolved = _resolve_spot(spot_id)
    if resolved:
        spot_id = resolved[0]
    
    if catch_date is None:
        catch_date = date.today().isoformat()
    
    record = {
        "date": catch_date,
        "spot_id": spot_id,
        "fish": fish,
        "count": int(count),
    }
    if weight is not None:
        record["weight"] = float(weight)
    if method:
        record["method"] = method
    if bait:
        record["bait"] = bait
    if tide_state:
        record["tide_state"] = tide_state
    if time:
        record["time"] = time
    if notes:
        record["notes"] = notes
    
    # Generate unique ID
    from datetime import datetime
    record_id = f"{catch_date.replace('-', '')}_{datetime.now().strftime('%H%M%S')}_{spot_id}"
    record["id"] = record_id
    
    catches = _load_catches()
    catches.append(record)
    _save_catches(catches)
    
    # Get display name
    spot_name = spot_id
    if resolved:
        spot_name = resolved[1]
    
    print(f"✅ 已記錄: {spot_name} - {fish} x{count}", end="")
    if weight:
        print(f" ({weight}斤)", end="")
    print(f" [{catch_date}]")
    
    return record
    return record


def get_catches(spot_id=None, date=None, fish=None):
    """
    Query catches with optional filters.
    
    Args:
        spot_id: Filter by spot ID
        date: Filter by date (YYYY-MM-DD)
        fish: Filter by fish name
    
    Returns:
        List of matching catch records
    """
    catches = _load_catches()
    results = catches
    
    if spot_id:
        resolved = _resolve_spot(spot_id)
        sid = resolved[0] if resolved else spot_id
        results = [c for c in results if c.get("spot_id") == sid]
    if date:
        results = [c for c in results if c.get("date") == date]
    if fish:
        results = [c for c in results if c.get("fish") == fish]
    
    return results


def get_spot_stats(spot_id):
    """
    Get statistics for a fishing spot.
    
    Returns dict with:
        total_catches, total_count, most_common_fish, best_bait, best_method, best_tide
    """
    resolved = _resolve_spot(spot_id)
    sid = resolved[0] if resolved else spot_id
    spot_name = resolved[1] if resolved else spot_id
    
    catches = get_catches(spot_id=sid)
    if not catches:
        return {"spot_name": spot_name, "total_catches": 0, "total_count": 0}
    
    total_count = sum(c.get("count", 0) for c in catches)
    fish_counter = Counter()
    bait_counter = Counter()
    method_counter = Counter()
    tide_counter = Counter()
    
    for c in catches:
        fish_counter[c["fish"]] += c.get("count", 1)
        if c.get("bait"):
            bait_counter[c["bait"]] += c.get("count", 1)
        if c.get("method"):
            method_counter[c["method"]] += c.get("count", 1)
        if c.get("tide_state"):
            tide_counter[c["tide_state"]] += c.get("count", 1)
    
    stats = {
        "spot_name": spot_name,
        "total_catches": len(catches),
        "total_count": total_count,
        "most_common_fish": fish_counter.most_common(1)[0] if fish_counter else None,
        "best_bait": bait_counter.most_common(1)[0] if bait_counter else None,
        "best_method": method_counter.most_common(1)[0] if method_counter else None,
        "best_tide": tide_counter.most_common(1)[0] if tide_counter else None,
    }
    return stats


def get_fish_stats(fish_name):
    """
    Get statistics for a fish species across all spots.
    
    Returns dict with:
        fish, total_count, spots, best_bait, best_tide, best_method
    """
    catches = get_catches(fish=fish_name)
    if not catches:
        return {"fish": fish_name, "total_count": 0, "spots": []}
    
    total_count = sum(c.get("count", 0) for c in catches)
    spot_counter = Counter()
    bait_counter = Counter()
    tide_counter = Counter()
    method_counter = Counter()
    
    from data.fishing_spots import FISHING_SPOTS
    spot_map = {s["id"]: s["name_zh"] for s in FISHING_SPOTS}
    
    for c in catches:
        sid = c.get("spot_id", "")
        spot_name = spot_map.get(sid, sid)
        spot_counter[spot_name] += c.get("count", 1)
        if c.get("bait"):
            bait_counter[c["bait"]] += c.get("count", 1)
        if c.get("tide_state"):
            tide_counter[c["tide_state"]] += c.get("count", 1)
        if c.get("method"):
            method_counter[c["method"]] += c.get("count", 1)
    
    stats = {
        "fish": fish_name,
        "total_count": total_count,
        "total_catches": len(catches),
        "spots": spot_counter.most_common(),
        "best_bait": bait_counter.most_common(1)[0] if bait_counter else None,
        "best_tide": tide_counter.most_common(1)[0] if tide_counter else None,
        "best_method": method_counter.most_common(1)[0] if method_counter else None,
    }
    return stats


def update_catch(catch_id, fish=None, count=None, weight=None, method=None, bait=None, tide_state=None, time=None, notes=None, catch_date=None):
    """Update a catch record by ID. Only provided fields will be updated.
    
    Args:
        catch_id: The unique ID of the catch record
        fish, count, weight, method, bait, tide_state, time, notes, catch_date: Fields to update
    
    Returns:
        Updated record dict, or None if not found
    """
    catches = _load_catches()
    for i, c in enumerate(catches):
        if c.get("id") == catch_id:
            if fish is not None: c["fish"] = fish
            if count is not None: c["count"] = int(count)
            if weight is not None: c["weight"] = float(weight)
            if method is not None: c["method"] = method
            if bait is not None: c["bait"] = bait
            if tide_state is not None: c["tide_state"] = tide_state
            if time is not None: c["time"] = time
            if notes is not None: c["notes"] = notes
            if catch_date is not None: c["date"] = catch_date
            _save_catches(catches)
            return c
    return None


def delete_catch(catch_id):
    """Delete a catch record by its ID.
    
    Args:
        catch_id: The unique ID of the catch record (format: YYYYMMDD_HHMMSS_spot)
    
    Returns:
        True if deleted, False if not found
    """
    catches = _load_catches()
    original_len = len(catches)
    catches = [c for c in catches if c.get("id") != catch_id]
    if len(catches) < original_len:
        _save_catches(catches)
        return True
    return False


def delete_catches_by_spot(spot_id):
    """Delete all catch records for a spot.
    
    Args:
        spot_id: Spot name or ID
    
    Returns:
        Number of records deleted
    """
    resolved = _resolve_spot(spot_id)
    sid = resolved[0] if resolved else spot_id
    catches = _load_catches()
    original_len = len(catches)
    catches = [c for c in catches if c.get("spot_id") != sid]
    deleted = original_len - len(catches)
    _save_catches(catches)
    return deleted


def delete_all_catches():
    """Delete all catch records.
    
    Returns:
        Number of records deleted
    """
    catches = _load_catches()
    deleted = len(catches)
    _save_catches([])
    return deleted


def format_catch_report(spot_id=None):
    """Pretty print catch stats."""
    from data.fishing_spots import FISHING_SPOTS
    spot_map = {s["id"]: s["name_zh"] for s in FISHING_SPOTS}
    
    if spot_id:
        # Spot-specific report
        resolved = _resolve_spot(spot_id)
        sid = resolved[0] if resolved else spot_id
        spot_name = resolved[1] if resolved else spot_id
        catches = get_catches(spot_id=sid)
        
        if not catches:
            print(f"📋 {spot_name} 暫無釣獲記錄")
            return
        
        stats = get_spot_stats(sid)
        print(f"📋 {spot_name} 釣獲記錄:")
        
        for c in sorted(catches, key=lambda x: x.get("date", ""), reverse=True)[:20]:
            d = c.get("date", "")[5:]  # MM-DD
            fish = c.get("fish", "?")
            count = c.get("count", 0)
            weight = c.get("weight")
            bait = c.get("bait", "")
            method = c.get("method", "")
            tide = c.get("tide_state", "")
            
            parts = [f"{d} {fish} x{count}"]
            if weight:
                parts.append(f"{weight}斤")
            if bait or method:
                parts.append(f"{bait}/{method}" if bait and method else bait or method)
            if tide:
                parts.append(tide)
            print(f"   {' '.join(parts)}")
        
        # Summary
        fish_counter = Counter()
        for c in catches:
            fish_counter[c["fish"]] += c.get("count", 0)
        fish_summary = ", ".join(f"{f}({n})" for f, n in fish_counter.most_common(5))
        print(f"共 {stats['total_count']} 條魚，最常釣: {fish_summary}")
    else:
        # Overall report
        all_catches = _load_catches()
        if not all_catches:
            print("📋 暫無釣獲記錄")
            return
        
        # Group by spot
        by_spot = {}
        for c in all_catches:
            sid = c.get("spot_id", "unknown")
            by_spot.setdefault(sid, []).append(c)
        
        print("📋 釣獲總報告:")
        total_fish = 0
        for sid in sorted(by_spot.keys()):
            spot_name = spot_map.get(sid, sid)
            catches = by_spot[sid]
            count = sum(c.get("count", 0) for c in catches)
            total_fish += count
            fish_counter = Counter()
            for c in catches:
                fish_counter[c["fish"]] += c.get("count", 0)
            top_fish = ", ".join(f"{f}({n})" for f, n in fish_counter.most_common(3))
            print(f"   {spot_name}: {len(catches)}次, {count}條魚 - {top_fish}")
        
        print(f"\n總計: {len(all_catches)}次記錄, {total_fish}條魚")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hong Kong Fishing Catch Log')
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # log command
    log_parser = subparsers.add_parser("log", help="Log a catch")
    log_parser.add_argument("spot", help="Spot name or ID (e.g. 龍蝦灣, lobster_bay)")
    log_parser.add_argument("fish", help="Fish name in Chinese (e.g. 石斑)")
    log_parser.add_argument("count", type=int, help="Number caught")
    log_parser.add_argument("--weight", type=float, help="Weight in 斤")
    log_parser.add_argument("--method", help="釣法 (e.g. 磯釣, 投釣, 沉底)")
    log_parser.add_argument("--bait", help="魚餌 (e.g. 活蝦, 青蟲)")
    log_parser.add_argument("--tide", help="潮汐狀態 (漲潮/退潮/高潮/低潮)")
    log_parser.add_argument("--time", help="時間 (HH:MM)")
    log_parser.add_argument("--date", help="日期 (YYYY-MM-DD), 預設今天")
    log_parser.add_argument("--notes", help="備註")
    
    # stats command
    stats_parser = subparsers.add_parser("stats", help="Show stats for a spot")
    stats_parser.add_argument("spot", help="Spot name or ID")
    
    # fish command
    fish_parser = subparsers.add_parser("fish", help="Show stats for a fish")
    fish_parser.add_argument("name", help="Fish name in Chinese")
    
    # list command
    list_parser = subparsers.add_parser("list", help="Show recent catches")
    list_parser.add_argument("--spot", help="Filter by spot")
    list_parser.add_argument("--fish", help="Filter by fish")
    list_parser.add_argument("--limit", type=int, default=20, help="Max results")
    
    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete catch records")
    delete_parser.add_argument("--id", help="Delete a specific catch by ID")
    delete_parser.add_argument("--spot", help="Delete all catches for a spot")
    delete_parser.add_argument("--all", action="store_true", help="Delete all catches")

    # report command
    report_parser = subparsers.add_parser("report", help="Show overall catch report")
    
    args = parser.parse_args()
    
    if args.command == "log":
        log_catch(
            spot_id=args.spot,
            fish=args.fish,
            count=args.count,
            weight=args.weight,
            method=args.method,
            bait=args.bait,
            tide_state=args.tide,
            time=args.time,
            notes=args.notes,
            catch_date=args.date,
        )
    elif args.command == "stats":
        format_catch_report(spot_id=args.spot)
    elif args.command == "fish":
        stats = get_fish_stats(args.name)
        if stats["total_count"] == 0:
            print(f"🐟 {args.name} 暫無釣獲記錄")
        else:
            print(f"🐟 {args.name} 釣獲統計:")
            print(f"   總數: {stats['total_count']}條 ({stats['total_catches']}次記錄)")
            if stats["spots"]:
                spots_str = ", ".join(f"{s}({n})" for s, n in stats["spots"])
                print(f"   釣點: {spots_str}")
            if stats["best_bait"]:
                print(f"   最佳魚餌: {stats['best_bait'][0]} ({stats['best_bait'][1]}條)")
            if stats["best_method"]:
                print(f"   最佳釣法: {stats['best_method'][0]} ({stats['best_method'][1]}條)")
            if stats["best_tide"]:
                print(f"   最佳潮汐: {stats['best_tide'][0]} ({stats['best_tide'][1]}條)")
    elif args.command == "list":
        catches = get_catches(spot_id=args.spot, fish=args.fish)
        if not catches:
            print("📋 暫無釣獲記錄")
        else:
            from data.fishing_spots import FISHING_SPOTS
            spot_map = {s["id"]: s["name_zh"] for s in FISHING_SPOTS}
            for c in sorted(catches, key=lambda x: x.get("date", ""), reverse=True)[:args.limit]:
                spot_name = spot_map.get(c.get("spot_id", ""), c.get("spot_id", "?"))
                d = c.get("date", "?")
                fish = c.get("fish", "?")
                count = c.get("count", 0)
                weight = c.get("weight")
                w_str = f" {weight}斤" if weight else ""
                print(f"   {d} {spot_name} {fish} x{count}{w_str}")
    elif args.command == "delete":
        if args.all:
            deleted = delete_all_catches()
            print(f"🗑️ 已刪除所有 {deleted} 條記錄")
        elif args.id:
            if delete_catch(args.id):
                print(f"🗑️ 已刪除記錄: {args.id}")
            else:
                print(f"❌ 找不到記錄: {args.id}")
        elif args.spot:
            deleted = delete_catches_by_spot(args.spot)
            print(f"🗑️ 已刪除 {args.spot} 的 {deleted} 條記錄")
        else:
            print("❌ 請指定 --id, --spot 或 --all")
    elif args.command == "report":
        format_catch_report()
    else:
        parser.print_help()