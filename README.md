# 전장제어교육 사이트 스타터 키트

아두이노 전장 미니카 교재를 정적 웹사이트로 만들어 Netlify에 올리기 위한 틀이다.

```powershell
pip install -r requirements.txt
python build.py serve      # http://localhost:8000 미리보기, 결과는 dist/
```

- 원고: `src/chapters/*.md` (견본 `ch02.md`, `ch03.md`)
- 차례·제목: `src/site.json`
- 디자인: `static/assets/css/style.css`
- 배포: `dist/` 폴더를 <https://app.netlify.com/drop> 에 끌어다 놓기

전체 절차는 **[GUIDE.md](GUIDE.md)** 에 있다.
