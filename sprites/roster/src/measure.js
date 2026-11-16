const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;const types={'.html':'text/html','.js':'text/javascript','.png':'image/png','.obj':'text/plain'};
const R=JSON.parse(fs.readFileSync(process.argv[2]||'roster2.json'));
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:${srv.address().port}/page3.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
const out={};
for(const f of R) for(const u of f.units){ if(u.proc) continue;
  try{ out[u.id]=await p.evaluate(([u])=>measure(u.model||u.f,!u.f,u.rot||[0,0,0],u.c||u.tint),[u]); }catch(e){ out[u.id]={err:e.message}; } }
fs.writeFileSync('measure.json',JSON.stringify(out,null,1)); console.log('ok',Object.keys(out).length);
await b.close();srv.close();});
