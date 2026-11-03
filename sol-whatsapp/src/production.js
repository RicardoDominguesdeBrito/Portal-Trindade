// Explicit production gates. Merely deploying this code never enables sending.
export const productionAccount = {waba: '1982232865723855', phone: '1087653641089631'};
export function productionReady(env) {
  return env.MODE === 'production' && env.PRODUCTION_ENABLED === 'true'
    && env.WABA_ID === productionAccount.waba
    && env.PHONE_NUMBER_ID === productionAccount.phone
    && env.PHONE_NUMBER_ID !== env.TEST_PHONE_NUMBER_ID
    && !!env.WHATSAPP_TOKEN
    && ['allowlist', 'all-inbound'].includes(env.RECIPIENT_SCOPE);
}
export function senderAllowed(env, from) {
  if (env.MODE === 'production' && !productionReady(env)) return false;
  if (productionReady(env) && env.RECIPIENT_SCOPE === 'all-inbound') return true;
  return (env.ALLOWED_SENDERS || '').split(',').map(s => s.trim()).includes(from);
}
