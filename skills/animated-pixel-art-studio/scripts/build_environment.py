#!/usr/bin/env python3
"""Build an original component-based alpine scene. No external assets or services."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random

from PIL import Image, ImageDraw

SIZE = (640, 360)
# Shared material ramps, darkest to lightest. Every component uses this palette.
C = {
    "ink":"#182b36", "deep":"#243d42", "pine":"#315249", "leaf0":"#42634a",
    "leaf1":"#5d7d4d", "leaf2":"#83964e", "leaf3":"#a9b45f", "leaf4":"#d0cf80",
    "wood0":"#3c3541", "wood1":"#59414a", "wood2":"#78534c", "wood3":"#a57555",
    "wood4":"#c79a63", "plaster":"#d9bc86", "roof0":"#63434a", "roof1":"#94604b",
    "roof2":"#b47a4c", "roof3":"#d69a56", "roof4":"#e8bb73", "stone0":"#48565a",
    "stone1":"#657172", "stone2":"#919889", "stone3":"#b9b9a0", "snow":"#ecedc9",
    "cloud":"#dce5c4", "cloud2":"#b5d8ce", "cloud3":"#83bdcd", "sky":"#399fc2",
    "sky2":"#4aacc7", "sky3":"#83c8cf", "mount0":"#4c91a8", "mount1":"#67aab7",
    "mount2":"#8bc2c5", "water0":"#367f96", "water1":"#4eabb7", "water2":"#93d3cd",
    "foam":"#d8e6c1", "earth0":"#73684b", "earth1":"#a08c56", "earth2":"#c5ae6d",
    "flower":"#d39a86", "window":"#e8cd83",
}
RGB = {k:tuple(bytes.fromhex(v[1:])) for k,v in C.items()}


def canvas():
    return Image.new("RGBA", SIZE)


def poly(im, points, key):
    ImageDraw.Draw(im).polygon(points, fill=C[key])


def rect(im, box, key):
    ImageDraw.Draw(im).rectangle(box, fill=C[key])


def line(im, points, key, width=1):
    ImageDraw.Draw(im).line(points, fill=C[key], width=width)


def masked_texture(im, points, base, tones, seed, count, sx=4, sy=2):
    """Material clusters confined to an authored silhouette, never full-frame noise."""
    mask = Image.new("L",SIZE)
    md = ImageDraw.Draw(mask)
    md.polygon(points,fill=255)
    patch = Image.new("RGBA",SIZE,C[base])
    d=ImageDraw.Draw(patch)
    rng=random.Random(seed)
    bounds=mask.getbbox()
    if bounds is None:
        return
    x0,y0,x1,y1=bounds
    for _ in range(count):
        x,y=rng.randrange(x0,x1),rng.randrange(y0,y1)
        d.rectangle((x,y,x+rng.randint(1,sx),y+rng.randint(0,sy)),fill=C[rng.choice(tones)])
    im.paste(patch,(0,0),mask)


def cloud(im, x, y, scale, seed):
    # Authored contours and internal planes, rather than rings of shaded circles.
    def shape(points,key):
        poly(im,[(round(x+cx*scale),round(y+cy*scale)) for cx,cy in points],key)
    shape([(0,27),(7,16),(18,13),(22,3),(32,0),(37,-11),(47,-15),(49,-30),
           (57,-43),(68,-48),(80,-46),(88,-38),(89,-27),(101,-23),(109,-13),
           (111,0),(125,6),(130,16),(141,18),(152,29),(147,37),(119,41),
           (102,36),(78,43),(61,37),(45,42),(31,34),(13,38)],"cloud3")
    shape([(0,27),(7,16),(18,13),(22,3),(32,0),(37,-11),(47,-15),(49,-30),
           (57,-43),(68,-48),(80,-46),(85,-37),(80,-26),(92,-19),(91,-5),
           (107,4),(112,15),(129,20),(132,29),(117,34),(99,28),(78,35),
           (63,28),(47,35),(31,27),(16,31)],"cloud2")
    shape([(0,27),(7,16),(18,13),(22,3),(32,0),(37,-11),(47,-15),(49,-30),
           (57,-43),(68,-48),(77,-44),(80,-35),(70,-32),(76,-23),(69,-15),
           (77,-7),(72,2),(59,4),(64,13),(55,19),(43,16),(42,25),
           (28,23),(20,29)],"cloud")
    shape([(50,-27),(54,-39),(66,-46),(76,-42),(77,-35),(66,-34),(70,-26),
           (62,-24)],"snow")
    shape([(25,4),(38,-7),(47,-10),(51,-4),(47,4),(53,9),(43,13),(38,8)],"snow")
    shape([(81,9),(90,4),(99,8),(102,14),(98,20),(111,24),(99,27),(90,21)],"cloud")
    shape([(112,22),(122,18),(127,22),(126,27),(116,29)],"cloud")


def tree(im,x,y,s,seed,foreground=False):
    # y is root position. Branches are structural, leaves form connected masses.
    rng=random.Random(seed)
    dark,mid,light=("deep","pine","leaf0") if foreground else ("leaf0","leaf1","leaf2")
    line(im,[(x,y),(x-2*s,y-29*s),(x+4*s,y-55*s)],"wood0",max(1,round(4*s)))
    line(im,[(x,y-23*s),(x-17*s,y-41*s)],"wood1",max(1,round(2*s)))
    line(im,[(x,y-30*s),(x+17*s,y-47*s)],"wood1",max(1,round(2*s)))
    for cx,cy,rad in [(-17,-42,14),(13,-46,17),(-4,-61,16),(2,-40,16)]:
        px,py=x+cx*s,y+cy*s
        rr=rad*s
        points=[(round(px+math.cos(i*math.tau/14)*rr*rng.uniform(.75,1.12)),
                 round(py+math.sin(i*math.tau/14)*rr*.8*rng.uniform(.8,1.1))) for i in range(14)]
        masked_texture(im,points,dark,[mid,mid,light],seed+cx+cy,round(70*s*s),max(2,round(4*s)),max(1,round(2*s)))
        if not foreground:
            for k in range(11):
                xx=round(px+rng.uniform(-.7,.3)*rr); yy=round(py+rng.uniform(-.65,-.1)*rr)
                rect(im,(xx,yy,xx+3,yy+1),"leaf3")


def window(im,x,y,w=9,h=15,lit=False):
    rect(im,(x-2,y-2,x+w+2,y+h+2),"wood0")
    rect(im,(x-1,y-1,x+w,y+h),"wood3")
    rect(im,(x,y,x+w-1,y+h-1),"window" if lit else "deep")
    if not lit:
        rect(im,(x+1,y+1,x+w-2,y+3),"sky")
    line(im,[(x+w//2,y),(x+w//2,y+h)],"wood2")
    line(im,[(x,y+h//2),(x+w,y+h//2)],"wood2")
    rect(im,(x-3,y+h+2,x+w+3,y+h+3),"wood4")


def roof(im,points,seed):
    mask=Image.new("L",SIZE); ImageDraw.Draw(mask).polygon(points,fill=255)
    patch=Image.new("RGBA",SIZE,C["roof0"]); d=ImageDraw.Draw(patch)
    rng=random.Random(seed); x0,y0,x1,y1=mask.getbbox()
    for y in range(y0,y1,5):
        offset=(y//5%2)*4
        for x in range(x0-8+offset,x1,9):
            key=rng.choice(["roof1","roof2","roof2","roof3"])
            d.rectangle((x+1,y,x+8,y+3),fill=C[key])
            d.line([(x+2,y),(x+7,y)],fill=C["roof4"] if key=="roof3" else C["roof3"])
    im.paste(patch,(0,0),mask)
    line(im,points+[points[0]],"wood0",2)
    line(im,[points[0],points[1]],"roof4",2)


def stonewall(im, points, seed):
    mask=Image.new("L",SIZE); ImageDraw.Draw(mask).polygon(points,fill=255)
    patch=Image.new("RGBA",SIZE,C["stone0"]); d=ImageDraw.Draw(patch)
    rng=random.Random(seed); x0,y0,x1,y1=mask.getbbox()
    for y in range(y0,y1,6):
        for x in range(x0-12+(y//6%2)*6,x1,12):
            tone=rng.choice(["stone1","stone1","stone2"])
            d.rectangle((x+1,y+1,x+10,y+4),fill=C[tone])
            d.line([(x+2,y+1),(x+9,y+1)],fill=C["stone3"])
    im.paste(patch,(0,0),mask)


def inn(im):
    # Three distinct volumes with visible gable, side wall and foundations.
    stonewall(im,[(67,235),(191,228),(198,273),(63,278)],31)
    poly(im,[(80,159),(135,111),(187,160),(187,242),(80,251)],"wood0")
    poly(im,[(88,164),(135,121),(178,165),(178,238),(88,246)],"plaster")
    poly(im,[(178,165),(216,151),(216,235),(178,246)],"wood2")
    for y in [171,199,224,242]:
        line(im,[(84,y),(179,y-7),(215,y-17)],"wood0",4)
        line(im,[(84,y-2),(178,y-9)],"wood3")
    for x in [89,111,135,157,178]:
        line(im,[(x,153 if x in [111,135,157] else 165),(x,244-(x-89)//12)],"wood1",4)
    for x in [90,113,138,160]:
        line(im,[(x,176),(x+16,193)],"wood2",2)
        line(im,[(x,205),(x+16,219)],"wood2",2)
    for x in [193,208]:
        line(im,[(x,166),(x,236)],"wood0",3)
    for x in [95,119,145,165]:
        window(im,x,177-(x-95)//16,8,13)
        window(im,x,205-(x-95)//16,8,12,True)
    window(im,194,179,7,14)
    window(im,194,207,7,13,True)
    roof(im,[(69,169),(133,103),(188,157),(179,169),(134,120),(80,179)],7)
    roof(im,[(133,103),(174,91),(222,151),(188,157)],9)
    # Dormer breaks the large tiled plane.
    poly(im,[(170,126),(182,117),(193,136),(173,139)],"wood1")
    window(im,178,126,6,8,True)
    roof(im,[(166,126),(181,112),(197,132),(192,135),(181,119),(171,132)],12)
    rect(im,(155,79,163,102),"stone1")
    rect(im,(153,77,165,80),"stone3")
    line(im,[(158,83),(158,99)],"stone3",2)
    # Entrance porch, hanging sign and roof-supported terrace.
    rect(im,(109,234,132,271),"wood0")
    ImageDraw.Draw(im).pieslice((109,224,132,246),180,360,fill=C["wood0"])
    for x in range(112,131,4):
        line(im,[(x,237),(x,269)],"wood2")
    rect(im,(128,252,129,254),"roof4")
    roof(im,[(72,237),(100,221),(148,225),(157,238),(102,233)],51)
    for x in [79,147]:
        rect(im,(x,238,x+3,273),"wood0")
        line(im,[(x+1,241),(x+1,270)],"wood3")
    line(im,[(185,193),(230,193),(230,200)],"wood0",2)
    line(im,[(188,185),(206,193)],"wood2",2)
    rect(im,(219,200,238,215),"wood0")
    rect(im,(221,202,236,213),"wood3")
    poly(im,[(225,209),(229,204),(233,209)],"window")
    for x in range(89,178,20):
        rect(im,(x,221,x+12,224),"wood0")
        for k in range(0,13,3):
            rect(im,(x+k,218-(k%2),x+k+2,220),"leaf1")
            rect(im,(x+k,217-(k%2),x+k+1,218),"flower")


def tower(im):
    stonewall(im,[(475,149),(506,146),(513,270),(474,278)],42)
    poly(im,[(506,146),(527,157),(529,270),(513,270)],"stone0")
    for y in range(167,254,15):
        line(im,[(514,y),(523,y+2)],"stone1")
    roof(im,[(461,153),(493,107),(536,158),(505,169)],45)
    roof(im,[(493,107),(504,119),(536,158),(519,160)],46)
    window(im,489,176,8,19)
    window(im,489,218,8,19,True)
    rect(im,(492,92,494,108),"wood0")
    line(im,[(478,207),(510,203),(526,210)],"stone3",2)
    # Attached lakeside workshop.
    poly(im,[(523,221),(570,210),(602,229),(601,279),(523,287)],"wood1")
    poly(im,[(529,225),(568,219),(568,279),(529,283)],"plaster")
    for x in [529,548,568]:
        line(im,[(x,225),(x,282)],"wood0",3)
    for y in [244,267]:
        line(im,[(525,y),(571,y-7),(600,y+1)],"wood0",3)
    roof(im,[(512,224),(561,190),(608,225),(569,232)],48)
    window(im,534,248,8,12,True)
    window(im,553,245,8,12)
    rect(im,(578,252,591,279),"wood0")
    line(im,[(580,254),(580,278)],"wood3")


def build(output):
    output=Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Use a new or empty project directory: {output}")
    output.mkdir(parents=True,exist_ok=True)
    assets=output/"components"; assets.mkdir(exist_ok=True)
    chars="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@"
    keys=dict(zip(C,chars))
    scene={"version":1,"name":"Highland Waystation","canvas":list(SIZE),"fps":10,"frames":70,"scale":3,
           "loop":True,"palette":{keys[k]:v for k,v in C.items()},"background":keys["sky"],"sprites":{},"layers":[]}
    plan=[]
    def add(name,ims,note,ticks=1):
        ims=ims if isinstance(ims,list) else [ims]
        names=[]
        for i,im in enumerate(ims):
            sid=f"{name}-{i:02d}"; file=f"components/{sid}.png"
            im.save(output/file); scene["sprites"][sid]={"image":file}; names.append(sid)
        layer={"name":name,"x":0,"y":0}
        layer.update({"sprite":names[0]} if len(names)==1 else {"animation":names,"frame_ticks":ticks})
        scene["layers"].append(layer)
        plan.append({"id":name,"purpose":note,"files":[scene["sprites"][n]["image"] for n in names],
                     "position":[0,0],"native_canvas":list(SIZE),"light":"upper-left","motion":"static" if len(ims)==1 else "authored cel cycle"})

    im=canvas(); rect(im,(0,75,639,152),"sky2"); rect(im,(0,153,639,359),"sky3")
    add("01-sky",im,"Large quiet value bands, shared atmospheric colors.")
    im=canvas(); cloud(im,28,76,1.2,3); cloud(im,388,87,.9,7)
    add("02-cloud-masses",im,"Sculpted cream lobes with cyan shadow clusters. Inspect contour rhythm independently.")
    im=canvas()
    poly(im,[(100,239),(178,176),(203,188),(264,136),(291,169),(330,123),(375,177),(401,165),(454,218),(500,242)],"mount2")
    for points in [[(197,193),(264,136),(289,174),(267,161),(255,173),(257,153),(233,183)],
                   [(282,184),(330,123),(371,175),(338,152),(330,165),(322,148),(315,169)]]:
        poly(im,points,"snow")
    poly(im,[(331,133),(348,170),(363,177),(335,162),(324,185),(326,159)],"cloud2")
    for points in [[(267,152),(274,179),(291,195),(272,187),(255,203),(262,174)],
                   [(331,144),(338,180),(359,195),(344,184),(337,188),(332,174)],
                   [(320,166),(312,195),(285,218),(314,207),(326,186)]]:
        poly(im,points,"cloud2")
    add("03-distant-peaks",im,"Low-contrast distant silhouettes; angular snow planes, no near-field texture.")
    im=canvas()
    for points in [[(0,250),(0,159),(47,119),(96,174),(123,169),(169,211),(237,246)],
                   [(385,247),(432,204),(457,173),(489,129),(516,165),(538,154),(572,192),(640,174),(640,270)]]:
        poly(im,points,"mount0")
    poly(im,[(0,182),(47,119),(64,159),(51,146),(34,176),(11,183)],"mount1")
    poly(im,[(420,224),(489,129),(502,157),(482,153),(466,194),(448,203),(444,217)],"mount1")
    poly(im,[(494,156),(478,208),(514,188),(501,219),(563,235),(640,229),(640,271),(385,255)],"sky")
    add("04-mountain-sides",im,"Frame the central view without competing with architecture.")
    im=canvas(); poly(im,[(182,246),(315,230),(414,241),(507,292),(430,349),(184,337),(111,279)],"water0")
    poly(im,[(260,298),(402,294),(440,359),(238,359)],"water0")
    poly(im,[(300,307),(366,307),(399,359),(273,359)],"water1")
    for y in range(317,360,9):
        line(im,[(297-(y-317)//3,y),(362+(y-317)//2,y)],"water2")
    poly(im,[(214,249),(316,232),(405,242),(452,273),(356,289),(237,276)],"water1")
    for y,x0,x1 in [(240,278,363),(244,256,392),(250,245,407),(259,247,379),(269,279,412),(280,301,413)]:
        line(im,[(x0,y),(x1,y)],"water2")
    add("05-lake-base",im,"Opaque water body stays still; glints are a separate component.")
    im=canvas()
    left=[(0,249),(47,240),(108,257),(173,249),(205,262),(286,291),(273,359),(0,359)]
    right=[(390,293),(445,265),(489,258),(543,267),(589,250),(639,252),(639,359),(430,359)]
    masked_texture(im,left,"leaf1",["leaf2","leaf2","leaf3","leaf0"],14,800,7,1)
    masked_texture(im,right,"leaf1",["leaf2","leaf3","leaf0"],15,700,7,1)
    poly(im,[(0,290),(75,268),(153,270),(244,297),(258,309),(147,290),(73,285),(0,315)],"earth1")
    poly(im,[(0,292),(76,272),(146,274),(233,297),(149,283),(75,280),(0,305)],"earth2")
    add("06-ground",im,"Two connected land silhouettes, horizontal clustered grass and a readable path.")
    im=canvas()
    for x,y,s,seed in [(55,265,.8,1),(220,265,.65,2),(452,276,.6,3),(609,269,.85,4)]:
        tree(im,x,y,s,seed)
    add("07-middle-trees",im,"Shared leaf ramps; trunks and branch attachment remain legible.")
    im=canvas(); inn(im)
    add("08-inn",im,"Hero component: three volumes, perspective roof tiles, joinery, porch, sign and flower boxes.")
    im=canvas(); tower(im)
    add("09-watchtower-workshop",im,"Secondary landmark with masonry, copper roof and attached timber volume.")
    im=canvas()
    stonewall(im,[(190,282),(259,300),(265,319),(184,301)],67)
    stonewall(im,[(410,302),(455,278),(508,280),(505,295),(421,321)],68)
    line(im,[(190,282),(259,300)],"stone3",2); line(im,[(410,302),(455,278),(508,280)],"stone3",2)
    # Simple timber footbridge. Rails occlude water; posts attach to land.
    poly(im,[(250,301),(400,297),(421,306),(264,312)],"wood0")
    for x in range(254,411,7):
        line(im,[(x,302),(x+8,308)],"wood3",2)
    for x,y in [(255,301),(301,300),(350,299),(402,298)]:
        rect(im,(x,y-13,x+3,y+12),"wood0")
        line(im,[(x+1,y-12),(x+1,y+9)],"wood4")
    line(im,[(255,289),(405,286)],"wood2",3)
    line(im,[(255,288),(405,285)],"wood4")
    add("10-quay-bridge",im,"Contact, overlap and grounded posts. Structural geometry remains static.")
    glints=[]
    for phase in range(7):
        im=canvas(); rng=random.Random(100)
        for i in range(46):
            yy=rng.randrange(245,296); xx=rng.randrange(279,399); length=rng.randint(2,11)
            if (i+phase)%7 < 3:
                line(im,[(xx+(phase%3),yy),(xx+length+(phase%3),yy)],"foam" if i%5==0 else "water2")
        glints.append(im)
    add("11-water-glints",glints,"Only sparse surface accents change; preserve reflection placement and water outline.",5)
    flags=[]
    for phase in range(10):
        im=canvas()
        for x,y,length in [(493,92,42),(112,111,26)]:
            line(im,[(x,y-26),(x,y+2)],"wood0",2)
            line(im,[(x-1,y-26),(x-1,y+1)],"stone3")
            top=[]; bottom=[]
            for j in range(length+1):
                wave=round(math.sin(j/7-phase*math.tau/10)*min(3,j/7))
                top.append((x+j,y-25+wave)); bottom.append((x+j,y-18+wave-round(j/length*2)))
            poly(im,top+list(reversed(bottom)),"roof4")
            line(im,top,"snow")
            line(im,[(a,b+4) for a,b in top],"roof1",2)
        flags.append(im)
    add("12-pennants",flags,"Pinned cloth root; shape changes across ten cels rather than translating a stiff flag.",7)
    im=canvas()
    for x,y,s,seed in [(-12,360,1.7,10),(645,365,1.75,20),(31,390,1.0,21)]:
        tree(im,x,y,s,seed,True)
    poly(im,[(0,333),(30,326),(62,338),(101,332),(156,343),(208,356),(230,360),(0,360)],"deep")
    poly(im,[(430,360),(478,344),(531,329),(571,341),(608,322),(640,333),(640,360)],"deep")
    rng=random.Random(25)
    for side in [range(0,205,6),range(460,640,6)]:
        for x in side:
            y=round(348+12*math.sin(x/53))+rng.randrange(-4,7); height=rng.randrange(4,12)
            line(im,[(x,y+7),(x+1,y-height)],"pine",2)
            line(im,[(x,y),(x-5,y-5)],"leaf0",2)
            line(im,[(x+1,y-3),(x+6,y-7)],"leaf0",2)
    add("13-foreground-foliage",im,"Dark framing masses with restrained highlights, not uniform noise.")
    im=canvas()
    for x,y in [(48,307),(72,309),(96,312)]:
        rect(im,(x,y-20,x+4,y+11),"wood0")
        line(im,[(x+1,y-19),(x+1,y+9)],"wood3")
    for dy in [-13,-3]:
        line(im,[(49,307+dy),(99,312+dy)],"wood1",4)
        line(im,[(49,306+dy),(99,311+dy)],"wood3")
    add("14-foreground-fence",im,"Near-plane occlusion and readable silhouettes.")
    (output/"scene.json").write_text(json.dumps(scene,indent=2)+"\n",encoding="utf-8")
    (output/"art-plan.json").write_text(json.dumps({"title":scene["name"],"origin":"Original code-authored sample; no reference pixels copied.",
        "contract":{"canvas":list(SIZE),"palette":C,"perspective":"fixed camera; shallow three-quarter architectural view",
                    "light":"upper-left warm daylight; shared cool shadows","alpha":"binary; transparent outside component", "pixel_scale":1},
        "components":plan,"quality_status":"Study demonstrating component workflow. Visual quality must be judged by a person, not test results."},indent=2)+"\n",encoding="utf-8")
    return output/"scene.json"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    try:
        print(build(args.out))
    except (OSError,ValueError) as exc:
        parser.exit(2,f"Error: {exc}\n")


if __name__=="__main__":
    main()
