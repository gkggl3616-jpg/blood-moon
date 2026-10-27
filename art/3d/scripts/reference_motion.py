"""Authored phase poses from the 2026-10-28 run/roar reference review.
Coordinates are Blender Z-up, forward -Y. Support paws advance +Y at the
virtual root speed, then baked clips play in-place in the game. No mesh edits.
"""
import math
from mathutils import Vector,Matrix,Quaternion

RUN_SECONDS=16/30
RUN_METERS=8*RUN_SECONDS
ROAR_SECONDS=1.2
SOLE_OFFSETS={k:0. for k in ['frontL','frontR','rearL','rearR']}
def set_sole_offsets(values=None):
 for key in SOLE_OFFSETS:SOLE_OFFSETS[key]=(values or {}).get(key,0.)
# phase, pelvis height, lumbar pitch, rib pitch, neck-base pitch, neck pitch,
# head pitch. Angles are global X rotations from the approved standing rig.
RUN_KEYS=[
 (0.00,.335,94,96,64,46,67), # reach / leading forepaw touchdown
 (0.17,.315,89,96,60,42,64), # absorb front support, rear legs recover
 (0.34,.340,78,86,57,40,63), # gather under the belly
 (0.51,.322,82,92,62,43,65), # hind support / forelimb recovery
 (0.68,.355,96,100,68,47,68),# hind push-off and body extension
 (0.84,.360,99,98,66,44,66), # suspension / reach
 (1.00,.335,94,96,64,46,67)]
# phase, anticipation, arm spread, overhead, chest lift, jaw opening.
ROAR_KEYS=[(0,0,0,0,0,0),(.15,1,.14,0,0,0),(.30,.45,1,.08,.25,.2),(.49,0,.25,1,1,1),(.67,0,.18,1,1,1),(.82,.12,.65,.32,.4,.45),(1,0,0,0,0,0)]

def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)

def sample(keys,t,cyclic=False):
 t=t%1 if cyclic else max(0,min(1,t))
 for a,b in zip(keys,keys[1:]):
  if t<=b[0]+1e-8:
   u=ease((t-a[0])/(b[0]-a[0]));return [a[k]+(b[k]-a[k])*u for k in range(1,len(a))]
 return list(keys[-1][1:])

def rot(degrees):return Matrix.Rotation(math.radians(degrees),3,'X')

def trunk(p,base,angles):
 # Preserve every lumbar/chest/neck/head segment, not just limbs.
 for a,b,angle in zip(['hip','spine','chest','neck','head'],['spine','chest','neck','head','headEnd'],angles):p[b]=p[a]+rot(angle)@(base[b]-base[a])
 for side in ['L','R']:p['shoulder'+side]=p['chest']+rot(angles[2])@(base['shoulder'+side]-base['chest'])

def support(u,start,length,stance,lift):
 """Exact linear support + smooth recovery; return Y, rise, is_support."""
 u=u%1
 if u<=stance:return start+length*u/stance,0.,True
 s=(u-stance)/(1-stance);q=ease(s)
 return start+length*(1-q),lift*math.sin(math.pi*s)**1.25,False

def run_pose(base,t,h,two_bone):
 p={k:v.copy() for k,v in base.items()};z,*angles=sample(RUN_KEYS,t,True)
 # Match the shorter front-arm source without stretching its limb or neck.
 arms=[((base['elbow'+s]-base['shoulder'+s]).length+(base['wrist'+s]-base['elbow'+s]).length)/h for s in ['L','R']]
 z+=min(0,(min(arms)-.33)*.50)
 # Shorter source arms need a lower rib cage, not scaled bones or sliding
 # contact goals. Preserve the same phase curve, adapting lumbar inclination.
 lean_extra=max(0,(.33-min(arms))*230);angles[0]+=lean_extra;angles[1]+=lean_extra
 p['hip']=Vector((0,.145*h,z*h));trunk(p,base,angles)
 # Plant centers are authored in root space. Identical world travel and phase
 # windows for every wolf, with skeleton-width retargeting only.
 for side,sg,offset in [('L',1,0),('R',-1,.085)]:
  shoulder=p['shoulder'+side];front_stance=.18
  fy,fl,plant=support(t+offset,-.12*h-RUN_METERS*front_stance/2,RUN_METERS*front_stance,front_stance,.165*h)
  p['wrist'+side]=Vector((shoulder.x*.92,fy,(.105*h)+SOLE_OFFSETS['front'+side]+fl))
  p['elbow'+side]=shoulder+Vector((sg*.035*h,.16*h,-.07*h))
  p['finger'+side]=p['wrist'+side]+Vector((0,-.064,-.053)).normalized()*(base['finger'+side]-base['wrist'+side]).length
  # During recovery the fingers fold under the forearm rather than paddling.
  if not plant:
   q=ease(min(1,fl/(.15*h)));p['finger'+side]=p['wrist'+side]+Vector((0,-.35,-1)).normalized()*(base['finger'+side]-base['wrist'+side]).length
  hip_local=base['hip'+side]-base['hip'];p['hip'+side]=p['hip']+Vector((hip_local.x,hip_local.y,hip_local.z))
  rear_stance=.20
  ry,rl,rear_plant=support(t+offset+.49,.145*h-RUN_METERS*rear_stance/2,RUN_METERS*rear_stance,rear_stance,.175*h)
  p['ankle'+side]=Vector((sg*.108*h,ry,.092*h+SOLE_OFFSETS['rear'+side]+rl))
  # Splayed knee recovery is intentional in reference frames 11/35/59/83.
  gather=math.sin(math.pi*min(1,rl/(.175*h))) if not rear_plant else 0
  p['knee'+side]=p['hip'+side]+Vector((sg*(.055+.035*gather)*h,-.15*h,-.08*h))
  p['toe'+side]=p['ankle'+side]+Vector((0,-1,-.32)).normalized()*(base['toe'+side]-base['ankle'+side]).length
  for a,j,b,tip in [('shoulder','elbow','wrist','finger'),('hip','knee','ankle','toe')]:
   a+=side;j+=side;b+=side;tip+=side;d=p[tip]-p[b]
   p[j],p[b]=two_bone(p[a],p[b],p[j],(base[j]-base[a]).length,(base[b]-base[j]).length);p[tip]=p[b]+d
 # Preserve tail attachment and segment lengths, with a quiet trailing arc.
 p['tail']=p['hip']+rot(angles[0])@(base['tail']-base['hip'])
 for a,b in [('tail','tailMid'),('tailMid','tailEnd')]:
  length=(base[b]-base[a]).length;p[b]=p[a]+Vector((.018*math.sin(math.tau*t),.97,-.24)).normalized()*length
 return p

