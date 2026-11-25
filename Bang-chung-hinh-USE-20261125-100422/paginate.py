import json
from pathlib import Path
import re
import sys
import unicodedata

from docx import Document
from pypdf import PdfReader

def norm(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).replace("\u00ad", "")).strip()

mode, file, pdf = sys.argv[1:4]
document = Document(file)
reader = PdfReader(pdf)
pages = []
for physical, page in enumerate(reader.pages, start=1):
    lines = [norm(s) for s in page.extract_text().splitlines() if norm(s)]
    label = lines.pop(0) if lines and re.fullmatch(r"\d+|[ivx]+", lines[0]) else ""
    pages.append((physical, label, lines, " ".join(lines)))

start = next(i for i, (_, label, lines, _) in enumerate(pages) if label == "1" and lines[0].startswith("CHƯƠNG 1."))
active = False
index = {}
for paragraph in document.paragraphs:
    current = paragraph.text.strip()
    if current == "MỤC LỤC":
        active = True
        continue
    if current == "MỞ ĐẦU":
        break
    if not active or "\t" not in current:
        continue
    title, old = current.rsplit("\t", 1)
    title = norm(title)
    def matching(line, text):
        return line == text or line.startswith(text + " ") or line.startswith(text + ".")
    if title in {"DANH MỤC HÌNH", "DANH MỤC BẢNG", "MỞ ĐẦU"}:
        found = [p for p in pages[:start] if title in p[2]]
    else:
        number = re.match(r"\d+(?:\.\d+)+\. ", title)
        match = [p for p in pages[start:] if any(matching(line,title) for line in p[2]) or title in p[3]]
        if title.startswith(("Hình ", "Bảng ")):
            found = [p for p in match if any(matching(line,title) or (line and title.startswith(line + " ")) for line in p[2])]
        elif number:
            found = [p for p in match if any(matching(line,title) or (line.startswith(number[0]) and title.startswith(line + " ")) for line in p[2])]
        else:
            found = [p for p in match if any(matching(line,title) or (line and title.startswith(line + " ")) for line in p[2])]
    if len(found) != 1 or not found[0][1]:
        raise RuntimeError((title, old, [(p[0],p[1]) for p in found]))
    physical, label, *_ = found[0]
    index[title] = dict(physical=physical, label=label)
    if label != old:
        if mode != "update":
            raise RuntimeError(f"{title} has {old}, should be {label}")
        run = paragraph.runs[-1]
        if not run.text.endswith(old):
            raise RuntimeError((title, run.text, old))
        run.text = run.text[:-len(old)] + label
figs = json.loads(Path("figure-index.json").read_text(encoding="utf8"))
expected = {f"Hình {f['number']} {f['title']}" for f in figs.values()}
assert expected <= index.keys(), expected-index.keys()
if mode == "update":
    document.save("reviewed.docx")
else:
    for figure in expected:
        page = reader.pages[index[figure]["physical"] - 1]
        assert len(page.images)>0, figure
Path("page-index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf8")
print(f"{mode}: {len(index)} page entries and {len(expected)} updated figure entries. PDF: {len(pages)} pages.")

