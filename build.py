#!/usr/bin/env python3
"""교재 사이트 빌드 스크립트.

src/ 의 원고(Markdown)와 도구 페이지(HTML 조각), static/ 의 에셋을 모아
dist/ 에 완성된 정적 사이트를 만든다. dist/ 폴더를 Netlify에 올리면 끝.

사용법
    python build.py          # dist/ 생성
    python build.py serve    # 생성 후 http://localhost:8000 에서 미리보기
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("markdown 패키지가 없다. 먼저  pip install -r requirements.txt  를 실행한다.")

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

SITE = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
WARN = []


def warn(msg):
    WARN.append(msg)


def esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- 원고 읽기
def read_front_matter(text):
    """--- 로 감싼 머리말(key: value)을 읽는다."""
    meta = {}
    if text.startswith("---"):
        _, head, text = text.split("---", 2)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, text.lstrip("\n")


REF_KIND = {"표": "tbl", "그림": "fig"}


def ref_link(m):
    """[[표 3-1]] [[그림 2-1]] [[표 9-1@ch09]] [[부록 A]] [[9장]] 을 링크로 바꾼다."""
    label, _, page = m.group(1).partition("@")
    label = label.strip()
    page = page.strip()
    km = re.match(r"(표|그림)\s*([\w-]+)$", label)
    if km:
        anchor = f"#{REF_KIND[km.group(1)]}-{km.group(2)}"
        href = f"/{page}{anchor}" if page else anchor
    elif label.startswith("부록"):
        href = "/appendix-" + label.split()[-1].lower()
    elif re.match(r"\d+장$", label):
        href = f"/ch{int(label[:-1]):02d}"
    else:
        href = "/" + page if page else "#"
    return f'<a class="ref" href="{href}">{esc(label)}</a>'


class Stash:
    """Markdown 변환을 거치지 않을 HTML 덩어리를 잠시 맡아 둔다."""

    def __init__(self):
        self.items = []

    def put(self, raw_html):
        self.items.append(raw_html)
        return f"\n\nSTASH{len(self.items) - 1}END\n\n"

    def restore(self, out):
        out = re.sub(r"<p>STASH(\d+)END</p>", lambda m: self.items[int(m.group(1))], out)
        return re.sub(r"STASH(\d+)END", lambda m: self.items[int(m.group(1))], out)


def figure_html(line, img_dir):
    # !fig 2-1 | fig2-1_led_current.png | LED 회로와 전류 계산 | 79%
    parts = [p.strip() for p in line[4:].split("|")]
    num, src, cap = parts[0], parts[1], parts[2]
    width = parts[3] if len(parts) > 3 else "100%"
    if not (STATIC / "assets" / "img" / src).exists():
        warn(f"그림 파일 없음: static/assets/img/{src}")
    path = f"assets/img/{src}"
    return (
        f'<figure class="book-fig" id="fig-{esc(num)}">'
        f'<a href="{path}" class="fig-link" title="크게 보기">'
        f'<img src="{path}" alt="그림 {esc(num)} {esc(cap)}" loading="lazy" style="max-width:{esc(width)}"></a>'
        f'<figcaption><span class="num">그림 {esc(num)}</span> {esc(cap)}</figcaption></figure>'
    )


def code_html(info, code):
    # ```cpp C1.ino | C-1 방향지시등·비상등
    lang, _, rest = info.partition(" ")
    fname, _, title = rest.partition("|")
    fname, title = fname.strip() or "code", title.strip() or fname.strip()
    return (
        f'<details class="code-ex"><summary>{esc(title)}</summary>'
        f'<div class="code-bar"><span>{esc(fname)}</span>'
        f'<button type="button" class="copy-btn" data-copy-target>복사</button></div>'
        f'<pre><code class="lang-{esc(lang or "cpp")}">{esc(code)}</code></pre></details>'
    )


def table_marker(num, cap, opts):
    return f"<!--TBL|{num}|{cap}|{opts}-->"


def wrap_tables(out):
    """<!--TBL--> 표시 바로 뒤의 표를 교재 표 형식(번호·캡션·열 너비)으로 감싼다."""

    def repl(m):
        _, num, cap, opts = m.group(1).split("|", 3)
        table = m.group(2)
        first_col = "first-col" in opts
        widths = re.search(r"widths=([\d.,]+)", opts)
        cls = "book-table first-col" if first_col else "book-table"
        table = table.replace("<table>", f'<table class="{cls}">', 1)
        table = table.replace(' style="text-align: center;"', ' class="c"')
        table = table.replace(' style="text-align: right;"', ' class="r"')
        table = table.replace("<th>", '<th scope="col">').replace("<th class", '<th scope="col" class')
        if first_col:  # 본문 각 행의 첫 칸을 행 머리(th)로
            table = re.sub(
                r"<tr>\s*<td([^>]*)>(.*?)</td>",
                r'<tr><th scope="row"\1>\2</th>',
                table,
                flags=re.S,
            )
            # thead 의 첫 칸은 원래대로 둔다
        if widths:
            ws = [float(w) for w in widths.group(1).split(",")]
            total = sum(ws)
            cols = "".join(f'<col style="width:{w / total * 100:.1f}%">' for w in ws)
            table = table.replace(">", f"><colgroup>{cols}</colgroup>", 1)
        return (
            f'<figure class="table-wrap" id="tbl-{esc(num)}">'
            f'<figcaption class="table-cap"><span class="num">표 {esc(num)}</span> {esc(cap)}</figcaption>'
            f'<div class="table-scroll">{table}</div></figure>'
        )

    return re.sub(r"<!--(TBL\|[^>]*?)-->\s*(<table>.*?</table>)", repl, out, flags=re.S)


def md_to_html(text, stash):
    lines = text.splitlines()
    buf = []
    i = 0
    while i < len(lines):
        line = lines[i]
        fence = re.match(r"^```(.*)$", line)
        if fence:
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            buf.append(stash.put(code_html(fence.group(1).strip(), "\n".join(code))))
        elif line.startswith("!fig "):
            buf.append(stash.put(figure_html(line, None)))
        else:
            tm = re.match(r"^\[표\s+([\w-]+)\]\s*(.*?)\s*(\{(.*)\})?\s*$", line)
            if tm and i + 1 < len(lines) and lines[i + 1].lstrip().startswith("|"):
                buf.append("")
                buf.append(table_marker(tm.group(1), tm.group(2), tm.group(4) or ""))
            else:
                buf.append(re.sub(r"\[\[(.+?)\]\]", ref_link, line))
        i += 1
    out = markdown.markdown("\n".join(buf), extensions=["tables", "sane_lists"])
    out = wrap_tables(out)
    return stash.restore(out)


SECTION_CLASS = {"이론": "part theory", "실습": "part practice"}
SECTION_ID = {"이론": "theory", "실습": "practice", "예시 코드": "examples"}


def build_chapter(ch):
    path = SRC / "chapters" / ch["file"]
    if not path.exists():
        warn(f"원고 없음: src/chapters/{ch['file']} (준비 중 페이지로 만든다)")
        body = (f'<article class="chapter">{chap_head(ch)}'
                f'<p class="lead">이 장은 준비 중이다.</p></article>')
        return body, [], "준비 중"
    meta, text = read_front_matter(path.read_text(encoding="utf-8"))
    stash = Stash()

    # ## 단위로 나눈다: 이론 / 실습 / 예시 코드 / 그 밖의 제목
    chunks = re.split(r"^## (.+)$", text, flags=re.M)
    pre, pairs = chunks[0], list(zip(chunks[1::2], chunks[2::2]))

    parts_html, jump, practice_titles = [], [], []
    for name, body in pairs:
        name = name.strip()
        sid = SECTION_ID.get(name, "sec-" + str(len(parts_html) + 1))
        inner = md_to_html(body, stash)
        if name == "예시 코드":
            note = '<p class="note">실제 차량에서 검증하기 전의 참고용 코드이다. AI가 만든 코드와 비교하거나 막힌 부분을 확인하는 데 쓴다.</p>'
            parts_html.append(f'<section class="examples"><h2 id="{sid}">{esc(name)}</h2>{note}{inner}</section>')
        else:
            cls = SECTION_CLASS.get(name, "part")
            parts_html.append(f'<section class="{cls}"><h2 id="{sid}">{esc(name)}</h2>\n{inner}</section>')
            if name in SECTION_CLASS:
                jump.append(f'<a href="#{sid}">{esc(name)}</a>')
            if name == "실습":
                practice_titles = re.findall(r"<h3>(.*?)</h3>", inner)

    html_body = "".join(parts_html)

    # 소제목 h3 에 s1, s2 ... 번호를 붙이고 사이드바용 목록을 만든다
    subs = []

    def number_h3(m):
        subs.append(m.group(1))
        return f'<h3 id="s{len(subs)}">{m.group(1)}</h3>'

    html_body = re.sub(r"<h3>(.*?)</h3>", number_h3, html_body)

    # 도구 상자: tools: card=요구사항 카드 작성기, calc#blink=점멸 주기 계산기
    tool_box = ""
    if meta.get("tools"):
        items = []
        for t in meta["tools"].split(","):
            href, _, label = t.partition("=")
            items.append(f"<li><a href='/{href.strip()}'>{esc(label.strip())}</a></li>")
        tool_box = f'<aside class="tool-box"><p class="tool-h">도구</p><ul>{"".join(items)}</ul></aside>'
        # 예시 코드 앞에 끼워 넣는다
        if '<section class="examples">' in html_body:
            html_body = html_body.replace('<section class="examples">', tool_box + '<section class="examples">', 1)
        else:
            html_body += tool_box

    lead = meta.get("lead") or md_to_html(pre, stash).replace("<p>", "").replace("</p>", "").strip()
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    jump_html = f'<nav class="jump" aria-label="이 장의 구성">{"".join(jump)}</nav>' if jump else ""
    body = f'<article class="chapter">{chap_head(ch)}{lead_html}{jump_html}{html_body}</article>'
    summary = " · ".join(re.sub("<.*?>", "", t) for t in practice_titles) or ch["title"]
    return body, subs, summary


def chap_head(ch):
    no = ch["no"]
    kicker = f"부록 {no}" if not no.isdigit() else f"{no}장"
    return (f'<header class="chap-head"><span class="chap-no">{esc(no)}</span>'
            f'<div><p class="kicker">{esc(kicker)}</p><h1>{esc(ch["title"])}</h1></div></header>')


def chap_label(ch):
    return f'{ch["no"]}. {ch["title"]}' if ch["no"].isdigit() else f'부록 {ch["no"]} {ch["title"]}'


# ---------------------------------------------------------------- 공통 틀
def sidebar(current=None, subs=None):
    lis = []
    for ch in SITE["chapters"]:
        on = ch["slug"] == current
        sub = ""
        if on and subs:
            sub = '<ol class="sub">' + "".join(f'<li><a href="#s{i + 1}">{s}</a></li>' for i, s in enumerate(subs)) + "</ol>"
        cls = ' class="on"' if on else ""
        lis.append(f"<li{cls}><a href='/{ch['slug']}'>{esc(chap_label(ch))}</a>{sub}</li>")
    tool_items = []
    for t in SITE["tools"]:
        cls = ' class="on"' if t["slug"] == current else ""
        tool_items.append(f"<li{cls}><a href='/{t['slug']}'>{esc(t['title'])}</a></li>")
    tools = "".join(tool_items)
    return (f'<nav class="sidebar" id="sidebar" aria-label="목차"><div class="side-inner">'
            f'<p class="side-h">차례</p><ol class="chap-list">{"".join(lis)}</ol>'
            f'<p class="side-h">도구</p><ul class="tool-list">{tools}</ul></div></nav>')


def page(title, body, current=None, subs=None, top_title="", body_class="", head_extra="", scripts=()):
    full_title = f"{title} | {SITE['title']}" if title != SITE["title"] else title
    script_tags = "".join(f'<script src="{s}"></script>' if not s.startswith("module:")
                          else f'<script type="module" src="{s[7:]}"></script>' for s in scripts)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(SITE['description'])}">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/style.css">
<script>try{{if(localStorage.getItem('present')==='1')document.documentElement.classList.add('present')}}catch(e){{}}</script>
{head_extra}
</head>
<body class="{body_class}">
<a class="skip" href="#main">본문으로 건너뛰기</a>
<header class="topbar">
  <button type="button" class="menu-btn" aria-controls="sidebar" aria-expanded="false" aria-label="차례 열기"><span></span><span></span><span></span></button>
  <a class="brand" href="/">{esc(SITE['title'])}</a>
  <span class="top-title">{esc(top_title)}</span>
  <button type="button" class="present-btn" aria-pressed="false" title="강의 화면처럼 글자를 크게 본다 (단축키 P)">크게 보기</button>
</header>
<div class="layout">
{sidebar(current, subs)}
<div class="scrim" hidden></div>
<main id="main" class="content">
{body}
</main>
</div>
<script src="/assets/js/site.js"></script>
{script_tags}
</body>
</html>
"""


