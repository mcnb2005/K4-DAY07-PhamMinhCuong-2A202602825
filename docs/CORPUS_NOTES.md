# Nguồn dữ liệu — UIT + Thư viện Trung tâm + KTX ĐHQG-HCM

Bộ mặc định từ lượt thay đổi này là **data/uit-vnuhcm/**, theo lựa chọn rõ ràng của người dùng từ danh sách nguồn họ gửi. Có **7 file, 6 URL gốc, 6 chủ đề**, không có tài liệu VinUni trong lượt benchmark mới.

Các file là **bản tóm lược tiếng Việt có đối chiếu nguồn**, không phải bản sao toàn văn hoặc văn bản do trường ban hành. Chỉ chọn thông tin cần thiết; không bịa con số khi trang chỉ dẫn đến file đính kèm. Các URL trong nội dung hướng dẫn là thông tin tham khảo, không đăng nhập hoặc thực hiện thủ tục thay người dùng.

## 1. Danh mục

| File | Trang chính thức / mục | Đối tượng | Phiên bản |
|---|---|---|---|
| uit-dang-ky-hoc-phan.md | [Quy trình sinh viên UIT](https://daa.uit.edu.vn/mot-so-quy-trinh-danh-cho-sinh-vien), mục 2 | student | not-stated |
| uit-phuc-khao-sinh-vien.md | [Quy trình sinh viên UIT](https://daa.uit.edu.vn/mot-so-quy-trinh-danh-cho-sinh-vien), mục 9 | student | not-stated |
| uit-phuc-khao-giang-vien.md | [Quy trình cán bộ giảng dạy](https://daa.uit.edu.vn/content/quy-trinh-danh-cho-can-bo-giang-day), mục 6 | faculty | not-stated |
| uit-hoc-phi-he-2025-2026.md | [Thông báo học phí học kỳ hè](https://khtc.uit.edu.vn/content/2025-2026-thong-bao-thu-hoc-phi-hoc-ky-he-nh-2025-2026) | student | 21/07/2026; hè 2025-2026 |
| uit-hoc-bong-global-2026.md | [Thông báo UIT Global](https://ctsv.uit.edu.vn/bai-viet/thong-bao-trien-khai-hoc-bong-uit-global-tu-hoc-ky-1-nam-hoc-2026-2027) | student | 803/QĐ-ĐHCNTT; hiệu lực 01/09/2026 |
| vnulib-muon-tra.md | [Mượn trả tại TVTT/KTX B](https://www.vnulib.edu.vn/index.php/muon-tra-tai-lieu-tvtt) | all | not-stated |
| ktx-gia-han-2026-2027.md | [Hướng dẫn gia hạn nội trú](https://huongdan.ktxhcm.edu.vn/huong-dan/huong-dan-sinh-vien-dang-noi-tru-thuc-hien-gia-han) | student | 2026-2027; dẫn Thông báo 505 ngày 22/07/2026 |

Mọi file có retrieved_at=2026-09-19. Ngày này là ngày lấy, không phải ngày hiệu lực. [sources.csv](../data/uit-vnuhcm/sources.csv) kiểm kê một dòng cho mỗi file.

## 2. Cách xác minh

- Các trang UIT đã được mở bằng công cụ web; đọc nội dung cụ thể thay vì suy ra từ tên chuyên mục.
- Link thư viện trong tài liệu gợi ý có đường dẫn cũ. Tìm được trang mượn trả hiện có ở đường dẫn trong bảng, rồi đọc trực tiếp bằng HTTP; máy chủ trả **200**. robots.txt trả **404** (không có tệp); RobotFileParser xử lý theo quy tắc cho phép khi không có tệp. Không coi lỗi 502 của công cụ web là bằng chứng trang nguồn không tồn tại.
- robots.txt của huongdan.ktxhcm.edu.vn cho phép đường dẫn hướng dẫn đã chọn; trang gia hạn được đọc trực tiếp và trả **200**. Đối chiếu phần thanh toán và đối tượng đang nội trú trong HTML gốc.
- Không crawl toàn website, không dùng trang có danh sách hồ sơ cá nhân, không lấy số CCCD/tài khoản thật hoặc nội dung sau đăng nhập. Các bản HTML tạm để xác minh nằm trong .tools, được Git bỏ qua.
- Nhãn public-source; paraphrased-study-note mô tả cách sử dụng, không tuyên bố website có giấy phép mở hay cấp quyền sao chép toàn bộ.

## 3. Phạm vi và phiên bản

**Học phí:** câu hỏi gắn rõ kỳ hè năm học 2025-2026. Đợt thu trong thông báo đã kết thúc trước ngày lấy nguồn. Lưu làm dữ liệu lịch sử để thử truy xuất theo thời kỳ, không diễn giải thành hạn nộp học phí hiện tại. Không lấy mức tiền từ một trang chỉ có tệp đính kèm mà chưa đọc tệp.

**Học bổng:** dùng quy định 803 có hiệu lực từ 01/09/2026 theo trang gốc. Không dùng quy định 1026 năm 2025 như thể còn là cùng phiên bản. Bộ này chọn UIT Global, không suy diễn điều kiện của học bổng khuyến khích học tập khác.

**KTX:** tài liệu áp dụng cho sinh viên đã ở năm 2025-2026 muốn gia hạn sang 2026-2027. Không dùng hạn thanh toán của đăng ký ở mới cho gia hạn hoặc ngược lại.

**Thư viện:** thông tin thuộc Thư viện Trung tâm ĐHQG-HCM, không tự áp cho thư viện riêng của UIT. Nhóm chính quy và ngoài ĐHQG-HCM có quyền khác nhau, được mô tả trong phần thân. audience=all nghĩa là tài liệu bao gồm nhiều nhóm chứ không có nghĩa mọi nhóm cùng hạn mức.

**DAA:** trang quy trình không ghi phiên bản riêng cho từng mục, nên document_version=not-stated. Không tự thêm số ngày nộp đơn hoặc lệ phí phúc khảo cụ thể khi mục sinh viên không nêu.

## 4. Metadata để tránh trộn trường

university phân biệt UIT và VNU-HCM; institution chỉ rõ UIT, VNU-HCM-Central-Library hoặc VNU-HCM-Dormitory. category dùng sáu nhãn trong tài liệu gợi ý của người dùng. source_section ghi phần đã tóm lược khi trang chứa nhiều mục.

Các trường này được giữ trên mỗi chunk và có thể truyền vào search_with_filter. Bộ lọc thực nghiệm Q1 chỉ dùng audience=student để quan sát riêng tác động loại giảng viên. Không khẳng định đã thử lọc kết hợp university/category hoặc rằng ba trường được tự động suy ra từ câu hỏi.

## 5. Câu hỏi và giới hạn đánh giá

[data/uit-vnuhcm-queries.json](../data/uit-vnuhcm-queries.json) có đúng 5 câu cùng đáp án và cụm bằng chứng. Năm câu hỏi kiểm phúc khảo, học phí, học bổng, thư viện và KTX; tài liệu đăng ký học phần là nguồn nền/ứng viên gây nhiễu.

Bộ mới dài hơn bộ VinUni trước nhưng vẫn chỉ là tập học tập nhỏ, đã tóm lược. Mock không mã hóa ngữ nghĩa; kết quả thấp phản ánh giới hạn mô phỏng, không chứng minh bộ dữ liệu sai hay nguồn chính thức kém chất lượng. Chạy mô hình thật và đọc câu trả lời có dẫn nguồn trước khi đánh giá khả năng tư vấn thực tế.

## 6. Dữ liệu cũ

Bộ VinUni không bị xóa: data/vinuni-library và data/benchmark_queries.json giữ để tái lập lượt cũ. Báo cáo và kết quả cũ nằm ở [kho lưu VinUni](../report/archive/vinuni/benchmark.md). Lệnh python bench.py hiện mặc định chỉ nạp bộ UIT/ĐHQG-HCM.
