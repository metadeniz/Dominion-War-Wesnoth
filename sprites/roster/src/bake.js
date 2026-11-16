const { chromium } = require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;const types={'.html':'text/html','.js':'text/javascript','.png':'image/png'};
const OUT=process.argv[2];
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});s.end(d);});}).listen(0,async()=>{
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('page:',m.text().slice(0,300))});
await p.goto(`http://localhost:${srv.address().port}/bake.html`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
const o=await p.evaluate(cfg=>bake(cfg),{oldObj:'/dl/peregrine/x/f/fighter.obj',oldTex:'/dl/peregrine/x/textures/pfightertextures.png',newFbx:'/dl/peregrine2/x/source/peregrine.fbx',projW:1024,projH:1024,uvSize:2048});
fs.mkdirSync(OUT,{recursive:true});
for(const k of ['oldTop','oldBot','uv0','uv1']) fs.writeFileSync(path.join(OUT,k+'.png'),Buffer.from(o[k].split(',')[1],'base64'));
fs.writeFileSync(path.join(OUT,'boxes.json'),JSON.stringify({oldBox:o.oldBox,newBox:o.newBox}));
console.log(JSON.stringify({oldBox:o.oldBox,newBox:o.newBox}));
await b.close();srv.close();});
