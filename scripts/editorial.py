"""Conteúdo de história, cultura e turismo com referências explícitas."""
import html
import json

E = lambda value: html.escape(str(value), quote=True)
LABELS = {'historia':'História','fe':'Fé e devoção','cultura':'Cultura','gastronomia':'Gastronomia','turismo':'Planeje a visita'}

class CityGuide:
    def __init__(self, root, base):
        self.base = base
        self.data = json.loads((root/'data/conhecimento.json').read_text())
        self.articles = self.data['artigos']
        self.by_slug = {a['slug']:a for a in self.articles}
        self.questions = self.data['perguntas']
        self.sources = self.data['fontes']

    def photo(self, a, eager=False):
        return f'<img src="/{E(a["imagem"])}" alt="{E(a["alt"])}" width="1200" height="800" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async">'

    def card(self, a, prefix='./', searchable=False):
        terms = ' '.join([a['titulo'],a['resumo']]+[q['q'] for q in self.questions if q['artigo']==a['slug']])
        search = f'data-guide-card data-category-name="{a["categoria"]}" data-search="{E(terms)}"' if searchable else ''
        return f'<article class="guide-card story-card" {search}><div class="card-image">{self.photo(a)}</div><span class="tag">{LABELS[a["categoria"]]}</span><h3><a class="whole-card-link" href="{prefix}guias/{a["slug"]}.html">{E(a["curto"])}</a></h3><p>{E(a["resumo"])}</p><div class="card-end"><span>Ler e conhecer</span><span aria-hidden="true">↗</span></div></article>'

    def intro(self, title, lead, kicker='Conheça Trindade', prefix='./'):
        return f'<section class="page-intro"><div class="wrap"><nav class="breadcrumb" aria-label="Caminho"><a href="{prefix}index.html">Início</a><span>/</span><a href="{prefix}conheca-trindade.html">Conheça Trindade</a></nav><p class="eyebrow">{E(kicker)}</p><h1>{E(title)}</h1><p class="lead">{E(lead)}</p></div></section>'

    def home_section(self):
        featured=[self.by_slug[s] for s in ['historia-de-trindade','romaria-e-carreiros','sabores-de-trindade']]
        return '<section class="section city-section" id="conheca"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">História, fé e cultura</p><h2>Cada lugar tem<br>uma história para contar.</h2></div><a class="text-link" href="conheca-trindade.html">Conheça a cidade <span aria-hidden="true">→</span></a></div><p class="section-intro">Entenda a devoção, descubra a memória da cidade e planeje sua visita com informações de fontes institucionais.</p><div class="guide-grid">'+''.join(self.card(a) for a in featured)+'</div><div class="city-help"><span>Tem uma dúvida sobre Trindade?</span><a class="text-link" href="perguntas-frequentes.html">Encontre respostas para sua visita <span aria-hidden="true">→</span></a></div></div></section>'

    def hub(self):
        return self.intro('Trindade: história, fé e cultura para conhecer de perto.','Do antigo Barro Preto aos caminhos de hoje. Leituras e orientações para compreender a cidade e aproveitar a visita.')+'<section class="section"><div class="wrap"><nav class="topic-nav" aria-label="Assuntos da cidade">'+''.join(f'<a href="guias/{a["slug"]}.html">{LABELS[a["categoria"]] if a["slug"]!="romaria-e-carreiros" else "Romaria e carreiros"}</a>' for a in self.articles)+'</nav><div class="guide-grid knowledge-grid">'+''.join(self.card(a) for a in self.articles)+'</div><div class="city-help"><div><h2>Antes de arrumar as malas</h2><p>Respostas sobre a cidade, os santuários, a festa, os passeios e a organização da viagem.</p></div><a class="btn" href="perguntas-frequentes.html">Consultar perguntas frequentes</a></div><p class="editorial-note">Pesquisa em fontes do IBGE, Iphan, Goiás Turismo, Prefeitura de Trindade e Santuário. <a href="sobre-o-portal.html">Conheça nossos critérios editoriais.</a></p></div></section>'

    def used_sources(self,a):
        return list(dict.fromkeys([i for s in a['secoes'] for i in s['fontes']]+[t[2] for t in a.get('linha_do_tempo',[])]))

    def references(self,ids):
        rows=''.join(f'<li id="fonte-{n}"><a href="{E(self.sources[k]["url"])}" target="_blank" rel="noopener noreferrer">{E(self.sources[k]["instituicao"])} — {E(self.sources[k]["titulo"])}</a></li>' for n,k in enumerate(ids,1))
        return f'<section class="story-sources" id="fontes"><h2>Fontes para continuar a leitura</h2><p>Referências consultadas em 27/09/2026. Datas, agendas e condições de acesso devem ser conferidas para o dia da visita.</p><ol>{rows}</ol></section>'

    def article(self,a):
        ids=self.used_sources(a)
        def cite(keys):
            return '<p class="source-links">Fontes: '+ ' '.join(f'<a href="#fonte-{ids.index(k)+1}" aria-label="Fonte {ids.index(k)+1}: {E(self.sources[k]["instituicao"])}">[{ids.index(k)+1}]</a>' for k in keys)+'</p>' if keys else ''
        content=''.join(f'<section class="story-section" id="{s["id"]}"><h2>{E(s["titulo"])}</h2>'+''.join(f'<p>{E(p)}</p>' for p in s['paragrafos'])+cite(s['fontes'])+'</section>' for s in a['secoes'])
        timeline=''
        if a.get('linha_do_tempo'):
            timeline='<section class="story-section" id="linha-do-tempo"><h2>Trindade em alguns marcos</h2><ol class="history-timeline">'+''.join(f'<li><strong>{E(year)}</strong><div><p>{E(text)}</p>{cite([source])}</div></li>' for year,text,source in a['linha_do_tempo'])+'</ol></section>'
        toc=''.join(f'<a href="#{s["id"]}">{E(s["titulo"])}</a>' for s in a['secoes'])
        if timeline:toc+='<a href="#linha-do-tempo">Linha do tempo</a>'
        toc+='<a href="#fontes">Fontes consultadas</a>'
        related=''.join(self.card(self.by_slug[s],prefix='../') for s in a['relacionados'])
        next_links={
            'historia-de-trindade':[('guias/roteiro-turistico-um-dia.html','Ver roteiro de um dia')],
            'devocao-e-santuarios':[('guias/espacos-do-santuario.html','Conhecer espaços da Basílica'),('guias/igrejas-alem-do-roteiro.html','Outros espaços de fé')],
            'romaria-e-carreiros':[('hospedagem.html','Escolher hospedagem')],
            'cultura-e-memoria':[('guias/cultura-e-lazer.html','Ver lugares de cultura e lazer')],
            'sabores-de-trindade':[('guias/pamonharias.html','Encontrar pamonharias'),('guias/feiras.html','Dias e locais das feiras'),('leitura.html','Abrir guias e livro de receitas')],
            'planeje-sua-visita':[('hospedagem.html','Encontrar hospedagem'),('guia.html?categoria=gastronomia','Escolher onde comer'),('guias/roteiro-turistico-um-dia.html','Ver roteiro de um dia')]
        }
        useful=''.join(f'<a class="text-link" href="../{url}">{E(label)} <span aria-hidden="true">→</span></a>' for url,label in next_links[a['slug']])
        body=self.intro(a['titulo'],a['resumo'],LABELS[a['categoria']],prefix='../')
        body+=f'<div class="wrap"><div class="story-byline"><a href="../sobre-o-portal.html">Pesquisa e redação: Portal Trindade</a><span>Revisado em <time datetime="2026-09-27">27/09/2026</time></span></div><figure class="story-photo">{self.photo(a,True)}<figcaption>{E(a["legenda"])}</figcaption></figure></div>'
        body+=f'<div class="wrap story-layout"><article class="story-content"><p class="story-opening">{E(a["abertura"])}</p>{content}{timeline}<div class="story-useful"><h2>Do conteúdo ao passeio</h2>{useful}<a class="text-link" href="../perguntas-frequentes.html?tema={a["slug"]}">Dúvidas sobre este assunto →</a></div>{self.references(ids)}</article><aside class="story-sidebar"><nav aria-label="Nesta página"><p class="eyebrow">Nesta leitura</p>{toc}</nav><a class="text-link" href="../perguntas-frequentes.html">Perguntas frequentes →</a></aside></div>'
        body+='<section class="section city-section"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">Continue descobrindo</p><h2>Outras histórias, novos passeios.</h2></div></div><div class="guide-grid">'+related+'</div></div></section>'
        return body

    def faq(self):
        filters='<option value="">Todos os assuntos</option>'+''.join(f'<option value="{a["slug"]}">{E(a["curto"])}</option>' for a in self.articles)
        cards=[]
        for n,q in enumerate(self.questions,1):
            sources=' · '.join(f'<a href="{E(self.sources[k]["url"])}" target="_blank" rel="noopener noreferrer">{E(self.sources[k]["instituicao"])}</a>' for k in q['fontes'])
            note=f'<p class="faq-sources">Fonte: {sources}</p>' if sources else ''
            cards.append(f'<details class="faq-item" id="pergunta-{n}" data-faq data-topic="{q["artigo"]}" data-search="{E(q["q"]+" "+q["a"])}"><summary>{E(q["q"])}</summary><div><p>{E(q["a"])}</p>{note}<a class="text-link" href="guias/{q["artigo"]}.html">Ler o guia completo →</a></div></details>')
        return self.intro('Perguntas frequentes sobre Trindade','Respostas para conhecer a cidade e planejar o passeio, com fontes e caminhos para aprofundar cada assunto.')+f'<section class="section"><div class="wrap faq-wrap"><div class="faq-toolbar"><label class="searchbar"><span class="sr-only">Buscar uma pergunta sobre Trindade</span><input id="faq-search" type="search" placeholder="Busque por missa, museu, romaria, história..." autocomplete="off"></label><label class="select-field"><span>Assunto</span><select id="faq-topic">{filters}</select></label></div><div class="form-row"><p class="result-count" id="faq-count" aria-live="polite">{len(self.questions)} respostas disponíveis</p><button class="btn btn-outline" id="faq-clear" type="button" hidden>Limpar busca</button></div><div class="faq-list">'+''.join(cards)+'</div><p class="empty-state" id="faq-empty" hidden>Nenhuma resposta corresponde à busca. Tente outro termo ou limpe os filtros.</p><div class="city-help"><div><h2>Sua dúvida ainda não está aqui?</h2><p>Conte ao Portal o que você gostaria de saber sobre Trindade.</p></div><a class="btn" href="index.html#contato">Falar com o Portal</a></div><p class="editorial-note">Conteúdo revisado em 27/09/2026. <a href="sobre-o-portal.html">Leia os critérios de pesquisa e atualização.</a></p></div></section>'

    def about(self,contact):
        return self.intro('Um olhar local, com cuidado pela informação.','O Portal Trindade aproxima moradores, visitantes, cultura e comércio local.','Sobre o Portal')+f'<section class="section"><div class="wrap story-content about-content"><section class="story-section"><h2>O que você encontra aqui</h2><p>Histórias da cidade, fé, turismo, gastronomia, cultura, hospedagem e informações para organizar sua visita. O Portal é uma mídia local independente, idealizada por Ricardo Domingues de Brito, e não representa a Prefeitura, o Santuário ou os estabelecimentos mencionados.</p></section><section class="story-section"><h2>Como o conteúdo é preparado</h2><p>Esta seção foi produzida com pesquisa em referências institucionais e apoio de ferramentas de inteligência artificial na organização, redação e revisão. As fontes são identificadas nas páginas, para que o leitor possa consultar os registros originais.</p><p>Relatos de tradição religiosa são apresentados como tradição. Quando há divergência entre datas, o texto evita transformar uma versão incerta em informação definitiva. Notícias antigas ajudam a contar a história, mas não confirmam horários, preços ou programação atuais.</p><p>As imagens desta ampliação pertencem ao acervo já utilizado pelo Portal. Imagens de apresentação que não documentam um local específico são identificadas como ilustrativas.</p></section><section class="story-section"><h2>Indicações e publicidade</h2><p>Os parceiros anunciantes são identificados no site. As seleções editoriais e as enquetes indicam sua origem; não são rankings técnicos nem garantia sobre produtos ou serviços. Reservas e contratações são tratadas diretamente com cada estabelecimento.</p></section><section class="story-section"><h2>Correções e sugestões</h2><p>Encontrou uma informação que mudou? Envie o endereço da página, o ponto a corrigir e uma referência atual, se disponível. O conteúdo pode ser revisto após a conferência.</p><a class="btn" href="{E(contact)}" target="_blank" rel="noopener noreferrer">Enviar uma correção ou sugestão</a></section></div></section>'

    def schema(self,a):
        path='guias/'+a['slug']+'.html';url=self.base+path
        org={'@type':'Organization','name':'Portal Trindade','url':self.base+'sobre-o-portal.html'}
        return {'@context':'https://schema.org','@graph':[
            {'@type':'Article','@id':url+'#artigo','headline':a['titulo'],'description':a['resumo'],'image':[self.base+a['imagem']],'datePublished':'2026-09-27','dateModified':'2026-09-27','inLanguage':'pt-BR','author':org,'publisher':org,'mainEntityOfPage':url,'citation':[self.sources[k]['url'] for k in self.used_sources(a)]},
            {'@type':'BreadcrumbList','@id':url+'#caminho','itemListElement':[{'@type':'ListItem','position':1,'name':'Início','item':self.base},{'@type':'ListItem','position':2,'name':'Conheça Trindade','item':self.base+'conheca-trindade.html'},{'@type':'ListItem','position':3,'name':a['titulo'],'item':url}]}
        ]}
