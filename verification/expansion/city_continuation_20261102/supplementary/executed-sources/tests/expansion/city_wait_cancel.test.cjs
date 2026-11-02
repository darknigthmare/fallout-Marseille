// Regression: cancellation of one waiter must not cancel the shared city partition.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const src=fs.readFileSync('src/v050/04a_city_sources.js','utf8');
const start=src.indexOf('function v051CityAbort(');
const end=src.indexOf('function v051CityDescriptor(',start);
assert(start>=0&&end>start,'City wait helpers must exist');
const ctx=vm.createContext({AbortController,Error,Promise});
vm.runInContext(src.slice(start,end),ctx);
const wait=ctx.v051CityWait;
(async()=>{
 let finish;
 const shared=new Promise(resolve=>{finish=resolve;});
 const a=new AbortController(),b=new AbortController();
 const first=wait(shared,a.signal).then(()=>{throw Error('cancelled waiter resolved');},error=>error.name);
 const second=wait(shared,b.signal);
 a.abort();
 assert.equal(await first,'AbortError');
 finish('verified city tile');
 assert.equal(await second,'verified city tile');
 assert.equal(await wait(Promise.resolve(42),new AbortController().signal),42);
 const already=new AbortController();already.abort();
 assert.throws(()=>wait(Promise.resolve(1),already.signal),/annulé/);
 const failed=Promise.reject(Error('network failure'));
 await assert.rejects(wait(failed,new AbortController().signal),/network failure/);
 console.log('City streaming wait cancellation: 5 checks passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
