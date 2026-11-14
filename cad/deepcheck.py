import sys; sys.path.insert(0,'.')
import model as m, numpy as np, math, json
from manifold3d import Manifold, CrossSection, JoinType
m.frame_hole=lambda: Manifold()
BED=(340,320); BRIM=5
def flipx(g): return g.transform([[1,0,0,0],[0,-1,0,0],[0,0,-1,0]])
def bed(g): bb=g.bounding_box(); return g.translate([-(bb[0]+bb[3])/2,-(bb[1]+bb[4])/2,-bb[2]])
ring=m.ring_pieces()
import os as _os
ASM={'carrier':m.carrier(),'liner':m.liner(front_spk=_os.environ.get('NOSPK') is None),'mount':m.mount(),'cup':m.pen_cup_placed()}
for k,p in ring.items(): ASM['ring%+d%+d'%k]=p
PRINT={'carrier':bed(ASM['carrier']),'liner':bed(flipx(ASM['liner'])),'mount':bed(ASM['mount']),'cup':bed(m.pen_cup_v8())}
for k,p in ring.items(): PRINT['ring%+d%+d'%k]=bed(p)
FIX={'frame':m.frame(),'mat':m.matboard(),'tablet':m.tablet_body(),'felt':m.felt_strips(),'adapter':m.adapter(),'cable':m.charger_cable()}
R=lambda v,n=2: round(float(v),n)
out={}
print('=== A. integrity / bed fit / material')
tot=0
for n,g in PRINT.items():
    bb=g.bounding_box(); dx,dy,dz=bb[3]-bb[0],bb[4]-bb[1],bb[5]-bb[2]
    fit=(dx+2*BRIM<=BED[0] and dy+2*BRIM<=BED[1]) or (dy+2*BRIM<=BED[0] and dx+2*BRIM<=BED[1])
    vol=g.volume()/1000; tot+=vol
    print(f'{n:10s} pieces={len(g.decompose())} status={g.status().name if hasattr(g.status(),"name") else g.status()} size={R(dx,1)}x{R(dy,1)}x{R(dz,1)} bedfit(+{BRIM}brim)={fit} vol={R(vol,1)}cm3 solid={R(vol*1.27,0)}g')
print('total solid volume cm3',R(tot,1))
print('=== B. layer scan: bridges / cantilevers / islands (0.2 mm layers)')
def rect(x0,y0,x1,y1): return CrossSection.square([max(x1-x0,1e-3),max(y1-y0,1e-3)]).translate([x0,y0])
def scan(g,dz=0.2):
    bb=g.bounding_box(); zs=np.arange(dz/2,bb[5],dz); prev=None; items=[]
    for z in zs:
        S=g.slice(float(z))
        if prev is not None:
            O=(S-prev).offset(-0.2,JoinType.Round).offset(0.2,JoinType.Round)
            for c in O.decompose():
                if c.area()<0.6: continue
                x0,y0,x1,y1=c.bounds(); w=0.7
                lo,hi=0.0,min(x1-x0,y1-y0)/2+0.01
                for _ in range(9):
                    mid=(lo+hi)/2
                    if c.offset(-mid,JoinType.Round).area()>1e-3: lo=mid
                    else: hi=mid
                iw=2*lo                                    # widest unsupported spot (inscribed width)
                sup=lambda r: (r^prev).area()>0.15
                Ls,Rs,Bs,Ts=sup(rect(x0-w,y0,x0,y1)),sup(rect(x1,y0,x1+w,y1)),sup(rect(x0,y0-w,x1,y0)),sup(rect(x0,y1,x1,y1+w))
                if not (Ls or Rs or Bs or Ts): kind='ISLAND'
                elif (Ls and Rs) or (Bs and Ts): kind='bridge'
                else: kind='cantilever'
                items.append((kind,R(iw,1),R(z,1),R((x0+x1)/2,0),R((y0+y1)/2,0),R(x1-x0,1),R(y1-y0,1)))
        prev=S
    return items
for n,g in PRINT.items():
    it=scan(g)
    br=[i for i in it if i[0]=='bridge']; ca=[i for i in it if i[0]=='cantilever' and i[1]>2.5]; isl=[i for i in it if i[0]=='ISLAND']
    mb=max([i[1] for i in br],default=0)
    print(f'{n:10s} max bridge={mb}  bridges>28: {len([i for i in br if i[1]>28])}  cantilevers>2mm: {len(ca)}  islands: {len(isl)}')
    for i in sorted(ca,key=lambda i:-i[1])[:6]: print('     cantilever reach',i[1],'at z',i[2],'xy',(i[3],i[4]),'size',i[5],'x',i[6])
    for i in isl[:6]: print('     ISLAND',i)
    for i in sorted([i for i in br if i[1]>20],key=lambda i:-i[1])[:4]: print('     bridge',i[1],'at z',i[2],'xy',(i[3],i[4]),'size',i[5],'x',i[6])
    out[n]={'maxbridge':mb,'cant':ca[:20],'isl':isl[:20]}
