import re


def normalize_text(text: str) -> str:
    """
    Normalize copied item text while preserving newlines.
    Important: do not remove newlines, because PoE-style regex may use $.
    """
    return text.replace("：", ":")


def extract_item_name(text: str) -> str:
    """
    Language-independent item name extraction.
    It looks for the first colon line, usually:
        Rarity:
        稀 有 度:
        Rareté:
    Then captures lines until the first separator.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        if ":" in line:
            name_lines = []

            for j in range(i + 1, len(lines)):
                if lines[j] == "--------":
                    break
                name_lines.append(lines[j])

            return " ".join(name_lines)

    return ""


def extract_value(pattern: str, text: str) -> int:
    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def parse_map_stats(text):
    text = text.replace("：", ":")

    return {
        "quantity": extract_value(
            r"(?:Item Quantity|物品数量|物品數量):\s*\+(\d+)%", text
        ),

        "rarity": extract_value(
            r"(?:Item Rarity|物品稀有度):\s*\+(\d+)%", text
        ),

        "pack_size": extract_value(
            r"(?:Monster Pack Size|怪物群大小):\s*\+(\d+)%", text
        ),

        "more_maps": extract_value(
            r"(?:More Maps|更多地图|地圖增加):\s*\+(\d+)%", text
        ),

        "currency": extract_value(
            r"(?:More Currency|更多通货|通貨增加):\s*\+(\d+)%", text
        ),

        "scarabs": extract_value(
            r"(?:More Scarabs|更多圣甲虫|聖甲蟲增加):\s*\+(\d+)%", text
        ),

        "divination": extract_value(
            r"(?:More Divination Cards|更多命运卡|更多命运卡牌|命運卡增加):\s*\+(\d+)%", text
        ),
    }


def read_int_or_none(value: str):
    value = value.strip()
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def map_passes_thresholds(stats: dict, thresholds: dict) -> bool:
    """
    Current logic:
    - Empty input means ignore that field.
    - If any filled threshold is reached, the map passes.
    - If no thresholds are filled, it does not pass.
    """
    has_any_threshold = False

    for key, required in thresholds.items():
        if required is None:
            continue

        has_any_threshold = True

        if stats.get(key, 0) >= required:
            return True

    return False if has_any_threshold else False
