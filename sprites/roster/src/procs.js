// Simple stand-in ships built from primitives. Forward = +X, up = +Y, lateral = Z.
import * as T from 'three';
const texCache={};
function panelTex(seed=1){ if(texCache[seed]) return texCache[seed];
  const c=document.createElement('canvas'); c.width=c.height=256; const g=c.getContext('2d');
  let s=seed*9301+49297; const rnd=()=>((s=(s*9301+49297)%233280)/233280);
  g.fillStyle='#d8d8d8'; g.fillRect(0,0,256,256);
  for(let i=0;i<140;i++){ const v=200+Math.floor(rnd()*55); g.fillStyle=`rgb(${v},${v},${v})`; g.fillRect(rnd()*256,rnd()*256,8+rnd()*40,6+rnd()*30); }
  g.strokeStyle='rgba(70,70,70,0.55)'; g.lineWidth=1; for(let i=0;i<40;i++){ g.beginPath(); const x=rnd()*256,y=rnd()*256; g.moveTo(x,y); rnd()>.5?g.lineTo(x+20+rnd()*60,y):g.lineTo(x,y+20+rnd()*60); g.stroke(); }
  g.fillStyle='rgba(40,40,40,.6)'; for(let i=0;i<60;i++) g.fillRect(rnd()*256,rnd()*256,2,2);
  const t=new T.CanvasTexture(c); t.wrapS=t.wrapT=T.RepeatWrapping; t.repeat.set(1.5,1.5); t.colorSpace=T.SRGBColorSpace; return texCache[seed]=t; }
const M=(hex,seed=1,o={})=>new T.MeshStandardMaterial({color:hex,map:panelTex(seed),roughness:.6,metalness:.25,side:T.DoubleSide,...o});
const E=(hex,i=2)=>new T.MeshStandardMaterial({color:hex,emissive:hex,emissiveIntensity:i,roughness:.4});
function put(g,geo,mat,p=[0,0,0],r=[0,0,0],s=[1,1,1]){ const m=new T.Mesh(geo,mat); m.position.set(...p); m.rotation.set(...r); m.scale.set(...s); m.castShadow=true; m.receiveShadow=true; g.add(m); return m; }
// flat plate from top-view outline [[x,z],...]
function slab(g,mat,pts,th=.2,y=0,bev=.06,mirror=false){ const sh=new T.Shape(); pts.forEach(([x,z],i)=>i?sh.lineTo(x,z):sh.moveTo(x,z));
  const geo=new T.ExtrudeGeometry(sh,{depth:th,bevelEnabled:bev>0,bevelThickness:bev,bevelSize:bev,bevelSegments:2,curveSegments:8});
  geo.rotateX(Math.PI/2); geo.translate(0,y+th/2,0); const uv=geo.attributes.uv; for(let i=0;i<uv.count;i++) uv.setXY(i,uv.getX(i)*.35,uv.getY(i)*.35);
  return put(g,geo,mat); }
const symPts=(half)=>{ const a=half.map(([x,z])=>[x,z]); const b=half.slice().reverse().map(([x,z])=>[x,-z]); return a.concat(b.filter(([x,z])=>z!==0||true)); };
function saucer(g,mat,x,y,rx,rz,h=.22){ const pts=[[0,h],[.5,h*.85],[.85,h*.45],[1,.04],[1,-.04],[.85,-h*.35],[.4,-h*.6],[0,-h*.65]].map(([a,b])=>new T.Vector2(a,b));
  const geo=new T.LatheGeometry(pts.reverse(),32); return put(g,geo,mat,[x,y,0],[0,0,0],[rx,1,rz]); }
function capsule(g,mat,x,y,z,len,rad,sy=1){ const geo=new T.CapsuleGeometry(rad,len,6,14); geo.rotateZ(Math.PI/2); return put(g,geo,mat,[x,y,z],[0,0,0],[1,sy,1]); }
function nacelle(g,mat,x,y,z,len,rad,glow=0x5ec8ff,front=0xff4b37){ capsule(g,mat,x,y,z,len,rad,.85);
  put(g,new T.BoxGeometry(len*.8,rad*.5,rad*.5),E(glow),[x-len*.05,y,z-Math.sign(z||1)*rad*.75]);
  put(g,new T.SphereGeometry(rad*.62,12,8),E(front),[x+len/2+rad*.55,y,z]); }
