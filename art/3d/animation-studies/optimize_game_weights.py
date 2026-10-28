"""Fit four nonnegative skin influences to the authored action; fixed source geometry.
The approximation error is measured, not silently accepted as exact parity.
Run on the live Rigify study, before VFX and export.
"""
import bpy,numpy as np,json,itertools
from pathlib import Path
R=Path('/workspace/rogue-blood-moon');D=R/'dist/roar-study-03';s=bpy.context.scene;rig=bpy.data.objects['BilgeRigify'];names=[b.name for b in rig.data.bones if b.use_deform];frames=[0,4,8,14,20,27,33,44,51];mats=[]
for f in frames:
 s.frame_set(f);bpy.context.view_layer.update();mats.append(np.array([np.array(rig.pose.bones[n].matrix@rig.data.bones[n].matrix_local.inverted()) for n in names]))
mats=np.array(mats);report=[]
objects=[o for o in s.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
for obj in objects:
 N=len(obj.data.vertices)
 if not N:continue
 xyz=np.array([(*v.co,1) for v in obj.data.vertices]);weights=np.zeros((N,len(names)))
 for v in obj.data.vertices:
  for g in v.groups:
   n=obj.vertex_groups[g.group].name
   if n in names:weights[v.index,names.index(n)]=g.weight
 weights/=np.maximum(weights.sum(axis=1,keepdims=True),1e-12)
 positions=np.einsum('kbxy,ny->nkbx',mats,xyz)[:,:,:,:3];target=np.einsum('nkbv,nb->nkv',positions,weights)
 top=np.argsort(-weights,axis=1)[:,:7];candidate=np.take_along_axis(positions,top[:,None,:,None],axis=2)
 A=candidate.transpose(0,1,3,2).reshape(N,-1,7);Y=target.reshape(N,-1);best_weights=np.zeros_like(weights)
 for k in range(4):best_weights[np.arange(N),top[:,k]]=weights[np.arange(N),top[:,k]]
 best_weights/=np.maximum(best_weights.sum(axis=1,keepdims=True),1e-12)
 baseline=np.einsum('nkbv,nb->nkv',positions,best_weights);best_error=((baseline-target)**2).sum(axis=(1,2))
 for combo in itertools.combinations(range(7),4):
  ids=top[:,combo];a=A[:,:,combo];prior=np.take_along_axis(weights,ids,axis=1);prior/=np.maximum(prior.sum(axis=1,keepdims=True),1e-12)
  delta=a[:,:,:3]-a[:,:,3:4];goal=Y-a[:,:,3];ata=np.einsum('nki,nkj->nij',delta,delta);aty=np.einsum('nki,nk->ni',delta,goal);ata+=np.eye(3)[None]*1e-5;aty+=prior[:,:3]*1e-5
  q=np.linalg.solve(ata,aty[...,None])[...,0];q=np.c_[q,1-q.sum(axis=1)]
  # Euclidean projection onto the four-weight simplex.
  u=np.sort(q,axis=1)[:,::-1];cum=np.cumsum(u,axis=1)-1;den=np.arange(1,5);rho=np.maximum(0,(u-cum/den>0).sum(axis=1)-1);theta=cum[np.arange(N),rho]/(rho+1);q=np.maximum(q-theta[:,None],0)
  prediction=np.einsum('nki,ni->nk',a,q);error=((prediction-Y)**2).sum(axis=1);take=error<best_error
  if take.any():
   rows=np.flatnonzero(take);best_error[take]=error[take];best_weights[rows]=0
   for k in range(4):best_weights[rows,ids[rows,k]]=q[rows,k]
 fitted=np.einsum('nkbv,nb->nkv',positions,best_weights);err=np.linalg.norm(fitted-target,axis=2)
 for g in obj.vertex_groups:g.remove(list(range(N)))
 groups={g.name:g for g in obj.vertex_groups}
 for i,row in enumerate(best_weights):
  for k in np.flatnonzero(row>1e-6):groups[names[k]].add([i],float(row[k]),'REPLACE')
 report.append({'mesh':obj.name,'vertices':N,'max_influences':4,'max_error_m':float(err.max()),'p99_error_m':float(np.quantile(err,.99)),'mean_error_m':float(err.mean())});print('WEIGHT_FIT',report[-1])
s.frame_set(8);bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/3d/animation-studies/bilge-roar-study-03.blend'),compress=True);(D/'four-weight-fit.json').write_text(json.dumps({'sample_frames':frames,'meshes':report,'method':'Nonnegative four-influence pose fit; 35 candidate bone subsets, simplex projection','not_exact_mocap':True},indent=2))