def roar_pose(base,t,h,two_bone):
 p={k:v.copy() for k,v in base.items()};charge,spread,high,lift,jaw=sample(ROAR_KEYS,t)
 p['hip'].z-=h*(.012*charge+.003*high)
 trunk(p,base,[6*charge,-5*lift+5*charge,-12*lift+8*charge,-12*lift+4*charge,-27*lift])
 for side,sg,delay in [('L',1,0),('R',-1,.018)]:
  _,s,up,_,_=sample(ROAR_KEYS,max(0,t-delay));shoulder=p['shoulder'+side]
  l1=(base['elbow'+side]-base['shoulder'+side]).length;l2=(base['wrist'+side]-base['elbow'+side]).length
  arm=l1+l2;rest=base['wrist'+side]+Vector((0,0,-.012*h*charge))
  wide=Vector((sg*(abs(shoulder.x)+.17*h),-.07*h,shoulder.z-.10*h))
  top=Vector((sg*abs(shoulder.x)*.92,-.055*h,shoulder.z+.91*arm))
  goal=rest.lerp(wide,s).lerp(top,up)
  pole=shoulder+Vector((sg*.15*h,.045*h,.11*h*up-.12*h*(1-up)))
  p['elbow'+side],p['wrist'+side]=two_bone(shoulder,goal,pole,l1,l2)
  rest_dir=base['finger'+side]-base['wrist'+side];up_dir=Vector((sg*.08,-.22,1)).normalized()*rest_dir.length
  p['finger'+side]=p['wrist'+side]+rest_dir.lerp(up_dir,up).normalized()*rest_dir.length
  p['hip'+side]=p['hip']+(base['hip'+side]-base['hip'])
  p['knee'+side],p['ankle'+side]=two_bone(p['hip'+side],base['ankle'+side],base['knee'+side],(base['knee'+side]-base['hip'+side]).length,(base['ankle'+side]-base['knee'+side]).length)
  p['toe'+side]=p['ankle'+side]+(base['toe'+side]-base['ankle'+side])
 # Tail follows the hips without extending its root or whipping over the legs.
 for name in ['tail','tailMid','tailEnd']:p[name]+=p['hip']-base['hip']
 return p

def jaw_envelope(kind,t):return sample(ROAR_KEYS,t)[4] if kind=='WolfRoar' else 0

def wrist_roll(kind,t,side):
 return (1 if side=='L' else -1)*.48*sample(ROAR_KEYS,t)[2] if kind=='WolfRoar' else 0

def setup_digits(base,h):
 for side,sg in [('L',1),('R',-1)]:
  d=(base['finger'+side]-base['wrist'+side]).normalized()
  for label,sign in [('Inner',-1),('Outer',1)]:
   head=base['finger'+side]+Vector((sg*sign*.012*h,0,0));base['digits'+label+side]=head;base['digits'+label+'End'+side]=head+d*.050*h

def pose_digits(p,base,kind,t,h):
 for side,sg in [('L',1),('R',-1)]:
  direction=(p['finger'+side]-p['wrist'+side]).normalized()
  global_roll=Matrix.Rotation(math.tau*ease((t-.10)/.72),3,'X') if kind=='WolfRoll' else Matrix.Identity(3)
  align=global_roll@(base['finger'+side]-base['wrist'+side]).rotation_difference(global_roll.inverted()@direction).to_matrix()
  align=Quaternion(direction,wrist_roll(kind,t,side)).to_matrix()@align
  up=jaw_envelope(kind,t)
  u=(t+(0 if side=='L' else .085))%1
  curl=.32*math.sin(math.pi*max(0,(u-.18)/.82))**2 if kind=='WolfRunQuad' else -.25*up
  if kind=='WolfRoll':curl=.28*math.sin(math.pi*t)**2
  for label,sign in [('Inner',-1),('Outer',1)]:
   name='digits'+label+side;end='digits'+label+'End'+side
   p[name]=p['finger'+side]+align@(base[name]-base['finger'+side])
   bend=Matrix.Rotation(curl,3,'X')@Matrix.Rotation(sign*sg*.18*up,3,'Y')
   p[end]=p[name]+align@bend@(base[end]-base[name])
 return p
