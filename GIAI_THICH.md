# Những gì đã làm trong bài 7

Đã tải repository `VinUni-AI20k/K4-L3A-Data-Foundations` về `F:\bai7` và hoàn thành các TODO. Theo lựa chọn mới của người dùng, benchmark mặc định dùng **UIT + Thư viện Trung tâm + KTX ĐHQG-HCM**, gồm 7 bản tóm lược từ nguồn chính thức bao phủ 6 dịch vụ. Đây là bản thực hiện có hỗ trợ của Codex; thông tin cá nhân và hoạt động nhóm cần người học bổ sung.

## 1. Luồng xử lý

```text
File Markdown
  → đọc metadata và phần thân riêng biệt
  → chia phần thân thành các chunk
  → tạo Document cho từng chunk, giữ doc_id của tài liệu gốc
  → embedding biến chunk thành vector
  → EmbeddingStore lưu vector + nội dung + metadata
  → lọc metadata, xếp hạng độ tương tự, lấy top-k
  → KnowledgeBaseAgent dựng prompt kèm nguồn
  → llm_fn nhận prompt để tạo câu trả lời
```

Trong lần chạy đã lưu, embedding là **MockEmbedder**, LLM là hàm **demo trích ngữ cảnh**. Toàn bộ luồng chạy không cần API key; chưa có mô hình sinh câu trả lời thật. Mock băm chuỗi bằng MD5 để sinh vector, không hiểu nghĩa tiếng Việt.

## 2. Chia văn bản: `src/chunking.py`

- **FixedSizeChunker:** cửa sổ độ dài cố định có overlap. Bổ sung kiểm tra `chunk_size > 0` và `0 <= overlap < chunk_size` để tránh bước trượt bằng 0 hoặc âm.
- **SentenceChunker:** regex `(?<=[.!?])\s+` tách ở khoảng trắng sau dấu chấm, chấm than, chấm hỏi. Lookbehind giữ lại dấu câu. Sau đó gom số câu đã cấu hình, bỏ khoảng trắng hai đầu.
- **RecursiveChunker:** ưu tiên đoạn văn → dòng → câu → từ → ký tự. Mảnh quá dài được chia tiếp; các mảnh ngắn liên tiếp được gom lại. Giữ nguyên dấu phân cách để nối các chunk có thể tái tạo nội dung gốc. Kích thước mỗi chunk không vượt giới hạn.
- **compute_similarity:** `dot(a,b) / (norm(a)*norm(b))`; vector có độ lớn 0 trả 0; khác số chiều báo lỗi.
- **ChunkingStrategyComparator:** chạy 3 chiến lược và trả `count`, `avg_length`, `chunks` để so sánh.

Ví dụ 10.000 ký tự, size=500: overlap=50 tạo **23** chunk; overlap=100 tạo **25** chunk. Overlap giữ ngữ cảnh gần ranh giới nhưng làm tăng lượng dữ liệu lặp và số vector.

## 3. Kho vector: `src/store.py`

Dùng bộ nhớ theo hướng dẫn Codelab của repository. Mỗi Document đầu vào tương ứng một record; store không tự chunk. Metadata được sao chép, `doc_id` được giữ nếu đã có, nếu thiếu thì dùng `Document.id`.

`search()` nhúng câu hỏi, tính dot product với các record và sắp xếp giảm dần. Các embedder sẵn có trả vector chuẩn hóa nên dot product bằng cosine. Nếu tự truyền vector chưa chuẩn hóa, score là dot product thuần, không được diễn giải như cosine.

`search_with_filter()` lọc **trước khi lấy top-k** và yêu cầu tất cả trường cùng khớp. Nếu lấy top-3 trước rồi mới lọc, kết quả có thể rỗng dù trong kho vẫn còn tài liệu hợp lệ. `delete_document()` xóa mọi chunk có cùng `metadata['doc_id']` và báo có xóa được hay không.

Kho này phục vụ học tập, tìm kiếm tuyến tính, không lưu bền khi đóng chương trình. Không dùng ChromaDB theo khuyến nghị trong `day7-lab-data-foundations.md`.

## 4. Agent: `src/agent.py`

Agent lấy các chunk liên quan, đánh số `[1]`, `[2]`, `[3]`, gắn URL, ID chunk, audience và phiên bản vào ngữ cảnh. Prompt yêu cầu chỉ dùng nội dung cung cấp, trích dẫn nguồn và nói rõ khi thiếu thông tin. Nếu không có kết quả, trả thông báo ngay, không gọi LLM.

Giữ nguyên `answer(question, top_k=3)` và thêm `answer_with_filter()` để thử bộ lọc của L3A. Hàm `llm_fn` được truyền từ ngoài nên có thể thay demo bằng LLM thật. Prompt hỗ trợ grounding nhưng không tự bảo đảm mô hình luôn đúng; cần đánh giá đầu ra thật khi kết nối mô hình.

## 5. Phần thử nghiệm bổ sung

