# Kết quả benchmark

Corpus: `uit-vnuhcm` — 7 tài liệu.
Bộ câu hỏi: `uit-vnuhcm-queries.json`.
Python 3.11.16; embedding: `mock embeddings fallback`; chunk_size=300.
SentenceChunker dùng 2 câu/chunk; comparator baseline dùng 3 câu/chunk, size=200.
Agent chỉ trích ngữ cảnh bằng hàm giả lập; chưa đánh giá câu trả lời của LLM thật.
Mock dùng MD5 và số giả ngẫu nhiên: điểm số không phản ánh ngữ nghĩa, không dùng để chọn mô hình tốt nhất.

`Source hit`: có đúng tài liệu. `Evidence hit`: ngữ cảnh từ tài liệu đó chứa đủ các cụm đáp án đã khai báo.
Evidence hit là phép kiểm chuỗi hỗ trợ kiểm tra thủ công, không phải thang điểm chất lượng LLM.

| Chiến lược | Số chunk | Độ dài TB | Source hit@3 | Evidence hit@3 |
|---|---:|---:|---:|---:|
| fixed_size | 21 | 247.6 | 3/5 | 0/5 |
| by_sentences | 26 | 171.8 | 1/5 | 1/5 |
| recursive | 22 | 204.5 | 1/5 | 0/5 |
| heading | 23 | 221.1 | 2/5 | 2/5 |

## fixed_size

| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |
|---|---|---|
| Q1 | uit-phuc-khao-sinh-vien#1 (0.2188); uit-hoc-bong-global-2026#1 (0.2111); uit-hoc-phi-he-2025-2026#0 (0.1997) | False / False |
| Q2 | vnulib-muon-tra#1 (0.2167); uit-dang-ky-hoc-phan#1 (0.2136); uit-phuc-khao-giang-vien#2 (0.1859) | False / False |
| Q3 | vnulib-muon-tra#2 (0.2655); vnulib-muon-tra#0 (0.2423); uit-hoc-bong-global-2026#0 (0.2393) | False / False |
| Q4 | uit-hoc-phi-he-2025-2026#1 (0.2264); uit-hoc-bong-global-2026#2 (0.1897); uit-hoc-bong-global-2026#0 (0.1407) | False / False |
| Q5 | uit-phuc-khao-giang-vien#0 (0.2340); uit-phuc-khao-sinh-vien#0 (0.1831); ktx-gia-han-2026-2027#1 (0.0913) | False / False |

### A/B bộ lọc Q1

Metadata filter: `{"audience": "student"}`

- unfiltered: uit-phuc-khao-sinh-vien#1 (student, 0.2188); uit-hoc-bong-global-2026#1 (student, 0.2111); uit-hoc-phi-he-2025-2026#0 (student, 0.1997). Đủ bằng chứng: False.
- filtered: uit-phuc-khao-sinh-vien#1 (student, 0.2188); uit-hoc-bong-global-2026#1 (student, 0.2111); uit-hoc-phi-he-2025-2026#0 (student, 0.1997). Đủ bằng chứng: False.

## by_sentences

| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |
|---|---|---|
| Q1 | uit-dang-ky-hoc-phan#3 (0.2340); uit-dang-ky-hoc-phan#0 (0.0861); uit-hoc-bong-global-2026#4 (0.0749) | False / False |
| Q2 | uit-phuc-khao-giang-vien#2 (0.2102); ktx-gia-han-2026-2027#2 (0.1924); vnulib-muon-tra#3 (0.1811) | False / False |
| Q3 | uit-phuc-khao-giang-vien#1 (0.2954); uit-phuc-khao-sinh-vien#1 (0.2115); uit-dang-ky-hoc-phan#2 (0.1238) | False / False |
| Q4 | uit-dang-ky-hoc-phan#2 (0.2893); uit-hoc-bong-global-2026#1 (0.2433); uit-phuc-khao-giang-vien#1 (0.1803) | False / False |
| Q5 | ktx-gia-han-2026-2027#4 (0.2498); uit-hoc-bong-global-2026#3 (0.1445); ktx-gia-han-2026-2027#3 (0.1414) | False / True |

### A/B bộ lọc Q1

Metadata filter: `{"audience": "student"}`

- unfiltered: uit-dang-ky-hoc-phan#3 (student, 0.2340); uit-dang-ky-hoc-phan#0 (student, 0.0861); uit-hoc-bong-global-2026#4 (student, 0.0749). Đủ bằng chứng: False.
- filtered: uit-dang-ky-hoc-phan#3 (student, 0.2340); uit-dang-ky-hoc-phan#0 (student, 0.0861); uit-hoc-bong-global-2026#4 (student, 0.0749). Đủ bằng chứng: False.

