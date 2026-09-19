# Kết quả benchmark

Python 3.11.16; embedding: `mock embeddings fallback`; chunk_size=300.
SentenceChunker dùng 2 câu/chunk; comparator baseline dùng 3 câu/chunk, size=200.
Agent chỉ trích ngữ cảnh bằng hàm giả lập; chưa đánh giá câu trả lời của LLM thật.
Mock dùng MD5 và số giả ngẫu nhiên: điểm số không phản ánh ngữ nghĩa, không dùng để chọn mô hình tốt nhất.

`Source hit`: có đúng tài liệu. `Evidence hit`: ngữ cảnh từ tài liệu đó chứa đủ các cụm đáp án đã khai báo.
Evidence hit là phép kiểm chuỗi hỗ trợ kiểm tra thủ công, không phải thang điểm chất lượng LLM.

| Chiến lược | Số chunk | Độ dài TB | Source hit@3 | Evidence hit@3 |
|---|---:|---:|---:|---:|
| fixed_size | 10 | 245.8 | 2/5 | 1/5 |
| by_sentences | 14 | 156.7 | 4/5 | 2/5 |
| recursive | 11 | 200.7 | 1/5 | 1/5 |
| heading | 11 | 219.0 | 3/5 | 2/5 |

## fixed_size

| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |
|---|---|---|
| Q1 | student-borrowing#0 (0.1235); student-borrowing#1 (0.0489) | True / True |
| Q2 | hours-access#1 (0.1751); course-reserve#1 (0.0945); course-reserve#0 (0.0723) | False / False |
| Q3 | course-reserve#1 (0.1736); hours-access#0 (0.1637); student-borrowing#1 (0.1476) | False / False |
| Q4 | room-booking#0 (0.2407); room-booking#1 (0.1937); course-reserve#1 (0.1053) | False / False |
| Q5 | course-reserve#0 (0.1345); faculty-borrowing#1 (0.0730); room-booking#0 (0.0572) | False / False |

### A/B bộ lọc Q1

- unfiltered: student-borrowing#0 (student, 0.1235); course-reserve#1 (faculty, 0.0591); student-borrowing#1 (student, 0.0489). Đủ bằng chứng: True.
- filtered: student-borrowing#0 (student, 0.1235); student-borrowing#1 (student, 0.0489). Đủ bằng chứng: True.

## by_sentences

| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |
|---|---|---|
| Q1 | student-borrowing#0 (0.0140); student-borrowing#1 (-0.2154) | True / True |
| Q2 | hours-access#1 (0.1296); room-booking#2 (0.0848); faculty-borrowing#1 (0.0681) | False / False |
| Q3 | faculty-borrowing#0 (0.1458); room-booking#2 (0.0863); faculty-borrowing#1 (0.0861) | False / True |
| Q4 | hours-access#0 (0.2331); faculty-borrowing#2 (0.1849); student-borrowing#1 (0.0262) | False / False |
| Q5 | faculty-borrowing#0 (0.2141); hours-access#2 (0.1345); course-reserve#2 (0.0957) | False / False |

### A/B bộ lọc Q1

- unfiltered: room-booking#2 (all, 0.2188); faculty-borrowing#1 (faculty, 0.1745); room-booking#1 (all, 0.1465). Đủ bằng chứng: False.
- filtered: student-borrowing#0 (student, 0.0140); student-borrowing#1 (student, -0.2154). Đủ bằng chứng: True.

## recursive

| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |
|---|---|---|
| Q1 | student-borrowing#0 (0.0686); student-borrowing#1 (0.0490) | True / True |
| Q2 | hours-access#1 (0.1751); course-reserve#2 (0.1127); room-booking#0 (0.1015) | False / False |
| Q3 | student-borrowing#0 (0.1982); faculty-borrowing#0 (0.1896); student-borrowing#1 (0.1325) | False / False |
| Q4 | room-booking#0 (0.1570); faculty-borrowing#1 (0.0059); room-booking#1 (-0.0006) | False / False |
| Q5 | student-borrowing#1 (0.1746); hours-access#0 (0.1652); faculty-borrowing#1 (0.1118) | False / False |

### A/B bộ lọc Q1

- unfiltered: course-reserve#2 (faculty, 0.3612); hours-access#0 (all, 0.1110); room-booking#0 (all, 0.0928). Đủ bằng chứng: False.
- filtered: student-borrowing#0 (student, 0.0686); student-borrowing#1 (student, 0.0490). Đủ bằng chứng: True.

## heading

| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |
|---|---|---|
| Q1 | student-borrowing#0 (-0.1237); student-borrowing#1 (-0.1960) | True / True |
| Q2 | faculty-borrowing#1 (0.1299); faculty-borrowing#0 (0.1261); course-reserve#0 (0.0796) | False / False |
| Q3 | faculty-borrowing#0 (0.1140); course-reserve#1 (0.0744); course-reserve#0 (0.0657) | False / False |
| Q4 | room-booking#0 (0.1587); room-booking#1 (0.1476); hours-access#0 (0.1075) | False / False |
| Q5 | faculty-borrowing#1 (0.1588); course-reserve#2 (0.1137); course-reserve#1 (0.0709) | False / True |

### A/B bộ lọc Q1

- unfiltered: faculty-borrowing#1 (faculty, 0.3549); course-reserve#0 (faculty, 0.2548); hours-access#1 (all, 0.1449). Đủ bằng chứng: False.
- filtered: student-borrowing#0 (student, -0.1237); student-borrowing#1 (student, -0.1960). Đủ bằng chứng: True.

## Baseline trên ba tài liệu

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

## Dự đoán trước khi chạy

| Cặp | Câu A | Câu B | Dự đoán theo ngữ nghĩa | Cosine thực tế |
|---|---|---|---|---:|
| 1 | Sinh viên mượn sách tại thư viện. | Sinh viên mượn sách tại thư viện. | cao nhất: cùng một câu | 1.0000 |
| 2 | Sinh viên mượn sách tại thư viện. | Người học có thể mượn tài liệu ở thư viện. | cao về ngữ nghĩa | -0.0750 |
| 3 | Nhóm cần đặt phòng để cùng học bài. | Các bạn đăng ký phòng học nhóm. | cao về ngữ nghĩa | 0.2028 |
| 4 | Sinh viên phải gia hạn sách trước hạn trả. | Thư viện cung cấp máy in và máy quét. | trung bình: cùng chủ đề, khác dịch vụ | -0.0739 |
| 5 | Thư viện cho mượn sách. | Núi lửa phun trào tạo ra dung nham. | thấp nhất về ngữ nghĩa | -0.1249 |
