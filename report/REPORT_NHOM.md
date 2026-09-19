# Báo cáo nhóm — UIT + Thư viện Trung tâm + KTX ĐHQG-HCM

**Nhóm / thành viên:** [Người học điền]

**Ngày thực nghiệm:** 19/09/2026

> Bộ dữ liệu đã đổi theo lựa chọn của người dùng. Đây là bản thực nghiệm có hỗ trợ của Codex; không giả định đã thảo luận hoặc thuyết trình cùng nhóm. Báo cáo VinUni lần trước được lưu riêng trong archive/vinuni.

## 1. Bộ dữ liệu được chọn

Chọn hệ sinh thái UIT và các dịch vụ ĐHQG-HCM trong tài liệu người dùng gửi. Có **7 tài liệu thuộc 6 chủ đề**: đăng ký học phần, học phí, học bổng, thư viện, ký túc xá và phúc khảo. Phúc khảo tách quy trình sinh viên và giảng viên để thử lọc audience. Có 6 URL nguồn khác nhau; hai mục sinh viên trên DAA được tách thành hai file theo chủ đề.

Các file là bản tóm lược có đối chiếu nguồn, không phải toàn văn hoặc bản quy định chính thức. Không dùng trang chủ làm gold answer, không truy cập dữ liệu sau đăng nhập. Nguồn thư viện và KTX đã được đọc trực tiếp thành công sau khi kiểm robots.txt. Chi tiết ở [ghi chú nguồn](../docs/CORPUS_NOTES.md).

