
from copy import deepcopy
from pathlib import Path
import json
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph
from PIL import Image

root, source, target = map(Path, sys.argv[1:4])
f=json.loads((root/"facts.json").read_text(encoding="utf8"))
d=Document(source)
ps=d.paragraphs
assert ps[418].text.startswith("[Bổ sung ảnh từ hệ thống.")
assert ps[458].text=="CHƯƠNG 3. TRIỂN KHAI VÀ THỰC NGHIỆM" and ps[549].text=="KẾT LUẬN"
assert ps[151].text.startswith("Hình 2.7") and ps[454].text.startswith("Hình 2.7")

def styled(p,text,template=None):
    r=p.add_run(text)
    if template is not None and template._r.rPr is not None:
        r._r.insert(0,deepcopy(template._r.rPr))
    return r

def para(anchor,template,text="",run_template=None):
    node=OxmlElement("w:p")
    if template._p.pPr is not None:
        node.append(deepcopy(template._p.pPr))
    anchor._p.addprevious(node)
    p=Paragraph(node,anchor._parent)
    if text:
        styled(p,text,run_template)
    return p

def discard(p):
    p._p.getparent().remove(p._p)

def repl_one(p,old,new):
    present=False
    for r in p.runs:
        if old in r.text:
            r.text=r.text.replace(old,new)
            present=True
    assert present,(old,p.text)

function_data = {
    "TN01": ("auction", "end"), "TN03": ("counter","end"),
    "TN05": ("goal","end"), "TN06": ("missing","end"),
    "TN07-negative": ("negative","end"), "TN07-recovered": ("recovered","end")
}
variables={}
for k,(a,_) in function_data.items():
    variables[a+"_run"]=f[k]["short"]
    variables[a+"_end"]=f[k]["end"]
variables.update(
    auction_mid=f["TN01"]["mid"],
    auction_mid_price=f"{f['TN01']['mid_details']['a1']['price']:.2f}".replace(".",","),
    auction_mid_checks=len(f["TN01"]["mid_invariants"]),
    auction_acks=f["TN01"]["acks"],
    goal_before=f["TN05"]["before"],
    goal_context=f["TN05"]["case_context"],
    goal_invariants=f["TN05"]["invariants"],
    missing_name=" và ".join(f["TN06"]["artifacts"]),
    replay_run=f["TN02"]["run"][:8],
    replay_total=f["TN02"]["checkpoint_count"],
)
assert f["TN01"]["mid_details"]["a1"]["bid"]=="FULFILLED" and f["TN01"]["mid_details"]["a2"]["bid"]=="PENDING"

intro_org="Phép chiếu cũng giữ việc đảm nhiệm vai trò trong nhóm. Hai ảnh dưới đây lấy trong cùng phiên Auction {goal_run}, khi JaCaMo đang giữ dừng tại checkpoint {goal_end}.".format_map(variables)
text_org="Trong [[moise-org]], mục Players ghi bob (1) đảm nhiệm vai trò auctioneer (2) ở nhóm agrp (3). Trên sơ đồ [[oal-org]], tác tử bob được biểu diễn bằng đối tượng CSL kiểu auction_capabilities. Thể hiện vai trò auctioneer có khung bo tròn và hai đường nối tới đối tượng bob và ngữ cảnh agrp. Các ký hiệu (1), (2) và (3) nối cùng ba thành phần giữa ảnh nguồn và ảnh đích."

def evidence_note(case,checkpoint):
    return f"phiên {f[case]['short']}, checkpoint {checkpoint}"