print('=== C. thin walls (<0.8 mm) and narrow gaps (<0.4 mm), sampled layers')
for n,g in PRINT.items():
    bb=g.bounding_box(); worst=[]; gaps=[]
    for z in np.linspace(0.3,bb[5]-0.3,14):
        S=g.slice(float(z))
        T=(S-S.offset(-0.4,JoinType.Round).offset(0.4,JoinType.Round)).offset(-0.08,JoinType.Round)
        for c in T.decompose():
            if c.area()>0.4: x0,y0,x1,y1=c.bounds(); worst.append((R(c.area(),1),R(z,1),R((x0+x1)/2,0),R((y0+y1)/2,0)))
        Gp=(S.offset(0.2,JoinType.Round).offset(-0.2,JoinType.Round)-S).offset(-0.05,JoinType.Round)
        for c in Gp.decompose():
            if c.area()>0.4: x0,y0,x1,y1=c.bounds(); gaps.append((R(c.area(),1),R(z,1),R((x0+x1)/2,0),R((y0+y1)/2,0)))
    print(f'{n:10s} thin spots: {len(worst)}  narrow gaps: {len(gaps)}')
    for w in sorted(worst,reverse=True)[:6]: print('     thin  area',w[0],'z',w[1],'xy',(w[2],w[3]))
    for w in sorted(gaps,reverse=True)[:4]: print('     gap   area',w[0],'z',w[1],'xy',(w[2],w[3]))
print('=== D. clashes (assembled)')
ALL={**ASM,**FIX}; ks=list(ALL); n=0
for i in range(len(ks)):
    for j in range(i+1,len(ks)):
        v=(ALL[ks[i]]^ALL[ks[j]]).volume()
        if v>0.005: print('  CLASH',ks[i],ks[j],R(v,2)); n+=1
print('  clash pairs:',n,'(tablet^adapter = plug in the port, expected)')
print('=== E. clearances (min gap, mm)')
RING=Manifold.batch_boolean(list(ring.values()),m.M.OpType.Add)
for a,b,exp in (('tablet','liner','~0.5 sides'),('liner','carrier','0.3'),('mount','carrier','0.5-0.7'),('ring','frame','0.3'),('mat','ring','0.2 at lip'),('tablet','mount','0.3 pad'),('mat','frame','lip contact'),('carrier','frame','0 = ears on frame back'),('cup','frame','0 glue face'),('ring','carrier','0.3 locators'),('cable','carrier','>0'),('cable','ring','>0'),('cable','frame','>0')):
    A={**ALL,'ring':RING}[a]; B={**ALL,'ring':RING}[b]
    try: print(f'  {a:8s}-{b:8s} {R(A.min_gap(B,5.0),2)}   (expect {exp})')
    except Exception as e: print('  min_gap n/a',e); break
