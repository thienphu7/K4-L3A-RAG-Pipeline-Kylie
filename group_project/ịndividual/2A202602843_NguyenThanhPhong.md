# Báo cáo cá nhân — Nguyễn Thanh Phong

- Mã học viên: 2A202602843
- Nhóm: K4-L3A-RAG-Pipeline-Kylie
- Branch: `main`

## Đóng góp

| Hạng mục | Kết quả |
|---|---|
| Legal data | Thu thập 6 PDF và metadata nguồn. |
| Chuẩn hoá | Chuyển 6 PDF sang Markdown. |
| OCR | Thêm fallback OCRmyPDF + Tesseract `vie+eng` cho 5 PDF scan; giữ nguyên PDF gốc có chữ ký số. |
| Evaluation | Tạo script A/B RAGAS, chạy 16 câu cho dense-only và hybrid+RRF. |

## Kết quả

- 6 Markdown legal không rỗng; 20/20 tests pass.
- Hybrid+RRF đạt average **0.820**, cao hơn dense-only **0.759**.
- Hạn chế: OCR còn nhiễu; Answer Relevance ~0.56. Cần cải thiện chunking/prompt.

## File chính

- `src/task1_collect_legal_docs.py`
- `src/task3_convert_markdown.py`
- `group_project/evaluation/run_evaluation.py`
- `group_project/evaluation/benchmark_results.json`