fig_ch2=[
    ("moise-org","Vai trò trong nhóm agrp trên Moise",9.1,evidence_note("TN05",f["TN05"]["end"])),
    ("oal-org","Tác tử, vai trò và nhóm trong OAL State",9.0,evidence_note("TN05",f["TN05"]["end"])),
]
fig_ch3=[
    ("menu","Mở chức năng thực nghiệm JaCaMo",5.2,""),
    ("mrv","Hộp thoại chọn gói Auction",9.0,""),
    ("workbench","Cửa sổ thực nghiệm tại checkpoint được chọn",15.8,evidence_note("Workbench",f["Workbench"]["end"])),
    ("mid-a1","Tiến độ ObserveBid của a1",12.4,evidence_note("TN01",f["TN01"]["mid"])),
    ("mid-a2","Tiến độ ObserveBid của a2",12.4,evidence_note("TN01",f["TN01"]["mid"])),
    ("final-a1","Kết quả AuctionCompleted của a1",12.4,evidence_note("TN01",f["TN01"]["end"])),
    ("final-a2","Kết quả AuctionCompleted của a2",12.4,evidence_note("TN01",f["TN01"]["end"])),
    ("counter","Giá trị bộ đếm và kết quả TN03",15.8,evidence_note("TN03",f["TN03"]["end"])),
    ("bid-before","Giá tốt nhất trước lượt trả giá kém hơn",15.4,evidence_note("TN05",f["TN05"]["before"])),
    ("bid-after","Giá tốt nhất sau lượt trả giá kém hơn",15.4,evidence_note("TN05",f["TN05"]["end"])),
    ("bid-goal","Vi phạm mục tiêu giữ giá không tăng",12.4,evidence_note("TN05",f["TN05"]["end"])),
    ("bid-ocl","Kết quả bất biến CSL trong TN05",13.7,evidence_note("TN05",f["TN05"]["end"])),
    ("bid-hold","Quyết định tại mốc chuyển giao trong TN05",15.8,evidence_note("TN05",f["TN05"]["end"])),
    ("missing","Giữ dừng vì thiếu giá tốt nhất trong TN06",15.8,evidence_note("TN06",f["TN06"]["end"])),
    ("negative-console","Log giá trị của phiên Counter giữ âm",5.7,f"phiên {f['TN07-negative']['short']}, trước checkpoint {f['TN07-negative']['end']}"),
    ("negative-checkpoint","Giá trị âm tại checkpoint của TN07",15.8,evidence_note("TN07-negative",f["TN07-negative"]["end"])),
    ("recovered-console","Log giá trị của phiên Counter khôi phục",5.7,f"phiên {f['TN07-recovered']['short']}, trước checkpoint {f['TN07-recovered']['end']}"),
    ("recovered-checkpoint","Giá trị đã khôi phục tại checkpoint",15.8,evidence_note("TN07-recovered",f["TN07-recovered"]["end"])),
]
table_defs=[
    ("tn04","Phản hồi với ảnh trạng thái thiếu trong TN04",
     [2.2,2.7,2.4,3.6,4.9],
     [
       ["Lần gửi","Ảnh đầy đủ","Giá trị nguồn","Gauge trong USE","Quyết định"],
       ["Mốc 1","Có","1","1","APPROVE"],
       ["Mốc 2","Không","Danh sách rỗng","1 (giữ nguyên)","HOLD_UNVERIFIED"],
       ["Mốc 2 gửi lại","Có","2","2 (cùng đối tượng)","APPROVE"],
     ]),
    ("tn05-control","Đối chứng theo cách cập nhật giá và ranh giới TN05",
     [3.7,3.5,3.4,5.2],
     [
       ["Cập nhật giá","Ranh giới","Giá trong ảnh","Quyết định"],
       ["Giữ giá 10","Cuối nhóm","10","28 mốc cho tiếp tục"],
       ["Thay bằng 20","Cuối nhóm","Chỉ thấy 20 sau hai lượt","27 mốc cho tiếp tục"],
       ["Giữ giá 10","Tách chuyển giao","10 ở cả hai mốc","31 mốc cho tiếp tục"],
       ["Thay bằng 20","Tách chuyển giao","10 lên 20 ở hai mốc","Giữ dừng ở mốc 22"],
     ]),
    ("replay","Đối chiếu vết gốc và kết quả đánh giá lại trong TN02",
     [7.8,8.0],
     [
       ["Nội dung đối chiếu","Kết quả"],
       ["Số checkpoint được lệnh đọc và đánh giá",str(f["TN02"]["checkpoint_count"])],
       ["Quyết định khớp vết gốc",f"{f['TN02']['decision_matches']}/{f['TN02']['checkpoint_count']}"],
       ["Tập Goal, Task đã đạt khớp theo ngữ cảnh",f"{f['TN02']['fulfilled_matches']}/{f['TN02']['checkpoint_count']}"],
       ["Bản xác nhận JaCaMo khớp vết gốc",f"{f['TN02']['acks']}/{f['TN02']['checkpoint_count']}"],
       ["Kết quả ở checkpoint cuối","APPROVE, a1 và a2 đều đạt AuctionCompleted"],
     ])
]
assert [r["count"] for r in f["reference_TN05"]]==[28,27,31,22]
figs, tables = {}, {}
for chapter, first, definitions in ((2,7,fig_ch2),(3,1,fig_ch3)):
    for number,(k,title,width,note) in enumerate(definitions,start=first):
        asset_name={"mid-a1":"auction-mid-a1","mid-a2":"auction-mid-a2","final-a1":"auction-final-a1","final-a2":"auction-final-a2"}.get(k,k)
        figs[k]={"number":f"{chapter}.{number}","title":title,"width":width,"note":note,"path":f"hinh-chen/{asset_name}.png"}
