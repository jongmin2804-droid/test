/* 공통 동작: 차례 열기, 크게 보기, 키보드 이동, 코드 복사·색칠, 그림 확대 */
(function () {
  var root = document.documentElement;
  function store(k, v) { try { return v === undefined ? localStorage.getItem(k) : localStorage.setItem(k, v); } catch (e) { return null; } }

  /* 알림과 복사 (도구 페이지에서도 쓴다) */
  var toastEl;
  window.showToast = function (msg) {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'toast'; toastEl.setAttribute('role', 'status'); document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastEl._t); toastEl._t = setTimeout(function () { toastEl.classList.remove('show'); }, 1600);
  };
  window.copyText = function (text) {
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); showToast('복사했다'); } catch (e) { showToast('복사하지 못했다. 직접 선택해 복사한다.'); }
      ta.remove();
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(function () { showToast('복사했다'); }, fallback);
    else fallback();
  };

  /* 차례 열기(휴대폰) */
  var menuBtn = document.querySelector('.menu-btn'), scrim = document.querySelector('.scrim');
  function setNav(open) {
    document.body.classList.toggle('nav-open', open);
    if (menuBtn) menuBtn.setAttribute('aria-expanded', String(open));
    if (scrim) scrim.hidden = !open;
  }
  if (menuBtn) menuBtn.addEventListener('click', function () { setNav(!document.body.classList.contains('nav-open')); });
  if (scrim) scrim.addEventListener('click', function () { setNav(false); });
  document.querySelectorAll('.sidebar a').forEach(function (a) { a.addEventListener('click', function () { setNav(false); }); });

  /* 크게 보기 */
  var pBtn = document.querySelector('.present-btn');
  function syncPresent() {
    var on = root.classList.contains('present');
    if (pBtn) { pBtn.setAttribute('aria-pressed', String(on)); pBtn.textContent = on ? '보통 크기' : '크게 보기'; }
    window.dispatchEvent(new Event('resize'));
  }
  function togglePresent() { root.classList.toggle('present'); store('present', root.classList.contains('present') ? '1' : '0'); syncPresent(); }
  if (pBtn) pBtn.addEventListener('click', togglePresent);
  syncPresent();

  /* 키보드: P 크게 보기, ←/→ 이전·다음 장, Esc 닫기 */
  document.addEventListener('keydown', function (e) {
    var t = e.target;
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (e.key === 'p' || e.key === 'P') togglePresent();
    else if (e.key === 'ArrowRight') { var n = document.querySelector('.pager .next'); if (n) location.href = n.href; }
    else if (e.key === 'ArrowLeft') { var p = document.querySelector('.pager .prev'); if (p) location.href = p.href; }
    else if (e.key === 'Escape') { setNav(false); closeLightbox(); }
  });

  /* 사이드바: 지금 읽는 소제목 표시 */
  var subLinks = Array.prototype.slice.call(document.querySelectorAll('.sub a'));
  if (subLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    subLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          subLinks.forEach(function (a) { a.classList.remove('cur'); });
          map[en.target.id].classList.add('cur');
        }
      });
    }, { rootMargin: '-70px 0px -70% 0px' });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  /* 코드 색칠 (아두이노 C++ 간단 규칙) */
  var KW = 'const|int|unsigned|long|bool|boolean|void|if|else|for|while|return|true|false|HIGH|LOW|INPUT|OUTPUT|INPUT_PULLUP|char|byte|float|static|switch|case|break|default';
  var RE = new RegExp('(\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/)|("(?:[^"\\\\]|\\\\.)*"|\'(?:[^\'\\\\]|\\\\.)*\')|(#include|#define)|\\b(' + KW + ')\\b|\\b(0x[0-9A-Fa-f]+|\\d+(?:\\.\\d+)?)\\b|\\b([A-Za-z_]\\w*)(?=\\s*\\()', 'g');
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  document.querySelectorAll('pre code.lang-cpp').forEach(function (el) {
    var src = el.textContent, out = '', last = 0, m;
    RE.lastIndex = 0;
    while ((m = RE.exec(src))) {
      out += esc(src.slice(last, m.index));
      var cls = m[1] ? 'tok-c' : m[2] ? 'tok-s' : m[3] ? 'tok-p' : m[4] ? 'tok-k' : m[5] ? 'tok-n' : 'tok-f';
      out += '<span class="' + cls + '">' + esc(m[0]) + '</span>';
      last = RE.lastIndex;
    }
    el.innerHTML = out + esc(src.slice(last));
  });
  document.querySelectorAll('[data-copy-target]').forEach(function (b) {
    b.addEventListener('click', function () {
      var code = b.closest('details, .panel').querySelector('pre code');
      if (code) copyText(code.textContent);
    });
  });

  /* 그림 크게 보기 */
  var lb;
  function closeLightbox() { if (lb) { lb.remove(); lb = null; } }
  document.querySelectorAll('.fig-link').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      lb = document.createElement('div');
      lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-label', '그림 크게 보기');
      lb.style.cssText = 'position:fixed;inset:0;z-index:80;background:rgba(10,20,30,.82);display:grid;place-items:center;padding:16px;cursor:zoom-out';
      var img = document.createElement('img'); img.src = a.getAttribute('href'); img.alt = (a.querySelector('img') || {}).alt || '';
      img.style.cssText = 'max-width:96vw;max-height:92vh;background:#fff;border-radius:8px;padding:10px';
      lb.appendChild(img); lb.addEventListener('click', closeLightbox);
      document.body.appendChild(lb);
    });
  });
})();
