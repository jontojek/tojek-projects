document.getElementById('launch3d').addEventListener('click',async function(){
 this.disabled=true;this.textContent='Opening…';document.querySelector('.spinner').hidden=false;
 document.getElementById('loading').classList.add('started');
 document.getElementById('loadingText').textContent='Loading geometry, lights, and materials…';
 try{for(const src of ['vendor/babylon.js','vendor/babylonjs.loaders.min.js','app.js']){
 await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=src;script.onload=resolve;script.onerror=()=>reject(new Error('Could not load '+src));document.head.append(script);});
 }this.hidden=true;}catch(e){document.getElementById('loadingText').textContent=e.message+' — please reload to retry.';}
});