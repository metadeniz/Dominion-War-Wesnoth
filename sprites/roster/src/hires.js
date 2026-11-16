// node hires.js OUTDIR PX id1,id2  -> renders roster2 units at PX pixels (same framing as the 72px sprite)
const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;const types={'.html':'text/html','.js':'text/javascript','.png':'image/png','.obj':'text/plain'};
const R=JSON.parse(fs.readFileSync(process.env.RJSON||'roster2.json')); const OUT=process.argv[2], PX=+process.argv[3], only=process.argv[4].split(','); const EL=45, HD=321;
fs.mkdirSync(OUT,{recursive:true});
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:${srv.address().port}/page3.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
for(const f of R) for(const u of f.units){ if(!only.includes(u.id)) continue; const cv=u.canvas||72;
  await p.evaluate(([px,sf])=>setFrame(px,sf),[PX*cv/72,1.6*cv/72]);
  const url=await p.evaluate(([u,h,el])=>{ window.LIGHTCFG=u.light||null; return shot(u.model||u.f,!u.f,u.rot||[0,0,0],h,u.size||1,el,u.proc,u.c||u.tint); },[u,HD,EL]);
  fs.writeFileSync(path.join(OUT,u.id+'.png'),Buffer.from(url.split(',')[1],'base64')); }
await b.close();srv.close();});
