# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Nguyễn Thanh Phong
- Mã học viên: 2A202602843
- Nhóm: K4-L3A-RAG-Pipeline-Kylie
- Repository/branch: `main` — `https://github.com/thienphu7/K4-L3A-RAG-Pipeline-Kylie`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit | Trạng thái |
| --- | --- | --- | --- |
| Thu thập dữ liệu pháp lý | Xây dựng tập dữ liệu về trật tự, an toàn giao thông đường bộ từ nguồn Chính phủ; lưu 6 PDF và metadata nguồn để truy xuất xuất xứ. | `src/task1_collect_legal_docs.py`, `data/landing/legal/sources.json` | Done |
| Chuẩn hoá dữ liệu pháp lý | Chuyển 6 PDF pháp lý sang Markdown trong `data/standardized/legal/` để dùng cho bước chunking và indexing. | `src/task3_convert_markdown.py`, `data/standardized/legal/` | Done |
| OCR cho PDF scan | Phát hiện 5 PDF có chữ ký số/không có text layer. Bổ sung OCRmyPDF + Tesseract (`vie+eng`) làm fallback khi MarkItDown không trích xuất được text. | `src/task3_convert_markdown.py`, commit `6cfa698` | Done |

## Quyết định kỹ thuật quan trọng

1. **Ưu tiên MarkItDown, chỉ gọi OCR khi cần.**

   **Lý do/evidence:** Một PDF có text layer và được MarkItDown đọc trực tiếp; 5 PDF scan trả về nội dung rỗng.

   **Trade-off:** Giảm thời gian xử lý cho PDF có text, nhưng các PDF scan vẫn cần thời gian OCR.

2. **OCR trên bản sao tạm, không thay đổi PDF gốc.**

   **Lý do/evidence:** Các PDF scan có chữ ký số; OCR sẽ tạo một bản PDF mới và làm chữ ký trên bản sao mất hiệu lực.

   **Trade-off:** Tốn thêm dung lượng/thời gian tạm thời, đổi lại giữ nguyên tài liệu nguồn và tính truy xuất.

## Kiểm thử và kết quả

- Đã chạy: `python -m src.task3_convert_markdown`.
- Kết quả: tạo đủ 6 file Markdown pháp lý, tất cả đều không rỗng (tổng khoảng 885 KB).
- Đã chạy acceptance test: 3 test liên quan dữ liệu/chuẩn hoá đạt. Hai test đánh giá chưa đạt do `golden_dataset.json` đang rỗng và `reports/RESULT.md` còn `TODO`, không thuộc phần chuẩn hoá dữ liệu.

## Điều còn hạn chế

- OCR từ bản scan vẫn có thể sai một số ký tự tiếng Việt, đặc biệt ở khu vực con dấu hoặc chữ có chất lượng ảnh thấp.
- Thay đổi ưu tiên tiếp theo: rà soát chất lượng Markdown OCR trước khi đưa vào chunking/indexing; bổ sung các phần đóng góp khác sau khi hoàn thành.

## Phần sẽ cập nhật tiếp

- [ ] Bổ sung họ tên và mã học viên.
- [ ] Ghi nhận phần việc tiếp theo (Task 4–10 hoặc evaluation) khi hoàn thành.
- [ ] Cập nhật kết quả test/evaluation cuối cùng trước khi nộp.
