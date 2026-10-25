import test from 'node:test';import assert from 'node:assert/strict';
import {RehearsalState} from '../player_state.mjs';
const model={pages:['one','two'],boundaries:[9],measures:[{number:0,start:-1.5,end:0,id:'pickup',page:0},{number:1,start:0,end:9,id:'one',page:0},{number:2,start:9,end:12,id:'two',page:1}]};
const events=[{time:1,beat:0},{time:2,beat:7},{time:3,beat:6.8},{time:4,beat:9},{time:5,beat:8.8}];
test('pickup and all crossed events, preview retains outgoing page',()=>{let s=new RehearsalState(model,events);assert.equal(s.at(0).measure.number,0);let v=s.at(2.1);assert.equal(v.page,0);assert.equal(v.preview,1);assert.equal(s.at(3).preview,1);assert.equal(s.fired.size,1);assert.equal(s.at(4).page,1);assert.equal(s.at(5).page,1);});
test('pause time stable, manual recovery, rejoin, restart',()=>{let s=new RehearsalState(model,events);assert.deepEqual(s.at(2),s.at(2));s.manual(1);assert.equal(s.at(2).page,1);s.auto=true;assert.equal(s.at(2).page,0);s.at(5);s.reset();assert.equal(s.at(0).page,0);assert.equal(s.fired.size,0);assert.equal(s.at(2).preview,1);});
test('seek backwards resets consumed events',()=>{let s=new RehearsalState(model,events);s.at(5);assert.equal(s.at(1).page,0);assert.equal(s.at(2).preview,1);});
