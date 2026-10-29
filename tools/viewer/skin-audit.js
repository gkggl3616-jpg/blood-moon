import {Vector3} from 'three';
// Read-only diagnostics: test real deformed edges, not only bone/key metadata.
export function auditSkin(actor,limit=20){
 if(!actor)return null;actor.updateMatrixWorld(true);const meshes=[];
 actor.traverse(mesh=>{if(!mesh.isSkinnedMesh||!mesh.visible)return;mesh.skeleton.update();const g=mesh.geometry,p=g.attributes.position,index=g.index,si=g.attributes.skinIndex,sw=g.attributes.skinWeight;const posed=[];
 for(let i=0;i<p.count;i++)posed.push(mesh.applyBoneTransform(i,new Vector3().fromBufferAttribute(p,i)));
 const edges=new Set(),bad=[],ratios=[];let maxRatio=0;
 const weights=i=>Array.from({length:4},(_,j)=>({bone:mesh.skeleton.bones[si.array[i*4+j]]?.name,weight:sw.array[i*4+j]})).filter(w=>w.weight>.0001);
 for(let t=0;t<(index?.count||p.count);t+=3){const tri=[0,1,2].map(j=>index?index.getX(t+j):t+j);
  for(let k=0;k<3;k++){const a=Math.min(tri[k],tri[(k+1)%3]),b=Math.max(tri[k],tri[(k+1)%3]),key=a+':'+b;if(edges.has(key))continue;edges.add(key);const pa=new Vector3().fromBufferAttribute(p,a),pb=new Vector3().fromBufferAttribute(p,b),rest=pa.distanceTo(pb);if(rest<1e-8)continue;const length=posed[a].distanceTo(posed[b]),ratio=length/rest;ratios.push(ratio);maxRatio=Math.max(maxRatio,ratio);
   if(ratio>3)bad.push({ratio,length,rest,vertices:[{id:a,rest:pa.toArray(),weights:weights(a)},{id:b,rest:pb.toArray(),weights:weights(b)}]});
  }
 }
 ratios.sort((a,b)=>a-b);const referenceScale=ratios[Math.floor(ratios.length/2)]||1;for(const e of bad)e.ratio/=referenceScale;const unit=actor.userData.nativeGeometryBasis?actor.userData.nativeUnitScaleMeters:1;for(const e of bad){e.physicalRestM=e.rest*unit;e.physicalLengthM=e.length/referenceScale*unit;}const stretched=bad.filter(e=>e.ratio>3&&(e.physicalLengthM-e.physicalRestM)>.01);stretched.sort((a,b)=>b.ratio-a.ratio);meshes.push({mesh:mesh.name,vertices:p.count,edges:edges.size,referenceScale,maxRawRatio:maxRatio/referenceScale,physicalGrowthThresholdM:.01,maxRatio:Math.max(1,...stretched.map(e=>e.ratio)),edgesOver3:stretched.length,worst:stretched.slice(0,limit)});
 });return {meshes};
}

// Test-only full mesh contact measurement; never called from the render loop.
export function skinFloor(actor){
 if(!actor)return null;actor.updateMatrixWorld(true);let floor=Infinity;const v=new Vector3();
 actor.traverse(o=>{if(!o.isSkinnedMesh||!o.visible||!o.name.startsWith('Body'))return;const p=o.geometry.attributes.position;for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i);o.applyBoneTransform(i,v).applyMatrix4(o.matrixWorld);floor=Math.min(floor,v.y);}});return Number.isFinite(floor)?floor:null;
}
