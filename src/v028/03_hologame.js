/* Original offline routing game. Six authored boards, no XP/caps or loot rewards. */
const V028_ROUTES=[
 {name:'Ligne droite',path:[10,11,12,13,14]},
 {name:'Contourner la panne',path:[15,16,11,6,7,8,13,14]},
 {name:'Double retour',path:[5,6,11,16,17,18,13,8,9]},
 {name:'Service de nuit',path:[20,21,16,11,6,7,12,17,18,19]},
 {name:'Les trois relais',path:[0,1,6,11,10,15,20,21,22,17,12,7,8,13,18,19]},
 {name:'Dernière correspondance',path:[20,15,10,5,0,1,2,7,6,11,16,17,22,23,18,13,8,3,4]}
];
function v028Direction(a,b){return b===a-5?1:b===a+1?2:b===a+5?4:8;}
function v028MaskRotate(mask,n){for(let i=0;i<n;i++)mask=((mask<<1)&15)|((mask>>3)&1);return mask;}
function v028Board(i=V028.puzzle){const d=V028_ROUTES[i];if(!d)return null;const masks=Array(25).fill(0);d.path.forEach((cell,j)=>masks[cell]=(j?v028Direction(cell,d.path[j-1]):8)|(j<d.path.length-1?v028Direction(cell,d.path[j+1]):2));return {...d,masks,start:d.path[0],end:d.path.at(-1)};}
function v028GameState(i=V028.puzzle){const board=v028Board(i);if(!board)return null;const all=state.v028.game.levels;let g=all[i];if(!g||g.turns.length!==25){const best=g?.best??null;g=all[i]={turns:Array.from({length:25},(_,k)=>board.masks[k]&&k!==board.start&&k!==board.end?(k+i)%3+1:0),moves:0,best,won:false,hints:0};}g.turns[board.start]=0;g.turns[board.end]=0;return g;}
function v028Circuit(i=V028.puzzle){const b=v028Board(i),g=v028GameState(i),m=b.masks.map((v,k)=>v028MaskRotate(v,g.turns[k])),seen=new Set(),todo=[b.start],leaks=[];if(!(m[b.start]&8))return{connected:[],leaks:['entrée'],success:false};
 while(todo.length){const cell=todo.pop();if(seen.has(cell))continue;seen.add(cell);const x=cell%5,y=Math.floor(cell/5);for(const[bit,dx,dy,op]of[[1,0,-1,4],[2,1,0,8],[4,0,1,1],[8,-1,0,2]])if(m[cell]&bit){if(cell===b.start&&bit===8||cell===b.end&&bit===2)continue;const xx=x+dx,yy=y+dy,n=yy*5+xx;if(xx<0||xx>=5||yy<0||yy>=5||!(m[n]&op)){leaks.push(cell);continue;}if(!seen.has(n))todo.push(n);}}
 return {connected:[...seen],leaks:[...new Set(leaks)],success:seen.has(b.end)&&leaks.length===0};}
