# Ảnh chụp từ USE–JaCaMo

USE 7.5.0, plugin 1.0.1, JDK 21.0.5. Mã USE tại 6d6a9ee6d075d234bd3c4764e34651bcb5ac0682. SHA-256 của plugin đã nạp là `46569E4095B9F5CCB1F7D7B7B1643611ACA11F3ADA462343503727DE2DDE3EF3`.

Ảnh lấy từ các thành phần Swing của phiên chạy thật. Hai sơ đồ OAL và iStarSCN được bố trí lại trên canvas USE để đưa đủ nút và cạnh vào khung hình. Ảnh theo bố trí ban đầu cũng có trong thư mục Auction. Các bảng Markings trong Word trích các hàng của AuctionGroup, còn ảnh đầy đủ của bảng được giữ trong thư mục tương ứng.

| Ca chụp | Mã phiên | Checkpoint | Bằng chứng |
| --- | --- | --- | --- |
| [Auction](auction-layout/) | `804fdea5-8cc1-42ed-aa24-2eeffa473d45` | 1–8, 47, 58 | Ảnh trạng thái và tiến độ ở các checkpoint có ghi trong chú thích. |
| [TN03 — Counter](counterbase/) | `d6df3077-0a2e-49fc-a88d-9fcfdaade723` | 3 | Nonnegative = FAIL, HOLD_FAILURE. |
| [TN05 — lỗi chuyển giao](goal/) | `9c465412-f709-4612-bfbb-dd3bab325c12` | 22 | Giá 10 tại checkpoint trước và 20 tại checkpoint giữ dừng. BidNeverIncreases = VIOLATED. |
| [TN06 — thiếu dữ liệu khi chuyển giao](missing-final/) | `c94699f1-5e04-4bdb-8217-05db0c6fb66c` | 18 | HOLD_UNVERIFIED. Thanh trạng thái báo ATTRIBUTE_VALUE_MISSING:Auction.best_bid. |
| [TN07 — giữ âm](counter/) | `98ba754b-edc4-494e-8fd1-cc950d023f76` | 3 | Console ghi −1. Nonnegative = FAIL, HOLD_FAILURE. |
| [TN07 — khôi phục](restored-final/) | `2c2c05ea-2244-47ff-a2fb-b2aba94333ce` | 3 | Console ghi −1 rồi 2. Nonnegative = PASS, APPROVE. |

Trong mỗi thư mục có ảnh PNG, log nguồn, vết yêu cầu/phản hồi và các checkpoint đã chọn. Vết TN01/TN02 và số liệu từ các thực nghiệm đã dẫn trong khóa luận vẫn được tham chiếu riêng.

| Hình | Ảnh | Trang in |
| --- | --- | --- |
| Hình 2.5 Giá tốt nhất của hai artifact Auction | [PNG](auction-layout/artifacts.png) | 34 |
| Hình 2.6 Sơ đồ đầy đủ của trạng thái Auction trong OAL State | [PNG](auction-layout/oal-compact.png) | 34 |
| Hình 2.7 Các checkpoint đầu của Auction | [PNG](auction-layout/timeline.png) | 38 |
| Hình 3.1 Lệnh Run experiment trong trình đơn JaCaMo | [PNG](auction-layout/menu.png) | 40 |
| Hình 3.2 Hộp thoại chọn gói auction.mrv | [PNG](auction-layout/mrv.png) | 40 |
| Hình 3.3 Theo dõi Auction trong thẻ Checkpoints | [PNG](auction-layout/terminal-timeline.png) | 41 |
| Hình 3.4 Giá công bố khi hai cuộc đấu giá đã đạt mục tiêu | [PNG](auction-layout/terminal-artifacts.png) | 42 |
| Hình 3.5 Sơ đồ iStarSCN đầy đủ của ngữ cảnh a1 | [PNG](auction-layout/istar-a1-compact.png) | 43 |
| Hình 3.6 Các Goal của AuctionGroup trong ngữ cảnh a1 | [PNG](auction-layout/auctiongroup-a1.png) | 43 |
| Hình 3.7 Các Goal của AuctionGroup trong ngữ cảnh a2 | [PNG](auction-layout/auctiongroup-a2.png) | 44 |
| Hình 3.8 Vi phạm bất biến Nonnegative trong TN03 | [PNG](counterbase/ocl.png) | 44 |
| Hình 3.9 Giá tốt nhất trước lượt trả giá kém hơn trong TN05 | [PNG](goal/before.png) | 45 |
| Hình 3.10 Giá tốt nhất sau lượt trả giá kém hơn trong TN05 | [PNG](goal/after.png) | 45 |
| Hình 3.11 Quyết định HOLD_FAILURE trong TN05 | [PNG](goal/hold.png) | 45 |
| Hình 3.12 Vi phạm Goal BidNeverIncreases trong ngữ cảnh a1 | [PNG](goal/auctiongroup.png) | 45 |
| Hình 3.13 Kết quả các bất biến CSL trong TN05 | [PNG](goal/invariants.png) | 45 |
| Hình 3.14 Quyết định HOLD_UNVERIFIED trong TN06 | [PNG](missing-final/hold.png) | 46 |
| Hình 3.15 Chẩn đoán thiếu thuộc tính Auction.best_bid | [PNG](missing-final/diagnostic.png) | 46 |
| Hình 3.16 Giá trị quan sát trong Console của phiên Counter giữ âm | [PNG](counter/console.png) | 46 |
| Hình 3.17 Bất biến Nonnegative khi Counter giữ giá trị âm | [PNG](counter/ocl.png) | 46 |
| Hình 3.18 Giá trị quan sát trong Console của phiên Counter khôi phục | [PNG](restored-final/console.png) | 47 |
| Hình 3.19 Bất biến Nonnegative sau khi Counter khôi phục giá trị | [PNG](restored-final/ocl.png) | 47 |