- `src/heading.py`: chia theo tiêu đề Markdown; khi một mục dài phải tách tiếp, lặp lại đường dẫn tiêu đề ở mỗi chunk để giữ ngữ cảnh. Chỉ hỗ trợ Markdown đơn giản của corpus, chưa phải parser đầy đủ cho code fence hay mọi cú pháp Markdown.
- `src/ingestion.py`: đọc front matter dạng các trường chuỗi phẳng, kiểm metadata bắt buộc và tạo chunk có ID như `uit-phuc-khao-sinh-vien#0`. Không phải bộ phân tích YAML tổng quát.
- `data/uit-vnuhcm/`: 7 tài liệu gồm đăng ký học phần, học phí, học bổng, thư viện, ký túc xá, phúc khảo. Phúc khảo tách riêng quy trình sinh viên và giảng viên. Metadata có thêm `university`, `institution`, `category` cùng thời kỳ áp dụng khi nguồn nêu. Xem [CORPUS_NOTES.md](docs/CORPUS_NOTES.md).
- `data/uit-vnuhcm-queries.json`: 5 câu hỏi mới, đáp án và cụm bằng chứng khớp bộ UIT/ĐHQG-HCM. Q1 dùng `audience=student` để loại quy trình chấm phúc khảo của giảng viên.
- `bench.py`: so sánh fixed size, câu, đệ quy, tiêu đề; lưu top-3, score, nguồn, kết quả A/B lọc metadata và 5 cặp cosine.
- `tests/test_edge_cases.py`: kiểm tra mất dữ liệu khi chia, thứ tự lọc, xóa nhiều chunk, metadata bị sửa ngoài store, vector sai chiều, nguồn trong prompt và bằng chứng đáp án.

Phép đánh giá phân biệt “đúng tài liệu” với “đủ bằng chứng trả lời”. Chỉ tìm thấy doc_id chưa đủ: chunk được lấy có thể thuộc mục khác. Phép kiểm cụm bằng chứng là tiêu chí máy đơn giản, cần đọc ngữ cảnh để đánh giá câu trả lời đầy đủ.

`bench.py` kiểm tra đáp án chuẩn có trong corpus, bộ lọc không loại tài liệu gold và có đủ 5 câu hỏi trước khi chạy. Không được ghép bộ câu hỏi VinUni với dữ liệu UIT. Kiểm thử mới trong `tests/test_benchmark_datasets.py` xác nhận việc đổi bộ; tổng hiện tại là **77 kiểm thử đạt** trên Python 3.11.16.

## 6. Cách chạy trên máy này

Mở PowerShell:

```powershell
cd F:\bai7
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python.exe -m pytest tests/ -v
.\.venv\Scripts\python.exe main.py "Chunking là gì?"
.\.venv\Scripts\python.exe bench.py
```

Lệnh benchmark mặc định dùng bộ mới. Có thể chỉ định rõ hoặc thay dữ liệu khác:

```powershell
.\.venv\Scripts\python.exe bench.py --corpus-dir data/uit-vnuhcm --queries data/uit-vnuhcm-queries.json --output-dir report/results
```

Khi chọn corpus khác phải truyền bộ câu hỏi tương ứng bằng `--queries`. Bộ VinUni cũ chỉ giữ để đối chiếu; các kết quả và báo cáo lần trước nằm trong `report/archive/vinuni/`, không trộn vào lần chạy mặc định.

Môi trường `.venv` dùng Python 3.11.16, với dependencies đúng `requirements.txt`. Không cần kích hoạt venv. Python nền được tải riêng trong `.tools/python`, không thay Python hệ thống; nếu xóa `.tools` thì cần tạo lại venv. Hai thư mục này được Git bỏ qua.

Để tạo lại môi trường trên máy đã cài Python 3.11:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu muốn đánh giá bằng embedding đa ngữ thật, cài phần tùy chọn và lưu riêng kết quả:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.\.venv\Scripts\python.exe bench.py --provider local --output-dir report/results-local
```

Chưa chạy backend local trong lần thực hiện này. Lệnh sẽ tải mô hình và thư viện bổ sung. Benchmark báo lỗi nếu local không sẵn sàng, không âm thầm chuyển thành mock.

## 7. Đọc kết quả

- [Báo cáo cá nhân](report/REPORT_CANHAN.md): kiến thức, thuật toán, kiểm thử và phân tích kết quả.
- [Báo cáo nhóm](report/REPORT_NHOM.md): corpus, chiến lược, benchmark, lỗi và kịch bản demo.
- [Bảng kết quả](report/results/benchmark.md): top-3 cho mọi chiến lược, A/B, baseline và cosine.
- [Dữ liệu kết quả đầy đủ](report/results/benchmark.json): nội dung từng chunk và đầu ra agent demo để kiểm tra.

Đã giữ `tests/test_solution.py` nguyên vẹn. Báo cáo không tự gán điểm chất lượng LLM hoặc bịa hoạt động nhóm. Chỉ cần bổ sung thông tin cá nhân, xác nhận/thảo luận với nhóm và thực hiện thuyết trình khi nộp bài.
