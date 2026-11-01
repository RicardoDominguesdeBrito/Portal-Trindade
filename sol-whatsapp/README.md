# Sol — integração de teste do WhatsApp

Estado: **backend implantado na Cloudflare em 31/10/2026 (horário de São Paulo), com fila Durable Object SQLite e testes do GitHub aprovados; webhook da Meta conectado e validado com evento de painel em 31/10/2026 às 23:29 (São Paulo), sem atendimento automático ativo**.

Endereço de verificação: https://sol-portal-trindade.ricardodbrito.workers.dev/health. Implantação pela branch `sol/whatsapp-integration`, workflow `.github/workflows/sol-whatsapp.yml`, Wrangler 4.156.0. Credencial de implantação limitada ao serviço, armazenada como segredo GitHub `SOL_CLOUDFLARE_API_TOKEN`. Não há token no código. Modo dry-run e pausa padrão preservados. Segredos META_APP_SECRET, WHATSAPP_TOKEN, VERIFY_TOKEN, ADMIN_TOKEN e ALLOWED_SENDERS confirmados como criptografados na Cloudflare. Callback /webhook validado pela Meta e campo messages assinado. Teste sintético enviado pelo painel Meta obteve sucesso em 31/10/2026 às 23:29:14 (São Paulo). O exemplo sintético da Meta não usa os IDs nem o destinatário permitidos; portanto, esse teste confirma transporte/assinatura/HTTP, não processamento de uma conversa ou resposta. Falta validar recebimento de mensagem real, rascunho, ativação limitada, resposta e pausa. App permanece não publicado; painel informa restrições para eventos de produção. MODE=dry-run e pausa padrão continuam ativos. O número oficial não foi alterado. A primeira credencial de implantação sem uso foi revogada; apenas a credencial Sol GitHub deploy permanece.
Este diretório é independente do site. Não faz alterações nas páginas, no domínio nem no WhatsApp Business existente. Não adicionar credenciais, transcrições, números particulares ou arquivos de clientes ao GitHub.

## O que foi implementado

- Webhook HTTPS com validação GET e HMAC SHA-256 do corpo original dos POSTs.
- Conta, Phone Number ID e destinatários explicitamente permitidos. Eventos de status, mensagens antigas e eventos de outras contas não geram respostas.
- Fila persistente em um Durable Object com SQLite, deduplicação por ID, um executor e alarme de processamento.
- Modo `dry-run` padrão: apenas prepara rascunhos. Atendimento começa pausado.
- Modo `test`: envia somente pelo Phone Number ID de teste e para a lista autorizada. **Produção não está habilitada neste código.**
- Atendimento inicial por regras, sem modelo generativo, ferramentas externas nem cobrança de tokens de IA. Não equivale a uma Sol com compreensão livre de conversas, voz, pesquisa ou análise de mídia.
- Identificação da Sol, triagem comercial, materiais, publicações, encaminhamento humano e opt-out.
- API administrativa com token separado: pausa global e por contato, consulta de rascunhos e encaminhamentos. Não há painel visual nem caixa de entrada humana nesta versão.
- Nenhum fechamento, desconto, cobrança, confirmação de pagamento, publicação ou agendamento automático.
- Política de envio conservadora: falha de rede, resposta ambígua ou interrupção após início do envio fica `uncertain`, sem reenvio automático. Pode exigir contato manual, evitando duplicatas.

## Implantação proposta: Cloudflare Workers + Durable Objects

Documentação conferida em 31/10/2026: há plano Workers Free com Durable Objects SQLite, sujeito a limites. Não foi criada conta nem ativado plano. Não é promessa de gratuidade de toda a operação: WhatsApp/Meta, serviços futuros e modelos de IA têm condições próprias.

- https://developers.cloudflare.com/workers/platform/pricing/
- https://developers.cloudflare.com/durable-objects/platform/pricing/
- https://developers.cloudflare.com/durable-objects/api/alarms/
- https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/webhooks/start/

O GitHub guarda o código; GitHub Pages não executa este backend. O endereço de callback só existe após a implantação do Worker.

### Sequência de implantação assistida

