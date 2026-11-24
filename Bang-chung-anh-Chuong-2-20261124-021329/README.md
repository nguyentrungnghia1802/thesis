# Ảnh Auction cho Chương 2

Phiên chụp dùng trong Word có run `db329b13-eba1-410c-8788-1d8b014ea019`, ngày 24/11/2026. USE 7.5.0 và plugin JaCaMo 1.0.1 được nạp từ bản ZIP vừa đóng gói ở commit USE `6d6a9ee6`. Bản ZIP được mở trong vùng staging vì thao tác thay thư mục `target/new` gặp một tệp JAR đang bị khóa.

Đường vào là **Plugins → JaCaMo → Run experiment...**. Bản này chọn gói `use-plugin/src/main/resources/example/auction/auction.mrv`. SHA-256 xác nhận bốn tệp `auction.jcm`, `attribute-mapping.xml`, `auction.csl` và `auction.istar` trong gói trùng với bốn tệp cạnh gói. Xem [inputs.json](inputs.json) và [hash của JAR và gói](phien-chinh-thuc/artifact-hashes.txt).

| Ảnh chèn | PNG gốc | Phạm vi |
| --- | --- | --- |
| Hình 2.2 | [CSL Model](phien-chinh-thuc/CSL-Model-original.png) | Cây và sơ đồ AuctionState, gồm các ngữ cảnh, vai trò và thuộc tính của Auction. |
| Hình 2.4 | [iStar Model](phien-chinh-thuc/iStar-Model-original.png) | Bản cắt tập trung vào AuctionGroup và ba nhánh AND. PNG gốc còn cho thấy vùng điều kiện của SafeBid. |
| Hình 2.5 | [Checkpoints](phien-chinh-thuc/Checkpoints-original.png) | Ảnh giữ hàng 1–8 và cả bảy cột. Hàng được chọn là checkpoint 1. |

Đối chiếu Hình 2.5 với [vết thực thi](phien-chinh-thuc/consumer-history.jsonl) và [receipt của checkpoint 1](phien-chinh-thuc/checkpoint-1.json). Số liệu TN01 và các kết quả đã ghi ở Chương 3 thuộc phiên trước. PDF kiểm tra bố cục được xuất trực tiếp bằng Word.
