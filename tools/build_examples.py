"""Rebuild original, editable starter scenes. No downloads or external assets."""
import json
from pathlib import Path
import random

DEST = Path(__file__).resolve().parents[1] / "skills" / "animated-pixel-art-studio" / "assets"
PAL = {"0":"#111827", "1":"#1e293b", "2":"#334155", "3":"#475569",
       "4":"#64748b", "5":"#94a3b8", "6":"#cbd5e1", "7":"#f8e8c8",
       "8":"#eab676", "9":"#bc7855", "a":"#794b47", "b":"#483c46",
       "c":"#2e5959", "d":"#4c8c78", "e":"#91bd91", "f":"#e38b66"}


def base(name, size=(160,90), frames=48):
    return {"version":1,"name":name,"canvas":list(size),"fps":12,"frames":frames,
            "scale":6,"loop":True,"palette":PAL.copy(),"background":"0","sprites":{},"layers":[]}


def rect(s,x,y,w,h,c,name=""):
    s["layers"].append({"name":name,"rect":[w,h],"color":c,"x":x,"y":y})


def sprite(s,name,rows):
    s["sprites"][name]={"rows":rows}


def actor(s,name,x,y,animation=None,ticks=1,motion=None):
    layer={"name":name,"x":x,"y":y}
    if animation:
        layer.update(animation=animation,frame_ticks=ticks)
    else:
        layer["sprite"]=name
    if motion:
        layer["motion"]=motion
    s["layers"].append(layer)


def cafe():
    s=base("After Hours / Rainy Cafe")
    rect(s,0,0,160,90,"1")
    # Distant skyline and warm windows, restrained clusters rather than noise.
    for x,y,w in [(2,23,17),(23,12,19),(47,27,15),(68,17,22),(97,9,17),(121,25,25),(150,18,10)]:
        rect(s,x,y,w,65-y,"2")
        rect(s,x+2,y+2,w-4,1,"3")
        for wx in range(x+4,x+w-2,6):
            for wy in range(y+6,61,9):
                rect(s,wx,wy,2,3,"9" if (wx+wy)%3 else "4")
    rect(s,0,65,160,25,"0")
    for x,y,w in [(3,70,31),(110,73,24),(9,80,18),(122,84,32),(101,68,22)]:
        rect(s,x,y,w,1,"3")
    # Cafe architecture, stepped roof, wood trim, glowing interior.
    rect(s,34,31,78,42,"0")
    rect(s,37,34,72,37,"a")
    rect(s,41,38,64,29,"8")
    rect(s,43,40,60,25,"9")
    rect(s,43,40,60,2,"7")
    rect(s,43,51,60,1,"a")
    rect(s,47,45,19,2,"a")
    for x in [49,55,61]:
        rect(s,x,42,3,3,"b")
    rect(s,41,59,64,6,"b")
    rect(s,41,58,64,2,"7")
    for x in [41,70,102]:
        rect(s,x,38,3,29,"a")
        rect(s,x,38,1,29,"8")
    rect(s,32,30,82,3,"8")
    rect(s,29,33,88,5,"c")
    for x in range(29,117,8):
        rect(s,x,33,4,5,"e")
    rect(s,30,38,86,2,"0")
    rect(s,38,68,70,4,"b")
    rect(s,33,72,80,2,"3")
    rect(s,29,75,88,2,"2")
    # Cafe plaque: pixel coffee cup icon.
    rect(s,62,17,27,12,"0")
    rect(s,63,18,25,10,"8")
    rect(s,64,19,23,8,"a")
    sprite(s,"cup",["77777..","777777.","7777.7.","777777.",".777...","777777."])
    actor(s,"cup",72,20)
    # Lamp and foreground shrub.
    rect(s,131,29,2,43,"3")
    rect(s,128,27,8,2,"4")
    rect(s,129,29,6,5,"8")
    rect(s,130,29,4,3,"7")
    rect(s,127,72,10,2,"2")
    for x,y,w,h in [(18,57,5,13),(13,62,5,7),(23,61,6,7),(16,54,4,7),(24,56,3,9)]:
        rect(s,x,y,w,h,"c")
        rect(s,x,y,1,h-2,"d")
    rect(s,14,69,13,3,"9")
    rect(s,16,72,9,7,"a")
    # Cat rests on the counter; blink and tail are independent of rainfall.
    cat=[".a...a......",".aa.aa......",".a888a......",".85858a.....","..888888aa..","...8888888a.","...9999999a.","..aaaaaaaa.."]
    blink=cat.copy();blink[3]=".8a8a8a....."
    sprite(s,"cat-open",cat);sprite(s,"cat-blink",blink)
    actor(s,"counter cat",81,50,["cat-open"]*10+["cat-blink","cat-open"],4)
    sprite(s,"steam-a",["..5..",".5...","..5..","...5.","..5.."])
    sprite(s,"steam-b",[".5...","..5..","...5.","..5..",".5..."])
    actor(s,"warm cup steam",56,51,["steam-a","steam-b"],6)
    rect(s,56,56,4,2,"7")
    # Rain moves by one pixel per tick and wraps offscreen over a 24-frame period.
    sprite(s,"rain",[".4","4.","4."])
    for x in range(-12,181,12):
        for y in range(-24,97,24):
            actor(s,"rain",x,y,motion={"period":24,"keys":[[0,x,y],[24,x-12,y+24]]})
    # Reflections pulse in small controlled patches.
    sprite(s,"reflect-a",["...8888888.....",".99999999999...","....aaaaaa....."])
    sprite(s,"reflect-b",["..88888888.....","....99999999...","..aaaaaa......."])
    actor(s,"window reflections",61,81,["reflect-a","reflect-b"],6)
    return s


