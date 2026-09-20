"""Task 1 - collect the legal documents used by the RAG corpus.

Topic: road traffic order and safety in Vietnam.

The National Legal Portal links to the National Legal Database (vbpl.vn). The
download URLs below use the official Government document store so the files
are stable, public, and machine-readable.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
MANIFEST_PATH = DATA_DIR / "sources.json"

DOCUMENT_SOURCES = [
    {
        "filename": "luat-36-2024-qh15-trat-tu-an-toan-giao-thong.pdf",
        "document_number": "36/2024/QH15",
        "title": "Luật Trật tự, an toàn giao thông đường bộ",
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/36-2024-qh15.pdf",
        "reference_url": "https://phapluat.gov.vn/he-thong-van-ban-phap-luat",
    },
    {
        "filename": "nghi-dinh-151-2024-nd-cp.pdf",
        "document_number": "151/2024/NĐ-CP",
        "title": "Quy định chi tiết một số điều và biện pháp thi hành Luật Trật tự, an toàn giao thông đường bộ",
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/12/151-cp.signed.pdf",
        "reference_url": "https://phapluat.gov.vn/he-thong-van-ban-phap-luat",
    },
    {
        "filename": "nghi-dinh-168-2024-nd-cp.pdf",
        "document_number": "168/2024/NĐ-CP",
        "title": "Xử phạt vi phạm hành chính về trật tự, an toàn giao thông đường bộ; trừ điểm, phục hồi điểm giấy phép lái xe",
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/01/168-nd-cp.signed.pdf",
        "reference_url": "https://phapluat.gov.vn/he-thong-van-ban-phap-luat",
    },
    {
        "filename": "nghi-dinh-236-2026-nd-cp.pdf",
        "document_number": "236/2026/NĐ-CP",
        "title": "Sửa đổi quy định chi tiết thi hành Luật Trật tự, an toàn giao thông đường bộ",
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/6/236-ndcp.signed.pdf",
        "reference_url": "https://phapluat.gov.vn/tin-tuc/sua-doi-bo-sung-mot-so-quy-dinh-ve-trat-tu-an-toan-giao-thong-duong-bo",
    },
    {
        "filename": "nghi-dinh-238-2026-nd-cp.pdf",
        "document_number": "238/2026/NĐ-CP",
        "title": "Sửa đổi Nghị định 168/2024/NĐ-CP về xử phạt giao thông đường bộ",
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/7/238-ndcp.signed.pdf",
        "reference_url": "https://phapluat.gov.vn/tin-tuc/chinh-sach-moi/tu-15-8-phat-canh-cao-o-to-cho-tre-em-khong-co-thiet-bi-an-toan-phu-hop",
    },
    {
        "filename": "nghi-dinh-241-2026-nd-cp.pdf",
        "document_number": "241/2026/NĐ-CP",
        "title": "Sửa đổi quy định về đường quốc lộ và trạm dừng nghỉ",
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/7/241-ndcp.signed.pdf",
        "reference_url": "https://phapluat.gov.vn/tin-tuc/sua-doi-mot-so-quy-dinh-ve-duong-quoc-lo-tram-dung-nghi",
    },
]


def setup_directory() -> None:
    """Create the landing directory for original legal documents."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def _is_valid_pdf(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size <= 1024:
        return False
    with path.open("rb") as file:
        return file.read(5) == b"%PDF-"


def download_documents() -> None:
    """Download the three official documents and record their provenance."""
    setup_directory()
    headers = {"User-Agent": "K4-L3A-RAG-Lab/1.0 (educational corpus)"}

    for source in DOCUMENT_SOURCES:
        output = DATA_DIR / source["filename"]
        if _is_valid_pdf(output):
            print(f"Exists: {output.name}")
            continue

        response = requests.get(source["url"], headers=headers, timeout=90)
        response.raise_for_status()
        content = response.content
        if len(content) <= 1024 or not content.startswith(b"%PDF-"):
            raise ValueError(f"Downloaded content is not a valid PDF: {source['url']}")

        output.write_bytes(content)
        print(f"Saved: {output.name} ({len(content):,} bytes)")

    MANIFEST_PATH.write_text(
        json.dumps(DOCUMENT_SOURCES, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved provenance: {MANIFEST_PATH.name}")


if __name__ == "__main__":
    download_documents()
