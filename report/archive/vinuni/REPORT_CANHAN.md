# Báo cáo cá nhân — Lab 7: Embedding & Vector Store

**Họ tên / mã sinh viên:** [Người học điền]

**Nhóm:** [Người học điền]

**Ngày thực nghiệm:** 19/09/2026

> Bản thực hiện có hỗ trợ của Codex, gồm code và số liệu chạy thật. Người học cần đọc, hiểu và xác nhận nội dung trước khi nộp. Phần trao đổi/thuyết trình thật của nhóm chưa diễn ra trong phiên làm việc này.

## 1. Khởi động

Cosine cao nghĩa là hai vector có hướng gần nhau. Với embedding ngữ nghĩa phù hợp, điều đó thường cho thấy nội dung gần nhau; không đồng nghĩa mọi dữ kiện giống nhau hoặc đều đúng.

- Dự kiến cao: “Sinh viên mượn sách tại thư viện.” và “Người học có thể mượn tài liệu ở thư viện.” Cùng hành động, đối tượng và bối cảnh.
- Dự kiến thấp: “Thư viện cho mượn sách.” và “Núi lửa phun trào tạo ra dung nham.” Khác chủ đề.

Cosine bỏ qua độ lớn vector, tập trung vào hướng biểu diễn. Euclid bị ảnh hưởng bởi cả độ lớn và hướng. Nếu hai vector đã chuẩn hóa đơn vị thì distance² = 2 − 2 × cosine; hai phép đo cho cùng thứ tự xếp hạng. Cosine không luôn tốt hơn Euclid trong mọi trường hợp.

### Bài toán chunking

Với 10.000 ký tự, size=500, overlap=50:

```text
bước trượt = 500 - 50 = 450
ceil((10000 - 50) / 450) = ceil(22,111...) = 23 chunk
```

Đổi overlap=100: ceil((10000 − 100)/(500 − 100)) = ceil(24,75) = **25 chunk**.

Đã đối chiếu trực tiếp bằng FixedSizeChunker trong kiểm thử. Overlap giữ thông tin qua ranh giới, nhưng tăng số vector và có thể khiến top-k chứa nhiều nội dung lặp.

## 2. Hướng tiếp cận

### Chunking

**SentenceChunker** dùng regex `(?<=[.!?])\s+`. Lookbehind giữ dấu câu; các câu được gom theo số lượng cấu hình. Text trắng trả danh sách rỗng. Hạn chế: chữ viết tắt như TS. hay v.v. có thể bị tách sai. Số thập phân dạng 3.14 không bị tách vì sau dấu chấm không có khoảng trắng.

**RecursiveChunker** ưu tiên đoạn văn → dòng → câu → từ → ký tự. Mảnh quá dài được chia tiếp; các mảnh nhỏ liên tiếp được gom lên đến giới hạn. Dừng khi text rỗng, đủ ngắn hoặc hết separator thì dùng fixed size không overlap. Giữ nguyên dấu phân cách, không làm mất nội dung.

**compute_similarity** tính dot chia tích hai norm, bảo vệ vector zero và từ chối vector khác số chiều. **ChunkingStrategyComparator** trả đúng ba khóa theo bài và thống kê count, avg_length, chunks, không chia cho 0 với text rỗng.

Chiến lược riêng chọn **HeadingChunker(300)**: giữ cả tiêu đề tài liệu và mục trên mọi mảnh con. Đổi lại, tiêu đề lặp chiếm ngân sách; cấu hình quá nhỏ để chứa tiêu đề sẽ báo lỗi.

### EmbeddingStore

Store in-memory độc lập theo hướng dẫn Codelab. Mỗi Document là một record; việc chia chunk ở tầng ingest. Metadata sao chép sâu, giữ doc_id của tài liệu gốc; nếu thiếu mới dùng Document.id.

Search nhúng câu hỏi một lần, xếp hạng theo dot product. Các embedder sẵn có chuẩn hóa vector nên dot bằng cosine; vector tự truyền chưa chuẩn hóa thì không có bảo đảm này. top_k không dương hoặc kho rỗng trả [].

Lọc metadata **trước** top-k, khớp tất cả trường. Lọc sau có thể bỏ hết kết quả dù kho còn tài liệu hợp lệ. delete_document xóa mọi chunk cùng doc_id. Lô vector sai chiều bị từ chối trước khi thêm record vào kho.

### KnowledgeBaseAgent

Lấy top-k, đánh số nguồn [1], [2]... rồi tạo prompt chứa nội dung, URL, chunk ID, audience và phiên bản. Prompt yêu cầu dựa vào bằng chứng, trích dẫn và báo thiếu thông tin. Nếu không có kết quả, không gọi LLM. Giữ nguyên answer() và thêm answer_with_filter() cho bài L3A.

Chi tiết code, luồng xử lý và cách chạy ở [GIAI_THICH.md](../../../GIAI_THICH.md).

## 3. Kết quả kiểm thử

Windows, **Python 3.11.16**, **pytest 9.1.1**. Lệnh đã chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Tóm lược output thực tế:

```text
collected 69 items
tests/test_edge_cases.py ... PASSED
tests/test_solution.py ... PASSED
69 passed in 0.36s
```

