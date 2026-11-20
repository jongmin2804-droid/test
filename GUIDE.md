# 전장제어교육 사이트 만들기 — 상세 절차와 가이드

목표 사이트: <https://dreamy-baklava-9d71ab.netlify.app/>

이 문서는 위 사이트를 **가지고 있는 재료(원고, 그림, 예시 코드, 3D 파일)** 로 처음부터 똑같이 만들어 Netlify에 올리는 과정을 순서대로 설명한다. 이 저장소에는 그대로 쓸 수 있는 **스타터 키트**(빌드 스크립트, 디자인, 도구 페이지 견본)가 함께 들어 있다.

---

## 0. 완성 사이트 분석

실제 사이트를 내려받아 구조를 분석한 결과이다.

| 항목 | 내용 |
|---|---|
| 종류 | **정적 사이트**(서버 프로그램 없음). React 같은 프레임워크 없이 HTML + CSS 1개 + JavaScript 4개 |
| 호스팅 | Netlify 무료 플랜. 주소가 `dreamy-baklava-9d71ab`처럼 무작위인 것은 **Netlify Drop(폴더 끌어다 놓기)** 으로 올렸다는 뜻 |
| 페이지 | 첫 화면 1 + 본문 13장 + 부록 A 1 + 도구 4 = **19쪽** |
| 주소 | `/ch01`, `/card` 처럼 `.html`이 없다. Netlify가 `ch01.html`을 `/ch01`로 자동 연결해 준다 |
| 만든 방식 | 모든 쪽의 머리 막대·차례가 똑같고, 표의 열 너비가 `18.2%`처럼 계산되어 있다 → **원고를 스크립트로 변환해 생성**한 것 |
| 디자인 | 남색 `#1F4E78`, 표 머리 `#DCE6F1`, 실습 강조 빨강 `#C0504D`, 맑은 고딕 계열 글꼴 |
| 3D | three.js r170을 사이트 안에 두고(`assets/vendor/three`) `minicar_assembly.glb`를 불러온다 |

### 페이지 구성

```
/              첫 화면: 대표 그림 + 차례 카드 14개 + 도구 카드 4개
/ch01 ~ /ch13  본문 장: 장 번호 머리 → 도입글 → [이론] → [실습] → 도구 상자 → [예시 코드] → 이전/다음
/appendix-a    부록 A 표준 핀맵과 배선
/card          요구사항 카드 작성기 (입력 → AI에 붙여 넣을 문장, 브라우저에 저장)
/calc          계산기 (LED 전류, 점멸 주기, 초음파 거리, PWM)
/model         미니카 3D 모델 (회전, 부품 이름, 분해 슬라이더, STL 내려받기)
/app           제어 앱 안내 (설치·연결 순서, 통신 규약 표)
```

### 모든 쪽에 공통인 기능

- 왼쪽 **차례**(휴대폰에서는 ☰ 버튼으로 열고 닫음), 지금 장의 소제목 목록과 현재 위치 표시
- **크게 보기** 버튼(단축키 `P`) — 강의 화면용으로 글자를 키우고 설정을 기억
- 키보드 `←` `→`로 이전/다음 장 이동
- 예시 코드 **색칠**과 **복사** 버튼
- 그림을 누르면 **크게 보기**(라이트박스)
- `표 3-1`, `그림 2-1` 같은 **교차 참조 링크**

---

## 1. 재료 점검

아래 표의 재료가 있는지 먼저 확인한다. 오른쪽 칸이 스타터 키트에서 넣을 자리이다.