function box(g,mat,p,s,r=[0,0,0]){ return put(g,new T.BoxGeometry(...s),mat,p,r); }
function glow(g,hex,p,r=.08,i=2.5){ return put(g,new T.SphereGeometry(r,12,8),E(hex,i),p); }
function pylon(g,mat,a,b,w=.1,h=.06){ const A=new T.Vector3(...a),B=new T.Vector3(...b),d=B.clone().sub(A),L=d.length();
  const m=put(g,new T.BoxGeometry(L,h,w),mat,A.clone().add(B).multiplyScalar(.5).toArray()); m.quaternion.setFromUnitVectors(new T.Vector3(1,0,0),d.normalize()); return m; }
const both=f=>{f(1);f(-1);};
const S=(pts)=>{ // mirror a half outline (z>=0, from nose to tail) into a closed outline
  const back=pts.slice().reverse().map(([x,z])=>[x,-z]); return pts.concat(back); };

const FED=0xc4c9d1, KL=0x66745a, JH=0x9690b0, CA=0xb59d6e, BR=0x6f7a52, MQ=0xa3968a;
export const P={
 // ---------- Federation
 'fed-fighter':g=>{ const m=M(FED,2); slab(g,m,S([[1.3,0],[.2,.35],[-.9,.75],[-1.1,.7],[-1,0.0]]),.18); both(s=>nacelle(g,m,-.45,.05,.62*s,.9,.11)); glow(g,0xff7a3a,[-1.08,.1,0],.09); },
 'fed-saber':g=>{ const m=M(FED,3); slab(g,m,S([[1.4,0],[1.2,.6],[.6,1.05],[-.2,1.25],[-.6,1.05],[-.5,.4],[-.8,0]]),.16,.05); box(g,m,[.15,.22,0],[.9,.16,.6]); both(s=>nacelle(g,m,-.85,.08,1.15*s,1.4,.14)); glow(g,0xff7a3a,[-.82,.1,0],.08);},
 'fed-oberth':g=>{ const m=M(FED,4); saucer(g,m,.55,.35,1.05,1.05,.2); both(s=>{nacelle(g,m,-.55,.32,.62*s,2.1,.17);}); box(g,m,[-.7,-.35,0],[1.6,.25,.35]); pylon(g,m,[-.2,.2,0],[-.6,-.3,0],.2);},
 'fed-olympic':g=>{ const m=M(FED,5); put(g,new T.SphereGeometry(.9,24,16),m,[.85,0,0],[0,0,0],[1,.75,1]); capsule(g,m,-.6,0,0,1.8,.34); both(s=>{ nacelle(g,m,-1.1,.25,.85*s,1.6,.16); pylon(g,m,[-.8,0,.2*s],[-1.0,.25,.8*s],.18);}); box(g,E(0xff3030,1.2),[.85,.68,0],[.8,.03,.14]); box(g,E(0xff3030,1.2),[.85,.68,0],[.14,.03,.8]); },
 'fed-olympic-refit':g=>{ P['fed-olympic'](g); const m=M(FED,6); both(s=>{ capsule(g,m,-.3,-.05,.55*s,1.0,.22); }); put(g,new T.TorusGeometry(.95,.07,8,32),m,[.85,0,0],[Math.PI/2,0,0]); },
 'fed-steamrunner':g=>{ const m=M(FED,7); slab(g,m,S([[1.3,0],[1.15,.7],[.6,1.2],[0,1.35],[-.4,1.2],[-.6,.5],[-.9,0]]),.2,.05); both(s=>nacelle(g,m,-.55,.12,1.35*s,1.9,.17)); slab(g,m,S([[-.6,0],[-.7,1.3],[-1.4,1.35],[-1.4,0]]),.08,.12,.03); glow(g,0xff7a3a,[-.9,.1,0],.08);},
 'fed-nova':g=>{ const m=M(FED,8); saucer(g,m,.55,.15,1.1,.95,.25); slab(g,m,S([[.2,0],[.1,.55],[-1.1,.45],[-1.3,0]]),.35,-.1); both(s=>nacelle(g,m,-.95,-.05,.75*s,1.3,.15)); box(g,M(0x8fd0ff,8),[1.15,.05,0],[.25,.15,.6]);},
 'fed-nebula':g=>{ const m=M(FED,9); saucer(g,m,.55,.1,1.35,1.7,.22); capsule(g,m,-1.0,-.15,0,1.3,.3); both(s=>{ nacelle(g,m,-1.25,-.1,1.25*s,1.9,.16); pylon(g,m,[-.9,-.15,.25*s],[-1.1,-.1,1.15*s],.2);}); both(s=>pylon(g,m,[-.9,.1,.3*s],[-1.4,.6,.5*s],.12)); slab(g,m,S([[-.9,0],[-1.1,.9],[-1.9,.8],[-2.0,0]]),.12,.6); box(g,E(0xff4b37,1.5),[-1.95,.68,0],[.08,.06,.6]); },
 'fed-akira':g=>{ const m=M(FED,10); saucer(g,m,.6,.1,1.2,1.45,.2); both(s=>{ box(g,m,[-.8,.0,.7*s],[1.6,.3,.35]); nacelle(g,m,-1.3,-.15,1.25*s,1.3,.15); pylon(g,m,[-1.1,-.05,.8*s],[-1.2,-.12,1.15*s],.25);}); box(g,m,[-1.25,.45,0],[.5,.25,1.9]); both(s=>box(g,m,[-1.25,.25,.85*s],[.4,.4,.15])); },
 'fed-prometheus':g=>{ const m=M(FED,11); slab(g,m,S([[2.0,0],[1.4,.35],[-.2,.95],[-1.6,1.05],[-1.8,.7],[-1.6,0]]),.32,0,.08); box(g,m,[-.2,.38,0],[2.0,.18,.35]); both(s=>nacelle(g,m,-.85,.05,1.0*s,1.5,.13)); glow(g,0xff7a3a,[-1.62,.15,0],.1); },
 'fed-intrepid':g=>{ const m=M(FED,12); slab(g,m,S([[1.7,0],[1.4,.55],[.7,.85],[0,.8],[-.3,.5],[-.5,0]]),.22,.15,.08); capsule(g,m,-.9,0,0,1.3,.28); both(s=>{ nacelle(g,m,-1.25,.3,1.05*s,1.5,.13); pylon(g,m,[-.9,.05,.2*s],[-1.1,.3,1.0*s],.22);}); glow(g,0x5ec8ff,[.9,.05,0],.12);},
 // ---------- Klingon
 'kl-ktinga':g=>{ const m=M(KL,13); put(g,new T.SphereGeometry(.42,18,12),m,[1.65,0,0],[0,0,0],[1.2,.7,1]); box(g,m,[.65,.0,0],[1.6,.16,.2]); slab(g,m,S([[0,0],[-.2,.45],[-1.3,.5],[-1.5,0]]),.3,-.05); slab(g,m,S([[-.35,.3],[-.7,1.6],[-1.1,1.6],[-1.2,.3]]),.08,-.15,.03); both(s=>nacelle(g,m,-1.0,-.25,1.65*s,1.2,.13,0xff5a2a,0xff5a2a)); glow(g,0x7cff6a,[2.05,0,0],.08); },
 'kl-d7':g=>{ const m=M(0x7a7462,14); put(g,new T.SphereGeometry(.4,18,12),m,[1.5,0,0],[0,0,0],[1.15,.7,1]); box(g,m,[.6,0,0],[1.4,.15,.18]); slab(g,m,S([[0,0],[-.2,.42],[-1.2,.45],[-1.4,0]]),.28,-.05); slab(g,m,S([[-.35,.3],[-.7,1.5],[-1.05,1.5],[-1.15,.3]]),.08,-.15,.03); both(s=>nacelle(g,m,-.95,-.25,1.55*s,1.1,.13,0xff5a2a,0xff5a2a)); },
 'kl-assault':g=>{ const m=M(KL,15); slab(g,m,S([[1.0,0],[.6,.75],[-1.0,.85],[-1.3,.4],[-1.2,0]]),.45,0,.08); both(s=>{ box(g,m,[1.2,0,.4*s],[.8,.18,.18]); glow(g,0x7cff6a,[1.62,0,.4*s]);}); glow(g,0xff5a2a,[-1.3,.1,0],.12); box(g,M(0x4a5540,15),[-.2,.38,0],[1.2,.2,.6]); },
 'kl-scout':g=>{ const m=M(KL,16); capsule(g,m,.1,0,0,2.2,.25,.7); slab(g,m,S([[.2,0],[-.6,1.1],[-1.0,1.15],[-.9,0]]),.08,-.02,.03); put(g,new T.ConeGeometry(.25,.5,12),m,[1.55,0,0],[0,0,-Math.PI/2]); glow(g,0xff5a2a,[-1.25,0,0],.1); both(s=>glow(g,0x7cff6a,[-.95,0,1.13*s]));},
 'kl-boarding':g=>{ const m=M(KL,17); slab(g,m,S([[1.6,0],[1.4,.9],[.6,.7],[-1.0,1.0],[-1.5,.5],[-1.4,0]]),.55,0,.1); both(s=>{ box(g,m,[1.75,0,.7*s],[.7,.25,.25]); box(g,m,[2.05,0,.55*s],[.15,.25,.35]); nacelle(g,m,-.8,-.2,1.25*s,1.3,.16,0xff5a2a,0xff5a2a);}); box(g,M(0x4a5540,17),[-.1,.45,0],[1.8,.25,.7]); },
 // ---------- Dominion Alliance
 'ca-hideki':g=>{ const m=M(CA,18); slab(g,m,S([[1.3,0],[1.1,.5],[.2,.45],[-.5,.9],[-1.1,.8],[-.7,.25],[-1.0,0]]),.25,0,.06); glow(g,0xffb04a,[1.3,.12,0],.1); both(s=>glow(g,0xffb04a,[-1.0,.1,.75*s],.07)); },
 'ca-scout':g=>{ const m=M(CA,19); put(g,new T.SphereGeometry(.45,18,12),m,[1.2,0,0],[0,0,0],[.8,.4,1.2]); slab(g,m,S([[.9,0],[.6,.22],[-1.5,.18],[-1.7,0]]),.2); both(s=>slab(g,m,[[-.5,.15*s],[-1.2,.75*s],[-1.5,.7*s],[-1.2,.15*s]],.08,0,.03)); glow(g,0xffb04a,[1.55,0,0],.09); },
 'ca-obsidian':g=>{ const m=M(0x6a655d,20); put(g,new T.SphereGeometry(.6,18,12),m,[1.1,0,0],[0,0,0],[.8,.35,1.5]); slab(g,m,S([[.8,0],[.5,.3],[-1.8,.22],[-2.0,0]]),.25); both(s=>slab(g,m,[[-.3,.2*s],[-1.4,1.0*s],[-1.8,.95*s],[-1.3,.2*s]],.08,0,.03)); glow(g,0xffb04a,[1.6,0,0],.1); box(g,E(0xffb04a,1.4),[-.6,.2,0],[1.6,.03,.06]); },
 'ca-dread':g=>{ const m=M(CA,21); put(g,new T.SphereGeometry(.9,22,14),m,[1.0,0,0],[0,0,0],[.7,.35,1.7]); slab(g,m,S([[.6,0],[.3,.5],[-1.9,.45],[-2.1,0]]),.4,0,.1); both(s=>{ slab(g,m,[[-.2,.4*s],[-1.1,1.6*s],[-1.6,1.6*s],[-1.4,.4*s]],.12,0,.04); glow(g,0xffb04a,[-1.6,0,1.6*s],.09);}); glow(g,0xffb04a,[1.55,0,0],.14); box(g,M(0x8d7a55,21),[-.7,.4,0],[1.2,.3,.5]); },
 'br-frigate':g=>{ const m=M(BR,22); slab(g,m,S([[1.0,0],[.6,.35],[-1.0,.45],[-1.3,0]]),.4,0,.12); both(s=>slab(g,m,[[.4,.3*s],[1.2,.75*s],[1.4,.95*s],[.7,1.05*s],[-.7,.75*s],[-.6,.35*s]],.15,0,.05)); glow(g,0xb6ff4a,[1.0,.15,0],.11); both(s=>glow(g,0xb6ff4a,[1.35,0,.92*s],.07)); },
 'br-warship':g=>{ const m=M(BR,23); slab(g,m,S([[1.5,0],[.9,.45],[-1.3,.55],[-1.7,0]]),.45,0,.14); both(s=>{ slab(g,m,[[.6,.4*s],[1.6,.95*s],[1.8,1.2*s],[.9,1.35*s],[-1.1,.95*s],[-.9,.45*s]],.16,0,.05); slab(g,m,[[-1.0,.4*s],[-1.6,.9*s],[-1.9,.85*s],[-1.5,.3*s]],.1,.15,.04); glow(g,0xb6ff4a,[1.75,0,1.17*s],.08);}); glow(g,0xb6ff4a,[1.5,.17,0],.13); box(g,M(0x535c3e,23),[-.3,.4,0],[1.4,.22,.5]); },
 'br-heavy':g=>{ P['br-warship'](g); const m=M(BR,24); slab(g,m,S([[2.1,0],[1.6,.25],[1.0,.25],[1.0,0]]),.25,.1,.08); both(s=>slab(g,m,[[-.4,1.2*s],[-.2,1.8*s],[-1.2,1.7*s],[-1.3,1.0*s]],.14,0,.05)); glow(g,0xb6ff4a,[2.1,.2,0],.12); },
 'jh-battleship':g=>{ const m=M(JH,25); slab(g,m,S([[2.0,0],[1.5,.5],[.4,.75],[-1.7,.9],[-2.0,.4],[-1.9,0]]),.45,0,.12); both(s=>{ slab(g,m,[[.6,.6*s],[1.6,1.2*s],[2.0,1.7*s],[1.3,1.85*s],[-.2,1.4*s],[-.8,.8*s]],.18,0,.05); slab(g,m,[[-.6,.8*s],[.2,2.0*s],[-.4,2.1*s],[-1.6,1.1*s]],.14,-.12,.05); glow(g,0xe6a6ff,[1.95,0,1.72*s],.08); glow(g,0xe6a6ff,[.15,-.1,2.0*s],.08);}); box(g,E(0xc779ff,1.5),[0,.37,0],[3.2,.04,.12]); glow(g,0xc779ff,[2.0,.15,0],.16); box(g,M(0x7d7896,25),[-.5,.42,0],[1.8,.25,.8]); },
 // ---------- Non-Aligned Worlds
 'mq-peregrine':g=>{ const m=M(MQ,26); capsule(g,m,0,0,0,1.8,.24,.8); slab(g,m,S([[.6,0],[-.1,.85],[-.5,.9],[-.3,0]]),.07,0,.03); both(s=>nacelle(g,m,-.25,0,.95*s,.9,.11,0xffb04a,0xff4b37)); put(g,new T.ConeGeometry(.24,.5,12),m,[1.4,0,0],[0,0,-Math.PI/2]);},
 'bj-lightship':g=>{ const m=M(0x9b7b55,27); capsule(g,m,-.4,0,0,1.2,.2,.8); const sail=new T.MeshStandardMaterial({color:0xffd27a,emissive:0x8a5a10,emissiveIntensity:.6,roughness:.5,metalness:.4,side:T.DoubleSide});
   [[.6,0,0],[.2,0,1],[.2,0,-1]].forEach(([x,y,k])=>{ const sh=new T.Shape(); sh.moveTo(0,0); sh.lineTo(.7,.25*k||.0001); sh.lineTo(.9,1.3*(k||1)); sh.lineTo(-.6,1.2*(k||1)); const geo=new T.ShapeGeometry(sh); const mm=put(g,geo,sail,[x-0.6,.25,0],[k?-Math.PI/2:0,0,0]); if(!k){ mm.rotation.set(-Math.PI/2.4,0,0);} });
   both(s=>pylon(g,m,[-.4,0,0],[.4,.3,1.2*s],.04,.04)); pylon(g,m,[-.4,0,0],[.2,1.0,0],.04,.04);},
 'pk-clunker':g=>{ const m=M(0x8c8570,28), m2=M(0x6b6a5c,29); box(g,m,[0,0,0],[1.6,.5,.9],[0,.1,0]); box(g,m2,[.9,.05,.1],[.7,.35,.6],[0,-.2,0]); box(g,m2,[-.9,0,-.2],[.6,.6,.6],[.1,.3,0]); capsule(g,m,-.7,.0,.7,1.1,.18); capsule(g,m2,-.6,.1,-.75,.9,.2); box(g,m,[.2,.38,.0],[.5,.3,.4],[0,.4,0]); glow(g,0xffb04a,[-1.25,0,-.2],.12); glow(g,0x5ec8ff,[1.25,.05,.1],.08);},
 'bj-raider':g=>{ const m=M(0xa08a64,30); put(g,new T.SphereGeometry(.5,18,12),m,[.3,0,0],[0,0,0],[1.5,.6,.9]); both(s=>{ capsule(g,m,-.3,-.05,.85*s,1.3,.2); pylon(g,m,[.1,0,.3*s],[-.2,-.05,.75*s],.35,.08); glow(g,0xffb04a,[-1.1,-.05,.85*s],.12);}); box(g,M(0x6a2a22,30),[.6,.25,0],[.5,.1,.3]); },
 'bj-interceptor':g=>{ const m=M(0xa08a64,31); slab(g,m,S([[1.5,0],[1.0,.35],[-.2,.5],[-1.2,.45],[-1.3,0]]),.3,0,.08); both(s=>{ capsule(g,m,-.4,0,.9*s,1.6,.2); slab(g,m,[[.4,.35*s],[-.1,.9*s],[-.9,.9*s],[-.8,.4*s]],.08,0,.03); glow(g,0xffb04a,[-1.4,0,.9*s],.12); glow(g,0xff4b37,[.55,0,.9*s],.07);}); box(g,M(0x6a2a22,31),[.4,.25,0],[.8,.1,.3]);},
 'bj-assault':g=>{ const m=M(0xa08a64,32); slab(g,m,S([[1.7,0],[1.4,.6],[.2,.8],[-1.6,.7],[-1.8,0]]),.5,0,.12); both(s=>{ capsule(g,m,-.6,-.1,1.15*s,2.0,.26); pylon(g,m,[-.4,0,.6*s],[-.6,-.1,1.0*s],.4,.1); glow(g,0xffb04a,[-1.9,-.1,1.15*s],.14);}); box(g,M(0x6a2a22,32),[-.2,.45,0],[1.6,.2,.6]); glow(g,0xff7a3a,[1.7,.15,0],.12);},
 'bj-transport':g=>{ const m=M(0xc7b89a,33); box(g,m,[0,0,0],[2.6,.5,.7]); box(g,m,[1.4,.05,0],[.5,.4,.55],[0,0,0]); both(s=>{ capsule(g,m,-.6,0,.55*s,1.2,.16); glow(g,0xffb04a,[-1.35,0,.55*s],.1);}); box(g,E(0xb8302a,.6),[0,.26,0],[2.2,.02,.15]); },
 'bj-vedek':g=>{ P['bj-transport'](g); const m=M(0xc7b89a,34); box(g,m,[-.2,.35,0],[1.4,.25,.5]); box(g,E(0xffd27a,1.2),[-.2,.49,0],[1.2,.02,.1]); both(s=>box(g,m,[.2,0,.55*s],[.9,.35,.3])); },
 'fe-marauder':g=>{ const m=M(0xb07a45,35); const sh=[]; for(let i=0;i<=20;i++){ const a=-Math.PI*.85+i*(Math.PI*1.7/20); sh.push([Math.cos(a)*1.5,Math.sin(a)*1.5]); } for(let i=20;i>=0;i--){ const a=-Math.PI*.75+i*(Math.PI*1.5/20); sh.push([Math.cos(a)*.9-.15,Math.sin(a)*.9]); }
   slab(g,m,sh,.22,0,.08); slab(g,m,S([[1.9,0],[1.5,.3],[.2,.35],[0,0]]),.3,.1,.1); glow(g,0x7cff6a,[1.9,.2,0],.1); both(s=>glow(g,0xffb04a,[-1.25,.05,.75*s],.1)); },
 'fe-daimon':g=>{ P['fe-marauder'](g); const m=M(0xc08a50,36); box(g,m,[.6,.45,0],[.9,.2,.4]); both(s=>capsule(g,m,-.2,.05,1.55*s,1.0,.15)); },
 'or-interceptor':g=>{ const m=M(0x3f7a55,37); slab(g,m,S([[1.8,0],[.6,.25],[-.3,.75],[-1.1,.85],[-1.0,.25],[-1.2,0]]),.2,0,.06); both(s=>{ slab(g,m,[[1.1,.12*s],[.8,.5*s],[.5,.45*s],[.6,.15*s]],.05,.05,.02); glow(g,0xff4b37,[-1.1,0,.8*s],.08);}); glow(g,0xffd27a,[.5,.2,0],.1); },
 'or-corsair':g=>{ P['or-interceptor'](g); const m=M(0x356b48,38); both(s=>capsule(g,m,-.4,-.05,1.0*s,1.2,.16)); box(g,m,[-.1,.25,0],[1.0,.15,.35]); },
 'na-raider':g=>{ const m=M(0x6b5d50,39); slab(g,m,S([[1.4,0],[.8,.3],[.3,.9],[-.1,.55],[-1.2,.8],[-1.0,.25],[-1.3,0]]),.3,0,.04); both(s=>{ put(g,new T.ConeGeometry(.12,.6,6),m,[.45,0,1.05*s],[0,0,-Math.PI/2]); glow(g,0xff4b37,[-1.2,0,.75*s],.09);}); glow(g,0xffb04a,[1.4,.1,0],.08);},
 'na-marauder':g=>{ const m=M(0x5e5246,40); slab(g,m,S([[1.8,0],[1.1,.4],[.5,1.2],[0,.7],[-1.5,1.1],[-1.3,.3],[-1.6,0]]),.4,0,.05); both(s=>{ put(g,new T.ConeGeometry(.14,.8,6),m,[.7,0,1.35*s],[0,0,-Math.PI/2]); put(g,new T.ConeGeometry(.12,.7,6),m,[-1.0,0,1.25*s],[0,0,-Math.PI/2]); glow(g,0xff4b37,[-1.5,0,1.05*s],.1);}); box(g,m,[-.2,.35,0],[1.2,.2,.5]); },
 'th-vessel':g=>{ const c=new T.MeshStandardMaterial({color:0xff8a3a,emissive:0x8a2a00,emissiveIntensity:.9,roughness:.25,metalness:.6,flatShading:true});
   slab(g,c,S([[1.5,0],[-.3,.75],[-1.1,.4],[-.8,0]]),.25,0,0); put(g,new T.OctahedronGeometry(.45),c,[-.2,.25,0],[0,0,0],[1.6,.6,1]); glow(g,0xffe08a,[.4,.2,0],.12,3); },
 'th-spinner':g=>{ P['th-vessel'](g); const w=E(0xffb84a,2.5); both(s=>{ const c=new T.Group(); P['th-vessel'](c); c.scale.setScalar(.45); c.position.set(-.9,0,1.25*s); g.add(c); pylon(g,w,[.6,.1,0],[-.9,.05,1.25*s],.03,.03); pylon(g,w,[-.9,.1,0],[-.9,.05,1.25*s],.03,.03); }); },
 'th-lattice':g=>{ const w=E(0xffb84a,2.5); const pts=[]; for(let i=0;i<6;i++){ const a=i*Math.PI/3; pts.push([Math.cos(a)*1.5,Math.sin(a)*1.5]); }
   pts.forEach(([x,z],i)=>{ const c=new T.Group(); P['th-vessel'](c); c.scale.setScalar(.45); c.position.set(x,0,z); c.rotation.y=-Math.atan2(z,x)+Math.PI/2; g.add(c); const [x2,z2]=pts[(i+1)%6]; pylon(g,w,[x,.05,z],[x2,.05,z2],.03,.03); pylon(g,w,[x,.05,z],[0,.05,0],.025,.025); }); const c=new T.Group(); P['th-vessel'](c); c.scale.setScalar(.7); g.add(c); },
 'gn-cruiser':g=>{ const m=M(0x6d6a3e,41); put(g,new T.SphereGeometry(.9,20,14),m,[-.2,0,0],[0,0,0],[1.6,.5,1.0]); put(g,new T.SphereGeometry(.45,16,12),m,[1.4,0,0],[0,0,0],[1.4,.5,.9]); both(s=>{ capsule(g,M(0x5a5634,41),-.6,-.1,1.05*s,1.6,.25); glow(g,0xff7a3a,[-1.5,-.1,1.05*s],.12);}); glow(g,0x7cff6a,[2.0,0,0],.1); box(g,M(0x4c4a2c,41),[-.2,.42,0],[1.6,.15,.4]); },
 'tl-warship':g=>{ const m=M(0x8a8a86,42); slab(g,m,S([[1.6,0],[.9,.3],[.2,.35],[-.3,1.1],[-.8,1.15],[-.7,.35],[-1.4,.4],[-1.6,0]]),.3,0,.05); both(s=>glow(g,0xff4b37,[-.75,0,1.12*s],.08)); box(g,M(0x6b6b66,42),[-.2,.3,0],[1.4,.18,.4]); glow(g,0xffb04a,[1.6,.1,0],.09); },
};
