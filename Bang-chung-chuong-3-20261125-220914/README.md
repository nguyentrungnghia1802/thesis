# Bằng chứng cho Chương 3 và Mục 2.6.3

Ảnh thu từ USE 7.5.0, plugin JaCaMo 1.0.1 và JDK 21.0.5 trên Windows 11. Checkout USE tại `6d6a9ee6d075d234bd3c4764e34651bcb5ac0682`.

- SHA-256 của JAR plugin `46569e4095b9f5ccb1f7d7b7b1643611aca11f3ada462343503727de2dde3ef3`.
- SHA-256 của JAR JaCaMo `dede2e2cde568c747a774e33f821cdcee6501515997a710816aa9c02c7c901f5`.

## Phiên chụp và bằng chứng đầu vào

| Ca chụp | Mã lần chạy | Checkpoint trong hình | Hình |
| --- | --- | --- | --- |
| [Mở gói và chọn một checkpoint](TN01-trinhbay/) | `5acdfd2b-88d2-4c55-959a-2fd70450bde0` | 58 sau khi mở gói | 3.1–3.3 |
| [Auction tại mốc lệch tiến độ và mốc cuối](TN01-in/) | `98170b4f-83e5-44d5-91c1-dae4b48d4da2` | 41 và 58 | 3.4–3.7 |
| [Counter cơ bản](TN03-in/) | `8b4f7da3-b16a-4aab-bd63-d27362cea888` | 3 | 3.8 |
| [Auction lỗi ở mốc chuyển giao, kèm đối chiếu Moise–OAL](TN05-chuyen-giao/) | `26400acd-d4e9-49b7-b7ae-9a9e6e6c0be1` | 21 và 22 | 2.7–2.8 và 3.9–3.13 |
| [Auction thiếu giá tốt nhất](TN06-chuyen-giao-trinhbay/) | `b8241f0f-ea21-42f9-97a3-7ab4c9e1cce0` | 18 | 3.14 |
| [Counter giữ giá trị âm](TN07-giu-am-in/) | `54271a7f-cc8a-40d3-bc2b-425d1ef79033` | 3 | 3.15–3.16 |
| [Counter khôi phục giá trị](TN07-khoi-phuc-in/) | `769f1728-9f47-47d5-a134-03a737bb73df` | 3 | 3.17–3.18 |

Mỗi thư mục ca chụp chứa PNG gốc, lệnh chạy, mã băm của gói MRV, log nguồn, vết USE và xác nhận checkpoint phía JaCaMo. Ảnh các thẻ USE được kết xuất từ giao diện Swing đang chạy. Những phần cắt giữ nguyên các dòng, nhãn và giá trị hiển thị.

Hai ảnh tổ chức thuộc lần chạy TN05 ở checkpoint 22. Trình quan sát Moise đọc nhóm agrp trong lúc JaCaMo đang giữ dừng. Ảnh OAL lấy từ dữ liệu USE ở cùng checkpoint. Vết xác nhận bob đảm nhiệm auctioneer trong agrp và trạng thái đích có hai liên kết tương ứng. Ảnh chèn đánh dấu ba thành phần, còn ảnh và HTML thô nằm trong thư mục ca chụp.

## Kiểm thử và đối chiếu vết

- [TN02](TN02/) lưu lệnh đánh giá lại, kết quả và so sánh từng checkpoint. Ca này dùng cùng vết gốc 3868eb28 và đặc tả đã lưu. Có 58/58 quyết định và 58/58 tập Goal, Task đã đạt theo ngữ cảnh khớp. Bản xác nhận phía nguồn cũng trùng vết gốc ở 58/58 mốc.
- [TN04](TN04/) lưu báo cáo JUnit và vết của ba lần gửi ảnh vào bộ kiểm chứng. Vết bổ sung ghi cùng đối tượng Gauge giữ nguyên giá trị 1 khi ảnh thiếu, rồi nhận giá trị 2 ở lần đánh giá ảnh đầy đủ.
- [TN05 đối chứng](TN05-doi-chung.json) đối chiếu bốn vết nguồn đã lưu trong Du-lieu-thuc-nghiem-bo-sung-20261124.

## Ảnh đưa vào Word

| Hình | Ảnh PNG chèn | Trang in |
| --- | --- | --- |
| Hình 2.7 Vai trò trong nhóm agrp trên Moise | [PNG](hinh-chen/moise-org.png) | 39 |
| Hình 2.8 Tác tử, vai trò và nhóm trong OAL State | [PNG](hinh-chen/oal-org.png) | 39 |
| Hình 3.1 Mở chức năng thực nghiệm JaCaMo | [PNG](hinh-chen/menu.png) | 45 |
| Hình 3.2 Hộp thoại chọn gói Auction | [PNG](hinh-chen/mrv.png) | 45 |
| Hình 3.3 Cửa sổ thực nghiệm tại checkpoint được chọn | [PNG](hinh-chen/workbench.png) | 46 |
| Hình 3.4 Tiến độ ObserveBid của a1 | [PNG](hinh-chen/auction-mid-a1.png) | 48 |
| Hình 3.5 Tiến độ ObserveBid của a2 | [PNG](hinh-chen/auction-mid-a2.png) | 48 |
| Hình 3.6 Kết quả AuctionCompleted của a1 | [PNG](hinh-chen/auction-final-a1.png) | 49 |
| Hình 3.7 Kết quả AuctionCompleted của a2 | [PNG](hinh-chen/auction-final-a2.png) | 49 |
| Hình 3.8 Giá trị bộ đếm và kết quả TN03 | [PNG](hinh-chen/counter.png) | 50 |
| Hình 3.9 Giá tốt nhất trước lượt trả giá kém hơn | [PNG](hinh-chen/bid-before.png) | 51 |
| Hình 3.10 Giá tốt nhất sau lượt trả giá kém hơn | [PNG](hinh-chen/bid-after.png) | 51 |
| Hình 3.11 Vi phạm mục tiêu giữ giá không tăng | [PNG](hinh-chen/bid-goal.png) | 51 |
| Hình 3.12 Kết quả bất biến CSL trong TN05 | [PNG](hinh-chen/bid-ocl.png) | 52 |
| Hình 3.13 Quyết định tại mốc chuyển giao trong TN05 | [PNG](hinh-chen/bid-hold.png) | 52 |
| Hình 3.14 Giữ dừng vì thiếu giá tốt nhất trong TN06 | [PNG](hinh-chen/missing.png) | 53 |
| Hình 3.15 Log giá trị của phiên Counter giữ âm | [PNG](hinh-chen/negative-console.png) | 54 |
| Hình 3.16 Giá trị âm tại checkpoint của TN07 | [PNG](hinh-chen/negative-checkpoint.png) | 54 |
| Hình 3.17 Log giá trị của phiên Counter khôi phục | [PNG](hinh-chen/recovered-console.png) | 54 |
| Hình 3.18 Giá trị đã khôi phục tại checkpoint | [PNG](hinh-chen/recovered-checkpoint.png) | 54 |
