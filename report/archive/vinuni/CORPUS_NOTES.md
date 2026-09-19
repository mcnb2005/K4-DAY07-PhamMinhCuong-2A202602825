# Ghi chú bộ dữ liệu VinUni Library

Ngày đọc nguồn: **2026-09-19**. Corpus dùng trong benchmark là `data/vinuni-library/`, gồm **5 bản tóm lược tiếng Việt**, không phải bản sao đầy đủ hay bản dịch chính thức của quy định. Chỉ giữ thông tin cần cho bài thực hành. Các file mẫu `data/university/` có URL example.edu không được đưa vào benchmark.

## Nguồn và cách chọn

| File | Phần nguồn được sử dụng | Phạm vi |
|---|---|---|
| student-borrowing.md | [Undergraduate students and staff](https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/) — Borrowing privileges | Chỉ phần sinh viên bậc đại học |
| faculty-borrowing.md | [Library Access & Services Policy](https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/) — 2.2 | Giảng viên VinUni; V4.0, ban hành 09/07/2025 |
| course-reserve.md | [Course Reserve](https://library.vinuni.edu.vn/course-reserve/) — Faculty/Staff/instructors | Quy trình đề nghị tài liệu của giảng viên |
| room-booking.md | [Room booking](https://library.vinuni.edu.vn/room-booking/) — điều kiện sử dụng | Sinh viên, giảng viên, nhân viên |
| hours-access.md | [Hours and access](https://library.vinuni.edu.vn/about-us/hours-and-access/) — Access | Đối tượng được dùng không gian 24/7 |

Metadata `audience` biểu thị phạm vi của **bản tóm lược**, không suy ra máy móc từ tên trang. Ví dụ trang đầu có cả nhân viên nhưng file chỉ tóm lược phần undergraduate. `all` ở đây là các nhóm người dùng hợp lệ của trường, không có nghĩa mọi người ngoài trường đều được truy cập.

Không suy đoán phiên bản khi trang không nêu: ghi `document_version: not-stated`. `retrieved_at` là ngày đọc, không phải ngày có hiệu lực. `sources.csv` kiểm kê một dòng cho mỗi file. Các tài liệu chỉ có thông tin dịch vụ công khai, không có tài khoản hoặc dữ liệu cá nhân.

## Cách thu thập

Đọc các trang công khai bằng công cụ web, tự viết bản tóm lược ngắn và đối chiếu con số với nguồn. Không chạy script crawl toàn website. Đã thử đọc robots.txt bằng công cụ web nhưng công cụ không truy cập được; vì vậy không khẳng định đã xác minh quyền crawl tự động. Nhãn `public-source; paraphrased-study-note` chỉ mô tả nguồn và cách xử lý, không tuyên bố nguồn có giấy phép mở. Website hiển thị thông báo bản quyền.

## Khác biệt giữa nguồn

- Trang Hours and access có lịch theo tháng nhưng không ghi năm. Corpus giữ nguyên điều kiện này; Q4 chỉ hỏi đối tượng truy cập sau giờ đóng cửa, không dùng lịch đó làm khẳng định về giờ mở cửa hiện tại.
- Phần Course Reserve dành cho sinh viên và bảng trong chính sách V4.0 có hạn mức khác nhau. Corpus chỉ lấy phần thủ tục giảng viên; Q5 không hỏi hạn mức sinh viên.
- Trang thông tin graduate/faculty cũ có điều khoản gia hạn, thiết bị và phí khác chính sách V4.0. Không đưa các điều khoản đó vào corpus hoặc tự hòa giải chúng.

Các khác biệt này là lý do phải lưu nguồn, phiên bản và đối tượng áp dụng, thay vì gộp mọi nội dung có chữ “thư viện” vào một tài liệu.

## Giới hạn

Corpus nhỏ và đã tóm lược có chủ đích nên dễ hơn tài liệu thực tế dài, nhiều bảng và ngoại lệ. Benchmark chỉ là snapshot học tập. Cần kiểm tra lại nguồn trước khi dùng để tư vấn dịch vụ thật. Bộ lọc bằng dấu bằng không tự bao gồm `audience=all`; dùng student cho mọi câu hỏi sẽ loại cả tài liệu chung cần thiết ở Q3/Q4.
