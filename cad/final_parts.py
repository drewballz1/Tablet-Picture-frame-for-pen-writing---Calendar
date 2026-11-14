import sys; sys.path.insert(0,'.')
import model as m, numpy as np, struct, os, zipfile
from manifold3d import Manifold
from render import Scene
from PIL import Image
flipx=lambda g: g.transform([[1,0,0,0],[0,-1,0,0],[0,0,-1,0]])
def bed(g): bb=g.bounding_box(); return g.translate([-(bb[0]+bb[3])/2,-(bb[1]+bb[4])/2,-bb[2]])
ring=m.ring_pieces()
P={'P1_wall_mount_black':bed(m.mount()),'P2_carrier_black':bed(m.carrier()),'P3a_liner_white_speaker_slits':bed(flipx(m.liner())),'P3b_liner_white_plain':bed(flipx(m.liner(front_spk=False))),
   'P4a_ring_top_left_black':bed(ring[(-1,1)]),'P4b_ring_top_right_black':bed(ring[(1,1)]),'P4c_ring_bottom_left_black':bed(ring[(-1,-1)]),'P4d_ring_bottom_right_black':bed(ring[(1,-1)]),
   'P5_pen_cup_white':bed(m.pen_cup_v8())}
os.makedirs('../stl',exist_ok=True)
def stl(g,path):
    me=g.to_mesh(); V=np.asarray(me.vert_properties)[:,:3].astype(np.float32); F=np.asarray(me.tri_verts)
    a,b,c=V[F[:,0]],V[F[:,1]],V[F[:,2]]; n=np.cross(b-a,c-a); n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
    rec=np.zeros(len(F),dtype=[('n','<f4',3),('a','<f4',3),('b','<f4',3),('c','<f4',3),('u','<u2')])
    rec['n'],rec['a'],rec['b'],rec['c']=n,a,b,c
    with open(path,'wb') as f: f.write(b'nook mount v8'.ljust(80,b' ')); f.write(struct.pack('<I',len(F))); f.write(rec.tobytes())
for n,g in P.items(): stl(g,'../stl/%s.stl'%n); print(n,[round(v,1) for v in g.bounding_box()[3:]],os.path.getsize('../stl/%s.stl'%n)//1024,'kB')
def shot(g,col,az,el,title,sub,zoom=None,center=None):
    s=Scene(); s.add(g,col,'p'); kw={}
    if zoom: kw=dict(zoom=zoom,center=center)
    s.render(az,el,size=(1500,950),margin=(60,60,110,40),**kw); s.title(title,sub); return s.img
A=shot(P['P2_carrier_black'],(98,100,108),35,35,'P2 carrier, as printed (wall side on the bed)','8 ears on the bed, catch blocks up, big USB window on the right edge')
B=shot(P['P3a_liner_white_speaker_slits'],(232,230,224),35,40,'P3 liner, as printed (white face on the bed)','back side up: tablet pocket, sound tunnels, USB window, spring beams')
R4=Manifold.batch_boolean(list(ring.values()),m.M.OpType.Add)
C=shot(bed(R4),(80,82,90),35,40,'P4 ring, 4 pieces shown together (back on the bed, lip up)','lap joints mid-sides; bay on the right rail for the pen charger body; cable groove underneath')
D=shot(P['P5_pen_cup_white'],(200,200,205),-50,30,'P5 pen cup, as printed (upright)','open side = glue face to the frame; cone seat and drain hole inside')
W=Image.new('RGB',(3000,1900),(250,250,248))
for im,(x,y) in zip((A,B,C,D),((0,0),(1500,0),(0,950),(1500,950))): W.paste(im,(x,y))
W.save('../images/print_orientation.png')
