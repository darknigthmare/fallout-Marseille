'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const M=require('../../src/v050/19_fps_hud.js');
const overlap=(a,b)=>a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;
const inside=(r,w,h)=>r&&r.x>=12&&r.y>=12&&r.x+r.w<=w-12&&r.y+r.h<=h-12;
test('a short landscape suit notice fits beside the actual top-right assistance and objective columns',()=>{
 const blocks=[{x:658,y:120,w:170,h:40},{x:615,y:22,w:205,h:90},{x:538,y:120,w:108,h:32},{x:16,y:84,w:200,h:56},{x:409,y:182,w:26,h:26},{x:16,y:237,w:170,h:81},{x:658,y:209,w:170,h:110},{x:24,y:321,w:796,h:44}];
 const r=M.notificationSlot(844,390,{x:530,y:80,w:290,h:56,minH:56},blocks);
 assert.ok(inside(r,844,390));assert.equal(r.scroll,false);assert.ok(blocks.every(b=>!overlap(r,b)));assert.ok(r.x<530);
});
test('a portrait notification avoids both primary panels and can move to the other free column',()=>{
 const blocks=[{x:211,y:270,w:165,h:63},{x:14,y:650,w:155,h:70},{x:211,y:630,w:165,h:110},{x:14,y:775,w:362,h:44}];
 const r=M.notificationSlot(390,844,{x:201,y:278,w:175,h:56,minH:56},blocks);assert.ok(inside(r,390,844));assert.equal(r.scroll,false);assert.ok(blocks.every(b=>!overlap(r,b)));
});
test('a fully readable stack takes priority over a closer but shortened scroll region',()=>{
 const blocks=[{x:600,y:70,w:180,h:260}];const r=M.notificationSlot(844,390,{x:640,y:120,w:180,h:180,minH:44},blocks);
 assert.equal(r.scroll,false);assert.equal(r.h,180);assert.ok(!overlap(r,blocks[0]));
});
test('a crowded viewport returns a bounded scroll region while retaining the original content height',()=>{
 const box={x:16,y:100,w:280,h:500,minH:44},before=structuredClone(box),blocks=[{x:0,y:0,w:390,h:80},{x:0,y:200,w:390,h:400}];
 const r=M.notificationSlot(390,600,box,blocks);assert.ok(inside(r,390,600));assert.equal(r.scroll,true);assert.equal(r.h,104);assert.deepEqual(box,before);assert.ok(blocks.every(b=>!overlap(r,b)));
});
test('overlapping obstacle intervals are merged before choosing a free strip',()=>{
 const blocks=[{x:0,y:40,w:400,h:80},{x:0,y:100,w:400,h:100},{x:0,y:260,w:400,h:100}];
 const r=M.notificationSlot(400,400,{x:50,y:100,w:300,h:44,minH:44},blocks);assert.equal(r.y,208);assert.equal(r.h,44);assert.ok(blocks.every(b=>!overlap(r,b)));
});
test('no sufficiently tall region is reported explicitly instead of inventing a hidden or clipped message',()=>{
 assert.equal(M.notificationSlot(390,200,{w:300,h:60,minH:60},[{x:0,y:0,w:390,h:200}]),null);
 for(const b of[{w:0,h:50},{w:500,h:50},{w:300,h:0},{w:NaN,h:50}])assert.equal(M.notificationSlot(390,200,b),null);
});
test('empty, invalid and offscreen obstacles do not corrupt a valid notification placement',()=>{
 const r=M.notificationSlot(390,844,{x:999,y:-20,w:180,h:70},[null,{x:NaN,y:0,w:200,h:200},{x:0,y:0,w:0,h:900},{x:0,y:-100,w:390,h:20}]);
 assert.ok(inside(r,390,844));assert.equal(r.scroll,false);assert.equal(r.x,198);assert.equal(r.y,12);
});
test('placement is deterministic and never edits source obstacle rectangles',()=>{
 const box={x:180,y:300,w:175,h:55},blocks=[{x:0,y:200,w:200,h:200},{x:240,y:250,w:150,h:100}],before=structuredClone(blocks);
 assert.deepEqual(M.notificationSlot(390,844,box,blocks),M.notificationSlot(390,844,box,blocks));assert.deepEqual(blocks,before);
});
