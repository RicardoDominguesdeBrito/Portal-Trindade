#!/usr/bin/env python3
"""Build the editorial image directory without replacing existing guides."""
from pathlib import Path
import html,json,re
ROOT=Path(__file__).resolve().parents[1]
e=lambda v:html.escape(str(v),quote=True)
def add_visual_navigation(s):
 s=s.replace("112 fichas","121 fichas")
 mobile='<nav id="mobile-nav" class="mobile-nav" aria-label="Menu do celular" hidden>'
 link='<a href="/lugares.html">Guia visual · 121 fichas</a>'
 if mobile+link not in s:s=s.replace(mobile,mobile+link,1)
 hero='<div class="hero-actions">'
 button='<a class="btn btn-gold" href="/lugares.html">Guia visual · 121 fichas →</a>'
 if hero+button not in s:s=s.replace(hero,hero+button,1)
 return s

def build_directory(out):
 p=out/'guia.html';s=p.read_text()
 links=re.findall(r'<h3><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h3>',s)
 if not links:
  old=re.search(r'<!-- roteiros-start -->(.*?)<!-- roteiros-end -->',s,re.S)
  if old:links=re.findall(r'<a href="([^"]+)">(.*?)</a>',old.group(1))
 assert len(links)==17, 'Expected all17 existing guides'
 topics=[('', 'Todos'),('historia','História'),('gastronomia','Gastronomia'),('fe','Fé e devoção'),('turismo','Turismo'),('cultura','Cultura e lazer'),('comercios','Comércios e serviços'),('hospedagem','Hospedagem'),('compras','Compras'),('servicos','Serviços e bem-estar')]
 filters=''.join(f'<a class="filter-btn" href="/lugares.html{("?tipo="+key) if key else ""}">{label}</a>' for key,label in topics)
 stories=''.join(f'<li><a href="{url}">{title}</a></li>' for url,title in links)
 main=f'''<main id="conteudo"><section class="page-intro"><div class="wrap"><nav class="breadcrumb" aria-label="Caminho"><a href="./index.html">Início</a><span>/</span><span>Explore Trindade</span></nav><p class="eyebrow">O guia do Portal</p><h1>O que você quer conhecer?</h1><p class="lead">Encontre comércios, serviços e lugares nas 121 fichas do Portal. Escolha um assunto ou busque pelo nome.</p><form action="/lugares.html" method="get" role="search"><label class="searchbar"><span class="sr-only">Buscar nas fichas</span><input name="q" type="search" placeholder="Busque por nome ou categoria..." autocomplete="off"></label><button type="submit" class="btn">Buscar</button></form><nav class="filters" aria-label="Escolher assunto das fichas">{filters}</nav><p><a class="text-link" href="#roteiros">Histórias e roteiros da cidade ↓</a></p></div></section><section class="directory-section" id="roteiros"><div class="wrap"><details class="guide-stories"><summary>Histórias e roteiros da cidade · 17 conteúdos</summary><p>Leituras para conhecer a história, planejar passeios e aprofundar a visita.</p><!-- roteiros-start --><ul>{stories}</ul><!-- roteiros-end --></details><p class="notice">Procurando um hotel ou uma pousada? <a class="text-link" href="hospedagem.html">Consulte a lista completa de hospedagens →</a></p></div></section></main>'''
 s=re.sub(r'<main[^>]*>.*?</main>',main,s,flags=re.S)
 if '/guia-entry.js' not in s:s=s.replace('</head>','<script defer src="/guia-entry.js?v=20261019"></script><link rel="stylesheet" href="/fichas.css?v=20261019-2"></head>')
 p.write_text(add_visual_navigation(s))

