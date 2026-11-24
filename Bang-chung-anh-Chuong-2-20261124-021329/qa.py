import hashlib,json,os,pathlib,re
from zipfile import ZipFile
from lxml import etree
from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader
from PIL import Image,ImageDraw
import pypdfium2 as pdfium
e=pathlib.Path(os.environ["THESIS_EVIDENCE"])
original=Document(os.environ["THESIS_BACKUP"])
revised=Document(e/"reviewed.docx")
imgdir=e/"phien-chinh-thuc"
ch3="CHƯƠNG 3. TRIỂN KHAI VÀ THỰC NGHIỆM"
def text(x):return "".join(x.xpath(".//w:t/text()"))
def canon_tail(d,first):
    rows=list(d.element.body)
    i=next(i for i,x in enumerate(rows) if text(x)==first)
    return [etree.tostring(x,method="c14n") for x in rows[i:]]
assert canon_tail(original,ch3)==canon_tail(revised,ch3),"Chương 3 changed"
assert not any("[Ảnh chụp cần bổ sung]" in p.text for p in revised.paragraphs)
def meta_images(doc):
    result={}
    for p in doc.paragraphs:
        if p.style.name=="Caption" and p.text.startswith("Hình 2.") and "Trích nguyên hình từ [28" in p.text:
            node=p._p.getprevious()
            refs=node.xpath(".//a:blip")
            assert len(refs)==1
            img=doc.part.related_parts[refs[0].get(qn("r:embed"))].blob
            result[p.text.split("Siêu mô hình",1)[1]]=hashlib.sha256(img).hexdigest()
    return result
assert len(meta_images(original))==2 and meta_images(original)==meta_images(revised)
prefix="Minh họa từ vết Auction."
a=next(p.text for p in original.paragraphs if p.text.startswith(prefix))
b=next(p.text for p in revised.paragraphs if p.text.startswith(prefix))
assert b.startswith(a) and "58 checkpoint" in a and "mốc 39" in a and "3868eb28" in a
assert all(item.exists() and item.stat().st_size for item in imgdir.glob("*-original.png"))
assert len([p for p in revised.paragraphs if p.style.name=="Caption" and p.text.startswith("Hình 2.")])==5
index=json.loads((e/"page-index.json").read_text(encoding="utf8"))
pdf=e/"reviewed.pdf"
raw=[p.extract_text() for p in PdfReader(pdf).pages]
chap2=next(i for i,t in enumerate(raw) if re.match(r"23\s+CHƯƠNG 2\.",t))
chap3=next(i for i,t in enumerate(raw) if re.match(r"\d+\s+CHƯƠNG 3\.",t))
for key,page in index.items():
    if key.startswith("Hình 2."):
        ref=key.split(" ",2)[1]
        locations=[idx for idx in range(chap2,chap3) if re.search(r"(?m)^Hình "+re.escape(ref)+r" ",raw[idx])]
        assert len(locations)==1,(ref,locations)
        assert raw[locations[0]].splitlines()[0].strip()==page
        assert any(line.rstrip().endswith(page) and line.startswith("Hình "+ref+" ") for t in raw[6:10] for line in t.splitlines()),(ref,page)
print(f"Chương 2 trang in 23–{raw[chap3-1].splitlines()[0].strip()}. Chương 3 controls unchanged, both metamodel image hashes and TN01 data preserved.")
doc=pdfium.PdfDocument(pdf)
def render(seq,name):
    w,h=475,680
    seq=list(seq)
    out=Image.new("RGB",(3*w,h*((len(seq)+2)//3)),"#eeeeee")
    for k,i in enumerate(seq):
        im=doc[i].render(scale=1.55).to_pil()
        im.save(e/f"qa-{i+1:02d}.png")
        im.thumbnail((w-12,h-22))
        x,y=w*(k%3),h*(k//3)
        ImageDraw.Draw(out).text((x+7,y+6),f"PDF {i+1} / {raw[i].splitlines()[0].strip()}",fill="#222")
        out.paste(im,(x+6,y+18))
    out.save(e/f"qa-{name}.png")
render([6,7,8],"front")
figure_pages=sorted({idx for idx,t in enumerate(raw) if re.search(r"(?m)^Hình 2\.[1-5]\. ",t) and chap2<=idx<chap3})
render(figure_pages,"figures")
render(range(chap2,chap3),"chapter")
