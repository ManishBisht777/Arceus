import re


def generate_branch_keyword(summary: str) -> str:
    words = re.findall(
        r"[a-zA-Z0-9]+",
        summary.lower(),
    )

    stop_words = {
        "the",
        "a",
        "an",
        "to",
        "for",
        "in",
        "on",
        "of",
        "and",
        "with",
        "is",
        "fix",
        "update",
        "add",
        "change",
    }

    meaningful_words = [
        word
        for word in words
        if word not in stop_words
    ]

    if not meaningful_words:
        return "fix"

    return meaningful_words[0]