| Tài liệu | Đơn vị | Chủ đề / audience | Ký tự | Nguồn / phiên bản |
|---|---|---|---:|---|
| ktx-gia-han-2026-2027 | VNU-HCM-Dormitory | ky_tuc_xa / student | 790 | [Nguồn](https://huongdan.ktxhcm.edu.vn/huong-dan/huong-dan-sinh-vien-dang-noi-tru-thuc-hien-gia-han) — Hướng dẫn gia hạn 2026-2027; dẫn Thông báo 505 ngày 2026-07-22 |
| uit-dang-ky-hoc-phan | UIT | dang_ky_hoc_phan / student | 687 | [Nguồn](https://daa.uit.edu.vn/mot-so-quy-trinh-danh-cho-sinh-vien) — not-stated |
| uit-hoc-bong-global-2026 | UIT | hoc_bong / student | 808 | [Nguồn](https://ctsv.uit.edu.vn/bai-viet/thong-bao-trien-khai-hoc-bong-uit-global-tu-hoc-ky-1-nam-hoc-2026-2027) — 803/QĐ-ĐHCNTT (2026-07-07) |
| uit-hoc-phi-he-2025-2026 | UIT | hoc_phi / student | 606 | [Nguồn](https://khtc.uit.edu.vn/content/2025-2026-thong-bao-thu-hoc-phi-hoc-ky-he-nh-2025-2026) — Thông báo ngày 2026-07-21 |
| uit-phuc-khao-giang-vien | UIT | phuc_khao / faculty | 553 | [Nguồn](https://daa.uit.edu.vn/content/quy-trinh-danh-cho-can-bo-giang-day) — not-stated |
| uit-phuc-khao-sinh-vien | UIT | phuc_khao / student | 374 | [Nguồn](https://daa.uit.edu.vn/mot-so-quy-trinh-danh-cho-sinh-vien) — not-stated |
| vnulib-muon-tra | VNU-HCM-Central-Library | thu_vien / all | 682 | [Nguồn](https://www.vnulib.edu.vn/index.php/muon-tra-tai-lieu-tvtt) — not-stated |

Tất cả có retrieved_at=2026-09-19. [sources.csv](../data/uit-vnuhcm/sources.csv) có một dòng mỗi file. Quy định có phạm vi thời gian rõ được lưu cùng academic_year/effective_from; không dùng hạn thu học phí hè 2025-2026 cho kỳ học khác. Đăng ký KTX mới và gia hạn nội trú là hai thủ tục khác nhau.

### Metadata

| Trường | Kiểu | Mục đích |
|---|---|---|
| doc_id / title | string | Định danh và tên tài liệu |
| university | string | UIT hoặc VNU-HCM, không trộn thành một trường |
| institution | string | Đơn vị cụ thể: UIT, VNU-HCM-Central-Library, VNU-HCM-Dormitory |
| audience | string | student, faculty hoặc all |
| category / department / language | string | Chủ đề dịch vụ, đơn vị phụ trách, ngôn ngữ |
| source_url / source_section | string | URL gốc, mục đã đọc khi có |
| retrieved_at / document_version | string | Ngày lấy và phiên bản; not-stated nếu nguồn không ghi |
| academic_year / effective_from | string | Chỉ gán khi có bằng chứng trong nguồn |
| content_type | string | Ghi rõ paraphrased-study-note |
| chunk_index | integer | Vị trí chunk do ingest gán |

audience=all của thư viện bao gồm nhiều nhóm, nhưng nội dung phân biệt chính quy và ngoài ĐHQG-HCM. Q4 nêu rõ đối tượng trong câu hỏi; không dùng bộ lọc student cho Q4 vì sẽ loại tài liệu all. Mỗi chunk giữ metadata gốc. Phần metadata không được đưa vào văn bản embedding.

## 2. Chiến lược

| Chiến lược | Cấu hình benchmark | Điểm mạnh | Hạn chế |
|---|---|---|---|
| fixed_size | 300 ký tự, overlap=50 | Ngân sách rõ, có vùng lặp | Có thể cắt giữa từ/URL/điều kiện |
| by_sentences | 2 câu/chunk | Giữ câu hoàn chỉnh | Regex đơn giản, độ dài không cố định |
| recursive | 300 ký tự | Ưu tiên đoạn/dòng/câu/từ, gom mảnh nhỏ | Không tự lặp tiêu đề |
| heading | 300 ký tự, lặp tiêu đề cha/mục | Giữ bối cảnh Điều/Mục ở các mảnh | Tiêu đề lặp chiếm dung lượng |

Heading dùng tiêu đề Markdown đã chuẩn hóa từ các mục của trang gốc. Không tuyên bố đã parse toàn bộ văn bản pháp quy Chương/Điều/Khoản. Corpus nhỏ và tóm lược nên kết quả không đại diện cho mọi sổ tay dài.

### Baseline trên 3 tài liệu

Comparator dùng size=200, overlap=50 và 3 câu/chunk cho sentence (khác cấu hình 2 câu của benchmark chính).

| Tài liệu | Chiến lược | Số chunk | Độ dài TB |
|---|---|---:|---:|
| ktx-gia-han-2026-2027 | fixed_size | 5 | 198.0 |
| ktx-gia-han-2026-2027 | by_sentences | 4 | 196.0 |
| ktx-gia-han-2026-2027 | recursive | 6 | 131.7 |
| uit-dang-ky-hoc-phan | fixed_size | 5 | 177.4 |
| uit-dang-ky-hoc-phan | by_sentences | 3 | 227.7 |
| uit-dang-ky-hoc-phan | recursive | 6 | 114.5 |
| uit-hoc-bong-global-2026 | fixed_size | 6 | 176.3 |
| uit-hoc-bong-global-2026 | by_sentences | 3 | 267.7 |
| uit-hoc-bong-global-2026 | recursive | 6 | 134.7 |

### Kết quả chạy lại trên bộ mới

Python 3.11.16; MockEmbedder; top-k=3. Corpus và năm câu hỏi giữ nguyên giữa bốn chiến lược.

| Chiến lược | Số chunk | Độ dài TB | Đúng nguồn top-3 | Đủ bằng chứng top-3 |
|---|---:|---:|---:|---:|
| fixed_size | 21 | 247.6 | 3/5 | 0/5 |
| by_sentences | 26 | 171.8 | 1/5 | 1/5 |
| recursive | 22 | 204.5 | 1/5 | 0/5 |
| heading | 23 | 221.1 | 2/5 | 2/5 |

Mock sinh vector từ hash, không hiểu tiếng Việt. Do đó không dùng bảng này để kết luận heading tốt nhất về ngữ nghĩa. Số chunk, độ dài, khả năng giữ tiêu đề/câu vẫn là những quan sát có giá trị độc lập với embedder.

## 3. Năm câu hỏi mới và đáp án

| Câu | Câu hỏi | Đáp án chuẩn | Tài liệu / mục |
|---|---|---|---|
| Q1 | Ở UIT, tôi cần làm gì để yêu cầu phúc khảo và nhận kết quả bằng cách nào? | Sau khi có điểm, gửi yêu cầu tại https://daa.uit.edu.vn/sinhvien/dkphuckhao, nộp lệ phí; kết quả được thông báo qua email. | uit-phuc-khao-sinh-vien / Gửi yêu cầu; Lệ phí và kết quả |
| Q2 | Hạn đóng học phí học kỳ hè 2025-2026 của UIT là ngày nào? | Hạn cuối là ngày 16/08/2026, áp dụng riêng học kỳ hè năm học 2025-2026. | uit-hoc-phi-he-2025-2026 / Tra cứu và thời hạn nộp |
| Q3 | Theo quy định UIT Global có hiệu lực từ 01/09/2026, sinh viên được nộp chứng chỉ xét học bổng trong những học kỳ nào? | Trong 6 học kỳ đầu; hạn mỗi học kỳ là 30 ngày từ khi học kỳ kết thúc. Từ học kỳ 7 không còn được xét. | uit-hoc-bong-global-2026 / Thời điểm nộp chứng chỉ |
| Q4 | Sinh viên chính quy thuộc ĐHQG-HCM được mượn bao nhiêu tài liệu tại Thư viện Trung tâm, trong bao lâu và gia hạn thế nào? | Mượn 5 tài liệu trong 21 ngày; được gia hạn 1 lần thêm 21 ngày. | vnulib-muon-tra / Nhóm chính quy thuộc ĐHQG-HCM |
| Q5 | Sinh viên đang ở KTX ĐHQG-HCM gia hạn năm 2026-2027 phải thanh toán trong bao lâu sau khi hồ sơ được duyệt? | Trong vòng 7 ngày kể từ khi hồ sơ gia hạn được duyệt; quá hạn có thể bị hủy kết quả. | ktx-gia-han-2026-2027 / Điều kiện hoàn tất |

Đăng ký học phần có trong corpus nhưng không có câu hỏi riêng do bài yêu cầu đúng 5 câu. Tài liệu này đồng thời là ứng viên gây nhiễu để thử phân biệt chủ đề. Có thể thay một câu hỏi bằng đăng ký học phần trong một lần thử nghiệm mới, không thay giữa các chiến lược của cùng lượt đo.

### A/B audience của Q1

Người hỏi là sinh viên UIT; bộ lọc là `{"audience":"student"}`. Cùng chủ đề phúc khảo nhưng giảng viên thực hiện nhận/chấm/chuyển bài, sinh viên thực hiện yêu cầu/nộp phí/nhận thông báo. Corpus giữ cả hai để kiểm tra đúng đối tượng.

| Chiến lược | Top-3 thay đổi sau lọc? | Loại chunk faculty khỏi top-3? | Đủ đáp án trước / sau |
|---|---|---|---|
| fixed_size | Không | Không | Không / Không |
| by_sentences | Không | Không | Không / Không |
| recursive | Có | Có | Không / Không |
| heading | Có | Có | Không / Không |

Trong lần chạy mock này, filter loại faculty trong top-3 của recursive và heading nhưng **không tạo ra ngữ cảnh đủ đáp án Q1**. Fixed và sentence không đổi top-3 vì ba ứng viên đầu vốn đã có audience=student. Không diễn giải thành “lọc đã trả lời đúng”. Lọc đối tượng và hiểu chủ đề là hai bước khác nhau; cần embedding thật để đo chất lượng retrieval.

Top-3 đầy đủ, score và A/B nằm trong [benchmark.md](results/benchmark.md); nội dung và ngữ cảnh agent nằm trong [benchmark.json](results/benchmark.json). Agent chỉ trích ngữ cảnh bằng hàm demo, chưa có LLM thật; chưa tự chấm điểm chất lượng trả lời /10.

## 4. Failure analysis

1. **Q3 fixed_size:** top-3 có uit-hoc-bong-global-2026#0 nhưng đoạn này chưa chứa đủ mốc học kỳ và hạn nộp. Source hit báo có; evidence hit báo không. Đúng tài liệu chưa đủ để trả lời.
2. **Q1 heading:** bỏ được chunk giảng viên nhưng top-3 vẫn là KTX/học bổng. Audience đúng không đồng nghĩa category đúng. Cải thiện bằng embedding đa ngữ và thử lọc category/university theo thông tin người hỏi cung cấp; ghi rõ bộ lọc mới trước lần đo tiếp theo.
3. **Q2 mọi chiến lược:** không lấy được đoạn hạn học phí. Không suy diễn quy định từ score hoặc dùng hạn của kỳ khác. Chỉ dùng gold có năm học và học kỳ tương ứng.

Phép evidence kiểm cụm đáp án trong các chunk từ đúng nguồn, không tự chấm chất lượng LLM. Cần đọc thủ công vì chunk có thể thiếu điều kiện xung quanh ngay cả khi đủ một cụm số liệu.

## 5. Demo và tái lập

```powershell
cd F:\bai7
.\.venv\Scripts\python.exe -m pytest tests/ -q
.\.venv\Scripts\python.exe bench.py
```

Lệnh mặc định dùng UIT/ĐHQG-HCM. Có thể chỉ rõ `--corpus-dir data/uit-vnuhcm --queries data/uit-vnuhcm-queries.json`. Corpus khác bắt buộc có bộ câu hỏi tương ứng. Benchmark từ chối gold thiếu trong corpus hoặc bị chính bộ lọc loại bỏ.

**77 kiểm thử đạt** (42 bài gốc và 35 bài bổ sung); `tests/test_solution.py` giữ nguyên. Gợi ý demo: nguồn/phạm vi → bốn cách chia → Q3 đúng file nhưng thiếu bằng chứng → A/B Q1 → giới hạn mock. Phân công, trao đổi thực tế và điểm tự đánh giá do nhóm bổ sung.
