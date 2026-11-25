from copy import deepcopy
import json
from pathlib import Path
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph
from PIL import Image

e = Path(__file__).parent
source = Path(sys.argv[1])
d = Document(source)
ps = d.paragraphs

def selection(case):
    data = dict(line.split("=", 1) for line in (e / case / "selection.txt").read_text().splitlines())
    data["short"] = data["run"].split("-")[0]
    return data

def records(case):
    return [json.loads(l) for l in (e / case / "consumer-history.jsonl").read_text().splitlines() if l]

auction = selection("auction-layout")
goal = selection("goal")
missing = selection("missing-final")
base = selection("counterbase")
negative = selection("counter")
restored = selection("restored-final")
run, sel, mark = auction["short"], int(auction["selected"]), int(auction["latest"])
auction_case = "auction-layout"
goal_cp = int(goal["latest"])
missing_cp = int(missing["latest"])
goal_rows = records("goal")
goal_result = goal_rows[-1]["response"]["result"]
goal_id = next(row["id"].strip("'") for row in goal_result["state"] if row["object"] == goal["context"])
def focus_markings(case, original, focused):
    with Image.open(e / case / original) as img:
        # Header plus the seven AuctionGroup rows painted by the native table.
        assert img.height == 724
        header = img.height - 19 * 36
        img.crop((0, 0, img.width, header + 7 * 36)).save(e / case / focused)

for entity in ("a1", "a2"):
    focus_markings(auction_case, f"markings-{entity}.png", f"auctiongroup-{entity}.png")
focus_markings("goal", "markings.png", "auctiongroup.png")
goal_invariants = [row for row in goal_result["checks"] if row["kind"] == "CSL_INVARIANT"]
assert goal_invariants and all(row["verdict"] == "PASS" for row in goal_invariants)
assert "value=-1" in (e / "counter" / "producer.log").read_text()
assert re.search(r"COUNTER_WITNESS value=-1[^\n]*\n[^\n]*COUNTER_WITNESS value=2", (e / "restored-final" / "producer.log").read_text())
auction_rows = records(auction_case)
cut = next(r for r in auction_rows if r["request"]["snapshot"]["sequence"] == sel)
scope = {item["name"]: item["properties"]["best_bid"] for item in cut["request"]["snapshot"]["artifacts"] if item["name"] in {"a1", "a2"}}
def vn(v): return str(v).replace(".", ",")

figs = {}
def group(chapter, key, path, title, note="", width=15.7):
    n = sum(f["chapter"] == chapter for f in figs.values()) + (5 if chapter == 2 else 1)
    figs[key] = dict(chapter=chapter, number=f"{chapter}.{n}", path=path, title=title, note=note, width=width)

