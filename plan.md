# Kế hoạch hoàn thiện Chương 3 — Triển khai và thực nghiệm

Hoàn thiện Chương 3 trong [thesis - fixx.docx](<thesis - fixx.docx>) theo mục lục hiện có. Chương 2 đã giải thích phương pháp, ánh xạ, checkpoint và ngữ nghĩa Goal/Task. Chương 3 cần cho thấy phương pháp được hiện thực ở đâu, chạy được với đầu vào nào và bằng chứng thực nghiệm cho phép kết luận đến mức nào. Kế hoạch này mô tả công việc cần thực hiện. Các kết quả kỳ vọng phải được đối chiếu với ảnh, log hoặc báo cáo của lần chạy được dùng trong bản thảo.

## Cách vận dụng bố cục của Nguyễn Đức Quyền

- **Trang 44–45, mục 3.1–3.2.** Tác giả nêu mục đích thực nghiệm rồi đi từ yêu cầu môi trường, đóng gói đến xác nhận plugin xuất hiện trong USE. Hình 3.1 và 3.2 phục vụ hai việc khác nhau: xác nhận cấu trúc bản cài và xác nhận lối vào trên giao diện. Với USE–JaCaMo, ảnh nên tập trung vào lối vào plugin và cấu hình chạy giúp người đọc lặp lại thực nghiệm.
- **Trang 46–47, mục 3.3.** Hình 3.3 cho biết đầu vào được xử lý ở đâu, còn Hình 3.4 chỉ vị trí đầu vào, công cụ và đầu ra trên giao diện thật. Các biến thể Point of Sale tăng dần từ ca đơn giản đến ca có thêm luồng và lỗi. Chương này dùng cách tiến từ phiên Auction bình thường sang replay, Counter và ca thiếu dữ liệu. Mỗi ca cần chỉ rõ phần nào thay đổi và bằng chứng nào phân biệt được các kết quả.
- **Trang 48–52, mục 3.4–3.7.** Tác giả đặt tiêu chí, nêu phần đạt và phần còn thiếu, dùng bảng để tổng hợp, rồi gắn hướng mở rộng với hạn chế. Đối với USE–JaCaMo, đối chiếu chính là hành vi dự kiến với hành vi quan sát được, các context cùng kiểu và hai cách đánh giá cùng một vết. Tiêu chí lấy từ yêu cầu kiểm chứng ở Chương 2. [Khóa luận của Nguyễn Đức Quyền, Chương 3, trang in 44–52](<1, Tham Khảo/CNTT20_21020388_NguyenDucQuyen.pdf>)

## 3.1. Giới thiệu

- [ ] Viết một đoạn ngắn nối từ Chương 2. Câu hỏi của chương là công cụ có theo dõi riêng hai thực thể cùng kiểu, quyết định đúng theo bằng chứng ở checkpoint và tái hiện quyết định khi đánh giá lại cùng vết hay không.
- [ ] Nêu vai trò của từng ca trong một đoạn. Auction kiểm tra luồng từ JaCaMo đến USE/iStar và định danh. Replay kiểm tra khả năng đối chiếu vết. Counter minh họa vi phạm ở ranh giới quan sát. Ca kiểm thử snapshot thiếu kiểm tra cách giữ dừng khi dữ liệu chưa đủ.
- [ ] Dẫn đường đọc theo các mục 3.2–3.7. Kết quả và các số liệu cụ thể trình bày ở mục 3.5.

## 3.2. Triển khai công cụ

### 3.2.1. Tổ chức các thành phần

- [ ] Trình bày ngắn bốn module Maven: `use-core`, `use-gui`, `use-plugin`, `use-assembly`. Giải thích vì sao phần hiển thị/kiểm chứng nằm phía USE và phần thực thi/thu trạng thái nằm ở JVM JaCaMo riêng. Thêm một bảng nhỏ gồm thành phần, trách nhiệm, đầu vào/đầu ra và vị trí mã nguồn.
- [ ] Đọc mã theo một lượt từ mở phiên đến checkpoint đầu tiên. Khi trích mã, chọn đoạn ngắn từ commit thực nghiệm, chẳng hạn một luật XML ánh xạ và một đoạn kiểm tra có ý nghĩa giải thích. Nếu cần minh họa kiến trúc, dùng sơ đồ gọn chỉ hai tiến trình, bốn tệp đầu vào, hướng truyền snapshot và hướng trả quyết định. Dẫn lại Chương 2 cho chi tiết thuật toán.
- [ ] Kiểm tra các điểm sau trước khi viết về cách hiện thực. Các lớp trong bảng thuộc `use-plugin/src/main/java/org/tzi/use/plugins/jacamo/` của kho USE, trừ nơi ghi khác.