function v028GameRender(c){if(!state.v028.game.unlocked){c.innerHTML='<div class="p28-empty"><h2>Aiguilleur Mistral</h2><p>Holodisque-jeu original. Trouvez la cassette d’entraînement au poste de Sofia dans l’Annexe des Veilleurs.</p><p>Aucun téléchargement, voix ou score en ligne.</p></div>';return;}
 const b=v028Board(),g=v028GameState(),flow=v028Circuit();g.won=flow.success;
 const tiles=b.masks.map((mask,i)=>{const m=v028MaskRotate(mask,g.turns[i]),locked=i===b.start||i===b.end,live=flow.connected.includes(i);let lines='';for(const[bit,x,y]of[[1,40,0],[2,80,40],[4,40,80],[8,0,40]])if(m&bit)lines+=`<path d="M40 40L${x} ${y}"/>`;return `<button data-p27="p28:rotate" data-arg="${i}" class="p28-tile ${live?'live':''} ${flow.leaks.includes(i)?'leak':''}" ${!mask||locked?'disabled':''} aria-label="Case ${Math.floor(i/5)+1}, ${i%5+1}${locked?', borne fixe':mask?', tourner de 90 degrés':', isolant'}"><svg viewBox="0 0 80 80" aria-hidden="true"><g>${lines}</g>${mask?'<circle cx="40" cy="40" r="7"/>':''}</svg>${locked?'<span>'+ (i===b.start?'ENTRÉE':'SORTIE')+'</span>':''}</button>`;}).join('');
 c.innerHTML=`<div class="p28-game"><div><p class="p27-kicker">HOLODISQUE ORIGINAL · HORS LIGNE</p><h2>Aiguilleur Mistral</h2><p>Reliez l’entrée à la sortie sans fuite. Cliquez une conduite pour la tourner de 90°. Les bornes sont fixes ; les cellules hors circuit peuvent rester déconnectées.</p><div class="p28-levels">${V028_ROUTES.map((d,i)=>v027Button(`${i+1}${state.v028.game.levels[i]?.best!==null&&state.v028.game.levels[i]?.best!==undefined?' ✓':''}`,'p28:level',i,V028.puzzle===i)).join('')}</div><h3>${V028.puzzle+1}. ${b.name}</h3><p>Rotations : <b>${g.moves}</b> · Meilleur : <b>${g.best??'—'}</b></p><p class="p28-verdict" role="status">${flow.success?'CIRCUIT CONTINU · SORTIE ALIMENTÉE':`${flow.connected.length} cellule(s) alimentée(s) · ${flow.leaks.length} fuite(s)`}</p><p>${v027Escape(V028.gameMessage)}</p><div class="p27-actions">${v027Button('Indice','p28:hint')}${v027Button('Recommencer ce circuit','p28:reset')}</div><p class="p27-muted">Le meilleur score et la disposition sont sauvegardés. Ni XP ni capsules. Pas de chronomètre imposé.</p></div><div class="p28-board" aria-label="Grille de cinq lignes et cinq colonnes">${tiles}</div></div>`;
}
function v028GameAction(a,arg){if(!v027CanAct()||!state.v028.game.unlocked||V027.tab!=='radio'||V027.sub!=='games')return false;
 if(a==='level'){const n=Number(arg);if(!Number.isInteger(n)||!V028_ROUTES[n])return false;V028.puzzle=n;V028.gameMessage='';}
 else{const b=v028Board(),g=v028GameState();if(a==='rotate'){const n=Number(arg);if(!Number.isInteger(n)||n<0||n>=25||!b.masks[n]||n===b.start||n===b.end)return false;g.turns[n]=(g.turns[n]+1)%4;g.moves++;V028.gameMessage='';const flow=v028Circuit();g.won=flow.success;if(g.won){g.best=g.best===null?g.moves:Math.min(g.best,g.moves);V028.gameMessage='Le relais reçoit le signal. Aucun gain de personnage attribué.';audio.ui(720,.05);}}
 else if(a==='hint'){const idx=b.path.find(k=>v028MaskRotate(b.masks[k],g.turns[k])!==b.masks[k]);g.hints++;V028.gameMessage=idx===undefined?'Tous les raccords sont déjà alignés.':`Vérifiez la case ligne ${Math.floor(idx/5)+1}, colonne ${idx%5+1}. L’indice ne tourne aucune pièce.`;}
 else if(a==='reset'){if(!confirm('Recommencer ce circuit ? Le meilleur score est conservé.'))return false;const best=g.best;delete state.v028.game.levels[V028.puzzle];v028GameState().best=best;V028.gameMessage='Disposition initiale rétablie.';}else return false;}
 v028Save();return true;
}
V027_SUBS.radio.games='JEUX';
const v028Radio=v027Radio;v027Radio=function(c){if(V027.sub==='games')return v028GameRender(c);return v028Radio(c);};
