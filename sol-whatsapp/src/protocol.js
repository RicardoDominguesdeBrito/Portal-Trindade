export const identity = 'Sol, inteligência artificial do canal Portal Trindade';
export const normalize = text => String(text || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

// Rule-based first stage: no paid model calls, arbitrary tools or prompt execution.
// Conflicting commercial durations are deliberately kept for Ricardo's review.
export function answer(message, state = {}) {
  const t = normalize(message.text);
  const prefix = identity + '.\n\n';
  if (/\b(parar|sair|cancelar mensagens|nao me envie|nao quero mensagens)\b/.test(t))
    return {pause: 'opt-out', text: prefix + 'Certo. O atendimento automático foi interrompido nesta conversa.'};
  if (/\b(ricardo|humano|atendente|desconto|pagamento|pix|parcela|reembolso|reclamacao|urgente|contratar|fechar|reserva|agendar|hoje|amanha)\b/.test(t))
    return {pause: 'human', text: prefix + 'Esse assunto precisa da análise do Ricardo. Deixe os detalhes aqui para ele dar continuidade nesta conversa.'};
  if (message.type !== 'text')
    return {pause: 'media-review', text: prefix + 'Este atendimento inicial ainda não analisa áudios ou anexos. Você pode descrever por texto o que precisa? O material fica para análise do Ricardo.'};
  if (/\b(preco|valor|pacote|plano|quanto)\b/.test(t))
    return {text: prefix + 'Temos opções de divulgação e de produção de vídeo. As condições e a permanência das publicações estão em revisão com o Ricardo. Você procura divulgação com material pronto ou gravação no local?'};
  if (/\b(material|foto|video|logo|enviar)\b/.test(t))
    return {text: prefix + 'Para preparar a divulgação, precisamos das fotos ou vídeos originais, do logotipo oficial e das informações comerciais. Se houver promoção, inclua validade e regras. Você já tem esse material pronto?'};
  if (/\b(publicacao|postagem|aprovar|ajuste|relatorio)\b/.test(t))
    return {pause: 'publication-review', text: prefix + 'Qual é o negócio e a publicação a que você se refere? O Ricardo precisa analisar aprovações, ajustes e relatórios.'};
  if (/\b(anunciar|divulgar|propaganda|negocio|empresa)\b/.test(t))
    return {nextStage: 'business', text: prefix + 'O Portal conecta turismo, fé, cultura, comércio e serviços de Trindade. Qual é o nome do seu negócio?'};
  if (state.stage === 'business')
    return {nextStage: 'instagram', business: String(message.text).slice(0, 160), text: prefix + 'Qual é o perfil do negócio no Instagram?'};
  if (state.stage === 'instagram')
    return {nextStage: 'objective', instagram: String(message.text).slice(0, 160), text: prefix + 'Qual é o objetivo da divulgação?'};
  if (state.stage === 'objective')
    return {pause: 'proposal-review', objective: String(message.text).slice(0, 500), text: prefix + 'Obrigada pelas informações. O Ricardo precisa avaliar a proposta e a disponibilidade. Você já tem fotos ou vídeos prontos?'};
  if (/\b(turismo|visitar|passeio|hospedagem|restaurante|evento)\b/.test(t))
    return {pause: 'information-review', text: prefix + 'Você pode consultar o Portal em https://www.trindadeportal.com.br/. Para confirmar horários, reservas e disponibilidade, fale com o estabelecimento. Qual informação você procura?'};
  if (state.greeted)
    return {pause: 'context-review', text: prefix + 'Para não passar uma informação incorreta, este assunto fica para análise do Ricardo. Pode deixar os detalhes nesta conversa.'};
  return {text: prefix + 'Olá! Posso ajudar com divulgação de negócios, publicações ou sugestões para o Portal. Como posso ajudar?'};
}

export function inHours(env, now = new Date()) {
  const h = Number(new Intl.DateTimeFormat('en-GB', {timeZone:'America/Sao_Paulo', hour:'2-digit', hourCycle:'h23'}).format(now));
  return h >= Number(env.START_HOUR || 5) && h < Number(env.END_HOUR || 22);
}
