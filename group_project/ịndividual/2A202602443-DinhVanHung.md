# Individual contribution report

## Thông tin

- Họ và tên: Đinh Văn Hùng
- Mã học viên: 2A202602443
- Nhóm: K4-L3A-RAG-Pipeline
- Vai trò: Nhóm trưởng
- Repository/branch: K4-L3A-RAG-Pipeline-Kylie / main

## Thành viên nhóm

| Họ và tên | Mã học viên | Vai trò |
|---|---|---|
| Đinh Văn Hùng | 2A202602443 | Nhóm trưởng |
| Nguyễn Thanh Phong | 2A202602843 | Thành viên |
| Lê Hoàng Thiên Phú | 2A202602908 | Thành viên |

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Chuẩn hóa dữ liệu | Hoàn thiện chuyển PDF/DOCX và JSON article sang Markdown, bỏ qua file rỗng | `src/task3_convert_markdown.py` | Done |
| Chunking và indexing | Hoàn thiện đọc tài liệu, chunk ổn định, embedding và upsert ChromaDB | `src/task4_chunking_indexing.py` | Done |
| Hybrid retrieval | Hoàn thiện dense search, BM25 và RRF | `src/task5_semantic_search.py`, `src/task6_lexical_search.py`, `src/task7_reranking.py` | Done |
| Retrieval fallback | Hoàn thiện threshold theo dense cosine score và fallback an toàn | `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| Generation và UI | Hoàn thiện gọi LLM, safe refusal, context formatting, citation source và hiển thị nguồn | `src/task10_generation.py`, `app.py` | Done |
| Quy chuẩn báo cáo | Cập nhật quy chuẩn tên repository và báo cáo cá nhân | `README.md`, `group_project/ịndividual/INDIVIDUAL_REPORT.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Dùng cùng embedding function cho indexing và semantic search.**  
   **Lý do/evidence:** Task 4 và Task 5 dùng chung `embed_texts()`, giúp vector của document và query cùng dimension/model.  
   **Trade-off:** Embedding local có thể cần tải model và tốn tài nguyên; embedding API dễ triển khai hơn nhưng phát sinh chi phí.

2. **Dùng dense cosine score gốc để quyết định fallback, không dùng RRF score.**  
   **Lý do/evidence:** Cosine score phản ánh độ tương đồng còn RRF chỉ phản ánh thứ hạng, đúng theo `docs/MODULE_CONTRACTS.md`.  
   **Trade-off:** Cần hiệu chỉnh threshold theo corpus thực tế; PageIndex chỉ hoạt động khi được cấu hình provider.

## Kiểm thử và kết quả

- Đã chạy `pytest tests/test_contracts.py -q`: 15 tests passed.
- Đã chạy `pytest tests/test_acceptance.py -q`: 5 tests passed sau khi hoàn thiện corpus và golden dataset.
- Đã kiểm tra compile toàn bộ `src/` và `app.py`, cùng `git diff --check`.
- Dữ liệu corpus gồm 6 legal Markdown và 5 news Markdown; golden dataset gồm 15 cases.

## Điều còn hạn chế

- Một số đoạn PDF scan còn nhiễu OCR, đặc biệt ở bảng và biểu mẫu.
- PageIndex mới có cơ chế opt-in an toàn, chưa tích hợp API thật.
- Các metric RAGAS chưa được chạy tự động; báo cáo hiện ghi N/A thay vì bịa số liệu.
- Nếu có thêm thời gian, ưu tiên làm sạch OCR, chạy benchmark A/B và hiệu chỉnh fallback threshold.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh phần việc đã thực hiện và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/09/2026
- Tên thành viên: Đinh Văn Hùng