- **42/42 kiểm thử gốc đạt**; giữ nguyên tests/test_solution.py.
- **27 kiểm thử bổ sung đạt**: dấu câu, chia không mất ký tự, giới hạn kích thước, lọc trước top-k, xóa nhiều chunk, metadata bị sửa bên ngoài, vector sai chiều, nguồn trong prompt và bằng chứng đáp án.
- main.py với câu hỏi “Chunking là gì?” chạy thành công. Thông báo bỏ qua customer_support_playbook.txt là file mẫu thiếu sẵn, đã được Codelab ghi nhận.
- bench.py chạy thành công; dữ liệu đầy đủ ở [benchmark.json](benchmark.json).

## 4. Dự đoán độ tương tự

Dự đoán được lưu trong data/similarity_pairs.json trước khi chạy. Dự đoán nói về **ngữ nghĩa**, còn kết quả đo dùng **MockEmbedder**.

| Cặp | Câu A | Câu B | Dự đoán | Cosine thực tế | Đối chiếu |
|---|---|---|---|---:|---|
| 1 | Sinh viên mượn sách tại thư viện. | Sinh viên mượn sách tại thư viện. | Cao nhất | 1.0000 | Đúng, cùng chuỗi |
| 2 | Sinh viên mượn sách tại thư viện. | Người học có thể mượn tài liệu ở thư viện. | Cao | -0.0750 | Không khớp ngữ nghĩa |
| 3 | Nhóm cần đặt phòng để cùng học bài. | Các bạn đăng ký phòng học nhóm. | Cao | 0.2028 | Tương đồng không mạnh |
| 4 | Sinh viên phải gia hạn sách trước hạn trả. | Thư viện cung cấp máy in và máy quét. | Trung bình | -0.0739 | Điểm không biểu diễn ngữ nghĩa |
| 5 | Thư viện cho mượn sách. | Núi lửa phun trào tạo ra dung nham. | Thấp nhất | -0.1249 | Thấp nhất lần này, có thể ngẫu nhiên |

Cặp 2 cho thấy diễn đạt gần nghĩa vẫn có điểm âm. Mock dùng MD5 để sinh vector giả ngẫu nhiên, không học ý nghĩa. Chỉ chuỗi giống hệt mới bảo đảm cùng vector. Không dùng bảng này để kết luận về embedding thật.

## 5. Kết quả truy xuất cá nhân

Dùng HeadingChunker(300), top-k=3, tổng 11 chunk, độ dài trung bình 219,0. Bộ 5 câu hỏi trùng báo cáo nhóm và data/benchmark_queries.json. Q1 lọc audience=student.

| Câu | Top-1 chunk | Score | Đủ bằng chứng top-1 / top-3 | Ngữ cảnh Agent demo |
|---|---|---:|---|---|
| Q1: hạn mức/thời hạn mượn | student-borrowing#0 | -0.1237 | Có / Có | Đúng đối tượng và có đáp án |
| Q2: gia hạn sách sinh viên | faculty-borrowing#1 | 0.1299 | Không / Không | Nhầm ngữ cảnh giảng viên |
| Q3: đến muộn đặt phòng | faculty-borrowing#0 | 0.1140 | Không / Không | Thiếu đoạn về hủy phòng |
| Q4: đối tượng dùng khu 24/7 | room-booking#0 | 0.1587 | Không / Không | Có đúng file ở top-3 nhưng sai mục |
| Q5: thời hạn gửi Course Reserve | faculty-borrowing#1 | 0.1588 | Không / Có | Có đáp án trong course-reserve#2 ở hạng 2 |

**Đủ cụm bằng chứng top-3: 2/5; có đúng doc_id top-3: 3/5.** Top-3 đầy đủ cho mọi câu nằm trong [bảng kết quả](benchmark.md).

Agent hiện chỉ trích ngữ cảnh bằng extractive_demo, không tổng hợp đáp án bằng LLM thật. Vì vậy chưa chấm tiêu chí “agent trả lời đúng” theo rubric. Điểm âm ở Q1 không chứng minh dữ liệu sai: bộ lọc đã chọn đúng tài liệu, còn score mock không mang ngữ nghĩa.

## 6. Phân tích lỗi và bài học

**Lỗi Q4:** heading lấy hours-access#0 nói về lịch mở cửa, nhưng đáp án nằm ở mục Không gian 24/7 trong #1. Chỉ chấm doc_id sẽ báo đạt sai. Cần kiểm bằng chứng và đọc câu trả lời LLM khi có mô hình thật.

**Bộ lọc Q1:** không lọc thì heading trả top-1 faculty-borrowing#1, không đúng đối tượng. Lọc student lấy được mục hạn mức. Đây là tác dụng xác định tập ứng viên, không phải mock hiểu câu hỏi.

**Cải thiện:** chạy LocalEmbedder đa ngữ trên bộ câu hỏi giữ nguyên; phân tích lỗi theo mục; thử kích thước/overlap, lấy mục lân cận hoặc reranker. Không tăng top-k tùy tiện để che lỗi mà không đo lại nhiễu.

**Điều học từ thành viên hoặc nhóm khác:** người học bổ sung sau buổi trao đổi thật. Không suy diễn từ thực nghiệm tự động.

## 7. Tự đánh giá

Đã có code, giải thích, kiểm thử, benchmark và phân tích lỗi. Chưa tự gán điểm vì phần hiểu bài, hoạt động nhóm và chất lượng trả lời của LLM thật cần được xác nhận riêng.
