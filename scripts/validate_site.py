#!/usr/bin/env python3
"""Verifica navegação, arquivos, IDs e integridade do diretório antes de publicar."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import sys

root=Path(__file__).resolve().parents[1]
out=root/(sys.argv[1] if len(sys.argv)>1 else '.')
if not out.is_dir():
    sys.exit(f'Diretório de validação inexistente: {out}')
if not out.is_dir():
    sys.exit(f'Diretório de validação inexistente: {out}')
class Document(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.ids=[];self.h1=0;self.missing_alt=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if 'id' in a:self.ids.append(a['id'])
        if tag=='img' and 'alt' not in a:self.missing_alt+=1
        for k in ['src','href']:
            if a.get(k):self.refs.append(a[k])
docs={}
for path in list(out.glob('*.html'))+list((out/'guias').glob('*.html')):
    if path.name=='responsive-check.html' or path.name.startswith('google'):continue
    doc=Document();doc.feed(path.read_text());docs[path.resolve()]=doc
errors=[];count=0
if not docs:errors.append('Nenhuma página encontrada para validar.')
if not docs:
    sys.exit(f'Nenhuma página encontrada em {out}')
for path,doc in docs.items():
    if doc.h1!=1:errors.append(f'{path.name}: {doc.h1} títulos H1')
    if doc.missing_alt:errors.append(f'{path.name}: imagens sem texto alternativo')
    dup=[id for id,n in Counter(doc.ids).items() if n>1]
    if dup:errors.append(f'{path.name}: IDs duplicados {dup}')
    for raw in doc.refs:
        u=urlsplit(raw)
        if u.scheme or u.netloc:continue
        count+=1
        if u.path:
            target=(root/unquote(u.path).lstrip('/') if u.path.startswith('/') else path.parent/unquote(u.path)).resolve()
        else:target=path
        if not target.exists():errors.append(f'{path.name}: arquivo ausente {raw}')
        if u.fragment and target in docs and unquote(u.fragment) not in docs[target].ids:errors.append(f'{path.name}: âncora ausente {raw}')
d=json.loads((root/'hospedagens.json').read_text());items=d['estabelecimentos']
assert len(items)==d['total_confirmados']==72
assert len({i['nome'].casefold() for i in items})==len(items)
assert Counter(i['tipo'] for i in items)=={'Hotel':21,'Pousada':50,'Chalé':1}
if errors:print('\n'.join(errors));sys.exit(1)
print(f'OK: {len(docs)} páginas, {count} referências locais e 72 hospedagens verificadas.')
