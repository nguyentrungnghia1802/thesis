
from pathlib import Path
import json
import sys
root=Path(sys.argv[1])
facts=json.loads((root/"facts.json").read_text(encoding="utf8"))
index=json.loads((root/"page-index.json").read_text(encoding="utf8"))
doc=json.loads((root/"figure-index.json").read_text(encoding="utf8"))
labels=[
 ("Workbench","Mở gói và chọn một checkpoint","3.1–3.3"),
 ("TN01","Auction tại mốc lệch tiến độ và mốc cuối","3.4–3.7"),
 ("TN03","Counter cơ bản","3.8"),
 ("TN05","Auction lỗi ở mốc chuyển giao, kèm đối chiếu Moise–OAL","2.7–2.8 và 3.9–3.13"),
 ("TN06","Auction thiếu giá tốt nhất","3.14"),
 ("TN07-negative","Counter giữ giá trị âm","3.15–3.16"),
 ("TN07-recovered","Counter khôi phục giá trị","3.17–3.18"),
]
def code(value): return chr(96)+str(value)+chr(96)
lines=[
 "# Bằng chứng cho Chương 3 và Mục 2.6.3",
 "",
 "Ảnh thu từ USE 7.5.0, plugin JaCaMo 1.0.1 và JDK 21.0.5 trên Windows 11. Checkout USE tại "
 +code("6d6a9ee6d075d234bd3c4764e34651bcb5ac0682")+".",
 "",
 "- SHA-256 của JAR plugin "+code("46569e4095b9f5ccb1f7d7b7b1643611aca11f3ada462343503727de2dde3ef3")+".",
 "- SHA-256 của JAR JaCaMo "+code("dede2e2cde568c747a774e33f821cdcee6501515997a710816aa9c02c7c901f5")+".",
 "",
 "## Phiên chụp và bằng chứng đầu vào",
 "",
 "| Ca chụp | Mã lần chạy | Checkpoint trong hình | Hình |",
 "| --- | --- | --- | --- |",
]
for key,label,nos in labels:
    v=facts[key]
    checkpoints=f"{v['mid']} và {v['end']}" if key=="TN01" else f"{v['before']} và {v['end']}" if key=="TN05" else str(v['end'])
    if key=="Workbench": checkpoints+= " sau khi mở gói"
    lines.append(f"| [{label}]({v['folder']}/) | {code(v['run'])} | {checkpoints} | {nos} |")
lines += [
 "",
 "Mỗi thư mục ca chụp chứa PNG gốc, lệnh chạy, mã băm của gói MRV, log nguồn, vết USE và xác nhận checkpoint phía JaCaMo. "
 "Ảnh các thẻ USE được kết xuất từ giao diện Swing đang chạy. Những phần cắt giữ nguyên các dòng, nhãn và giá trị hiển thị.",
 "",
 "Hai ảnh tổ chức thuộc lần chạy TN05 ở checkpoint 22. Trình quan sát Moise đọc nhóm agrp trong lúc JaCaMo đang giữ dừng. "
 "Ảnh OAL lấy từ dữ liệu USE ở cùng checkpoint. Vết xác nhận bob đảm nhiệm auctioneer trong agrp và trạng thái đích có hai liên kết tương ứng. "
 "Ảnh chèn đánh dấu ba thành phần, còn ảnh và HTML thô nằm trong thư mục ca chụp.",
 "",
 "## Kiểm thử và đối chiếu vết",
 "",
 "- [TN02](TN02/) lưu lệnh đánh giá lại, kết quả và so sánh từng checkpoint. "
 "Ca này dùng cùng vết gốc 3868eb28 và đặc tả đã lưu. Có 58/58 quyết định và 58/58 tập Goal, Task đã đạt theo ngữ cảnh khớp. "
 "Bản xác nhận phía nguồn cũng trùng vết gốc ở 58/58 mốc.",
 "- [TN04](TN04/) lưu báo cáo JUnit và vết của ba lần gửi ảnh vào bộ kiểm chứng. "
 "Vết bổ sung ghi cùng đối tượng Gauge giữ nguyên giá trị 1 khi ảnh thiếu, rồi nhận giá trị 2 ở lần đánh giá ảnh đầy đủ.",
 "- [TN05 đối chứng](TN05-doi-chung.json) đối chiếu bốn vết nguồn đã lưu trong Du-lieu-thuc-nghiem-bo-sung-20261124.",
 "",
 "## Ảnh đưa vào Word",
 "",
 "| Hình | Ảnh PNG chèn | Trang in |",
 "| --- | --- | --- |",
]
for v in doc["figures"].values():
    title=f"Hình {v['number']} {v['title']}"
    lines.append(f"| {title} | [PNG]({v['path']}) | {index[title]['label']} |")
(root/"README.md").write_text("\n".join(lines)+"\n",encoding="utf8")

