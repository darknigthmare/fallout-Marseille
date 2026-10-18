/* v0.23 — bounded state. Tests/skills never overwrite S.P.E.C.I.A.L. or old quest fields. */
const V023={goatPage:0,draft:[],exam:false,dialogueEpoch:0,historyOpen:false,criticalShot:false,hit:false,dialogueReturn:null};
const V023_SKILLS={
 repair:{name:'Réparation',stat:'I',desc:'Pièces, assemblages et diagnostics mécaniques. Spécialité : usure des armes −12 %.'},
 medicine:{name:'Médecine',stat:'I',desc:'Triage, soins et lecture des protocoles. Spécialité : soins des Stimpaks +15 %.'},
 science:{name:'Science',stat:'I',desc:'Capteurs, énergie et vérification des données. Spécialité : dégâts énergétiques +6 %.'},
 speech:{name:'Éloquence',stat:'C',desc:'Négocier des conditions précises, pas supprimer tous les désaccords. Sert aux tests de dialogue.'},
 survival:{name:'Survie',stat:'E',desc:'Évaluer vivres, abris et itinéraires. Sert aux tests de préparation de la relève.'},
 sneak:{name:'Discrétion',stat:'A',desc:'Approche méthodique et observation. Spécialité : +5 points de précision V.A.T.S. accroupi.'},
 guns:{name:'Balistique',stat:'P',desc:'Armes à projectile. Spécialité : dégâts balistiques +6 %.'},
 melee:{name:'Mêlée',stat:'S',desc:'Outils de contact et maîtrise du geste. Spécialité : dégâts de mêlée +6 %.'}
};
function v023Fresh(){return {schema:1,goat:{answers:[],tags:[],completed:false,method:null},critical:0,history:[],seen:{},checks:{},quest:{accepted:false,evidence:{manifest:false,register:false,protocol:false},witness:{diane:false,rayan:false},trust:0,ending:null,rewarded:false,deliveries:{transit_depot:false,traverse_archives:false,mooring_station:false},tracked:false},consequences:[]};}
const v023Base=baseState;baseState=function(){const s=v023Base();s.v023=v023Fresh();return s;};
const v023Migration=migrateState;migrateState=function(input={}){const s=v023Migration(input),p=input.v023||{},f=v023Fresh(),g=p.goat||{},q=p.quest||{};s.v023={...f,...p,schema:1,goat:{...f.goat,...g},quest:{...f.quest,...q,evidence:{manifest:false,register:false,protocol:false},witness:{diane:false,rayan:false},deliveries:{}},history:[],checks:{},seen:{},consequences:[]};
 const t=s.v023;t.goat.answers=Array.from({length:Math.min(10,Array.isArray(g.answers)?g.answers.length:0)},(_,i)=>Number.isInteger(g.answers[i])&&g.answers[i]>=0&&g.answers[i]<4?g.answers[i]:null);t.goat.tags=[...new Set(Array.isArray(g.tags)?g.tags:[])].filter(k=>V023_SKILLS[k]).slice(0,3);t.goat.completed=!!g.completed&&t.goat.tags.length===3;t.goat.method=['test','manual'].includes(g.method)?g.method:null;t.critical=clamp(Number.isFinite(p.critical)?p.critical:0,0,100);
 for(const k of ['manifest','register','protocol'])t.quest.evidence[k]=!!q.evidence?.[k];for(const k of ['diane','rayan'])t.quest.witness[k]=!!q.witness?.[k];for(const k of ['transit_depot','traverse_archives','mooring_station'])t.quest.deliveries[k]=!!q.deliveries?.[k];t.quest.trust=clamp(Number(q.trust)||0,-2,2);t.quest.ending=['appeal','network','contract'].includes(q.ending)?q.ending:null;t.quest.rewarded=!!q.rewarded;t.quest.accepted=!!q.accepted;t.quest.tracked=!!q.tracked;
 for(const a of(Array.isArray(p.history)?p.history:[]).slice(-120))if(a&&typeof a.text==='string')t.history.push({speaker:String(a.speaker||'').slice(0,90),text:a.text.slice(0,4200),role:String(a.role||'').slice(0,120),zone:String(a.zone||'').slice(0,90),choice:!!a.choice});
 for(const[k,v]of Object.entries(p.checks||{}).slice(0,50))if(/^[a-z0-9_-]{1,55}$/.test(k))t.checks[k]=!!v;for(const[k,v]of Object.entries(p.seen||{}).slice(0,200))if(/^[a-z0-9_:.-]{1,90}$/.test(k))t.seen[k]=!!v;
 for(const a of(Array.isArray(p.consequences)?p.consequences:[]).slice(-20))if(a&&typeof a.text==='string')t.consequences.push({id:String(a.id||'').slice(0,90),text:a.text.slice(0,1500),observed:!!a.observed});return s;};state=migrateState(state);
function v023Skill(k){const d=V023_SKILLS[k];if(!d)return 0;const sp=state.character.special;return Math.round(clamp(10+4*(sp[d.stat]||3)+(sp.L||3)+(state.v023.goat.completed&&state.v023.goat.tags.includes(k)?15:0),0,100));}
function v023Tagged(k){return !!(state.v023?.goat.completed&&state.v023.goat.tags.includes(k));}
function v023Log(speaker,text,choice=false,role=''){if(!state.v023)return;const h=state.v023.history,last=h.at(-1);if(last?.speaker===speaker&&last.text===text&&last.choice===choice)return;h.push({speaker:String(speaker).slice(0,90),text:String(text).slice(0,4200),choice,role:String(role).slice(0,120),zone:world?.id||''});if(h.length>120)h.splice(0,h.length-120);}
function v023Near(id,r=3.3){const i=world?.interactables.find(x=>x.id===id);return !!(i&&vLen(vSub(state.player.pos,i.pos))<=r&&Math.abs(state.player.pos[1]-i.pos[1])<2&&lineOfSight(state.player.pos,i.pos));}
function v023Safe(id){if(!v023Near(id))return v020Notify('Rejoignez le bon poste, au bon étage.',true);if(v020Danger()||V022.clock<V022.alarmUntil)return v020Notify('Le relais doit être au calme pour cet échange.',true);return true;}
const v023Load=loadZone;loadZone=function(...a){v023CloseExtras();V023.dialogueEpoch++;V023.exam=false;return v023Load(...a);};
