
import os, pathlib, re, json
from lxml import etree
from docx import Document
from pypdf import PdfReader
from PIL import Image,ImageDraw
import pypdfium2 as pdfium
e=pathlib.Path(os.environ["THESIS_EVIDENCE"])
original=Document(os.environ["THESIS_BACKUP"])
updated=Document(e/"reviewed.docx")
d=json.loads((e/"figure-evidence.json").read_text(encoding="utf8"))
idx=json.loads((e/"page-index.json").read_text(encoding="utf8"))
def text(node):return "".join(node.xpath(".//w:t/text()"))
base=list(original.element.body); after=list(updated.element.body)
skip_src={original.paragraphs[i]._p for i in [387,388,428,430,519,520,522,523,524,525,529]}
starts=["Hình 2.5. Đối chiếu Artifacts","Hình 2.6. Tab Checkpoints","Hình 3.8. TN05","Hình 3.9. TN06","Hình 3.10. TN07","Hình 3.11. TN07"]
original_leads=[original.paragraphs[i].text for i in [387,519,522,524]]
for value in original_leads:assert sum(p.text.startswith(value) for p in updated.paragraphs)==1
def compact_filtered(rows,is_old):
    start=next(i for i,el in enumerate(rows) if text(el)=="MỞ ĐẦU")
    out=[]
    for node in rows[start:]:
        row=text(node)
        if is_old and node in skip_src:continue
        if not is_old:
            if any(row.startswith(lead) for lead in original_leads):continue
            if row.startswith("Khả năng tái hiện một vết và khả năng lặp lại một lần chạy mới"):continue
            if row.startswith(tuple(starts)):continue
            if row==original.paragraphs[428].text.replace("Hình 2.5","Hình 2.6"):continue
            if any("Phiên " in el.get("descr","") for el in node.xpath("./w:r/w:drawing/*/wp:docPr")):continue
        out.append(etree.tostring(node,method="c14n"))
    return out
assert compact_filtered(base,True)==compact_filtered(after,False),"Word XML changed outside marked sections"
assert not any("[Ảnh chụp cần bổ sung]" in p.text for p in updated.paragraphs)
raw=[p.extract_text() for p in PdfReader(e/"reviewed.pdf").pages]
doc=pdfium.PdfDocument(e/"reviewed.pdf")
pages=[]
for number in ("2.5","2.6","3.8","3.9","3.10","3.11"):
    id=f"Hình {number}."
    printed=next(page for title,page in idx.items() if title.startswith(id+" "))
    loc=[i for i,p in enumerate(raw) if p.splitlines()[0].strip().isdigit() and re.search(r"(?m)^"+re.escape(id)+r" ",p)]
    assert len(loc)==1,(id,loc)
    i=loc[0]
    assert raw[i].splitlines()[0].strip()==printed,(id,printed)
    assert any(line.startswith(id+" ") and line.rstrip().endswith(printed) for t in raw[6:10] for line in t.splitlines()),id
    assert len(PdfReader(e/"reviewed.pdf").pages[i].images)>0
    pages.append(i)
print("preservation and pagination checks completed",[(i+1,raw[i].splitlines()[0].strip()) for i in pages])
indices=[6,7,8]+sorted(set(pages))
W,H=480,685
sheet=Image.new("RGB",(3*W,H*((len(indices)+2)//3)),"#e9e9e9")
for j,i in enumerate(indices):
    png=doc[i].render(scale=1.65).to_pil()
    png.save(e/f"qa-page-{i+1}.png")
    png.thumbnail((W-14,H-28))
    x,y=j%3*W,j//3*H
    ImageDraw.Draw(sheet).text((x+8,y+4),f"PDF {i+1} | {raw[i].splitlines()[0].strip()}",fill="#231f20")
    sheet.paste(png,(x+7,y+21))
sheet.save(e/"qa-review.png")

