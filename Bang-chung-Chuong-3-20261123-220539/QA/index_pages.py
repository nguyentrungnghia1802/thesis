import os,pathlib,re,unicodedata,json
from docx import Document
from pypdf import PdfReader
p=pathlib.Path(os.environ["THESIS_EVIDENCE"])/"QA"
def norm(s):
    return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",s).replace("\u00ad","")).strip()
def loadpages(path):
    output=[]
    for i,page in enumerate(PdfReader(path).pages):
        raw=page.extract_text()
        top=raw.strip().split("\n",1)[0].strip()
        label=top if re.fullmatch(r"[ivx]+|\d+",top) else str(i+1)
        output.append((label,norm(raw)))
    return output
pages=loadpages(p/"staged.pdf")
def find_first_start(text):
    return next(i for i,(_,x) in enumerate(pages) if x.split(" ",1)[-1].startswith(text))
lists_start=find_first_start("DANH MỤC HÌNH")
intro_start=find_first_start("MỞ ĐẦU Hệ thống")
chapter_start=find_first_start("CHƯƠNG 1. KIẾN THỨC NỀN TẢNG Đặc tả")
chapter3_start=find_first_start("CHƯƠNG 3. TRIỂN KHAI VÀ THỰC NGHIỆM 3.1.")
doc=Document(p/"chapter-staged.docx")
printed={}
active=False
for para in doc.paragraphs:
    if para.text=="MỤC LỤC": active=True; continue
    if para.text=="MỞ ĐẦU": break
    if not active or "\t" not in para.text: continue
    title,old=para.text.rsplit("\t",1)
    if title in ("DANH MỤC HÌNH","DANH MỤC BẢNG"):
        found=next(label for label,s in pages[lists_start:intro_start] if title in s)
    elif title=="MỞ ĐẦU":
        found=pages[intro_start][0]
    else:
        cap=re.match(r"((?:Hình|Bảng) \d+\.\d+)\. ",title)
        needle=norm(" ".join(title.split()[:6]) if cap else title)
        start=chapter_start if not cap or not cap[1].endswith("3.1") else chapter_start
        hits=[label for label,s in pages[start:] if needle in s]
        if not hits:
            if old=="000" or title.startswith(("3.","CHƯƠNG 3","TÀI LIỆU THAM KHẢO")): raise ValueError(title)
            print("Unchanged existing TOC unmatched:",title)
            continue
        found=hits[0]
    printed[title]=found
    if old!=found:
        for run in para.runs[::-1]:
            if run.text.endswith(old):
                run.text=run.text[:-len(old)]+found
                break
        else: raise ValueError(f"Cannot find page field: {title}")
assert len(printed)>75
(p/"page-index.json").write_text(json.dumps(printed,ensure_ascii=False,indent=2),encoding="utf8")
doc.save(p/"chapter-reviewed.docx")
print(f"Updated {len(printed)} page references. Chapter 3 starts at printed page {pages[chapter3_start][0]}; bibliography page {printed['TÀI LIỆU THAM KHẢO']}.")
