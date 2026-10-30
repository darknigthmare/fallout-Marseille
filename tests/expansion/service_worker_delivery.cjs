/* Production cache-first worker upgrading an explicitly synthetic old shell.
   Verifies an actual browser install/activate/offline lifecycle on loopback HTTP. */
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const {chromium}=require(process.env.MISTRAL_PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'../..'),out=process.env.MISTRAL_QA_OUTPUT||path.join(root,'verification/gamedev-streaming-2026-10-29');
fs.mkdirSync(out,{recursive:true});
const currentHTML=fs.readFileSync(path.join(root,'index.html')),currentWorker=fs.readFileSync(path.join(root,'sw.js'),'utf8');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),htmlSHA=sha(currentHTML);
const cacheName=currentWorker.match(/const CACHE='([^']+)'/)[1],oldCache='fallout-mistral-v050-12';
const oldWorker=currentWorker.replace(/const CACHE='[^']+'/,"const CACHE='"+oldCache+"'");
const oldHTML=Buffer.from('<!doctype html><title>Explicit synthetic cached old shell</title><p>Cache upgrade fixture</p>');
let upgraded=false,browser;
const report={scope:'Actual Chromium service worker lifecycle; production worker and current HTML, explicitly synthetic old cached HTML',checks:[],htmlSha256:htmlSHA,cacheName,oldCache,requests:[]};
const check=(name,ok,detail)=>{report.checks.push({name,ok:!!ok,...(detail===undefined?{}:{detail})});console.log((ok?'PASS ':'FAIL ')+name);if(!ok)throw Error(name);};
const server=http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost'),name=url.pathname;
 report.requests.push({path:name,upgraded,worker:req.headers['service-worker']||null});
 res.setHeader('Cache-Control','no-store');
 if(name==='/sw.js'){res.setHeader('Content-Type','text/javascript');return res.end(upgraded?currentWorker:oldWorker);}
 if(name==='/'||name==='/index.html'||name==='/JOUER_FALLOUT_MISTRAL_v0.50.html'){res.setHeader('Content-Type','text/html');return res.end(upgraded?currentHTML:oldHTML);}
 const filename=path.resolve(root,'.'+decodeURIComponent(name));
 if(!filename.startsWith(root+path.sep)||!fs.existsSync(filename)||!fs.statSync(filename).isFile()){res.writeHead(404);return res.end('Not part of this source-only QA snapshot');}
 res.setHeader('Content-Type',name.endsWith('.png')?'image/png':'application/manifest+json');fs.createReadStream(filename).pipe(res);
});
(async()=>{
 check('Offline cache name follows actual HTML digest',cacheName==='fallout-mistral-v050-'+htmlSHA.slice(0,16));
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin='http://127.0.0.1:'+server.address().port;
 browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),headless:true,timeout:60000,args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 report.browser=browser.version();const context=await browser.newContext();const page=await context.newPage();page.setDefaultTimeout(60000);
 await page.goto(origin+'/index.html');
 await page.evaluate(async()=>{await navigator.serviceWorker.register('/sw.js',{updateViaCache:'none'});await navigator.serviceWorker.ready;});
 await page.waitForFunction(()=>!!navigator.serviceWorker.controller);
 const oldResponse=await page.reload({waitUntil:'load'});
 check('Existing cache serves the old shell',sha(await oldResponse.body())===sha(oldHTML));
 upgraded=true;
 await page.evaluate(async()=>{const registration=await navigator.serviceWorker.getRegistration();await registration.update();});
 await page.evaluate(async({cacheName,oldCache})=>{const end=Date.now()+30000;while(Date.now()<end){const keys=await caches.keys(),registration=await navigator.serviceWorker.getRegistration();if(keys.includes(cacheName)&&!keys.includes(oldCache)&&registration?.active?.state==='activated')return;await new Promise(resolve=>setTimeout(resolve,50));}throw Error('Worker activation and old-cache removal did not complete');},{cacheName,oldCache});
 const cached=await page.evaluate(async cacheName=>{const cache=await caches.open(cacheName);const response=await cache.match('./index.html');const bytes=await response.arrayBuffer();const hash=await crypto.subtle.digest('SHA-256',bytes);return{sha256:Array.from(new Uint8Array(hash),b=>b.toString(16).padStart(2,'0')).join(''),bytes:bytes.byteLength,firstBytes:Array.from(new Uint8Array(bytes).slice(0,12))};},cacheName);
 report.cacheSnapshot=await page.evaluate(async()=>{const result={};for(const name of await caches.keys()){const cache=await caches.open(name);result[name]=await Promise.all((await cache.keys()).map(async r=>({url:r.url,bytes:(await(await cache.match(r)).arrayBuffer()).byteLength})));}return result;});
 check('Updated worker stores rebuilt production HTML',cached.sha256===htmlSHA,cached);
 check('Previous cache is removed',!(await page.evaluate(()=>caches.keys())).includes(oldCache));
 await context.setOffline(true);
 const response=await page.goto(origin+'/index.html',{waitUntil:'domcontentloaded'});
 check('Offline navigation receives the rebuilt game',sha(await response.body())===htmlSHA);
 const missing=await page.evaluate(async()=>{const r=await fetch('/data/qa-missing.json');return{status:r.status,text:await r.text()};});
 check('Missing map data remains an explicit failure offline',missing.status===503&&!missing.text.includes('<html'),missing);
 await context.close();
})().catch(e=>{report.exception=String(e.stack||e);console.error(report.exception);process.exitCode=1;}).finally(async()=>{
 if(browser)await browser.close().catch(()=>{});await new Promise(r=>server.close(r));
 report.passed=report.checks.filter(c=>c.ok).length;report.failed=Math.max(report.checks.filter(c=>!c.ok).length,report.exception?1:0);
 fs.writeFileSync(path.join(out,'SERVICE_WORKER.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,failed:report.failed}));
});
