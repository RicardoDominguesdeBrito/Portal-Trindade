// Local operator control. Never put the admin token in the URL or command arguments.
const [action,contact]=process.argv.slice(2);
const base=process.env.SOL_URL,token=process.env.SOL_ADMIN_TOKEN;
if(!base || !token || !base.startsWith('https://')) throw new Error('Configure SOL_URL (HTTPS) e SOL_ADMIN_TOKEN no ambiente local. Não publique os valores.');
const route={status:'/admin/status',pause:'/admin/pause',resume:'/admin/pause',takeover:'/admin/chat',release:'/admin/chat'}[action];
if(!route) throw new Error('Use: node admin.mjs status|pause|resume|takeover NUMERO|release NUMERO');
if(['takeover','release'].includes(action) && !/^\d{8,20}$/.test(contact || '')) throw new Error('Informe o número internacional, somente dígitos.');
const body=action==='status'?undefined:JSON.stringify(['takeover','release'].includes(action)?{from:contact,paused:action==='takeover'}:{paused:action==='pause'});
const result=await fetch(new URL(route,base),{method:body?'POST':'GET',headers:{authorization:'Bearer '+token,'content-type':'application/json'},body,signal:AbortSignal.timeout(15000)});
if(!result.ok) throw new Error('Operação não concluída: HTTP '+result.status);
console.log(JSON.stringify(await result.json(),null,2));
