#!/usr/bin/env python3
"""Gera páginas estáticas completas; nenhum serviço pago ou dependência de build."""
import argparse
import html
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlencode
from editorial import CityGuide

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.trindadeportal.com.br/'
DATE = '2026-09-27'
city = CityGuide(ROOT, BASE)
data = json.loads((ROOT / 'conteudo.json').read_text())
lodgings = json.loads((ROOT / 'hospedagens.json').read_text())
collections = json.loads((ROOT / 'data/curadoria.json').read_text())['colecoes']
publication_dates = {p['codigo']:p['publicado_em'] for p in json.loads((ROOT / 'data/fontes-instagram.json').read_text())['publicacoes']}
WA = 'https://wa.me/' + data['site']['whatsapp']
INSTA = data['site']['instagram'] + '/'
labels = {'historia':'História','gastronomia':'Gastronomia','fe':'Fé e devoção','turismo':'Turismo','cultura':'Cultura e lazer','servicos':'Serviços'}
escape = lambda x: html.escape(str(x), quote=True)
def icon(name='arrow'):
    paths = {'arrow':'<path d="M4 12h16m-6-6 6 6-6 6"/>','external':'<path d="M14 4h6v6M20 4l-9 9M10 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5"/>','search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>','menu':'<path d="M4 7h16M4 12h16M4 17h16"/>','pin':'<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.3"/>','food':'<path d="M5 3v7m3-7v7m-6-7v7c0 2 6 2 6 0M5 12v9M18 3c-3 3-4 8 0 9V3Zm0 9v9"/>','bed':'<path d="M3 18v3M21 18v3M3 18V8h18v10H3Zm0-5h18M5 8V4h14v4M8 8v5M16 8v5"/>','church':'<path d="M12 2v6M9 5h6M4 21V12l8-5 8 5v9H4Zm6 0v-6h4v6"/>','sun':'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 1.5 1.5M5 19l1.5-1.5M17.5 6.5 1.5-1.5"/>','instagram':'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.4 6.6h.1"/>','message':'<path d="M21 11.5a9 9 0 0 1-9 9 10 10 0 0 1-4-.9L3 21l1.4-4.7A9 9 0 1 1 21 11.5Z"/><path d="M8 8c1 4 3 6 7 7"/>','book':'<path d="M12 5c-3-2-6-2-9-1v15c3-1 6-1 9 1 3-2 6-2 9-1V4c-3-1-6-1-9 1Zm0 0v15"/>','share':'<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.7 10.5 6.6-4M8.7 13.5l6.6 4"/>'}
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths.get(name,paths["arrow"])}</svg>'

def asset(path): return '/' + path.lstrip('/')
def img(path, alt, cls='', width=1000, height=750, eager=False):
    return f'<img src="{escape(asset(path))}" alt="{escape(alt)}" width="{width}" height="{height}" class="{cls}" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async">'
def ext(url,text,cls='text-link',arrow=True):
    return f'<a href="{escape(url)}" class="{cls}" target="_blank" rel="noopener noreferrer">{escape(text)}{icon("external") if arrow else ""}</a>'
def wa(text): return WA + '?' + urlencode({'text':text})
def brand(prefix='./'):
    return f'<a class="brand" href="{prefix}index.html" aria-label="Portal Trindade — início">{img("imagens/editorial/logo-portal.webp","",width=51,height=51)}<span><strong>Portal Trindade</strong><small>Conectando a nossa cidade</small></span></a>'
def header(prefix='./',active=''):
    nav=[('conheca-trindade.html','Conheça a cidade'),('guia.html','Guias locais'),('hospedagem.html','Hospedagem'),('index.html#gastronomia','Parceiros'),('leitura.html','Livros e guias')]
    links=''.join(f'<a href="{prefix}{href}" {"aria-current=page" if href==active else ""}>{text}</a>' for href,text in nav)
    return f'''<a class="skip" href="#conteudo">Pular para o conteúdo</a>
    <div class="topline"><div class="wrap"><span>TRINDADE · GOIÁS · CAPITAL DA FÉ</span>{ext(INSTA,'Acompanhe @trindadeportal','top-instagram',False).replace('</a>',icon('instagram')+'</a>')}</div></div>
    <header class="site-header" id="topo"><div class="wrap navigation">{brand(prefix)}<nav class="desktop-nav" aria-label="Principal">{links}</nav><div class="nav-actions"><a class="btn" href="{prefix}index.html#contato">Anuncie no Portal {icon('arrow')}</a><button type="button" id="menu-toggle" class="menu-toggle" aria-controls="mobile-nav" aria-expanded="false" aria-label="Abrir menu">{icon('menu')}</button></div></div><nav id="mobile-nav" class="mobile-nav" aria-label="Menu do celular" hidden>{links}<a href="{prefix}index.html#contato">Anunciar ou falar com o Portal</a><a href="{prefix}guia.html">Buscar no guia</a></nav></header>'''
