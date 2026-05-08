#!/usr/bin/env python3
"""
Hong Kong Fish Season Calendar
Month-by-month fishing calendar with bite ratings, methods, and bait recommendations.
"""

# bite_rating: 1-5 (5 = peak season, most active)

FISH_SEASON_CALENDAR = {
    1: {  # 一月
        "烏頭": {"bite_rating": 5, "method": "浮波、沉底", "bait": "麵包、青蟲", "note": "冬季巔峰！大烏頭最活躍時期"},
        "白鱲": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "冬季好釣，深水位"},
        "鱲魚": {"bite_rating": 3, "method": "沉底、浮波", "bait": "青蟲、蝦肉", "note": "全年可釣，冬季一般"},
        "盲鰽": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "秋冬巔峰期"},
        "黃腲鱲": {"bite_rating": 2, "method": "沉底、浮波", "bait": "青蟲、蝦肉、南極蝦", "note": "冬季較慢，深水有魚"},
        "泥鯭": {"bite_rating": 2, "method": "沉底", "bait": "青蟲、蝦肉", "note": "冬季較少"},
        "石斑": {"bite_rating": 1, "method": "磯釣、沉底", "bait": "活蝦、魚肉", "note": "冬季很少咬口"},
        "鯛魚": {"bite_rating": 2, "method": "沉底、磯釣", "bait": "青蟲、蝦肉", "note": "冬季一般"},
        "紅鮋": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦、魚肉", "note": "冬季不活躍"},
        "火點": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "冬季很少"},
        "沙鯭": {"bite_rating": 1, "method": "投釣", "bait": "青蟲、蝦肉", "note": "冬季少"},
    },
    2: {  # 二月
        "烏頭": {"bite_rating": 5, "method": "浮波、沉底", "bait": "麵包、青蟲", "note": "仍然是冬季高峰"},
        "白鱲": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "冬季持續好釣"},
        "盲鰽": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "秋冬尾聲"},
        "鱲魚": {"bite_rating": 3, "method": "沉底、浮波", "bait": "青蟲、蝦肉", "note": "開始回升"},
        "黃腲鱲": {"bite_rating": 2, "method": "沉底、浮波", "bait": "青蟲、南極蝦", "note": "開始好轉"},
        "泥鯭": {"bite_rating": 2, "method": "沉底", "bait": "青蟲、蝦肉", "note": "仍然少"},
        "石斑": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "尚未活躍"},
        "鯛魚": {"bite_rating": 2, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
        "紅鮋": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "不活躍"},
        "火點": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "少"},
        "沙鯭": {"bite_rating": 1, "method": "投釣", "bait": "青蟲", "note": "少"},
    },
    3: {  # 三月
        "烏頭": {"bite_rating": 4, "method": "浮波、沉底", "bait": "麵包、青蟲", "note": "開始回落但仍好釣"},
        "白鱲": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "春季開始"},
        "鱲魚": {"bite_rating": 4, "method": "浮波、沉底", "bait": "青蟲、蝦肉", "note": "春季回升！"},
        "黃腲鱲": {"bite_rating": 3, "method": "浮波、沉底", "bait": "青蟲、南極蝦", "note": "開始活躍"},
        "盲鰽": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "尾聲"},
        "泥鯭": {"bite_rating": 2, "method": "沉底", "bait": "青蟲、蝦肉", "note": "慢慢多"},
        "石斑": {"bite_rating": 2, "method": "磯釣、沉底", "bait": "活蝦、魚肉", "note": "天氣回暖開始咬"},
        "鯛魚": {"bite_rating": 3, "method": "沉底、磯釣", "bait": "青蟲、蝦肉", "note": "春季開始活躍"},
        "紅鮋": {"bite_rating": 2, "method": "磯釣", "bait": "活蝦、魚肉", "note": "開始出現"},
        "火點": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "仍少"},
        "沙鯭": {"bite_rating": 2, "method": "投釣", "bait": "青蟲、蝦肉", "note": "開始多"},
    },
    4: {  # 四月
        "黃腲鱲": {"bite_rating": 4, "method": "浮波、沉底", "bait": "青蟲、南極蝦、蝦肉", "note": "春季高峰開始！"},
        "鱲魚": {"bite_rating": 5, "method": "浮波、沉底", "bait": "青蟲、蝦肉", "note": "春季巔峰！"},
        "鯛魚": {"bite_rating": 4, "method": "沉底、磯釣", "bait": "青蟲、蝦肉、活蝦", "note": "好季節"},
        "石斑": {"bite_rating": 3, "method": "磯釣、沉底", "bait": "活蝦、魚肉", "note": "越來越活躍"},
        "烏頭": {"bite_rating": 3, "method": "浮波", "bait": "麵包、青蟲", "note": "春季仍有但減少"},
        "白鱲": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
        "泥鯭": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "回暖好釣"},
        "紅鮋": {"bite_rating": 3, "method": "磯釣", "bait": "活蝦、魚肉", "note": "開始好釣"},
        "沙鯭": {"bite_rating": 3, "method": "投釣", "bait": "青蟲、蝦肉", "note": "活躍"},
        "火點": {"bite_rating": 2, "method": "磯釣", "bait": "活蝦", "note": "開始出現"},
        "盲鰽": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "淡季"},
    },
    5: {  # 五月
        "黃腲鱲": {"bite_rating": 5, "method": "浮波、沉底", "bait": "青蟲、南極蝦、蝦肉", "note": "🔥 全年最旺！必釣！"},
        "鱲魚": {"bite_rating": 5, "method": "浮波、沉底", "bait": "青蟲、蝦肉", "note": "🔥 巔峰期！"},
        "石斑": {"bite_rating": 4, "method": "磯釣、沉底", "bait": "活蝦、魚肉", "note": "開始大咬"},
        "鯛魚": {"bite_rating": 5, "method": "磯釣、沉底", "bait": "活蝦、青蟲、魚肉", "note": "🔥 巔峰期！"},
        "紅鮋": {"bite_rating": 4, "method": "磯釣", "bait": "活蝦、魚肉", "note": "好季節"},
        "泥鯭": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "活躍"},
        "沙鯭": {"bite_rating": 4, "method": "投釣", "bait": "青蟲、蝦肉", "note": "沙灘好釣"},
        "白鱲": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
        "火點": {"bite_rating": 3, "method": "磯釣", "bait": "活蝦", "note": "開始活躍"},
        "烏頭": {"bite_rating": 2, "method": "浮波", "bait": "麵包、青蟲", "note": "淡季"},
        "盲鰽": {"bite_rating": 1, "method": "沉底", "bait": "青蟲", "note": "少"},
    },
    6: {  # 六月
        "黃腲鱲": {"bite_rating": 5, "method": "浮波、沉底", "bait": "青蟲、南極蝦、蝦肉", "note": "🔥 巔峰持續！"},
        "石斑": {"bite_rating": 5, "method": "磯釣、沉底", "bait": "活蝦、魚肉", "note": "🔥 夏季大咬！最佳時期"},
        "鯛魚": {"bite_rating": 5, "method": "磯釣、沉底", "bait": "活蝦、青蟲、魚肉", "note": "🔥 巔峰！"},
        "紅鮋": {"bite_rating": 5, "method": "磯釣", "bait": "活蝦、魚肉", "note": "🔥 夏季巔峰！"},
        "火點": {"bite_rating": 4, "method": "磯釣", "bait": "活蝦", "note": "夏季好釣"},
        "泥鯭": {"bite_rating": 5, "method": "沉底", "bait": "青蟲、蝦肉", "note": "🔥 最旺！"},
        "沙鯭": {"bite_rating": 4, "method": "投釣", "bait": "青蟲、蝦肉", "note": "好釣"},
        "鱲魚": {"bite_rating": 4, "method": "浮波、沉底", "bait": "青蟲、蝦肉", "note": "仍然好釣"},
        "白鱲": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "夏季較少"},
        "烏頭": {"bite_rating": 1, "method": "浮波", "bait": "麵包", "note": "淡季"},
        "盲鰽": {"bite_rating": 1, "method": "沉底", "bait": "青蟲", "note": "少"},
    },
    7: {  # 七月
        "石斑": {"bite_rating": 5, "method": "磯釣、沉底", "bait": "活蝦、魚肉", "note": "🔥 夏季巔峰！"},
        "紅鮋": {"bite_rating": 5, "method": "磯釣", "bait": "活蝦、魚肉", "note": "🔥 最旺！"},
        "火點": {"bite_rating": 5, "method": "磯釣", "bait": "活蝦", "note": "🔥 夏季巔峰！"},
        "泥鯭": {"bite_rating": 5, "method": "沉底", "bait": "青蟲、蝦肉", "note": "🔥 持續高峰"},
        "黃腲鱲": {"bite_rating": 4, "method": "浮波、沉底", "bait": "青蟲、南極蝦", "note": "仍然好釣，注意颱風"},
        "鯛魚": {"bite_rating": 4, "method": "磯釣、沉底", "bait": "活蝦、青蟲", "note": "好釣"},
        "沙鯭": {"bite_rating": 4, "method": "投釣", "bait": "青蟲、蝦肉", "note": "好釣"},
        "鱲魚": {"bite_rating": 3, "method": "浮波、沉底", "bait": "青蟲、蝦肉", "note": "開始回落"},
        "白鱲": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "少"},
        "烏頭": {"bite_rating": 1, "method": "浮波", "bait": "麵包", "note": "淡季"},
        "盲鰽": {"bite_rating": 1, "method": "沉底", "bait": "青蟲", "note": "少"},
    },
    8: {  # 八月
        "石斑": {"bite_rating": 5, "method": "磯釣、沉底", "bait": "活蝦、魚肉", "note": "🔥 巔峰持續！注意颱風"},
        "紅鮋": {"bite_rating": 5, "method": "磯釣", "bait": "活蝦、魚肉", "note": "🔥 仍然最旺"},
        "火點": {"bite_rating": 4, "method": "磯釣", "bait": "活蝦", "note": "好釣"},
        "泥鯭": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "仍然活躍"},
        "黃腲鱲": {"bite_rating": 4, "method": "浮波、沉底", "bait": "青蟲、南極蝦", "note": "仍然好釣"},
        "鯛魚": {"bite_rating": 4, "method": "磯釣、沉底", "bait": "活蝦、青蟲", "note": "好釣"},
        "沙鯭": {"bite_rating": 4, "method": "投釣", "bait": "青蟲、蝦肉", "note": "好釣"},
        "鱲魚": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
        "白鱲": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "少"},
        "烏頭": {"bite_rating": 1, "method": "浮波", "bait": "麵包", "note": "淡季"},
        "盲鰽": {"bite_rating": 1, "method": "沉底", "bait": "青蟲", "note": "少"},
    },
    9: {  # 九月
        "石斑": {"bite_rating": 4, "method": "磯釣、沉底", "bait": "活蝦、魚肉", "note": "仍然好釣"},
        "紅鮋": {"bite_rating": 5, "method": "磯釣", "bait": "活蝦、魚肉", "note": "🔥 秋季大咬！"},
        "火點": {"bite_rating": 3, "method": "磯釣", "bait": "活蝦", "note": "開始回落"},
        "泥鯭": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "活躍"},
        "黃腲鱲": {"bite_rating": 3, "method": "浮波、沉底", "bait": "青蟲、南極蝦", "note": "開始回落"},
        "鯛魚": {"bite_rating": 3, "method": "磯釣、沉底", "bait": "活蝦、青蟲", "note": "回落中"},
        "烏頭": {"bite_rating": 3, "method": "浮波", "bait": "麵包、青蟲", "note": "⚠️ 秋季開始活躍！"},
        "白鱲": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "開始回升"},
        "盲鰽": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "開始出現"},
        "沙鯭": {"bite_rating": 3, "method": "投釣", "bait": "青蟲、蝦肉", "note": "一般"},
        "鱲魚": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
    },
    10: {  # 十月
        "烏頭": {"bite_rating": 5, "method": "浮波、沉底", "bait": "麵包、青蟲", "note": "🔥 秋冬巔峰開始！"},
        "白鱲": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "好釣"},
        "盲鰽": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "活躍中"},
        "紅鮋": {"bite_rating": 4, "method": "磯釣", "bait": "活蝦、魚肉", "note": "仍然好釣"},
        "石斑": {"bite_rating": 3, "method": "磯釣", "bait": "活蝦", "note": "開始回落"},
        "泥鯭": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
        "黃腲鱲": {"bite_rating": 2, "method": "浮波、沉底", "bait": "青蟲、南極蝦", "note": "減少中"},
        "鯛魚": {"bite_rating": 2, "method": "沉底", "bait": "青蟲、蝦肉", "note": "回落"},
        "鱲魚": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
        "沙鯭": {"bite_rating": 2, "method": "投釣", "bait": "青蟲", "note": "回落"},
        "火點": {"bite_rating": 2, "method": "磯釣", "bait": "活蝦", "note": "少"},
    },
    11: {  # 十一月
        "烏頭": {"bite_rating": 5, "method": "浮波、沉底", "bait": "麵包、青蟲", "note": "🔥 冬季高峰！最佳時期"},
        "白鱲": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "好釣"},
        "盲鰽": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "秋冬高峰"},
        "鱲魚": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
        "紅鮋": {"bite_rating": 3, "method": "磯釣", "bait": "活蝦", "note": "開始回落"},
        "石斑": {"bite_rating": 2, "method": "磯釣", "bait": "活蝦", "note": "減少"},
        "泥鯭": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "減少"},
        "黃腲鱲": {"bite_rating": 2, "method": "沉底", "bait": "青蟲、南極蝦", "note": "深水有魚"},
        "鯛魚": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "一般"},
        "沙鯭": {"bite_rating": 1, "method": "投釣", "bait": "青蟲", "note": "少"},
        "火點": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "少"},
    },
    12: {  # 十二月
        "烏頭": {"bite_rating": 5, "method": "浮波、沉底", "bait": "麵包、青蟲", "note": "🔥 冬季巔峰！大烏頭"},
        "白鱲": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "好釣"},
        "盲鰽": {"bite_rating": 4, "method": "沉底", "bait": "青蟲、蝦肉", "note": "秋冬高峰"},
        "鱲魚": {"bite_rating": 3, "method": "沉底", "bait": "青蟲、蝦肉", "note": "一般"},
        "黃腲鱲": {"bite_rating": 2, "method": "沉底", "bait": "青蟲、南極蝦", "note": "冬季深水有魚"},
        "泥鯭": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "少"},
        "石斑": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "很少咬口"},
        "鯛魚": {"bite_rating": 2, "method": "沉底", "bait": "青蟲", "note": "一般"},
        "紅鮋": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "不活躍"},
        "沙鯭": {"bite_rating": 1, "method": "投釣", "bait": "青蟲", "note": "少"},
        "火點": {"bite_rating": 1, "method": "磯釣", "bait": "活蝦", "note": "少"},
    },
}


