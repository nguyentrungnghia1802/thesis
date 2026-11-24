# Ảnh và vết dùng cho bốn vị trí trong luận văn

Ảnh PNG gốc được kết xuất trực tiếp từ cửa sổ Swing của USE đang chạy ngày 24/11/2026. Các ảnh ghép trong Word chỉ lấy phần cắt từ những PNG gốc đã đối chiếu với trace và receipt. Chọn checkpoint trong lịch sử của chính phiên chạy rồi chuyển tab để giữ hai vùng Artifacts và USE Evaluation ở cùng mốc. Các ảnh không dùng replay.

USE 7.5.0, plugin JaCaMo 1.0.1, mã nguồn USE `6d6a9ee6`. Cấu hình thực nghiệm nạp qua **Plugins → JaCaMo → Run experiment...**. Các bản sao TN05 và TN06 được so với diff lưu trong `Du-lieu-thuc-nghiem-bo-sung-20261124`. Hai ca TN07 dùng lại ASL và Java từ hồ sơ đó. Các mã phiên trong mục dưới thuộc lần thu ảnh mới.

| Hình | Ca và phiên | Checkpoint | PNG gốc | Log và receipt dùng để đối chiếu |
| --- | --- | --- | --- | --- |
| 2.5 | Auction · `3ca479bf` | 45 | [Artifacts](Auction-trong-Word/source-original.png), [OAL State](Auction-trong-Word/oal-original.png) | [Trace](Auction-trong-Word/consumer-history.jsonl), [receipt 45](Auction-trong-Word/checkpoint-45.json). Giá nguồn và USE tương ứng là 12,25180855001036 (a1) và 61,79266359141802 (a2). |
| 3.8 | TN05-loi-chuyen-giao · `8ae8adb8` | 21 → 22 | [Giá trước](TN05-loi-chuyen-giao/before-original.png), [giá tại HOLD](TN05-loi-chuyen-giao/hold-original.png), [iStarSCN](TN05-loi-chuyen-giao/marking-original.png), [OCL](TN05-loi-chuyen-giao/ocl-original.png) | [Log](TN05-loi-chuyen-giao/producer.log), [receipt 21](TN05-loi-chuyen-giao/checkpoint-21.json), [receipt 22](TN05-loi-chuyen-giao/checkpoint-22.json). Giá 10 → 20, BidNeverIncreases VIOLATED, 17/17 lần kiểm tra bất biến PASS, HOLD_FAILURE. |
| 3.9 | TN06-thieu-chuyen-giao · `0ad85523` | 18 | [Checkpoints, trạng thái và Console](TN06-thieu-chuyen-giao/hold-original.png) | [Log của USE](TN06-thieu-chuyen-giao/execution.log), [log nguồn](TN06-thieu-chuyen-giao/producer.log), [receipt 18](TN06-thieu-chuyen-giao/checkpoint-18.json). Dòng HOLD trong bảng hiển thị “?” khi phép chiếu thất bại và không tạo được đối tượng kết quả. Console, trace và receipt cho biết sequence 18. |
| 3.10 | TN07-counter-giu-am · `91765262` | 3 | [Console và OCL](TN07-counter-giu-am/counter-original.png), [Checkpoints](TN07-counter-giu-am/checkpoints-original.png) | [Log](TN07-counter-giu-am/producer.log), [receipt 3](TN07-counter-giu-am/checkpoint-3.json). -1 ở cuối nhóm, Nonnegative FAIL và HOLD_FAILURE. |
| 3.11 | TN07-counter-khoi-phuc · `a17facf2` | 3 | [Console và OCL](TN07-counter-khoi-phuc/counter-original.png), [Checkpoints](TN07-counter-khoi-phuc/checkpoints-original.png) | [Log](TN07-counter-khoi-phuc/producer.log), [receipt 3](TN07-counter-khoi-phuc/checkpoint-3.json). Sau -1, Counter trở về 2 trước biên, Nonnegative PASS và APPROVE. |

Thẻ Artifacts hiển thị giá khởi tạo của một số vết dưới dạng số thập phân dài, nên Hình 2.5 dùng checkpoint mà hai giá đã thay đổi và đều đọc được. Số liệu TN01 của đoạn văn được giữ nguyên. [Bản kê mã phiên đầy đủ và checkpoint](figure-evidence.json).

[PDF kiểm tra bản Word đã lưu](delivered.pdf). Các ảnh mới nằm ở trang in 33 và 53–55.