| Mạch đọc mã | Cần xác nhận để viết |
| --- | --- |
| `entrypoint/JaCaMoPlugin`, `JaCaMoExperimentAction`, `gui/main/RunDialog`, `ExperimentWindow` | Đường vào từ menu USE, tệp người dùng chọn, các thao tác Run, Stop, Restart và các vùng giao diện. |
| `session/VerificationSession`, `ProducerProcess`, `runtime/StateProducer`, `JaCaMoCheckpoints` | Cách khởi chạy tiến trình nguồn, mốc lấy snapshot, mốc trả quyết định và nơi lưu bằng chứng hai phía. Xem `ExecutionBarrier` trong `checkpoint-dependencies/runtime` ở kho JaCaMo nếu cần giải thích điều kiện giữ dừng. |
| `bridge/mapping/AttributeMapping`, `SnapshotProjection`, `session/SnapshotVerifier`, `verify/use75/NativeOclBackend` | Nơi đọc XML, dựng đối tượng/link CSL trong MSystem, áp dụng ràng buộc OCL và phân loại kết quả checkpoint. |
| `verify/istar/GoalTaskSession`, `org.vnu.sme.goal.verify.istar.IStarMarking`, `gui/views/UseEvaluationPanel`, `entrypoint/ReplayMain` | Nơi lưu lịch sử Goal/Task theo context, cách giao diện hiển thị checkpoint đã chọn, cách replay tính lại kết quả và dừng ở HOLD đầu tiên. |

### 3.2.2. Môi trường và cách khởi chạy

- [ ] Ghi hệ điều hành, ngày chạy, JDK/Maven/Python thực tế, phiên bản USE/plugin, commit của hai kho và phiên bản hoặc SHA-256 của JAR checkpoint **thực sự được nạp**. Mốc tài liệu là USE 7.5.0, plugin 1.0.1, JDK 21 và Maven 3.9. Nếu dùng bản khác, ghi đúng phiên bản và phân tích kết quả theo bản đó. Bản đóng gói lấy runtime từ `bridge/state`. Nếu sửa runtime trong kho JaCaMo, build và nhập lại JAR trước khi đánh giá thay đổi.
- [ ] Xác nhận bản đóng gói mở được USE và menu **Plugins → JaCaMo → Run experiment...** hoạt động. Mở hộp thoại **Run JaCaMo in USE** và điền bốn đầu vào bắt buộc: project `.jcm`, XML ánh xạ, `.csl`, `.istar`. Nếu Java Artifact nằm ngoài `src/env` cạnh `.jcm`, chọn **Artifact Java sources (optional)**. Chụp cấu hình trước khi bấm **Run**.
- [ ] Chụp ảnh S01–S02 ở phần danh sách ảnh. Mô tả giao diện bằng một đoạn theo thứ tự: project và dữ liệu nguồn ở trái, mô hình/trạng thái/OCL/iStar ở phải, checkpoint và quyết định ở vùng kết quả. Nếu kiểm tra **Stop/Restart**, lưu log tách phiên cũ/mới và ghi rõ đây là kiểm tra vòng đời.
- [ ] Để người khác tái lập, ghi lệnh build và lối vào đã dùng. Lệnh dưới đây theo README của kho USE, chạy từ thư mục có `pom.xml`. Trên Windows, mở `use-assembly/target/new/bin/start_use.bat`.

```bash
java -version
mvn -version
python3 use-plugin/tools/install-runtime.py
mvn -B package -Dmaven.test.skip=true
bash use-assembly/target/new/bin/use
```

Build trên bỏ qua test. Với phép thử tự động, lưu lệnh và báo cáo Surefire riêng. Nếu dùng CLI, ghi cả lệnh `java` và classpath thực tế. Thứ tự tham số của `WorkbenchMain` là `project.jcm mapping.xml model.csl model.istar [--headless] [--seconds=N] [--artifact-source=DIR]`. Có thể đặt `-Duse.state.work=<thư_mục_phiên>` trước tên lớp Java để chủ động lưu dữ liệu. Với chế độ desktop, tìm thư mục bằng chứng qua dòng **Run evidence** trong tab **Console**.