## recursive

| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |
|---|---|---|
| Q1 | uit-hoc-bong-global-2026#1 (0.2382); uit-hoc-phi-he-2025-2026#2 (0.1435); uit-hoc-phi-he-2025-2026#0 (0.1352) | False / False |
| Q2 | uit-dang-ky-hoc-phan#0 (0.3973); uit-hoc-bong-global-2026#2 (0.1032); ktx-gia-han-2026-2027#1 (0.0960) | False / False |
| Q3 | uit-hoc-bong-global-2026#1 (0.2028); uit-hoc-phi-he-2025-2026#2 (0.1703); vnulib-muon-tra#0 (0.1127) | False / False |
| Q4 | uit-hoc-bong-global-2026#3 (0.2001); ktx-gia-han-2026-2027#0 (0.1930); uit-hoc-phi-he-2025-2026#2 (0.1881) | False / False |
| Q5 | uit-dang-ky-hoc-phan#1 (0.3006); uit-phuc-khao-giang-vien#0 (0.2649); uit-dang-ky-hoc-phan#2 (0.1282) | False / False |

### A/B bộ lọc Q1

Metadata filter: `{"audience": "student"}`

- unfiltered: uit-hoc-bong-global-2026#1 (student, 0.2382); uit-hoc-phi-he-2025-2026#2 (student, 0.1435); uit-phuc-khao-giang-vien#2 (faculty, 0.1372). Đủ bằng chứng: False.
- filtered: uit-hoc-bong-global-2026#1 (student, 0.2382); uit-hoc-phi-he-2025-2026#2 (student, 0.1435); uit-hoc-phi-he-2025-2026#0 (student, 0.1352). Đủ bằng chứng: False.

## heading

| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |
|---|---|---|
| Q1 | ktx-gia-han-2026-2027#2 (0.2239); ktx-gia-han-2026-2027#3 (0.1567); uit-hoc-bong-global-2026#3 (0.1287) | False / False |
| Q2 | uit-dang-ky-hoc-phan#2 (0.3882); vnulib-muon-tra#3 (0.2762); uit-phuc-khao-giang-vien#2 (0.2749) | False / False |
| Q3 | ktx-gia-han-2026-2027#0 (0.2712); uit-hoc-bong-global-2026#2 (0.1662); uit-hoc-bong-global-2026#3 (0.1440) | False / True |
| Q4 | uit-dang-ky-hoc-phan#0 (0.2662); uit-hoc-bong-global-2026#3 (0.2631); uit-phuc-khao-giang-vien#2 (0.1929) | False / False |
| Q5 | uit-hoc-bong-global-2026#0 (0.2279); vnulib-muon-tra#0 (0.2244); ktx-gia-han-2026-2027#2 (0.1913) | False / True |

### A/B bộ lọc Q1

Metadata filter: `{"audience": "student"}`

- unfiltered: ktx-gia-han-2026-2027#2 (student, 0.2239); uit-phuc-khao-giang-vien#1 (faculty, 0.1906); ktx-gia-han-2026-2027#3 (student, 0.1567). Đủ bằng chứng: False.
- filtered: ktx-gia-han-2026-2027#2 (student, 0.2239); ktx-gia-han-2026-2027#3 (student, 0.1567); uit-hoc-bong-global-2026#3 (student, 0.1287). Đủ bằng chứng: False.

## Baseline trên ba tài liệu

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

## Dự đoán trước khi chạy

| Cặp | Câu A | Câu B | Dự đoán theo ngữ nghĩa | Cosine thực tế |
|---|---|---|---|---:|
| 1 | Sinh viên mượn sách tại thư viện. | Sinh viên mượn sách tại thư viện. | cao nhất: cùng một câu | 1.0000 |
| 2 | Sinh viên mượn sách tại thư viện. | Người học có thể mượn tài liệu ở thư viện. | cao về ngữ nghĩa | -0.0750 |
| 3 | Nhóm cần đặt phòng để cùng học bài. | Các bạn đăng ký phòng học nhóm. | cao về ngữ nghĩa | 0.2028 |
| 4 | Sinh viên phải gia hạn sách trước hạn trả. | Thư viện cung cấp máy in và máy quét. | trung bình: cùng chủ đề, khác dịch vụ | -0.0739 |
| 5 | Thư viện cho mượn sách. | Núi lửa phun trào tạo ra dung nham. | thấp nhất về ngữ nghĩa | -0.1249 |
