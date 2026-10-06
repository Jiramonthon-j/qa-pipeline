from PIL import Image, ImageDraw, ImageFont
import sys
F='/sessions/focused-awesome-euler/.fonts/'
S=2
def font(sz,bold=False): return ImageFont.truetype(F+('Waree-Bold.ttf' if bold else 'Waree.ttf'), int(sz*S), layout_engine=ImageFont.Layout.RAQM)
C=dict(bg='#f5f8f7',text='#182320',dim='#55655f',border='#d6e0db',auto='#0f766e',autos='#e6f4f1',gate='#b45309',gates='#fdf0dc',good='#15803d',goods='#dcf3e4',loop='#6d28d9',loops='#efe9fc',white='#ffffff',chip='#eef1f0')
PH={'A':'#0f766e','B':'#1d4ed8','C':'#334155','D':'#6d28d9'}
T={
'en':dict(title='QA Pipeline',sub='15 AI-agent skills that take one feature from requirements to closed bugs',
 ph={'A':('PHASE A','Analyse requirements'),'B':('PHASE B','Prepare & execute'),'C':('PHASE C','Report & decide'),'D':('PHASE D','Close defects (loop)')},
 st={'00-pre':'Collect requirements from all sources','00':'Scope, exit criteria, schedule','01':'Extract business rules','02':'Design end-to-end user flows','03':'Generate test cases','04':'Check coverage gaps','05':'Prioritise P0 – P3','06':'Build concrete mock test data','06a':'Run tests, save evidence','07':'Results & root-cause analysis','07a':'Rebuild traceability matrix','08':'Go / No-Go report','09':'Open ticket, notify dev','10':'Retest after the fix','10a':'Close or comment'},
 dec='Any failed cases?',yes='Yes',no='No',done='Feature closed',loop='failures remain',allp='all pass',
 lg=('Automatic','Human sign-off required','Tool used'),gate='SIGN-OFF'),
'th':dict(title='QA Pipeline',sub='15 Skill ที่พาฟีเจอร์หนึ่งตั้งแต่รวบรวม Requirement จนปิดบั๊ก',
 ph={'A':('PHASE A','วิเคราะห์ Requirement'),'B':('PHASE B','เตรียมข้อมูลและรันทดสอบ'),'C':('PHASE C','สรุปผลและตัดสินใจ'),'D':('PHASE D','ปิดบั๊ก (วนซ้ำ)')},
 st={'00-pre':'รวบรวม Requirement จากทุกแหล่ง','00':'ขอบเขต เกณฑ์ผ่าน ตารางเวลา','01':'สกัด Business Rule','02':'ออกแบบ User Flow','03':'สร้าง Test Case','04':'ตรวจความครบถ้วน','05':'จัดลำดับความสำคัญ P0 – P3','06':'สร้างข้อมูลทดสอบ','06a':'รันเทส เก็บหลักฐาน','07':'สรุปผลและหาสาเหตุ','07a':'คำนวณ Traceability Matrix ใหม่','08':'รายงาน Go / No-Go','09':'เปิด Ticket แจ้ง Dev','10':'Retest หลัง Dev แก้','10a':'ปิด/คอมเมนต์ Ticket'},
 dec='มีเคส Fail ค้างไหม?',yes='มี',no='ไม่มี',done='ปิด Feature ได้',loop='ยังมี Fail',allp='ผ่านครบ',
 lg=('อัตโนมัติ','ต้องให้คนอนุมัติ/ลงนาม','เครื่องมือที่ใช้'),gate='อนุมัติ')}