## 3.3. Kịch bản thử nghiệm

Mỗi ca cần một phiếu ngắn gồm **mã ca, điều cần kiểm chứng, đầu vào và thay đổi so với bản gốc, bước chạy, kết quả kỳ vọng, bằng chứng và kết quả quan sát**. Ghi kỳ vọng trước khi chạy. Khi tìm kết quả, đối chiếu điều kiện độc lập từ mã nguồn/fixture và đặc tả, rồi mới kiểm tra quyết định của plugin.

### 3.3.1. Chạy Auction và đánh giá lại vết

| Mã ca | Thao tác và kỳ vọng | Dữ liệu cần lưu |
| --- | --- | --- |
| **TN01 — Auction live** | Mở bộ `auction.jcm`, `attribute-mapping.xml`, `auction.csl`, `auction.istar` từ cùng một cấu hình đã xác nhận. Kiểm tra hai auction `a1`, `a2` cùng kiểu nguồn `AuctionArtifact`. Chọn các checkpoint cho thấy giai đoạn trước khi hoàn tất, một thay đổi giá quan sát được và thời điểm hai context đã đạt `AuctionCompleted`. Dựa trên `AuctionArtifact.java`, mapping và đặc tả để đối chiếu `running`, `best_bid`, `winner` theo từng context. Tìm một mốc minh họa `APPROVE` khi Goal/Task còn `PENDING` nếu vết có mốc đó. | `consumer-history.jsonl`, các receipt `checkpoint-<sequence>.json`, log phiên và ảnh S03–S05. Lập bảng liên kết tên artifact, identity nguồn, đối tượng USE và khóa context của iStar. Dùng log cho những trường giao diện chỉ hiển thị tên. |
| **TN02 — Replay cùng vết** | Dùng `ReplayMain` với đúng ba tệp mapping/CSL/iStar của TN01 và `consumer-history.jsonl` từ chính phiên được phân tích. Đối chiếu theo `sequence`: quyết định, HOLD đầu tiên nếu có và tập phần tử `FULFILLED` theo bộ `(context, actor, element)`, ưu tiên `AuctionCompleted` của cả hai context. Replay tạo bộ đánh giá mới trên tiền tố vết đã lưu và dừng khi gặp HOLD đầu tiên. | Lệnh chạy, SHA-256 của vết và ba tệp đặc tả, tệp kết quả JSON, bảng live/replay và ảnh S07 nếu chọn dùng hình terminal. Lớp `ReplayMain` nhận `mapping.xml model.csl model.istar history.jsonl output.json`. |

- [ ] Chốt đường dẫn bộ ví dụ. Dùng `use-plugin/src/main/resources/example/auction/` hoặc bản đóng gói tương ứng. Nếu dùng `jacamo/examples/auction` làm nguồn như phiên tài liệu, kiểm tra chênh lệch .jcm, ASL và Java so với bản trong USE, ghi rõ nguồn từng tệp.
- [ ] Trích các hàng từ vết thực tế để minh họa quá trình. Các checkpoint minh họa ở Chương 2 giải thích phương pháp. Chương 3 cần dùng số thứ tự và trạng thái quan sát được từ phiên đã chọn. Nếu hai auction không cùng hoàn tất trong vết, ghi kết quả đó và xem log trước khi chọn chạy lại.
- [ ] Nếu có thời gian, lặp TN01 vài lần với cùng bản build và cấu hình, ghi riêng số checkpoint, quyết định và kết quả theo context của mỗi lần. Dùng độ dao động như mô tả thực nghiệm vì lịch chạy có thể thay đổi.

### 3.3.2. Vi phạm ràng buộc và thiếu dữ liệu

