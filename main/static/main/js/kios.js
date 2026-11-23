/* Kios (POS): scanner barcode USB (Qoltec) = keyboard wedge -> kódigu + Enter. Tudu offline. */
(function () {
  var root = document.getElementById('pos');
  if (!root) return;
  var urls = { scan: root.dataset.scan, cari: root.dataset.cari, checkout: root.dataset.checkout };
  var csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
  var $ = function (id) { return document.getElementById(id); };
  var scan = $('scan'), cari = $('cari'), results = $('cari-results'), body = $('cart-body');
  var discount = $('discount'), paid = $('paid'), payBtn = $('pay'), autoprint = $('autoprint');
  var cart = [];
  try { cart = JSON.parse(sessionStorage.getItem('kios_cart') || '[]'); } catch (e) { cart = []; }
  try { autoprint.checked = localStorage.getItem('kios_autoprint') !== '0'; } catch (e) {}

  function cents(v) { var n = parseFloat(String(v || '').replace(',', '.')); return isNaN(n) ? 0 : Math.round(n * 100); }
  function fmt(c) { return '$ ' + (c / 100).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }

  var audio;
  function beep(ok) {
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      var o = audio.createOscillator(), g = audio.createGain();
      o.type = 'square'; o.frequency.value = ok ? 1500 : 320;
      g.gain.value = 0.05; o.connect(g); g.connect(audio.destination);
      o.start(); o.stop(audio.currentTime + (ok ? 0.08 : 0.3));
    } catch (e) {}
  }
  function toast(msg, type) {
    var box = $('toast');
    box.innerHTML = '<div class="alert alert-' + (type || 'danger') + ' py-2 mb-2 shadow">' + esc(msg) + '</div>';
    clearTimeout(toast.t);
    toast.t = setTimeout(function () { box.innerHTML = ''; }, 3500);
  }

  function save() { try { sessionStorage.setItem('kios_cart', JSON.stringify(cart)); } catch (e) {} }

  function add(p) {
    if (p.stock <= 0) { beep(false); return toast('Stock "' + p.name + '" mamuk.'); }
    var item = cart.filter(function (c) { return c.id === p.id; })[0];
    if (item) {
      if (item.qty + 1 > p.stock) { beep(false); return toast('Stock "' + p.name + '" la to\'o (iha ' + p.stock + ').'); }
      item.qty += 1; item.stock = p.stock;
    } else {
      cart.push({ id: p.id, code: p.code, name: p.name, price: cents(p.price), stock: p.stock, qty: 1 });
    }
    beep(true); render();
  }

  function subtotal() { return cart.reduce(function (s, c) { return s + c.price * c.qty; }, 0); }

  function render() {
    body.innerHTML = '';
    cart.forEach(function (c, i) {
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td><div class="font-weight-bold">' + esc(c.name) + '</div><small class="text-muted">' + esc(c.code) + ' · stock ' + c.stock + '</small>' +
        '<small class="d-sm-none text-maroon font-weight-bold"> · ' + fmt(c.price) + '</small></td>' +
        '<td class="text-right text-nowrap d-none d-sm-table-cell">' + fmt(c.price) + '</td>' +
        '<td class="text-center text-nowrap"><div class="input-group input-group-sm qty-group">' +
        '<div class="input-group-prepend"><button type="button" class="btn btn-outline-secondary" data-act="dec" data-i="' + i + '">&minus;</button></div>' +
        '<input type="number" min="1" class="form-control text-center" value="' + c.qty + '" data-act="qty" data-i="' + i + '">' +
        '<div class="input-group-append"><button type="button" class="btn btn-outline-secondary" data-act="inc" data-i="' + i + '">+</button></div></div></td>' +
        '<td class="text-right text-nowrap font-weight-bold">' + fmt(c.price * c.qty) + '</td>' +
        '<td class="text-right"><button type="button" class="btn btn-sm btn-outline-danger" data-act="del" data-i="' + i + '"><i class="fa fa-times"></i></button></td>';
      body.appendChild(tr);
    });
    $('cart-empty').style.display = cart.length ? 'none' : 'block';
    save(); recalc();
  }

  function recalc() {
    var sub = subtotal();
    var disc = Math.min(Math.max(cents(discount.value), 0), sub);
    var total = sub - disc;
    var pay = cents(paid.value);
    var change = pay - total;
    $('subtotal').textContent = fmt(sub);
    $('total').textContent = fmt(total);
    $('n-items').textContent = cart.reduce(function (s, c) { return s + c.qty; }, 0);
    var chg = $('change');
    if (!cart.length) { chg.textContent = fmt(0); chg.className = 'pos-change'; }
    else if (change >= 0) { chg.textContent = fmt(change); chg.className = 'pos-change ok'; }
    else { chg.textContent = 'Kuran ' + fmt(-change); chg.className = 'pos-change bad'; }
    payBtn.disabled = !(cart.length && pay >= total);
    return { sub: sub, disc: disc, total: total, pay: pay };
  }

  body.addEventListener('click', function (e) {
    var b = e.target.closest('[data-act]'); if (!b) return;
    var i = +b.dataset.i, c = cart[i], act = b.dataset.act;
    if (act === 'del') cart.splice(i, 1);
    else if (act === 'inc') { if (c.qty + 1 > c.stock) { beep(false); toast('Stock la to\'o (iha ' + c.stock + ').'); } else c.qty++; }
    else if (act === 'dec') { c.qty--; if (c.qty <= 0) cart.splice(i, 1); }
    render(); scan.focus();
  });
  body.addEventListener('change', function (e) {
    if (e.target.dataset.act !== 'qty') return;
    var c = cart[+e.target.dataset.i], q = parseInt(e.target.value, 10);
    if (isNaN(q) || q <= 0) q = 1;
    if (q > c.stock) { q = c.stock; beep(false); toast('Stock la to\'o (iha ' + c.stock + ').'); }
    c.qty = q; render(); scan.focus();
  });

  // ---- scanner: Enter = remata scan
  scan.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    e.preventDefault();
    var code = scan.value.trim(); scan.value = '';
    if (!code) return;
    fetch(urls.scan + '?q=' + encodeURIComponent(code), { credentials: 'same-origin' })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (r) { if (r.ok) add(r.d); else { beep(false); toast(r.d.error); } })
      .catch(function () { beep(false); toast('Erru konexaun ba servidór.'); });
  });

  // ---- buka tuir naran
  var timer;
  cari.addEventListener('input', function () {
    clearTimeout(timer);
    var q = cari.value.trim();
    if (q.length < 2) { results.innerHTML = ''; return; }
    timer = setTimeout(function () {
      fetch(urls.cari + '?q=' + encodeURIComponent(q), { credentials: 'same-origin' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          results.innerHTML = '';
          d.results.forEach(function (p) {
            var a = document.createElement('a');
            a.href = '#'; a.className = 'list-group-item list-group-item-action py-2 d-flex justify-content-between';
            a.innerHTML = '<span>' + esc(p.name) + '<br><small class="text-muted">' + esc(p.code) + ' · stock ' + p.stock + '</small></span><strong class="text-nowrap">' + fmt(cents(p.price)) + '</strong>';
            a.addEventListener('click', function (ev) { ev.preventDefault(); add(p); results.innerHTML = ''; cari.value = ''; scan.focus(); });
            results.appendChild(a);
          });
          if (!d.results.length) results.innerHTML = '<div class="list-group-item text-muted py-2">La hetan.</div>';
        });
    }, 250);
  });

  [discount, paid].forEach(function (el) { el.addEventListener('input', recalc); });

  document.querySelectorAll('[data-amt]').forEach(function (b) {
    b.addEventListener('click', function () {
      var amt = b.dataset.amt;
      paid.value = amt === 'pas' ? (recalc().total / 100).toFixed(2) : parseFloat(amt).toFixed(2);
      recalc(); scan.focus();
    });
  });
  $('clear-cart').addEventListener('click', function () {
    if (cart.length && !confirm('Hamoos karrinhu hotu?')) return;
    cart = []; discount.value = ''; paid.value = ''; render(); scan.focus();
  });
  autoprint.addEventListener('change', function () { try { localStorage.setItem('kios_autoprint', autoprint.checked ? '1' : '0'); } catch (e) {} });

  // ---- selu
  function pay() {
    var t = recalc();
    if (payBtn.disabled) return;
    payBtn.disabled = true; payBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Prosesu...';
    var fd = new FormData();
    fd.append('csrfmiddlewaretoken', csrf);
    fd.append('cart', JSON.stringify(cart.map(function (c) { return { pesa: c.id, qty: c.qty }; })));
    fd.append('discount', (t.disc / 100).toFixed(2));
    fd.append('paid', (t.pay / 100).toFixed(2));
    fd.append('kliente', $('kliente').value);
    fd.append('note', $('note').value);
    fetch(urls.checkout, { method: 'POST', body: fd, credentials: 'same-origin' })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (r) {
        if (r.ok) {
          beep(true);
          try { sessionStorage.removeItem('kios_cart'); } catch (e) {}
          window.location.href = autoprint.checked ? r.d.struk_url : r.d.detail_url;
        } else {
          beep(false); toast(r.d.error); payBtn.innerHTML = '<i class="fa fa-check"></i> Selu &amp; Print'; recalc();
        }
      })
      .catch(function () { toast('Erru konexaun ba servidór.'); payBtn.innerHTML = '<i class="fa fa-check"></i> Selu &amp; Print'; recalc(); });
  }
  payBtn.addEventListener('click', pay);

  // ---- fokus: scanner tenke sempre hatama iha kampu scan
  document.addEventListener('click', function (e) {
    if (!e.target.closest('input,select,textarea,button,a,label')) scan.focus();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'F2') { e.preventDefault(); scan.focus(); }
    if (e.key === 'F9') { e.preventDefault(); pay(); }
  });
  scan.addEventListener('focus', function () { $('scan-status').className = 'badge badge-success'; $('scan-status').textContent = 'Scanner prontu'; });
  scan.addEventListener('blur', function () { $('scan-status').className = 'badge badge-secondary'; $('scan-status').textContent = 'Klik iha kampu scan (F2)'; });

  render(); scan.focus();
})();