NAME={'00-pre':'source-ingest','00':'test-plan','01':'requirement-review','02':'e2e-flow-designer','03':'test-case-generator','04':'coverage-review','05':'risk-analysis','06':'test-data-generator','06a':'qa-automation-script','07':'result-analysis','07a':'RTM qa-reconcile','08':'qa-report-generator','09':'redmine-logging','10':'qa-retest','10a':'qa-retest-closure'}
TOOL={'03':'Excel','06a':'Playwright','07a':'Excel','08':'Word','09':'Redmine','10':'Playwright','10a':'Redmine'}
GATES={'00-pre','00','08'}
lang=sys.argv[1]; L=T[lang]
W,H=1640,900
im=Image.new('RGB',(W*S,H*S),C['bg']); d=ImageDraw.Draw(im)
def P(*a): return [int(v*S) for v in a]
def rr(x,y,w,h,r,fill,outline=None,width=1): d.rounded_rectangle(P(x,y,x+w,y+h),radius=r*S,fill=fill,outline=outline,width=int(width*S))
def tx(x,y,s,sz,col,bold=False,anchor='la'): d.text(P(x,y),s,font=font(sz,bold),fill=col,anchor=anchor)
def tw(s,sz,bold=False): return d.textlength(s,font=font(sz,bold))/S
def arrow(pts,col,width=2.2,head=9):
    d.line([tuple(P(*p)) for p in pts],fill=col,width=int(width*S),joint='curve')
    (x1,y1),(x2,y2)=pts[-2],pts[-1]
    import math; a=math.atan2(y2-y1,x2-x1)
    p1=(x2-head*math.cos(a)+head*0.55*math.sin(a), y2-head*math.sin(a)-head*0.55*math.cos(a))
    p2=(x2-head*math.cos(a)-head*0.55*math.sin(a), y2-head*math.sin(a)+head*0.55*math.cos(a))
    d.polygon([tuple(P(x2,y2)),tuple(P(*p1)),tuple(P(*p2))],fill=col)
# header
tx(40,34,L['title'],30,C['text'],True); tx(40+tw(L['title'],30,True)+14,46,L['sub'],16,C['dim'])
# legend
lx=W-40
items=[(L['lg'][2],'chip'),(L['lg'][1],'gate'),(L['lg'][0],'auto')]
for lab,k in items:
    w=tw(lab,13)
    lx-=w; tx(lx,46,lab,13,C['dim'])
    lx-=26
    if k=='chip': rr(lx,45,20,16,8,C['chip'],C['border'])
    else: rr(lx,44,20,18,5,C[k+'s'],C[k],1.6)
    lx-=22
# cards
CX={'A':40,'B':440,'C':840,'D':1240}; CW=360; CY=104; CH=H-104-36
BH=74; G=10
def card(k):
    x=CX[k]; rr(x,CY,CW,CH,16,C['white'],C['border'],1.2)
    rr(x,CY,CW,8,4,PH[k]); d.rectangle(P(x,CY+4,x+CW,CY+8),fill=PH[k])
    tx(x+20,CY+24,L['ph'][k][0],12,PH[k],True); tx(x+20,CY+42,L['ph'][k][1],18,C['text'],True)
def stage(k,sid,y,wcut=0):
    x=CX[k]+18; w=CW-36-wcut
    g=sid in GATES; col=C['gate'] if g else C['auto']; fill=C['gates'] if g else C['autos']
    rr(x,y,w,BH,10,fill,col,1.6)
    bw=max(tw(sid,13,True)+18,44); rr(x+12,y+12,bw,22,11,col); tx(x+12+bw/2,y+23,sid,13,C['white'],True,'mm')
    tx(x+12+bw+10,y+13,NAME[sid],14.5,C['text'],True)
    tx(x+14,y+44,L['st'][sid],13,C['dim'])
    chips=[]
    if g: chips.append((L['gate'],C['gate'],C['gate'],C['white']))
    if sid in TOOL: chips.append((TOOL[sid],C['chip'],C['border'],C['dim']))
    # place chips on bottom-right row (y+44 line) ; ensure no overlap with description
    right=x+w-10
    need=sum(tw(c[0],11,True)+22 for c in chips)
    descend=x+14+tw(L['st'][sid],13)
    namend=x+12+bw+10+tw(NAME[sid],14.5,True)
    rowy = y+43 if descend+8 < right-need else y+12
    if rowy==y+12 and namend+8 > right-need: print('WARN overlap',sid)
    for t,f,o,tc in chips:
        cw=tw(t,11,True)+16; rr(right-cw,rowy,cw,20,10,f,o); tx(right-cw/2,rowy+10,t,11,tc,True,'mm'); right-=cw+6
    return (x,y,w,BH)