for number,(k,title,widths,rows) in enumerate(table_defs,start=1):
    tables[k]={"number":f"3.{number}","title":title,"widths":widths,"rows":rows}

def reference(key):
    if key in figs:
        return "Hình "+figs[key]["number"]
    if key in tables:
        return "Bảng "+tables[key]["number"]
    raise KeyError(key)

def text(p):
    return re.sub(r"\[\[([a-z0-9-]+)\]\]",lambda x:reference(x.group(1)).replace(" ",chr(160)),p.format_map(variables))

def fig(anchor,key):
    meta=figs[key]
    path=root/meta["path"]
    assert path.is_file()
    p=para(anchor,ps[472])
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next=True
    p.paragraph_format.keep_together=True
    p.paragraph_format.space_before=Pt(5)
    p.paragraph_format.space_after=Pt(0)
    with Image.open(path) as image:
        w,h=image.size
        assert w>=200
        width=min(meta["width"],15.6*w/h)
    inline=p.add_run().add_picture(str(path),width=Cm(width))
    inline._inline.docPr.set("descr",meta["title"])
    caption=para(anchor,ps[473])
    caption.alignment=WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.keep_with_next=key in {"moise-org","mid-a1","final-a1","bid-before","negative-console","recovered-console"}
    caption.paragraph_format.keep_together=True
    caption.paragraph_format.space_after=Pt(5)
    styled(caption,reference(key),ps[473].runs[0])
    desc=meta["title"]+(" ("+meta["note"]+")" if meta["note"] else "")
    styled(caption," "+desc+".",ps[473].runs[1])

