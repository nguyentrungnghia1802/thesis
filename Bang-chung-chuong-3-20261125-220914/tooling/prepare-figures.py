
from pathlib import Path
import json, math, shutil
from PIL import Image, ImageDraw, ImageFont, ImageChops
import sys

root=Path(sys.argv[1])
output=root/"hinh-chen"
output.mkdir(exist_ok=True)
facts=json.loads((root/"facts.json").read_text(encoding="utf8"))
org=root/facts["TN05"]["folder"]
palette={"bob":("#135B9B",1),"auctioneer":("#A34B00",2),"agrp":("#287048",3)}
font=ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf",23)

def mark(draw, name, coords, tag_at):
    color,number=palette[name]
    draw.rounded_rectangle(coords, radius=8, outline=color, width=4)
    x,y=tag_at
    r=14
    draw.ellipse((x-r,y-r,x+r,y+r),fill=color)
    draw.text((x,y),str(number),font=font,fill="white",anchor="mm")

def moise():
    image=Image.open(org/"moise-group-original.png").convert("RGB").crop((0,0,796,517))
    data=json.loads((org/"moise-boxes.json").read_text(encoding="utf8"))["boxes"]
    draw=ImageDraw.Draw(image)
    for label in ("bob","auctioneer","agrp"):
        if label!="agrp":
            x=next(q for q in data[label] if q["tag"]=="A" and q["text"]==label)
            p=[int(v*2) for v in (x["x"],x["y"],x["width"],x["height"])]
            rect=(p[0]-5,p[1]-4,p[0]+p[2]+5,p[1]+p[3]+4)
            at=(p[0]+p[2]//2,p[1]+p[3]+24)
        else:
            x=next(q for q in data[label] if q["tag"]=="H2")
            y0,y1=int(x["y"]*2),int((x["y"]+x["height"])*2)
            found=[]
            for y in range(y0,y1):
                for x in range(0,410):
                    r,g,b=image.getpixel((x,y))
                    if r>200 and g<130 and b<130: found.append((x,y))
            rect=(min(x for x,y in found)-7,y0-5,max(x for x,y in found)+9,y1+5)
            at=(rect[2]+24,(y0+y1)//2)
        mark(draw,label,rect,at)
    image.save(output/"moise-org.png")

def oal():
    image=Image.open(org/"oal-org-original.png").convert("RGB").crop((0,28,767,694))
    rows=[x.split("\t") for x in (org/"oal-org-boxes.tsv").read_text().splitlines()]
    draw=ImageDraw.Draw(image)
    for name,x,y,w,h in rows:
        l,top,bw,bh=(math.floor(float(v)*2) for v in (x,y,w,h))
        top -= 28
        rect=(l-7,top-7,l+bw+7,top+bh+7)
        mark(draw,name,rect,(rect[0]-27,top+bh//2))
    image.save(output/"oal-org.png")

def copy(code, source, name, bbox=None):
    original=root/facts[code]["folder"]/source
    target=output/(name+".png")
    if bbox is None:
        shutil.copyfile(original,target)
    else:
        with Image.open(original) as im:
            im.crop(bbox).save(target)

moise()
oal()
copy("Workbench","menu.png","menu")
copy("Workbench","mrv.png","mrv")
copy("Workbench","workbench.png","workbench")
for st in ("mid","final"):
    for a in ("a1","a2"):
        source=root/facts["TN01"]["folder"]/f"{st}-{a}-focused.png"
        with Image.open(source) as image:
            # Retain the native checkpoint, active tab, context and observed rows.
            # Drop only the save toolbar and the unused area below the rows.
            bottom=444 if st=="mid" else 479
            top=image.crop((0,0,1100,38))
            body=image.crop((0,104,1100,bottom))
            print_image=Image.new("RGB",(1100,top.height+body.height))
            print_image.paste(top,(0,0))
            print_image.paste(body,(0,top.height))
            print_image.save(output/f"auction-{st}-{a}.png")
copy("TN03","counter-workbench.png","counter")
copy("TN05","before.png","bid-before")
copy("TN05","after.png","bid-after")
copy("TN05","hold.png","bid-hold")
copy("TN05",f"violation-{facts['TN05']['case_context']}-focused.png","bid-goal",(0,0,1100,408))
copy("TN05","invariants.png","bid-ocl")
copy("TN06","missing-workbench.png","missing")
for code,label in (("TN07-negative","negative"),("TN07-recovered","recovered")):
    copy(code,"console.png",label+"-console")
    copy(code,"counter-workbench.png",label+"-checkpoint")
for q in output.glob("*.png"):
    print(q.name,Image.open(q).size)

