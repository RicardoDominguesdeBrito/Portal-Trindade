import {answer, inHours} from './protocol.js';
import {adminPage} from './admin-page.js';
import {productionReady, senderAllowed} from './production.js';

const json = (body, status=200) => new Response(JSON.stringify(body), {status, headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff'}});
const digits = x => /^\d{8,20}$/.test(x || '');
const enc = new TextEncoder();
export async function signatureValid(raw, signature, secret) {
  if (!secret || !/^sha256=[a-f0-9]{64}$/.test(signature || '')) return false;
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), {name:'HMAC',hash:'SHA-256'}, false, ['verify']);
  const sig = Uint8Array.from(signature.slice(7).match(/../g), h => parseInt(h,16));
  return crypto.subtle.verify('HMAC', key, sig, raw);
}
async function equal(a,b) {
  if (!a || !b) return false;
  const hash = x => crypto.subtle.digest('SHA-256', enc.encode(x));
  const [x,y] = await Promise.all([hash(a),hash(b)]);
  let mismatch=0;
  const aa=new Uint8Array(x), bb=new Uint8Array(y);
  for(let i=0;i<aa.length;i++) mismatch |= aa[i]^bb[i];
  return mismatch===0;
}
export function extract(payload, env, now=Date.now()) {
  const result=[];
  if(payload?.object !== 'whatsapp_business_account' || !env.WABA_ID || !env.PHONE_NUMBER_ID) return result;
  for (const entry of payload.entry || []) {
    if (entry.id !== env.WABA_ID) continue;
    for (const change of entry.changes || []) {
      const value=change.value;
      if(change.field !== 'messages' || value?.metadata?.phone_number_id !== env.PHONE_NUMBER_ID) continue;
      for(const m of value.messages || []) {
        const age=now/1000-Number(m.timestamp);
        if(!digits(m.from) || !senderAllowed(env,m.from) || !m.id || m.id.length>256 || !Number.isFinite(age) || age< -60 || age>Number(env.MAX_AGE_SECONDS || 600)) continue;
        if(!['text','image','video','audio','document','sticker','location','contacts','interactive','button'].includes(m.type)) continue;
        result.push({id:m.id,from:m.from,type:m.type,text:(m.text?.body || '').slice(0,4096),at:Number(m.timestamp)*1000});
      }
    }
  }
  return result;
}
async function limitedBody(request, limit=262144) {
  const reader=request.body?.getReader();
  if(!reader) return new Uint8Array();
  const chunks=[]; let size=0;
  while(true) { const {value,done}=await reader.read(); if(done) break; size+=value.length; if(size>limit){await reader.cancel(); throw new Error('too-large');} chunks.push(value); }
  const all=new Uint8Array(size); let offset=0;
  for(const chunk of chunks){all.set(chunk,offset);offset+=chunk.length;}
  return all;
}
export default {
  async fetch(request, env) {
    const url=new URL(request.url);
    if(url.pathname==='/console' && request.method==='GET') return new Response(adminPage,{headers:{'content-type':'text/html; charset=utf-8','cache-control':'no-store','x-frame-options':'DENY','referrer-policy':'no-referrer','content-security-policy':"default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"}});
    if(url.pathname==='/health' && request.method==='GET') {
      const id=env.SOL.idFromName('sol-single-executor');
      return env.SOL.get(id).fetch(new Request('https://sol.internal/health'));
    }
    if(url.pathname==='/webhook' && request.method==='GET') {
      if(url.searchParams.get('hub.mode')!=='subscribe' || !await equal(url.searchParams.get('hub.verify_token'),env.VERIFY_TOKEN)) return json({error:'forbidden'},403);
      return new Response(url.searchParams.get('hub.challenge') || '',{headers:{'cache-control':'no-store'}});
    }
    if(url.pathname.startsWith('/admin/')) {
      if(!env.ADMIN_TOKEN || env.ADMIN_TOKEN.length<32 || !await equal(request.headers.get('authorization'),'Bearer '+env.ADMIN_TOKEN)) return json({error:'unauthorized'},401);
      if(!['GET','POST'].includes(request.method)) return json({error:'method'},405);
      const id=env.SOL.idFromName('sol-single-executor');
      return env.SOL.get(id).fetch(request);
    }
    if(url.pathname!=='/webhook' || request.method!=='POST') return json({error:'not-found'},404);
    let raw;
    try{raw=await limitedBody(request);}catch{return json({error:'body-too-large'},413);}
    if(!await signatureValid(raw, request.headers.get('x-hub-signature-256'),env.META_APP_SECRET)) return json({error:'invalid-signature'},401);
    let payload;
    try{payload=JSON.parse(new TextDecoder().decode(raw));}catch{return json({error:'invalid-json'},400);}
    let messages;
    try{messages=extract(payload,env);}catch{return json({error:'invalid-payload'},400);}
    if(!messages.length) return json({accepted:0});
    const id=env.SOL.idFromName('sol-single-executor');
    // Persist before acknowledging: a failed storage call makes Meta retry.
    return env.SOL.get(id).fetch(new Request('https://sol.internal/enqueue',{method:'POST',body:JSON.stringify(messages)}));
  }
};

