// node dbglights.js PATH... -> lights and cameras inside each loaded model
const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;const types={'.html':'text/html','.js':'text/javascript'};
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();
await p.goto(`http://localhost:${srv.address().port}/page3.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
for(const m of process.argv.slice(2)){ const r=await p.evaluate(async m=>{ const o=await window.loadFile(m); const L=[]; o.traverse(x=>{ if(x.isLight||x.isCamera) L.push(x.type+' '+(x.intensity??'')+' '+x.name); }); return L; },m); console.log(m.slice(0,50), JSON.stringify(r)); }
await b.close();srv.close();});