def pager(idx):
    chs = SITE["chapters"]
    prev = chs[idx - 1] if idx > 0 else None
    nxt = chs[idx + 1] if idx + 1 < len(chs) else None
    a = ""
    if prev:
        a += f"<a class='prev' href='/{prev['slug']}' rel='prev'><small>이전</small>{esc(chap_label(prev))}</a>"
    if nxt:
        a += f"<a class='next' href='/{nxt['slug']}' rel='next'><small>다음</small>{esc(chap_label(nxt))}</a>"
    return f'<nav class="pager" aria-label="장 이동">{a}</nav>'


def home(summaries):
    s = SITE
    hero_img = ""
    if s.get("hero_image"):
        if not (STATIC / s["hero_image"]).exists():
            warn(f"대표 그림 없음: static/{s['hero_image']}")
        hero_img = f'<figure class="hero-img"><img src="/{s["hero_image"]}" alt="{esc(s.get("hero_alt", ""))}" width="1200" height="900"></figure>'
    first = s["chapters"][0]["slug"]
    toc = "".join(
        f"<li><a class='toc-card' href='/{c['slug']}'><span class=\"toc-no\">{esc(c['no'])}</span>"
        f"<span class=\"toc-t\">{esc(c['title'])}</span><span class=\"toc-s\">{esc(summaries[c['slug']])}</span></a></li>"
        for c in s["chapters"]
    )
    tools = "".join(
        f"<li><a class='tool-card' href='/{t['slug']}'><strong>{esc(t['title'])}</strong><span>{esc(t['desc'])}</span></a></li>"
        for t in s["tools"]
    )
    extra_btn = "".join(f"<a class='btn' href='{esc(h)}'>{esc(l)}</a>" for l, h in s.get("hero_links", {}).items())
    return f"""<section class="hero">
  <div class="hero-text">
    <p class="kicker">{esc(s['kicker'])}</p>
    <h1>{esc(s['title'])}</h1>
    <p class="hero-sub">{esc(s['subtitle'])}</p>
    <p class="hero-desc">{esc(s['description'])}</p>
    <p class="hero-actions"><a class='btn primary' href='/{first}'>1장부터 보기</a>{extra_btn}</p>
  </div>
  {hero_img}
</section>
<section class="home-sec"><h2>차례</h2><ol class="toc-grid">{toc}</ol></section>
<section class="home-sec"><h2>도구</h2><ul class="tool-grid">{tools}</ul></section>"""


