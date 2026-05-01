import re


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

    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise ValueError(f"Invalid {label}: {e}")
