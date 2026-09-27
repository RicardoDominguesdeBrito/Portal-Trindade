(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const normalize = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  const menu = $('#mobile-nav'), toggle = $('#menu-toggle');
  const setMenu = open => { if (!menu || !toggle) return; menu.hidden = !open; toggle.setAttribute('aria-expanded', String(open)); toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu'); };
  toggle?.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  $$('#mobile-nav a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') { setMenu(false); toggle.focus(); } });
  document.addEventListener('click', e => { if (menu && !menu.hidden && !e.target.closest('.site-header')) setMenu(false); });
  const params = new URLSearchParams(location.search);
  const search = $('#guide-search');
  if (search) {
    const cards = $$('[data-guide-card]'), filters = $$('[data-category]');
    let category = filters.some(b => b.dataset.category === params.get('categoria')) ? params.get('categoria') : 'todos';
    search.value = params.get('q') || '';
    const apply = () => {
      const terms = normalize(search.value).split(/\s+/).filter(Boolean);
      let count = 0;
      cards.forEach(card => { const hit = (category === 'todos' || card.dataset.categoryName === category) && terms.every(t => normalize(card.dataset.search).includes(t)); card.hidden = !hit; if (hit) count++; });
      filters.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.category === category)));
      $('#result-count').textContent = `${count} ${count === 1 ? 'guia encontrado' : 'guias encontrados'}`;
      $('#empty-state').hidden = count > 0;
      const q = new URLSearchParams(); if (search.value.trim()) q.set('q',search.value.trim()); if (category !== 'todos') q.set('categoria',category);
      history.replaceState(null,'',location.pathname + (q.size ? '?' + q : '') + location.hash);
    };
    search.addEventListener('input', apply);
    filters.forEach(b => b.addEventListener('click', () => { category = b.dataset.category; apply(); }));
    $('#clear-guides')?.addEventListener('click', () => { search.value = ''; category = 'todos'; apply(); search.focus(); });
    apply();
  }
  const lodgingSearch = $('#lodging-search');
  if (lodgingSearch) {
    const cards = $$('[data-lodging]'), type = $('#type-filter'), neighborhood = $('#neighborhood-filter');
    lodgingSearch.value = params.get('q') || '';
    const apply = () => {
      const terms = normalize(lodgingSearch.value).split(/\s+/).filter(Boolean);
      let count = 0;
      cards.forEach(card => { const hit = terms.every(t => normalize(card.dataset.search).includes(t)) && (!type.value || card.dataset.type === type.value) && (!neighborhood.value || card.dataset.neighborhood === neighborhood.value); card.hidden = !hit; if (hit) count++; });
      $('#result-count').textContent = `${count} ${count === 1 ? 'hospedagem encontrada' : 'hospedagens encontradas'}`;
      $('#empty-state').hidden = count > 0;
      $('#clear-filters').hidden = !(lodgingSearch.value || type.value || neighborhood.value);
    };
    lodgingSearch.addEventListener('input',apply); type.addEventListener('change',apply); neighborhood.addEventListener('change',apply);
    $('#clear-filters').addEventListener('click', () => { lodgingSearch.value='';type.value='';neighborhood.value='';apply();lodgingSearch.focus(); });
    apply();
  }
  const dialog = $('#photo-dialog');
  $$('.gallery-open').forEach(button => button.addEventListener('click', () => { if (!dialog || !dialog.showModal) return; const img = button.querySelector('img'); $('#dialog-image').src = img.src; $('#dialog-image').alt = img.alt; $('#dialog-caption').textContent = img.alt; dialog.showModal(); }));
  dialog?.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
  $('#share-guide')?.addEventListener('click', async () => {
    const url = location.pathname.includes('/previa-2026/') ? location.href : (document.querySelector('link[rel=canonical]')?.href || location.href);
    const status = $('#share-status');
    try { if (navigator.share) { await navigator.share({title:document.title,url}); status.textContent=''; } else { await navigator.clipboard.writeText(url); status.textContent='Link copiado.'; } }
    catch (e) { if (e.name !== 'AbortError') { status.textContent='Copie o endereço na barra do navegador para compartilhar.'; } }
  });
})();
