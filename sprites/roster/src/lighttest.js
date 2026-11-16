// node lighttest.js ROSTER.json ID OUTDIR PX  -> renders one unit under several lighting set-ups (game view)
const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;const types={'.html':'text/html','.js':'text/javascript','.png':'image/png'};
const R=JSON.parse(fs.readFileSync(process.argv[2])); const ID=process.argv[3], OUT=process.argv[4], PX=+process.argv[5];
const LIGHTS=process.env.SET==='right2'?[['right-d',{hemi:0.45,dir:0.75,extra:[{dir:3.9,pos:[7,2.5,-0.5]}]}],['right-e',{hemi:0.4,dir:0.7,extra:[{dir:4.4,pos:[7,2.5,-0.5]}]}]]:process.env.SET==='right'?[['right-side',{hemi:0.5,dir:3.2,pos:[7,2.5,-0.5]}],['right-a',{hemi:0.6,dir:0.9,extra:[{dir:3.4,pos:[7,2.5,-0.5]}]}],['right-b',{hemi:0.8,dir:1.0,extra:[{dir:3.8,pos:[7,3.5,-0.5]}]}],['right-c',{hemi:0.9,dir:0.8,extra:[{dir:4.2,pos:[7,2.5,0.5]}]}]]:process.env.ONLY?[['default',{}],['overhead',{hemi:0.5,dir:3.2,pos:[0,8,0.4]}],['overhead-sameshadow',{hemi:0.5,dir:0.9,extra:[{dir:2.6,pos:[0,8,0.4]}]}]]:[['default',{}],['less-fill',{hemi:0.5,dir:3.0}],['overhead',{hemi:0.5,dir:3.2,pos:[0,8,0.4]}],['left-side',{hemi:0.5,dir:3.2,pos:[-7,2.5,0.5]}],['right-side',{hemi:0.5,dir:3.2,pos:[7,2.5,-0.5]}],['back-top',{hemi:0.5,dir:3.2,pos:[-1,6,-4]}]];
fs.mkdirSync(OUT,{recursive:true}); let u; for(const f of R) for(const x of f.units) if(x.id===ID) u=x;
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:${srv.address().port}/page3.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
await p.evaluate(([px,sf])=>setFrame(px,sf),[PX,1.6]);
for(const [n,cfg] of LIGHTS){ await p.evaluate(c=>{window.LIGHTCFG=c;},cfg);
  const url=await p.evaluate(([u])=>shot(u.model||u.f,!u.f,u.rot||[0,0,0],321,u.size||1,45,u.proc,u.c||u.tint),[u]);
  fs.writeFileSync(path.join(OUT,ID+'_'+n+'.png'),Buffer.from(url.split(',')[1],'base64')); console.log('done',n); }
await b.close();srv.close();});