| 재료 | 형식 | 넣을 자리 |
|---|---|---|
| 13장 + 부록 A 원고 | 한글(HWP)·Word(DOCX)·텍스트 등 | `src/chapters/ch01.md` … `appendix-a.md` (Markdown으로 변환) |
| 본문 그림 12장 | PNG | `static/assets/img/fig2-1_led_current.png` 처럼 |
| 대표 그림(미니카 렌더링) | PNG/JPG → **WebP** 권장 | `static/assets/img/minicar_render.webp` |
| 예시 코드 C-1, C-2 … | `.ino` | 각 장 원고의 `## 예시 코드` 안 |
| 3D 출력물 4개 | STL | `static/assets/model/tray.stl` 등 |
| 조립 모델 | GLB | `static/assets/model/minicar_assembly.glb` |
| three.js r170 | JS | `static/assets/vendor/three/` (7-3 참고) |
| 제어 앱 | APK (준비되면) | `static/assets/app/minicar.apk` |

> 그림 파일 이름은 영문·숫자·`-`·`_`만 쓴다. 한글·띄어쓰기가 있으면 일부 환경에서 깨진다.

---

## 2. 작업 환경 준비 (Windows 기준)

1. **Python 3.11 이상** — <https://www.python.org/downloads/> 에서 설치. 설치 첫 화면의 **“Add python.exe to PATH”** 를 반드시 체크한다.
2. **VS Code** — <https://code.visualstudio.com/> (원고·설정 파일 편집용)
3. **Git** (선택) — <https://git-scm.com/> GitHub와 연결해 자동 배포하려면 필요
4. **Pandoc** (원고가 HWP/DOCX일 때) — <https://pandoc.org/installing.html>

설치 확인 (PowerShell 또는 VS Code 터미널):

```powershell
python --version      # Python 3.11.x 이상
pandoc --version      # 원고 변환을 할 때만
```

이 저장소를 내려받고 의존성을 설치한다.

```powershell
git clone https://github.com/jongmin2804-droid/test.git jeonjang-site
cd jeonjang-site
git checkout ccr-95371e69-t5nea8      # 스타터 키트가 있는 가지
pip install -r requirements.txt
```

---

## 3. 폴더 구조

```
jeonjang-site/
├─ build.py               ← 빌드 스크립트 (원고 → HTML). 거의 손댈 일 없음
├─ requirements.txt       ← markdown 패키지
├─ netlify.toml           ← Git 연동 배포 설정
├─ src/
│  ├─ site.json           ← 사이트 제목, 장 목록, 도구 목록 (★ 여기서 차례를 관리)
│  ├─ chapters/           ← 장 원고 (Markdown)  ch01.md … appendix-a.md
│  └─ pages/              ← 도구 페이지 본문 (HTML 조각) card / calc / model / app
├─ static/                ← 그대로 복사되는 파일
│  └─ assets/
│     ├─ css/style.css    ← 디자인 전체
│     ├─ js/site.js       ← 공통 동작 (차례, 크게 보기, 복사, 그림 확대 …)
│     ├─ js/card.js, calc.js, model.js   ← 도구별 동작
│     ├─ img/             ← 그림
│     ├─ model/           ← STL, GLB
│     └─ vendor/three/    ← three.js
└─ dist/                  ← 빌드 결과 (★ 이 폴더를 Netlify에 올린다. 직접 수정하지 않음)
```

원리는 단순하다. `build.py`가 `site.json`의 순서대로 원고를 읽어 **공통 틀(머리 막대 + 차례 + 본문 + 이전/다음)** 에 끼운 HTML을 `dist/`에 쓰고, `static/`의 파일을 그대로 복사한다.

---

## 4. 원고를 Markdown으로 옮기기

### 4-1. 자동 변환으로 초안 만들기

원고가 **Word(DOCX)** 이면:

```powershell
pandoc "3장 AI 코딩과 방향지시등.docx" -t gfm --wrap=none -o src/chapters/ch03.md
```

원고가 **한글(HWP)** 이면 한글 프로그램에서 `다른 이름으로 저장 → Word 문서(*.docx)`로 저장한 뒤 위 명령을 쓴다.

> 변환 결과는 초안이다. 아래 4-2의 작성 규칙에 맞게 다듬어야 표 번호·그림·예시 코드가 사이트 형식으로 나온다. 이 다듬기는 AI(Claude, Gemini 등)에 “아래 GUIDE.md 4-2 규칙에 맞게 바꿔 줘”라고 원고와 함께 맡기면 빠르다.

