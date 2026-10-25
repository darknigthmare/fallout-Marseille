'use strict';
// Run the exact archived test bytes with their original repository path
// resolution. No HTML, map request, game state, or source geometry is mocked.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(process.env.MISTRAL_REPO_ROOT||process.cwd()),output=path.resolve(process.env.MISTRAL_AUDIT_OUTPUT_DIR||__dirname),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const expected={'src/v050/07_facades.js':process.env.MISTRAL_EXPECT_FACADE_SHA||'855db991e5053752a7d1a366cac3610f6ea7b304461e448d99e45362a49eb432','src/v050/08_city_interiors.js':process.env.MISTRAL_EXPECT_INTERIOR_SHA||'1f5c099bc4082baa6c64660fe6aacb22a52b839b2cbdaf0ce29cb55a4fbc83bf'};
for(const[name,hash]of Object.entries(expected))if(sha(fs.readFileSync(path.join(root,name)))!==hash)throw Error('Frozen production module changed: '+name);
const bootstrap="const fs=require('node:fs'),path=require('node:path'),Module=require('node:module');const original=process.argv[1],snapshot=process.argv[2],m=new Module(original,module);m.filename=original;m.paths=Module._nodeModulePaths(path.dirname(original));m._compile(fs.readFileSync(snapshot,'utf8'),original);";
const rows=[];fs.mkdirSync(output,{recursive:true});
for(const[name,count]of[['facades_model.cjs',89],['facades_coverage.cjs',19]]){
 const original=path.join(root,'tests/expansion',name),snapshot=path.join(__dirname,'EXECUTED_'+name),bytes=fs.readFileSync(snapshot);if(sha(bytes)!==sha(fs.readFileSync(original)))throw Error('The archived test differs from the frozen repository: '+name);
 const result=spawnSync(process.execPath,['-e',bootstrap,original,snapshot],{cwd:root,encoding:'utf8',timeout:120000});
 const logName=name+'.log',log='COMMAND '+JSON.stringify([process.execPath,'-e',bootstrap,original,snapshot])+'\n'+result.stdout+'\nSTDERR\n'+result.stderr;fs.writeFileSync(path.join(output,logName),log);
 if(result.error||result.status!==0)throw result.error||Error('Test process failed: '+name+' ('+result.status+')');const summaries=result.stdout.trim().split('\n').filter(line=>line.startsWith('{"passed":')).map(JSON.parse);if(summaries.length!==1||summaries[0].passed!==count||summaries[0].failed!==0)throw Error('Unexpected test summary: '+name);
 rows.push({name,passed:count,failed:0,exitCode:result.status,scriptSha256:sha(bytes),archive:'EXECUTED_'+name,log:logName,logSha256:sha(Buffer.from(log)),execution:'Unmodified archived test bytes compiled with their original module filename; relative imports resolve to the frozen repository.'});
}
for(const[name,hash]of Object.entries(expected))if(sha(fs.readFileSync(path.join(root,name)))!==hash)throw Error('Production changed during tests: '+name);
const report={scope:'Production facade model/runtime hooks and three pinned real IGN source fixtures. Documentary plans and synthetic corner/clearance/stress fixtures remain explicit; this is not a native browser playthrough.',stage:'complete',passed:rows.reduce((n,r)=>n+r.passed,0),failed:0,modules:expected,nodeVersion:process.version,executedRunnerSha256:sha(fs.readFileSync(__filename)),rows};fs.writeFileSync(path.join(output,'FACADES_TESTS.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
