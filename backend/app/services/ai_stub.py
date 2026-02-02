import re


def summarize_text(text: str, max_chars: int = 1200) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    # naive summary: first sentences until max_chars
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) + 1 > max_chars:
            break
        summary = f"{summary} {sentence}".strip()
    return summary or text[:max_chars]


def generate_title(text: str) -> str:
    if not text:
        return "Черновик"
    title = text.split(".", 1)[0]
    return title[:80]
