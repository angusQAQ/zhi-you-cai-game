// Adapted from yi-jiu-games' AnimationQueue and train placement model.
// One logical clock controls delayed events; no countdowns or game timers.
export class AnimationQueue {
  constructor(){this.position=0;this.paused=false;this.jobs=[];this.serial=0;}
  after(delay,fn){const token=++this.serial;this.jobs.push({at:this.position+delay,fn,token});return token;}
  tick(delta){if(this.paused)return;this.position+=Math.max(0,delta);const due=this.jobs.filter(j=>j.at<=this.position);this.jobs=this.jobs.filter(j=>j.at>this.position);for(const j of due.sort((a,b)=>a.at-b.at||a.token-b.token))j.fn();}
  clear(){this.jobs=[];}
}
export function newRound(type,index,content){const q=content[type][index];if(!q)throw new RangeError('No such question');return {type,index,q,clock:new AnimationQueue(),paused:false,phase:type==='life'?'choosing':'assembling',selected:null,wrong:[],slots:type==='train'?q.tokens.map(()=>null):[],drags:new Map(),animationDone:false,speechDone:false,advancing:false,startedAt:null,demo:0};}
export function roles(i){return {chooser:i%2+1,actor:(i+1)%2+1};}
export function choose(g,id){if(g.type!=='life'||g.paused||!['choosing','selected'].includes(g.phase)||!g.q.options.includes(id))return null;g.selected=id;const correct=id===g.q.correct;g.wrong=correct?[]:[id];g.phase=correct?'selected':'choosing';return correct;}
export function perform(g){if(g.paused||g.phase!=='selected')return false;g.phase='acting';g.startedAt=g.clock.position;return true;}
export function place(g,id,target){if(g.paused||g.phase!=='assembling'||!g.q.tokens.includes(id)||!Number.isInteger(target)||target<0||target>=g.slots.length)return false;const origin=g.slots.indexOf(id),occupant=g.slots[target];if(origin===target||[...g.drags.values()].some(d=>d.id===occupant||d.id===id))return false;if(origin>=0)g.slots[origin]=occupant;g.slots[target]=id;g.wrong=[];g.selected=null;return true;}
export function remove(g,id){if(g.paused||g.phase!=='assembling'||[...g.drags.values()].some(d=>d.id===id))return false;const i=g.slots.indexOf(id);if(i<0)return false;g.slots[i]=null;g.wrong=[];g.selected=null;return true;}
export function verdict(g){const complete=g.slots.length===g.q.tokens.length&&g.slots.every(Boolean),wrong=g.slots.flatMap((id,i)=>id!==g.q.tokens[i]?[i]:[]);return {complete,correct:complete&&wrong.length===0,wrong};}
export function checkTrain(g){if(g.paused||g.phase!=='assembling'||g.drags.size)return null;const v=verdict(g);if(!v.complete)return null;g.wrong=v.wrong;if(v.correct){g.phase='departing';g.startedAt=g.clock.position;}return v;}
export function canAdvance(g){return !g.paused&&g.animationDone&&g.speechDone&&!g.advancing;}
