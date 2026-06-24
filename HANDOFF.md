# 인수인계 문서 — 아이큐리에게

> 작성: 다비 (다비-한양 프로젝트) → 아이큐리 (아이큐리허브 전담)
> 작성일: 2026-06-24
> 이 문서는 아이큐리가 처음 일을 넘겨받았을 때 "지금 상황이 어디까지 와 있고, 다음에 뭘 하면 되는지"를 한 번에 파악하기 위한 문서다.

---

## 0. 한 줄 요약
AI 뉴스 큐레이션 허브 "아이큐리허브"가 구축돼서 라이브로 떠 있다.
구조·디자인·첫 데이터까지 완료됐고, **남은 건 정기 수집·게시를 굴러가게 만드는 것**이다.

---

## 1. 이 프로젝트가 뭔가
Joy가 nest.kndli.com/intel 같은 "나만의 AI 지식 허브"를 원해서 만들었다.
- AI 관련 최신·정확한 정보만 카드 형태로 모아서 보여주는 웹사이트
- 1년간은 사실상 Joy 개인용, 안정화되면 정식 공개 예정
- 현재 라이브: **https://ma2jjoo-a11y.github.io/AI-Curi-hub/**

## 2. 지금까지 완료된 것 ✅
- [x] GitHub 레포 생성 (`ma2jjoo-a11y/AI-Curi-hub`, public)
- [x] 프론트엔드 카드 피드 (`docs/` — index.html, style.css, app.js)
- [x] 디자인: 라이트 테마 (배경 #f6f7f9, 카드 #ffffff, 드롭쉐도우), 카테고리/날짜/중요도 필터
- [x] GitHub Pages 배포 완료 (main `/docs`)
- [x] 에이전트 프롬프트 2종 (Curator = `CLAUDE.md`, Collector = `collector/CLAUDE.md`)
- [x] **첫 실제 큐레이션** — 2026-06-24 기준 AI 뉴스 9건 수집·게시 (`docs/data/feed.json`)

## 3. 남은 일 (우선순위 순) ⬜
1. **정기 수집·게시 루틴 확립**
   - 주 1~2회 Collector 소스 순회 → Curator 편집 → feed.json 갱신 → push
   - 자동 스케줄(예: 매일 아침)로 만들지, 수동으로 돌릴지 Joy와 결정 필요
2. **feed.json 30일 롤오버**
   - 카드가 쌓이면 30일 지난 항목은 `docs/data/archive/`로 분리 (아직 archive 폴더 없음 — 필요 시 생성)
3. **소스 확장**
   - Joy가 "학교 SNS 말고 더 폭넓게 수집하고 싶다"고 했음 → 관심 분야 넓히면 `collector/CLAUDE.md` 소스 표에 추가
4. **OpenAI 블로그 수집 이슈**
   - openai.com/news는 WebFetch가 403 반환함. 대안: RSS나 다른 경로 탐색 필요

## 4. 매번 수집·게시할 때 워크플로
```
1. collector/CLAUDE.md의 소스 목록을 WebFetch로 순회
2. 24시간(또는 지난 수집 이후) 새 항목만 추림, 중복 URL 제외
3. Curator 기준으로 필터링 + 중요도 판단 + 한국어 요약 2~3문장
4. docs/data/feed.json의 items 배열 갱신 (최신순, 5~15건 유지)
5. last_updated 갱신
6. git add → commit → push
7. 1~2분 후 라이브 사이트에서 확인
```

## 5. 절대 잊지 말 것 ⚠️
- **feed.json 위치는 반드시 `docs/data/feed.json`** (GitHub Pages가 `/docs`만 서빙하기 때문). 루트 `data/`에 두면 사이트에서 404 난다. (실제로 한 번 겪은 실수)
- 요약은 **사실만, 과장·감탄사 없이**. 마케팅성("TOP 10" 류)·루머·출처 불분명은 제외.
- JSON 문법 깨지면 사이트 전체가 "오류" 표시됨 → 커밋 전 JSON 유효성 확인.
- 카드는 품질 우선, 하루 15건 초과 금지.

## 6. 자주 쓰는 명령
```bash
# 레포 클론 (최초 1회)
git clone https://github.com/ma2jjoo-a11y/AI-Curi-hub.git

# 로컬 미리보기 (docs를 루트로 서빙)
cd AI-Curi-hub && python3 -m http.server 3456 --directory docs
# → http://localhost:3456 접속

# 게시
git add docs/data/feed.json && git commit -m "큐레이션 YYYY-MM-DD" && git push
```

## 7. 연락/계정 정보
- GitHub: ma2jjoo-a11y (gh CLI 인증돼 있음)
- Joy 이메일: ma2jjoo@gmail.com
- 라이브: https://ma2jjoo-a11y.github.io/AI-Curi-hub/

---
*다비가 깔아둔 토대 위에서, 이제 아이큐리가 굴려주면 돼! — 다비 🦁*
