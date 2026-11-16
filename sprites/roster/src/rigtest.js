// node rigtest.js ROSTER.json ID RIGS.json OUTDIR PX -> renders one unit (game view) under each named light rig in RIGS.json
const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;const types={'.html':'text/html','.js':'text/javascript','.png':'image/png'};
const R=JSON.parse(fs.readFileSync(process.argv[2])); const ID=process.argv[3], RIGS=JSON.parse(fs.readFileSync(process.argv[4])), OUT=process.argv[5], PX=+process.argv[6];
fs.mkdirSync(OUT,{recursive:true}); let u; for(const f of R) for(const x of f.units) if(x.id===ID) u=x;
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:${srv.address().port}/page3.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
const cv=u.canvas||72; await p.evaluate(([px,sf])=>setFrame(px,sf),[PX*cv/72,1.6*cv/72]);   // bigger canvas for ships like the Jem'Hadar battleship
for(const rig of RIGS){ const url=await p.evaluate(([u,c])=>{ window.LIGHTCFG=c; return shot(u.model||u.f,!u.f,u.rot||[0,0,0],321,u.size||1,45,u.proc,u.c||u.tint); },[u,rig.cfg]);
  fs.writeFileSync(path.join(OUT,rig.id+'.png'),Buffer.from(url.split(',')[1],'base64')); console.log('done',rig.id); }
await b.close();srv.close();});
