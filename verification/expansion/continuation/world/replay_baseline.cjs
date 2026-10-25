/* Controlled regression replay: baseline production source, current tests. */
const fs=require('node:fs'),path=require('node:path');
const root=process.env.MISTRAL_REPO_ROOT||'/workspace/fallout-Marseille',baseline=path.join(__dirname,'baseline');
const sources=new Set(['src/v046/02_environment.js','src/v050/04a_city_sources.js','src/v050/04aa_city_water.js']);
const suite=process.argv[2];if(!['world_placements.cjs','city_streaming.cjs','city_water.cjs'].includes(suite))throw Error('Unknown baseline suite');
const original=fs.readFileSync;
fs.readFileSync=function(file,options){if(typeof file==='string'){const relative=path.relative(root,file);if(sources.has(relative))return original.call(fs,path.join(baseline,relative),options);}return original.call(fs,file,options);};
require(path.join(root,'tests/expansion',suite));
