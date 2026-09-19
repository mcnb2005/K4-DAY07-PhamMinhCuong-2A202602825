# Báo cáo nhóm — Lab 7: Dịch vụ thư viện VinUni

**Nhóm / thành viên:** [Người học điền]

**Ngày thực nghiệm:** 19/09/2026

> Bản tổng hợp kỹ thuật có hỗ trợ của Codex, chạy bốn cấu hình để chuẩn bị so sánh nhóm. Không giả định đã có bốn thành viên hoặc đã thuyết trình. Nhóm cần xác nhận câu hỏi, phân công chiến lược và bổ sung trao đổi thực tế.

## 1. Bộ tài liệu

Chủ đề **dịch vụ và quy định thư viện đại học** phù hợp L3A: có thông tin định lượng, đối tượng khác nhau và cấu trúc theo mục. Corpus gồm 5 bản tóm lược tiếng Việt từ 5 trang chính thức, không phải bản dịch chính thức hay toàn bộ quy định.

| doc_id | Nguồn | Phiên bản | Ký tự phần thân | audience / category |
|---|---|---|---:|---|
| student-borrowing | [Undergraduate students and staff](https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/) | not-stated | 390 | student / borrowing |
| faculty-borrowing | [Library Access & Services Policy](https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/) | POL-LLR-001-V4.0, 09/07/2025 | 432 | faculty / borrowing |
| course-reserve | [Course Reserve](https://library.vinuni.edu.vn/course-reserve/) | not-stated | 493 | faculty / course-reserve |
| room-booking | [Room booking](https://library.vinuni.edu.vn/room-booking/) | not-stated | 456 | all / study-space |
| hours-access | [Hours and access](https://library.vinuni.edu.vn/about-us/hours-and-access/) | not-stated | 437 | all / opening-hours |

Mọi tài liệu có retrieved_at=2026-09-19, department=library, language=vi. Danh sách một-một với file nằm trong [sources.csv](../../../data/vinuni-library/sources.csv). Không dùng file mẫu có URL example.edu trong benchmark.

- Nguồn được đọc qua công cụ web và tóm lược; không chạy crawler toàn website.
- Không có dữ liệu cá nhân, tài khoản hay nội dung sau đăng nhập.
- Không tự bịa phiên bản/ngày hiệu lực. Ngày lấy khác ngày ban hành.
- audience mô tả phạm vi bản tóm lược: trang có thể phục vụ nhiều nhóm nhưng file chỉ chọn phần của một nhóm.
- Chi tiết giới hạn quyền crawl và khác biệt giữa các trang ở [CORPUS_NOTES.md](../../../docs/CORPUS_NOTES.md).

### Metadata

| Trường | Kiểu | Vai trò |
|---|---|---|
| doc_id | string | Nhóm chunk theo tài liệu gốc, truy vết và xóa |
| title | string | Tên dễ đọc |
| audience | string | student, faculty, all |
| department / category / language | string | Lọc đơn vị, dịch vụ, ngôn ngữ |
| source_url | string | Nguồn để kiểm chứng |
| retrieved_at | string ngày ISO | Ngày đọc |
| document_version | string | Phiên bản nguồn hoặc not-stated |
| content_type | string | Nhận biết bản tóm lược học tập |
| chunk_index | integer | Vị trí chunk, bổ sung khi ingest |

Front matter được đưa vào metadata, không trộn URL/ngày vào nội dung embedding. ID chunk dạng doc_id#0 khác metadata.doc_id của tài liệu nguồn.

## 2. Thiết kế chiến lược

### Baseline

Comparator size=200; fixed overlap=50, sentence 3 câu/chunk:

| Tài liệu | Chiến lược | Số chunk | Độ dài TB |
|---|---|---:|---:|
| course-reserve | fixed_size | 3 | 197.7 |
| course-reserve | by_sentences | 2 | 245.5 |
| course-reserve | recursive | 4 | 123.2 |
| faculty-borrowing | fixed_size | 3 | 177.3 |
| faculty-borrowing | by_sentences | 2 | 215.0 |
| faculty-borrowing | recursive | 3 | 144.0 |
| hours-access | fixed_size | 3 | 179.0 |
| hours-access | by_sentences | 2 | 217.5 |
| hours-access | recursive | 3 | 145.7 |

Sentence không giới hạn ký tự nên có thể vượt 200. Fixed có thể cắt ngang từ/câu. Recursive giữ ranh giới lớn khi có thể, nhưng không bảo đảm trọn mục.

### Cấu hình chung cho benchmark

Giữ nguyên corpus, 5 query, embedder và top-k=3; thay chiến lược:

| Cấu hình | Tham số | Điểm mạnh | Điểm yếu |
|---|---|---|---|
| A: fixed_size | size=300, overlap=50 | Độ dài dễ kiểm soát; ngữ cảnh lặp | Cắt ngang ý, trùng nội dung |
| B: by_sentences | 2 câu/chunk | Giữ dấu câu, câu trọn vẹn | Regex chưa hiểu viết tắt; độ dài biến động |
| C: recursive | size=300 | Thích ứng đoạn/dòng/câu/từ | Chunk con có thể thiếu tiêu đề |
| D: heading | size=300, giữ chuỗi tiêu đề | Truy vết đúng mục dễ hơn | Tiêu đề lặp tốn ngân sách |

Heading trong src/heading.py tính ngân sách phần thân bằng chunk_size trừ độ dài chuỗi tiêu đề, dùng RecursiveChunker chia mục dài rồi gắn tiêu đề vào từng mảnh. Đây là chiến lược tùy chỉnh theo yêu cầu L3A.

### Kết quả chạy thật

Backend **MockEmbedder**, Python **3.11.16**. Q1 áp bộ lọc student ở cả bốn chiến lược.

| Chiến lược | Số chunk | Độ dài TB | Có đúng nguồn top-3 | Đủ cụm bằng chứng top-3 |
|---|---:|---:|---:|---:|
| fixed_size | 10 | 245.8 | 2/5 | 1/5 |
| by_sentences | 14 | 156.7 | 4/5 | 2/5 |
| recursive | 11 | 200.7 | 1/5 | 1/5 |
| heading | 11 | 219.0 | 3/5 | 2/5 |

**Chưa kết luận chiến lược tốt nhất về ngữ nghĩa.** Mock tạo vector từ hash nên thứ hạng không phản ánh ý nghĩa. Các đặc điểm có thể đánh giá độc lập: heading giữ tên mục; sentence giữ câu; fixed tạo overlap; recursive giới hạn kích thước. Heading phù hợp cấu trúc sổ tay về khả năng đọc và truy vết, nhưng cần embedding thật để kiểm chứng hiệu quả truy xuất.

## 3. Năm câu hỏi và đáp án chuẩn

Các đáp án trích được từ corpus đã đối chiếu nguồn. ID chunk dưới đây theo HeadingChunker(300).

| Câu | Câu hỏi | Đáp án chuẩn | Nguồn / mục / chunk |
|---|---|---|---|
| Q1 | Tôi được mượn bao nhiêu tài liệu và trong bao lâu? | Sinh viên đại học: 3 tài liệu, 2 tuần/tài liệu | student-borrowing / Hạn mức và thời hạn / #0 |
| Q2 | Sinh viên đại học được gia hạn sách mấy lần, thêm bao lâu và cần điều kiện gì? | 1 lần, thêm 1 tuần; chưa quá hạn, không có người khác yêu cầu | student-borrowing / Gia hạn sách / #1 |
| Q3 | Nhóm đến muộn bao nhiêu phút thì bị hủy lượt đặt phòng? | Không xuất hiện trong 10 phút đầu | room-booking / Đặt trước và đến muộn / #1 |
| Q4 | Ai được vào khu học tập 24/7 sau khi thư viện đóng cửa? | Sinh viên, giảng viên, nhân viên VinUni đang hoạt động | hours-access / Không gian 24/7 / #1 |
| Q5 | Giảng viên phải gửi biểu mẫu Course Reserve trước khi học phần bắt đầu bao lâu? | Ít nhất 8 tuần | course-reserve / Thời hạn gửi biểu mẫu / #2 |

Q1 không nói đối tượng trong câu chữ. Hồ sơ người hỏi cung cấp `metadata_filter={"audience":"student"}`; tài liệu giảng viên có quy định khác nên cần xác định đối tượng.

### Kết quả bằng chứng

| Câu | Fixed | Sentence | Recursive | Heading | Ghi chú |
|---|---|---|---|---|---|
| Q1 | Có | Có | Có | Có | Lọc đúng đối tượng |
| Q2 | Không | Không | Không | Không | Mock không lấy được thông tin gia hạn |
| Q3 | Không | Có | Không | Không | Sentence lấy bằng chứng ở hạng 2 |
| Q4 | Không | Không | Không | Không | Có đúng file vẫn có thể sai mục |
| Q5 | Không | Không | Không | Có | Heading có bằng chứng ở hạng 2 |

“Có” nghĩa là ngữ cảnh từ gold_doc_id chứa đủ evidence_phrases. Đây là phép kiểm chuỗi, cần kiểm tra thủ công; không tự chứng minh LLM trả lời đúng. Agent trong benchmark chỉ trích ngữ cảnh bằng hàm demo và được ghi nhãn rõ. **Chưa tự chấm điểm /10 cho chất lượng trả lời của LLM thật.**

### A/B bộ lọc Q1

| Chiến lược | Top-1 không lọc | Đủ bằng chứng top-3 không lọc | Top-1 có lọc | Đủ bằng chứng top-3 có lọc |
|---|---|---|---|---|
| fixed_size | student-borrowing#0 | Có | student-borrowing#0 | Có |
| by_sentences | room-booking#2 | Không | student-borrowing#0 | Có |
| recursive | course-reserve#2 | Không | student-borrowing#0 | Có |
| heading | faculty-borrowing#1 | Không | student-borrowing#0 | Có |

Top-3 và score chi tiết hai lần ở [benchmark.md](benchmark.md); nội dung chunk và ngữ cảnh Agent ở [benchmark.json](benchmark.json).

Filter cải thiện việc có bằng chứng ở 3/4 cấu hình. Fixed vốn có đáp án lần này, nhưng filter vẫn loại chunk khác đối tượng. Sau lọc chỉ còn 2 chunk do corpus chỉ có một file student; không đánh đồng thử nghiệm nhỏ với hiệu quả trên kho lớn.

## 4. Phân tích lỗi

1. **Q5 fixed size — đúng nguồn nhưng thiếu đáp án:** course-reserve#0 ở top-1 chỉ chứa phần Mục đích; thời hạn nằm ở chunk khác không lọt top-3. Chấm doc_id đơn thuần báo đạt sai.
2. **Q4 heading — chọn sai mục:** hours-access#0 nói về lịch; #1 mới chứa quyền truy cập khu 24/7. Giữ tiêu đề không thay thế embedding ngữ nghĩa.
3. **Bộ lọc quá chặt:** dùng student cho Q4 sẽ loại hours-access vì audience=all. Cần áp bộ lọc theo câu hỏi và có chính sách nhận tài liệu chung trong ứng dụng thực tế.

Cải thiện: chạy embedding đa ngữ thật trên corpus/query giữ nguyên; đọc lỗi theo mục; thử chunk size, overlap hoặc lấy mục lân cận; cân nhắc reranker. Đo cả số chunk, độ mạch lạc, bằng chứng và chất lượng câu trả lời có nguồn.

## 5. Demo và bài học nhóm

Kịch bản đề xuất 8 phút:

- 1 phút: chủ đề, 5 nguồn và metadata.
- 2 phút: so sánh bốn cách chia; chỉ ra chunk bị cắt và chunk giữ tiêu đề.
- 2 phút: A/B Q1, giải thích lọc trước top-k.
- 2 phút: Q5 fixed size để chứng minh đúng doc_id chưa đủ.
- 1 phút: giới hạn mock và cách chạy lại với --provider local.

Lệnh: `python -m pytest tests/ -v`, sau đó `python bench.py`. Đã có **69 kiểm thử đạt**, gồm 42 bài gốc và 27 bài bổ sung. Xem [hướng dẫn chạy](../../../GIAI_THICH.md).

**Phân công thành viên, điều học từ nhóm khác và buổi thuyết trình:** nhóm bổ sung sau hoạt động thật. Chưa tự gán điểm phần chưa diễn ra; không dùng thử nghiệm tự động thay cho trải nghiệm nhóm.