1. Entrar na conta Cloudflare do titular; escolher Workers Free, sem assinar plano pago. Revisar qualquer nova permissão ou termo antes da aceitação.
2. Importar a branch e usar `sol-whatsapp` como diretório raiz. Comando de implantação: `npx wrangler deploy`. Alternativamente, usar Wrangler oficial localmente. Fixar a versão da ferramenta escolhida durante a implantação e registrar essa versão; não há dependência runtime de terceiros no aplicativo.
3. Manter `MODE=dry-run`. Definir `WABA_ID`, `PHONE_NUMBER_ID`, `TEST_PHONE_NUMBER_ID` com os identificadores da **conta de teste**, e `ALLOWED_SENDERS` com os destinatários verificados, separados por vírgula. Números só com dígitos. Não usar o número comercial oficial.
4. Cadastrar no gerenciador de segredos do Worker: `META_APP_SECRET` (segredo do app Meta), `VERIFY_TOKEN` (valor aleatório próprio para handshake), `ADMIN_TOKEN` (aleatório, no mínimo 32 caracteres). `VERIFY_TOKEN` não é o token de acesso da Meta. Para modo test, cadastrar `WHATSAPP_TOKEN` como segredo também. Nunca usar variáveis públicas, código, commits, logs ou chat para segredos.
5. Configurar na Meta `https://ENDERECO-REAL-DO-WORKER/webhook` e o mesmo `VERIFY_TOKEN`. Assinar o campo `messages` e associar o app à conta de teste conforme as opções efetivamente disponíveis. O painel Meta observado exige publicação do app para dados de produção; revisar requisitos atuais antes de produção.
6. Fazer teste de webhook assinado. Consultar rascunho pela API administrativa; iniciar processamento com `resume`. `dry-run` continua sem enviar. Fazer os testes em horário configurado (padrão 05h–22h de São Paulo, sem envio fora dessa janela).
7. Para teste de envio, revisar credenciais, usar `MODE=test`, confirmar `PHONE_NUMBER_ID=TEST_PHONE_NUMBER_ID` e os destinatários permitidos. Reabrir manualmente os contatos pausados se necessário. Só novas mensagens são processadas; rascunhos e mensagens antigas não são reenviados.
8. Verificar no WhatsApp: recebimento, resposta, identificação da Sol, uma pergunta por vez, pausa humana, opt-out e ausência de duplicatas. Guardar resultado sem tokens.
9. Só depois preparar produção como etapa separada: coexistência/migração do número oficial, permissões, publicação do app, condições comerciais, horários, custos, armazenamento e confirmação do titular. Não desconectar o WhatsApp Business nem remover aparelhos durante os testes.

### Controle do operador

Em um terminal privado, configurar `SOL_URL` e `SOL_ADMIN_TOKEN` como variáveis locais. O token não deve aparecer em capturas nem ser salvo no histórico em comandos literais.

```
node admin.mjs status
node admin.mjs pause
node admin.mjs resume
node admin.mjs takeover NUMERO_INTERNACIONAL
node admin.mjs release NUMERO_INTERNACIONAL
```

`status` contém conteúdo de atendimento: uso privado do responsável. `takeover` deve ser feito **antes** de responder manualmente. Esta versão não detecta automaticamente que Ricardo assumiu em outro aplicativo. Uma pausa espera concluir uma chamada de envio já iniciada; não pode recolher mensagem já enviada. Clientes nunca podem acionar esses comandos pelo WhatsApp.

## Protocolo recuperado e decisões pendentes

Identidade: “Sol, inteligência artificial do canal Portal Trindade”. Português simples, cordial, profissional. Uma pergunta por vez; não repetir saudação nem anexos. Ricardo confirma compromissos, pagamentos, descontos, exceções, disponibilidade, deslocamentos e aprovações editoriais. Não prometer vendas, alcance nem prazo de atendimento humano. Não alegar encaminhamento externo concluído: a fila interna precisa ser consultada pelo operador.

Fontes: instruções CLARA Atendimento e configuração declarativa da Sol de 24/10/2026. Esses documentos não comprovam serviço instalado. A versão anterior de monitoramento de navegador não foi reativada.

Condições comerciais recuperadas de outubro incluem pacotes Story R$50, 1 publicação R$100, 2 R$200, 4 R$350, 8 R$640, vídeo local R$300 e drone R$500. Há também pacote R$400 com composição própria; não foi confundido com tabela geral. Permanência de 30/60 dias diverge entre fontes. Por isso **preços e durações não são oferecidos automaticamente nesta primeira versão**; validar mídia kit atual antes de habilitar catálogo. Divulgação não se soma automaticamente ao pacote de vídeo. Tráfego pago separado.

## Limites e operação

- Testes locais: `npm test`; sintaxe: `npm run check`. Node >=22, sem instalação de pacotes para testar.
- Testes usam armazenamento simulado; ainda falta validação no runtime Cloudflare e na Meta. Não foi verificada implantação real.
- Limite de 500 registros na fila operacional (inclui concluídos até a limpeza). Ao atingir o limite, responde 503 e depende de nova tentativa da Meta. Não é apropriado para alto volume sem evolução de armazenamento/paginação.
- Deduplicação retida por 30 dias; jobs e conversas normais por 7 dias, limpeza diária em lotes limitados. Pausas/opt-outs preservados até intervenção; não são removidos pela limpeza. Contatos pausados podem manter dados da triagem até revisão manual. Definir política de privacidade e exclusão antes de clientes reais.
- Mensagens fora do horário são marcadas, sem resposta e sem retomada automática no dia seguinte. Mensagens com mais de 10 minutos também expiram; operador deve revisar pendências.
- Envio bem-sucedido significa aceito pela API, não leitura ou entrega confirmada. Status de entrega não são persistidos nesta fase.
- Não há prospecção, grupos, chamadas, envio de arquivos, transcrição, análise de anexos, notificações externas ao operador nem navegação autônoma.
- Não há execução permanente no computador de Ricardo. Atendimento depende de implantação e configuração real no provedor.

## Pendências para retomar

1. Autenticação do titular na Cloudflare e acesso do navegador conectado.
2. Implantar apenas no plano aprovado, inserir segredos pela interface segura, configurar webhook de teste.
3. Validar runtime e teste ponta a ponta. Conciliar mídia kit e definir motor de IA se desejado, com orçamento e autorização próprios.
4. Preparar integração oficial após avaliação do número atualmente mostrado como Offline no Gerenciador Meta. Não foi alterado por este projeto.
