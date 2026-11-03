# Sol — preparação de produção (03/11/2026)

Esta proposta não foi implantada nem ativada. O workflow existente só implanta a branch `sol/whatsapp-integration`; a branch de revisão não deve ser fundida antes da validação.

## Estado confirmado na interface

- Cloudflare: serviço `sol-portal-trindade`, fila Durable Object, MODE=dry-run, horário 05h–22h e ativos de teste. Cinco segredos existentes criptografados; seus valores não foram lidos.
- Meta: app Sol portal trindade não publicado; callback existente e campo messages assinado. A própria Meta informa que dados reais não são enviados antes da publicação.
- Conta oficial Portal Trindade: WABA 1982232865723855, Phone Number ID 1087653641089631. Número comercial já aparece Conectado, qualidade Alta. Isso não comprova acesso deste app/token à API dessa conta.
- Não houve remoção, migração ou registro de número. O acesso do token existente à conta oficial e a assinatura do app nessa WABA ainda precisam ser verificados.

## Alteração preparada

Modo production com trava explícita, limitado aos IDs oficiais acima. Dois escopos: `allowlist` para validação inicial e `all-inbound` para responder somente a quem iniciar uma conversa. A configuração de produção começa com PRODUCTION_ENABLED=false e escopo allowlist; mantém a pausa administrativa padrão. Horário 00h–24h de São Paulo. O arquivo de teste e seu workflow permanecem intactos.

Mantidos HMAC, deduplicação, pausa global, pausa por contato, opt-out, prazo máximo de mensagem de dez minutos e ausência de reenvio após resultado incerto. Não dispara campanhas nem mensagens proativas. Ainda é triagem por regras, sem interpretação livre de conversas ou áudio. Não confirma preços, pagamentos, contratos, publicações ou disponibilidade.

## Sequência para ativação

1. Aprovar e publicar o aviso de privacidade abaixo em URL HTTPS pública; cadastrá-la na Meta e publicar o app. Revisar qualquer termo ou permissão apresentados pela plataforma no momento.
2. Confirmar que o token já armazenado tem acesso de mensagens à conta oficial e que o app está associado a essa WABA. Se exigir novo token/permissão, obter aprovação específica e inserir somente pelo gerenciador de segredos, sem copiar no chat ou no repositório.
3. Implantar com wrangler.production.jsonc, ainda com PRODUCTION_ENABLED=false. Não acionar o workflow de teste depois disso: ele restauraria os IDs de teste. Antes de consolidar, separar o workflow de teste do serviço oficial.
4. Autorizar teste inicial pelo número oficial, restrito à lista já configurada. Habilitar a trava somente após validar os ativos; retomar pelo controle administrativo com a chave do titular. Não extrair nem substituir a chave administrativa para contornar acesso.
5. Receber uma nova mensagem enviada pelo contato autorizado e confirmar a resposta no WhatsApp, pausa humana e ausência de duplicatas. A aceitação pela API sozinha não comprova entrega.
6. Só após o teste ponta a ponta, selecionar all-inbound para novos contatos. Preservar opt-outs e pausas existentes. Não reprocessar mensagens antigas.

## Minuta do aviso de privacidade — requer aprovação antes de publicar

**Sol — Atendimento do Portal Trindade**

A Sol realiza a triagem inicial das mensagens enviadas ao WhatsApp do Portal Trindade. O responsável pelo atendimento é Ricardo Domingues de Brito. Para dúvidas sobre dados pessoais ou pedidos de acesso, correção e exclusão, escreva para trindadeportalgo@gmail.com ou solicite atendimento humano no próprio WhatsApp.

O atendimento utiliza o número do remetente, identificadores e horários das mensagens, o texto enviado e informações fornecidas sobre o negócio, perfil no Instagram e objetivo da divulgação. Esses dados servem para responder à solicitação, organizar o atendimento, evitar respostas duplicadas e permitir a continuidade por Ricardo. Não envie senhas, documentos, dados bancários ou informações de saúde. A Sol não analisa o conteúdo de áudios, imagens e documentos nesta versão.

As mensagens passam pela plataforma WhatsApp/Meta. O serviço de triagem e sua fila funcionam na Cloudflare. Não há envio a um modelo generativo de IA nesta versão. O responsável pelo Portal pode consultar a fila administrativa protegida. O código público no GitHub não contém conversas de clientes nem credenciais.

Na fila da Sol, registros operacionais comuns são submetidos a limpeza após sete dias, e os identificadores usados para impedir duplicação após trinta dias. A limpeza é periódica, não imediata. Conversas pausadas, informações necessárias à continuidade e registros de recusa ao atendimento automático são preservados até revisão pelo responsável. O histórico mantido no WhatsApp e os registros dos provedores seguem também seus próprios controles e políticas; os prazos da fila não representam a exclusão de todas as cópias nesses serviços.

Você pode escrever “parar” para interromper o atendimento automático nesta conversa ou pedir um atendente humano. A Sol não fecha contratos, confirma pagamentos ou toma decisões comerciais finais. Solicitações de exclusão são tratadas pelo responsável e precisam considerar os registros necessários para manter sua preferência de não receber respostas automáticas.

Versão proposta: 3 de novembro de 2026. Publicar somente após o titular validar o tratamento descrito e os canais de contato.
