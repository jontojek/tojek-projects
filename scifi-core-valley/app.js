'use strict';
const $=id=>document.getElementById(id);
const MODEL='assets/scifi_core_valley_0001.glb';
let scene,engine,camera,pipeline,shadow,lights=[],baseIntensities=[],startCamera,original,dirty=false,toastTimer;
const look={exposure:1,environment:.65,rotation:0,background:'#17232f',shadows:true,shadowStrength:.65,bloom:true,bloomWeight:.18};
function notify(text){$('toast').textContent=text;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),4500);}
function markDirty(){dirty=true;$('savedState').textContent='Unsaved changes';}
function cameraState(){return {alpha:camera.alpha,beta:camera.beta,radius:camera.radius,target:camera.target.asArray(),fov:camera.fov};}
function setCamera(c){camera.inertialAlphaOffset=camera.inertialBetaOffset=camera.inertialRadiusOffset=0;camera.inertialPanningX=camera.inertialPanningY=0;camera.setTarget(BABYLON.Vector3.FromArray(c.target));camera.alpha=c.alpha;camera.beta=c.beta;camera.radius=c.radius;camera.fov=c.fov;syncCamera();}
function syncCamera(){if(!camera)return;$('fov').value=Math.round(camera.fov*180/Math.PI);$('fovOut').textContent=$('fov').value+'°';['X','Y','Z'].forEach((a,i)=>{if(document.activeElement!==$('target'+a))$('target'+a).value=camera.target.asArray()[i].toFixed(1);});}
function colorHex(c){return c.toGammaSpace().toHexString();}
function fromHex(hex){return BABYLON.Color3.FromHexString(hex).toLinearSpace();}
function snapshot(){return {version:1,asset:MODEL,look:{...look},camera:cameraState(),lights:lights.map((l,i)=>({id:i,name:l.name,type:l.getTypeID(),enabled:l.isEnabled(),intensity:l.intensity,color:colorHex(l.diffuse),position:l.position?.asArray()||null,direction:l.direction?.asArray()||null}))};}
function finite(n,min,max){return typeof n==='number'&&Number.isFinite(n)&&n>=min&&n<=max;}
function validate(s){
 const vec=(v,max)=>Array.isArray(v)&&v.length===3&&v.every(n=>finite(n,-max,max));
 const hex=v=>typeof v==='string'&&/^#[0-9a-f]{6}$/i.test(v);
 if(!s||s.version!==1||s.asset!==MODEL)throw Error('Choose a version 1 setup for this valley GLB.');
 const c=s.camera,k=s.look;
 if(!c||!finite(c.alpha,-1e5,1e5)||!finite(c.beta,.03,Math.PI-.03)||!finite(c.radius,3,1200)||!finite(c.fov,.2,1.6)||!vec(c.target,1000))throw Error('Invalid camera values.');
 if(!k||!finite(k.exposure,.1,3)||!finite(k.environment,0,3)||!finite(k.rotation,-180,180)||!hex(k.background)||typeof k.shadows!=='boolean'||typeof k.bloom!=='boolean'||!finite(k.shadowStrength,0,1)||!finite(k.bloomWeight,0,.8))throw Error('Invalid lighting values.');
 if(!Array.isArray(s.lights)||s.lights.length!==lights.length)throw Error('This setup has a different light rig.');
 s.lights.forEach((l,i)=>{if(l.id!==i||l.name!==lights[i].name||l.type!==lights[i].getTypeID()||typeof l.enabled!=='boolean'||!finite(l.intensity,0,1e9)||!hex(l.color)||(l.position!==null&&!vec(l.position,1000))||(l.direction!==null&&(!vec(l.direction,10)||Math.hypot(...l.direction)<.0001)))throw Error('Invalid scene light at index '+i);});
 return s;
}
function applyLook(){
 scene.imageProcessingConfiguration.exposure=look.exposure;scene.environmentIntensity=look.environment;scene.environmentTexture.rotationY=look.rotation*Math.PI/180;
 const c=BABYLON.Color3.FromHexString(look.background);scene.clearColor=new BABYLON.Color4(c.r,c.g,c.b,1);
 scene.shadowsEnabled=look.shadows;shadow?.setDarkness(1-look.shadowStrength);
 pipeline.bloomEnabled=look.bloom;pipeline.bloomWeight=look.bloomWeight;
 for(const id of ['exposure','environment','rotation','shadowStrength','bloomWeight']){$(id).value=look[id];$(id+'Out').textContent=id==='rotation'?look[id]+'°':Number(look[id]).toFixed(2);}
 $('background').value=look.background;$('shadows').checked=look.shadows;$('bloom').checked=look.bloom;
}
function applySetup(s){validate(s);Object.assign(look,s.look);s.lights.forEach((v,i)=>{const l=lights[i];l.intensity=v.intensity;l.diffuse=fromHex(v.color);l.setEnabled(v.enabled);if(l.position&&v.position)l.position.copyFromFloats(...v.position);if(l.direction&&v.direction)l.direction.copyFromFloats(...v.direction);});setCamera(s.camera);startCamera=structuredClone(s.camera);applyLook();syncLight();}
function selectedLight(){return lights[Number($('lightSelect').value)||0];}
function syncLight(){const l=selectedLight(),i=lights.indexOf(l);if(!l)return;$('lightEnabled').checked=l.isEnabled();const mult=l.intensity/baseIntensities[i];$('lightPower').max=Math.max(5,Math.ceil(mult));$('lightPower').value=mult;$('lightPowerOut').textContent=mult.toFixed(2)+'×';$('lightColor').value=colorHex(l.diffuse);$('directionControls').hidden=!l.direction;$('positionControls').hidden=l.getTypeID()===1;if(l.direction){const d=l.direction.normalizeToNew();const az=Math.atan2(d.z,d.x)*180/Math.PI;const el=Math.asin(-d.y)*180/Math.PI;$('azimuth').value=az;$('elevation').value=el;$('azimuthOut').textContent=az.toFixed(0)+'°';$('elevationOut').textContent=el.toFixed(0)+'°';}if(l.position)['X','Y','Z'].forEach((a,i)=>$('light'+a).value=l.position.asArray()[i].toFixed(1));}
function exportJSON(){const s=snapshot();validate(s);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(s,null,2)],{type:'application/json'}));a.download='valley-look-'+new Date().toISOString().replace(/[:.]/g,'-')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);notify('Exported a portable look and camera setup.');}
async function save(){exportJSON();startCamera=cameraState();return {downloaded:true};}

