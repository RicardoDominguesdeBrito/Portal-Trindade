import {test} from 'node:test';
import assert from 'node:assert/strict';
import {productionAccount, productionReady} from '../src/production.js';
import {extract, SolInbox} from '../src/worker.js';
import {inHours} from '../src/protocol.js';

const env={MODE:'production',PRODUCTION_ENABLED:'true',RECIPIENT_SCOPE:'all-inbound',WABA_ID:productionAccount.waba,PHONE_NUMBER_ID:productionAccount.phone,TEST_PHONE_NUMBER_ID:'1315171965023813',WHATSAPP_TOKEN:'fake-test-token',START_HOUR:'0',END_HOUR:'24',GRAPH_VERSION:'v25.0'};
const from='5511999999999';
const message={id:'production-inbound-1',from,type:'text',text:'Olá',at:Date.now()};
function payload(account=env.WABA_ID, phone=env.PHONE_NUMBER_ID) {
  return {object:'whatsapp_business_account',entry:[{id:account,changes:[{field:'messages',value:{metadata:{phone_number_id:phone},messages:[{...message,timestamp:String(Date.now()/1000),text:{body:'Olá'}}]}}]}]};
}
class Store {
  values=new Map(); alarmAt=null;
  async get(k){return structuredClone(this.values.get(k));}
  async put(k,v){if(typeof k==='object')for(const [key,value] of Object.entries(k))this.values.set(key,structuredClone(value));else this.values.set(k,structuredClone(v));}
  async list({prefix='',limit=1000}={}){return new Map([...this.values].filter(([k])=>k.startsWith(prefix)).slice(0,limit));}
  async getAlarm(){return this.alarmAt;}
  async setAlarm(t){this.alarmAt=t;}
  async delete(k){this.values.delete(k);}
}
test('production refuses disabled, missing credentials, wrong assets and unknown recipient scope',()=>{
  for(const change of [{PRODUCTION_ENABLED:'false'},{WHATSAPP_TOKEN:''},{WABA_ID:'wrong'},{PHONE_NUMBER_ID:env.TEST_PHONE_NUMBER_ID},{RECIPIENT_SCOPE:'*'}]){
    const invalid={...env,...change};assert.equal(productionReady(invalid),false);assert.equal(extract(payload(),invalid).length,0);
  }
});
test('all-inbound receives only the chosen official account and phone; allowlist remains default boundary',()=>{
  assert.equal(extract(payload(),env).length,1);
  assert.equal(extract(payload('other'),env).length,0);
  assert.equal(extract(payload(env.WABA_ID,'other'),env).length,0);
  assert.equal(extract(payload(),{...env,RECIPIENT_SCOPE:'allowlist'}).length,0);
  assert.equal(extract(payload(),{...env,RECIPIENT_SCOPE:'allowlist',ALLOWED_SENDERS:from}).length,1);
});
test('24-hour configuration works across midnight in São Paulo',()=>{
  for(const at of ['2026-11-03T03:00:00Z','2026-11-04T02:59:00Z'])assert.equal(inHours(env,new Date(at)),true);
});
test('production remains paused by default and explicit resume preserves deduplication and human takeover',async()=>{
  const db=new Store(),box=new SolInbox({storage:db,blockConcurrencyWhile:fn=>fn()},env);
  const enqueue=()=>box.fetch(new Request('https://internal/enqueue',{method:'POST',body:JSON.stringify([message])}));
  const original=globalThis.fetch;let calls=0;
  globalThis.fetch=async(url,options)=>{calls++;assert.equal(url,'https://graph.facebook.com/v25.0/'+env.PHONE_NUMBER_ID+'/messages');assert.equal(JSON.parse(options.body).to,from);return Response.json({messages:[{id:'outbound-1'}]});};
  try{
    await enqueue();await box.alarm();assert.equal(calls,0);
    await db.put('paused',false);await box.alarm();await enqueue();await box.alarm();assert.equal(calls,1);
    await db.put('chat:'+from,{paused:true,reason:'owner'});
    await db.put('job:held',{...message,id:'second',status:'queued'});await box.alarm();assert.equal(calls,1);assert.equal((await db.get('job:held')).status,'held');
  }finally{globalThis.fetch=original;}
});
test('queued production cannot send after the gate is disabled',async()=>{
  const db=new Store(),box=new SolInbox({storage:db,blockConcurrencyWhile:fn=>fn()},{...env,PRODUCTION_ENABLED:'false'});
  await db.put('paused',false);await db.put('job:disabled',{...message,status:'queued'});
  const original=globalThis.fetch;globalThis.fetch=()=>{throw new Error('must not call network');};
  try{await box.alarm();assert.equal((await db.get('job:disabled')).status,'blocked-production-config');}finally{globalThis.fetch=original;}
});
