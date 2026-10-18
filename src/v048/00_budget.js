/* Cooperative preparation. Budgets are targets between indivisible operations,
   not a real-time or frame-rate guarantee. No browser globals are required. */
const MistralWork = (() => {
  function abortError() { const e = new Error('Préparation annulée'); e.name = 'AbortError'; return e; }
  function check(signal) { if (signal?.aborted) throw abortError(); }
  async function pause(signal) {
    check(signal);
    return new Promise((resolve, reject) => {
      let timer;
      const abort = () => { clearTimeout(timer); signal?.removeEventListener('abort', abort); reject(abortError()); };
      timer = setTimeout(() => { signal?.removeEventListener('abort', abort); if(signal?.aborted) reject(abortError()); else resolve(); }, 0);
      signal?.addEventListener('abort', abort, {once:true});
    });
  }
  class Budget {
    constructor({signal, budgetMs=6, maxUnits=512, now=()=>performance.now(), yieldFn=pause}={}) {
      if (!Number.isFinite(budgetMs) || budgetMs<=0 || !Number.isInteger(maxUnits) || maxUnits<1) throw Error('Budget invalide');
      this.signal=signal; this.budgetMs=budgetMs; this.maxUnits=maxUnits;
      this.now=now; this.yieldFn=yieldFn; this.started=now(); this.slice=this.started;
      this.units=0; this.totalUnits=0; this.yields=0; this.maxSliceMs=0; this.phase='validation';
    }
    async checkpoint(units=1, force=false) {
      check(this.signal); this.units+=units; this.totalUnits+=units;
      const elapsed=this.now()-this.slice;
      if (force || this.units>=this.maxUnits || elapsed>=this.budgetMs) {
        this.maxSliceMs=Math.max(this.maxSliceMs,elapsed); this.yields++;
        await this.yieldFn(this.signal); check(this.signal); this.slice=this.now(); this.units=0;
      }
    }
    snapshot() { return {phase:this.phase,units:this.totalUnits,yields:this.yields,budgetMs:this.budgetMs,
      maxSliceMs:Math.round(this.maxSliceMs*100)/100,elapsedMs:Math.round((this.now()-this.started)*100)/100}; }
  }
  function sameReturn(saved, request, epsilon=.05) {
    return Array.isArray(saved)&&Array.isArray(request)&&saved.length>=3&&request.length>=3&&
      saved.slice(0,3).every((v,i)=>Number.isFinite(v)&&Number.isFinite(request[i])&&Math.abs(v-request[i])<=epsilon);
  }
  function spans(from,to,gap=null,width=0) {
    if (![from,to,width].every(Number.isFinite)) throw Error('Cloison non finie');
    const lo=Math.min(from,to),hi=Math.max(from,to);
    if (hi===lo) return [];
    if (gap===null || !Number.isFinite(gap) || width<=0) return [[lo,hi]];
    const a=Math.max(lo,Math.min(hi,gap-width/2)),b=Math.max(lo,Math.min(hi,gap+width/2));
    return [[lo,a],[b,hi]].filter(([x,y])=>y>x);
  }
  return {Budget,check,pause,sameReturn,spans};
})();
if (typeof module!=='undefined' && module.exports) module.exports=MistralWork;