| Mã ca | Thao tác và kỳ vọng | Dữ liệu cần lưu |
| --- | --- | --- |
| **TN03 — Counter live** | Mở bộ `counter.jcm`, `attribute-mapping.xml`, `counter.csl`, `counter.istar` từ ví dụ Counter. Đọc `counter.asl`: các plan con đồng bộ kết thúc với `set(-1)` trong nhóm cha `run`. Tại checkpoint quan sát được `value = -1`, đối chiếu bất biến `Nonnegative: self.value >= 0` có `FAIL`, quyết định `HOLD_FAILURE` và receipt phía nguồn. Báo cáo cũ ghi checkpoint 3 ở cuối plan cha. Dùng sequence thật của lần chạy mới. | Bản đặc tả/mã nguồn đã dùng, ảnh S06, dòng log trước và tại HOLD, receipt có quyết định cùng sequence và dữ liệu `value`. Nếu cần chứng minh hoạt động phía sau HOLD chưa chạy, bổ sung ca có dấu mốc được định nghĩa trước và nêu rõ cấu hình của ca đó. |
| **TN04 — Snapshot thiếu** | Chạy ca `CslStateVerifierTest#incompleteCoverageCannotDeleteObjectsOrCertifyEmptyState`. Fixture nạp snapshot đầy đủ có một đối tượng ở sequence 1, rồi snapshot `complete=false` với danh sách rỗng ở sequence 2. Kỳ vọng `HOLD_UNVERIFIED` và vẫn còn đối tượng của trạng thái trước; fixture còn kiểm tra một snapshot đầy đủ ở sequence 2 được `APPROVE`. Đây là phép thử trực tiếp bộ kiểm chứng. | Báo cáo Surefire, tên ca chạy, điều kiện fixture và assertion. Trình bày bảng trước/sau hoặc trích fixture ngắn có nguồn. Nếu cần bằng chứng mạnh hơn về giá trị/identity của đối tượng, xuất hoặc xác nhận các giá trị đó bên cạnh assertion hiện có về số lượng. |

Lệnh chạy riêng TN04 theo mẫu Maven trong `doc/TESTING.md`, sau khi nhập runtime:

```bash
mvn -B -pl use-plugin -am test \
  '-Dtest=CslStateVerifierTest#incompleteCoverageCannotDeleteObjectsOrCertifyEmptyState' \
  -Dsurefire.failIfNoSpecifiedTests=false -DfailIfNoTests=false
```

### Ca mở rộng nếu cần làm rõ phạm vi kết luận

- [ ] **Bổ sung bằng chứng live cho trường hợp thiếu thuộc tính.** Nếu cần quan sát `HOLD_UNVERIFIED` trong phiên JaCaMo, dùng ca `missing_property` của `use-plugin/tools/verify-state-checker.py`. Ca này bỏ khai báo observable property `best_bid` trên bản sao Auction. Đối chiếu chẩn đoán `ATTRIBUTE_VALUE_MISSING`, receipt và dấu mốc tiếp tục chạy. Nếu mở được cùng cấu hình qua USE, có thể chụp thanh trạng thái kèm chẩn đoán và dẫn sequence từ log. Ca này bổ sung cho TN04 vì dữ liệu ánh xạ thiếu một thuộc tính, còn TN04 đặt trực tiếp cờ `complete=false`.
- [ ] **TN05 — Vi phạm Goal iStar trong Auction.** Ưu tiên nếu muốn chứng minh marking cũng có thể làm checkpoint giữ dừng. Dùng ca `increasing_best_bid` của `use-plugin/tools/verify-state-checker.py` và ca đối chứng `valid_non_improving_bid`. Kiểm tra hai giá tại hai checkpoint kề nhau của cùng context, điều kiện `BidNeverIncreases` với `@pre`, trạng thái `VIOLATED` và quyết định. Kiểm tra cả danh sách invariant sai để xác định nguyên nhân giữ dừng. Một bid kém hơn có thể hợp lệ và giữ nguyên `best_bid`.
- [ ] **TN06 — Chẩn đoán với cùng vết.** Có thể dùng `classify-state-faults.py` trên vết đã ghi, đổi một điều kiện iStar, một invariant hoặc một ánh xạ mỗi lần. Ưu tiên đối chiếu `increasing_best_bid` khi bỏ riêng `BidNeverIncreases`, hoặc ca `wrong_winner` và `wrong_eligible_winner` khi thêm ràng buộc winner thuộc roster. Ca thứ hai cho biết ràng buộc về tư cách có đủ để phân biệt người thắng đúng theo giá hay không. Lưu biến thể, SHA-256 của vết, quyết định và điểm dừng. Phạm vi đối chiếu là phần vết đã thu.
- [ ] Khi dùng hai script, build kho USE để có `use-plugin/target/classes` và `use-plugin/target/runtime-classpath.txt`. Chiến dịch live dùng `verify-state-checker.py --output <thư_mục_mới> --cases <các_ca>`. Nếu chạy script phân loại theo cấu hình có sẵn, chuẩn bị đủ các ca mà script đó tham chiếu và chạy `classify-state-faults.py --campaign <thư_mục_chiến_dịch> --output <thư_mục_mới>`. Ghi các thay đổi mà script áp dụng cho bản sao chương trình nguồn. Diễn giải kết quả theo ca đã có bằng chứng từ source và trace.

