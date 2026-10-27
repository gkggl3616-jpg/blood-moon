import {THREE} from './engine.js';
export function humanView(scene){
 const root=new THREE.Group();scene.add(root);root.userData.recoil=0;
 const gun=new THREE.MeshStandardMaterial({color:0x283843,roughness:.48,metalness:.7}),steel=new THREE.MeshStandardMaterial({color:0x8496a1,roughness:.34,metalness:.8}),gold=new THREE.MeshStandardMaterial({color:0xb69a58,roughness:.5,metalness:.6}),glove=new THREE.MeshStandardMaterial({color:0x29343e,roughness:.9}),cloth=new THREE.MeshStandardMaterial({color:0x27344d,roughness:1});
 const groups={};
 function box(g,w,h,d,mat,x,y,z){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);g.add(m);return m;}
 function tube(g,r,len,mat,x,y,z){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,len,10),mat);m.rotation.x=Math.PI/2;m.position.set(x,y,z);g.add(m);return m;}
 for(const kind of ['rifle','sniper','pistol','knife','frag','smoke']){
  const g=new THREE.Group();root.add(g);groups[kind]=g;
  if(['rifle','sniper'].includes(kind)){
   box(g,.10,.11,.42,gun,.18,-.22,-.73);box(g,.09,.08,.19,cloth,.18,-.24,-.43);box(g,.075,.14,.10,gun,.18,-.33,-.70);box(g,.07,.19,.09,gun,.18,-.36,-.87);
   tube(g,.022,kind==='sniper'?.62:.40,steel,.18,-.21,-1.12);tube(g,.032,.05,gun,.18,-.21,kind==='sniper'?-1.43:-1.34);
   box(g,.08,.09,.25,gun,.18,-.22,-1.02);for(let j=0;j<6;j++)box(g,.10,.012,.014,steel,.18,-.163,-.93-j*.035);
   box(g,.035,.035,.04,gold,.18,-.14,-.70);box(g,.035,.035,.04,steel,.18,-.14,-1.17);
   if(kind==='sniper'){tube(g,.045,.21,gun,.18,-.095,-.82);tube(g,.047,.012,steel,.18,-.095,-.93);}
   box(g,.019,.035,.10,steel,.245,-.25,-.74);box(g,.025,.02,.13,gold,.18,-.20,-.48);
  }else if(kind==='pistol'){
   box(g,.075,.08,.26,steel,.18,-.23,-.65);box(g,.06,.12,.10,gun,.18,-.31,-.58);tube(g,.022,.05,gun,.18,-.23,-.81);box(g,.025,.022,.025,gold,.18,-.177,-.75);
  }else if(kind==='knife'){
   tube(g,.025,.18,cloth,.20,-.23,-.6);box(g,.11,.02,.025,gold,.20,-.22,-.72);
   const shape=new THREE.Shape();shape.moveTo(-.022,0);shape.lineTo(.022,0);shape.lineTo(.032,.22);shape.lineTo(0,.33);shape.lineTo(-.022,.22);const m=new THREE.Mesh(new THREE.ExtrudeGeometry(shape,{depth:.008,bevelEnabled:false}),steel);m.rotation.x=-Math.PI/2;m.position.set(.20,-.22,-.73);g.add(m);
  }else{
   const body=new THREE.Mesh(new THREE.IcosahedronGeometry(.07,1),kind==='frag'?new THREE.MeshStandardMaterial({color:0x547545,roughness:.8}):steel);body.position.set(.20,-.25,-.64);g.add(body);box(g,.04,.025,.035,gun,.20,-.17,-.64);const pin=new THREE.Mesh(new THREE.TorusGeometry(.025,.004,5,12),gold);pin.position.set(.17,-.15,-.62);g.add(pin);
  }
 }
 const arms=new THREE.Group();root.add(arms);
 for(const [x,z] of [[.22,-.44],[-.10,-.84]]){tube(arms,.047,.25,cloth,x,-.34,z);tube(arms,.051,.06,gold,x,-.34,z-.10);const hand=new THREE.Mesh(new THREE.SphereGeometry(.055,10,8),glove);hand.scale.set(.8,1,1.1);hand.position.set(x,-.29,z-.13);arms.add(hand);for(let i=0;i<4;i++)box(arms,.012,.038,.035,glove,x-.025+i*.015,-.28,z-.17);}
 root.setWeapon=kind=>{for(const [k,g] of Object.entries(groups))g.visible=k===kind;};root.setWeapon('rifle');return root;
}
