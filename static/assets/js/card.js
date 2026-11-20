/* 요구사항 카드 작성기: 항목 → AI에 붙여 넣을 문장, 입력은 브라우저에 저장 */
(function () {
  var KEY = 'card-v1';
  var LABEL = { goal: '목표', input: '입력', output: '출력', rule: '동작 규칙', cond: '조건', check: '확인 방법' };
  var EXAMPLE = {
    goal: '왼쪽 방향지시등이 일정한 주기로 점멸한다.',
    input: '없음(코드의 변수로 점등 여부를 지정한다.)',
    output: 'D7: 왼쪽 방향지시등, D8: 오른쪽 방향지시등',
    rule: 'leftOn이 true이면 D7이 400ms 점등, 400ms 소등을 반복한다. rightOn도 같은 방식으로 D8을 제어한다. 둘 다 true이면 비상등과 같이 동시에 점멸한다.',
    cond: 'Arduino Uno, C++. 핀 번호는 코드 맨 위의 상수로 선언한다. 시간은 millis()로 처리한다. 각 줄에 한국어 주석을 단다.',
    check: '10초 동안의 점멸 횟수를 세어 1분당 횟수로 환산하고, 60~120회 범위에 드는지 확인한다.'
  };
  var fields = Array.prototype.slice.call(document.querySelectorAll('[data-k]'));
  var out = document.getElementById('card-out');
  var plan = document.getElementById('plan-first');

  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  function save(d) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) {} }

  function render() {
    var d = {}, lines = ['다음 요구사항 카드대로 아두이노 코드를 만들어 줘.', ''];
    fields.forEach(function (f) {
      d[f.dataset.k] = f.value;
      if (f.value.trim()) lines.push('[' + LABEL[f.dataset.k] + '] ' + f.value.trim());
    });
    if (plan.checked) lines.push('', '코드를 쓰기 전에 구현 계획부터 설명해 줘. 내가 확인한 뒤에 코드를 만들어 줘.');
    out.value = lines.join('\n');
    save(d);
  }
  function fill(d) { fields.forEach(function (f) { f.value = d[f.dataset.k] || ''; }); render(); }

  fields.forEach(function (f) { f.addEventListener('input', render); });
  plan.addEventListener('change', render);
  document.querySelectorAll('[data-preset]').forEach(function (b) {
    b.addEventListener('click', function () { fill(b.dataset.preset === 'example' ? EXAMPLE : {}); });
  });
  document.getElementById('copy-card').addEventListener('click', function () { copyText(out.value); });
  fill(load());
})();
