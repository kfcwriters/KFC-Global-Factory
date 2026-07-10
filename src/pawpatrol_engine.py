"""
pawpatrol_engine.py — Professional Kids Cartoon Engine
Paw Patrol / Baby Bus style with:
★ 4 animated scenes: city, forest, beach, space
★ Hero dog character with walk/run/jump cycles
★ Speech bubbles synced to story
★ Particle effects: stars, confetti, bubbles
★ Animated title card + ending credits
★ Color cycling border + smooth transitions
★ 24 FPS professional quality
"""
import math, random, os, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FPS  = 24

FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

def font(size):
    for f in FONTS:
        if Path(f).exists():
            try: return ImageFont.truetype(f, size)
            except: pass
    return ImageFont.load_default()

def lerp(a,b,t): return a+(b-a)*t
def lerp_c(c1,c2,t): return tuple(int(lerp(c1[i],c2[i],t)) for i in range(3))
def ease_out(t): return 1-(1-t)**3

BORDER_COLORS = [
    [(255,100,50),(255,200,50),(100,200,255),(200,255,100)],
    [(255,50,150),(255,150,50),(50,200,255),(150,255,50)],
    [(200,50,255),(50,150,255),(50,255,150),(255,200,50)],
]


# ── Backgrounds ───────────────────────────────────────────────────────────────

