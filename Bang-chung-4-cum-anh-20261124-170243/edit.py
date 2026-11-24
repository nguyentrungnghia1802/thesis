
import os,pathlib,re,copy,json
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
e=pathlib.Path(os.environ["THESIS_EVIDENCE"])
d=Document(os.environ["THESIS_BACKUP"])
p=d.paragraphs
data=json.loads((e/"figure-evidence.json").read_text(encoding="utf8"))
markers=[i for i,para in enumerate(p) if para.text.startswith("[Ảnh chụp cần bổ sung]")]
assert markers==[388,520,523,525],markers
assert all(str(p[i].runs[0].font.color.rgb)=="C00000" for i in markers)
m,g,u,k,r=(data[key] for key in ("mapping","goal","missing","persistent","restored"))
def short(row):return row["run"][:8]
def num(n):return str(n).replace(".",",")
def rename(par,old,new):
    runs=[run for run in par.runs if old in run.text]
    assert len(runs)==1,(old,par.text)
    runs[0].text=runs[0].text.replace(old,new,1)
for index in (148,428,430):rename(p[index],"Hình 2.5","Hình 2.6")
rename(p[529],"các ảnh Chương 2 dùng phiên db329b13","Hình 2.6 dùng phiên db329b13")
rename(p[529],"Phiên ảnh được ghi riêng với TN01.",f"Hình 2.5 dùng phiên {short(m)}. Hai phiên chụp ảnh được ghi riêng với TN01.")
lead={
 387:" Hình 2.5 đối chiếu hai trạng thái ở một phiên chụp riêng.",
 519:" Hình 3.8 đối chiếu hai checkpoint kề nhau của lần chạy chụp ảnh.",
 522:" Hình 3.9 cho thấy thông báo thiếu giá tốt nhất tại checkpoint chuyển giao.",
 524:" Hình 3.10 và Hình 3.11 đối chiếu hai Console với kết quả OCL ở cuối nhóm plan.",
}
for index,s in lead.items():p[index].add_run(s)
def image(par,file):
    fmt=par.paragraph_format
    fmt.alignment=WD_ALIGN_PARAGRAPH.CENTER
    fmt.first_line_indent=Inches(0)
    fmt.space_before=Pt(5);fmt.space_after=Pt(0);fmt.line_spacing=1
    fmt.keep_together=True;fmt.keep_with_next=True
    width=6.10
    if file in ("persistent-word.png","restored-word.png"):width=5.76
    return par.add_run().add_picture(str(e/file),width=Inches(width))
def caption(par,text):
    c=d.add_paragraph(text,"Caption")
    par._p.addnext(c._p)
    fmt=c.paragraph_format
    fmt.alignment=WD_ALIGN_PARAGRAPH.CENTER
    fmt.first_line_indent=Inches(0)
    fmt.space_after=Pt(7);fmt.space_before=Pt(3)
    fmt.keep_with_next=False;fmt.keep_together=True
    run=c.runs[0];run.font.name="Times New Roman";run.font.size=Pt(11);run.font.color.rgb=RGBColor.from_string("000000")
    return c
figs=[
 (388,m,"2.5",f"Đối chiếu Artifacts và OAL State tại checkpoint {m['sequence']}, phiên Auction {short(m)}. Giá của a1 và a2 lần lượt là {num(m['values']['a1'])} và {num(m['values']['a2'])}.",
       f"Đối chiếu trạng thái Auction tại checkpoint {m['sequence']}"),
 (520,g,"3.8",f"TN05, phiên {short(g)}. Giá tăng từ 10 ở checkpoint {g['previous']} lên 20 ở checkpoint {g['sequence']}. Tại mốc {g['sequence']}, BidNeverIncreases ở trạng thái VIOLATED, cả {g['pass_count']} lần đánh giá bất biến đều PASS và quyết định là HOLD_FAILURE.",
       "TN05: giá tăng và vi phạm BidNeverIncreases"),
 (523,u,"3.9",f"TN06, phiên {short(u)}, checkpoint {u['sequence']} (AGENT_HANDOFF). USE trả HOLD_UNVERIFIED khi thiếu Auction.best_bid. Hàng “?” trên giao diện ứng với sequence {u['sequence']} trong Console.",
       "TN06: giữ dừng khi thiếu Auction.best_bid"),
 (525,k,"3.10",f"TN07 giữ âm, phiên {short(k)}, checkpoint {k['sequence']}. Counter giữ giá trị −1 đến cuối nhóm plan, Nonnegative = FAIL và quyết định là HOLD_FAILURE.",
       "TN07: giữ −1 đến cuối nhóm plan"),
 (525,r,"3.11",f"TN07 khôi phục, phiên {short(r)}, checkpoint {r['sequence']}. Console ghi −1 rồi 2 trong cùng nhóm plan. Nonnegative = PASS và quyết định là APPROVE.",
       "TN07: khôi phục về 2 trước checkpoint"),
]
last={}
for pos,row,label,desc,listing in figs:
    if pos not in last:
        node=p[pos];node.clear()
    else:
        node=d.add_paragraph()
        last[pos]._p.addnext(node._p)
    shape=image(node,row["image"])
    shape._inline.docPr.set("descr",f"{listing}. Phiên {row['run']}, checkpoint {row['sequence']}.")
    last[pos]=caption(node,f"Hình {label}. {desc}")
    anchor=p[148] if label.startswith("2.") else p[156]
    entry=d.add_paragraph(f"Hình {label}. {listing}\t000")
    anchor._p.addprevious(entry._p)
    entry._p.insert(0,copy.deepcopy(p[147]._p.pPr))
    f=entry.runs[0].font;f.name="Times New Roman";f.size=Pt(10.5)
d.save(e/"staged.docx")

