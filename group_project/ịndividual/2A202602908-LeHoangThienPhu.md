# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Lê Hoàng Thiên Phú
- Mã học viên: 2A202602908
- Nhóm: K4-L3A-RAG-Pipeline-Kylie
- Repository/branch: `main` — `https://github.com/thienphu7/K4-L3A-RAG-Pipeline-Kylie`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Xác định domain và phạm vi corpus | Chọn domain pháp luật về trật tự, an toàn giao thông đường bộ Việt Nam; giới hạn corpus vào Luật 36/2024/QH15, các nghị định hướng dẫn/sửa đổi và bài viết pháp luật có quan hệ trực tiếp với các văn bản này. | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py`, commit `9fa2aba` | Done |
| Thu thập dữ liệu nền | Thu thập 6 văn bản pháp luật, 5 bài viết liên quan; lưu metadata gồm URL, tiêu đề, ngày crawl và nội dung Markdown để bảo đảm truy xuất nguồn gốc. | `data/landing/legal/`, `data/landing/news/`, `data/landing/legal/sources.json`, commit `9fa2aba` | Done |
| Demo Streamlit theo domain | Thiết kế lại giao diện để thể hiện rõ domain, phạm vi corpus, cấu hình LLM/embedding/chunking, hybrid retrieval, RRF, fallback, latency và evidence thực tế được đưa vào LLM. | `app.py` | Done |
| Bộ kịch bản demo một-click | Soạn prompt có sẵn gồm happy path, truy vấn số hiệu, tổng hợp nhiều nguồn, câu mơ hồ, tiền đề sai, ngoài domain, prompt injection và yêu cầu khẳng định quá mức. | `src/demo_config.py`, `tests/test_demo_config.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Chọn domain hẹp và có liên kết pháp lý: trật tự, an toàn giao thông đường bộ.**

   **Lý do/evidence:** Domain có một văn bản lõi là Luật 36/2024/QH15, các nghị định quy định chi tiết hoặc sửa đổi (151, 168, 236, 238 và 241) và các bài viết trên Cổng Pháp luật quốc gia giải thích chính sách tương ứng. Cấu trúc này tạo được cả câu hỏi tra cứu điều khoản chính xác lẫn câu hỏi tổng hợp thay đổi giữa văn bản gốc và văn bản sửa đổi. Corpus thực tế đạt 6 legal documents và 5 news articles, vượt yêu cầu tối thiểu 3/5 của LAB; toàn bộ được ghi nhận trong commit `9fa2aba`.

   **Trade-off:** Corpus nhất quán và dễ đánh giá grounding nhưng phạm vi hẹp, vì vậy hệ thống phải từ chối câu hỏi thuộc đất đai, thuế hoặc lĩnh vực khác. Văn bản pháp luật có tính thời điểm và quan hệ sửa đổi phức tạp; PDF ký số dạng scan còn gây nhiễu OCR nên citation và ngày hiệu lực phải được kiểm tra kỹ.

2. **Biến Streamlit demo thành giao diện giải thích được RAG, không chỉ là một ô chat.**

   **Lý do/evidence:** Demo hiển thị domain, số lượng tài liệu, model/provider đang chạy, chunk size/overlap, Chroma cosine, BM25, RRF `k=60`, PageIndex fallback và workflow sáu bước. Mỗi kết quả cho phép mở evidence, xem chunk, nguồn, retriever và score; UI giải thích rõ RRF `0,0164` là điểm thứ hạng chứ không phải xác suất đúng. Bộ 8 prompt một-click buộc hệ thống thể hiện cả khả năng trả lời có căn cứ và safe refusal thay vì chỉ trình diễn happy case.

   **Trade-off:** Giao diện giàu thông tin giúp giảng viên kiểm chứng pipeline nhưng nhiều chi tiết hơn chatbot thông thường. Việc mở nội dung chunk cũng làm màn hình dài; các kịch bản negative hiện kiểm tra hành vi mong đợi ở mức demo, chưa thay thế benchmark tự động về faithfulness và answer correctness.

## Kiểm thử và kết quả

- **Test đã dùng:** `pytest -q`; `pytest tests/test_demo_config.py tests/test_contracts.py -q`; kiểm tra tải ứng dụng bằng `streamlit.testing.v1.AppTest`.
- **Kết quả:** 22 test toàn repo đạt; 17 test demo/contract đạt sau lần chỉnh UI cuối; AppTest nhận đủ 3 tab, 14 nút, 14 expander và không có exception.
- **Các query tiêu biểu:** ngày áp dụng thiết bị an toàn trẻ em; phạm vi Nghị định 151; so sánh Nghị định 168 và 238; “Mức phạt là bao nhiêu?”; câu hỏi sổ đỏ; prompt yêu cầu bỏ qua nguồn.
- **Lỗi đã phát hiện và cách xử lý:** UI cũ chỉ hiển thị score nhỏ như `0,0164`, dễ bị hiểu là độ tin cậy thấp. Demo mới gắn nhãn RRF, giải thích công thức/xấp xỉ điểm, đồng thời cho mở evidence để đánh giá chất lượng bằng nội dung thay vì nhìn trị số tuyệt đối.

## Điều còn hạn chế

- Corpus chưa bao phủ toàn bộ pháp luật giao thông và có thể lỗi thời khi văn bản mới sửa đổi hoặc thay thế; một số văn bản scan còn nhiễu OCR.
- Bộ prompt demo mới xác nhận độ phủ tình huống và khả năng chạy UI, chưa tự động chấm đúng/sai câu trả lời của LLM.
- Nếu có thêm thời gian, tôi sẽ ưu tiên bổ sung kiểm tra phiên bản/hiệu lực văn bản và biến các prompt negative thành regression test có tiêu chí pass/fail định lượng.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc đã thực hiện và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/9/2026
- Tên thành viên: Lê Hoàng Thiên Phú