def draw_city(draw, frame):
    t = frame/FPS
    for y in range(H):
        draw.line([(0,y),(W,y)], fill=lerp_c((100,180,255),(200,230,255),y/H))

    # Sun
    sx,sy = W-150,100
    for r in range(65,30,-6):
        draw.ellipse([sx-r,sy-r,sx+r,sy+r], fill=(255,230,80))
    draw.ellipse([sx-32,sy-32,sx+32,sy+32], fill=(255,245,50))
    for i in range(12):
        a = math.radians(i*30+t*25)
        draw.line([(sx+int(38*math.cos(a)),sy+int(38*math.sin(a))),
                   (sx+int(55*math.cos(a)),sy+int(55*math.sin(a)))],
                  fill=(255,200,0), width=4)

    # Clouds
    for cx0,cy,sp in [(0,80,.6),(400,130,.35),(800,65,.75)]:
        cx = int((cx0+t*sp*60)%(W+300))-150
        for ox,oy,r in [(0,0,50),(42,0,44),(-42,0,38),(18,-28,36),(-18,-28,32)]:
            draw.ellipse([cx+ox-r,cy+oy-r,cx+ox+r,cy+oy+r],fill=(255,255,255))

    # Road
    draw.rectangle([0,H-220,W,H], fill=(140,175,140))
    draw.rectangle([0,H-170,W,H-105], fill=(75,75,85))
    dash_off = int(t*120)%120
    for x in range(-120+dash_off, W+120, 120):
        draw.rectangle([x,H-140,x+60,H-134], fill=(255,255,100))

    # Buildings
    for bx,by2,bw,col in [
        (50,H-570,120,(100,120,180)),(180,H-430,115,(120,100,160)),
        (310,H-520,105,(90,110,170)),(430,H-490,135,(110,130,190)),
        (580,H-545,110,(100,115,175)),(700,H-445,130,(95,125,165)),
        (845,H-515,120,(115,105,180)),(975,H-475,145,(105,120,185)),
        (1130,H-535,130,(108,112,172)),
    ]:
        draw.rectangle([bx,by2,bx+bw,H-220], fill=col)
        draw.rectangle([bx+3,by2+3,bx+bw-3,H-220],
                       fill=lerp_c(col,(0,0,0),0.1))
        for wy in range(by2+12, H-245, 32):
            for wx in range(bx+8, bx+bw-8, 22):
                lit = (wx+wy+frame//8)%7 != 0
                draw.rectangle([wx,wy,wx+12,wy+20],
                               fill=(255,240,150) if lit else (40,50,80))
        draw.rectangle([bx,by2-6,bx+bw,by2], fill=lerp_c(col,(0,0,0),0.2))

    # Cars
    for cx0,lane,col,sp in [
        (0,H-158,(220,50,50),90),(350,H-158,(50,150,220),70),
        (750,H-123,(50,200,50),110),(150,H-123,(255,165,0),80),
    ]:
        cx = int((cx0+t*sp)%(W+200))-150
        draw.rounded_rectangle([cx,lane-22,cx+75,lane+8],radius=9,fill=col)
        draw.rounded_rectangle([cx+8,lane-40,cx+62,lane-18],radius=7,
                               fill=lerp_c(col,(255,255,255),0.3))
        for wx in [cx+10,cx+55]:
            draw.ellipse([wx-9,lane+5,wx+9,lane+18],fill=(30,30,30))
            draw.ellipse([wx-4,lane+8,wx+4,lane+15],fill=(180,180,180))


def draw_forest(draw, frame):
    t = frame/FPS
    for y in range(H):
        draw.line([(0,y),(W,y)],fill=lerp_c((160,210,160),(90,160,90),y/H))

    # Sun rays
    for i in range(16):
        a = math.radians(i*22+t*3)
        draw.line([(900,-50),(900+int(1100*math.cos(a)),-50+int(1100*math.sin(a)))],
                  fill=(255,240,100), width=18)

    for y in range(H-250, H):
        draw.line([(0,y),(W,y)],
                  fill=lerp_c((70,150,55),(35,90,25),(y-(H-250))/250))

    # Trees
    for i,(tx,ty,ht,col) in enumerate([
        (0,H-290,200,(25,110,25)),(180,H-310,250,(30,125,30)),
        (370,H-275,195,(35,120,35)),(580,H-305,235,(28,115,28)),
        (770,H-285,205,(32,118,32)),(1000,H-295,225,(26,122,26)),
        (1180,H-265,185,(38,112,38)),
    ]):
        sway = int(6*math.sin(t*0.7+i))
        draw.rectangle([tx-10+sway//2,ty,tx+10+sway//2,ty+ht//2],fill=(90,55,20))
        for layer in range(3):
            lr = 50-layer*10+int(4*math.sin(t*0.5+i+layer))
            ly = ty-layer*28+sway
            draw.ellipse([tx-lr+sway,ly-lr,tx+lr+sway,ly+lr],
                         fill=lerp_c(col,(15,70,15),layer*0.2))

    # Flowers
    for i in range(18):
        fx=(i*80+frame//3)%W; fy=H-195+(i%5)*28
        for p in range(5):
            pa=p*72+frame*2
            px=fx+int(9*math.cos(math.radians(pa)))
            py=fy+int(9*math.sin(math.radians(pa)))
            draw.ellipse([px-5,py-5,px+5,py+5],
                         fill=[(255,100,100),(255,200,50),(200,100,255),
                               (100,200,255),(255,150,50)][i%5])
        draw.ellipse([fx-4,fy-4,fx+4,fy+4],fill=(255,255,100))

    # Fireflies
    rng=random.Random(frame//6)
    for _ in range(25):
        fx=rng.randint(0,W); fy=rng.randint(H//3,H-200)
        if math.sin(frame*0.3+fx*0.01)>0.4:
            draw.ellipse([fx-4,fy-4,fx+4,fy+4],fill=(255,255,100))


def draw_beach(draw, frame):
    t=frame/FPS
    for y in range(H-270):
        draw.line([(0,y),(W,y)],fill=lerp_c((100,185,255),(200,230,255),y/(H-270)))

    sx,sy=180,100
    draw.ellipse([sx-48,sy-48,sx+48,sy+48],fill=(255,245,50))
    for i in range(12):
        a=math.radians(i*30+t*20)
        draw.line([(sx+int(53*math.cos(a)),sy+int(53*math.sin(a))),
                   (sx+int(72*math.cos(a)),sy+int(72*math.sin(a)))],
                  fill=(255,210,0),width=4)

    for y in range(H-270,H-270+110):
        draw.line([(0,y),(W,y)],fill=lerp_c((25,95,195),(95,195,235),(y-(H-270))/110))
    for i in range(8):
        wx=int((i*200+t*80)%(W+200))-100; wy=H-270+i*13
        pts=[(wx+x+640,wy+int(14*math.sin(math.radians(x*3+frame*8+i*45))))
             for x in range(-80,81,5)]
        if len(pts)>1: draw.line(pts,fill=(200,240,255),width=3)

    for y in range(H-165,H):
        draw.line([(0,y),(W,y)],fill=lerp_c((238,218,148),(198,178,108),(y-(H-165))/165))

    for i in range(3):
        cx=int((i*400+150+t*28*((-1)**i))%(W-100))+50; cy=H-158+i*18
        draw.ellipse([cx-18,cy-10,cx+18,cy+10],fill=(218,78,58))
        wc=int(8*math.sin(t*3+i))
        draw.ellipse([cx-32+wc,cy-6,cx-18+wc,cy+6],fill=(218,78,58))
        draw.ellipse([cx+18-wc,cy-6,cx+32-wc,cy+6],fill=(218,78,58))


def draw_space(draw, frame):
    t=frame/FPS
    for y in range(H):
        draw.line([(0,y),(W,y)],fill=lerp_c((5,0,20),(18,4,48),y/H))

    rng=random.Random(42)
    for _ in range(180):
        sx=rng.randint(0,W); sy=rng.randint(0,H)
        b=int(150+105*math.sin(frame*0.1+sx*0.05))
        sz=rng.randint(1,3)
        draw.ellipse([sx-sz,sy-sz,sx+sz,sy+sz],fill=(b,b,b))

    for px,py,pr,pc in [(900,200,88,(200,100,50)),(200,300,58,(100,180,100)),
                        (1100,400,48,(180,50,50))]:
        bob=int(10*math.sin(t*0.2+px))
        draw.ellipse([px-pr,py-pr+bob,px+pr,py+pr+bob],fill=lerp_c(pc,(0,0,0),0.5))
        draw.ellipse([px-pr+6,py-pr+bob,px+pr,py+pr+bob],fill=pc)

    rx=int((t*100)%(W+280))-140; ry=int(H//3+75*math.sin(t*0.5))
    for i in range(7):
        fx=rx-12-i*7; fy=ry+int(7*random.Random(frame+i).random()-3)
        fr=9-i; fc=[(255,200,50),(255,140,25),(200,50,10)][min(i//2,2)]
        draw.ellipse([fx-fr,fy-fr//2,fx+fr,fy+fr//2],fill=fc)
    draw.polygon([(rx+45,ry),(rx,ry-18),(rx,ry+18)],fill=(200,200,220))
    draw.ellipse([rx-18,ry-13,rx+18,ry+13],fill=(220,220,240))
    draw.ellipse([rx-7,ry-7,rx+7,ry+7],fill=(100,200,255))
    draw.polygon([(rx-18,ry+12),(rx-38,ry+32),(rx-18,ry+32)],fill=(200,50,50))
    draw.polygon([(rx-18,ry-12),(rx-38,ry-32),(rx-18,ry-32)],fill=(200,50,50))

SCENES = {"city":draw_city,"forest":draw_forest,"beach":draw_beach,"space":draw_space}


# ── Hero Dog Character ────────────────────────────────────────────────────────

def draw_dog(draw, cx, cy, frame, action="idle"):
    t      = frame/FPS
    bounce = int(8*abs(math.sin(t*3.5))) if action=="idle" else 0
    run_b  = int(12*abs(math.sin(t*8))) if action=="run" else 0
    cy    -= bounce + run_b
    col    = (255,180,80)
    ic     = lerp_c(col,(255,230,180),0.45)

    draw.ellipse([cx-48,cy+100,cx+48,cy+115],fill=(0,0,0,40))

    # Tail
    ta=math.radians(50+35*math.sin(t*4.5))
    for i in range(10):
        tf=i/10; ttx=cx+int(38*tf*math.cos(ta)); tty=cy+48-int(38*tf*math.sin(ta))
        r=8+int(tf*4)
        draw.ellipse([ttx-r,tty-r,ttx+r,tty+r],fill=lerp_c(col,(255,220,150),tf*0.5))

    # Body
    draw.ellipse([cx-43,cy+10,cx+43,cy+98],fill=col)
    draw.ellipse([cx-26,cy+25,cx+26,cy+92],fill=ic)

    # Badge
    draw.ellipse([cx-16,cy+30,cx+16,cy+56],fill=(50,150,255))
    draw.ellipse([cx-10,cy+36,cx+10,cy+50],fill=(30,100,200))
    draw.text((cx-8,cy+38),"★",font=font(16),fill=(255,215,0))

    # Collar
    draw.rectangle([cx-20,cy+6,cx+20,cy+19],fill=(200,50,50))
    draw.ellipse([cx-7,cy+9,cx+7,cy+17],fill=(255,215,0))

    # Head
    ht=int(5*math.sin(t*1.5))
    draw.ellipse([cx-50,cy-88+ht,cx+50,cy+12+ht],fill=col)
    draw.ellipse([cx-25,cy-28+ht,cx+25,cy+16+ht],fill=ic)

    # Nose
    draw.ellipse([cx-9,cy-30+ht,cx+9,cy-16+ht],fill=(40,20,10))
    draw.ellipse([cx-4,cy-28+ht,cx-1,cy-22+ht],fill=(70,40,30))

    # Eyes
    blink=frame%70 in range(0,3)
    for ex,ey in [(-23,-53),(23,-53)]:
        if not blink:
            draw.ellipse([cx+ex-14,cy+ey+ht,cx+ex+14,cy+ey+19+ht],fill=(255,255,255))
            draw.ellipse([cx+ex-9,cy+ey+4+ht,cx+ex+9,cy+ey+14+ht],fill=(80,50,200))
            draw.ellipse([cx+ex-6,cy+ey+6+ht,cx+ex+6,cy+ey+12+ht],fill=(20,10,30))
            draw.ellipse([cx+ex-4,cy+ey+7+ht,cx+ex-1,cy+ey+10+ht],fill=(255,255,255))
        else:
            draw.arc([cx+ex-14,cy+ey+ht,cx+ex+14,cy+ey+19+ht],0,180,fill=(30,20,10),width=3)

    # Ears
    ef=int(10*math.sin(t*2))
    for ex2,s in [(-38,-1),(38,1)]:
        draw.ellipse([cx+ex2-16,cy-78+ef*s+ht,cx+ex2+16,cy-28+ef*s+ht],
                     fill=lerp_c(col,(170,90,20),0.3))

    # Mouth
    if action in ("happy","run"):
        draw.arc([cx-18,cy-18+ht,cx+18,cy+ht],0,180,fill=(40,20,10),width=3)
        draw.ellipse([cx-8,cy-6+ht,cx+8,cy+8+ht],fill=(255,100,120))
    else:
        draw.arc([cx-11,cy-16+ht,cx+11,cy-2+ht],0,180,fill=(40,20,10),width=3)

    # Helmet
    draw.ellipse([cx-43,cy-93+ht,cx+43,cy-63+ht],fill=(50,150,255))
    draw.ellipse([cx-38,cy-90+ht,cx+38,cy-68+ht],fill=(80,180,255))
    draw.text((cx-17,cy-86+ht),"PAW",font=font(13),fill=(255,255,255))

    # Legs
    for i,(lx,_) in enumerate([(-26,-1),(26,1)]):
        if action=="run":
            phase=math.sin(t*8+i*math.pi)
            ly2=cy+150+int(14*phase); lx2=lx+int(18*phase)
        else:
            ly2=cy+150; lx2=lx
        draw.line([(cx+lx,cy+93),(cx+lx2,ly2)],fill=col,width=20)
        draw.ellipse([cx+lx2-14,ly2-8,cx+lx2+14,ly2+10],fill=ic)

    # Arms
    for i,(ax,_) in enumerate([(-42,-1),(42,1)]):
        ay=int(8*math.sin(t*2+i)) if action=="idle" else int(18*math.sin(t*8+i*math.pi+math.pi/2))
        draw.ellipse([cx+ax-14,cy+14+ay,cx+ax+14,cy+62+ay],fill=col)
        draw.ellipse([cx+ax-12,cy+56+ay,cx+ax+12,cy+76+ay],fill=ic)


# ── Speech Bubble ─────────────────────────────────────────────────────────────

def draw_bubble(draw, text, bx, by, frame):
    fnt  = font(30 if len(text)<45 else 24)
    words= text.split(); lines=[]; line=""
    for w in words:
        test=line+(" " if line else "")+w
        bb=draw.textbbox((0,0),test,font=fnt)
        if bb[2]>480: lines.append(line); line=w
        else: line=test
    if line: lines.append(line)
    lines=lines[:3]
    lh=38; bw=max((draw.textbbox((0,0),l,font=fnt)[2] for l in lines),default=100)+44
    bh=len(lines)*lh+28
    bx=max(18,min(bx,W-bw-18)); by=max(18,min(by,H-bh-55))
    draw.rounded_rectangle([bx,by,bx+bw,by+bh],radius=16,fill=(255,255,255),
                           outline=(50,100,220),width=4)
    tx=bx+60
    draw.polygon([(tx,by+bh),(tx-14,by+bh+32),(tx+18,by+bh)],fill=(255,255,255))
    draw.line([(tx,by+bh),(tx-14,by+bh+32)],fill=(50,100,220),width=4)
    draw.line([(tx+18,by+bh),(tx-14,by+bh+32)],fill=(50,100,220),width=4)
    for i,ln in enumerate(lines):
        bb=draw.textbbox((0,0),ln,font=fnt)
        tx2=bx+(bw-bb[2])//2
        draw.text((tx2+2,by+16+i*lh+2),ln,font=fnt,fill=(0,0,0,80))
        draw.text((tx2,by+16+i*lh),ln,font=fnt,fill=(30,30,100))


# ── Particles ─────────────────────────────────────────────────────────────────

def draw_particles(draw, frame, ptype="stars"):
    rng=random.Random(frame//5)
    if ptype=="stars":
        for _ in range(20):
            px=rng.randint(50,W-50); py=rng.randint(50,int(H*0.65))
            if math.sin(frame*0.15+px*0.01)>0.35:
                sz=rng.randint(4,9)
                col=rng.choice([(255,255,0),(255,200,50),(200,255,100),(100,200,255)])
                draw.polygon([(px,py-sz),(px+2,py-2),(px+sz,py),(px+2,py+2),
                              (px,py+sz),(px-2,py+2),(px-sz,py),(px-2,py-2)],fill=col)
    elif ptype=="confetti":
        cols=[(255,100,100),(100,200,255),(255,215,0),(100,255,100),(255,100,255)]
        rng2=random.Random(42)
        for i in range(35):
            x0=rng2.randint(0,W); sp=rng2.uniform(1.5,3.5)
            y0=int((frame*sp+i*55)%(H+50))-25
            cx2=x0+int(18*math.sin(frame*0.05+i))
            col=cols[i%len(cols)]; sz=rng2.randint(6,12); rot=frame*0.1+i
            pts=[(cx2+int(sz*math.cos(rot+j*1.57)),y0+int(sz*math.sin(rot+j*1.57)))
                 for j in range(4)]
            draw.polygon(pts,fill=col)
    elif ptype=="bubbles":
        for i in range(12):
            bx=rng.randint(30,W-30); sp=rng.uniform(0.8,2.2)
            by=H-int((frame*sp+i*75)%(H+90))
            r=rng.randint(10,25); wobble=int(7*math.sin(frame*0.07+i)); bx2=bx+wobble
            if 0<by<H:
                draw.ellipse([bx2-r,by-r,bx2+r,by+r],fill=(200,240,255))
                draw.ellipse([bx2-r,by-r,bx2+r,by+r],outline=(150,200,255),width=2)
                draw.ellipse([bx2-r//3,by-r//2,bx2,by-r//4],fill=(255,255,255))


# ── Title Card ────────────────────────────────────────────────────────────────

def draw_title(draw, title, subtitle, frame):
    t=frame/FPS; tf=min(1.0,t/1.2); yo=int((1-ease_out(tf))*(-H))
    c1,c2=(255,100,50),(255,200,50)
    for y in range(H):
        draw.line([(0,y+yo),(W,y+yo)],fill=lerp_c(c1,c2,y/H))
    for i in range(20):
        sx=int(W*i/20); sy=int(H*0.3+H*0.4*(i%3)/2)+yo
        if math.sin(t*3+i)>0:
            draw.text((sx,sy),"★",font=font(22),fill=(255,255,200))
    f1=font(68); bb=draw.textbbox((0,0),title,font=f1)
    tx=(W-bb[2])//2; ty=H//2-55+yo
    for s in range(5,0,-1):
        draw.text((tx+s,ty+s),title,font=f1,fill=(0,0,0,40))
    draw.text((tx,ty),title,font=f1,fill=(255,255,255))
    if subtitle:
        f2=font(36); bb2=draw.textbbox((0,0),subtitle,font=f2)
        draw.text(((W-bb2[2])//2,ty+82),subtitle,font=f2,fill=(255,240,200))


def draw_ending(draw, frame):
    t=frame/FPS
    import colorsys
    for y in range(H):
        h2=(y/H+t*0.08)%1.0; r2,g2,b2=colorsys.hsv_to_rgb(h2,0.7,0.9)
        draw.line([(0,y),(W,y)],fill=(int(r2*255),int(g2*255),int(b2*255)))
    for i in range(28):
        sx=int(W*i/28+25*math.sin(t+i)); sy=int(H*0.5+130*math.sin(t*0.7+i*0.5))
        sz=14+int(7*math.sin(t*2+i))
        draw.text((sx,sy),"★",font=font(sz),fill=(255,255,255))
    f3=font(76); msg="THE END! 🌟"
    bb=draw.textbbox((0,0),msg,font=f3); tx=(W-bb[2])//2; ty=H//2-55
    for s in range(6,0,-1): draw.text((tx+s,ty+s),msg,font=f3,fill=(0,0,0,50))
    draw.text((tx,ty),msg,font=f3,fill=(255,255,255))
    f4=font(34); sub="Subscribe for more fun! 🐾"
    bb2=draw.textbbox((0,0),sub,font=f4)
    draw.text(((W-bb2[2])//2,ty+95),sub,font=f4,fill=(255,240,200))


# ── Animated Border ───────────────────────────────────────────────────────────

def draw_border(draw, frame, palette_idx=0):
    cols=BORDER_COLORS[palette_idx%len(BORDER_COLORS)]
    n=len(cols)
    for i in range(12):
        t=(frame*0.05+i*0.3)%n; i1=int(t)%n; i2=(i1+1)%n
        col=lerp_c(cols[i1],cols[i2],t-int(t))
        draw.rectangle([i,i,W-i,H-i],outline=col,width=1)
    for cx2,cy2 in [(22,22),(W-22,22),(22,H-22),(W-22,H-22)]:
        a=frame*0.05
        for j in range(5):
            a1=a+j*(2*math.pi/5); a2=a+j*(2*math.pi/5)+math.pi/5
            draw.polygon([(cx2,cy2),(cx2+int(16*math.cos(a1)),cy2+int(16*math.sin(a1))),
                          (cx2+int(7*math.cos(a2)),cy2+int(7*math.sin(a2)))],
                         fill=cols[j%n])


# ── Main Renderer ─────────────────────────────────────────────────────────────

def create_cartoon_video(script, audio_path, output_path, content_type):
    scene_map={"bedtime_story":"forest","nursery_rhyme":"beach",
               "educational":"city","fairy_tale":"space"}
    scene=scene_map.get(content_type,"forest"); bg_fn=SCENES[scene]
    palette_idx=list(SCENES.keys()).index(scene)

    dur=_probe_duration(audio_path); total=int(dur*FPS)
    TITLE_F=int(3*FPS); END_F=int(3*FPS)
    story_f=max(1,total-TITLE_F-END_F)
    spl=max(1,story_f//max(len(script),1))

    print(f"  [cartoon] {content_type} | {scene} scene | {total}f@{FPS}fps")
    print(f"  [cartoon] {len(script)} lines × {spl/FPS:.1f}s each")

    ptypes=["stars","confetti","bubbles"]

    with tempfile.TemporaryDirectory(prefix="cf_") as fdir:
        fdir=Path(fdir)
        for frame in range(total):
            img=Image.new("RGB",(W,H),(100,150,200))
            draw=ImageDraw.Draw(img)

            if frame<TITLE_F:
                title=content_type.replace("_"," ").title()
                draw_title(draw,title,"A Fun Story for Kids!",frame)
            elif frame>=total-END_F:
                draw_ending(draw,frame-(total-END_F))
            else:
                sf=frame-TITLE_F; li=min(sf//spl,len(script)-1)
                bg_fn(draw,frame)

                # Particles
                pt=ptypes[(frame//(FPS*7))%3]
                draw_particles(draw,frame,pt)

                # Character action
                lf=sf-li*spl
                action="run" if lf<int(FPS*0.4) else ("happy" if li%3==0 else "idle")
                char_x=210+int(55*math.sin(sf*0.03))
                draw_dog(draw,char_x,H-230,frame,action)

                # Speech bubble
                if lf>FPS//2 and li<len(script):
                    draw_bubble(draw,script[li],char_x+85,H-430,lf)

                draw_border(draw,frame,palette_idx)

            img.save(str(fdir/f"f{frame:06d}.jpg"),quality=85,optimize=True)
            if frame%(FPS*4)==0:
                print(f"  [cartoon] {frame}/{total} ({int(frame/total*100)}%)")

        print("  [cartoon] Assembling video ...")
        r=subprocess.run([
            "ffmpeg","-y","-framerate",str(FPS),"-i",str(fdir/"f%06d.jpg"),
            "-i",audio_path,"-c:v","libx264","-preset","fast","-crf","24",
            "-c:a","aac","-b:a","128k","-shortest","-pix_fmt","yuv420p",
            "-movflags","+faststart",output_path
        ],capture_output=True,text=True)
        if r.returncode!=0: raise RuntimeError(f"FFmpeg: {r.stderr[-400:]}")

    sz=os.path.getsize(output_path)//1024
    print(f"  [cartoon] Done! {sz}KB ✓")
    return output_path


def get_thumbnail_frame(content_type="bedtime_story"):
    img=Image.new("RGB",(W,H)); draw=ImageDraw.Draw(img)
    draw_forest(draw,30); draw_dog(draw,220,H-230,30,"happy")
    draw_border(draw,30,1)
    return img


def _probe_duration(path):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                      "-of","default=noprint_wrappers=1:nokey=1",path],
                     capture_output=True,text=True)
    return float(r.stdout.strip() or 60)
