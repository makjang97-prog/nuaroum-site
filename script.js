/* NOUAROUM — site behaviour: catalog data, filters, product modal, header, menu */
(() => {
  'use strict';

  /* GATE — 오픈 준비중 게이트가 켜진 일반 방문(page)에서는 카탈로그·애니메이션을 실행하지 않는다 */
  if (document.documentElement.classList.contains('gate-on')) return;

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const state = { products: [], categories: [], filter: 'all', lastFocus: null };

  /* ---------------------------------------------------------------- data */
  async function loadCatalog() {
    try {
      const res = await fetch('products.json', { cache: 'no-cache' });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      state.products = Array.isArray(data.products) ? data.products : [];
      state.categories = Array.isArray(data.categories) ? data.categories : [];
      renderCategories();
      renderFilters();
      renderProducts();
      applyHashCategory();
    } catch (err) {
      console.warn('제품 데이터를 불러오지 못했습니다.', err);
      const grid = $('#products');
      if (grid) grid.textContent = '제품 데이터를 불러오지 못했습니다.';
    }
  }

  const catById = (id) => state.categories.find((c) => c.id === id) || null;
  const productsIn = (id) => state.products.filter((p) => p.category === id);
  const firstImage = (id) => {
    const hit = productsIn(id).find((p) => p.image);
    return hit ? hit.image : null;
  };

  /* --------------------------------------------------------- placeholders */
  function placeholder(code, label, name) {
    const wrap = document.createElement('div');
    wrap.className = 'ph';

    const rings = document.createElement('span');
    rings.className = 'ph__rings';
    rings.setAttribute('aria-hidden', 'true');

    const codeEl = document.createElement('span');
    codeEl.className = 'ph__code';
    codeEl.textContent = code || 'NOUAROUM';

    const labelEl = document.createElement('span');
    labelEl.className = 'ph__label';
    labelEl.textContent = label || 'PHOTO IN PREPARATION';

    wrap.append(rings, codeEl);
    if (name) {
      const nameEl = document.createElement('span');
      nameEl.className = 'ph__name';
      nameEl.textContent = name;
      wrap.append(nameEl);
    }
    wrap.append(labelEl);
    return wrap;
  }

  /* ------------------------------------------------------------ categories */
  function renderCategories() {
    const host = $('#cats');
    if (!host) return;
    host.textContent = '';

    state.categories.forEach((cat) => {
      const items = productsIn(cat.id);
      const img = firstImage(cat.id);

      const a = document.createElement('a');
      a.className = 'cat reveal';
      a.href = '#catalog';
      a.dataset.cat = cat.id;

      const frame = document.createElement('div');
      frame.className = 'cat__frame';
      if (img) {
        const el = document.createElement('img');
        el.src = img;
        el.alt = `${cat.kr} ${cat.en} 컬렉션 대표 이미지`;
        el.loading = 'lazy';
        el.width = 1086;
        el.height = 1448;
        frame.append(el);
      } else {
        frame.append(placeholder(cat.prefix, 'COLLECTION'));
      }

      const hover = document.createElement('span');
      hover.className = 'cat__hover';
      hover.textContent = 'VIEW COLLECTION';
      frame.append(hover);

      const body = document.createElement('div');
      body.className = 'cat__body';

      const range = document.createElement('span');
      range.className = 'cat__range';
      range.textContent = cat.prefix;

      const en = document.createElement('h3');
      en.className = 'cat__en';
      en.textContent = cat.en;

      const kr = document.createElement('span');
      kr.className = 'cat__kr';
      kr.textContent = items.length
        ? `${cat.kr} · ${items.length} ${items.length === 1 ? 'design' : 'designs'}`
        : cat.kr;

      body.append(range, en, kr);
      a.append(frame, body);
      a.addEventListener('click', () => setFilter(cat.id, false));
      host.append(a);
    });

    observeReveal(host);
  }

  /* --------------------------------------------------------------- filters */
  function renderFilters() {
    const host = $('#filters');
    if (!host) return;
    host.textContent = '';

    const make = (id, label) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'chip' + (state.filter === id ? ' is-active' : '');
      b.dataset.filter = id;
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-selected', String(state.filter === id));
      b.textContent = label;
      b.addEventListener('click', () => setFilter(id, true));
      host.append(b);
    };

    make('all', 'ALL');
    state.categories.forEach((c) => make(c.id, c.en));
  }

  function setFilter(id, scroll) {
    state.filter = id;
    $$('#filters .chip').forEach((b) => {
      const on = b.dataset.filter === id;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-selected', String(on));
    });
    renderProducts();
    if (scroll) {
      const target = $('#catalog');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function applyHashCategory() {
    const params = new URLSearchParams(location.search);
    const wanted = params.get('cat');
    if (wanted && state.categories.some((c) => c.id === wanted)) setFilter(wanted, false);
  }

  /* -------------------------------------------------------------- products */
  function renderProducts() {
    const host = $('#products');
    if (!host) return;
    host.textContent = '';

    const list = state.filter === 'all'
      ? state.products
      : state.products.filter((p) => p.category === state.filter);

    if (!list.length) {
      const empty = document.createElement('p');
      empty.className = 'grid-empty';
      empty.textContent = '준비 중인 컬렉션입니다.';
      host.append(empty);
      return;
    }

    list.forEach((p, i) => {
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'card';
      card.dataset.code = p.code;
      card.style.transitionDelay = `${Math.min(i, 6) * 40}ms`;
      card.setAttribute('aria-label', `${p.code} ${p.title} 상세 보기`);

      const frame = document.createElement('div');
      frame.className = 'card__frame';
      if (p.image) {
        const img = document.createElement('img');
        img.src = p.image;
        img.alt = `${p.code} ${p.title} — ${p.metal}, ${p.stone}`;
        img.loading = 'lazy';
        img.width = 1086;
        img.height = 1448;
        frame.append(img);
      } else {
        frame.append(placeholder(p.code, 'PHOTO IN PREPARATION', p.title));
      }

      const view = document.createElement('span');
      view.className = 'card__view';
      view.textContent = 'VIEW DETAIL';
      frame.append(view);

      const body = document.createElement('div');
      body.className = 'card__body';

      const code = document.createElement('span');
      code.className = 'card__code';
      code.textContent = p.code;

      const title = document.createElement('h3');
      title.className = 'card__title';
      title.textContent = p.title;

      const spec = document.createElement('span');
      spec.className = 'card__spec';
      spec.textContent = p.stone && p.stone !== '없음' ? `${p.metal} · ${p.stone}` : p.metal;

      body.append(code, title, spec);
      card.append(frame, body);
      card.addEventListener('click', () => openModal(p, card));
      host.append(card);
    });
  }

  /* ----------------------------------------------------------------- modal */
  const modal = $('#modal');

  function openModal(product, trigger) {
    if (!modal) return;
    state.lastFocus = trigger || document.activeElement;
    const body = $('#modalBody');
    body.textContent = '';

    const media = document.createElement('div');
    media.className = 'modal__media';
    const shots = Array.isArray(product.gallery) && product.gallery.length
      ? product.gallery
      : (product.image ? [product.image] : []);
    if (shots.length) {
      const img = document.createElement('img');
      img.src = shots[0];
      img.alt = `${product.code} ${product.title} 제품 사진`;
      media.append(img);
      if (shots.length > 1) {
        const thumbs = document.createElement('div');
        thumbs.className = 'modal__thumbs';
        shots.forEach((src, idx) => {
          const t = document.createElement('button');
          t.type = 'button';
          t.className = 'thumb' + (idx === 0 ? ' is-active' : '');
          const ti = document.createElement('img');
          ti.src = src;
          ti.alt = `${product.title} 이미지 ${idx + 1}`;
          t.append(ti);
          t.addEventListener('click', () => {
            img.src = src;
            $$('.thumb', thumbs).forEach((x) => x.classList.remove('is-active'));
            t.classList.add('is-active');
          });
          thumbs.append(t);
        });
        media.append(thumbs);
      }
    } else {
      media.append(placeholder(product.code, 'PHOTO IN PREPARATION'));
    }

    const info = document.createElement('div');
    info.className = 'modal__info';

    const code = document.createElement('span');
    code.className = 'modal__code';
    code.textContent = product.code;

    const title = document.createElement('h3');
    title.className = 'modal__title';
    title.id = 'modalTitle';
    title.textContent = product.title;

    const cat = catById(product.category);
    const sub = document.createElement('span');
    sub.className = 'modal__sub';
    sub.textContent = cat ? `${cat.en} · ${cat.kr}` : '';

    const dl = document.createElement('dl');
    dl.className = 'modal__spec';
    [['METAL', product.metal], ['STONE', product.stone || '—'], ['PRICE', '방문 상담 시 안내']]
      .forEach(([k, v]) => {
        const row = document.createElement('div');
        const dt = document.createElement('dt');
        dt.textContent = k;
        const dd = document.createElement('dd');
        dd.textContent = v;
        row.append(dt, dd);
        dl.append(row);
      });

    const desc = document.createElement('p');
    desc.className = 'modal__desc';
    desc.textContent = product.description || '';

    info.append(code, title, sub, dl, desc);

    if (Array.isArray(product.options) && product.options.length) {
      const opts = document.createElement('ul');
      opts.className = 'modal__options';
      product.options.forEach((o) => {
        const li = document.createElement('li');
        li.textContent = o;
        opts.append(li);
      });
      info.append(opts);
    }

    const cta = document.createElement('a');
    cta.className = 'btn btn--solid modal__cta';
    cta.href = '#reservation';
    cta.textContent = '방문 예약 안내';
    cta.addEventListener('click', closeModal);

    const note = document.createElement('p');
    note.className = 'modal__note';
    note.textContent = '제품 코드로 상담·주문·케어 이력이 관리됩니다.';

    info.append(cta, note);
    body.append(media, info);

    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('is-locked');
    $('#modalClose').focus();
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('is-locked');
    if (state.lastFocus && typeof state.lastFocus.focus === 'function') state.lastFocus.focus();
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target.closest('[data-close]')) closeModal();
    });
    $('#modalClose')?.addEventListener('click', closeModal);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('is-open')) closeModal();
    });
  }

  /* ---------------------------------------------------------------- header */
  const hdr = $('#hdr');
  const onScroll = () => {
    if (hdr) hdr.classList.toggle('is-scrolled', window.scrollY > 12);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------------------------------------------------------------- drawer */
  const drawer = $('#drawer');
  const burger = $('#burger');

  function setDrawer(open) {
    if (!drawer || !burger) return;
    drawer.classList.toggle('is-open', open);
    drawer.setAttribute('aria-hidden', String(!open));
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
    document.body.classList.toggle('is-locked', open);
  }

  burger?.addEventListener('click', () => setDrawer(!drawer.classList.contains('is-open')));
  $('#drawerClose')?.addEventListener('click', () => setDrawer(false));
  $$('#drawer a').forEach((a) => a.addEventListener('click', () => setDrawer(false)));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawer?.classList.contains('is-open')) setDrawer(false);
  });

  /* ---------------------------------------------------------------- reveal */
  let observer = null;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function observeReveal(root = document) {
    const nodes = $$('.reveal', root);
    if (reduced || !('IntersectionObserver' in window)) {
      nodes.forEach((n) => n.classList.add('is-in'));
      return;
    }
    if (!observer) {
      observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-in');
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    }
    nodes.forEach((n) => observer.observe(n));
  }

  observeReveal();
  loadCatalog();
})();
