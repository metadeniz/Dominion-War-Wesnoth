// node try.js JOBS.json OUTDIR : JOBS=[{id,f,rot,size,el,hd,light,px}]
const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname; const J=JSON.parse(fs.readFileSync(process.argv[2])); const OUT=process.argv[3]; fs.mkdirSync(OUT,{recursive:true});
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':{'.html':'text/html','.js':'text/javascript'}[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>console.log('page:',m.text().slice(0,600)));
await p.goto(`http://localhost:${srv.address().port}/page3.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
for(const u of J){ const px=u.px||288; await p.evaluate(([px,sf])=>setFrame(px,sf),[px,1.6]);
  if(u.measure){ console.log(u.id, JSON.stringify(await p.evaluate(([u])=>measure(u.f,false,u.rot||[0,0,0]),[u]))); }
  const url=await p.evaluate(([u])=>{ window.LIGHTCFG=u.light||null; return shot(u.f,false,u.rot||[0,0,0],u.hd??321,u.size||1,u.el??45); },[u]);
  fs.writeFileSync(path.join(OUT,u.id+'.png'),Buffer.from(url.split(',')[1],'base64')); console.log('done',u.id); }
await b.close();srv.close();});
