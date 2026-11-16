// node passes.js PASSES.json OUTDIR PX [id1,id2|all]  -> renders each roster2 unit once per pass (one light at a time), for compositing
// PASSES.json: {name: LIGHTCFG}. Output OUTDIR/<id>/<name>.png at PX (times canvas/72).
const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;const types={'.html':'text/html','.js':'text/javascript','.png':'image/png','.obj':'text/plain'};
const R=JSON.parse(fs.readFileSync(process.env.RJSON||path.join(ROOT,'roster2.json'))); const PS=JSON.parse(fs.readFileSync(process.argv[2]));
const OUT=process.argv[3], PX=+process.argv[4], only=(process.argv[5]||'all').split(','); const EL=45, HD=321;
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:${srv.address().port}/page3.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
for(const f of R) for(const u of f.units){ if(!only.includes('all')&&!only.includes(u.id)) continue; const cv=u.canvas||72; const t0=Date.now();
  fs.mkdirSync(path.join(OUT,u.id),{recursive:true});
  await p.evaluate(([px,sf])=>setFrame(px,sf),[PX*cv/72,1.6*cv/72]);
  for(const [name,lc] of Object.entries(PS)){ const fn=path.join(OUT,u.id,name+'.png'); if(fs.existsSync(fn)) continue;
    const url=await p.evaluate(([u,lc,h,el])=>{ window.LIGHTCFG=lc; return shot(u.model||u.f,!u.f,u.rot||[0,0,0],h,u.size||1,el,u.proc,u.c||u.tint); },[u,lc,HD,EL]);
    fs.writeFileSync(fn,Buffer.from(url.split(',')[1],'base64')); }
  console.log(u.id, ((Date.now()-t0)/1000).toFixed(1)+'s'); }
await b.close();srv.close();});
