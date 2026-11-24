import os,pathlib,re,unicodedata,json
from docx import Document
from pypdf import PdfReader
e=pathlib.Path(os.environ["THESIS_EVIDENCE"])
def norm(s):
    return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",s).replace("\u00ad","")).strip()
def read_pages(file):
    output=[]
    for idx,page in enumerate(PdfReader(file).pages):
        raw=page.extract_text().strip()
        match=re.match(r"^(\d+|[ivx]+)\s*\n",raw)
        page_number=match[1] if match else str(idx+1)
        body=raw[match.end():] if match else raw
        output.append((page_number,norm(body),[norm(s) for s in body.splitlines()]))
    return output
pages=read_pages(e/"staged.pdf")
start=next(i for i,(_,body,_) in enumerate(pages) if body.startswith("CHƯƠNG 1. KIẾN THỨC"))
index={}
d=Document(e/"staged.docx")
active=False
for p in d.paragraphs:
    text=p.text
    if text=="MỤC LỤC": active=True; continue
    if text=="MỞ ĐẦU": break
    if not active or "\t" not in text: continue
    title,old=text.rsplit("\t",1)
    if title in ("DANH MỤC HÌNH","DANH MỤC BẢNG","MỞ ĐẦU"):
        matches=[label for label,body,lines in pages[:start] if title in lines]
    else:
        number=re.match(r"((Hình|Bảng) \d+\.\d+\.) ",title)
        if number: matches=[label for label,body,lines in pages[start:] if any(l.startswith(number[1]+" ") for l in lines)]
        else:
            lead=norm(title)
            number=re.match(r"\d+(?:\.\d+)+\.",title)
            if number: matches=[label for label,body,lines in pages[start:] if any(line.startswith(number[0]+" ") for line in lines) and lead in body]
            else: matches=[label for label,body,lines in pages[start:] if lead in body]
    if not matches:
        assert old!="000" and title.startswith("1."),title
        continue
    new=matches[0]
    index[title]=new
    if old==new: continue
    last=p.runs[-1]
    assert last.text.endswith(old),(title,last.text,old)
    last.text=last.text[:-len(old)]+new
assert len(index)==101,len(index)
assert all(k in index for k in (
    "Hình 2.1. Siêu mô hình CSL",
    "Hình 2.2. Mô hình AuctionState trong tab CSL Model",
    "Hình 2.3. Siêu mô hình iStar mở rộng với điều kiện",
    "Hình 2.4. Nhóm AuctionGroup của mô hình AuctionStateGoals"))
(e/"page-index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf8")
d.save(e/"reviewed.docx")
print("Updated pagination across TOC and lists")
for t,v in index.items():
    if t.startswith(("Hình 2.","Hình 3.","CHƯƠNG 3.","PHỤ LỤC")) or t=="TÀI LIỆU THAM KHẢO": print(t,v)