group(2, "source", f"{auction_case}/artifacts.png", "Giá tốt nhất của hai artifact Auction", f"phiên {run}, checkpoint {sel}")
group(2, "oal", f"{auction_case}/oal-compact.png", "Sơ đồ đầy đủ của trạng thái Auction trong OAL State", f"phiên {run}, checkpoint {sel}")
group(2, "cuts", f"{auction_case}/timeline.png", "Các checkpoint đầu của Auction", f"phiên {run}, checkpoint 1–8")
group(3, "menu", f"{auction_case}/menu.png", "Lệnh Run experiment trong trình đơn JaCaMo", width=5.2)
group(3, "mrv", f"{auction_case}/mrv.png", "Hộp thoại chọn gói auction.mrv", width=10)
group(3, "history", f"{auction_case}/terminal-timeline.png", "Theo dõi Auction trong thẻ Checkpoints", f"phiên {run}, đến checkpoint {mark}")
group(3, "prices", f"{auction_case}/terminal-artifacts.png", "Giá công bố khi hai cuộc đấu giá đã đạt mục tiêu", f"phiên {run}, checkpoint {mark}")
group(3, "scn", f"{auction_case}/istar-a1-compact.png", "Sơ đồ iStarSCN đầy đủ của ngữ cảnh a1", f"phiên {run}, checkpoint {mark}")
group(3, "a1", f"{auction_case}/auctiongroup-a1.png", "Các Goal của AuctionGroup trong ngữ cảnh a1", f"phiên {run}, checkpoint {mark}", 9.2)
group(3, "a2", f"{auction_case}/auctiongroup-a2.png", "Các Goal của AuctionGroup trong ngữ cảnh a2", f"phiên {run}, checkpoint {mark}", 9.2)
group(3, "base", "counterbase/ocl.png", "Vi phạm bất biến Nonnegative trong TN03", f"phiên {base['short']}, checkpoint {base['latest']}", 10.4)
group(3, "before", "goal/before.png", "Giá tốt nhất trước lượt trả giá kém hơn trong TN05", f"phiên {goal['short']}, checkpoint {goal_cp-1}")
group(3, "after", "goal/after.png", "Giá tốt nhất sau lượt trả giá kém hơn trong TN05", f"phiên {goal['short']}, checkpoint {goal_cp}")
group(3, "hold", "goal/hold.png", "Quyết định HOLD_FAILURE trong TN05", f"phiên {goal['short']}, checkpoint {goal_cp}")
group(3, "violated", "goal/auctiongroup.png", "Vi phạm Goal BidNeverIncreases trong ngữ cảnh " + goal_id, f"phiên {goal['short']}, checkpoint {goal_cp}", 9.2)
group(3, "invariants", "goal/invariants.png", "Kết quả các bất biến CSL trong TN05", f"phiên {goal['short']}, checkpoint {goal_cp}", 13.6)
group(3, "unverified", "missing-final/hold.png", "Quyết định HOLD_UNVERIFIED trong TN06", f"phiên {missing['short']}, checkpoint {missing_cp}")
group(3, "diagnostic", "missing-final/diagnostic.png", "Chẩn đoán thiếu thuộc tính Auction.best_bid", f"phiên {missing['short']}, checkpoint {missing_cp}")
group(3, "negative-log", "counter/console.png", "Giá trị quan sát trong Console của phiên Counter giữ âm", f"phiên {negative['short']}, trước checkpoint {negative['latest']}", 5.6)
group(3, "negative-ocl", "counter/ocl.png", "Bất biến Nonnegative khi Counter giữ giá trị âm", f"phiên {negative['short']}, checkpoint {negative['latest']}", 10.4)
group(3, "restored-log", "restored-final/console.png", "Giá trị quan sát trong Console của phiên Counter khôi phục", f"phiên {restored['short']}, trước checkpoint {restored['latest']}", 5.6)
group(3, "restored-ocl", "restored-final/ocl.png", "Bất biến Nonnegative sau khi Counter khôi phục giá trị", f"phiên {restored['short']}, checkpoint {restored['latest']}", 10.4)

def ref(key):
    return "Hình " + figs[key]["number"]

def remove(p):
    p._p.getparent().remove(p._p)

def replace(p, text):
    p.clear()
    p.add_run(text)

def styled_run(paragraph, value, sample):
    run = paragraph.add_run(value)
    if sample._r.rPr is not None:
        run._r.insert(0, deepcopy(sample._r.rPr))
    return run

def before(anchor, example):
    xml = OxmlElement("w:p")
    if example._p.pPr is not None:
        xml.append(deepcopy(example._p.pPr))
    anchor._p.addprevious(xml)
    return Paragraph(xml, anchor._parent)

def figure(anchor, key):
    info = figs[key]
    picture = before(anchor, ps[390])
    picture.paragraph_format.keep_with_next = True
    picture.paragraph_format.keep_together = True
    picture.alignment = WD_ALIGN_PARAGRAPH.CENTER
    path = e / info["path"]
    with Image.open(path) as png:
        assert png.format == "PNG" and png.width >= 200, path
        width = min(info["width"], 16.1 * png.width / png.height)
        pic = picture.add_run().add_picture(str(path), width=Cm(width))
    pic._inline.docPr.set("descr", info["title"])
    caption = before(anchor, ps[391])
    caption.paragraph_format.keep_with_next = key in {"negative-log", "restored-log"}
    caption.paragraph_format.keep_together = True
    styled_run(caption, ref(key), ps[391].runs[0])
    extra = f" ({info['note']})" if info["note"] else ""
    styled_run(caption, f" {info['title']}{extra}.", ps[391].runs[1])

