(() => {
      'use strict';

      const $ = selector => document.querySelector(selector);
      const $$ = selector => [...document.querySelectorAll(selector)];
      const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, char => ({
        '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'
      })[char]);
      const safeUrl = value => {
        try {
          const url = new URL(value, window.location.origin);
          return ['http:','https:'].includes(url.protocol) ? url.href : '#';
        } catch { return '#'; }
      };
      const normalize = value => String(value || '')
        .normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();

      const icons = {
        phone:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.8a2 2 0 0 1-.45 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.45c.9.35 1.8.58 2.8.7A2 2 0 0 1 22 16.9Z"/></svg>',
        whatsapp:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9.5 9.5 0 0 1-3.8-1L3 20.5l1.5-5a8.5 8.5 0 1 1 16.5-4Z"/><path d="M8.5 8.5c.5 3 2 4.5 5 5"/></svg>',
        map:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
        link:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 3h7v7M10 14 21 3M21 14v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h6"/></svg>'
      };

      const state = { all: [], filtered: [] };
      const search = $('#search');
      const typeFilter = $('#type-filter');
      const neighborhoodFilter = $('#neighborhood-filter');
      const clearFilters = $('#clear-filters');

      const menuButton = $('#menu-toggle');
      const menu = $('#menu-mobile');
      const setMenu = open => {
        menu.classList.toggle('hidden', !open);
        menuButton.setAttribute('aria-expanded', String(open));
        menuButton.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
        $('#menu-icon').innerHTML = open ? '<path d="m6 6 12 12M18 6 6 18"/>' : '<path d="M4 7h16M4 12h16M4 17h16"/>';
      };
      menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
      $$('.mobile-link').forEach(link => link.addEventListener('click', () => setMenu(false)));

      const header = $('#topo');
      const updateHeader = () => header.classList.toggle('shadow-[0_10px_35px_-25px_rgba(20,33,58,.5)]', window.scrollY > 16);
      updateHeader();
      addEventListener('scroll', updateHeader, { passive:true });

      const waUrl = (number, name) => {
        const message = `Olá! Vi ${name} no Portal Trindade e gostaria de informações sobre hospedagem.`;
        return `https://wa.me/${String(number || '').replace(/\D/g,'')}?text=${encodeURIComponent(message)}`;
      };

      const renderCard = item => {
        const name = escapeHtml(item.nome);
        const phone = escapeHtml(item.telefone);
        const alt = escapeHtml(item.telefone_alternativo);
        const rating = Number(item.nota_google);
        const reviews = Number(item.avaliacoes_google);
        const ratingHtml = Number.isFinite(rating)
          ? `<span class="rating" aria-label="Nota ${rating.toFixed(1).replace('.',',')} no Google, ${Number.isFinite(reviews) ? reviews : 0} avaliações"><span class="star">★</span>${rating.toFixed(1).replace('.',',')}${Number.isFinite(reviews) ? ` · ${reviews}` : ''}</span>`
          : '';
        const contactLines = [
          phone ? `<div class="contact-line"><strong>Telefone:</strong> <a href="tel:+${String(item.telefone).replace(/\D/g,'')}">${phone}</a></div>` : '',
          alt ? `<div class="contact-line"><strong>Alternativo:</strong> ${alt}</div>` : '',
          item.email ? `<div class="contact-line"><strong>E-mail:</strong> <a href="mailto:${escapeHtml(item.email)}">${escapeHtml(item.email)}</a></div>` : ''
        ].filter(Boolean).join('');
        const actions = [];
        const phoneHref = item.telefone ? `+${String(item.telefone).replace(/\D/g,'')}` : '';
        const whatsappNumber = item.whatsapp ? String(item.whatsapp).split('/')[0].replace(/\D/g,'') : '';
        const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${item.nome}, ${item.endereco}`)}`;
        if (phoneHref) actions.push(`<a class="action action-primary" href="tel:${escapeHtml(phoneHref)}">${icons.phone}Ligar</a>`);
        if (whatsappNumber) actions.push(`<a class="action action-whatsapp" href="${waUrl(whatsappNumber, item.nome)}" target="_blank" rel="noopener noreferrer">${icons.whatsapp}WhatsApp</a>`);
        actions.push(`<a class="action action-secondary" href="${safeUrl(mapUrl)}" target="_blank" rel="noopener noreferrer">${icons.map}Localizar</a>`);
        if (item.site) actions.push(`<a class="action action-secondary" href="${safeUrl(item.site)}" target="_blank" rel="noopener noreferrer">${icons.link}Site</a>`);
        if (item.instagram) actions.push(`<a class="action action-secondary" href="${safeUrl(item.instagram)}" target="_blank" rel="noopener noreferrer">Instagram</a>`);

        return `<article class="lodging-card">
          <div class="card-top"><span class="type-pill">${escapeHtml(item.tipo)}</span>${ratingHtml}</div>
          <h3>${name}</h3>
          <div class="neighborhood">${escapeHtml(item.bairro || 'Trindade - GO')}</div>
          <p class="address">${escapeHtml(item.endereco)}</p>
          <div class="contact-list">${contactLines}</div>
          <div class="card-actions">${actions.join('')}</div>
        </article>`;
      };

      const applyFilters = () => {
        const q = normalize(search.value);
        const type = typeFilter.value;
        const neighborhood = neighborhoodFilter.value;
        state.filtered = state.all.filter(item => {
          const haystack = normalize([item.nome,item.tipo,item.bairro,item.endereco].join(' '));
          return (!q || haystack.includes(q))
            && (!type || item.tipo === type)
            && (!neighborhood || item.bairro === neighborhood);
        });
        const results = $('#results');
        results.innerHTML = state.filtered.length
          ? state.filtered.map(renderCard).join('')
          : '<div class="empty-state"><strong>Nenhuma hospedagem encontrada.</strong><br>Altere os filtros ou tente outro termo de busca.</div>';
        results.setAttribute('aria-busy','false');
        $('#result-count').textContent = `${state.filtered.length} ${state.filtered.length === 1 ? 'hospedagem encontrada' : 'hospedagens encontradas'}`;
        clearFilters.hidden = !(q || type || neighborhood);
      };

      const load = async () => {
        try {
          const response = await fetch('./hospedagens.json', { cache:'no-cache' });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const data = await response.json();
          state.all = (data.estabelecimentos || []).slice().sort((a,b) => a.nome.localeCompare(b.nome,'pt-BR'));
          $('#stat-total').textContent = data.total_confirmados ?? state.all.length;
          $('#stat-hotels').textContent = data.hoteis ?? state.all.filter(i => i.tipo === 'Hotel').length;
          $('#stat-pousadas').textContent = data.pousadas ?? state.all.filter(i => i.tipo === 'Pousada').length;
          const neighborhoods = [...new Set(state.all.map(i => i.bairro).filter(Boolean))].sort((a,b) => a.localeCompare(b,'pt-BR'));
          neighborhoodFilter.insertAdjacentHTML('beforeend', neighborhoods.map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join(''));
          applyFilters();
        } catch (error) {
          console.error('Falha ao carregar o diretório de hospedagem.', error);
          $('#results').innerHTML = '<div class="empty-state"><strong>Não foi possível carregar o diretório agora.</strong><br>Tente novamente em instantes.</div>';
          $('#results').setAttribute('aria-busy','false');
          $('#result-count').textContent = 'Diretório temporariamente indisponível';
        }
      };

      search.addEventListener('input', applyFilters);
      typeFilter.addEventListener('change', applyFilters);
      neighborhoodFilter.addEventListener('change', applyFilters);
      clearFilters.addEventListener('click', () => {
        search.value=''; typeFilter.value=''; neighborhoodFilter.value=''; applyFilters(); search.focus();
      });

      load();
    })();
