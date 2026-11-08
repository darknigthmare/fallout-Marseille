'use strict';
const M=require('../../src/v050/10i_fete_voisins.js');
const R=require('../../src/v050/10f_cite_radieuse.js');
const U=require('../../src/v050/10g_mutuelle_phoceenne.js');
const N=require('../../src/v050/10h_notaires_apres.js');
function base(acte='usage',representation='lots',assurance='forfait'){
 let s={player:{hp:100,caps:300},character:{special:{I:6,C:6}},playTime:10,inventory:{food:60,water:60,cloth:60,scrap:60,circuitry:60},v063Radieuse:R.fresh(),v064Mutuelle:U.fresh(),v065Notaires:N.fresh(),v066Voisins:M.fresh(),v060Council:{charter:'charte_vivants'},v061Poste:{finished:true},v062Pharmacy:{care:2}};
 const ra=(type,id,choice)=>{s=R.apply(s,{type,id,choice},{local:true,near:true,point:['accept','finish'].includes(type)?'josiane':['clause','vote'].includes(type)?'assemblee':id});};
 ra('accept');for(const id of Object.keys(R.EVIDENCE))ra('inspect',id);for(const p of R.PEOPLE)ra('hear',p.id);for(const [k,v]of Object.entries({charges:'solidarite',representation,controle:'audit'}))ra('clause',k,v);ra('vote');for(const w of R.WORKS)ra('repair',w);ra('finish');
 const ua=(type,id)=>{s=U.apply(s,{type,id},{local:true,near:true,point:type==='evidence'?U.EVIDENCE[id].point:type==='report'?'josiane':'expert'});};
 ua('open');for(const id of U.IDS)ua('evidence',id);ua('argue','copies');ua('settle',assurance);ua('report');
 const na=(type,id,value)=>{s=N.apply(s,{type,id,value},{local:true,near:true,point:type==='read'?N.READINGS[id].point:['witness','notify'].includes(type)?id:['dial','unseal','collect'].includes(type)?'vault':'notaire'});};
 na('open');for(const id of Object.keys(N.READINGS))na('read',id);for(const id of ['josiane','salome'])na('witness',id);for(const [i,v]of ['76','48','86'].entries())na('dial',i,v);na('unseal','sequence');na('collect');na('decide',acte);na('notify','josiane');na('notify','salome');na('close');return s;
}
const where=(type,id)=>['open','start','finish'].includes(type)?'josiane':type==='meal'?'buffet':['notice','sound'].includes(type)?'console':id;
function doIt(s,type,id,value){return M.apply(s,{type,id,value},{local:true,near:true,point:where(type,id)});}
function invited(s=base()){s=doIt(s,'open');for(const k of M.GUESTS)s=doIt(s,'listen',k);return s;}
function prepared(meal='apport',sound='silence',s=invited()){
 s=doIt(s,'meal',meal);if(meal==='placard')for(const k of M.PANTRY)s=doIt(s,'collect',k);
 if(sound==='test'){s=doIt(s,'notice');for(const [k,v]of Object.entries({source:'micro',sortie:'local',niveau:'limite'}))s=doIt(s,'switch',k,v);}
 if(sound==='technique')s=doIt(s,'notice');return doIt(s,'sound',sound);
}
function served(layout='commune',s=prepared()){s=doIt(s,'start',layout);for(const id of M.GUESTS)s=doIt(s,'serve',id);return s;}
function answered(layout='commune',karim='comptes',salome='reserves',s=served(layout)){s=doIt(s,'answer','karim',karim);return doIt(s,'answer','salome',salome);}
const old=s=>JSON.stringify([s.v063Radieuse,s.v064Mutuelle,s.v065Notaires,s.v060Council,s.v061Poste,s.v062Pharmacy]);


function complete(acte='usage',representation='lots',assurance='forfait',layout='commune',response='comptes'){let s=base(acte,representation,assurance);s.inventory.chemicals=20;s.inventory.clay=20;s=invited(s);s=prepared('placard','silence',s);s=served(layout,s);s=answered(layout,response,'reserves',s);return doIt(s,'finish');}
module.exports={complete};
