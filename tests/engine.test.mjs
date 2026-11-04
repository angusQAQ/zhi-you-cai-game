import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {AnimationQueue,newRound,roles,choose,perform,place,remove,verdict,checkTrain,canAdvance} from '../dist/engine.js';
const content=JSON.parse(readFileSync(new URL('../dist/content.json',import.meta.url)));
test('10 life questions, five conditions then five results; updated wording',()=>{
 assert.equal(content.life.length,10);assert.deepEqual(content.life.map(q=>q.mode),[...Array(5).fill('condition'),...Array(5).fill('result')]);
 assert.equal(content.life[0].sentence,'小明只有打開水樽蓋，才可以喝水。');
 assert.equal(content.life[3].sentence,'我們只有拿出車票，才可以坐火車。');
 assert(!JSON.stringify(content).includes('鑰匙'));assert(!JSON.stringify(content).includes('小島火車'));
 for(const q of content.life){assert.equal(new Set(q.options).size,3);assert.equal(q.options.filter(id=>id===q.correct).length,1);assert.equal(content.words[q.correct].text,q[q.mode]);assert.equal(q.frames,16);}
 assert.equal(new Set(content.life.map(q=>q.options.indexOf(q.correct))).size,3);
});
test('all sentences have subjects, proper punctuation and matching audio/reviews',()=>{
 for(const q of [...content.life,...content.train]){
  assert.equal(q.sentence,`${q.subject}只有${q.condition}，才${q.result}。`);assert(!q.sentence.startsWith('只有'));assert.equal(content.audio[q.audio].text,q.sentence);
 }
 assert.equal(new Set([...content.life,...content.train].map(q=>q.id)).size,15);
});
test('train fixed semantic chunks, seven/eight carriages, independent punctuation',()=>{
 assert.equal(content.train.length,5);assert.deepEqual(content.train.map(q=>q.showLengthHints),[true,true,true,false,false]);
 const expected=[['我','只有','打開盒蓋','，','才','可以拿出','盒內的餅乾','。'],['雨傘','只有','打開','，','才','可以擋雨','。'],['小明','只有','打開','膠水蓋','，','才','可以塗膠水','。'],['我','只有','投入硬幣','，','才','可以買到','果汁','。'],['小花','只有','得到水分','，','才','可以繼續','生長','。']];
 content.train.forEach((q,i)=>{const text=q.tokens.map(id=>content.words[id].text);assert.deepEqual(text,expected[i]);assert.equal(text.join(''),q.sentence);assert.equal(new Set(q.tokens).size,q.tokens.length);});
 for(const w of Object.values(content.words)){assert(!/[1-6]/.test(w.jyutping));if('，。'.includes(w.text)){assert.equal(w.jyutping,'');assert.equal(w.picture,null);}else{assert(w.jyutping);assert(w.picture);}assert.equal(content.audio[w.audio].text,({'，':'逗號','。':'句號'}[w.text]||w.text));}
});
test('wrong life choice retries, correct cannot auto-act or be overwritten',()=>{
 const g=newRound('life',0,content),wrong=g.q.options.find(id=>id!==g.q.correct);assert.equal(perform(g),false);assert.equal(choose(g,wrong),false);assert.equal(g.phase,'choosing');assert.equal(perform(g),false);assert.equal(choose(g,g.q.correct),true);assert.equal(g.phase,'selected');assert.equal(choose(g,wrong),null);assert.equal(perform(g),true);assert.equal(perform(g),false);assert.equal(g.phase,'acting');
});
test('cooperative roles alternate; pause forbids input and requires both completion gates',()=>{
 for(let i=0;i<10;i++){const r=roles(i);assert.notEqual(r.chooser,r.actor);if(i)assert.notEqual(r.chooser,roles(i-1).chooser);}
 const g=newRound('life',0,content);g.paused=true;assert.equal(choose(g,g.q.correct),null);g.animationDone=true;g.speechDone=true;assert.equal(canAdvance(g),false);g.paused=false;assert.equal(canAdvance(g),true);g.speechDone=false;assert.equal(canAdvance(g),false);
});
test('clock freezes exact position and pending jobs; clear cancels stale events',()=>{
 const clock=new AnimationQueue(),events=[];clock.after(100,()=>events.push(1));clock.after(200,()=>events.push(2));clock.tick(50);clock.paused=true;clock.tick(99999);assert.equal(clock.position,50);assert.deepEqual(events,[]);clock.paused=false;clock.tick(50);assert.deepEqual(events,[1]);clock.clear();clock.tick(300);assert.deepEqual(events,[1]);
});
test('train swaps without duplicating cards, removes to bank and preserves other slots',()=>{
 const g=newRound('train',0,content),[a,b]=g.q.tokens;assert(place(g,a,0));assert(place(g,b,1));assert(place(g,a,1));assert.deepEqual(g.slots.slice(0,2),[b,a]);assert(remove(g,a));assert.equal(g.slots[0],b);assert.equal(g.slots[1],null);assert.equal(remove(g,a),false);assert.equal(place(g,'foreign',1),false);
});
test('two pointers reserve distinct cards and occupied destinations; defer checks',()=>{
 const g=newRound('train',0,content),[a,b]=g.q.tokens;place(g,b,1);g.drags.set(1,{id:a});g.drags.set(2,{id:b});assert.equal(place(g,a,1),false);assert.equal(remove(g,b),false);g.q.tokens.forEach((id,i)=>g.slots[i]=id);assert.equal(checkTrain(g),null);g.drags.delete(1);assert.equal(checkTrain(g),null);g.drags.clear();assert.equal(checkTrain(g).correct,true);assert.equal(g.phase,'departing');assert.equal(place(g,a,1),false);
});
test('train error reports positions without replacing student arrangement',()=>{
 const g=newRound('train',2,content);g.slots=[...g.q.tokens];[g.slots[0],g.slots[1]]=[g.slots[1],g.slots[0]];const before=[...g.slots];const v=checkTrain(g);assert.equal(v.correct,false);assert.deepEqual(v.wrong,[0,1]);assert.deepEqual(g.slots,before);assert.equal(g.phase,'assembling');assert.equal(verdict(g).complete,true);
});