// One Durable Object serializes admin actions, delivery and deduplication.
// Network operations have a 12s bound, below blockConcurrencyWhile's 30s limit.
export class SolInbox {
  constructor(ctx, env) { this.ctx=ctx; this.db=ctx.storage; this.env=env; }
  async fetch(request) {
    return this.ctx.blockConcurrencyWhile(async()=>{
      try { return await this.route(request); }
      catch { return json({error:'operation-failed'},500); }
    });
  }
  async route(request) {
    const url=new URL(request.url);
    if(url.pathname==='/health' && request.method==='GET') {
      // Publish only operational booleans, never IDs, tokens or customer records.
      // Persisted cache bounds the Meta read to one request per minute.
      const key='health:phone', now=Date.now(), env=this.env;
      let check=await this.db.get(key);
      if(!check || now-check.at>60000 || check.phone!==env.PHONE_NUMBER_ID) {
        let accessible=false,errorCode=null;
        if(env.WHATSAPP_TOKEN && digits(env.PHONE_NUMBER_ID)) {
          try {
            const response=await fetch('https://graph.facebook.com/'+env.GRAPH_VERSION+'/'+env.PHONE_NUMBER_ID+'?fields=id',{
              headers:{authorization:'Bearer '+env.WHATSAPP_TOKEN},signal:AbortSignal.timeout(8000)
            });
            const data=await response.json();
            accessible=response.ok && data.id===env.PHONE_NUMBER_ID;
            errorCode=accessible?null:(Number(data?.error?.code)||null);
          } catch {errorCode=null;}
        }
        check={at:now,phone:env.PHONE_NUMBER_ID,accessible,errorCode};
        await this.db.put(key,check);
      }
      return json({service:'Sol',alive:true,mode:env.MODE||'dry-run',productionConfigured:productionReady(env),
        paused:(await this.db.get('paused'))!==false,phoneApiAccessible:check.accessible,apiErrorCode:check.errorCode});
    }
    if(url.pathname==='/enqueue' && request.method==='POST') {
      const incoming=await request.json();
      const active=await this.db.list({prefix:'job:',limit:501});
      if(active.size+incoming.length>500) return json({error:'queue-full'},503);
      let accepted=0;
      for(const m of incoming) {
        const key='seen:'+m.id;
        if(await this.db.get(key)) continue;
        const jobKey='job:'+String(Date.now()).padStart(16,'0')+':'+m.id;
        await this.db.put({[key]:{at:Date.now()},[jobKey]:{...m,status:'queued',received:Date.now()}});
        accepted++;
      }
      // Fresh inbound must preempt the idle daily cleanup alarm. Preserve an
      // earlier wake-up; scheduling never changes pause/opt-out permissions.
      const wakeAt=Date.now()+1000, alarmAt=await this.db.getAlarm();
      if(alarmAt===null || alarmAt===undefined || (accepted>0 && alarmAt>wakeAt)) await this.db.setAlarm(wakeAt);
      return json({accepted});
    }
    if(url.pathname==='/admin/status' && request.method==='GET') {
      const jobs=await this.db.list({prefix:'job:',limit:100});
      const chats=await this.db.list({prefix:'chat:',limit:100});
      const testUntil=(await this.db.get('testUntil')) || 0;
      return json({paused:(await this.db.get('paused'))!==false, mode:this.env.MODE || 'dry-run', testUntil,testActive:testUntil>Date.now(),
        jobs:[...jobs].map(([key,j])=>({key,...j})),chats:[...chats].map(([key,c])=>({key,...c}))});
    }
    if(request.method!=='POST') return json({error:'not-found'},404);
    const raw=await limitedBody(request,8192);
    let body; try{body=JSON.parse(new TextDecoder().decode(raw));}catch{return json({error:'invalid-json'},400);}
    if(url.pathname==='/admin/test') {
      if(!Number.isInteger(body.minutes) || body.minutes<1 || body.minutes>15) return json({error:'minutes-1-to-15'},400);
      if(!this.env.WHATSAPP_TOKEN || !this.env.TEST_PHONE_NUMBER_ID || this.env.PHONE_NUMBER_ID!==this.env.TEST_PHONE_NUMBER_ID || !(this.env.ALLOWED_SENDERS || '').trim()) return json({error:'test-configuration-incomplete'},409);
      const now=Date.now(), until=now+body.minutes*60000;
      await this.db.put({paused:false,testUntil:until,testStarted:now});
      await this.db.setAlarm(now+1000);
      return json({testActive:true,expiresAt:new Date(until).toISOString(),scope:'test-number-and-allowlist-only'});
    }
    if(url.pathname==='/admin/pause') {
      if(typeof body.paused!=='boolean') return json({error:'boolean-required'},400);
      await this.db.put('paused',body.paused);
      if(!body.paused) await this.db.setAlarm(Date.now()+1000);
      return json({paused:body.paused});
    }
    if(url.pathname==='/admin/chat') {
      if(!digits(body.from) || typeof body.paused!=='boolean') return json({error:'invalid-chat'},400);
      const key='chat:'+body.from, chat=(await this.db.get(key)) || {};
      await this.db.put(key,{...chat,paused:body.paused,reason:body.paused?'owner':'',updated:Date.now()});
      return json({ok:true});
    }
    return json({error:'not-found'},404);
  }
  async alarm() {
    return this.ctx.blockConcurrencyWhile(async()=>{
      // Mark before any outbound side effect. Never resend processing/uncertain records.
      try {
        const now=Date.now();
        await this.cleanup(now);
        const jobs=await this.db.list({prefix:'job:',limit:500});
        for(const [key,j] of jobs) if(j.status==='processing') await this.db.put(key,{...j,status:'uncertain',updated:now});
        if((await this.db.get('paused'))!==false) return;
        const next=[...jobs].find(([,j])=>j.status==='queued');
        if(next) await this.process(...next);
      } finally {
        const jobs=await this.db.list({prefix:'job:',limit:500});
        const pending=[...jobs.values()].some(j=>j.status==='queued');
        const running=(await this.db.get('paused'))===false;
        await this.db.setAlarm(Date.now()+(pending && running?1000:86400000));
      }
    });
  }
  async process(key,j) {
    const env=this.env;
    const testUntil=(await this.db.get('testUntil')) || 0;
    const temporaryTest=testUntil>Date.now();
    const mode=temporaryTest?'test':env.MODE;
    const chatKey='chat:'+j.from, chat=(await this.db.get(chatKey)) || {};
    const finish=async(status,extra={})=>this.db.put(key,{...j,status,updated:Date.now(),...extra,text:undefined});
    if(chat.paused) return finish('held');
    if(Date.now()-j.at>Number(env.MAX_AGE_SECONDS || 600)*1000) return finish('expired');
    if(temporaryTest && j.at<((await this.db.get('testStarted')) || 0)-5000) return finish('before-test');
    if(!temporaryTest && !inHours(env)) return finish('outside-hours');
    const decision=answer(j,chat);
    if(decision.text===chat.lastReply) return finish('duplicate-answer');
    if(chat.lastSent && Date.now()-chat.lastSent<5000 && !decision.pause) return finish('rate-limited');
    if(!['dry-run','test','production'].includes(mode)) return finish('blocked-mode');
    if(mode==='production' && !productionReady(env)) return finish('blocked-production-config');
    if(mode==='production' && !senderAllowed(env,j.from)) return finish('not-allowlisted');
    if(mode==='test' && (!env.WHATSAPP_TOKEN || !digits(env.PHONE_NUMBER_ID))) return finish('missing-credentials');
    if(mode==='test' && !(env.ALLOWED_SENDERS || '').split(',').map(s=>s.trim()).includes(j.from)) return finish('not-allowlisted');
    if(mode==='test' && env.PHONE_NUMBER_ID!==env.TEST_PHONE_NUMBER_ID) return finish('blocked-production-number');
    // Commit handoff/triage state only with planned/sent result, not with an unsent draft.
    const updated={...chat,stage:decision.nextStage || chat.stage,greeted:true,lastReply:decision.text,lastSent:Date.now(),updated:Date.now(),
      business:decision.business || chat.business,instagram:decision.instagram || chat.instagram,objective:decision.objective || chat.objective,
      paused:!!decision.pause,reason:decision.pause || ''};
    if(mode==='dry-run') {
      await this.db.put(chatKey,updated);
      return finish('draft',{draft:decision.text});
    }
    await this.db.put(key,{...j,status:'processing',updated:Date.now()});
    let response, data;
    try {
      response=await fetch('https://graph.facebook.com/'+env.GRAPH_VERSION+'/'+env.PHONE_NUMBER_ID+'/messages',{
        method:'POST',headers:{'authorization':'Bearer '+env.WHATSAPP_TOKEN,'content-type':'application/json'},signal:AbortSignal.timeout(12000),
        body:JSON.stringify({messaging_product:'whatsapp',to:j.from,type:'text',text:{body:decision.text,preview_url:false}})
      });
      data=await response.json();
    } catch { return finish('uncertain'); }
    if(!response.ok) return finish('failed',{httpStatus:response.status,errorCode:Number(data?.error?.code)||null});
    if(!data?.messages?.[0]?.id) return finish('uncertain');
    await this.db.put(chatKey,updated);
    return finish('sent',{outboundId:data.messages[0].id});
  }
  async cleanup(now) {
    // Bounded reads; each delivery is capped by the 500-record operational queue.
    for(const prefix of ['job:','chat:','seen:']) {
      const entries=await this.db.list({prefix,limit:1000});
      const ttl=prefix==='seen:'?30*86400000:7*86400000;
      for(const [key,value] of entries) {
        if(prefix==='chat:' && value.paused) continue; // preserve opt-out/owner takeover
        if(now-(value.updated || value.received || value.at || now)>ttl) await this.db.delete(key);
      }
    }
  }
}

