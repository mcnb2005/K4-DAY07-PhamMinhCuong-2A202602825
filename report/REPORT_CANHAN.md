# Báo cáo cá nhân — Lab 7: Embedding & Vector Store

**Họ tên / mã sinh viên:** Phạm Minh Cương - 2A202602825

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

Chi tiết code, luồng xử lý và cách chạy ở [GIAI_THICH.md](../GIAI_THICH.md).

## 3. Kết quả kiểm thử

Windows, **Python 3.11.16**, **pytest 9.1.1**. Lệnh đã chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Tóm lược output thực tế:

```text
collected 77 items
tests/test_benchmark_datasets.py ... PASSED
tests/test_edge_cases.py ... PASSED
tests/test_solution.py ... PASSED
77 passed in 0.34s
```

- **42/42 kiểm thử gốc đạt**; giữ nguyên tests/test_solution.py.
- **35 kiểm thử bổ sung đạt**: dấu câu, chia không mất ký tự, giới hạn kích thước, lọc trước top-k, xóa nhiều chunk, metadata bị sửa bên ngoài, vector sai chiều, nguồn trong prompt và bằng chứng đáp án.
- main.py với câu hỏi “Chunking là gì?” chạy thành công. Thông báo bỏ qua customer_support_playbook.txt là file mẫu thiếu sẵn, đã được Codelab ghi nhận.
- bench.py chạy thành công; dữ liệu đầy đủ ở [benchmark.json](results/benchmark.json).

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

## 5. Kết quả truy xuất trên bộ đã chọn

Theo yêu cầu mới, dùng **UIT + Thư viện Trung tâm + KTX ĐHQG-HCM**, không dùng corpus VinUni trong lượt benchmark này. Có 7 bản tóm lược nguồn chính thức, 6 chủ đề và 5 câu hỏi mới trong data/uit-vnuhcm-queries.json. Danh mục và gold answer đầy đủ ở [báo cáo nhóm](REPORT_NHOM.md).

HeadingChunker(300), top-k=3: **23 chunk**, độ dài trung bình **221,1**. Q1 có bộ lọc audience=student. Các kết quả khác chỉ dùng câu hỏi, không tự thêm bộ lọc để nâng điểm.

| Câu | Câu hỏi | Top-1 | Score | Đủ bằng chứng top-1 / top-3 |
|---|---|---|---:|---|
| Q1 | Ở UIT, tôi cần làm gì để yêu cầu phúc khảo và nhận kết quả bằng cách nào? | ktx-gia-han-2026-2027#2 | 0.2239 | Không / Không |
| Q2 | Hạn đóng học phí học kỳ hè 2025-2026 của UIT là ngày nào? | uit-dang-ky-hoc-phan#2 | 0.3882 | Không / Không |
| Q3 | Theo quy định UIT Global có hiệu lực từ 01/09/2026, sinh viên được nộp chứng chỉ xét học bổng trong những học kỳ nào? | ktx-gia-han-2026-2027#0 | 0.2712 | Không / Có |
| Q4 | Sinh viên chính quy thuộc ĐHQG-HCM được mượn bao nhiêu tài liệu tại Thư viện Trung tâm, trong bao lâu và gia hạn thế nào? | uit-dang-ky-hoc-phan#0 | 0.2662 | Không / Không |
| Q5 | Sinh viên đang ở KTX ĐHQG-HCM gia hạn năm 2026-2027 phải thanh toán trong bao lâu sau khi hồ sơ được duyệt? | uit-hoc-bong-global-2026#0 | 0.2279 | Không / Có |

**Đúng nguồn top-3: 2/5. Đủ bằng chứng top-3: 2/5** (Q3 học bổng và Q5 KTX). Không có câu nào đủ bằng chứng ở top-1 trong cấu hình này. Agent demo trích chính các chunk; không phải câu trả lời được LLM tổng hợp hoặc chấm đúng/sai tự động.

### Bằng chứng trong corpus trước khi tìm kiếm

Các chunk heading có thông tin để trả lời (không có nghĩa chúng đã được retrieve):

- Q1: uit-phuc-khao-sinh-vien#0, uit-phuc-khao-sinh-vien#1.
- Q2: uit-hoc-phi-he-2025-2026#1.
- Q3: uit-hoc-bong-global-2026#2.
- Q4: vnulib-muon-tra#1.
- Q5: ktx-gia-han-2026-2027#2.

Q1 cần nhiều đoạn để đủ quy trình; việc chỉ lấy đoạn về kết quả sẽ thiếu cách gửi yêu cầu. Xem [benchmark.md](results/benchmark.md) và [benchmark.json](results/benchmark.json) để đối chiếu các đoạn thực tế.

## 6. Phân tích lỗi

**Q1:** metadata student loại được quy trình faculty khỏi top-3 của heading, nhưng top-3 còn lại vẫn thuộc KTX/học bổng. Bộ lọc đúng đối tượng không thay thế việc hiểu câu hỏi. Không tuyên bố bộ lọc làm câu trả lời đúng trong lần chạy này.

**Q3 với fixed size:** đúng nguồn học bổng trong top-3 nhưng sai đoạn; thiếu những mốc cần cho gold answer. Đây là trường hợp source hit thổi phồng kết quả so với evidence hit.

**Q2:** cần giữ chính xác kỳ hè 2025-2026 khi hỏi hạn học phí. Metadata university/institution/category và academic_year giúp nhận diện phạm vi. Không dùng ngày lấy nguồn như ngày hiệu lực.

**Cải thiện:** dùng LocalEmbedder đa ngữ rồi chạy lại cùng bộ dữ liệu; kiểm tra ngữ cảnh và cân nhắc lọc category theo yêu cầu hoặc lấy mục lân cận. Không đổi câu hỏi theo score của mock để tạo kết quả đẹp. Các cặp cosine phần 4 giữ nguyên để có đối chiếu giữa hai corpus; chúng không phụ thuộc vào corpus.

**Điều học từ thành viên/nhóm khác:** người học bổ sung sau hoạt động thật; phiên này chỉ có thực nghiệm tự động.

## 7. Tự đánh giá

Đã có code, kiểm thử, bộ dữ liệu đã chọn, benchmark mới và phân tích lỗi. Không tự gán điểm cho chất lượng mô hình thật hay hoạt động nhóm chưa diễn ra. Hướng dẫn chạy tại [GIAI_THICH.md](../GIAI_THICH.md); kết quả VinUni cũ giữ riêng trong archive/vinuni để truy vết thay đổi.
