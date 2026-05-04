import re


def expand_numeric_ranges(pattern: str) -> str:
    """
    Convert PoE-style stat ranges into regex alternatives.

    Example:
        +(8-10) life -> +(8|9|10) life
        +(8—10) life -> +(8|9|10) life
    """
    range_pattern = re.compile(
        r"[\(\uFF08]\s*(\d+)\s*[-\u2013\u2014]\s*(\d+)\s*[\)\uFF09]"
    )

    def replace_range(match):
        start = int(match.group(1))
        end = int(match.group(2))

        if start > end or end - start > 200:
            return match.group(0)

        return "(" + "|".join(str(value) for value in range(start, end + 1)) + ")"

    return range_pattern.sub(replace_range, pattern)


def safe_user_regex(pattern: str) -> str:
    # PoE stat lines may use normal + or full-width + in localized text.
    pattern = re.sub(
        r"(?<!\\)\+",
        lambda _match: r"[+\uFF0B]",
        pattern,
    )
    pattern = re.sub(
        r"\uFF0B",
        lambda _match: r"[+\uFF0B]",
        pattern,
    )
    return pattern


def flexible_poe_text_regex(pattern: str) -> str:
    """
    Make copied PoE stat-line matching less brittle.

    Users often paste readable stat text, while Ctrl+C output may vary around
    spaces and colon width. Preserve regex groups/operators, but make ordinary
    whitespace and ':' / full-width ':' flexible.
    """
    pattern = re.sub(
        r"[:\uFF1A]\s*",
        lambda _match: r"[:\uFF1A]\s*",
        pattern,
    )
    pattern = re.sub(r"\s+", r"\\s*", pattern)
    return pattern


def flexible_literal_text(text: str) -> str:
    escaped = re.escape(text.strip())
    return re.sub(r"\\\s+", r"\\s*", escaped)


def build_plus_range_stat_variant(pattern: str):
    text = pattern.strip()

    for separator in (":", "\uFF1A"):
        if separator in text:
            text = text.rsplit(separator, 1)[1].strip()
            break

    match = re.search(
        r"[+\uFF0B]\s*[\(\uFF08]\s*(\d+)\s*[-\u2013\u2014]\s*(\d+)\s*[\)\uFF09]\s*(.+)$",
        text,
    )

    if not match:
        return None

    start = int(match.group(1))
    end = int(match.group(2))
    stat_text = match.group(3).strip()

    if start > end or end - start > 200 or not stat_text:
        return None

    values = "|".join(str(value) for value in range(start, end + 1))
    return rf"[+\uFF0B]\s*(?:{values})\s*{flexible_literal_text(stat_text)}"


def build_flexible_pattern(pattern: str) -> str:
    variants = [pattern]

    for separator in (":", "\uFF1A"):
        if separator in pattern:
            tail = pattern.rsplit(separator, 1)[1].strip()

            if tail:
                variants.append(tail)

            break

    compiled_variants = []

    for variant in variants:
        variant = expand_numeric_ranges(variant)
        variant = safe_user_regex(variant)
        variant = flexible_poe_text_regex(variant)
        compiled_variants.append(f"(?:{variant})")

    plus_range_variant = build_plus_range_stat_variant(pattern)

    if plus_range_variant:
        compiled_variants.append(f"(?:{plus_range_variant})")

    return "|".join(compiled_variants)


def clean_poe_regex(text: str) -> str:
    """
    Cleans PoE-style stash regex input.

    Examples:
        "!f ph"  -> f ph
        !ilm     -> ilm

    The leading ! means "not" in PoE stash search.
    In this program, map avoid regex already means "reject if matched",
    so we remove the leading !.
    """
    text = text.strip()

    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1].strip()

    if text.startswith("!"):
        text = text[1:].strip()

    return text


def compile_regex(pattern: str, label: str = "regex"):
    """
    Returns compiled regex or raises ValueError with a readable message.
    """
    pattern = pattern.strip()

    if not pattern:
        return None

    pattern = build_flexible_pattern(pattern)

    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise ValueError(f"Invalid {label}: {e}")