def figures(anchor, *keys):
    for key in keys:
        figure(ps[anchor], key)

assert ps[148].text.startswith("Hình 2.5") and ps[160].text.startswith("Hình 3.11")
assert ps[391].text.startswith("Hình 2.5") and ps[496].text.startswith("Hình 3.11")
replace(ps[328], ps[328].text.replace("Hình 3.8", ref("violated")))
replace(ps[379], ps[379].text.replace("Hình 2.6", ref("cuts")))
replace(ps[392], f"{ref('source')} ghi giá tốt nhất do JaCaMo công bố tại checkpoint {sel} của phiên chụp {run}. Giá của a1 là {vn(scope['a1'])} và của a2 là {vn(scope['a2'])}. {ref('oal')} cho thấy hai giá trị được gán vào thuộc tính best_bid của đúng đối tượng Auction trong USE. Sơ đồ OAL giữ cả các đối tượng tổ chức, vai trò và quan hệ trong cùng trạng thái.")
figures(393, "source", "oal")
replace(ps[428], ps[428].text.replace("Hình 2.6 cho thấy checkpoint khởi tạo và các mốc kết thúc nhóm plan trong một lần chạy Auction.", f"{ref('cuts')} cho thấy checkpoint khởi tạo và các mốc kết thúc nhóm plan ở đầu phiên chụp Auction {run}."))
figures(429, "cuts")
replace(ps[447], f"Người dùng mở Plugins → JaCaMo → Run experiment... như trong {ref('menu')}.")
figures(448, "menu")
replace(ps[450], f"Trong {ref('mrv')}, người dùng chỉ chọn gói auction.mrv rồi bấm Run. Gói này chứa manifest mrv.json trỏ đến dự án JaCaMo (.jcm), đặc tả CSL, mô hình iStar và luật ánh xạ XML, cùng mã nguồn cần cho thực nghiệm. Khi chạy, khung bên trái hiển thị dữ liệu thực thi JaCaMo và khung bên phải hiển thị kết quả của USE. Chọn một hàng ở thẻ Checkpoints để xem dữ liệu nguồn, trạng thái đối tượng CSL và kết quả Goal/Task tại cùng mốc.")
figures(451, "mrv")
replace(ps[457], f"TN01 chạy Auction với hai phiên a1 và a2 dùng chung cấu trúc, điều kiện mục tiêu và luật ánh xạ. Ca thử kiểm tra liệu từng phiên có giữ được giá và tiến độ riêng qua các checkpoint hay không. {ref('history')} minh họa thẻ theo dõi của phiên chụp mới {run}. TN02 dùng chuỗi snapshot và các tệp đặc tả của lần chạy TN01 đã lưu để so sánh quyết định và các phần tử đạt tại từng checkpoint.")
figures(458, "history")
replace(ps[472], f"Vết gốc của TN01 ghi giá của hai artifact và hai đối tượng tương ứng tại checkpoint 58. {ref('prices')} minh họa dữ liệu nguồn ở checkpoint {mark} của phiên chụp mới {run}. Cách đối chiếu cùng checkpoint với trạng thái OAL được trình bày ở {ref('source')} và {ref('oal')}.")
figures(473, "prices")
replace(ps[475], f"Ở phiên chụp {run}, {ref('scn')} trình bày toàn bộ sơ đồ iStarSCN của ngữ cảnh a1 tại checkpoint {mark}. Bảng Markings ở {ref('a1')} ghi AuctionCompleted = FULFILLED của a1 tại mốc đó.")
figures(476, "scn", "a1")
replace(ps[478], f"{ref('a2')} cho thấy AuctionCompleted cũng đạt trên ngữ cảnh a2 tại cùng checkpoint {mark} của phiên chụp. Trong vết gốc TN01, JaCaMo xác nhận đủ cả 58 quyết định APPROVE.")
figures(479, "a2")
replace(ps[483], ps[483].text.replace("Trong TN03 ở Hình 3.7", "Trong TN03").replace("USE phát hiện vi phạm Nonnegative và trả HOLD_FAILURE.", f"USE phát hiện vi phạm Nonnegative và trả HOLD_FAILURE. {ref('base')} minh họa kết quả OCL trong lần chụp lại."))
figures(484, "base")
replace(ps[488], f"Khi có thêm mốc chuyển giao, USE quan sát được giá 10 ở checkpoint 21 và 20 ở checkpoint 22. Mục tiêu BidNeverIncreases bị vi phạm, JaCaMo nhận HOLD_FAILURE và log không ghi hoạt động sau điểm dừng. Phiên đối chứng dùng cùng ranh giới và tiếp tục ở cả 31 checkpoint. Trong phiên chụp {goal['short']}, thẻ Artifacts cho thấy bước tăng từ 10 lên 20 ({ref('before')} và {ref('after')}). Thẻ Checkpoints ghi HOLD_FAILURE ({ref('hold')}), thẻ iStarSCN ghi BidNeverIncreases = VIOLATED ({ref('violated')}) và cả {len(goal_invariants)} lượt đánh giá bất biến đều PASS ({ref('invariants')}).")
figures(489, "before", "after", "hold", "violated", "invariants")
replace(ps[491], f"Trong TN06, cả hai phiên đều thu được đối tượng Auction nhưng thiếu giá tốt nhất để ánh xạ vào Auction.best_bid. USE trả HOLD_UNVERIFIED tại checkpoint 18 và JaCaMo xác nhận phản hồi. Ở phiên gom plan, thao tác đánh dấu đã diễn ra trước khi chụp. Khi đưa checkpoint chuyển giao lên trước thao tác đó, log không còn ghi thao tác. Trong phiên chụp {missing['short']}, hàng có dấu hỏi ở {ref('unverified')} ứng với checkpoint {missing_cp} trong vết chạy. Thanh trạng thái USE ở {ref('diagnostic')} ghi thuộc tính còn thiếu.")
figures(492, "unverified", "diagnostic")
replace(ps[494], f"Ở phiên Counter giữ âm {negative['short']} của TN07, Console ghi bộ đếm nhận giá trị −1 ({ref('negative-log')}). Tại checkpoint {negative['latest']}, Counter vẫn có giá trị −1, bất biến Nonnegative cho kết quả FAIL ({ref('negative-ocl')}) và USE trả HOLD_FAILURE. Đối chứng dùng một phiên riêng để kiểm tra điều gì xảy ra khi giá trị được sửa trong cùng nhóm plan.")
figures(495, "negative-log", "negative-ocl")
replace(ps[497], f"Trong phiên Counter khôi phục {restored['short']}, Console ghi bộ đếm nhận −1 rồi trở về 2 trong cùng nhóm plan ({ref('restored-log')}). Tại checkpoint {restored['latest']}, Nonnegative cho kết quả PASS ({ref('restored-ocl')}) và USE trả APPROVE. Giá trị −1 chỉ xuất hiện trong log nguồn vì bộ đếm đã được khôi phục trước khi chụp ở cuối nhóm plan.")
figures(498, "restored-log", "restored-ocl")

for i in [390,391,426,427,445,446,448,449,455,456,469,470,471,473,474,476,477,481,482,486,487,489,490,492,493,495,496]:
    remove(ps[i])
for key, info in figs.items():
    p = before(ps[161], ps[148])
    styled_run(p, f"{ref(key)} {info['title']}", ps[148].runs[0])
    styled_run(p, "\t000", ps[148].runs[-1])
for i in range(148, 161):
    remove(ps[i])

(e / "figure-index.json").write_text(json.dumps(figs, ensure_ascii=False, indent=2), encoding="utf-8")
d.save(e / "staged.docx")
print(f"Updated {len(figs)} figures.")