for k in 'ABCD': card(k)
y0=CY+80
def column(k,ids,gap=G):
    boxes=[];y=y0
    for i,s in enumerate(ids):
        b=stage(k,s,y); boxes.append(b)
        if i: arrow([(CX[k]+CW/2,y-gap+1),(CX[k]+CW/2,y-1)],C['dim'],1.8,7)
        y+=BH+gap
    return boxes
A=column('A',['00-pre','00','01','02','03','04','05'])
B=column('B',['06','06a','07','07a'],G+22)
Cb=column('C',['08'])
# inter-phase arrows (header level)
for a,b in [('A','B'),('B','C')]:
    yy=CY+40; arrow([(CX[a]+CW+6,yy),(CX[b]-6,yy)],C['dim'],2.4,10)
# also connect A last -> B first via note: arrow at header is enough
# decision diamond in C
cx=CX['C']+CW/2; dy=Cb[0][1]+BH+70; dw,dh=210,92
d.polygon([tuple(P(cx,dy-dh/2)),tuple(P(cx+dw/2,dy)),tuple(P(cx,dy+dh/2)),tuple(P(cx-dw/2,dy))],fill=C['white'],outline=C['text'],width=int(1.8*S))
tx(cx,dy,L['dec'],13,C['text'],True,'mm')
arrow([(cx,Cb[0][1]+BH),(cx,dy-dh/2-1)],C['dim'],1.8,7)
# done pill
doy=CY+CH-90; dw2=220
rr(cx-dw2/2,doy,dw2,52,26,C['goods'],C['good'],2); tx(cx,doy+26,'✓  '+L['done'] if False else L['done'],17,C['good'],True,'mm')
arrow([(cx,dy+dh/2),(cx,doy-1)],C['good'],2.2,9); tx(cx+10,dy+dh/2+(doy-dy-dh/2)/2,L['no'],14,C['good'],True,'lm')
# D column with spacing
D=[]; ys=[y0, (y0+doy-5)/2, doy-5]
for i,s in enumerate(['09','10','10a']):
    D.append(stage('D',s,ys[i],34))
    if i: arrow([(CX['D']+CW/2-40,ys[i-1]+BH),(CX['D']+CW/2-40,ys[i]-1)],C['dim'],1.8,7)
# yes arrow: diamond right -> 09
yx=cx+dw/2; ty=D[0][1]+BH/2
arrow([(yx,dy),(CX['C']+CW+30,dy),(CX['C']+CW+30,ty),(D[0][0]-1,ty)],C['gate'],2.2,9)
tx(CX['C']+CW+12,dy-22,L['yes'],14,C['gate'],True,'mm')
# loop arrow on right: 10a -> 09
rx=CX['D']+CW-26
lx2=D[0][0]+D[0][2]
arrow([(lx2,D[2][1]+BH/2+10),(rx,D[2][1]+BH/2+10),(rx,D[0][1]+BH/2+8),(lx2+1,D[0][1]+BH/2+8)],C['loop'],2.2,9)
mid=(D[1][1]+BH+D[2][1])/2
lab=L['loop']; lw=tw(lab,13,True)+14
rr(rx-lw-6,mid-12,lw,24,12,C['loops'],C['loop'],1.2); tx(rx-6-lw/2,mid,lab,13,C['loop'],True,'mm')
# all pass: 10a left -> done
arrow([(D[2][0],doy+26),(cx+dw2/2+1,doy+26)],C['good'],2.2,9)
tx((D[2][0]+cx+dw2/2)/2,doy+6,L['allp'],13,C['good'],True,'mm')
im.save(f'/tmp/flow/qa-pipeline-flow-{lang}.png',optimize=True)
print(im.size)
