
import json
from pathlib import Path
import re
import sys
import unicodedata

from docx import Document
from pypdf import PdfReader
from PIL import Image

def norm(text):
    return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",text).replace("\u00ad","").replace("\u200b","")).strip()

mode, root, file, pdf, output = sys.argv[1:6]
root, file, pdf, output = map(Path,(root,file,pdf,output))
document=Document(file)
reader=PdfReader(pdf)
pages=[]
for physical,page in enumerate(reader.pages,1):
    lines=[norm(s) for s in page.extract_text().splitlines() if norm(s)]
    label=lines.pop(0) if lines and re.fullmatch(r"\d+|[ivx]+",lines[0]) else ""
    pages.append((physical,label,lines," ".join(lines)))

start=next(i for i,(_,label,lines,_) in enumerate(pages) if label=="1" and lines[0].startswith("CHƯƠNG 1."))
active=False
index={}
for paragraph in document.paragraphs:
    entry=paragraph.text.strip()
    if entry=="MỤC LỤC":
        active=True
        continue
    if entry=="MỞ ĐẦU":
        break
    if not active or "\t" not in entry:
        continue
    title, old=entry.rsplit("\t",1)
    title=norm(title)
    def matching(line,text):
        return line==text or line.startswith(text+" ") or line.startswith(text+".")
    def anchored(page):
        return any(matching(l,title) or (title.startswith(l+" ") and l.startswith(title.split(" ")[0]+" ") and len(l)>25)
                   for l in page[2])
    if title in {"DANH MỤC HÌNH","DANH MỤC BẢNG","MỞ ĐẦU"}:
        found=[page for page in pages[:start] if title in page[2]]
    else:
        broader=[page for page in pages[start:] if title in page[3] or any(matching(l,title) for l in page[2])]
        found=[page for page in broader if anchored(page)]
        if not found and re.match(r"(Hình |Bảng )",title):
            # Existing legacy list entries can differ by one punctuation character.
            lead=re.match(r"(Hình |Bảng )\d+\.\d+(?!\d)",title)[0]
            found=[page for page in pages[start:] if any(l.startswith(lead+" ") and l[0:len(title.split(" ",2)[-1])].strip()
                  for l in page[2]) and title in page[3]]
    if len(found)!=1 or not found[0][1]:
        raise RuntimeError((title,old,[(page[0],page[1]) for page in found]))
    physical,label,*_=found[0]
    index[title]=dict(physical=physical,label=label)
    if label!=old:
        if mode!="update":
            raise RuntimeError(f"{title} has {old} but appears on page {label}")
        run=paragraph.runs[-1]
        if not run.text.endswith(old):
            raise RuntimeError((title,run.text,old))
        run.text=run.text[:-len(old)]+label

metadata=json.loads((root/"figure-index.json").read_text(encoding="utf8"))
figures=metadata["figures"]
tables=metadata["tables"]
expected={f"Hình {f['number']} {f['title']}" for f in figures.values()}|{f"Bảng {f['number']} {f['title']}" for f in tables.values()}
assert expected <= index.keys(),expected-index.keys()
if mode=="update":
    document.save(output)
else:
    for f in figures.values():
        caption=f"Hình {f['number']} {f['title']}"
        page=reader.pages[index[caption]["physical"]-1]
        with Image.open(root/f["path"]) as im:
            ar=im.width/im.height
        assert any(abs(image.image.width/image.image.height/ar-1)<0.036 for image in page.images),caption
    assert not any("[Bổ sung ảnh từ hệ thống." in paragraph.text for paragraph in document.paragraphs)
(root/"page-index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf8")
print(f"{mode}: {len(index)} mục. PDF {len(pages)} trang. {len(figures)} ảnh mới, {len(tables)} bảng mới.")
for k in index:
    if k in expected or k=="DANH MỤC BẢNG" or k.startswith(("3.","CHƯƠNG 3.","KẾT LUẬN")):
        print(index[k]["label"],k)

