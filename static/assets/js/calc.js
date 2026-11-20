/* 계산기: 입력이 바뀔 때마다 다시 계산한다 */
(function () {
  function $(id) { return document.getElementById(id); }
  function num(id) { var v = parseFloat($(id).value); return isNaN(v) ? null : v; }
  function fmt(x, d) { return (Math.round(x * Math.pow(10, d)) / Math.pow(10, d)).toLocaleString('ko-KR'); }
  function judge(el, ok, okText, badText) { el.className = ok ? 'ok' : 'bad'; el.textContent = ok ? okText : badText; }

  function led() {
    var v = num('led-v'), vf = num('led-vf'), r = num('led-r');
    if (v === null || vf === null || !r) { $('led-i').textContent = '-'; return; }
    var mA = (v - vf) / r * 1000;
    $('led-i').textContent = fmt(mA, 1);
    judge($('led-judge'), mA > 0 && mA <= 20, '적정(20mA 이하)', mA <= 0 ? '전압을 확인한다' : '전류가 많다 — 저항을 키운다');
  }
  function blink() {
    var t = num('bl-t');
    if (!t) { $('bl-n').textContent = '-'; return; }
    var n = 60000 / (2 * t);
    $('bl-n').textContent = fmt(n, 1);
    judge($('bl-judge'), n >= 60 && n <= 120, '기준 만족', '기준 벗어남');
  }

  ['led-v', 'led-vf', 'led-r'].forEach(function (id) { $(id).addEventListener('input', led); });
  $('bl-t').addEventListener('input', blink);
  led(); blink();
})();
