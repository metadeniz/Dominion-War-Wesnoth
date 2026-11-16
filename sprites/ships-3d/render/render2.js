const { chromium } = require('playwright');
const http=require('http'), fs=require('fs'), path=require('path');
const ROOT=__dirname, cfg=JSON.parse(fs.readFileSync(path.join(ROOT,'cfg.json'))), OUT=process.argv[2], EL=+(process.argv[3]||45);
const dirs=(process.argv[4]||'se,ne,n,nw,sw,s').split(','), H={e:0,ne:39,n:90,nw:141,w:180,sw:219,s:270,se:321};
const only=process.argv[5]?process.argv[5].split(','):null;
fs.mkdirSync(OUT,{recursive:true});
const types={'.html':'text/html','.js':'text/javascript','.png':'image/png','.obj':'text/plain'};
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0])); fs.readFile(f,(e,d)=>{ if(e){s.writeHead(404);return s.end();} s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'}); s.end(d);});}).listen(0, async()=>{
 const port=srv.address().port;
 const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage(); p.on('pageerror',e=>console.log('ERR',e.message)); p.on('console',m=>{ if(m.type()==='error') console.log('page:',m.text())});
 await p.goto(`http://localhost:${port}/page.html`); await p.waitForFunction(()=>window.ready,null,{timeout:60000});
 for (const [n,c] of Object.entries(cfg)) { if(only&&!only.includes(n)) continue; for (const d of dirs) {
   const url=await p.evaluate(([n,c,h,el])=>shot(n,c.tex,c.rot,h,c.size,el),[n,c,H[d],EL]);
   fs.writeFileSync(path.join(OUT,`${n}-${d}.png`),Buffer.from(url.split(',')[1],'base64')); } console.log('done',n); }
 await b.close(); srv.close();
});
