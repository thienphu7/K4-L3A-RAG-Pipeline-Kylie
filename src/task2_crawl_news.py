"""Task 2 - crawl articles related to the legal documents from phapluat.gov.vn."""

from __future__ import annotations

import asyncio
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

# Every article cites, explains, or discusses at least one Task 1 document.
# ``related_documents`` makes that relationship auditable.
ARTICLE_SOURCES = [
    {
        "url": "https://phapluat.gov.vn/tin-tuc/quy-dinh-bat-buoc-ve-thiet-bi-an-toan-cho-tre-em-tren-o-to-tu-1-7",
        "related_documents": ["36/2024/QH15", "168/2024/NĐ-CP", "238/2026/NĐ-CP"],
    },
    {
        "url": "https://phapluat.gov.vn/tin-tuc/chinh-sach-moi/tu-15-8-phat-canh-cao-o-to-cho-tre-em-khong-co-thiet-bi-an-toan-phu-hop",
        "related_documents": ["36/2024/QH15", "168/2024/NĐ-CP", "238/2026/NĐ-CP"],
    },
    {
        "url": "https://phapluat.gov.vn/tin-tuc/sua-doi-bo-sung-mot-so-quy-dinh-ve-trat-tu-an-toan-giao-thong-duong-bo",
        "related_documents": ["36/2024/QH15", "151/2024/NĐ-CP", "236/2026/NĐ-CP"],
    },
    {
        "url": "https://phapluat.gov.vn/tin-tuc/chinh-sach-moi/de-xuat-thay-doi-cach-tra-cuu-phat-nguoi-1878",
        "related_documents": ["36/2024/QH15", "168/2024/NĐ-CP"],
    },
    {
        "url": "https://phapluat.gov.vn/tin-tuc/sua-doi-mot-so-quy-dinh-ve-duong-quoc-lo-tram-dung-nghi",
        "related_documents": ["36/2024/QH15", "241/2026/NĐ-CP"],
    },
]

ARTICLE_URLS = [item["url"] for item in ARTICLE_SOURCES]
RELATED_DOCUMENTS = {
    item["url"]: item["related_documents"] for item in ARTICLE_SOURCES
}


def _slug_from_url(url: str) -> str:
    slug = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
    slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")


def _markdown_text(markdown: object) -> str:
    """Support string and MarkdownGenerationResult in Crawl4AI 0.9.x."""
    if isinstance(markdown, str):
        return markdown.strip()
    for attribute in ("fit_markdown", "raw_markdown"):
        value = getattr(markdown, attribute, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return str(markdown or "").strip()


def _article_only(content: str, title: str) -> str:
    """Remove the portal navigation and footer from Crawl4AI output."""
    clean_title = title.split(" - Cổng Pháp luật", 1)[0].strip()
    start = content.find(f"\n{clean_title}\n")
    if start >= 0:
        content = content[start + 1 :]
    end = content.find("[Xem tất cả tin tức]")
    if end >= 0:
        content = content[:end]
    return content.strip()


async def crawl_article(url: str) -> dict:
    """Crawl one public article and return the required metadata schema."""
    if urlparse(url).netloc.lower() != "phapluat.gov.vn":
        raise ValueError(f"Only phapluat.gov.vn article URLs are allowed: {url}")

    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(url=url)

    if not getattr(result, "success", True):
        raise RuntimeError(getattr(result, "error_message", "Crawl failed"))

    metadata = getattr(result, "metadata", {}) or {}
    title = str(metadata.get("title") or _slug_from_url(url).replace("-", " ")).strip()
    title = title.split(" - Cổng Pháp luật", 1)[0].strip()
    content = _article_only(_markdown_text(getattr(result, "markdown", "")), title)
    if len(content) < 200:
        raise ValueError(f"Article content is too short ({len(content)} chars): {url}")

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": content,
        "related_documents": RELATED_DOCUMENTS[url],
    }


async def crawl_all() -> None:
    """Crawl all configured articles into stable, rerunnable JSON files."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    for source in ARTICLE_SOURCES:
        url = source["url"]
        try:
            article = None
            last_error: Exception | None = None
            for attempt in range(1, 4):
                try:
                    article = await crawl_article(url)
                    break
                except Exception as error:
                    last_error = error
                    print(f"Retry {attempt}/3: {url} ({type(error).__name__})")
            if article is None:
                raise RuntimeError("Crawl failed after 3 attempts") from last_error

            output = DATA_DIR / f"{_slug_from_url(url)}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output.name}")
        except Exception as error:
            failures.append(f"{url}: {error}")
            print(f"Failed: {url} ({type(error).__name__})")

    if failures:
        raise RuntimeError("Some articles failed to crawl:\n" + "\n".join(failures))


if __name__ == "__main__":
    asyncio.run(crawl_all())