def get_monthly_fish(month):
    """Get fish calendar for a specific month."""
    return FISH_SEASON_CALENDAR.get(month, {})


def get_spot_monthly_fish(spot_id, month):
    """Get recommended fish for a specific spot in a specific month."""
    from data.fishing_spots import FISHING_SPOTS
    
    spot = next((s for s in FISHING_SPOTS if s['id'].strip() == spot_id.strip()), None)
    if not spot:
        return {}
    
    month_data = FISH_SEASON_CALENDAR.get(month, {})
    spot_fish = spot.get('fish', [])
    
    result = {}
    for fish in spot_fish:
        if fish in month_data:
            result[fish] = month_data[fish]
    
    # Sort by bite rating descending
    result = dict(sorted(result.items(), key=lambda x: x[1]['bite_rating'], reverse=True))
    return result


def get_best_month_for_fish(fish_name):
    """Find the best months for a specific fish species."""
    months = []
    for month, data in FISH_SEASON_CALENDAR.items():
        if fish_name in data:
            months.append((month, data[fish_name]['bite_rating']))
    
    months.sort(key=lambda x: x[1], reverse=True)
    return months


if __name__ == "__main__":
    from data.fishing_spots import FISHING_SPOTS
    
    print("🐟 香港釣魚月曆")
    print("=" * 60)
    
    season_names = {1: "冬季", 2: "冬季", 3: "春季", 4: "春季", 5: "春季",
                    6: "夏季", 7: "夏季", 8: "夏季", 9: "秋季", 10: "秋季",
                    11: "秋季", 12: "冬季"}
    
    for month in range(1, 13):
        data = FISH_SEASON_CALENDAR[month]
        season = season_names[month]
        print(f"\n📅 {month}月（{season}）")
        print("-" * 40)
        
        sorted_fish = sorted(data.items(), key=lambda x: x[1]['bite_rating'], reverse=True)
        for fish, info in sorted_fish:
            stars = "⭐" * info['bite_rating']
            fire = "🔥" if info['bite_rating'] >= 5 else ""
            print(f"  {stars} {fire} {fish}")
            print(f"     🎣 {info['method']} | 🪱 {info['bait']}")
            print(f"     💡 {info['note']}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 各魚種最佳月份")
    print("-" * 40)
    all_fish = set()
    for m in FISH_SEASON_CALENDAR.values():
        all_fish.update(m.keys())
    
    for fish in sorted(all_fish):
        best = get_best_month_for_fish(fish)
        peak_months = [str(m) for m, r in best if r >= 5]
        good_months = [str(m) for m, r in best if r == 4]
        print(f"  {fish}: 🔥{','.join(peak_months) if peak_months else '無'} | ✅{','.join(good_months) if good_months else '無'}月")