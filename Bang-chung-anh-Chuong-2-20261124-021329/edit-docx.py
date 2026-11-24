import os,pathlib,re,copy,json
from PIL import Image
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
e=pathlib.Path(os.environ["THESIS_EVIDENCE"])
folder=e/"phien-chinh-thuc"
d=Document(os.environ["THESIS_BACKUP"])
p=d.paragraphs
def replace(para,a,b):
    sources=[r for r in para.runs if a in r.text]
    assert len(sources)==1,(a,para.text)
    sources[0].text=sources[0].text.replace(a,b,1)
for index in [139,331,333]:
    replace(p[index],"Hình 2.2","Hình 2.3")
for index in [329,340,403]:
    assert p[index].text.startswith("[Ảnh chụp cần bổ sung]") and str(p[index].runs[0].font.color.rgb)=="C00000"
for index,source,tail in (
    (328,"auction.csl"," Hình 2.2 thể hiện cấu trúc này trong USE."),
    (339,"auction.istar"," Hình 2.4 minh họa ba nhánh AND trong mô hình đã mở."),
    (402,"vết TN01"," Hình 2.5 minh họa bảng checkpoint trong một phiên Auction chụp riêng."),
):
    assert source in p[index].text
    p[index].add_run(tail)
trace=[json.loads(line) for line in (folder/"consumer-history.jsonl").read_text(encoding="utf8").splitlines()]
run=trace[0]["request"]["run"]
assert all(q["request"]["run"]==run for q in trace)
assert trace[0]["request"]["checkpoint"]["boundary"]=="INITIAL"
assert [v["request"]["snapshot"]["sequence"] for v in trace[:8]]==list(range(1,9))
assert all(v["request"]["checkpoint"]["boundary"]=="PLAN_COMPLETED" for v in trace[1:8])
receipt=json.loads((folder/"checkpoint-1.json").read_text(encoding="utf8"))
assert receipt==trace[0]
for tab,bounds in (
    ("CSL-Model",(229,232,1295,650)),
    ("iStar-Model",(1077,333,1831,685)),
    ("Checkpoints",(230,232,1115,413)),
):
    with Image.open(folder/(tab+"-original.png")) as im:
        assert im.size==(1920,1080)
        im.crop(bounds).save(folder/(tab+"-word.png"))
def cap_after(paragraph,text):
    para=d.add_paragraph(text,"Caption")
    paragraph._p.addnext(para._p)
    fmt=para.paragraph_format
    fmt.alignment=WD_ALIGN_PARAGRAPH.CENTER
    fmt.first_line_indent=Inches(0)
    fmt.space_after=Pt(8); fmt.space_before=Pt(4)
    fmt.keep_with_next=False
    fmt.keep_together=True
    run=para.runs[0]
    run.font.name="Times New Roman"
    run.font.size=Pt(11)
    run.font.color.rgb=RGBColor.from_string("000000")
    run.italic=True
def image_at(index,tab,caption,desc):
    p[index].clear()
    item=p[index]
    fmt=item.paragraph_format
    fmt.alignment=WD_ALIGN_PARAGRAPH.CENTER
    fmt.first_line_indent=Inches(0)
    fmt.space_before=Pt(5); fmt.space_after=Pt(0)
    fmt.line_spacing=1
    fmt.keep_together=True; fmt.keep_with_next=True
    img=item.add_run().add_picture(str(folder/(tab+"-word.png")),width=Inches(6.09))
    img._inline.docPr.set("descr",desc)
    cap_after(item,caption)
image_at(329,"CSL-Model",
    "Hình 2.2. Mô hình AuctionState mở từ auction.csl trong tab CSL Model của USE [43].",
    "AuctionOrg, auctionGroup, vai trò auctioneer, participant và các thuộc tính của thực thể Auction")
image_at(340,"iStar-Model",
    "Hình 2.4. Nhóm AuctionGroup của mô hình AuctionStateGoals mở từ auction.istar trong tab iStar Model [43].",
    "AuctionCompleted và ba nhánh AND O_start, O_bid và O_decide")
image_at(403,"Checkpoints",
    f"Hình 2.5. Tab Checkpoints của phiên Auction ngày 24/11/2026, mã {run[:8]}. "
    "Ảnh hiển thị mốc INITIAL ở checkpoint 1 đang chọn và các mốc PLAN_COMPLETED ở checkpoint 2–8.",
    f"Checkpoints 1–8 của phiên {run}, gồm cột Checkpoint, Agent, Plan, Boundary, Merged subplans, Source outcome và Decision")
def front(anchor,label):
    para=d.add_paragraph(label+"\t000")
    anchor._p.addprevious(para._p)
    para._p.insert(0,copy.deepcopy(p[138]._p.pPr))
    for r in para.runs:
        r.font.name="Times New Roman";r.font.size=Pt(10.5)
front(p[139],"Hình 2.2. Mô hình AuctionState trong tab CSL Model")
front(p[140],"Hình 2.4. Nhóm AuctionGroup của mô hình AuctionStateGoals")
front(p[140],f"Hình 2.5. Bảng Checkpoints của phiên Auction {run[:8]}")
d.save(e/"staged.docx")
print(f"New run {run}; trace has {len(trace)} checkpoints.")
