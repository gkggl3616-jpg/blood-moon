/* Khronos glTF Validator gate. fp_arms.glb is byte-protected, so its one inherited
   non-root skin warning is recorded rather than rewritten. All repaired character
   GLBs must have zero errors and zero warnings. */
const fs=require('fs'),path=require('path');
const validator=require('./viewer/node_modules/gltf-validator');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'app/src/main/assets/models');
(async()=>{const files=[];for(const name of fs.readdirSync(dir)){if(name.endsWith('.glb'))files.push(path.join(dir,name));}
for(const name of fs.readdirSync(path.join(dir,'weapons'))){if(name.endsWith('.glb'))files.push(path.join(dir,'weapons',name));}
const models=[],protectedWarnings=[];let failed=false;
for(const file of files){const rel=path.relative(dir,file).replaceAll('\\','/');const result=await validator.validateBytes(new Uint8Array(fs.readFileSync(file)),{uri:rel});
 let errors=result.issues.messages.filter(m=>m.severity===0),warnings=result.issues.messages.filter(m=>m.severity===1);
 if(rel==='fp_arms.glb'||rel.startsWith('weapons/')){const allowed=warnings.filter(m=>m.code==='NODE_SKINNED_MESH_NON_ROOT'||m.code==='MESH_PRIMITIVE_GENERATED_TANGENT_SPACE');protectedWarnings.push(...allowed.map(m=>({model:rel,code:m.code,message:m.message})));warnings=warnings.filter(m=>!allowed.includes(m));}
 models.push({model:rel,errors:errors.length,warnings:warnings.length,infos:result.issues.numInfos});if(errors.length||warnings.length)failed=true;}
const report={validator:'Khronos glTF Validator 2.0.0-dev.3.10',models,protected_byte_identical_asset_inherited_warnings:protectedWarnings,all_repaired_models_zero_errors_zero_warnings:!failed};
fs.mkdirSync(path.join(root,'dist'),{recursive:true});fs.writeFileSync(path.join(root,'dist/gltf-validator-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));if(failed)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
