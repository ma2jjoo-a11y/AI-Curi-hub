# 인수인계 문서 — 큐리에게

> 작성: 다비 (다비-한양 프로젝트) → 큐리 (아이큐리허브 전담 에이전트)
> 작성일: 2026-06-24
> 이 문서는 큐리가 처음 일을 넘겨받았을 때 "지금 상황이 어디까지 와 있고, 다음에 뭘 하면 되는지"를 한 번에 파악하기 위한 문서다.
> (네이밍: 서비스·사이트="아이큐리(AI-Curi)", 레포="아이큐리허브(AI-Curi-hub)", 운영 에이전트=나="큐리(Curi)")

---

## 0. 한 줄 요약
AI 뉴스 큐레이션 서비스 "아이큐리(AI-Curi)"가 구축돼서 라이브로 떠 있다.
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

## 8. 운영 로그 / 알려진 이슈 (큐리 기록)

### 2026-07-17 큐레이션
- **게시**: 6장 (feed.json). WAIC 2026(상하이) 개막이 그날 뉴스를 지배 → 5장이 WAIC 관련(시진핑 첫 기조연설, 中 AI 거버넌스 행동계획·WAICO 29개국 서명, 화웨이 아틀라스 950, 미니맥스 M3, WAIC 로봇 데뷔) + 구글 제미나이 3.5 프로 출시 연기 1장.
- **수집 로그**: `collector/output/2026-07-17.json` (published 6 / dropped 5 / errors 기록).

#### ⚠️ 오류 (발생 → 해결)
1. **웹 소스 전면 접근 불가 (근본 원인 규명)** — 처음엔 "사이트측 봇 차단"으로 봤으나 **오진이었음**. 실제 원인은 **이 실행 환경의 네트워크 송신(egress) 정책**이다.
   - 증거: `curl "$HTTPS_PROXY/__agentproxy/status"`의 `recentRelayFailures`에 `connect_rejected` / "gateway answered 403 to CONNECT (**policy denial**)" 로 techcrunch·openai·the-decoder 등이 기록됨. curl 에러도 "CONNECT tunnel failed, response 403"(=프록시가 CONNECT 거부).
   - 정책 성격(실측): **허용** = `api.github.com`·`raw.githubusercontent.com`·pypi/npm 등 패키지 레지스트리·anthropic.com. **차단** = 일반 웹 전부(wikipedia·google·arxiv·hn.algolia·reddit + 모든 뉴스/RSS 소스). 즉 "GitHub + 패키지 레지스트리만 허용"하는 **제한형 네트워크 정책**.
   - ⚠️ 프록시 규칙상 **조직 정책 거부(403/407)는 우회 금지, 보고 대상**. 그래서 코드로 뚫지 않는다.
   → **당장의 해결(우회)**: **WebSearch**(앤트로픽 서버측 도구라 egress 정책과 무관하게 동작)로 수집·작성. 원문 1:1 대조는 불가 → **복수 신뢰매체 교차확인 + 품질게이트**로 보완.
   → **근본 해결(Joy 조치 필요)**: 웹 세션 생성 시 **네트워크 정책을 더 개방적인 등급으로 변경**하거나 수집 소스 도메인을 허용목록에 추가. 문서: https://code.claude.com/docs/en/claude-code-on-the-web (환경·네트워크 정책 섹션).
2. **제미나이 카드 오류(초벌)** — 초벌에서 "제미나이 3.5 정식 출시"로 카드를 썼으나, 그 blog.google URL은 **5월 19일 I/O 발표분(이미 archive/2026-05.json에 존재)**이었고, 저품질 매체만 "7/17 출시"라 보도. 블룸버그·CNBC(7/16)는 **오히려 출시 연기 + 알파벳 주가 하락**으로 확인.
   → **해결**: `curation-quality-gate`가 archive URL 중복으로 플래그 → 카드를 사실(출시 연기, 출처 CNBC)로 교체. **품질 게이트가 오보를 막은 사례.**

#### 🕳️ 누락건 (수집했으나 제외 — 사유 기록)
- **네이버 AI탭 정식 출시** / **카카오톡 챗GPT 채팅방 기능**: 각각 6/26·6/16 건이라 오늘치(신규 발표) 아님 → 제외. (한국 소식이라 아쉽지만 날짜 부정확 방지 우선)
- **정부 반도체·AI 1350조 투자(하반기 경제성장전략)**: 7/14 건, 컷오프 이전 → 제외.
- **Anthropic 블로그(대규모 코드 마이그레이션) / Claude Code 접근성 업데이트**: 개별 기사 URL 확정 실패(대문·롤링 release-notes만 확인) → '개별 기사 URL' 규칙 미충족으로 보류.

#### 📌 다음 할 일 (이 이슈들 근본 해결)
- **[Joy 조치] 네트워크 정책 변경이 근본 해결**: 현재 환경은 뉴스/RSS 소스가 전부 차단이라 원문 대조가 구조적으로 불가. 웹 세션의 네트워크 정책을 개방형으로 바꾸면 collector가 원래 설계대로(RSS/WebFetch) 굴러감. → https://code.claude.com/docs/en/claude-code-on-the-web
- **[정책 변경 전까지] WebSearch 기반 수집을 표준 절차로**: `collector/CLAUDE.md`에 반영함. 규율 = ①한 건당 신뢰매체 2곳 이상 교차확인 ②출시/수치 주장은 저품질 매체 단독 근거 금지(오늘 제미나이 오보를 이 규율로 잡음) ③게시 전 `curation-quality-gate` 필수.
- **한국 소식 소스 보강**: AI타임스/디지털투데이 RSS도 차단이라 국내 커버리지 약함 → 정책 개방 시 우선 복구, 그 전엔 WebSearch 한국어 쿼리로 보완.

---
*다비가 깔아둔 토대 위에서, 이제 큐리가 굴려주면 돼! — 다비 🦁*