## Danh sách screenshot cần chuẩn bị

Dùng ảnh chụp USE thật ở kích thước có thể đọc trong Word. Khi cần đối chiếu nhiều tab của cùng một hình, tắt **Follow live** hoặc chọn hàng checkpoint trong **Checkpoints**, rồi kiểm tra tiêu đề còn chỉ đúng checkpoint khi chuyển tab. Lưu PNG gốc, ghi mã ca, phiên, sequence và artefact log đi kèm. Các mã S01–S07 dùng khi thu ảnh. Đánh lại số Hình 3.x theo thứ tự chèn và cập nhật Danh mục hình sau khi đưa vào Word.

| Ảnh | Vị trí | Cần chụp và thông tin phải nhìn được |
| --- | --- | --- |
| **S01 — Lối vào plugin** | 3.2.2 | USE với menu **Plugins → JaCaMo → Run experiment...**. Có thể bổ sung một ảnh thư mục bản đóng gói ở phụ lục nếu cần chỉ vị trí JAR. |
| **S02 — Cấu hình Auction** | 3.2.2 hoặc 3.3.1 | Hộp thoại Run experiment với tên bốn tệp từ cấu hình TN01. Hiện thư mục Java Artifact nếu dùng vị trí tùy chọn. |
| **S03 — Cửa sổ thực nghiệm** | 3.3.1 | Cửa sổ Auction với vùng **JaCaMo** bên trái, **USE Evaluation** bên phải. Chọn **Project** và **Checkpoints** để thấy liên hệ giữa project, agent/plan, ranh giới và quyết định. Ghi số checkpoint được chọn. |
| **S04 — Trạng thái nguồn và CSL** | 3.5 | **Artifacts** và **OAL State** tại cùng checkpoint. Ưu tiên mốc thấy được cả `a1`, `a2`, giá quan sát và hai đối tượng CSL tương ứng. Dùng hai ảnh cắt nếu cần để đọc rõ. Ghép thêm bảng identity từ log nếu giao diện chỉ hiện tên. |
| **S05 — Kết quả Goal/Task** | 3.5 | Tab **iStarSCN** ở mốc hai context đạt `AuctionCompleted`. Nếu giao diện chỉ cho xem một context mỗi lần, dùng hai ảnh con có cùng checkpoint. Có thể thêm ảnh mốc sớm có `PENDING` nếu giúp giải thích sự khác nhau giữa tiến độ mục tiêu và quyết định `APPROVE`. |
| **S06 — Vi phạm Counter** | 3.5 | Tab **OCL** hiển thị dòng `Nonnegative` có `FAIL`, thanh trạng thái `HOLD_FAILURE`, số checkpoint và giá trị nguồn `-1` nếu bố cục cho phép. Nếu cần thể hiện ranh giới plan cha, lấy thêm ảnh **Checkpoints** ở cùng sequence hoặc dẫn dòng tương ứng trong bảng. |
| **S07 — Replay, tùy chọn** | 3.5 hoặc phụ lục | Terminal với lệnh hoặc tóm tắt số checkpoint và kết quả. Bảng đối chiếu và JSON là bằng chứng chính cho hai context. TN04 ưu tiên báo cáo kiểm thử và bảng dữ liệu. |

Mỗi chú thích ảnh nên nói rõ ca nào, checkpoint nào, đối tượng/ràng buộc nào và ảnh chứng minh điều gì. Giữ nguyên nội dung bằng chứng khi cắt ảnh và lược địa chỉ máy, đường dẫn cá nhân hoặc dữ liệu xác thực trước khi đưa vào bản nộp.

## 3.4. Tiêu chí đánh giá