print('=== F. assembly motions')
car,lin,mnt=ASM['carrier'],ASM['liner'],ASM['mount']
print('  liner onto carrier (liner moved +z = toward room):',[(d,R((lin.translate([0,0,d])^car).volume(),1)) for d in (0,0.5,1,2,3,6,12)])
mod=car+lin+FIX['tablet']
fr=FIX['frame']+FIX['mat']+RING
print('  module into frame (module moved -z = toward wall side/away from frame):',[(d,R((mod.translate([0,0,-d])^fr).volume(),2)) for d in (0,1,3,6,12,20)])
print('  ring into rabbet (ring moved -z):',[(d,R((RING.translate([0,0,-d])^(FIX["frame"]+FIX["mat"])).volume(),2)) for d in (0,2,6,12)])
asm=car
print('  seated, pull straight off wall (+z):',[(d,R((asm.translate([0,0,d])^mnt).volume(),1)) for d in (0.5,1,2)], '-> must be >0 (trapped)')
print('  lift (+y):',[(d,R((asm.translate([0,d,0])^mnt).volume(),2)) for d in (2,6,12,18,22,24)],'-> 0 all the way')
print('  lifted L then off (+z 3 mm):',[(L,R((asm.translate([0,L,3])^mnt).volume(),1)) for L in (6,12,16,18,20,22,24)],'-> first 0 = release lift')
print('  sideways seated (x 1 mm):',R((asm.translate([1,0,0])^mnt).volume(),1),'-> >0 = centred')
print('  module (with tablet) seated vs mount:',R(((car+FIX["tablet"])^mnt).volume(),3))
plug=FIX['tablet']+FIX['adapter']+m.usba_plug()+m.pd_plug()+lin
print('  carrier onto liner+tablet+adapter+plugs (carrier moved -z):',[(dd,R((car.translate([0,0,-dd])^plug).volume(),2)) for dd in (0,1,3,6,10,16)])
print('  hang path with tablet+bump in (lift y, mount fixed):',[(L,R(((car+FIX['tablet']).translate([0,L,0])^mnt).volume(),2)) for L in (0,8,16,24)])
print('=== G. sound paths (port connected to the room)')
solid=ASM['liner']+ASM['carrier']+FIX['tablet']+FIX['mat']+FIX['felt']+RING
my,mx=m.MAT_OPEN[1]/2,m.MAT_OPEN[0]/2
for x0,x1 in m.MIC_X:
    xa,xb=m.tab_x(x0),m.tab_x(x1); xm=(xa+xb)/2
    B=m.box(xa+0.5,xb-0.5,m.TAB_H/2-3,my+5,m.Z_TAB0+0.2,m.Z_MAT1+1.5)
    air=B-solid; ok=False
    for c in air.decompose():
        if (c^m.box(xm-1,xm+1,m.TAB_H/2+0.05,m.TAB_H/2+0.45,m.PORT_T-0.3,m.PORT_T+0.3)).volume()>1e-4:
            ok=c.bounding_box()[5]>m.Z_MAT1+1.0
    print('  mic at',R((x0+x1)/2,1),'from left: open to room =',ok)
for y0,y1 in m.SPK_Y:
    ya,yb=m.tab_y(y1),m.tab_y(y0); ym=(ya+yb)/2
    for sg in (-1,1):
        xs=sorted((sg*(m.TAB_W/2-3),sg*(mx+5)))
        B=m.box(xs[0],xs[1],ya+0.5,yb-0.5,m.Z_TAB0+0.2,m.Z_MAT1+1.5); air=B-solid; ok=False
        px=sorted((sg*(m.TAB_W/2+0.05),sg*(m.TAB_W/2+0.45)))
        for c in air.decompose():
            if (c^m.box(px[0],px[1],ym-1,ym+1,m.PORT_T-0.3,m.PORT_T+0.3)).volume()>1e-4:
                ok=c.bounding_box()[5]>m.Z_MAT1+1.0
        print('  speaker',('L' if sg<0 else 'R'),R((y0+y1)/2,1),'from top: front slit open =',ok)
print('=== H. spot checks')
l=ASM['liner']
print('  liner material touching glass zone (z<15.4 inside tablet outline):',R((l^(m.rrect(m.TAB_W,m.TAB_H,m.TAB_R,m.Z_TAB1,m.Z_FELT1-0.1))).volume(),2))
print('  tablet corner vs liner pocket min gap:',R(FIX['tablet'].min_gap(l,5),2))
print('  front camera + sensor window clear:',R((l^m.box(-11.5,11.5,m.FCAM_Y-1.6,m.FCAM_Y+1.6,m.Z_TAB1,m.Z_MAT1+3)).volume(),3),' mat over it:',R((FIX['mat']^m.box(-11.5,11.5,m.FCAM_Y-1.6,m.FCAM_Y+1.6,0,40)).volume(),3))
print('  ear thickness under screw head:',R(m._lug_z1()-m.Z_CAR_BACK-1.9,2),' ear end inside frame edge:',R(m.FR_OUT[1]/2-m.EAR_Y1,2),' screw to rabbet edge:',R(m.EAR_SCREW_Y-m.MAT_H/2,2),' to outer edge:',R(m.FR_OUT[1]/2-m.EAR_SCREW_Y,2))
print('  frame back off wall:',R(m.Z_FR_BACK,2),' frame face off wall:',R(m.Z_FR_FACE,2))
print('  felt vs tunnels/window clash with liner:',R((FIX['felt']^l).volume(),3))
print('  cup lowest z (wall at 0):',R(ASM['cup'].bounding_box()[2],2),' cup y range:',R(ASM['cup'].bounding_box()[1],1),R(ASM['cup'].bounding_box()[4],1),' frame bottom:',-m.FR_OUT[1]/2)
