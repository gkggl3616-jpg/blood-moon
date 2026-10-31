"""Make shipped character GLBs Khronos-clean without changing rendered skinning.

Zero-weight JOINTS slots are semantically ignored but the validator requires index 0.
Skinned mesh nodes are moved from the common scale parent to scene roots with the same
world matrix, as required by glTF; the armature keeps its existing scale parent.
"""
from pathlib import Path
import json
import struct
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'app/src/main/assets/models'


def unpack(data):
    length = struct.unpack_from('<I', data, 12)[0]
    return json.loads(data[20:20 + length]), bytearray(data[28 + length:])


def node_matrix(node):
    if 'matrix' in node: return np.array(node['matrix'], float).reshape(4, 4).T
    x, y, z, w = node.get('rotation', [0, 0, 0, 1]); result = np.eye(4)
    result[:3, :3] = np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                               [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                               [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]) * np.array(node.get('scale', [1,1,1]))
    result[:3, 3] = node.get('translation', [0,0,0]); return result


def main(path):
    before = path.read_bytes(); gltf, binary = unpack(before)
    parents = {child: parent for parent, node in enumerate(gltf['nodes']) for child in node.get('children', [])}
    cache = {}
    def world(index):
        if index not in cache:
            local = node_matrix(gltf['nodes'][index]); cache[index] = local if index not in parents else world(parents[index]) @ local
        return cache[index]
    mesh_roots = []
    for index, node in enumerate(gltf['nodes']):
        if 'mesh' not in node or 'skin' not in node or index not in parents: continue
        parent = parents[index]
        gltf['nodes'][parent]['children'].remove(index)
        for key in ('translation', 'rotation', 'scale'): node.pop(key, None)
        node.pop('matrix', None)
        gltf['scenes'][gltf.get('scene', 0)].setdefault('nodes', []).append(index)
        mesh_roots.append(node.get('name', str(index)))
    zeroed = 0
    for node in gltf['nodes']:
        if 'mesh' not in node or 'skin' not in node: continue
        for primitive in gltf['meshes'][node['mesh']]['primitives']:
            ja = gltf['accessors'][primitive['attributes']['JOINTS_0']]
            wa = gltf['accessors'][primitive['attributes']['WEIGHTS_0']]
            jv = gltf['bufferViews'][ja['bufferView']]; wv = gltf['bufferViews'][wa['bufferView']]
            jdtype = {5121:np.uint8,5123:np.uint16}[ja['componentType']]
            wdtype = {5121:np.uint8,5123:np.uint16,5126:np.float32}[wa['componentType']]
            jo = jv.get('byteOffset',0)+ja.get('byteOffset',0); wo=wv.get('byteOffset',0)+wa.get('byteOffset',0)
            joints=np.frombuffer(binary,jdtype,ja['count']*4,jo).reshape(-1,4).copy()
            weights=np.frombuffer(binary,wdtype,wa['count']*4,wo).reshape(-1,4).copy()
            mask=weights==0;zeroed+=int(((joints!=0)&mask).sum());joints[mask]=0
            binary[jo:jo+joints.nbytes]=joints.tobytes()
    # Store the same tangent basis Three.js would otherwise generate at runtime.
    for node in gltf['nodes']:
        if 'mesh' not in node: continue
        for primitive in gltf['meshes'][node['mesh']]['primitives']:
            material = gltf['materials'][primitive.get('material', 0)] if gltf.get('materials') else {}
            attrs = primitive['attributes']
            if 'normalTexture' not in material or 'TANGENT' in attrs or not {'POSITION','NORMAL','TEXCOORD_0'} <= set(attrs): continue
            def values(accessor_index, width, dtype):
                acc=gltf['accessors'][accessor_index];view=gltf['bufferViews'][acc['bufferView']]
                offset=view.get('byteOffset',0)+acc.get('byteOffset',0)
                return np.frombuffer(binary,dtype,acc['count']*width,offset).reshape(-1,width).copy()
            pos=values(attrs['POSITION'],3,np.float32);normal=values(attrs['NORMAL'],3,np.float32);uv=values(attrs['TEXCOORD_0'],2,np.float32)
            ia=gltf['accessors'][primitive['indices']];idt={5123:np.uint16,5125:np.uint32}[ia['componentType']]
            tri=values(primitive['indices'],1,idt).ravel().reshape(-1,3).astype(int)
            tan=np.zeros_like(pos);bit=np.zeros_like(pos)
            for a,b,c in tri:
                e1=pos[b]-pos[a];e2=pos[c]-pos[a];d1=uv[b]-uv[a];d2=uv[c]-uv[a];den=d1[0]*d2[1]-d1[1]*d2[0]
                if abs(den)<1e-12:continue
                t=(e1*d2[1]-e2*d1[1])/den;q=(e2*d1[0]-e1*d2[0])/den
                tan[[a,b,c]]+=t;bit[[a,b,c]]+=q
            tangent=np.zeros((len(pos),4),np.float32)
            for i in range(len(pos)):
                t=tan[i]-normal[i]*np.dot(normal[i],tan[i]);length=np.linalg.norm(t)
                tangent[i,:3]=t/length if length>1e-12 else [1,0,0]
                tangent[i,3]=-1 if np.dot(np.cross(normal[i],tangent[i,:3]),bit[i])<0 else 1
            binary.extend(b'\0'*(-len(binary)%4));view_index=len(gltf['bufferViews']);gltf['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':tangent.nbytes});binary.extend(tangent.tobytes())
            accessor_index=len(gltf['accessors']);gltf['accessors'].append({'bufferView':view_index,'componentType':5126,'count':len(tangent),'type':'VEC4'});attrs['TANGENT']=accessor_index
    gltf['buffers'][0]['byteLength']=len(binary)
    encoded=json.dumps(gltf,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4);binary.extend(b'\0'*(-len(binary)%4))
    data=struct.pack('<III',0x46546c67,2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
    path.write_bytes(data);print(path.name,'mesh roots',mesh_roots,'zero slots',zeroed)


if __name__ == '__main__':
    for model in sorted(MODELS.glob('*.glb')):
        if model.name != 'fp_arms.glb': main(model)