function bind(){
 for(const id of ['exposure','environment','rotation','shadowStrength','bloomWeight'])$(id).addEventListener('input',()=>{look[id]=Number($(id).value);applyLook();markDirty();});
 for(const id of ['shadows','bloom'])$(id).addEventListener('change',()=>{look[id]=$(id).checked;applyLook();markDirty();});
 $('background').oninput=()=>{look.background=$('background').value;applyLook();markDirty();};
 $('lightSelect').onchange=syncLight;
 $('lightPower').oninput=()=>{const i=Number($('lightSelect').value);lights[i].intensity=Number($('lightPower').value)*baseIntensities[i];$('lightPowerOut').textContent=Number($('lightPower').value).toFixed(2)+'×';markDirty();};
 $('lightEnabled').onchange=()=>{selectedLight().setEnabled($('lightEnabled').checked);markDirty();};
 $('lightColor').oninput=()=>{selectedLight().diffuse=fromHex($('lightColor').value);markDirty();};
 for(const id of ['azimuth','elevation'])$(id).oninput=()=>{const a=Number($('azimuth').value)*Math.PI/180,e=Number($('elevation').value)*Math.PI/180;selectedLight().direction.copyFromFloats(Math.cos(a)*Math.cos(e),-Math.sin(e),Math.sin(a)*Math.cos(e));syncLight();markDirty();};
 ['X','Y','Z'].forEach((a,i)=>{$('light'+a).onchange=()=>{const n=Number($('light'+a).value);if(!finite(n,-500,500)){syncLight();return;}selectedLight().position[['x','y','z'][i]]=n;markDirty();};$('target'+a).onchange=()=>{const n=Number($('target'+a).value);if(!finite(n,-500,500)){syncCamera();return;}const t=camera.target.clone();t[['x','y','z'][i]]=n;camera.setTarget(t);syncCamera();markDirty();};});
 $('fov').oninput=()=>{camera.fov=Number($('fov').value)*Math.PI/180;syncCamera();markDirty();};
 $('setCamera').onclick=()=>{startCamera=cameraState();markDirty();notify('Starting view set. Export look + view to keep it.');};
 $('resetCamera').onclick=()=>{setCamera(startCamera);notify('Returned to your starting view.');};
 $('overview').onclick=()=>{setCamera(original.camera);markDirty();};
 $('frameCore').onclick=()=>{setCamera({...original.camera,radius:140,target:[0,34,0]});markDirty();};
 $('save').onclick=()=>save().catch(console.error);$('export').onclick=exportJSON;
 $('import').onclick=()=>$('importFile').click();$('importFile').onchange=async()=>{try{const f=$('importFile').files[0];if(!f)return;if(f.size>131072)throw Error('Setup file is too large.');applySetup(JSON.parse(await f.text()));markDirty();notify('Setup loaded. Export to keep your setup.');}catch(e){notify(e.message);}finally{$('importFile').value='';}};
 $('factory').onclick=()=>{applySetup(structuredClone(original));markDirty();notify('Original look restored. Your downloaded files are unchanged.');};
 $('fullscreen').onclick=()=>{const p=document.querySelector('.viewport');(document.fullscreenElement?document.exitFullscreen():p.requestFullscreen()).catch(e=>notify(e.message));};
 $('renderCanvas').addEventListener('pointerdown',markDirty);$('renderCanvas').addEventListener('wheel',markDirty,{passive:true});
}
function registerTools(){const context=document.modelContext;if(!context?.registerTool)return;for(const t of [
 {name:'read_valley_setup',title:'Read current valley setup',description:'Read current lighting and camera from the local valley editor.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true},execute:()=>snapshot()},
 {name:'set_valley_exposure',title:'Adjust exposure',description:'Set the visible exposure slider. Does not save files.',inputSchema:{type:'object',properties:{exposure:{type:'number',minimum:.1,maximum:3}},required:['exposure'],additionalProperties:false},execute:({exposure})=>{if(!finite(exposure,.1,3))throw Error('Exposure outside range');look.exposure=exposure;applyLook();markDirty();return {exposure};}},
 {name:'save_valley_setup',title:'Download look and camera',description:'Download the current look and camera as a JSON file. Does not save to the website.',inputSchema:{type:'object',properties:{},additionalProperties:false},execute:save}
 ])try{Promise.resolve(context.registerTool(t)).catch(console.warn);}catch(e){console.warn(e);}}
async function boot(){try{
 if(!window.BABYLON||!BABYLON.Engine.isSupported())throw Error('WebGL is unavailable. Open this viewer in a browser with hardware acceleration.');
 engine=new BABYLON.Engine($('renderCanvas'),true,{preserveDrawingBuffer:true,stencil:true});engine.setHardwareScalingLevel(Math.max(1,window.devicePixelRatio/1.5));
 scene=new BABYLON.Scene(engine);scene.useRightHandedSystem=true;
 await BABYLON.SceneLoader.AppendAsync('assets/','scifi_core_valley_0001.glb',scene);
 lights=[...scene.lights];
 // glTF lights are parented to transform nodes. Expose world-space controls.
 // The source Blender export converted watts to photometric values with 683.
 // Start with a calibrated browser look; keep the original GLB untouched.
 for(const l of lights){if(l.parent){l.parent.computeWorldMatrix(true);const world=l.parent.getWorldMatrix();const p=l.position?BABYLON.Vector3.TransformCoordinates(l.position,world):null;const d=l.direction?BABYLON.Vector3.TransformNormal(l.direction,world).normalize():null;l.parent=null;if(p)l.position=p;if(d)l.direction=d;}l.intensity/=683;}
 baseIntensities=lights.map(l=>Math.max(l.intensity,.001));
 camera=new BABYLON.ArcRotateCamera('Look studio camera',0,1,280,new BABYLON.Vector3(0,24,-12),scene);camera.setPosition(new BABYLON.Vector3(145,132,205));camera.fov=.67;camera.minZ=.2;camera.maxZ=2000;camera.lowerRadiusLimit=3;camera.upperRadiusLimit=1200;camera.lowerBetaLimit=.04;camera.upperBetaLimit=Math.PI-.04;camera.wheelDeltaPercentage=.025;camera.panningSensibility=35;camera.attachControl($('renderCanvas'),true);scene.activeCamera=camera;
 const env=BABYLON.CubeTexture.CreateFromPrefilteredData('assets/studio.env',scene);scene.environmentTexture=env;
 scene.imageProcessingConfiguration.toneMappingEnabled=true;scene.imageProcessingConfiguration.toneMappingType=BABYLON.ImageProcessingConfiguration.TONEMAPPING_ACES;
 for(const m of scene.materials)if('maxSimultaneousLights' in m)m.maxSimultaneousLights=8;
 const sun=lights.find(l=>l.getTypeID()===1);if(sun){shadow=new BABYLON.ShadowGenerator(2048,sun);shadow.usePercentageCloserFiltering=true;shadow.filteringQuality=BABYLON.ShadowGenerator.QUALITY_MEDIUM;shadow.bias=.001;shadow.normalBias=.15;for(const m of scene.meshes)if(m.getTotalVertices()>0){m.receiveShadows=true;shadow.addShadowCaster(m,false);}}
 pipeline=new BABYLON.DefaultRenderingPipeline('Look studio finish',true,scene,[camera]);pipeline.samples=1;pipeline.fxaaEnabled=true;pipeline.bloomThreshold=1;pipeline.bloomKernel=48;pipeline.bloomScale=.5;
 lights.forEach((l,i)=>{const o=document.createElement('option');o.value=i;o.textContent=l.name;$('lightSelect').append(o);});
 startCamera=cameraState();applyLook();syncLight();syncCamera();original=snapshot();
 try{const r=await fetch('viewer-settings.json');if(r.ok){const data={settings:await r.json(),filename:"Artist’s starting setup"};if(data.settings){applySetup(data.settings);$('fileStatus').textContent=data.filename;$('savedState').textContent='Artist’s starting view';}else $('savedState').textContent='Original look';}else $('savedState').textContent='Original look';}catch(e){$('savedState').textContent='Original look';}
 bind();$('controls').inert=false;$('save').disabled=false;$('sceneStats').textContent=lights.length+' imported lights · '+scene.meshes.filter(m=>m.getTotalVertices()>0).length+' mesh groups';
 engine.runRenderLoop(()=>scene.render());await scene.whenReadyAsync();$('loading').style.display='none';registerTools();
 let last=performance.now();scene.onAfterRenderObservable.add(()=>{if(performance.now()-last>750){$('fps').textContent=Math.round(engine.getFps())+' FPS';syncCamera();last=performance.now();}});
 window.addEventListener('resize',()=>engine.resize());document.addEventListener('fullscreenchange',()=>engine.resize());
 }catch(e){console.error(e);$('loadingText').textContent=e.message;$('loading').querySelector('h2').textContent='Could not open the scene';$('loading').querySelector('.spinner').style.display='none';}}
boot();
