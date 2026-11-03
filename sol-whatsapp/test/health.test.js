import {test} from 'node:test';
import assert from 'node:assert/strict';
import {SolInbox} from '../src/worker.js';
test('health checks token privately, caches reads and exposes no customer or credential data',async()=>{
  const values=new Map(),db={get:async k=>values.get(k),put:async(k,v)=>values.set(k,v)};
  const env={MODE:'dry-run',PHONE_NUMBER_ID:'1087653641089631',GRAPH_VERSION:'v25.0',WHATSAPP_TOKEN:'fake-private-token'};
  const box=new SolInbox({storage:db,blockConcurrencyWhile:fn=>fn()},env);
  let calls=0;const original=globalThis.fetch;
  globalThis.fetch=async(url,opts)=>{calls++;assert.equal(opts.headers.authorization,'Bearer fake-private-token');return Response.json({id:env.PHONE_NUMBER_ID});};
  try{
    const request=()=>new Request('https://internal/health');
    const first=await (await box.fetch(request())).json();
    assert.equal(first.phoneApiAccessible,true);assert.equal(first.paused,true);assert.equal(first.productionConfigured,false);
    await box.fetch(request());assert.equal(calls,1);
    assert.doesNotMatch(JSON.stringify(first),/fake-private-token|1087653641089631|jobs|chats/);
    values.get('health:phone').at=0;
    globalThis.fetch=async()=>Response.json({error:{code:190,message:'sensitive details'}},{status:400});
    const expired=await (await box.fetch(request())).json();assert.equal(expired.phoneApiAccessible,false);assert.equal(expired.apiErrorCode,190);assert.doesNotMatch(JSON.stringify(expired),/sensitive details/);
  }finally{globalThis.fetch=original;}
});
