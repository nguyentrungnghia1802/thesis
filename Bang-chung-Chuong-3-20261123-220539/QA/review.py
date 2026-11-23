import hashlib,json,os,re,pathlib
from zipfile import ZipFile
from lxml import etree
from pypdf import PdfReader
from PIL import Image,ImageDraw
import pypdfium2 as pdfium
p=pathlib.Path(os.environ["THESIS_EVIDENCE"])
qa=p/"QA"
root=pathlib.Path(os.environ["THESIS_USE"])
ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
def contents(doc):
    with ZipFile(doc) as z:
        xml=etree.fromstring(z.read("word/document.xml"))
    return xml.find("w:body",ns)
def text(x): return "".join(x.xpath(".//w:t/text()",namespaces=ns))
old=contents(os.environ["THESIS_DRAFT"])
new=contents(qa/"chapter-reviewed.docx")
def from_to(body,start,end):
    rows=list(body)
    a=next(i for i,x in enumerate(rows) if text(x)==start)
    b=next(i for i,x in enumerate(rows) if text(x)==end)
    return [etree.tostring(x,method="c14n") for x in rows[a:b]]
one="CHƯƠNG 1. KIẾN THỨC NỀN TẢNG"
three="CHƯƠNG 3. TRIỂN KHAI VÀ THỰC NGHIỆM"
assert from_to(old,one,three)==from_to(new,one,three),"Chapters 1 and 2 differ"
def body_text(body,start,end):
    return [etree.fromstring(x) for x in from_to(body,start,end)]
assert [text(x) for x in body_text(old,"MỞ ĐẦU",one)]==[text(x) for x in body_text(new,"MỞ ĐẦU",one)]
pdf=PdfReader(qa/"reviewed.pdf")
pdf_raw=[page.extract_text() for page in pdf.pages]
page_index=json.loads((qa/"page-index.json").read_text(encoding="utf8"))
figure_page=next(page for title,page in page_index.items() if title.startswith("Hình 3.7. "))
refs_page=page_index["TÀI LIỆU THAM KHẢO"]
assert "DANH MỤC HÌNH" in pdf_raw[8] and re.search(r"Hình 3\.7\..*"+figure_page+r"\b",pdf_raw[8])
assert re.search(r"TÀI LIỆU THAM KHẢO\s+\.+\s*"+refs_page+r"\b",pdf_raw[7])
chapter_start=next(i for i,t in enumerate(pdf_raw) if re.match(r"34\s+CHƯƠNG 3",t))
chapter_end=next(i for i,t in enumerate(pdf_raw) if re.match(refs_page+r"\s+TÀI LIỆU THAM KHẢO",t))
chapter="\n".join(pdf_raw[chapter_start:chapter_end])
assert len(re.findall(r"(?m)^Hình 3\.[1-7]\.\s",chapter))==7
assert "HOLD_UNVERIFIED" in chapter and "58/58" in chapter
def compact(s): return re.sub(r"\s+","",s)
assert "[46]NguyễnĐứcQuyền" in compact(pdf_raw[-1])
doc=pdfium.PdfDocument(qa/"reviewed.pdf")
for base, seq in (("front",[6,7,8,9]),("chapter",list(range(chapter_start,chapter_end))),("refs",list(range(chapter_end,len(doc))))):
    W,H=470,665
    out=Image.new("RGB",(W*3,H*((len(seq)+2)//3)),"#eeeeee")
    for j,i in enumerate(seq):
        im=doc[i].render(scale=1.65).to_pil()
        im.save(qa/f"page-{i+1:02d}.png")
        im.thumbnail((W-12,H-24))
        x,y=j%3*W,j//3*H
        out.paste(im,(x+6,y+20))
        ImageDraw.Draw(out).text((x+8,y+5),f"PDF {i+1} | {pdf_raw[i].splitlines()[0].strip()}",fill="#222")
    out.save(qa/f"review-{base}.png")
print(f"Verified unchanged Ch. 1–2 XML and introduction text. Chapter 3: {chapter_end-chapter_start} pages; total {len(pdf.pages)}.")
def hash(path): return hashlib.sha256(path.read_bytes()).hexdigest()
a=p/"TN01"/"input"; b=root/"use-plugin/src/main/resources/example/auction"
files=["auction.jcm","src/agt/auction_capabilities.asl","src/env/auction_env/AuctionArtifact.java","src/org/auction-os.xml"]
with (p/"TN01/source-comparison.tsv").open("w",encoding="utf8") as f:
    f.write("relative_path\tTN01_sha256\tbundled_USE_sha256\n")
    for path in files:
        f.write(f"{path}\t{hash(a/path)}\t{hash(b/path)}\n")