### 4-2. 원고 작성 규칙

견본: `src/chapters/ch03.md` (표·예시 코드), `src/chapters/ch02.md` (그림)

````markdown
---
lead: 장 맨 앞의 도입글. 한 문단으로 쓴다.
tools: card=요구사항 카드 작성기, calc#blink=점멸 주기 계산기
---

## 이론

### 소제목 (자동으로 s1, s2 … 번호가 붙고 왼쪽 차례에 나온다)

본문 문단. 표는 [[표 3-1]], 그림은 [[그림 2-1]] 처럼 참조한다.
다른 장의 표는 [[표 9-1@ch09]], 부록은 [[부록 A]], 다른 장은 [[7장]].

[표 3-1] 표 제목 {first-col widths=18,44,37}
| 단계 | 하는 일 | 확인할 점 |
|---|---|---|
| 요구사항 | … | … |

!fig 2-1 | fig2-1_led_current.png | 그림 제목 | 79%

## 실습

### 회로 구성
…

## 예시 코드

```cpp C1.ino | C-1 방향지시등·비상등
const int LEFT_LAMP = 7;
…
```
````

| 쓰는 법 | 결과 |
|---|---|
| 맨 위 `---` 사이 `lead:` | 장 머리 아래 남색 줄 상자의 도입글 |
| 맨 위 `tools:` | 실습 끝에 나오는 ‘도구’ 상자. `주소=이름`을 쉼표로 구분 |
| `## 이론` / `## 실습` | 남색 / 빨강 띠 제목, 위쪽 ‘이론·실습’ 바로가기 단추 |
| `## 예시 코드` | 회색 띠 제목 + 접히는 코드 상자 |
| `### 제목` | 소제목. 첫 화면 차례 카드의 요약은 **실습의 소제목**을 ` · `로 이어 자동으로 만든다 |
| `[표 3-1] 제목 {옵션}` 바로 다음 줄부터 표 | 번호·제목이 달린 교재식 표 (`id="tbl-3-1"`) |
| 옵션 `first-col` | 첫 열을 굵은 행 머리로 |
| 옵션 `widths=18,44,37` | 열 너비 비율 (합이 100이 아니어도 자동 환산) |
| 표 구분줄 `|:---:|` | 그 열 가운데 정렬 |
| `!fig 번호 \| 파일 \| 제목 \| 폭` | 번호·제목이 달린 그림, 누르면 확대 (`id="fig-2-1"`). 폭 생략 시 100% |
| ```` ```cpp 파일이름 \| 제목 ```` | 예시 코드 상자 (파일 이름 표시, 복사 버튼, 색칠) |
| `` `millis()` `` | 본문 속 코드 글씨 |
| `1.` `2.` / `-` | 번호 목록 / 점 목록 |

### 4-3. 장 목록 관리

`src/site.json`의 `chapters` 배열 순서가 곧 차례·이전/다음 순서이다. 장을 더하거나 이름을 바꾸면 여기만 고친다.

```json
{ "slug": "ch03", "no": "3", "title": "AI 코딩과 방향지시등", "file": "ch03.md" }
```

- `slug` — 주소 (`/ch03`)
- `no` — 숫자이면 “3장”, 글자(`A`)이면 “부록 A”로 표시
- `file` — `src/chapters/` 안의 원고 파일. 아직 없으면 ‘준비 중’ 쪽이 만들어진다

첫 화면 글귀(제목, 부제, 설명, 대표 그림)도 같은 파일 위쪽에서 바꾼다.

---

## 5. 그림 준비

1. **본문 그림**: PNG로 `static/assets/img/`에 둔다. 이름 규칙 `fig<장>-<번호>_<영문설명>.png`
   - 가로 1200~1600px 정도면 충분하다. 파일이 300KB를 넘으면 <https://tinypng.com> 으로 줄인다.
   - 그림마다 원고의 `!fig` 줄 마지막 폭(`79%`)으로 화면에서의 크기를 맞춘다. 교재 쪽 배치 비율을 그대로 쓰면 된다.
2. **대표 그림**: 4:3 비율(1200×900) 권장. <https://squoosh.app> 에서 WebP로 바꿔 `minicar_render.webp`로 저장한다.
3. **파비콘**: `static/assets/img/favicon.svg` (견본이 들어 있음, 바꿔도 된다)

빌드할 때 원고에 적었는데 파일이 없는 그림은 `[확인] 그림 파일 없음`으로 알려 준다.

---

## 6. 빌드와 미리보기

```powershell
python build.py serve
```

- `dist/`에 19쪽이 만들어지고, 브라우저에서 <http://localhost:8000> 을 열면 실제 사이트와 똑같이 볼 수 있다(`/ch03` 주소도 그대로 동작).
- 원고를 고친 뒤에는 `Ctrl+C`로 끄고 다시 실행한다.
- 출력 끝의 `[확인]` 줄은 빠진 원고·그림 목록이다. 이 목록이 없어지면 재료가 모두 들어간 것이다.

> `dist/index.html`을 더블클릭해서 열면 링크와 3D 보기가 동작하지 않는다(주소가 `/`로 시작하기 때문). 반드시 `serve`로 본다.

---

## 7. 도구 페이지

도구 페이지는 `src/pages/*.html`(본문 조각)과 `static/assets/js/*.js`(동작) 한 쌍이다. 머리 막대와 차례는 빌드가 자동으로 씌운다. 쓸 스크립트는 `site.json`의 `tools[].scripts`에 적는다. 본문 조각 안에서도 `[[표 9-1@ch09]]` 참조를 쓸 수 있다.

### 7-1. 요구사항 카드 작성기 (`card`)

- 여섯 칸(목표, 입력, 출력, 동작 규칙, 조건, 확인 방법) → 아래 상자에 AI용 문장 생성 → ‘문장 복사’
- 입력은 `localStorage`에 저장되어 새로고침해도 남는다.
- 원본 사이트에는 **‘AI에 다시 질문하기’ 탭**과 **‘기본 조건 넣기’ 버튼**, 부록 A 핀맵 접기 상자가 더 있다. 견본 `card.js`의 `render()`와 같은 방식(칸 → 문장)으로 탭을 하나 더 만들면 된다. 다시 질문하기 탭의 칸 예: “어떤 상황에서 / 기대한 동작 / 실제 동작 / 의심 가는 부분”.

### 7-2. 계산기 (`calc`)

견본에는 LED 전류와 점멸 주기가 있다. 같은 모양(`panel` 상자 + 입력 + 결과)으로 두 개를 더한다.

| 계산기 | 식 | 판정 |
|---|---|---|
| LED 전류 (2장) | I = (V − Vf) ÷ R | 20mA 이하 |
| 점멸 주기 (3장) | 1분당 횟수 = 60,000 ÷ 2T | 60~120회 |
| 초음파 거리 (5장) | 거리(cm) = 왕복시간(µs) × 음속 ÷ 2 ÷ 10,000, 음속 = 343 + 0.6 × (온도 − 20) m/s | 경보 단계 표시 |
| PWM (6장) | 듀티(%) = 값 ÷ 255 × 100, 평균 전압 = 전원 × 듀티 | — |

각 `section`에 `id="led"`, `id="blink"`, `id="ultra"`, `id="pwm"`을 붙여 두면 본문에서 `calc#blink`처럼 바로 그 계산기로 보낼 수 있다.

### 7-3. 미니카 3D 모델 (`model`)

1. **three.js 받기** — 아래 4개 파일을 같은 이름·구조로 `static/assets/vendor/three/`에 저장한다(브라우저로 열어 `Ctrl+S`).
   - <https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js> → `three.module.min.js`
   - <https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/controls/OrbitControls.js> → `addons/controls/OrbitControls.js`
   - <https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/loaders/GLTFLoader.js> → `addons/loaders/GLTFLoader.js`
   - <https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/utils/BufferGeometryUtils.js> → `addons/utils/BufferGeometryUtils.js`
   
   (사이트 안에 두는 이유: 강의실 인터넷이 막혀도, CDN이 바뀌어도 그대로 동작한다.)
2. **GLB 준비** — `minicar_assembly.glb`의 부품 이름을 `model.js`의 `PARTS` 키와 맞춘다: `tray`, `dashboard`, `rear_pod`, `front_pod`, `plate_E26_est`, `wheel_L`/`wheel_R`, `tt_motor_L`/`_R`, `caster`, `standoff_0~3`, `battery_18650_2S`, `power_block`, `uno_r3`, `l298n`, `breadboard_400`, `relay_1ch`, `hc06`, `lcd_1602`, `hc_sr04`. (`_L`, `_R`, `_숫자`는 자동으로 같은 부품으로 묶인다.)
   - 단위는 m, 좌표는 CAD식 **X 앞 · Y 왼쪽 · Z 위**. Blender에서 `+Y Up`으로 내보냈다면 `model.js` 맨 위 `MODEL_Z_UP`을 `false`로.
   - 분해 방향은 `EXPLODE` 표(mm)에서 고친다.
3. **STL 4개**는 `static/assets/model/`에 두면 내려받기 단추가 바로 동작한다.
4. 원본에는 시점 단추(기본/위/앞/옆), ‘모두 보기’, 부품 목록(그룹별 체크) UI가 더 있다. 견본에 `camera.position.set(...)`을 부르는 단추를 더하는 식으로 넓히면 된다.

### 7-4. 제어 앱 (`app`)

설치·연결 순서와 통신 규약 표(K/k, 1/2/3, `<`/`>`, H, `.`)가 들어 있다. APK가 준비되면 `static/assets/app/minicar.apk`에 두고 `src/pages/app.html`의 주석대로 단추를 바꾼다.

---

## 8. 디자인 바꾸기

`static/assets/css/style.css` 맨 위 `:root`의 변수만 고치면 사이트 전체가 바뀐다.

| 변수 | 뜻 | 기본값 |
|---|---|---|
| `--navy` | 주 색(머리 막대, 이론, 표 번호) | `#1F4E78` |
| `--head` | 표 머리 바탕 | `#DCE6F1` |
| `--accent` | 실습 강조 | `#C0504D` |
| `--fs` | 기본 글자 크기 | `17px` (크게 보기 `22px`) |
| `--content` | 본문 최대 폭 | `820px` |
| `--side` | 차례 폭 | `270px` |

인쇄(`Ctrl+P`)하면 차례·막대가 빠지고 본문만 나온다.

---

## 9. Netlify에 올리기

### 방법 A. 끌어다 놓기 (원본 사이트와 같은 방식, 가장 쉬움)

1. `python build.py` 로 `dist/`를 만든다.
2. <https://app.netlify.com/drop> 에 접속해 **`dist` 폴더를 통째로** 끌어다 놓는다.
3. 몇 초 뒤 `https://무작위-이름.netlify.app` 주소가 나온다.
4. **반드시 로그인(무료 가입)** 해서 사이트를 계정에 연결한다. 로그인하지 않으면 1시간 뒤 사라진다.
5. **고칠 때**: 다시 빌드한 뒤 Netlify의 사이트 → **Deploys** 탭 아래 “Drag and drop your site output folder here” 영역에 `dist`를 또 끌어다 놓는다. 주소는 그대로 유지된다.

### 방법 B. GitHub 연동 (고칠 때마다 자동 배포)

1. 이 폴더를 GitHub 저장소에 올린다(`git push`).
2. Netlify → **Add new project → Import an existing project → GitHub** → 저장소 선택.
3. 빌드 설정은 `netlify.toml`에서 자동으로 읽는다(빌드 명령 `python build.py`, 공개 폴더 `dist`). 확인만 하고 **Deploy**.
4. 이후에는 원고를 고쳐 `git push`만 하면 1~2분 안에 사이트가 바뀐다.

### 사이트 주소 바꾸기

Netlify의 사이트 → **Project configuration → Change project name** 에서 `jeonjang-edu`처럼 바꾸면 `https://jeonjang-edu.netlify.app`이 된다. 개인 도메인은 **Domain management → Add a domain**.

---

## 10. 올리기 전 점검표

- [ ] `python build.py` 출력에 `[확인]` 줄이 없다 (원고·그림 모두 있음)
- [ ] 첫 화면 차례 카드 14개의 요약 문구가 맞다
- [ ] 각 장: 표·그림 번호가 원고와 같고, `표 3-1` 같은 링크를 누르면 그 자리로 간다
- [ ] 그림을 누르면 크게 보이고, 다시 누르면 닫힌다
- [ ] 예시 코드 ‘복사’ → Arduino IDE에 붙여 넣어 **컴파일이 된다**
- [ ] `P` 키로 크게 보기, `←` `→`로 장 이동
- [ ] 휴대폰(또는 브라우저 F12 → 기기 모드)에서 ☰ 차례가 열리고 가로로 밀리지 않는다
- [ ] `/model`에서 모델이 보이고 분해 슬라이더·부품 이름이 동작한다, STL이 내려받아진다
- [ ] `/card`에서 예시 불러오기 → 문장 복사가 된다
- [ ] 없는 주소(`/abc`)에서 ‘페이지를 찾을 수 없다’가 나온다

---

## 11. 자주 겪는 문제

| 증상 | 원인과 해결 |
|---|---|
| `python`을 찾을 수 없다 | 설치 때 PATH 체크를 안 함 → 다시 설치하며 체크, 또는 `py build.py` |
| `markdown 패키지가 없다` | `pip install -r requirements.txt` |
| 표가 표로 안 나오고 `|`가 그대로 보인다 | 표 바로 위에 빈 줄이 없거나, 두 번째 줄(`|---|`)이 빠짐. `[표 …]` 줄 다음 줄부터 바로 표를 쓴다 |
| 그림이 안 나온다 | 파일 이름 대소문자·확장자 확인(`.PNG` ≠ `.png`). Netlify는 대소문자를 구분한다 |
| 3D 모델이 “불러오지 못했다” | `assets/model/minicar_assembly.glb` 위치 확인, three.js 4개 파일 경로 확인(F12 → Console) |
| 3D 모델이 서 있다/뒤집혀 있다 | `model.js`의 `MODEL_Z_UP` 값을 바꾼다 |
| 고쳤는데 사이트가 그대로다 | 브라우저 캐시 → `Ctrl+F5`. 방법 A라면 `dist`를 다시 빌드해서 올렸는지 확인 |
| 복사 버튼이 안 된다 | `http://`가 아닌 `https://`(Netlify)나 `localhost`에서만 클립보드가 허용된다 |

---

## 12. 작업 순서 요약

1. Python·Pandoc 설치 → 저장소 받기 → `pip install -r requirements.txt`
2. `src/site.json`에서 제목·장 목록 확인
3. 원고 DOCX → `pandoc`으로 `src/chapters/chNN.md` 초안 → 4-2 규칙대로 다듬기 (AI에 맡겨도 됨)
4. 그림 → `static/assets/img/`, STL·GLB → `static/assets/model/`, three.js → `static/assets/vendor/three/`
5. `python build.py serve`로 확인하며 `[확인]` 목록이 없어질 때까지 채우기
6. 도구 페이지 보강(카드 다시 질문하기 탭, 계산기 2개, 3D 시점 단추)
7. 10번 점검표 확인
8. `dist`를 Netlify Drop에 끌어다 놓기(또는 GitHub 연동) → 사이트 이름 바꾸기
