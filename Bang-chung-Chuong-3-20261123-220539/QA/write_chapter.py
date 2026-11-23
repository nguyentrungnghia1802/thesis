import copy,json,os,pathlib,re
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
p=pathlib.Path(os.environ["THESIS_EVIDENCE"])
qa=p/"QA"
backup=os.environ["THESIS_BACKUP"]
doc=Document(backup)
headings={x.text.split(". ",1)[0]:x for x in doc.paragraphs[389:411] if x.style.name in ("Heading 2","Heading 3")}
for h in headings.values():
    h.paragraph_format.keep_with_next=True
    h.paragraph_format.keep_together=True
old=list(doc.paragraphs)
body_pr=copy.deepcopy(old[391]._p.pPr)
for par in old[390:411]:
    if par not in headings.values() and par.style.name=="Normal":
        par._p.getparent().remove(par._p)
def add(anchor, text="", style="Normal"):
    par=doc.add_paragraph(text,style=style)
    anchor.addprevious(par._p)
    return par
def body(anchor,text):
    par=add(anchor,text)
    par._p.insert(0,copy.deepcopy(body_pr))
    return par
def cap(anchor,text,before):
    par=add(anchor,text,"Caption")
    fmt=par.paragraph_format
    fmt.alignment=WD_ALIGN_PARAGRAPH.CENTER
    fmt.first_line_indent=Inches(0)
    fmt.space_before=Pt(5)
    fmt.space_after=Pt(5 if before else 11)
    fmt.keep_together=True
    fmt.keep_with_next=before
    for r in par.runs:
        r.font.name="Times New Roman"
        r.font.size=Pt(11)
    return par
def img(anchor,key,width):
    par=add(anchor); par.alignment=WD_ALIGN_PARAGRAPH.CENTER
    fmt=par.paragraph_format
    fmt.first_line_indent=Inches(0); fmt.space_after=Pt(3); fmt.keep_with_next=True
    shape=par.add_run().add_picture(str(qa/f"use-{key}.png"),width=Inches(width))
    shape._inline.docPr.set("descr",f"Ảnh chụp USE, bằng chứng {key}")
    return par
def table(anchor,title,widths,header,entries):
    cap(anchor,title,True)
    t=doc.add_table(rows=1+len(entries),cols=len(widths))
    anchor.addprevious(t._tbl)
    t.style="Table Grid"; t.autofit=False
    for i,v in enumerate(widths): t.columns[i].width=Inches(v)
    for index, vals in enumerate([header]+entries):
        row=t.rows[index]
        trPr=row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if index==0: trPr.append(OxmlElement("w:tblHeader"))
        for i,(cell,val) in enumerate(zip(row.cells,vals)):
            cell.width=Inches(widths[i])
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=cell.paragraphs[0]
            f=cp.paragraph_format
            f.first_line_indent=Inches(0)
            f.keep_with_next=index<len(entries)
            f.space_after=Pt(4); f.space_before=Pt(4); f.line_spacing=1.05
            cp.alignment=WD_ALIGN_PARAGRAPH.CENTER if i==0 else WD_ALIGN_PARAGRAPH.LEFT
            rr=cp.add_run(val); rr.font.name="Times New Roman"; rr.font.size=Pt(10.5 if len(widths)>3 else 11)
            if index==0:
                rr.bold=True
                tcPr=cell._tc.get_or_add_tcPr()
                shd=OxmlElement("w:shd"); shd.set(qn("w:fill"),"E7EDF3"); tcPr.append(shd)
    f=add(anchor).paragraph_format; f.space_before=Pt(0); f.space_after=Pt(1); f.line_spacing=Pt(4)
def code(anchor,text):
    par=add(anchor)
    f=par.paragraph_format
    f.first_line_indent=Inches(0); f.left_indent=Inches(.17); par.alignment=WD_ALIGN_PARAGRAPH.LEFT
    f.keep_together=True; f.space_after=Pt(8); f.space_before=Pt(3); f.line_spacing=1.02
    run=par.add_run(text); run.font.name="Consolas"; run.font.size=Pt(9)
    box=OxmlElement("w:shd"); box.set(qn("w:fill"),"F2F4F6")
    par._p.get_or_add_pPr().append(box)

content=json.loads((qa/"chapter.json").read_text(encoding="utf-8-sig"))
flow=list(headings)
assert len(flow)==11,flow
for i,label in enumerate(flow):
    anchor=headings[flow[i+1]]._p if i+1<len(flow) else old[411]._p
    for item in content.get(label,[]):
        key,*args=item
        if key=="p": body(anchor,*args)
        elif key=="t": table(anchor,*args)
        elif key=="code": code(anchor,*args)
        elif key=="i":
            img(anchor,args[0],args[1]); cap(anchor,args[2],False)
        elif key=="ii":
            for k,width in args[0]: img(anchor,k,width)
            cap(anchor,args[1],False)
        else: raise ValueError(item)

for empty in old[124:153]:
    assert not empty.text and not empty._p.xpath(".//w:sectPr | .//w:drawing | .//w:br")
    empty._p.getparent().remove(empty._p)
old[153].paragraph_format.page_break_before=True
intro=old[153]._p
listing_pr=copy.deepcopy(old[123]._p.pPr)
def listing_rows(prefix):
    labels=[]
    for par in doc.paragraphs:
        match=re.match(rf"({prefix} \d+\.\d+)\. (.+)",par.text)
        if par.style.name!="Caption" or not match: continue
        title=match[2].split(" Trích từ ",1)[0].split(" Xuất từ ",1)[0].split(" Sơ đồ tổng hợp ",1)[0]
        title=re.sub(r"\.?(?:\s+\[\d+\])+$","",title).rstrip(".")
        if len(title)>87: title=title[:85].rsplit(" ",1)[0]+"…"
        labels.append((match[1],title))
    return labels

for prefix, title in (("Hình","DANH MỤC HÌNH"),("Bảng","DANH MỤC BẢNG")):
    h=add(intro,title,"Front Heading")
    fmt=h.paragraph_format
    fmt.page_break_before=prefix=="Hình"
    fmt.keep_with_next=True; fmt.space_before=Pt(0 if prefix=="Hình" else 9)
    fmt.space_after=Pt(5)
    for key,text in listing_rows(prefix):
        para=add(intro,f"{key}. {text}\t000")
        para._p.insert(0,copy.deepcopy(listing_pr))
        fmt=para.paragraph_format
        fmt.line_spacing=1.01; fmt.space_after=Pt(1); fmt.space_before=Pt(0)
        fmt.keep_together=True
        for run in para.runs: run.font.size=Pt(10.5)

for title in ["DANH MỤC HÌNH","DANH MỤC BẢNG"]:
    para=add(old[66]._p,title+"\t000")
    para._p.insert(0,copy.deepcopy(listing_pr))
ref=doc.add_paragraph("[46] Nguyễn Đức Quyền, Phát triển mô đun sinh tự động biểu đồ UML từ đặc tả FRSL, khóa luận tốt nghiệp, Trường Đại học Công nghệ, Đại học Quốc gia Hà Nội, 2025, Chương 3, tr. 44–52.",style=old[456].style)
if old[456]._p.pPr is not None:
    if ref._p.pPr is not None: ref._p.remove(ref._p.pPr)
    ref._p.insert(0,copy.deepcopy(old[456]._p.pPr))
doc.save(qa/"chapter-staged.docx")
print("Staged native DOCX")
