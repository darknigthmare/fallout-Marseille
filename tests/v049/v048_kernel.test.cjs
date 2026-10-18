const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Budget,check,pause,sameReturn,spans}=require('../../src/v048/00_budget.js');
const tests=[];const ck=(name,ok,d)=>{tests.push({name,ok:!!ok,detail:d});if(!ok)throw Error(name);console.log('OK',name)};
(async()=>{
 let clock=0,yields=0;const b=new Budget({budgetMs:6,maxUnits:4,now:()=>clock,yieldFn:async()=>{yields++}});
 await b.checkpoint();ck('Pas de pause inutile avant budget',yields===0);
 clock=7;await b.checkpoint();ck('Pause au budget temporel',yields===1);
 for(let i=0;i<4;i++)await b.checkpoint();ck('Pause au quota opérations',yields===2);
 await b.checkpoint(0,true);ck('Pause forcée de changement de phase',yields===3);
 ck('Budget et compteurs mesurés',b.snapshot().units===6&&b.snapshot().maxSliceMs===7,b.snapshot());
 for(const bad of [{budgetMs:0},{budgetMs:NaN},{maxUnits:0},{maxUnits:.5}]){assert.throws(()=>new Budget(bad));ck('Budget invalide refusé '+JSON.stringify(bad),true)}
 const c=new AbortController();c.abort();await assert.rejects(pause(c.signal),{name:'AbortError'});ck('Pause respecte signal préannulé',true);
 await assert.rejects(new Budget({signal:c.signal}).checkpoint(),{name:'AbortError'});ck('Checkpoint respecte signal préannulé',true);
 const d=new AbortController();const pp=pause(d.signal);d.abort();await assert.rejects(pp,{name:'AbortError'});ck('Annulation pendant attente traitée',true);
 let heartbeat=0;const h=setInterval(()=>heartbeat++,0),w=new Budget({maxUnits:4});for(let i=0;i<40;i++)await w.checkpoint();clearInterval(h);ck('Le navigateur peut traiter des événements entre lots',heartbeat>0,{heartbeat,yields:w.yields});
 ck('Retour position identique accepté',sameReturn([1,2,3],[1,2,3]));
 ck('Erreur de position minimale tolérée',sameReturn([1,2,3],[1.01,2,3]));
 ck('Autre position refusée',!sameReturn([1,2,3],[20,2,3]));
 ck('Coordonnées NaN refusées',!sameReturn([1,2,3],[NaN,2,3]));
 ck('Position incomplète refusée',!sameReturn([1,2,3],[1,2]));
 ck('Mur inversé conserve les deux segments',JSON.stringify(spans(34,14,24,6))==='[[14,21],[27,34]]');
 ck('Mur normal et inversé identiques',JSON.stringify(spans(14,34,24,6))===JSON.stringify(spans(34,14,24,6)));
 ck('Porte hors du mur ne crée pas de débordement',JSON.stringify(spans(0,10,20,4))==='[[0,10]]');
 ck('Porte plus large que mur laisse passage libre',spans(0,10,5,20).length===0);
 ck('Mur sans longueur ignoré',spans(2,2,2,1).length===0);
 ck('Mur sans porte restauré',JSON.stringify(spans(10,0))==='[[0,10]]');
 assert.throws(()=>spans(0,Infinity));ck('Bornes de cloisons invalides refusées',true);
})().catch(e=>{tests.push({name:e.stack,ok:false})}).finally(()=>{const out={version:'0.48.0',passed:tests.filter(t=>t.ok).length,failed:tests.filter(t=>!t.ok).length,total:tests.length,tests};const root=path.join(__dirname,'../../verification/v049');fs.mkdirSync(root,{recursive:true});fs.writeFileSync(path.join(root,'QA_BUDGET_PASSAGES.json'),JSON.stringify(out,null,2));console.log(JSON.stringify({passed:out.passed,failed:out.failed,total:out.total}));process.exitCode=out.failed?1:0});
