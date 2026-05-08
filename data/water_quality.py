#!/usr/bin/env python3
"""Add water quality and edibility data to all fishing spots."""

# Water quality and edibility per spot
# water_quality: excellent/good/moderate/poor
# water_quality_zh: Chinese description
# edible: which fish are safe to eat, which to avoid
# edible_note: general eating advice

WATER_EDIBILITY = {
    # === HK Island ===
    "aberdeen": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 維港內灣，水質一般",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "盲鰽": "limit", "鱲魚": "yes"},
        "edible_note": "維港水質一般，建議少量食用。烏頭底棲魚易積累重金屬，不宜多食。黃腲鱲相對安全。",
    },
    "causeway_bay": {
        "water_quality": "poor",
        "water_quality_zh": "差 — 避風塘內，水質差",
        "edible": {"烏頭": "no", "黃腲鱲": "limit", "鱲魚": "limit"},
        "edible_note": "⚠️ 避風塘水質差，不建議食用。釣到放生為佳。",
    },
    "shek_o": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 東面外海，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "泥鯭": "yes", "紅鮋": "yes"},
        "edible_note": "✅ 外海水質好，魚可放心食用。石斑泥鯭都好味。",
    },
    "big_wave_bay": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 東面沙灘，水質好",
        "edible": {"沙鯭": "yes", "白鱲": "yes", "黃腲鱲": "yes"},
        "edible_note": "✅ 沙灘水質好，沙鯭白鱲可食。",
    },

    # === Kowloon ===
    "lei_yue_mun": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 維港東面，水質一般",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "火點": "limit"},
        "edible_note": "維港水質一般。石斑火點建議少量食用，鯛魚相對安全。大魚不宜多食。",
    },
    "cha_kwo_ling": {
        "water_quality": "poor",
        "water_quality_zh": "差 — 觀塘避風塘附近，水質差",
        "edible": {"烏頭": "no", "黃腲鱲": "limit", "鱲魚": "limit"},
        "edible_note": "⚠️ 觀塘水質差，不建議食用。釣到放生。",
    },
    "sam_dip_wong": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 將軍澳內灣",
        "edible": {"石斑": "limit", "鯛魚": "yes", "泥鯭": "yes"},
        "edible_note": "將軍澳水質一般。小型魚可食，大魚建議放生。",
    },

    # === NT East ===
    "tolo_harbour": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 吐露港內灣，水質一般",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "白鱲": "yes", "鱲魚": "yes"},
        "edible_note": "吐露港水質一般但持續改善。烏頭建議少量食用，鯛魚類可食。",
    },
    "tai_mei_tuk": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 船灣附近，水質一般",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "白鱲": "yes", "鱲魚": "yes"},
        "edible_note": "水質一般。秋冬大烏頭建議少量食用（1-2斤以下）。鯛魚類可食。",
    },
    "three_fathoms_cove": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 三門仔外灣，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "黃腲鱲": "yes"},
        "edible_note": "✅ 外灣水質好，魚可食。石斑鯛魚好味。",
    },

    # === NT West ===
    "sham_tseng": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 深井內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes"},
        "edible_note": "水質一般。烏頭少量食用，鯛魚類可食。釣完食燒鵝！",
    },
    "castle_peak_bay": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 屯門內灣",
        "edible": {"沙鯭": "yes", "白鱲": "yes", "黃腲鱲": "limit"},
        "edible_note": "屯門水質一般。小型魚可食，大魚建議放生。",
    },

    # === Islands ===
    "cheung_chau": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 外島，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "泥鯭": "yes", "火點": "yes"},
        "edible_note": "✅ 外島水質好，魚可放心食用。石斑蒸/煎都好味。",
    },
    "lamma_island": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 外島，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "火點": "yes"},
        "edible_note": "✅ 南丫島水質好，魚可食。釣完去海鮮餐廳加工！",
    },
    "lantau_tung_chung": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 東涌內灣，近機場",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "白鱲": "yes"},
        "edible_note": "近機場水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "ping_chau": {
        "water_quality": "excellent",
        "water_quality_zh": "極佳 — 東北外島，水質極佳",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "火點": "yes", "泥鯭": "yes"},
        "edible_note": "✅✅ 香港最佳水質！海岸公園，魚全部可食。石斑紅鮋特別鮮味。",
    },
    "crooked_island": {
        "water_quality": "excellent",
        "water_quality_zh": "極佳 — 東北外島，水質極佳",
        "edible": {"石斑": "yes", "紅鮋": "yes", "鯛魚": "yes", "火點": "yes"},
        "edible_note": "✅✅ 東北水域水質極佳，魚全部可放心食用。大魚特別鮮味。",
    },
    "lau_fau_shan": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣，水質一般",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "白鱲": "yes", "泥鯭": "yes"},
        "edible_note": "后海灣水質一般。烏頭少量食用（1-2斤以下可），鯛魚類可食。釣完食海鮮！",
    },
    "lau_fau_shan_rocky": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣，水質一般",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "后海灣水質一般。石斑建議少量食用，鯛魚類可食。",
    },
    "pak_kong": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣，水質一般",
        "edible": {"石斑": "limit", "鯛魚": "yes", "紅鮋": "limit"},
        "edible_note": "⚠️ 后海灣水質一般。大魚建議少量食用，小型魚可食。",
    },
    "ha_tsuen": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "后海灣水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "tsim_be_tsui_west": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "后海灣水質一般。石斑建議少量食用，鯛魚類可食。",
    },
    "ting_kau": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 深井灣，水質一般",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "深井灣水質一般。石斑少量食用，鯛魚泥鯭可食。",
    },
    "anglers_beach": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 深井灣沙灘",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "白鱲": "yes", "烏頭": "limit"},
        "edible_note": "沙灘水質一般。小型魚可食，烏頭少量食用。",
    },
    "lido_beach": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 深井灣沙灘",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "白鱲": "yes"},
        "edible_note": "沙灘水質一般。小型魚可食。",
    },
    "tsuen_wan_waterfront": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 荃灣內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "荃灣內灣水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "ma_wan": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 馬灣海峽，水流急水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "✅ 馬灣海峽水流急水質好，魚可食。石斑紅鮋特別好味！",
    },
    "tsing_yi_waterfront": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 荃灣內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "荃灣內灣水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "tuen_mun_waterfront": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 屯門內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "屯門內灣水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "sam_shing": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 屯門內灣",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "屯門內灣水質一般。石斑少量食用，鯛魚泥鯭可食。釣完去海鮮街加工！",
    },

    # === Sai Kung ===
    "sai_kung_town": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 西貢內灣，水質好",
        "edible": {"黃腲鱲": "yes", "烏頭": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "✅ 西貢水質好，魚可食。黃腲鱲最受歡迎。",
    },
    "sai_kung_pier": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 西貢碼頭，水質好",
        "edible": {"黃腲鱲": "yes", "鯛魚": "yes", "泥鯭": "yes", "烏頭": "yes"},
        "edible_note": "✅ 水質好，魚可食。碼頭附近黃腲鱲可帶走。",
    },
    "tui_min_chau": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 西貢外灣，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "泥鯭": "yes", "黃腲鱲": "yes"},
        "edible_note": "✅ 外灣水質好，石斑紅鮋可食。西貢最佳磯釣位之一。",
    },
    "sharp_island": {
        "water_quality": "excellent",
        "water_quality_zh": "極佳 — 外島，水質極佳",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "火點": "yes", "泥鯭": "yes"},
        "edible_note": "✅✅ 外島水質極佳！魚全部可放心食用。帶活蝦釣石斑最好味。",
    },
    "pak_sha_chau": {
        "water_quality": "excellent",
        "water_quality_zh": "極佳 — 外島，水質極佳",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes"},
        "edible_note": "✅✅ 水質極佳！大魚可放心食用。西貢最佳釣點之一。",
    },
    "sham_chuk_tsuen": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 西貢北內灣",
        "edible": {"黃腲鱲": "yes", "烏頭": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "✅ 內灣水質好，魚可食。秋冬烏頭好味。",
    },
    "clear_water_bay": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 清水灣半島，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "泥鯭": "yes", "黃腲鱲": "yes"},
        "edible_note": "✅ 清水灣水質好，魚可食。石斑清蒸好味。",
    },
    "clear_water_bay_1": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 清水灣一灘",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "白鱲": "yes"},
        "edible_note": "✅ 水質好，沙鯭可食。適合新手帶小孩釣魚。",
    },
    "lobster_bay": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 清水灣半島外灣",
        "edible": {"石斑": "yes", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "✅ 外灣水質好，石斑紅鮋可食。磯釣首選。",
    },
    "palm_beach": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 銀線灣沙灘",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "白鱲": "yes"},
        "edible_note": "✅ 水質好，小型魚可食。新手友善。",
    },
    "tai_a_chau": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 半島南端外海",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "泥鯭": "yes"},
        "edible_note": "✅ 外海水質好，魚可食。",
    },
    "po_toi_au": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 小漁村，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "✅ 小漁村水質好，釣到可去附近海鮮檔加工！",
    },
    "tin_hau_temple_bay": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 西貢內灣",
        "edible": {"黃腲鱲": "yes", "烏頭": "yes", "鱲魚": "yes"},
        "edible_note": "✅ 西貢內灣水質好，魚可食。",
    },
    "tai_chong_ting": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 西貢內灣",
        "edible": {"黃腲鱲": "yes", "烏頭": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "✅ 內灣水質好，秋冬烏頭好味。",
    },
    "high_island": {
        "water_quality": "excellent",
        "water_quality_zh": "極佳 — 東壩外海，水質極佳",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "火點": "yes", "泥鯭": "yes"},
        "edible_note": "✅✅ 香港最佳水質！5-10斤石斑紅鮋，全部可食。鮮味極佳！",
    },
    "ma_on_shan_waterfront": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 吐露港內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "吐露港水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "wu_kai_sha": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 吐露港內灣沙灘",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "白鱲": "yes", "烏頭": "limit"},
        "edible_note": "吐露港水質一般。小型魚可食，烏頭少量食用。",
    },
    "wu_kai_sha_pier": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 吐露港內灣",
        "edible": {"黃腲鱲": "yes", "鯛魚": "yes", "烏頭": "limit", "泥鯭": "yes"},
        "edible_note": "吐露港水質一般。烏頭少量食用，鯛魚泥鯭可食。",
    },
    "pak_shek_kok": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 吐露港內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "吐露港水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "tolo_harbour_front": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 吐露港內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "吐露港水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "fo_tan": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 城門河口，近排污口",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes"},
        "edible_note": "⚠️ 近排污口水質一般。烏頭少量食用，建議細魚可食大魚放生。",
    },
    "shing_mun_river": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 城門河，近排污口",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "⚠️ 城門河近排污口水質一般。烏頭少量食用，細魚可食。",
    },
    "ma_on_shan_rocky": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 吐露港外灣",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "吐露港水質一般。石斑少量食用，鯛魚泥鯭可食。",
    },
    "ting_kau": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 深井灣，水質一般",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "深井灣水質一般。石斑少量食用，鯛魚泥鯭可食。",
    },
    "anglers_beach": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 深井灣沙灘",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "白鱲": "yes", "烏頭": "limit"},
        "edible_note": "沙灘水質一般。小型魚可食，烏頭少量食用。",
    },
    "lido_beach": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 深井灣沙灘",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "白鱲": "yes"},
        "edible_note": "沙灘水質一般。小型魚可食。",
    },
    "tsuen_wan_waterfront": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 荃灣內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "荃灣內灣水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "ma_wan": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 馬灣海峽，水流急水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "✅ 馬灣海峽水流急水質好，魚可食。石斑紅鮋特別好味！",
    },
    "tsing_yi_waterfront": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 荃灣內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "荃灣內灣水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "tuen_mun_waterfront": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 屯門內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "屯門內灣水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "sam_shing": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 屯門內灣",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "屯門內灣水質一般。石斑少量食用，鯛魚泥鯭可食。釣完去海鮮街加工！",
    },
    "lau_fau_shan": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣，水質一般",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "白鱲": "yes", "泥鯭": "yes"},
        "edible_note": "后海灣水質一般。烏頭少量食用（1-2斤以下可），鯛魚類可食。釣完食海鮮！",
    },
    "lau_fau_shan_rocky": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣，水質一般",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "后海灣水質一般。石斑建議少量食用，鯛魚類可食。",
    },
    "pak_kong": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣，水質一般",
        "edible": {"石斑": "limit", "鯛魚": "yes", "紅鮋": "limit"},
        "edible_note": "⚠️ 后海灣水質一般。大魚建議少量食用，小型魚可食。",
    },
    "ha_tsuen": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣內灣",
        "edible": {"烏頭": "limit", "黃腲鱲": "yes", "鱲魚": "yes", "泥鯭": "yes"},
        "edible_note": "后海灣水質一般。烏頭少量食用，鯛魚類可食。",
    },
    "tsim_be_tsui_west": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 后海灣",
        "edible": {"石斑": "limit", "鯛魚": "yes", "黃腲鱲": "yes", "泥鯭": "yes"},
        "edible_note": "后海灣水質一般。石斑建議少量食用，鯛魚類可食。",
    },
    "lung_kwu_tan": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 龍鼓水道，不宜游泳但可釣魚",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "石斑": "limit", "紅鮋": "limit", "烏頭": "limit"},
        "edible_note": "龍鼓水道受珠江徑流影響，水質一般。底樣魚（石斑、紅鮋）建議少量，沙鯭黃腲鱲可食。",
    },
    "tai_long_wan_west": {
        "water_quality": "excellent",
        "water_quality_zh": "極佳 — 西貢外海，水質極佳",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes"},
        "edible_note": "✅✅ 西貢外海水質極佳！石斑紅鮋全部可放心食用。原野釣點大魚鮮味極佳！",
    },
    "long_ke": {
        "water_quality": "excellent",
        "water_quality_zh": "極佳 — 西貢東面外海，水質極佳",
        "edible": {"石斑": "yes", "鯛魚": "yes", "紅鮋": "yes", "火點": "yes"},
        "edible_note": "✅✅ 西貢東面水質極佳！魚全部可放心食用。夜釣火點石斑特別好味！",
    },
    "leung_shuen_wan": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 西貢內灣，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "黃腲鱲": "yes", "烏頭": "yes"},
        "edible_note": "✅ 西貢水質好，魚可食。石斑鯛魚好味。",
    },
    "pui_o": {
        "water_quality": "moderate",
        "water_quality_zh": "一般 — 大嶼山南面海灣，近岸水質一般",
        "edible": {"沙鯭": "yes", "黃腲鱲": "yes", "烏頭": "limit"},
        "edible_note": "大嶼山南面水質一般。沙鯭黃腲鱲可食，烏頭建議少量食用。",
    },
    "ham_tin_wan": {
        "water_quality": "excellent",
        "water_quality_zh": "極佳 — 西貢外海，水質極佳",
        "edible": {"石斑": "yes", "鯛魚": "yes", "沙鯭": "yes"},
        "edible_note": "✅✅ 西貢外海水質極佳！魚全部可放心食用。沙灘魚都鮮味！",
    },
    "chek_keng": {
        "water_quality": "good",
        "water_quality_zh": "良好 — 西貢內灣，水質好",
        "edible": {"石斑": "yes", "鯛魚": "yes", "黃腲鱲": "yes"},
        "edible_note": "✅ 西貢水質好，魚可食。石斑鯛魚黃腲鱲都好味。",
    },

    "victoria_harbour": {
        "water_quality": "poor",
        "water_quality_zh": "差 — 維港中心，水質差",
        "edible": {"烏頭": "no", "黃腲鱲": "limit"},
        "edible_note": "⚠️ 維港水質差，強烈建議不食用。釣到放生。",
    },
}

if __name__ == "__main__":
    import json
    print("🚰 水質 & 食用安全資料")
    print("=" * 65)
    
    quality_order = {"excellent": 0, "good": 1, "moderate": 2, "poor": 3}
    sorted_spots = sorted(WATER_EDIBILITY.items(), key=lambda x: quality_order.get(x[1]["water_quality"], 4))
    
    for sid, data in sorted_spots:
        icons = {"excellent": "✅✅", "good": "✅", "moderate": "⚠️", "poor": "❌"}
        icon = icons.get(data["water_quality"], "❓")
        print(f"\n{icon} {sid} — {data['water_quality_zh']}")
        print(f"   可食: {', '.join([f'{k}✅' if v=='yes' else f'{k}⚠️' if v=='limit' else f'{k}❌' for k,v in data['edible'].items()])}")
        print(f"   💡 {data['edible_note']}")