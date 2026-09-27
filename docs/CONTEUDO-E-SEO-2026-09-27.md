# História, cultura e busca orgânica — 27/09/2026

## Ampliação publicada

Seis artigos de história, devoção e santuários, Romaria e carreiros, memória e cultura, gastronomia e planejamento da visita. A página `conheca-trindade.html` reúne esse conteúdo; `perguntas-frequentes.html` oferece 34 respostas com busca por palavras e filtro de assunto. `sobre-o-portal.html` explica autoria, pesquisa, uso de IA, distinção entre publicidade e curadoria e envio de correções.

O conteúdo complementa os 11 guias locais e as 72 hospedagens existentes. A identidade visual, as fotografias do acervo, os parceiros e materiais de leitura foram mantidos. A imagem de gastronomia usada para apresentação é identificada como ilustrativa. Não foram copiadas fotografias de órgãos públicos.

## Pesquisa e manutenção editorial

As 16 referências estão em `data/conhecimento.json`, incluindo IBGE, Iphan, Prefeitura, Goiás Turismo, Goinfra e Santuário. Textos próprios sintetizam as informações; cada seção factual e resposta indica a referência correspondente. O inventário turístico de 2020 é usado para caracterizar lugares, sem reapresentar seus horários e telefones antigos como atuais.

- A origem religiosa é apresentada como tradição, situada na década de 1840. Datas divergentes dos primeiros acontecimentos não são tratadas como cronologia definitiva.
- A Matriz, a Basílica em funcionamento e o Novo Santuário em construção são identificados separadamente.
- O reconhecimento do Iphan refere-se especificamente à Romaria de Carros de Bois; não se afirma reconhecimento pela Unesco ou registro de toda a festa.
- A notícia do kart é datada de 03/06/2026 e não confirma por si só a situação atual.
- O festival é descrito a partir da proposta da XII edição, sem divulgar datas conflitantes da notícia municipal como programação futura.
- O número populacional é do Censo 2022, sem confusão com estimativa de 2026.
- Horários de missas, abertura, obras, preços e condições de acesso devem ser conferidos nos canais responsáveis. Nenhuma agenda futura foi inventada.
- Recomendações de roteiro são sugestões do Portal, sem alegação de experiência presencial ou duração garantida.

A data de revisão deve ser alterada após nova conferência, e não apenas por executar o gerador. Não foi configurada atualização automática nem acompanhamento contínuo. Mudanças futuras devem atualizar a fonte, o texto e os dados estruturados correspondentes.

## Estrutura para mecanismos de busca

- HTML completo, incluindo as respostas, entregue sem depender da execução de JavaScript.
- Títulos, descrições e URLs canônicas próprios; ligações entre artigos, guias, perguntas e diretório.
- Dados estruturados `Article` e `BreadcrumbList` nas seis matérias, com autor institucional, datas, imagens e referências correspondentes ao conteúdo visível.
- Sitemap com 24 páginas indexáveis; página 404 e prévia excluídas.
- Prévia com `noindex,nofollow` e bloqueio em `robots.txt`.
- Arquivo de verificação do Google existente preservado. Nenhuma nova propriedade de Search Console criada ou alterada nesta entrega.
- Imagens locais com descrição alternativa, dimensões e carregamento adiado quando apropriado.

Não são usados texto oculto, repetição artificial de palavras-chave, avaliações inventadas ou promessa de resultados enriquecidos para FAQ. A preparação técnica e editorial não garante rastreamento, indexação ou posição no Google.

Referências técnicas: [Google Search Essentials](https://developers.google.com/search/docs/essentials), [conteúdo útil](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), [artigos](https://developers.google.com/search/docs/appearance/structured-data/article) e [breadcrumbs](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb).

## Gerar e validar

Dados: `data/conhecimento.json`. Apresentação: `scripts/editorial.py`, integrado a `scripts/build_site.py`.

```sh
python scripts/build_site.py
python scripts/validate_site.py
node --check portal.js
python scripts/build_site.py --out previa-2026 --preview
python scripts/validate_site.py previa-2026
```

Verificações locais: 25 páginas, 1.105 referências locais, IDs, textos alternativos, integridade das 72 hospedagens, sintaxe JavaScript, JSON-LD válido, metadados únicos e correspondência do sitemap às 24 páginas indexáveis. O validador agora recusa diretório inexistente ou sem páginas, evitando um falso resultado positivo.

Revisão visual realizada no domínio de prévia em computador, celular de 390 px e tablet de 768 px. Artigos, imagens, índice de leitura e página de respostas conferidos. A busca sem acentos por `devocao` retornou cinco respostas; combinada com o assunto de devoção, três. Termo inexistente mostrou o estado vazio, e a limpeza restaurou as 34 respostas. No celular, a busca por `museu` retornou três respostas.

## Restaurar a versão anterior

Antes desta ampliação, o redesign em produção foi preservado na branch `backup/antes-conteudo-historico-2026-09-27`, commit `88eebf0478a2d437270e9ef4381cc43671956153`, árvore `a66273b97cc45954962e05b6ec01fa44457574a6`.

Para restaurar, criar um novo commit sobre o `main` atual com a árvore completa do backup e avançar `main` sem força. Assim, arquivos e configurações voltam ao estado anterior sem apagar o histórico. Conferir o GitHub Pages e o domínio após a publicação. Se houver mudanças posteriores, avaliar seu aproveitamento antes de repor toda a árvore.

O backup da aparência original, anterior ao redesign, continua em `backup/antes-redesign-2026-09-27`, commit `e5dfbca1ce9d6152d730aa41b2085a4317aaddb1`.