def table(anchor,key):
    meta=tables[key]
    caption=para(anchor,ps[473])
    caption.paragraph_format.keep_with_next=True
    styled(caption,reference(key),ps[473].runs[0])
    styled(caption," "+meta["title"]+".",ps[473].runs[1])
    grid=d.add_table(rows=len(meta["rows"]),cols=len(meta["widths"]))
    grid.style="Table Grid"
    grid.alignment=WD_TABLE_ALIGNMENT.CENTER
    grid.autofit=False
    for column,w in zip(grid.columns,meta["widths"]):
        column.width=Cm(w)
    for rid,(row,values) in enumerate(zip(grid.rows,meta["rows"])):
        tr_pr=row._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement("w:cantSplit"))
        if rid==0:
            tr_pr.append(OxmlElement("w:tblHeader"))
        for cid,(cell,value,w) in enumerate(zip(row.cells,values,meta["widths"])):
            cell.width=Cm(w)
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tc_pr=cell._tc.get_or_add_tcPr()
            if rid==0:
                shade=OxmlElement("w:shd")
                shade.set(qn("w:fill"),"F1F1F1")
                tc_pr.append(shade)
            p=cell.paragraphs[0]
            p.alignment=WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent=Cm(0)
            p.paragraph_format.space_before=Pt(3)
            p.paragraph_format.space_after=Pt(3)
            p.paragraph_format.line_spacing=1.08
            p.paragraph_format.keep_with_next=rid<len(meta["rows"])-1
            r=styled(p,value)
            r.font.name="Times New Roman"
            r.font.size=Pt(11)
            r.font.color.rgb=RGBColor(0,0,0)
            r.bold=rid==0
    anchor._p.addprevious(grid._tbl)

def list_entry(anchor,key,sample):
    meta=figs[key] if key in figs else tables[key]
    p=para(anchor,sample)
    styled(p,reference(key)+" "+meta["title"],sample.runs[0])
    styled(p,"\t000",sample.runs[-1])

# Chapter 2, replace the single red instruction and renumber the following figure.
anchor=ps[418]
lead=para(anchor,ps[417],intro_org,ps[417].runs[0])
lead.paragraph_format.keep_with_next=True
fig(anchor,"moise-org")
fig(anchor,"oal-org")
para(anchor,ps[417],text(text_org),ps[417].runs[0])
discard(anchor)
for p in (ps[151],ps[452],ps[454]):
    repl_one(p,"Hình 2.7","Hình 2.9")
for k,*_ in fig_ch2:
    list_entry(ps[151],k,ps[150])

# Chapter 3. Restore each existing heading with its paragraph and run formatting.
templates={p.text:p for p in ps[458:549] if p.style.name.startswith("Heading")}
seen=set()
anchor=ps[549]
p_body=ps[467]
blocks="\n\n".join((root/"tooling"/name).read_text(encoding="utf8") for name in ("chapter3-a.txt","chapter3-b.txt"))
previous=""
for block in re.split(r"\n\s*\n",blocks):
    block=block.strip()
    if not block: continue
    if block.startswith("##"):
        heading=block.lstrip("#").strip()
        original=templates[heading]
        para(anchor,original,heading,original.runs[0])
        seen.add(heading)
    elif block.startswith("@fig "):
        fig(anchor,block.split()[-1])
    elif block.startswith("@table "):
        table(anchor,block.split()[-1])
    else:
        paragraph=para(anchor,p_body,text(block),p_body.runs[0])
        paragraph.paragraph_format.widow_control=True
        if previous.startswith("@table "):
            paragraph.paragraph_format.space_before=Pt(5)
        if previous in {"@fig mid-a1","@fig final-a1","@fig bid-before","@fig negative-console","@fig recovered-console"} or block.startswith((
            "Ở phiên chụp {auction_run},","Hai đối tượng giữ định danh","Trong TN03, Counter kết thúc","TN05 kiểm tra trường hợp","Phiên khôi phục",
            "Khi cửa sổ thực nghiệm xuất hiện","Trong TN06, biến thể",
        )):
            paragraph.paragraph_format.keep_with_next=True
    previous=block
assert seen==set(templates)-{ps[458].text}
for p in ps[459:549]:
    discard(p)
for k,*_ in fig_ch3:
    list_entry(ps[171],k,ps[152])
for p in ps[152:171]:
    discard(p)
for k,*_ in table_defs:
    list_entry(ps[174],k,ps[173])

target.parent.mkdir(parents=True,exist_ok=True)
d.save(target)
report={
    "figures":figs,
    "tables":{k:{x:y for x,y in v.items() if x in ["number","title"]} for k,v in tables.items()}
}
(root/"figure-index.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(f"Built draft with {len(figs)} new screenshots and {len(tables)} evidence tables.")

