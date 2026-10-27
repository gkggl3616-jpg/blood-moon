import {THREE,identity} from './engine.js';
const tmp=new THREE.Vector3();
export class WolfEffects{
 constructor(scene){
  this.scene=scene;this.actor=null;this.key='kultigin';this.elapsed=0;this.trailLife=0;this.handles=[];
  const count=72;this.count=count;this.cursor=0;this.life=new Float32Array(count);this.vel=new Float32Array(count*3);this.positions=new Float32Array(count*3);this.colors=new Float32Array(count*3);this.sizes=new Float32Array(count);
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(this.positions,3));geo.setAttribute('color',new THREE.BufferAttribute(this.colors,3));geo.setAttribute('aSize',new THREE.BufferAttribute(this.sizes,1));
  this.particleMat=new THREE.ShaderMaterial({uniforms:{uTime:{value:0}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,vertexColors:true,vertexShader:'attribute float aSize; varying vec3 vColor; void main(){vColor=color;vec4 mv=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*mv;gl_PointSize=clamp(aSize*230./max(.2,-mv.z),1.,90.);}',fragmentShader:'uniform float uTime; varying vec3 vColor; void main(){vec2 p=gl_PointCoord-.5;p.x+=.07*sin(p.y*14.+uTime*18.);float d=length(p*vec2(1.5+max(0.,-p.y)*2.,.72));float a=pow(max(0.,1.-d*2.),1.7);gl_FragColor=vec4(vColor,a);}' });
  this.particles=new THREE.Points(geo,this.particleMat);this.particles.frustumCulled=false;scene.add(this.particles);
  this.trails=[];
  for(let i=0;i<4;i++){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(9*6*3),3));const m=new THREE.MeshBasicMaterial({color:0xa964ff,transparent:true,opacity:0,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,depthWrite:false});const mesh=new THREE.Mesh(g,m);mesh.frustumCulled=false;scene.add(mesh);this.trails.push(mesh);}
  this.ice=new THREE.Group();scene.add(this.ice);
  const crystal=new THREE.ConeGeometry(.065,.32,4),iceMat=new THREE.MeshStandardMaterial({color:0x64d6ff,emissive:0x1376ab,emissiveIntensity:.7,metalness:.25,roughness:.22});
  for(let hand=0;hand<2;hand++)for(let j=0;j<4;j++){const mesh=new THREE.Mesh(crystal,iceMat);this.ice.add(mesh);}
 }
 bind(actor,key){this.actor=actor;this.key=key;this.hasBuiltInIce=key==='bilge'&&actor?.getObjectByName('Body_bilge')?.userData.source_kind?.startsWith('new');this.handles=['L','R'].map(side=>actor?.getObjectByName('Hand'+side)||actor?.getObjectByName('mixamorigHand'+side)).filter(Boolean);this.elbows=['L','R'].map(side=>actor?.getObjectByName('Forearm'+side)).filter(Boolean);}
 spawn(pos,color=0xb14dff,n=5,burst=false){const c=new THREE.Color(color);for(let j=0;j<n;j++){const i=this.cursor++%this.count;this.life[i]=burst?.55:.38+Math.random()*.25;const p=i*3;this.positions[p]=pos.x+(Math.random()-.5)*.16;this.positions[p+1]=pos.y+(Math.random()-.5)*.14;this.positions[p+2]=pos.z+(Math.random()-.5)*.16;this.vel[p]=(Math.random()-.5)*(burst?4:.6);this.vel[p+1]=burst?Math.random()*3:1+Math.random();this.vel[p+2]=(Math.random()-.5)*(burst?4:.6);this.colors[p]=c.r;this.colors[p+1]=c.g;this.colors[p+2]=c.b;this.sizes[i]=burst?.35:.48;}}
 burst(pos,color=0xb14dff){this.spawn(pos,color,30,true);}
 claw(position,yaw){this.trailLife=.3;this.trailOrigin=position.clone();this.trailOrigin.y+=1.25;this.trailYaw=yaw;}
 update(dt,roaring,visible=true){
  this.elapsed+=dt;this.particleMat.uniforms.uTime.value=this.elapsed;const chosen=this.actor?.userData.clawProfile;const profile=chosen==='standard'?{color:0xb7d9e6,claws:3,tilt:-.3}:identity[chosen]||identity[this.key]||identity.kultigin;
  if(this.actor&&visible){this.actor.updateMatrixWorld(true);if(roaring)for(const bone of this.handles){bone.getWorldPosition(tmp);if(Math.random()<Math.min(1,dt*38))this.spawn(tmp,0xa849ff,2);}}
  this.ice.visible=visible&&this.key==='bilge'&&!this.hasBuiltInIce&&this.elbows.length===2;
  if(this.ice.visible){for(let side=0;side<2;side++){const bone=this.elbows[side];bone.getWorldPosition(tmp);for(let j=0;j<4;j++){const m=this.ice.children[side*4+j];m.position.copy(tmp);m.position.y-=j*.075;m.position.x+=(side?-.09:.09)*(1+j*.1);m.rotation.set(side?.4:-.4,0,side?-.65:.65);m.scale.setScalar(.8+j*.08);}}}
  for(let i=0;i<this.count;i++){const p=i*3;if(this.life[i]>0){this.life[i]-=dt;this.positions[p]+=this.vel[p]*dt;this.positions[p+1]+=this.vel[p+1]*dt;this.positions[p+2]+=this.vel[p+2]*dt;const fade=Math.max(0,1-dt*3);this.colors[p]*=fade;this.colors[p+1]*=fade;this.colors[p+2]*=fade;if(this.life[i]<=0)this.sizes[i]=0;}else this.sizes[i]=0;}
  for(const a of Object.values(this.particles.geometry.attributes))a.needsUpdate=true;
  this.trailLife=Math.max(0,this.trailLife-dt);
  const phase=(.3-this.trailLife)/.3;
  for(let stroke=0;stroke<this.trails.length;stroke++){
   const mesh=this.trails[stroke];mesh.visible=visible&&this.trailLife>0&&stroke<profile.claws;if(!mesh.visible)continue;
   mesh.material.color.setHex(profile.color);mesh.material.opacity=this.trailLife/.3;
   const arr=mesh.geometry.attributes.position.array;let offset=0;
   const point=(t,edge)=>{const angle=-1.15+t*2.2;const x=Math.sin(angle)*1.1,y=Math.cos(angle)*.75+stroke*.12-1;const tiltedX=x*Math.cos(profile.tilt)-y*Math.sin(profile.tilt),tiltedY=x*Math.sin(profile.tilt)+y*Math.cos(profile.tilt);return new THREE.Vector3(tiltedX+edge*.025,tiltedY,1.25+phase*.45).applyAxisAngle(new THREE.Vector3(0,1,0),this.trailYaw+Math.PI).add(this.trailOrigin);};
   for(let j=0;j<9;j++){const a=point(j/9,-1),b=point((j+1)/9,-1),c=point((j+1)/9,1),d=point(j/9,1);for(const v of [a,b,c,a,c,d]){arr[offset++]=v.x;arr[offset++]=v.y;arr[offset++]=v.z;}}
   mesh.geometry.attributes.position.needsUpdate=true;
  }
 }
 info(){return {particles:this.life.filter(x=>x>0).length,pool:this.count,flames:this.handles.length,ice:this.ice.visible,trail:this.trailLife>0};}
}
