"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

from pathlib import Path
import json
import shutil
import subprocess
import tempfile

from markitdown import MarkItDown


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def extract_document_text(path: Path, converter: MarkItDown) -> str:
    """Extract text directly, with OCR fallback for scanned PDFs."""
    text = converter.convert(str(path)).text_content.strip()
    if text or path.suffix.lower() != ".pdf":
        return text

    ocrmypdf = shutil.which("ocrmypdf")
    if ocrmypdf is None:
        raise RuntimeError(
            f"Không đọc được text từ {path.name} và không tìm thấy OCRmyPDF. "
            "Hãy cài bằng: brew install ocrmypdf tesseract-lang"
        )

    print(f"OCR scanned PDF: {path.name}")
    with tempfile.TemporaryDirectory(prefix="rag-ocr-") as temp_dir:
        searchable_pdf = Path(temp_dir) / path.name
        subprocess.run(
            [
                ocrmypdf,
                "--language",
                "vie+eng",
                "--rotate-pages",
                "--deskew",
                "--skip-text",
                # Only the temporary OCR copy is changed; the signed source is preserved.
                "--invalidate-digital-signatures",
                "--quiet",
                str(path),
                str(searchable_pdf),
            ],
            check=True,
        )
        return converter.convert(str(searchable_pdf)).text_content.strip()


def convert_legal_docs() -> None:
    # TODO:Convert PDF/DOCX vào standardized/legal. 
    #
    # from markitdown import MarkItDown
    # legal_dir = LANDING_DIR / "legal"
    # output_dir = OUTPUT_DIR / "legal"
    # output_dir.mkdir(parents=True, exist_ok=True)
    # converter = MarkItDown()
    # for path in legal_dir.iterdir():
    #     if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
    #         result = converter.convert(str(path))
    #         (output_dir / f"{path.stem}.md").write_text(
    #             result.text_content, encoding="utf-8"
    #         )
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()
    for path in sorted(legal_dir.glob("*")):
        if path.suffix.lower() not in {".pdf", ".doc", ".docx"}:
            continue
        text = extract_document_text(path, converter)
        if text:
            (output_dir / f"{path.stem}.md").write_text(text + "\n", encoding="utf-8")
            print(f"Converted: {path.name}")
        else:
            print(f"Skipped empty document: {path.name}")


def convert_news_articles() -> None:
    # TODO: Convert JSON vào standardized/news.
    #
    # import json
    # news_dir = LANDING_DIR / "news"
    # output_dir = OUTPUT_DIR / "news"
    # output_dir.mkdir(parents=True, exist_ok=True)
    # for path in news_dir.glob("*.json"):
    #     data = json.loads(path.read_text(encoding="utf-8"))
    #     header = (
    #         f"# {data['title']}\n\n"
    #         f"**Source:** {data['url']}\n\n"
    #         f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
    #     )
    #     (output_dir / f"{path.stem}.md").write_text(
    #         header + data["content_markdown"], encoding="utf-8"
    #     )
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        content = str(data.get("content_markdown", "")).strip()
        if not content:
            continue
        header = (f"# {data.get('title', path.stem)}\n\n"
                  f"**Source:** {data.get('url', '')}\n\n"
                  f"**Crawled:** {data.get('date_crawled', '')}\n\n---\n\n")
        (output_dir / f"{path.stem}.md").write_text(header + content + "\n", encoding="utf-8")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