# ---------------------------------------------------------------- 빌드
def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(STATIC, DIST, ignore=shutil.ignore_patterns("README.txt"))

    summaries = {}
    for idx, ch in enumerate(SITE["chapters"]):
        body, subs, summary = build_chapter(ch)
        summaries[ch["slug"]] = summary
        out = page(chap_label(ch), body + pager(idx), current=ch["slug"], subs=subs,
                   top_title=chap_label(ch), body_class="chap")
        (DIST / f"{ch['slug']}.html").write_text(out, encoding="utf-8")

    for t in SITE["tools"]:
        path = SRC / "pages" / t["file"]
        if path.exists():
            raw = path.read_text(encoding="utf-8")
            body = re.sub(r"\[\[(.+?)\]\]", ref_link, raw)
        else:
            warn(f"도구 페이지 없음: src/pages/{t['file']} (준비 중 페이지로 만든다)")
            body = f'<div class="tool-page"><h1>{esc(t["title"])}</h1><p class="intro">준비 중이다.</p></div>'
        head_extra = t.get("head", "")
        out = page(t["title"], body, current=t["slug"], top_title=t["title"], body_class="tool",
                   head_extra=head_extra, scripts=t.get("scripts", []))
        (DIST / f"{t['slug']}.html").write_text(out, encoding="utf-8")

    (DIST / "index.html").write_text(page(SITE["title"], home(summaries), body_class="home"), encoding="utf-8")
    nf = '<div class="tool-page"><h1>페이지를 찾을 수 없다</h1><p class="intro"><a href="/">처음으로</a> 돌아가 차례에서 고른다.</p></div>'
    (DIST / "404.html").write_text(page("찾을 수 없음", nf), encoding="utf-8")

    n = len(SITE["chapters"]) + len(SITE["tools"]) + 1
    print(f"완료: dist/ 에 {n}쪽을 만들었다.")
    for w in WARN:
        print("  [확인] " + w)


def serve(port=8000):
    """Netlify처럼 /ch01 주소를 ch01.html 로 연결해 주는 미리보기 서버."""
    import functools
    import http.server

    class Handler(http.server.SimpleHTTPRequestHandler):
        def send_head(self):
            p = self.path.split("?", 1)[0].split("#", 1)[0]
            if p != "/" and "." not in p.rsplit("/", 1)[-1] and (DIST / (p.lstrip("/") + ".html")).exists():
                self.path = p + ".html"
            return super().send_head()

        def send_error(self, code, message=None, explain=None):
            if code == 404 and (DIST / "404.html").exists():
                body = (DIST / "404.html").read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().send_error(code, message, explain)

    handler = functools.partial(Handler, directory=str(DIST))
    with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
        print(f"미리보기: http://localhost:{port}  (끝내려면 Ctrl+C)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve(int(sys.argv[2]) if len(sys.argv) > 2 else 8000)