def build(out=ROOT):
 out=Path(out);data=json.loads((ROOT/'data/fichas.json').read_text());items=data['fichas']
 source=(out/'index.html').read_text();headbody=add_visual_navigation(source).split('<body>',1)[1].split('<main',1)[0];footer='<footer'+source.rsplit('<footer',1)[1]
 cards=[]
 for i in items:
  links=f'<a href="/{e(i["imagem"])}" target="_blank" rel="noopener">Abrir arte completa ↗</a>'
  if i.get('instagram'):links+=f'<a href="{e(i["instagram"])}" target="_blank" rel="noopener noreferrer">Instagram ↗</a>'
  sources=''.join(f'<li><a href="{e(u)}" target="_blank" rel="noopener noreferrer">Fonte {n+1}</a></li>' for n,u in enumerate(i['fontes']))
  credits=''
  if i.get('credito'):credits+=f'<p>{e(i["credito"])}</p>'
  if i.get('fonte_foto'):credits+=f'<p><a href="{e(i["fonte_foto"])}" target="_blank" rel="noopener noreferrer">Fonte da fotografia</a></p>'
  if i.get('licenca_url'):credits+=f'<p><a href="{e(i["licenca_url"])}" rel="license">{e(i["licenca"])}</a></p>'
  desc=f'<p>{e(i["descricao"])}</p>' if i.get('descricao') else ''
  address=f'<p>{e(i["localizacao"])}</p>' if i.get('localizacao') else ''
  cards.append(f'''<article class="ficha" id="{e(i['id'])}" data-ficha data-grupo="{e(i['grupo'])}" data-categoria="{e(i['categoria'])}" data-busca="{e(i['nome']+' '+i['categoria']+' '+i.get('localizacao',''))}"><a class="ficha-image" href="/{e(i['imagem'])}" target="_blank" rel="noopener" aria-label="Abrir arte completa de {e(i['nome'])}"><img src="/{e(i['imagem'])}" width="1080" height="1920" alt="Ficha do Portal Trindade: {e(i['nome'])}" loading="lazy" decoding="async"></a><div class="ficha-body"><span class="tag">{e(i['categoria'])}</span><h2>{e(i['nome'])}</h2>{desc}{address}<div class="ficha-links">{links}</div><details><summary>Fontes e contexto</summary><p>{e(i['nota'])}</p>{credits}<ul>{sources}</ul></details></div></article>''')
 categories=sorted(set(i['categoria'] for i in items))
 options=''.join(f'<option>{e(c)}</option>' for c in categories)
 title='Comércios, serviços e lugares de Trindade'
 body=f'''<main id="conteudo"><section class="section ficha-intro"><div class="wrap"><p class="eyebrow">Guia visual · Portal Trindade</p><h1>{title}</h1><p>Explore 103 comércios e serviços e 18 lugares de turismo e cultura nas artes do Portal.</p><p class="editorial-note">Seleção editorial em ordem alfabética, sem ranking. A presença neste guia não indica parceria comercial. Fotos de arquivo e imagens de produtos podem não representar a aparência, o estoque ou a programação atuais. Confirme antes de visitar.</p><a class="text-link" href="/guia.html">← Escolher outro assunto</a><div class="ficha-toolbar"><label>Buscar por nome ou categoria<input id="ficha-search" type="search" placeholder="O que você procura?" autocomplete="off"></label><label>Assunto<select id="ficha-grupo"><option value="">Todos</option><option>Comércios e serviços</option><option>Turismo e cultura</option><option value="historia">História</option><option value="gastronomia">Gastronomia</option><option value="fe">Fé e devoção</option><option value="cultura">Cultura e lazer</option><option value="compras">Compras</option><option value="servicos">Serviços e bem-estar</option></select></label><label>Categoria<select id="ficha-categoria"><option value="">Todas</option>{options}</select></label><button class="btn btn-outline" type="button" id="ficha-clear">Limpar</button></div><p id="ficha-count" aria-live="polite">121 fichas</p></div></section><section class="section ficha-results"><div class="wrap"><div class="fichas-grid">{''.join(cards)}</div><p id="ficha-empty" hidden>Nenhum resultado. Tente outro nome ou limpe os filtros.</p><button class="btn" type="button" id="ficha-more" hidden>Mostrar mais</button><noscript><p>Ative o JavaScript para pesquisar e filtrar. Todas as fichas estão disponíveis abaixo.</p></noscript><p class="editorial-note">Guia atualizado em 19/10/2026. Créditos e condições de uso estão em “Fontes e contexto” de cada ficha.</p></div></section></main>'''
 page=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} | Portal Trindade</title><meta name="description" content="Descubra 121 fichas de comércios, serviços, turismo e cultura de Trindade. Pesquise por nome e categoria e consulte as artes e fontes do Portal."><meta name="theme-color" content="#17314e"><link rel="canonical" href="https://www.trindadeportal.com.br/lugares.html"><link rel="stylesheet" href="/portal.css?v=20260927-2"><link rel="stylesheet" href="/fichas.css?v=20261019-2"><script defer src="/portal.js?v=20260927-2"></script><script defer src="/fichas.js?v=20261019-3"></script><link rel="icon" href="/imagens/logo-portal-trindade.jpg"></head><body>{headbody}{body}{footer}'''
 (out/'lugares.html').write_text(page)
 cta='''<!-- fichas-start --><section class="section" id="guia-visual"><div class="wrap"><p class="eyebrow">Guia visual</p><h2>Comércios, serviços e lugares de Trindade</h2><p>121 fichas para explorar a cidade: 103 comércios e serviços e 18 lugares de turismo e cultura.</p><a class="btn" href="/lugares.html">Explorar as fichas →</a></div></section><!-- fichas-end -->'''
 build_directory(out)
 for name in ['index.html']:
  p=out/name;s=p.read_text();s=re.sub(r'<!-- fichas-start -->.*?<!-- fichas-end -->','',s,flags=re.S)
  # Guide directory gets a prominent entry before its existing content; home retains existing sections.
  s=s.replace('<main id="conteudo">','<main id="conteudo">'+cta,1) if name=='guia.html' else s.replace('</main>',cta+'</main>',1)
  p.write_text(add_visual_navigation(s))
 sitemap=out/'sitemap.xml'
 if sitemap.exists():
  s=sitemap.read_text();url='https://www.trindadeportal.com.br/lugares.html'
  if url not in s:s=s.replace('</urlset>',f'<url><loc>{url}</loc><lastmod>2026-10-19</lastmod></url></urlset>');sitemap.write_text(s)
if __name__=='__main__':build()
