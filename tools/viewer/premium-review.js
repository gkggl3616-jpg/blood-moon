// Static production intake only. This view never claims rig or animation acceptance.
import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(900,1000);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;document.body.appendChild(renderer.domElement);
const scene=new T.Scene();scene.background=new T.Color('#121b24');scene.add(new T.HemisphereLight(0xdae9ff,0x34302b,2));for(const [x,z] of [[3,4],[-3,-2]]){const l=new T.DirectionalLight(0xffffff,2.5);l.position.set(x,5,z);scene.add(l);}
const file=new URLSearchParams(location.search).get('asset');if(!file)throw Error('asset required');const gltf=await new GLTFLoader().loadAsync(file);scene.add(gltf.scene);const box=new T.Box3().setFromObject(gltf.scene),size=box.getSize(new T.Vector3()),center=box.getCenter(new T.Vector3());
const camera=new T.PerspectiveCamera(34,.9,.01,10000),views={front:[0,0,1],back:[0,0,-1],side:[1,0,0],three:[.65,.05,1]};
function view(name){const span=Math.max(size.y*1.15,size.x*1.2/.9);camera.position.copy(center).addScaledVector(new T.Vector3(...views[name]).normalize(),span/(2*Math.tan(34*Math.PI/360)));camera.lookAt(center);renderer.render(scene,camera);return {bounds:[box.min.toArray(),box.max.toArray()],renderedTriangles:renderer.info.render.triangles};}
window.premiumReview={ready:true,view,asset:file};view('three');
