# Bằng chứng thực nghiệm Chương 3 — 23/11/2026

Môi trường, commit và SHA-256 của JAR được ghi tại [environment.txt](environment.txt). Các ca GUI dùng bản cài USE 7.5.0 / plugin 1.0.1 qua bộ kiểm thử Swing dựa trên `EmbeddedUseSmoke.java`. Ảnh PNG gốc lấy từ cửa sổ USE đang chạy; ảnh chèn Word cắt từ các bản gốc. [QA/launcher.log](QA/launcher.log) ghi nhận launcher Windows của cùng bản đóng gói.

| Ca | Bằng chứng chính | Kết quả mới |
| --- | --- | --- |
| TN01 · 3868eb28-83b0-4ea5-9de0-78420f33e383 | [Lệnh](TN01/command.txt), [cấu hình chạy](TN01/session.txt), [log GUI](TN01/gui-run.log), [trace USE](TN01/run/consumer-history.jsonl), [log nguồn](TN01/run/producer.log), [receipt 58](TN01/run/checkpoint-58.json) và các receipt còn lại trong TN01/run. | 58/58 receipt khớp trace. Cả 58 quyết định APPROVE. Hai context AuctionCompleted FULFILLED ở checkpoint 58. |
| TN02 · chính vết TN01 | [Lệnh](TN02/command.txt), [hash đầu vào](TN02/inputs-sha256.txt), [kết quả](TN02/replay.json), [đối chiếu từng sequence](TN02/comparison.json). | 58/58 quyết định và 58/58 tập FULFILLED khớp. Không có hàng thiếu, sai khác hay HOLD. |
| TN03 · a0648d20-ec6f-4828-8340-db86cb0d208c | [Lệnh](TN03/command.txt), [cấu hình chạy](TN03/session.txt), [log GUI](TN03/gui-run.log), [trace USE](TN03/run/consumer-history.jsonl), [log nguồn](TN03/run/producer.log), [receipt 3](TN03/run/checkpoint-3.json). | Checkpoint 3 tại cuối plan cha +!run. value = −1, Nonnegative = FAIL, SafeValue = VIOLATED, HOLD_FAILURE. 3/3 receipt khớp trace. |
| TN04 · JUnit trực tiếp | [Lệnh](TN04/command.txt), [Maven](TN04/maven.log), [Surefire](TN04/TEST-org.tzi.use.plugins.jacamo.bridge.CslStateVerifierTest.xml) và [assertion của fixture](TN04/fixture.txt). | Một test qua. Snapshot thiếu ở sequence 2 được HOLD_UNVERIFIED và giữ một đối tượng; snapshot đầy đủ cùng sequence được APPROVE. |

## Ảnh và dữ liệu dùng trong Word

| Mã | Tệp gốc | Vị trí đối chiếu |
| --- | --- | --- |
| S01 | [Menu USE](TN01/S01-menu-verified.png) | Hình 3.1, kiểm tra lối vào riêng trên cùng bản cài, trước khi có checkpoint. |
| S02 | [Hộp thoại Auction](TN01/S02-configuration.png) | Hình 3.2, đầu vào của TN01 trước khi chạy. |
| S03 | [Project và Checkpoints](TN01/S03-auction-checkpoint.png) | Hình 3.3, TN01 checkpoint 58, đã cố định checkpoint. |
| S04 | [Artifacts và OAL State](TN01/S04-auction-oal.png) | Hình 3.4, TN01 checkpoint 58. Bảng 3.3 dùng UUID trong receipt. |
| S05a–b | [a1](TN01/S05a-auction-marking.png), [a2](TN01/S05b-auction-marking.png) | Hình 3.5–3.6, iStarSCN → Markings tại TN01 checkpoint 58. |
| S06a–b | [Plan cha](TN03/S06a-counter-checkpoint.png), [OCL và Artifacts](TN03/S06b-counter-ocl.png) | TN03 checkpoint 3. Hình 3.7 dùng S06b, bổ sung ranh giới plan từ receipt 3. |
| S07 (tùy chọn) | [Kết quả CLI](TN02/replay.log) và [JSON](TN02/replay.json) | Kết quả TN02 được trình bày bằng bảng và dữ liệu từng checkpoint. |

[TN01/source-comparison.tsv](TN01/source-comparison.tsv) xác nhận ASL, Java Artifact và đặc tả tổ chức trùng giữa nguồn chạy và ví dụ trong USE. Hai tệp .jcm chỉ chênh một dòng trống. Các checkpoint 39, 42 và 58 của TN01 dùng cho Bảng 3.4. [So sánh live/replay](TN02/comparison.json) ghi dữ liệu chi tiết của các mốc.

Mốc ngày 22/11 và các số trong doc/TESTING.md là số liệu tham chiếu, được ghi riêng trong mục 3.5. Các ca mở rộng TN05–TN06 nằm ngoài bốn ca cốt lõi của đợt thu bằng chứng này.

## Kiểm tra bản Word

[PDF được xuất bằng Word](QA/reviewed.pdf) và [chỉ mục số trang](QA/page-index.json). Chương 3 ở trang in 34–42, có 7 hình và 4 bảng. Chương 1–2 được đối chiếu nguyên khối XML với bản sao lưu; nội dung chữ phần Mở đầu trùng với bản gốc.
