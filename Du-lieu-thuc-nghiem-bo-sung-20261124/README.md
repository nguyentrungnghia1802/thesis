# Bằng chứng thực nghiệm bổ sung USE–JaCaMo

TN05–TN07 chạy ngày 24/11/2026 bằng dòng lệnh trên USE 7.5.0 và plugin 1.0.1 tại commit [c3f47cd38bb6](https://github.com/nguyentrungnghia1802/use/tree/c3f47cd38bb67d2de9581ab8fa221b547b326735). Phiên bản, lệnh build và SHA-256 của runtime trong [environment.txt](environment.txt).

| Nhóm | Mục đích | Thư mục |
| --- | --- | --- |
| TN05 | Đối chiếu giá tăng với giá hợp lệ trong nhóm plan và tại ranh giới chuyển giao | [Hợp lệ gom plan](TN05-hop-le-gom-plan), [Lỗi gom plan](TN05-loi-gom-plan), [Hợp lệ chuyển giao](TN05-hop-le-chuyen-giao), [Lỗi chuyển giao](TN05-loi-chuyen-giao) |
| TN06 | So sánh lỗi ánh xạ thiếu best_bid ở hai ranh giới | [Gom plan](TN06-thieu-gom-plan), [Chuyển giao](TN06-thieu-chuyen-giao) |
| TN07 | So sánh vi phạm Counter còn ở cuối nhóm với vi phạm được sửa trong nhóm | [Giữ âm](TN07-counter-giu-am), [Khôi phục](TN07-counter-khoi-phuc) |

Mỗi thư mục có log nguồn, vết yêu cầu/phản hồi nén gzip, receipt và tóm tắt. [summary.json](summary.json) giữ mã phiên, thứ tự, quyết định cuối và SHA-256 của vết trước khi nén. Giải nén consumer-history.jsonl.gz để đọc vết đầy đủ. mutation.diff.gz và boundary.diff.gz lưu nguyên bản các thay đổi trong bản sao Auction. Bản ASL và Java của mỗi ca Counter được lưu trực tiếp.

Cách chạy nằm trong phụ lục của tài liệu Word. Thư mục [scripts](scripts) chứa trình khởi chạy các ca có mốc chuyển giao và Counter.

Hình 2.5 trong tài liệu Word thuộc phiên chụp riêng và có hồ sơ tại [ảnh Chương 2](../Bang-chung-anh-Chuong-2-20261124-021329).