def footer(prefix='./'):
    return f'''<footer class="site-footer"><div class="wrap"><div class="footer-top"><div>{brand(prefix)}<p>Fé, turismo, cultura e comércio local. Um olhar de perto para quem vive ou visita Trindade.</p></div><nav class="footer-links" aria-label="Rodapé"><a href="{prefix}conheca-trindade.html">História, fé e cultura</a><a href="{prefix}perguntas-frequentes.html">Perguntas frequentes</a><a href="{prefix}sobre-o-portal.html">Sobre o Portal</a><a href="{prefix}guia.html">Explore Trindade</a><a href="{prefix}hospedagem.html">Onde se hospedar</a><a href="{prefix}index.html#gastronomia">Parceiros do Portal</a><a href="{prefix}leitura.html">Guias e livros</a><a href="{prefix}index.html#contato">Anuncie seu negócio</a>{ext(INSTA,'@trindadeportal','',False)}</nav></div><div class="footer-bottom">© 2026 Portal Trindade · Trindade, Goiás<span>Conteúdo local, feito para aproximar pessoas e lugares.</span></div></div></footer>'''
def page(title,desc,body,path='index.html',prefix='./',active='',preview=False,hero=None,schema=None):
    ld = {'@context':'https://schema.org','@type':'WebSite','name':'Portal Trindade','url':BASE,'inLanguage':'pt-BR','sameAs':[INSTA]} if path=='index.html' else {'@context':'https://schema.org','@type':'WebPage','name':title,'url':BASE+path,'description':desc,'inLanguage':'pt-BR'}
    if schema:
        if '@graph' in schema: ld=schema
        else: ld.update(schema)
    ogtype='article' if schema and '@graph' in schema else 'website'
    ogimage=BASE+(hero or 'imagens/hero-basilica-2026.webp')
    preload=f'<link rel="preload" as="image" href="{asset(hero)}" fetchpriority="high">' if hero else ''
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | Portal Trindade</title><meta name="description" content="{escape(desc)}"><meta name="theme-color" content="#17314e"><meta name="color-scheme" content="light">{'<meta name="robots" content="noindex,nofollow">' if preview else ''}<link rel="canonical" href="{BASE}{'' if path=='index.html' else path}"><meta property="og:type" content="{ogtype}"><meta property="og:locale" content="pt_BR"><meta property="og:title" content="{escape(title)} | Portal Trindade"><meta property="og:description" content="{escape(desc)}"><meta property="og:url" content="{BASE}{'' if path=='index.html' else path}"><meta property="og:image" content="{ogimage}"><link rel="icon" href="/imagens/logo-portal-trindade.jpg"><link rel="apple-touch-icon" href="/imagens/logo-portal-trindade.jpg">{preload}<link rel="stylesheet" href="{prefix}portal.css?v=20260927-2"><script defer src="{prefix}portal.js?v=20260927-2"></script><script type="application/ld+json">{json.dumps(ld,ensure_ascii=False).replace('<','\\u003c')}</script></head><body>{header(prefix,active)}<main id="conteudo">{body}</main>{footer(prefix)}</body></html>'''
def heading(kicker,title,link=None,text='Ver todos os guias'):
    return f'<div class="section-heading"><div><p class="eyebrow">{escape(kicker)}</p><h2>{title}</h2></div>{f"<a class=text-link href={link}>{escape(text)}{icon()}</a>" if link else ""}</div>'

# A curadoria parte das publicações do Portal, com referências complementares identificadas.
cmap={c['slug']:c for c in collections}
old_night=json.loads(json.dumps(cmap['gastronomia-de-bar']))
old_night.update(slug='onde-ir-a-noite')
collections.append(old_night)
cmap[old_night['slug']]=old_night
bars=cmap['gastronomia-de-bar']
bars.update(titulo='Gastronomia para o próximo rolê',resumo='Sete perfis para descobrir bares, restaurantes e novos sabores pela cidade.',fonte_url='https://www.instagram.com/trindadeportal/p/Ddq90QVnMsT/',observacao='Seleção editorial do Portal Trindade, sem ordem de preferência. Consulte os perfis para cardápios, preços e horários atualizados.')
bars['itens']=[{'nome':name,'descricao':'Conheça os pratos e acompanhe as informações diretamente no perfil do estabelecimento.','instagram':'https://www.instagram.com/'+handle+'/'} for name,handle in [('@rancho.bentos','rancho.bentos'),('@papitosgastrohouse','papitosgastrohouse'),('Carne de Sol 62','carnedesol.62ofc'),('@luansanduicheria','luansanduicheria'),('Santa Fé Empório','santafeemporio'),('La Casa Bar e Cozinha','lacasabarecozinha'),('@baronesa.cozinhaurbana','baronesa.cozinhaurbana')]]
cmap['acai']['observacao']='Os cinco primeiros locais foram lembrados pelos participantes da enquete do Portal. A Ibá foi apresentada em uma publicação posterior. As indicações não constituem avaliação técnica nem ranking.'
cmap['acai']['itens'][-1]['nome']='Ibá Açaí Trindade'
cmap['espacos-do-santuario']['resumo']='Espaços de oração, memória e devoção para conhecer dentro e ao redor da Basílica.'
cmap['espacos-do-santuario']['observacao']='Respeite os momentos de celebração e recolhimento. Consulte o Santuário sobre horários, acesso e programação antes da visita.'
cmap['igrejas-alem-do-roteiro']['observacao']='Os locais têm rotinas próprias de celebração e acolhimento. Confirme a possibilidade de visita antes de sair.'
cmap['cultura-e-lazer']['observacao']='Consulte cada espaço sobre programação, horários de visita e condições de acesso.'
cmap['cultura-e-lazer']['itens']=[i for i in cmap['cultura-e-lazer']['itens'] if i['nome'] not in ['Parque da Vila Padre Renato','Museu em casarão histórico']]
cmap['cultura-e-lazer']['itens'].append({'nome':'Loja Pai Eterno','descricao':'Terços, imagens, livros e lembranças religiosas no Santuário Basílica e junto à Casa do Abbá, no espaço de visitação da obra do Novo Santuário. Consulte as condições de acesso.','endereco':'Santuário Basílica: Praça Dom Antônio Ribeiro de Oliveira, bairro Santuário. Obra do Novo Santuário: ao lado da Casa do Abbá.'})
cmap['cultura-e-lazer']['resumo']='Artesanato, cinema, parque, museu e lembranças religiosas para conhecer outro lado da cidade.'
cmap['cultura-e-lazer']['itens'][1]['nome']='Mobicine Trindade'
cmap['hamburguerias']['observacao']='Indicações dos participantes da enquete do Portal, sem ordem de colocação ou avaliação técnica. Confira cardápio e funcionamento nos perfis.'
art_slugs=['gastronomia-de-bar','pamonharias','hamburguerias','acai','pizzarias','feiras']
photos={'roteiro-turistico-um-dia':'imagens/igreja-matriz-2026.webp','espacos-do-santuario':'imagens/galeria-gruta.webp','igrejas-alem-do-roteiro':'imagens/galeria-capela-cruzeiro.webp','cultura-e-lazer':'imagens/paisagem-trindade-2026.webp','onde-ir-a-noite':'imagens/editorial/gastronomia-de-bar.webp'}
for c in collections:
    c['imagem']='imagens/editorial/'+c['slug']+'.webp' if c['slug'] in art_slugs else photos[c['slug']]
    c['tipo_imagem']='arte' if c['slug'] in art_slugs+['onde-ir-a-noite'] else 'foto'
    if c['slug']=='igrejas-alem-do-roteiro': c['imagem']='imagens/igrejasaojose.png'
    c['atualizado_em']=DATE
def guide_card(c,prefix='./',art=None):
    is_art = c['tipo_imagem']=='arte' if art is None else art
    haystack=' '.join([c['titulo'],c['resumo'],labels[c['categoria']]]+[i['nome'] for i in c['itens']])
    return f'''<article class="guide-card {'art-card' if is_art else ''}" data-guide-card data-category-name="{c['categoria']}" data-search="{escape(haystack)}"><div class="card-image">{img(c['imagem'],('Arte do Portal Trindade: ' if is_art else '')+c['titulo'],width=800,height=1000 if is_art else 600)}</div><span class="tag">{labels[c['categoria']]}</span><h3><a class="whole-card-link" href="{prefix}guias/{c['slug']}.html">{escape(c['titulo'])}</a></h3><p>{escape(c['resumo'])}</p><div class="card-end"><span>{len(c['itens'])} lugares para conhecer</span>{icon()}</div></article>'''
def partner_card(p):
    links=ext(p['instagram'],'Instagram','',False)+ext(wa_partner(p),'WhatsApp','',False)
    if p.get('link'):links+=ext(p['link'],p.get('texto_link','Saiba mais'),'',False)
    return f'<article class="partner"><div class="partner-logo">{img(p["imagem"],"Logotipo de "+p["nome"],width=320,height=240)}</div><div class="partner-body"><span class="tag">{escape(p["tag"])}</span><h3>{escape(p["nome"])}</h3><p>{escape(p["descricao"])}</p><div class="partner-links">{links}</div></div></article>'
def wa_partner(p):return 'https://wa.me/'+p['whatsapp']+'?'+urlencode({'text':f'Olá! Vi {p["nome"]} no Portal Trindade e gostaria de informações.'})
def contact():
    return f'''<section class="contact-section" id="contato"><div class="wrap contact-grid"><div><p class="eyebrow">Anuncie no Portal</p><h2>Seu negócio faz parte<br>da vida de Trindade.</h2><p>Apresente sua empresa, hospedagem, imóvel, serviço ou oportunidade a quem vive, visita e procura informações sobre a cidade.</p></div><div class="contact-actions">{ext(wa('Olá! Quero conhecer os formatos de divulgação do Portal Trindade.'),'Vamos conversar','btn btn-gold')}<small>Já tem fotos, vídeos ou peças prontas? Conte o que você deseja divulgar. O Portal orienta o formato e prepara uma proposta.</small></div></div></section>'''
def reading_feature(recipe=False):
    if recipe:
        return f'<article class="reading-feature"><div>{img("imagens/capa-ebook-receitas-festival-2026.jpg","Capa do livro de receitas do XII Festival Gastronômico de Trindade 2026",width=150,height=230)}</div><div><p class="tag">Gastronomia · PDF gratuito</p><h3>Os sabores do festival,<br>na sua cozinha.</h3><p>Receitas do XII Festival Gastronômico de Trindade reunidas para guardar e experimentar.</p>{ext("/imagens/"+quote("Ebook Receitas Festival Gast Trindade 2026(1).pdf"),'Abrir livro de receitas')}</div></article>'
    return f'<article class="reading-feature blue"><div>{img("imagens/igreja-matriz-2026.webp","Igreja Matriz de Trindade, imagem de apresentação do guia turístico",width=150,height=220)}</div><div><p class="tag">Turismo · PDF gratuito</p><h3>Planeje a sua visita<br>à Capital da Fé.</h3><p>A publicação Trindade Turismo (2026), da Editora Formato 2, com colaboração de secretarias municipais, reúne história, pontos de visitação, cultura e roteiros.</p><div class="reading-actions">{ext(data["guia"]["visualizar"],'Ler o Guia Turístico')}{ext(data["guia"]["download"],'Baixar PDF')}</div></div></article>'
def home():
    main_guides=['roteiro-turistico-um-dia','espacos-do-santuario','cultura-e-lazer']
    food_guides=['gastronomia-de-bar','pamonharias','acai']
    quick=''.join(f'<a href="{href}">{icon(ico)}<span><strong>{title}</strong><small>{sub}</small></span></a>' for href,ico,title,sub in [('guia.html?categoria=gastronomia','food','Onde comer','Sabores da nossa cidade'),('hospedagem.html','bed','Onde ficar','Hotéis, pousadas e chalé'),('guia.html?categoria=fe','church','Fé e devoção','Lugares para se encontrar'),('guia.html?categoria=cultura','sun','O que fazer','Cultura, passeios e feiras')])
    gallery=''.join(f'<figure><button class="gallery-open" type="button" aria-label="Ampliar imagem: {escape(x["legenda"])}">{img(x["imagem"],x["legenda"])}</button><figcaption>{escape(x["legenda"])}</figcaption></figure>' for x in [data['galeria'][0],data['galeria'][2],data['galeria'][6]])
    books=''.join(f'<article class="book">{img(b["imagem"],"Capa: "+b["nome"],width=100,height=150)}<div><h3>{escape(b["nome"])}</h3><p>{escape(b["tag"])}</p>{ext(b["link"],b["texto_link"],"",False)}</div></article>' for b in data['leitura'][:4])
    return f'''<section class="hero"><div class="wrap"><div class="hero-grid"><div class="hero-copy"><p class="eyebrow">Seu guia na Capital da Fé</p><h1>Trindade,<br><em>de perto.</em></h1><p>Fé que acolhe. Sabores que surpreendem.<br>Lugares e histórias para quem vive<br>ou visita a nossa cidade.</p><div class="hero-actions"><a class="btn" href="guia.html">Explore Trindade {icon()}</a><a class="text-link" href="guia.html?categoria=gastronomia">Onde comer {icon()}</a></div></div><figure class="hero-photo">{img('imagens/hero-basilica-2026.webp','Vista aérea do Santuário Basílica do Divino Pai Eterno em Trindade',width=1600,height=1000,eager=True)}<figcaption class="photo-caption"><span><small>Um lugar para conhecer e sentir</small>Santuário Basílica do Divino Pai Eterno</span>{icon('pin')}</figcaption></figure></div><nav class="hero-index" aria-label="O que você procura">{quick}</nav></div></section>
    {city.home_section()}
    <section class="section"><div class="wrap">{heading('Descubra a cidade','O seu próximo passeio<br>começa aqui.','guia.html')}<div class="guide-grid">{''.join(guide_card(cmap[s]) for s in main_guides)}</div></div></section>
    <div class="discovery"><div class="wrap discovery-grid"><a href="guia.html">{icon('search')}<h3>O que você procura?</h3><p>Encontre os lugares e as indicações já apresentados pelo Portal.</p></a><a href="guias/feiras.html">{icon('sun')}<h3>Dia de feira</h3><p>Veja os dias, horários e endereços das feiras da cidade.</p></a><a href="guias/pizzarias.html">{icon('food')}<h3>Hoje tem pizza?</h3><p>Uma seleção de pizzarias para descobrir e consultar depois.</p></a></div></div>
    <section class="section"><div class="wrap">{heading('Gastronomia local','Trindade também<br>se conhece à mesa.','guia.html?categoria=gastronomia','Explorar os sabores')}<div class="guide-grid">{''.join(guide_card(cmap[s]) for s in food_guides)}</div></div></section>
    <section class="section" id="hospedagem" style="padding-top:0"><div class="wrap"><div class="lodging-feature"><div class="lodging-image">{img('imagens/igreja-matriz-2026.webp','Igreja Matriz, no centro de Trindade',width=900,height=720)}</div><div class="lodging-copy"><p class="eyebrow">Fique mais um pouco</p><h2>Encontre seu lugar<br>em Trindade.</h2><p>Hotéis, pousadas e chalé em uma lista organizada por nome, tipo e bairro. Escolha e fale diretamente com o estabelecimento.</p><div class="countline"><span><strong>72</strong>hospedagens</span><span><strong>21</strong>hotéis</span><span><strong>50</strong>pousadas</span><span><strong>1</strong>chalé</span></div><a class="btn btn-gold" href="hospedagem.html">Ver todos os hotéis e pousadas {icon()}</a></div></div></div></section>
    <section class="section" id="gastronomia" style="padding-top:0"><div class="wrap">{heading('Quem está com o Portal','Negócios da nossa cidade.')}<div class="partner-grid">{''.join(partner_card(p) for p in data['parceiros']['gastronomia'])}</div><p class="editorial-note">Parceiros anunciantes do Portal Trindade. Consulte cardápios, horários e condições diretamente nos canais de cada estabelecimento.</p></div></section>
    <section class="section faith-section"><div class="wrap faith-grid"><div class="faith-image">{img('imagens/galeria-vitral.webp','Vitral do Santuário Basílica do Divino Pai Eterno',width=1215,height=1295)}</div><div class="faith-copy"><p class="eyebrow">Fé que faz parte da nossa história</p><h2>Há lugares que acolhem.<br>E histórias que ficam.</h2><p>Conheça os espaços de devoção da Capital da Fé e acompanhe o quadro <strong>Milagres do Pai Eterno</strong>: testemunhos compartilhados pela comunidade, em palavras de quem viveu.</p><div class="faith-links"><a class="text-link" href="guias/igrejas-alem-do-roteiro.html">Outros espaços de fé {icon()}</a>{ext('https://www.instagram.com/trindadeportal/p/DdyhFtmnKmp/','Conhecer o quadro')}</div></div></div></section>
    <section class="section" id="cultura"><div class="wrap">{heading('Cultura e leitura','Leve um pouco de Trindade<br>com você.','leitura.html','Ver guias e livros')}<div class="reading-grid">{reading_feature()}{reading_feature(True)}</div><div class="book-shelf">{books}</div></div></section>
    <section class="section" id="galeria" style="padding-top:0"><div class="wrap">{heading('Nosso olhar','Retratos da Capital da Fé.')}<div class="gallery">{gallery}</div></div></section>
    <section class="social-band"><div class="wrap"><div><h2>A cidade continua no Instagram.</h2><p>Novos lugares, histórias, indicações e a participação de quem conhece Trindade.</p></div>{ext(INSTA,'Acompanhe @trindadeportal')}</div></section>{contact()}
    <dialog class="lightbox" id="photo-dialog" aria-labelledby="dialog-caption"><form method="dialog"><button>Fechar ×</button></form><img id="dialog-image" alt=""><p id="dialog-caption" class="lightbox-caption"></p></dialog>'''

def intro(kicker,title,lead,breadcrumb='Início',prefix='./'):
    return f'<section class="page-intro"><div class="wrap"><nav class="breadcrumb" aria-label="Caminho"><a href="{prefix}index.html">Início</a><span>/</span><span>{escape(breadcrumb if breadcrumb!="Início" else title)}</span></nav><p class="eyebrow">{escape(kicker)}</p><h1>{escape(title)}</h1><p class="lead">{escape(lead)}</p>'
def directory():
    filters=''.join(f'<button class="filter-btn" data-category="{c}" aria-pressed="{str(c=="todos").lower()}" type="button">{n}</button>' for c,n in [('todos','Todos'),('historia','História'),('gastronomia','Gastronomia'),('fe','Fé e devoção'),('turismo','Turismo'),('cultura','Cultura e lazer')])
    order=['roteiro-turistico-um-dia','gastronomia-de-bar','feiras','pizzarias','pamonharias','hamburguerias','acai','espacos-do-santuario','igrejas-alem-do-roteiro','cultura-e-lazer','onde-ir-a-noite']
    return intro('O guia do Portal','O que você quer conhecer?','Histórias, respostas e indicações locais para descobrir Trindade por assunto ou pelo nome do lugar.','Explore Trindade')+f'''<label class="searchbar">{icon('search')}<span class="sr-only">Buscar histórias, guias e estabelecimentos</span><input id="guide-search" type="search" placeholder="Busque por história, romaria, pizza, museu..." autocomplete="off"></label><div class="filters" role="group" aria-label="Filtrar guias por assunto">{filters}</div></div></section><section class="directory-section"><div class="wrap"><p class="result-count" id="result-count" aria-live="polite">{len(collections)+len(city.articles)} conteúdos disponíveis</p><div class="guide-grid">{''.join(city.card(a,searchable=True) for a in city.articles)}{''.join(guide_card(cmap[s]) for s in order)}<div id="empty-state" class="empty-state" hidden><h2>Vamos tentar outra busca?</h2><p>Nenhum conteúdo corresponde aos filtros escolhidos.</p><button id="clear-guides" type="button" class="btn btn-outline">Mostrar todos os conteúdos</button></div></div><p class="notice">Procurando um hotel ou uma pousada? <a class="text-link" href="hospedagem.html">Consulte o guia de hospedagem {icon()}</a></p></div></section>'''
def article(c):
    items=[]
    for i in c['itens']:
        details=''
        if i.get('horario'):details+=f'<p class="detail"><strong>Quando:</strong> {escape(i["horario"])}</p>'
        if i.get('endereco'):details+=f'<p class="detail"><strong>Onde:</strong> {escape(i["endereco"])}</p>'
        if i.get('instagram'):details+=ext(i['instagram'],'Consultar no Instagram')
        items.append(f'<section class="place"><div class="place-heading"><h2>{escape(i["nome"])}</h2></div><p>{escape(i["descricao"])}</p>{details}</section>')
    sources=[c['fonte_url']]+c.get('fontes_adicionais',[])
    def publication_link(url):
        code=re.search(r'/(?:p|reel)/([^/]+)',url).group(1)
        date=publication_dates[code]
        return ext(url,f'Publicação de {date[6:8]}/{date[4:6]}/{date[:4]}','',False)
    source_links=' · '.join(publication_link(u) for u in sources)
    if c.get('fontes_verificacao'):
        source_links+='<br><br><strong>Referências complementares</strong><ul>'+''.join('<li>'+ext(s['url'],s['titulo'],'',False)+'</li>' for s in c['fontes_verificacao'])+'</ul>'
    return intro(labels[c['categoria']],c['titulo'],c['resumo'],'Explore Trindade / '+c['titulo'],'../')+f'''<div class="article-tools"><a class="text-link" href="../guia.html?categoria={c['categoria']}">Mais guias de {labels[c['categoria']].lower()} {icon()}</a><button class="btn btn-outline" id="share-guide" type="button">Compartilhar {icon('share')}</button><span id="share-status" class="share-message" role="status"></span></div></div></section><div class="wrap article-layout"><div><div class="article-items">{''.join(items)}</div><aside class="source-note"><strong>Para planejar a visita</strong><br>{escape(c['observacao'])}<br>Conteúdo organizado em 27/09/2026 a partir das publicações do Portal Trindade. {source_links}</aside></div><aside class="article-aside"><figure>{img(c['imagem'],'Imagem de apresentação: '+c['titulo'],width=800,height=1000 if c['tipo_imagem']=='arte' else 650)}<figcaption>{'Arte publicada no Instagram do Portal Trindade.' if c['tipo_imagem']=='arte' else 'Imagem do acervo do Portal Trindade para apresentação do roteiro.'}</figcaption></figure><div class="aside-box"><h2>Trindade tem muito mais.</h2><p>Conhece um lugar que merece aparecer por aqui? Sua indicação ajuda o Portal a continuar descobrindo a cidade.</p>{ext(wa('Olá! Gostaria de indicar um lugar para o guia do Portal Trindade.'),'Indicar um lugar')}<a class="text-link" href="../hospedagem.html">Encontre uma hospedagem {icon()}</a></div></aside></div>'''
def lodging_card(i):
    digits=lambda s:re.sub(r'\D','',str(s))
    phone=digits(i.get('telefone',''))
    if phone and not phone.startswith('55'):phone='55'+phone
    whatsapp=digits(str(i.get('whatsapp','')).split('/')[0])
    if whatsapp and not whatsapp.startswith('55'):whatsapp='55'+whatsapp
    links=f'<a href="tel:+{phone}">Ligar</a>' if phone else ''
    if whatsapp:links+=ext('https://wa.me/'+whatsapp+'?'+urlencode({'text':f'Olá! Vi {i["nome"]} no Portal Trindade e gostaria de informações sobre hospedagem.'}),'WhatsApp','',False)
    if i.get('endereco') and not i.get('endereco_a_confirmar'):links+=ext('https://www.google.com/maps/search/?'+urlencode({'api':'1','query':i['nome']+', '+i['endereco']}),'Ver no mapa','',False)
    if i.get('site'):links+=ext(i['site'],'Site','',False)
    if i.get('instagram'):links+=ext(i['instagram'],'Instagram','',False)
    other=''
    if i.get('telefone_alternativo'):other+=f'<p>Outro contato: {escape(i["telefone_alternativo"])}</p>'
    if i.get('email'):other+=f'<p><a href="mailto:{escape(i["email"])}">{escape(i["email"])}</a></p>'
    if i.get('observacao'):other+=f'<p class="editorial-note">{escape(i["observacao"])}</p>'
    if i.get('fonte_contato'):other+='<p class="editorial-note">Contato e dados conferidos no '+ext(i['fonte_contato'],'site do estabelecimento','',False)+' em 27/09/2026.</p>'
    phone_line=f'<p class="phone"><a href="tel:+{phone}">{escape(i["telefone"])}</a></p>' if phone else ''
    return f'''<article class="lodging-card" data-lodging data-type="{escape(i['tipo'])}" data-neighborhood="{escape(i.get('bairro',''))}" data-search="{escape(' '.join(str(i.get(k,'')) for k in ['nome','tipo','bairro','endereco']))}"><span class="tag">{escape(i['tipo'])} · {escape(i.get('bairro','Trindade'))}</span><h2>{escape(i['nome'])}</h2><p>{escape(i.get('endereco',''))}</p>{phone_line}{other}<div class="partner-links">{links}</div></article>'''
def lodging_page():
    items=sorted(lodgings['estabelecimentos'],key=lambda i:i['nome'].casefold())
    neighborhoods=sorted(set(i.get('bairro','') for i in items)-{''})
    return intro('Guia de hospedagem','Hotéis e pousadas em Trindade','Encontre onde ficar na Capital da Fé. Pesquise pelo nome, escolha o bairro e fale diretamente com a hospedagem.','Hotéis e pousadas')+f'''<div class="stats-inline"><span><strong>72</strong>hospedagens</span><span><strong>21</strong>hotéis</span><span><strong>50</strong>pousadas</span><span><strong>1</strong>chalé</span></div></div></section><section class="section"><div class="wrap"><div class="lodging-toolbar"><label class="searchbar">{icon('search')}<span class="sr-only">Buscar hospedagem por nome, bairro ou endereço</span><input id="lodging-search" type="search" placeholder="Hotel, pousada, bairro..." autocomplete="off"></label><label class="select-field"><span>Tipo de hospedagem</span><select id="type-filter"><option value="">Todos os tipos</option><option>Hotel</option><option>Pousada</option><option>Chalé</option></select></label><label class="select-field"><span>Bairro</span><select id="neighborhood-filter"><option value="">Todos os bairros</option>{''.join(f'<option>{escape(n)}</option>' for n in neighborhoods)}</select></label></div><div class="form-row"><p id="result-count" class="result-count" aria-live="polite">72 hospedagens encontradas</p><button id="clear-filters" class="btn btn-outline" type="button" hidden>Limpar filtros</button></div><div class="lodging-grid" id="results">{''.join(lodging_card(i) for i in items)}<div class="empty-state" id="empty-state" hidden><h2>Nenhuma hospedagem encontrada.</h2><p>Tente outro termo ou limpe os filtros.</p></div></div><aside class="notice"><strong>Antes de reservar</strong><br>Lista em ordem alfabética, sem classificação comercial. Base organizada em 12/09/2026 e revisada documentalmente em 27/09/2026, com confirmação parcial em fontes próprias e registros históricos. A inclusão na lista não comprova funcionamento atual. Confirme contatos, endereço, valores e disponibilidade com o estabelecimento. O Portal Trindade não intermedeia reservas nem recebe pagamentos pelas hospedagens.</aside></div></section>'''
def reading_page():
    books=''.join(f'<article class="book-full">{img(b["imagem"],"Capa: "+b["nome"],width=160,height=240)}<div><p class="tag">{escape(b["tag"])}</p><h2>{escape(b["nome"])}</h2><p>{escape(b["descricao"])}</p>{ext(b["link"],b["texto_link"])}</div></article>' for b in data['leitura'])
    return intro('Cultura e leitura','Para ler, conhecer e guardar.','Guias gratuitos para explorar Trindade e leituras de fé, reflexão e recomeço.','Cultura e leitura')+'</div></section>'+f'<section class="section"><div class="wrap"><div class="reading-grid">{reading_feature()}{reading_feature(True)}</div></div></section><section class="section" style="padding-top:0"><div class="wrap">{heading("Na estante do Portal","Histórias que fazem companhia.")}<div class="book-grid-full">{books}</div><p class="notice">Algumas obras são gratuitas; outras estão disponíveis em lojas externas. Consulte preço, formato e disponibilidade na página de cada livro.</p></div></section>'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='.');parser.add_argument('--preview',action='store_true');args=parser.parse_args()
    out=(ROOT/args.out).resolve();out.mkdir(parents=True,exist_ok=True);(out/'guias').mkdir(exist_ok=True)
    pages={'index.html':('Trindade (GO): turismo, história, fé e gastronomia','Conheça Trindade, em Goiás: história, Divino Pai Eterno, Romaria, cultura, gastronomia e 72 hospedagens. Guias locais e respostas para planejar a visita.',home(),'imagens/hero-basilica-2026.webp'), 'guia.html':('Guias de Trindade: história, turismo e lugares para conhecer','Explore a história de Trindade, a devoção ao Pai Eterno, cultura e gastronomia. Busque lugares, pamonharias, feiras e roteiros para sua visita.',directory(),None),'hospedagem.html':('Hotéis e pousadas em Trindade','Consulte 72 hospedagens em Trindade-GO, com pesquisa por nome, tipo e bairro, telefone e contato direto.',lodging_page(),None),'leitura.html':('Cultura, guias e livros','Guia turístico de Trindade, receitas do Festival Gastronômico e livros de fé e reflexão.',reading_page(),None)}
    pages.update({
        'conheca-trindade.html':('Conheça Trindade: história, fé, cultura e turismo','História de Trindade, devoção ao Divino Pai Eterno, Romaria, cultura, gastronomia e informações para visitar a cidade, com fontes institucionais.',city.hub(),None),
        'perguntas-frequentes.html':('Perguntas frequentes sobre Trindade (GO)','Respostas sobre a história de Trindade, missas, Basílica, Romaria, museu, gastronomia, hospedagem e planejamento da visita.',city.faq(),None),
        'sobre-o-portal.html':('Sobre o Portal Trindade e nossos critérios editoriais','Conheça o Portal Trindade, as fontes de informação, os critérios editoriais e o canal para correções e sugestões.',city.about(wa('Olá! Gostaria de enviar uma correção ou sugestão sobre o site do Portal Trindade.')),None)
    })
    for a in city.articles:
        path='guias/'+a['slug']+'.html'
        (out/path).write_text(page(a['titulo'],a['resumo'],city.article(a),path,prefix='../',active='conheca-trindade.html',preview=args.preview,hero=a['imagem'],schema=city.schema(a)),encoding='utf-8')
    for path,(title,desc,body,hero) in pages.items(): (out/path).write_text(page(title,desc,body,path,active=path,preview=args.preview,hero=hero),encoding='utf-8')
    for c in collections:
        path='guias/'+c['slug']+'.html'; (out/path).write_text(page(c['titulo'],c['resumo'],article(c),path,prefix='../',preview=args.preview),encoding='utf-8')
    missing=intro('Portal Trindade','Vamos encontrar seu caminho.','Esta página não está disponível. Continue pelo guia e descubra os lugares da nossa cidade.','Página não encontrada',prefix='./' if args.preview else '/')+'</div></section><section class="section"><div class="wrap"><a class="btn" href="/guia.html">Ir para o guia '+icon()+'</a></div></section>'
    if args.preview: missing=missing.replace('href="/guia.html"','href="./guia.html"')
    (out/'404.html').write_text(page('Página não encontrada','Explore os guias do Portal Trindade.',missing,'404.html',prefix='./' if args.preview else '/',preview=args.preview))
    if out!=ROOT:
        for f in ['portal.css','portal.js']:shutil.copyfile(ROOT/f,out/f)
    if not args.preview:
        (ROOT/'data/guias.json').write_text(json.dumps(collections,ensure_ascii=False,indent=2)+'\n')
        urls=[BASE]+[BASE+p for p in pages if p!='index.html']+[BASE+'guias/'+c['slug']+'.html' for c in collections]+[BASE+'guias/'+a['slug']+'.html' for a in city.articles]
        (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{escape(url)}</loc><lastmod>{DATE}</lastmod></url>' for url in urls)+'</urlset>\n')
        (out/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /previa-2026/\nSitemap: '+BASE+'sitemap.xml\n')
    print(json.dumps({'paginas':len(pages)+len(collections)+len(city.articles)+1,'artigos':len(city.articles),'respostas':len(city.questions),'guias':len(collections),'lugares':sum(len(c['itens']) for c in collections),'hospedagens':len(lodgings['estabelecimentos']),'destino':str(out)},ensure_ascii=False))
if __name__=='__main__':main()
