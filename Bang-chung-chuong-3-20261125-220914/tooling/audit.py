
from pathlib import Path
import re
import json
import sys
from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader

root,base,updated,pdf=map(Path,sys.argv[1:5])
old,new=Document(base),Document(updated)
def between(d, first, last):
    p=d.paragraphs
    a=next(i for i,x in enumerate(p) if first(x))
    z=next(i for i,x in enumerate(p) if i>a and last(x))
    return p[a:z]
def heading(prefix):
    return lambda p:p.style.name.startswith("Heading 1") and p.text.startswith(prefix)

def media(d,area):
    out=[]
    for p in area:
        for node in p._p.xpath(".//a:blip"):
            rid=node.get(qn("r:embed"))
            if rid:
                out.append(d.part.related_parts[rid].blob)
    return out

old_ch1=between(old,heading("CHƯƠNG 1."),heading("CHƯƠNG 2."))
new_ch1=between(new,heading("CHƯƠNG 1."),heading("CHƯƠNG 2."))
assert [p._p.xml for p in old_ch1]==[p._p.xml for p in new_ch1]
assert media(old,old_ch1)==media(new,new_ch1)
assert [el._sectPr.xml for el in old.sections]==[el._sectPr.xml for el in new.sections]
old_ch2=between(old,heading("CHƯƠNG 2."),heading("CHƯƠNG 3."))
new_ch2=between(new,heading("CHƯƠNG 2."),heading("CHƯƠNG 3."))
sig_old=[p.text for p in old_ch2 if p.text and not p.text.startswith("[Bổ sung ảnh từ hệ thống.")]
sig_new=[p.text for p in new_ch2 if p.text and not p.text.startswith((
    "Phép chiếu cũng giữ việc đảm nhiệm",
    "Hình 2.7 Vai trò trong nhóm agrp",
    "Hình 2.8 Tác tử, vai trò và nhóm",
    "Trong Hình\u00a02.7, mục Players",
))]
assert sig_new==[t.replace("Hình 2.7","Hình 2.9") for t in sig_old]
old_ch2_media=media(old,old_ch2)
new_ch2_media=media(new,new_ch2)
assert new_ch2_media[:6]==old_ch2_media[:6] and new_ch2_media[-1]==old_ch2_media[-1]
assert [t._tbl.xml for t in new.tables[:2]]==[t._tbl.xml for t in old.tables]
def tail(d):
    p=d.paragraphs
    return p[next(i for i,x in enumerate(p) if heading("KẾT LUẬN")(x)):]
assert [p._p.xml for p in tail(old)]==[p._p.xml for p in tail(new)]
new_ch3=between(new,heading("CHƯƠNG 3."),heading("KẾT LUẬN"))
old_ch3=between(old,heading("CHƯƠNG 3."),heading("KẾT LUẬN"))
assert [(p.style.name,p.text) for p in new_ch3 if p.style.name.startswith("Heading")]==[(p.style.name,p.text) for p in old_ch3 if p.style.name.startswith("Heading")]
caps={}
for p in new.paragraphs:
    if p.style.name=="Caption" and (m:=re.match(r"(Hình|Bảng)\s+(\d+\.\d+)\b",p.text)):
        key=(m[1],m[2])
        assert key not in caps,key
        caps[key]=p.text
for p in (*new_ch1,*new_ch2,*new_ch3):
    for m in re.finditer(r"(Hình|Bảng)\s+(\d+\.\d+)\b",p.text):
        assert (m[1],m[2]) in caps, (p.text,m[0])
assert all(p.text.endswith(".") for p in new_ch3 if p.style.name=="Caption")
assert not any("[Bổ sung ảnh" in p.text for p in new.paragraphs)
assert len(new.tables)==5
print("Verified scope, Ch.3 headings, reference labels and native tables.")
index=json.loads((root/"page-index.json").read_text(encoding="utf8"))
figs=json.loads((root/"figure-index.json").read_text(encoding="utf8"))["figures"]
pairs=[("moise-org","oal-org"),("mid-a1","mid-a2"),("final-a1","final-a2"),
       ("bid-before","bid-after"),("negative-console","negative-checkpoint"),
       ("recovered-console","recovered-checkpoint")]
def detail(k):
    v=figs[k]
    return index[f"Hình {v['number']} {v['title']}"]["label"]
for a,b in pairs:
    assert detail(a)==detail(b),(a,b,detail(a),detail(b))
    print(a,b,"printed page",detail(a))
print("Verified Word PDF:",len(PdfReader(pdf).pages),"pages")