- [ ] **Bảo toàn định danh và kiểu.** `a1` và `a2` đi đến hai đối tượng CSL và hai context iStar có lịch sử riêng. Đối chiếu định danh và giá trị theo một hoặc vài checkpoint. Hai tên xuất hiện trong ảnh là bước đầu, chuỗi identity trong log là căn cứ kiểm tra.
- [ ] **Quyết định phù hợp với bằng chứng.** TN01 kiểm tra các checkpoint đủ dữ liệu và quyết định cho phép tiếp tục. TN03 kiểm tra OCL `FAIL` cùng `HOLD_FAILURE`. TN04 kiểm tra thiếu dữ liệu, giữ đối tượng và `HOLD_UNVERIFIED`. Nếu thực hiện TN05, xem riêng trường hợp Goal `VIOLATED`. Trong các ca live, ghép bản ghi USE và receipt phía nguồn bằng run, token/sequence, quyết định và định danh checkpoint có trong dữ liệu.
- [ ] **Khả năng đối chiếu khi replay.** Trên phần vết được đánh giá ở cả hai phía, báo số cặp khớp trên tổng số cặp so sánh, số hàng thiếu, sai khác đầu tiên nếu có và tập context đạt mục tiêu ở mốc được chọn. Một quyết định giống nhau ở cuối phiên có thể đi kèm khác biệt ở checkpoint giữa.
- [ ] **Phạm vi quan sát.** Chỉ rõ kết quả nào được xác nhận bằng GUI/live, kiểm thử trực tiếp hoặc replay. Liệt kê dữ liệu đã được chiếu, dữ liệu còn thiếu và ranh giới plan dùng để giải thích điểm phát hiện. Nếu đo thời gian, mô tả tải, số lần lặp, điểm đo và cách tổng hợp riêng trước khi đưa ra nhận xét hiệu năng.

## 3.5. Kết quả và phân tích sơ bộ

- [ ] Lập bảng tóm tắt theo mã ca với các cột **Cấu hình hoặc mã phiên | Kỳ vọng | Quan sát | Checkpoint liên quan | Bằng chứng | Đạt / không đạt / chưa đủ bằng chứng**. Điền từ kết quả đã thu. Nếu chỉ sử dụng báo cáo cũ cho một ca, ghi rõ ngày, nguồn và loại bằng chứng.
- [ ] Dùng bảng vết rút gọn: **Mã phiên, sequence | Ranh giới/plan | Artifact hoặc context | Trạng thái nguồn/CSL | Kết quả OCL/marking | Quyết định USE | Receipt phía nguồn**. Chọn vài mốc tiêu biểu ở Auction và Counter, có thể trình bày thành hai bảng để vừa chiều rộng trang. Kèm bảng live/replay nếu bảng vết rút gọn chưa thể hiện được độ khớp.
- [ ] Sau mỗi bảng hoặc hình, giải thích một điểm cụ thể: dữ liệu nguồn nào tạo ra trạng thái đang thấy, điều kiện nào tạo ra kết quả và ranh giới nào quyết định thời điểm phát hiện. Đối với TN04, dùng các assertion và báo cáo để giải thích trường hợp không đủ căn cứ kiểm tra. Nếu có sai khác, ghi snapshot đầu tiên khác, đầu vào và chẩn đoán khả dĩ. Dùng trường hợp lệch để làm rõ giới hạn.
- [ ] Giữ các mốc cũ dưới dạng số liệu tham chiếu. Mục 7.3 của tài liệu dự án ghi ngày **22/11/2026**: Auction qua CLI có 58 checkpoint `APPROVE` kèm receipt, hai context đạt `AuctionCompleted` và replay đánh giá lại 58 checkpoint. `doc/TESTING.md` ghi Counter giữ dừng ở checkpoint 3, Auction có 59 checkpoint trong test và 58 khi chạy form. Ghi riêng kết quả của từng nguồn/lần chạy, kể cả khi số đếm trùng nhau.

## 3.6. Giới hạn và hướng mở rộng