def campfire():
    s=base("Midnight / Campfire")
    rect(s,0,43,160,47,"1")
    rng=random.Random(71)
    for _ in range(42):
        rect(s,rng.randrange(160),rng.randrange(3,40),1,1,"4")
    sprite(s,"moon",["..7777..",".777777.","77777777","77777777","77777777",".777777.","..7777.."])
    actor(s,"moon",121,10)
    # Layered pines with consistent stepped silhouettes.
    for x,y,size,c in [(5,22,4,"2"),(28,33,3,"2"),(136,29,4,"2"),(113,38,3,"2"),(-9,40,5,"0"),(144,41,5,"0")]:
        for k in range(5):
            rect(s,x-k*size//2,y+k*5,2+k*size,5,c)
        rect(s,x,y+25,2,9,c)
    rect(s,0,72,160,18,"c")
    rect(s,0,76,160,14,"1")
    # Tent with stepped diagonal edge, opening, rope and stakes.
    for y in range(23):
        rect(s,40-y//2,47+y,y+2,1,"9")
        rect(s,42,47+y,max(1,y//2),1,"8")
    for y in range(16):
        rect(s,41-y//3,54+y,1+y//3,1,"a")
    rect(s,25,70,38,2,"0")
    rect(s,66,76,37,2,"a")
    rect(s,70,74,29,2,"9")
    rect(s,75,73,21,2,"8")
    for x,y in [(73,71),(78,73),(87,73),(94,71)]:
        rect(s,x,y,4,2,"3")
    rect(s,78,69,15,2,"a")
    rect(s,80,68,11,2,"9")
    flames=[
      [".....f.....",".....f.....","....ff.....","...f8f.....","...f88f....","..f878ff...","..f8778f...",".ff87788f..",".f887788f..","..fffffff.."],
      ["...........","....f......","....ff.....","....f8f....","...ff8f....","..ff88f....","..f8778ff..","..f87788f..",".ff88788f..","..fffffff.."],
      ["......f....",".....ff....",".....f8f...","....ff8f...","....f88f...","...f878f...","..ff8778f..","..f88778f..","..f88788ff.","...ffffff.."],
      ["...........","......f....",".....ff....","....f8f....","...ff8f....","...f88ff...","..ff778f...","..f87788f..",".ff88788f..","..fffffff.."]]
    for i,rows in enumerate(flames):sprite(s,f"flame-{i}",rows)
    actor(s,"fire",78,58,[f"flame-{i}" for i in (0,1,2,3,1,2)],2)
    sprite(s,"ember",["8"])
    for j in range(3):
        actor(s,"ember",82+j*3,57,motion={"period":24,"keys":[[0,82+j*3,57],[12,79+j*3,49],[24,83+j*3,41]]})
    # Small sitting traveler, scarf and a mug.
    sprite(s,"traveler",["..3333...",".333333..",".388883..","..8888...","...aa....","..dddd...",".dddddd..",".dddddd..","..2222...",".222222..","000..000."])
    actor(s,"traveler",104,60)
    rect(s,101,65,3,3,"7")
    return s


def walker():
    s=base("Little Explorer / Walk Cycle",(96,64),48)
    s["background"]="c"
    rect(s,0,0,96,38,"c")
    for x,y in [(7,13),(31,8),(66,17),(84,6)]:
        rect(s,x,y,10,2,"d");rect(s,x+3,y-2,12,2,"d")
    rect(s,0,39,96,25,"1")
    rect(s,0,39,96,2,"e")
    for x in range(1,96,9):rect(s,x,45+(x%3)*3,3,1,"2")
    head=["....00000.......","...0333330......","...0388880......","...0380850......","....088880......",".....0880......."]
    bodies=[
      ["...0dddd00......","..0ddddd080.....","..0ddddd0.......","...022220.......","...022.220......","..022...220.....","..000...000....."],
      ["....0ddd0.......","...0ddddd0......","...0ddddd080....","....02220.......","....02220.......","....02220.......","....00000......."],
      ["...0dddd00......","..0ddddd080.....","..0ddddd0.......","...022220.......","..022..220......","..022...220.....","..000...000....."],
      ["....0ddd0.......","...0ddddd0......","...0ddddd080....","....02220.......","....02220.......","....02220.......","....00000......."]]
    for i,body in enumerate(bodies):sprite(s,f"walk-{i}",head+body)
    rect(s,40,39,17,2,"0")
    actor(s,"walk in place",40,26,["walk-0","walk-1","walk-2","walk-3"],3)
    return s


def blank():
    s=base("Untitled",(96,64),24)
    sprite(s,"dot",["777","787","777"])
    actor(s,"dot",8,30,motion={"keys":[[0,8,30],[12,84,30],[24,8,30]]})
    return s


if __name__ == "__main__":
    DEST.mkdir(parents=True,exist_ok=True)
    for name,builder in [("rainy-cafe",cafe),("campfire",campfire),("walk-cycle",walker),("blank",blank)]:
        (DEST/f"{name}.json").write_text(json.dumps(builder(),indent=2)+"\n",encoding="utf-8")
        print(name)
