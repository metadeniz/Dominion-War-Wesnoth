// node angles.js SPEC.json OUTDIR PX  -> renders each unit in SPEC at several camera angles
// SPEC: [{id, f|model, tex(bool, for model), rot, size, c}], views: [[name, heading, elevation], ...]
const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;const types={'.html':'text/html','.js':'text/javascript','.png':'image/png','.obj':'text/plain'};
const SPEC=JSON.parse(fs.readFileSync(process.argv[2])); const OUT=process.argv[3], PX=+process.argv[4];
const VIEWS=SPEC.views||[['game',321,45],['top',0,89.9],['side',0,0.5],['front',270,0.5],['rear',141,25]];
fs.mkdirSync(OUT,{recursive:true});
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message)); if(process.env.LOG) p.on('console',m=>console.log('LOG',m.text().slice(0,3000)));
await p.goto(`http://localhost:${srv.address().port}/page3.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
await p.evaluate(([px,sf])=>setFrame(px,sf),[PX,1.6]);
for(const u of SPEC.units){ for(const [vn,hd,el] of VIEWS){
  const url=await p.evaluate(([u,h,el])=>{ window.LIGHTCFG=u.light||null; return shot(u.model||u.f, u.f?false:!!u.tex, u.rot||[0,0,0],h,u.size||1,el,null,u.c||null); },[u,hd,el]);
  fs.writeFileSync(path.join(OUT,u.id+'_'+vn+'.png'),Buffer.from(url.split(',')[1],'base64')); } console.log('done',u.id); }
await b.close();srv.close();});
