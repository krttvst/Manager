import re
import httpx
from bs4 import BeautifulSoup


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    text = " ".join(soup.stripped_strings)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_and_extract(url: str, timeout: int = 10) -> str:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return extract_text_from_html(response.text)
