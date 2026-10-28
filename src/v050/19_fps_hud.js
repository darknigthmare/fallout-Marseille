/* Presentation only: every value still comes from the normal game HUD. */
const MistralFpsHud=(()=>{
 const finite=(n,d=0)=>typeof n==='number'&&Number.isFinite(n)?n:d;
 const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
 function options(raw={}){return{compact:raw?.compact===true,objectives:raw?.objectives!==false};}
 function percent(value,maximum){return maximum>0?clamp(finite(value)/maximum*100,0,100):0;}
 function angle(deg){return((finite(deg)%360)+360)%360;}
 function delta(a,b){return((angle(a)-angle(b)+540)%360)-180;}
 function ticks(yaw){const degrees=angle(finite(yaw)*180/Math.PI),labels=['N','NE','E','SE','S','SO','O','NO'],result=[];for(let d=Math.floor((degrees-65)/15)*15;d<=degrees+65;d+=15){const x=delta(d,degrees);if(Math.abs(x)>60)continue;result.push({degree:angle(d),x:(x+60)/120*100,label:d%45===0?labels[angle(d)/45]:'',major:d%45===0});}return result;}
 function bearing(player,target,yaw){if(!Array.isArray(player)||!Array.isArray(target)||player.length<3||target.length<3||![player[0],player[2],target[0],target[2],yaw].every(Number.isFinite))return null;const dx=target[0]-player[0],dz=target[2]-player[2];if(Math.hypot(dx,dz)<.01)return null;const offset=delta(Math.atan2(dx,-dz)*180/Math.PI,yaw*180/Math.PI);return{offset,x:clamp((offset+60)/120*100,2,98),edge:Math.abs(offset)>60};}
 function read(player={},weapon={},reload=0){const hp=percent(player.hp,player.maxHp),ammo=Math.max(0,Math.floor(finite(player.ammoClip)));return{hp,ap:percent(player.ap,player.maxAp),lowHp:hp<=25&&finite(player.hp)>0,empty:!weapon.melee&&ammo===0,reloading:finite(reload)>0,stance:player.cameraMode==='third'?'VUE EXTERIEURE':player.crouched?'ACCROUPI':'DEBOUT'};}
 return Object.freeze({options,percent,angle,delta,ticks,bearing,read});
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralFpsHud;

function v056HudAfterInit(){
 if(typeof window==='undefined'||window.__mistralFpsHud)return;
 window.__mistralFpsHud=true;
 const M=MistralFpsHud,key='mistral_fps_hud_v1';let preferences=M.options();
 try{preferences=M.options(JSON.parse(localStorage.getItem(key)||'{}'));}catch{}
 const style=document.createElement('style');style.id='fps56-hud-style';style.textContent=`
 body.fps56{--hud-base:90px}body.fps56 #hud{--hud-pad:24px;color:#e7ebc9;text-shadow:0 1px 3px #000,0 0 8px #101b12}
 body.fps56 #locationCard{left:max(var(--hud-pad),env(safe-area-inset-left));top:max(22px,env(safe-area-inset-top));max-width:30vw;letter-spacing:.07em}
 body.fps56 #locationName{font-size:.83rem;font-weight:700;line-height:1.4}
 body.fps56 #hud .location-card small{font-size:.57rem;color:#c8b775}
 body.fps56 #compass{top:max(18px,env(safe-area-inset-top));width:260px;letter-spacing:.12em}
 body.fps56 #compassDir{font-size:.68rem;font-weight:bold}
 body.fps56 #compass>i{display:none}
 #fps56Compass{position:relative;height:29px;margin:6px 0 0;border-bottom:1px solid #d3dcb77a;overflow:hidden;mask-image:linear-gradient(90deg,transparent,#000 12% 88%,transparent)}
 #fps56Compass span{position:absolute;bottom:0;transform:translateX(-50%);height:6px;border-left:1px solid #dae4b5a6;font:9px monospace;color:#e7ebc9}
 #fps56Compass span.major{height:14px;border-color:#edf1d0}
 #fps56Compass span b{position:absolute;left:0;bottom:15px;transform:translateX(-50%);font:10px monospace}
 #fps56Compass:after{content:'';position:absolute;left:50%;bottom:0;border-left:4px solid transparent;border-right:4px solid transparent;border-bottom:5px solid #e7cf85;transform:translateX(-50%)}
 #fps56Bearing{position:absolute;top:42px;color:#f1d686;font:15px monospace;transform:translateX(-50%)}
 #fps56Bearing.edge{font-size:11px}
 body.fps56 #questDistance{font-size:.61rem;margin-top:5px;color:#f0d78c;min-height:14px}
 body.fps56 #questCard,body.fps56 #v020QuestHint{top:max(22px,env(safe-area-inset-top));right:max(24px,env(safe-area-inset-right));width:min(315px,28vw);background:linear-gradient(90deg,#101a1300,#101a13bd);border:0;border-right:2px solid #cfbd7c;padding:10px 12px;text-align:right;font-size:.72rem;line-height:1.55;box-shadow:none;max-height:150px;overflow:hidden}
 body.fps56 #questCard small,body.fps56 #v020QuestHint b{font-size:.63rem;letter-spacing:.08em;color:#f0d78c}
 body.fps56 #questCard p{font-size:.73rem;margin:7px 0 0;line-height:1.55}
 body.fps56 #v020QuestHint small{font-size:.58rem}
 body.fps56 .fps56-objective-hidden{display:none!important}
 body.fps56 #statusBars{left:max(24px,env(safe-area-inset-left));bottom:var(--hud-base);width:235px;padding:10px 13px;background:linear-gradient(90deg,#0b1514d9,#0b151455);border-left:2px solid #b7c98e}
 body.fps56 #statusBars>div{font-size:.68rem;grid-template-columns:1.6rem 1fr 2rem;margin:6px 0;gap:8px}
 body.fps56 #statusBars i{height:5px;background:#d7dfac2b}
 body.fps56 #statusBars i b{background:#c8dda4;transition:width .14s}
 body.fps56 #statusBars .radline i b{background:#dbaa65}
 body.fps56 #networkStatus{display:none}
 body.fps56 #statusBars[data-critical=true]{border-color:#f0a481}
 body.fps56 #statusBars[data-critical=true] #hpBar{background:#efa17b}
 body.fps56 #weaponHud{right:max(24px,env(safe-area-inset-right));bottom:var(--hud-base);min-width:210px;max-width:260px;padding:10px 13px;border-right:2px solid #b7c98e;background:linear-gradient(270deg,#0b1514d9,#0b151455);gap:6px}
 /* v046 fixed these dimensions with !important. Replace that specific contract
    so the responsive HUD can use content height and a bounded column. */
 body.fps56 #weaponHud{width:240px!important;min-width:0!important;max-width:260px!important;height:auto!important;min-height:0!important;max-height:none!important;grid-template-rows:auto!important}
 body.fps56 #weaponHud strong{display:block;height:auto!important;line-height:1.1!important;grid-template-columns:none}
 body.fps56 #weaponHud small{height:auto;white-space:normal;line-height:1.4}
 body.fps56 #weaponHud>em{height:auto}
 body.fps56 #weaponHud .condition-line{height:auto;max-width:100%;grid-template-columns:auto minmax(18px,1fr) auto minmax(18px,1fr);gap:4px;letter-spacing:0}
 body.fps56 #weaponHud .v018-reload{top:auto;bottom:100%;width:100%}
 body.fps56 #weaponName{font-size:.63rem;color:#d9ddb8;letter-spacing:.06em;line-height:1.35}
 body.fps56 #weaponHud strong{font:600 34px/1.1 monospace;color:#edf0ce;letter-spacing:-.05em}
 body.fps56 #ammoReserve{font-size:20px;color:#bbc5a5}
 body.fps56 #reloadHint{font-size:.59rem;color:#e5d38c;min-height:11px;margin:0}
 body.fps56 #weaponHud[data-empty=true] #ammoClip{color:#f0a481}
 body.fps56 #weaponHud .condition-line{font-size:8px;opacity:.85}
 body.fps56 #v020Quickbar{left:50%;bottom:max(20px,env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(9,minmax(0,1fr));width:min(850px,calc(100vw - 48px));max-width:none;height:auto;min-height:44px;gap:4px;z-index:23}
 body.fps56 #v020Quickbar button{font:11px/1.3 monospace;letter-spacing:0;text-transform:none;padding:7px 5px!important;border-radius:2px;min-width:0;max-width:none;height:44px;min-height:44px;background:#101d18e8;border-color:#6b805b;color:#dce5bb;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
 body.fps56 #v020Quickbar button.active{border-color:#e9d18b;color:#f5e7af;background:#3e4930}
 body.fps56 #v020Quickbar button:disabled{opacity:.6;color:#abb49b}
 body.fps56 #v020Quickbar[hidden]{display:none!important}
 body.fps56 #quickHelp{display:none}
 body.fps56 #hud:not(.touch) .touch-controls{display:none}
 body.fps56 #p28LampHud{right:max(24px,env(safe-area-inset-right));bottom:calc(var(--hud-base) + 130px);min-height:36px;font-size:10px;border-color:#758764;background:#101d18dd;padding:8px 10px}
 body.fps56 #v042LayerHud{top:84px;bottom:auto;left:24px;min-width:0;width:min(300px,30vw);max-width:30vw;padding:7px 10px;font-size:10px}
 body.fps56 #p30Hud{top:220px!important;right:24px;width:210px;max-width:calc(100vw - 28px);padding:8px 10px;font-size:10px}
 body.fps56 #p30Hud[hidden],body.fps56 #p28LampHud[hidden]{display:none!important}
 body.fps56 #p30Hud b{font-size:10px}body.fps56 #p30Hud div{margin:6px 0}body.fps56 #p30Hud small{font-size:9px}
 body.fps56 #stealth29{top:calc(50% - 38px);width:80px;padding:3px 4px;font:9px/12px monospace}
 body.fps56 #stealth29 strong{font-size:9px;letter-spacing:0}
 body.fps56 #stealth29 progress{height:3px;margin:3px 0}
 body.fps56 #stealth29 small{display:none}
 body.fps56 #levelHud{left:25px;bottom:calc(var(--hud-base) + 105px);width:180px;font-size:10px}
 body.fps56 #v023CriticalHud{left:25px;bottom:calc(var(--hud-base) + 145px);max-width:260px;font-size:10px;background:#101d18ad;border:0;padding:5px 7px}
 body.fps56 #needsHud{left:25px;bottom:calc(var(--hud-base) + 175px);font-size:9px;gap:5px}
 body.fps56 #companionCard{left:25px;bottom:calc(var(--hud-base) + 212px);font-size:10px}
 body.fps56 #effectHud{left:25px;bottom:calc(var(--hud-base) + 255px);right:auto;max-width:300px;display:flex;gap:4px;flex-wrap:wrap}
 body.fps56 #toastStack{right:24px;bottom:calc(var(--hud-base) + 180px);width:290px;max-height:40vh;overflow:hidden}
 body.fps56 #toastStack .toast{font-size:.67rem;background:#0c1717e8;line-height:1.5;padding:9px 11px}
 body.fps56 #interactPrompt{bottom:32%;max-width:min(540px,85vw);font-size:.77rem;line-height:1.45;padding:9px 13px;background:#101b17ed;border-color:#b2bf8b;box-shadow:0 3px 20px #0005;text-align:center}
 body.fps56 #crosshair{width:26px;height:26px;--spread:0px}
 body.fps56 #crosshair i{background:#e9efd0}
 body.fps56 #crosshair i:nth-child(1){left:calc(0px - var(--spread));top:12px;width:6px}
 body.fps56 #crosshair i:nth-child(2){right:calc(0px - var(--spread));top:12px;width:6px}
 body.fps56 #crosshair i:nth-child(3){left:12px;top:calc(0px - var(--spread));height:6px}
 body.fps56 #crosshair i:nth-child(4){left:12px;bottom:calc(0px - var(--spread));height:6px}
 body.fps56 #crosshair.interactive i{background:#f3d68c}
 body.fps56 #fps56Stance{position:absolute;left:50%;top:calc(50% + 28px);transform:translateX(-50%);font:9px monospace;letter-spacing:.13em;color:#e4e9c5;opacity:.8}
 body.fps56 #subtitle{bottom:calc(var(--hud-base) + 50px);font-size:1rem;max-width:65vw}
 body.fps56 #fps56ObjectiveToggle{position:absolute;right:max(24px,env(safe-area-inset-right));top:174px;pointer-events:auto;padding:6px 9px;min-height:32px;font-size:9px;letter-spacing:.05em;border:0;border-bottom:1px solid #95a078;background:#101d18ad}
 body.fps56 #hud.fps56-compact #locationCard small,body.fps56 #hud.fps56-compact #levelHud,body.fps56 #hud.fps56-compact #v023CriticalHud{display:none}
 body.fps56 #hud.fps56-compact #statusBars{padding:4px 9px}
 body.fps56 #hud.fps56-compact #weaponHud .condition-line{display:none}
 body.fps56 #hud.fps56-compact #weaponHud{padding:6px 9px}
 body.fps56:has(#hud.fps56-compact) #v023CriticalHud{display:none}
 body.fps56 .geo-hud,body.fps56 #v036Attribution{display:none!important}
 body.fps56 #geoAttribution{position:absolute;left:50%;bottom:calc(env(safe-area-inset-bottom,0px) + 1px);transform:translateX(-50%);display:block;max-width:calc(100vw - 20px);padding:1px 5px;font:9px/12px monospace;letter-spacing:0;text-transform:none;white-space:nowrap;color:#cbd6b4;background:#0c1719bf;pointer-events:auto;cursor:pointer;border:0;text-align:center}
 body.fps56 #geoAttribution[hidden]{display:none!important}
 body.fps56 #geoAttribution:focus-visible{outline:2px solid #eadb95;outline-offset:1px}
 .fps56-options{margin:18px 0;border:1px solid #758764;padding:14px}.fps56-options label{display:flex;gap:10px;align-items:center;margin:10px 0;font-size:13px}.fps56-options p{font:12px/1.6 monospace;color:#bbc5a5}
 @media(max-width:1100px){body.fps56 #hud{--hud-pad:16px}body.fps56 #locationCard{max-width:27vw}body.fps56 #questCard,body.fps56 #v020QuestHint{width:26vw;font-size:.66rem}body.fps56 #statusBars{left:16px}body.fps56 #weaponHud{right:16px}body.fps56 #p28LampHud{right:16px}}
 @media(max-width:760px){
 body.fps56{--hud-base:126px}
 body.fps56 #locationCard{left:14px;top:14px;max-width:52vw;letter-spacing:0}body.fps56 #locationName{font-size:.68rem}body.fps56 #locationCard small{font-size:.5rem}
 body.fps56 #compass{right:14px;left:auto;transform:none;top:14px;width:135px}body.fps56 #compassDir{font-size:10px}body.fps56 #fps56Compass{height:23px;margin-top:2px}body.fps56 #fps56Compass span b{font-size:8px}body.fps56 #fps56Bearing{top:34px}body.fps56 #questDistance{font-size:8px;margin-top:3px}
 body.fps56 #questCard,body.fps56 #v020QuestHint{top:82px;right:14px;max-height:100px;width:min(290px,76vw);font-size:11px;padding:7px 10px}body.fps56 #questCard p{font-size:11px;line-height:1.45}body.fps56 #questCard small,body.fps56 #v020QuestHint b{font-size:10px}
 body.fps56 #fps56ObjectiveToggle{top:187px;right:14px;min-height:28px;font-size:8px;padding:4px 7px}
 body.fps56 #v042LayerHud{top:220px;left:14px;width:min(240px,65vw);max-width:65vw;font-size:9px}
 body.fps56 #p30Hud{top:270px!important;right:14px;width:165px;padding:6px 8px}
 body.fps56 #v020Quickbar{bottom:max(12px,env(safe-area-inset-bottom));width:calc(100vw - 28px);grid-template-columns:repeat(5,minmax(0,1fr));gap:4px}body.fps56 #v020Quickbar button{height:44px;font-size:10px}body.fps56 #v020Quickbar .quick-slot{display:none}
 body.fps56 #statusBars{left:14px;width:min(155px,43vw);padding:6px 9px}body.fps56 #statusBars>div{font-size:10px;grid-template-columns:22px 1fr 26px;gap:4px;margin:5px 0}body.fps56 #statusBars i{height:4px}
 body.fps56 #weaponHud{right:14px;min-width:0;width:min(165px,45vw)!important;padding:6px 9px;gap:4px}body.fps56 #weaponName{font-size:9px}body.fps56 #weaponHud strong{font-size:28px}body.fps56 #ammoReserve{font-size:16px}body.fps56 #reloadHint{font-size:8px}body.fps56 #weaponHud .condition-line{font-size:7px}
 body.fps56 #p28LampHud{right:14px;bottom:calc(var(--hud-base) + 117px);min-height:32px;font-size:9px;padding:6px 9px}
 body.fps56 #levelHud{left:14px;bottom:calc(var(--hud-base) + 100px);width:125px}body.fps56 #v023CriticalHud{left:14px;bottom:calc(var(--hud-base) + 140px);font-size:8px;max-width:52vw}body.fps56 #needsHud{left:14px;bottom:calc(var(--hud-base) + 166px);max-width:55vw;flex-wrap:wrap;font-size:8px}
 body.fps56 #needsHud{max-width:140px}
 body.fps56 #companionCard{left:14px;bottom:calc(var(--hud-base) + 202px);padding:4px 7px}body.fps56 #effectHud{left:14px;bottom:calc(var(--hud-base) + 250px);max-width:50vw}body.fps56 #toastStack{right:14px;bottom:calc(var(--hud-base) + 160px);width:45vw;max-height:180px}body.fps56 #toastStack .toast{font-size:9px;padding:6px 8px}
 body.fps56 #subtitle{bottom:calc(var(--hud-base) + 40px);max-width:90vw;font-size:.8rem}body.fps56 #interactPrompt{bottom:43%;font-size:11px;max-width:85vw}
 body.fps56:has(#hud.touch){--hud-base:260px}body.fps56 #hud.touch #v020Quickbar{bottom:12px}body.fps56 #hud.touch #touchMove{bottom:112px;width:100px;height:100px;left:16px}body.fps56 #hud.touch .touch-fire{right:18px;bottom:112px}body.fps56 #hud.touch .touch-action{right:88px;bottom:145px}body.fps56 #hud.touch .touch-vats{right:18px;bottom:184px}body.fps56 #hud.touch .touch-pip{right:88px;bottom:77px}
 }
 @media(max-height:540px) and (min-width:600px){
 body.fps56{--hud-base:calc(max(12px,env(safe-area-inset-bottom)) + 60px)}body.fps56 #v020Quickbar{bottom:10px}body.fps56 #levelHud,body.fps56 #v023CriticalHud,body.fps56 #companionCard{display:none}body.fps56 #needsHud{bottom:185px}body.fps56 #effectHud{bottom:215px}body.fps56 #toastStack{bottom:205px;max-height:110px}body.fps56 #p28LampHud{bottom:190px}body.fps56 #questCard,body.fps56 #v020QuestHint{max-height:90px}body.fps56 #fps56ObjectiveToggle{top:120px}body.fps56:has(#hud.touch){--hud-base:calc(max(12px,env(safe-area-inset-bottom)) + 60px)}body.fps56 #hud.touch #statusBars{width:170px}body.fps56 #hud.touch #weaponHud{width:170px!important}body.fps56 #hud.touch #touchMove{bottom:70px;left:200px;width:80px;height:80px}body.fps56 #hud.touch .touch-fire{right:200px;bottom:70px}body.fps56 #hud.touch .touch-action{right:268px;bottom:70px}body.fps56 #hud.touch .touch-vats{right:200px;bottom:140px}body.fps56 #hud.touch .touch-pip{right:268px;bottom:140px}
 body.fps56 #v042LayerHud{top:84px;left:16px;width:200px;max-width:25vw}body.fps56 #p30Hud{top:120px!important;right:16px;width:170px;height:40px;padding:4px 8px;overflow:hidden}body.fps56 #p30Hud b{display:none}body.fps56 #p30Hud div{height:18px;margin:0}body.fps56 #p30Hud small{font:8px/11px monospace}body.fps56:has(#p30Hud:not([hidden])) #fps56ObjectiveToggle{right:200px}
 }
 @media(prefers-reduced-motion:reduce){body.fps56 #crosshair,body.fps56 #statusBars i b{transition:none}}
 /* Reserve a separate line for the map attribution, including safe areas. */
 body.fps56 #v020Quickbar,body.fps56 #hud.touch #v020Quickbar{bottom:calc(max(12px,env(safe-area-inset-bottom)) + 14px)}
 `;document.head.appendChild(style);document.body.classList.add('fps56');
 const hud=$('hud');hud.setAttribute('aria-live','off');
 const attribution=$('geoAttribution')||document.createElement('small');attribution.id='geoAttribution';
 if(attribution){hud.appendChild(attribution);attribution.setAttribute('role','button');attribution.tabIndex=0;attribution.setAttribute('aria-label','Sources géographiques et licences');const openSources=()=>{if(mode==='PLAYING')v047OpenStatus();};attribution.addEventListener('click',openSources);attribution.addEventListener('keydown',e=>{if(['Enter','Space'].includes(e.code)){e.preventDefault();e.stopPropagation();if(!e.repeat)openSources();}});}
 const strip=document.createElement('div');strip.id='fps56Compass';strip.setAttribute('aria-hidden','true');$('compass').insertBefore(strip,$('questDistance'));
 const pip=document.createElement('span');pip.id='fps56Bearing';pip.hidden=true;pip.setAttribute('aria-hidden','true');$('compass').appendChild(pip);
 const stance=document.createElement('span');stance.id='fps56Stance';hud.appendChild(stance);
 const objectiveToggle=document.createElement('button');objectiveToggle.id='fps56ObjectiveToggle';objectiveToggle.type='button';objectiveToggle.title='Afficher ou masquer le suivi de quête';hud.appendChild(objectiveToggle);
 const aim=document.createElement('button');aim.type='button';aim.dataset.fps56Aim='true';aim.textContent='X · Visée';aim.title='Maintenir pour présenter l’arme dans l’axe du viseur';aim.setAttribute('aria-label','Maintenir la visée');
 let aimingPointer=null;
 const setAim=held=>{if(typeof v056FirstPersonAim==='function')v056FirstPersonAim(held);else window.__MISTRAL_DEBUG?.v056Aim?.(held);};
 aim.addEventListener('pointerdown',e=>{if(e.button!==0||mode!=='PLAYING'||aimingPointer!==null)return;e.preventDefault();aimingPointer=e.pointerId;aim.setPointerCapture?.(e.pointerId);setAim(true);});
 const releaseAim=e=>{if(e&&e.pointerId!==aimingPointer)return;aimingPointer=null;setAim(false);};
 aim.addEventListener('pointerup',releaseAim);aim.addEventListener('pointercancel',releaseAim);aim.addEventListener('lostpointercapture',releaseAim);window.addEventListener('blur',()=>releaseAim());document.addEventListener('visibilitychange',()=>{if(document.hidden)releaseAim();});
 aim.addEventListener('keydown',e=>{if(['Space','Enter'].includes(e.code)){e.preventDefault();e.stopPropagation();if(!e.repeat)setAim(true);}});aim.addEventListener('keyup',e=>{if(['Space','Enter'].includes(e.code)){e.preventDefault();e.stopPropagation();setAim(false);}});aim.addEventListener('blur',()=>{if(aimingPointer===null)setAim(false);});
 const fields=document.createElement('fieldset');fields.className='fps56-options';fields.innerHTML='<legend>Affichage en jeu</legend><label><input type="checkbox" data-fps56="compact"> HUD compact</label><label><input type="checkbox" data-fps56="objectives"> Afficher le suivi de quête</label><p>Les jauges, munitions et effets restent disponibles. Le bouton de suivi masque seulement l’objectif à l’écran ; le journal conserve les quêtes.</p>';
 const optionsRoot=$('optionsScreen')?.querySelector('.options-card');if(optionsRoot)optionsRoot.insertBefore(fields,optionsRoot.querySelector('footer'));
 function sync(){hud.classList.toggle('fps56-compact',preferences.compact);fields.querySelector('[data-fps56=compact]').checked=preferences.compact;fields.querySelector('[data-fps56=objectives]').checked=preferences.objectives;objectiveToggle.textContent=preferences.objectives?'Suivi · masquer':'Suivi · afficher';objectiveToggle.setAttribute('aria-pressed',String(preferences.objectives));}
 function store(next){const before=preferences;preferences=M.options(next);try{localStorage.setItem(key,JSON.stringify(preferences));}catch{preferences=before;toast('Affichage non enregistré : stockage indisponible.','bad');}sync();}
 fields.addEventListener('change',()=>store({compact:fields.querySelector('[data-fps56=compact]').checked,objectives:fields.querySelector('[data-fps56=objectives]').checked}));objectiveToggle.onclick=()=>store({...preferences,objectives:!preferences.objectives});$('btnOptionsReset')?.addEventListener('click',()=>store(M.options()));sync();
 let compassStamp='',lastMode=null;
 const base=updateHUD;updateHUD=function(...args){const result=base(...args);if(!gameStarted||!state?.player)return result;const playing=mode==='PLAYING';if(lastMode!==mode){lastMode=mode;if(!playing)releaseAim();}hud.classList.toggle('fps56-compact',preferences.compact);
  const hint=$('v020QuestHint'),quest=$('questCard'),hasHint=!!hint&&!hint.hidden&&!!hint.textContent.trim();
  hint?.classList.toggle('fps56-objective-hidden',!preferences.objectives||!hasHint);quest.classList.toggle('fps56-objective-hidden',!preferences.objectives||hasHint);
  objectiveToggle.hidden=!playing;
  const model=M.read(state.player,currentWeapon(),reloadTimer);$('statusBars').dataset.critical=String(model.lowHp);$('weaponHud').dataset.empty=String(model.empty);$('weaponHud').dataset.reloading=String(model.reloading);
  $('reloadHint').textContent=currentWeapon().melee?'CORPS À CORPS':model.reloading?'RECHARGEMENT…':model.empty?'CHARGEUR VIDE · R':'R · RECHARGER';
  stance.textContent=model.stance;stance.hidden=!playing||!state.player.crouched&&state.player.cameraMode!=='third';
  const ticks=M.ticks(state.player.yaw),stamp=JSON.stringify(ticks.map(t=>[t.degree,Math.round(t.x*10)/10]));if(stamp!==compassStamp){compassStamp=stamp;strip.replaceChildren(...ticks.map(t=>{const el=document.createElement('span');el.style.left=t.x+'%';el.className=t.major?'major':'';if(t.label){const label=document.createElement('b');label.textContent=t.label;el.appendChild(label);}return el;}));}
  const objective=getObjectiveMarker(),bearing=objective?.zone===world?.id?M.bearing(state.player.pos,objective.pos,state.player.yaw):null;pip.hidden=!playing||!preferences.objectives||!bearing;if(bearing){pip.style.left=bearing.x+'%';pip.textContent=bearing.edge?(bearing.offset<0?'◀':'▶'):'◇';pip.classList.toggle('edge',bearing.edge);}
  const bar=$('v020Quickbar');if(bar&&!bar.contains(aim))bar.appendChild(aim);aim.disabled=!playing||state.player.cameraMode==='third'||!!world?.vehicleMode||!!currentWeapon().melee;aim.setAttribute('aria-pressed',String(typeof v056FirstPersonIsAiming==='function'&&v056FirstPersonIsAiming()));
  if(settings.reduceMotion)hud.classList.add('fps56-reduced');else hud.classList.remove('fps56-reduced');
  const stealth=$('stealth29');if(stealth)stealth.title=stealth.querySelector('small')?.textContent||'';
  if(attribution){const geographic=!!world?.v046;attribution.hidden=!geographic;if(geographic){attribution.title=attribution.textContent;attribution.textContent=typeof V046!=='undefined'&&V046.lab?'Banc synthétique · données de test':'© contributeurs OpenStreetMap · Cadastre/DGFiP · IGN';}}
  return result;
 };
 Object.assign(window.__MISTRAL_DEBUG,{v056HudInfo:()=>({preferences:{...preferences},model:M.read(state?.player,currentWeapon(),reloadTimer),mode,assistance:'Presentation only; no world position, health, ammo or quest writes.'})});
 updateHUD();
}