- [ ] **Độ hạt checkpoint.** Suy ra từ Counter và mã gom plan đồng bộ. Các biến đổi trung gian có thể biến mất trước checkpoint ở cuối nhóm. Hướng mở rộng là thêm điểm quan sát có chủ đích, rồi đo chi phí và kiểm tra tác động tới hành vi điều phối.
- [ ] **Dữ liệu để kiểm tra đúng người thắng hoặc đúng dịch vụ.** Tách điều kiện đo được như giá đã cải thiện hoặc tư cách participant với điều kiện cần thêm quan hệ giữa người trả giá và giá được giữ, hoặc giữa yêu cầu dịch vụ và dịch vụ thực hiện. Hướng mở rộng là bổ sung bid-owner/best-bidder và Request/Scheme hoặc mốc thích hợp, sau đó xác định ràng buộc và ca đối chứng.
- [ ] **Phạm vi mô hình và kết luận.** Kết quả gắn với workspace cục bộ, nguồn và kiểu dữ liệu có ánh xạ, các ràng buộc đã khai báo, cũng như Goal/Task và kiểu context mà luồng kiểm chứng hỗ trợ. Nêu các hành vi quan sát được cùng nguyên nhân giới hạn. Một tập ca nhỏ cung cấp bằng chứng theo từng kịch bản, replay chỉ bao phủ vết đã thu và không dự đoán hành vi sau một quyết định HOLD khác.

## 3.7. Tổng kết chương

- [ ] Trả lời ngắn các câu hỏi của 3.1 bằng kết quả đã ghi ở 3.5. Nêu công cụ đã được đánh giá ở luồng nào, ca nào xác nhận tách context, khi nào giữ dừng và phạm vi có thể tái hiện khi replay.
- [ ] Dẫn sang kết luận khóa luận bằng một giới hạn có bằng chứng và hướng cải tiến tương ứng.

## Trình tự bàn giao bằng chứng và chốt bản thảo

1. **Chốt môi trường và đầu vào.** Ghi Git SHA của USE/JaCaMo, phiên bản JAR thực tế, lệnh chạy và cấu hình của từng ca. Lưu bản sao .jcm, XML, CSL, iStar và các thay đổi ASL/Java nếu có.
2. **Thu bằng chứng gốc.** Mỗi lần chạy có thư mục riêng theo mã ca và mã phiên, lưu ảnh gốc, log, trace, receipt và tệp kiểm thử hoặc replay. Lập một danh mục nối từng ảnh/hàng kết quả với tệp nguồn và checkpoint. Giữ bản gốc cục bộ và chỉ đưa vào bản nộp phần trích đã kiểm tra.
3. **Chạy các ca cốt lõi và điền bảng.** Làm TN01 rồi TN02 trên đúng vết, tiếp theo TN03 và TN04. Làm TN05–TN06 nếu cần củng cố kết luận về vi phạm Goal hoặc giới hạn phát hiện. Ghi riêng kỳ vọng và quan sát. Giữ các kết quả sai khác hoặc chưa đủ bằng chứng để giải thích phạm vi.
4. **Viết và kiểm tra chương.** Dùng mục lục 3.1–3.7 hiện có. Mỗi kết luận liên kết được với một ca và bằng chứng. Đánh số hình/bảng, thêm dẫn chiếu trong văn bản, cập nhật mục lục và danh mục hình/bảng nếu có. Mở bản Word hoặc PDF xuất ra để kiểm tra chữ trong ảnh và ngắt trang.
5. **Kiểm tra nguồn.** Dùng [43] cho mã USE và bộ ví dụ, [44] cho nguồn JaCaMo, [45] cho tài liệu kỹ thuật và mốc cũ, theo danh mục hiện tại. Khi trích mã hoặc mô tả phiên bản khác, ghi đúng commit và đường dẫn tệp của bản đã dùng.

### Tài liệu đối chiếu

- [Chương 3 bản thảo hiện tại](<thesis - fixx.docx>) và [Tổng quan khóa luận, đặc biệt các mục 2.2, 2.3, 4–6, 7.3 và 7.4](TONG_QUAN_KHOA_LUAN_USE_PLUGIN.md).
- [Khóa luận của Nguyễn Đức Quyền, Chương 3, trang in 44–52](<1, Tham Khảo/CNTT20_21020388_NguyenDucQuyen.pdf>).
- [Kho USE ở commit c3f47cd](https://github.com/nguyentrungnghia1802/use/tree/c3f47cd38bb67d2de9581ab8fa221b547b326735) · [README](https://github.com/nguyentrungnghia1802/use/blob/c3f47cd38bb67d2de9581ab8fa221b547b326735/README.md) · [Báo cáo và cách chạy kiểm thử](https://github.com/nguyentrungnghia1802/use/blob/c3f47cd38bb67d2de9581ab8fa221b547b326735/doc/TESTING.md).
- [Kho JaCaMo ở commit 34f45bd](https://github.com/nguyentrungnghia1802/jacamo/tree/34f45bd70350135b11e75f289fe32273267e3eaa).
