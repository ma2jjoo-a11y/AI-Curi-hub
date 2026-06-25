# Handoff: AI-Curi 피드 — Threads 스타일 리디자인

## Overview
AI-Curi(아이큐리)는 AI 관련 비즈니스·연구·기술·릴리즈 소식을 크롤링해 보여주는 큐레이션 사이트입니다(레포: `ma2jjoo-a11y/AI-Curi-hub`, GitHub Pages). 기존에는 글씨가 작고 설명이 거의 없는 "카드뉴스" 타일을 나열하는 형태라 가독성이 떨어졌습니다.

이 리디자인은 기존 타일 그리드를 **Threads/X 스타일의 세로 단일 피드**로 바꿉니다. 항목마다 명확한 제목, 뉴스 기사처럼 읽히는 본문(원문 번역/요약), 3줄을 넘으면 `더보기`로 접기, 해시태그, 그리고 카드 전체가 아니라 작은 **`원본 읽기`** 버튼으로만 외부 원문으로 이동합니다. 아바타(프로필 이미지) 자리에는 항목의 **카테고리**가 들어갑니다.

## About the Design Files
이 번들의 `.dc.html` 파일들은 **HTML로 만든 디자인 레퍼런스(프로토타입)**입니다 — 의도한 외형과 동작을 보여주는 목업이며, 그대로 복사해 배포할 production 코드가 아닙니다.

작업의 목표는 이 HTML 디자인을 **대상 코드베이스(`AI-Curi-hub`)의 기존 환경에서 재현**하는 것입니다. 해당 사이트는 바닐라 HTML/CSS/JS 정적 사이트(GitHub Pages)로 보이므로, 기존 렌더링 로직(크롤링 데이터 → DOM 카드 생성) 안에서 카드 마크업/스타일을 이 스펙에 맞게 교체하면 됩니다. 만약 프레임워크(React 등)로 재작성 중이라면, 그 환경의 패턴을 따르되 아래 스펙을 픽셀 단위로 재현하세요.

> `.dc.html` 파일은 내부 디자인 런타임용 문법(`<x-dc>`, `{{ }}`, `<sc-for>` 등)을 포함합니다. 이 문법을 그대로 옮기지 말고, 아래 명세와 토큰을 기준으로 일반 HTML/CSS/JS(또는 대상 프레임워크)로 구현하세요. 브라우저에서 시각 참고용으로 열어볼 수는 있습니다.

## Fidelity
**High-fidelity (hifi).** 최종 색상·타이포그래피·간격·인터랙션이 모두 확정된 목업입니다. `AI-Curi 피드 (Threads 스타일).dc.html`이 구현 기준이며, 아래 토큰/측정값을 그대로 사용해 픽셀 단위로 재현하세요.

(참고: `AI-Curi 피드 와이어프레임.dc.html`은 초기 구조 탐색용 **lofi 와이어프레임**입니다. 결정의 맥락 참고용일 뿐, 시각 구현 기준은 hifi 파일입니다.)

---

## Screen: 메인 피드 (Feed)

### Purpose
사용자가 최신 AI 소식을 위에서 아래로 스크롤하며 훑고, 카테고리/중요도로 필터링하고, 관심 항목은 본문을 펼쳐 읽거나 원문으로 이동합니다.

### Layout
- 전체: `min-height:100vh`, 배경 `var(--bg)`, 글자색 `var(--tx)`. 세로 flex, 가로 가운데 정렬(`align-items:center`).
- 폰트 패밀리: `-apple-system, 'Apple SD Gothic Neo', 'Pretendard', system-ui, 'Segoe UI', sans-serif`. `-webkit-font-smoothing:antialiased`.
- 콘텐츠 컬럼: 모든 주요 블록(상단바 내부, 필터, 피드)은 **`max-width:640px`** 컬럼으로 가운데 정렬. 640px 이하 화면에서는 100% 폭(모바일 = 그대로 단일 컬럼).

세 영역으로 구성: **① 상단바(sticky) → ② 필터칩 행 → ③ 피드 리스트.**

### Component ① 상단바 (Top bar)
- `position:sticky; top:0; z-index:20`, 가로 100%, 내부에 640px 컬럼.
- 배경: `color-mix(in srgb, var(--bg) 86%, transparent)` + `backdrop-filter: saturate(180%) blur(20px)` (반투명 블러).
- 하단 경계선: `1px solid var(--div)`.
- 내부 패딩 `14px 16px`, flex 정렬 gap `12px`.
- 좌측 로고: `◈ 아이큐리` — `font-weight:800; font-size:19px; letter-spacing:-.02em`.
- 로고 옆 부제: `AI-Curi Intel` — `13px; font-weight:600; color:var(--sub)`.
- 우측: 검색 아이콘 버튼 — 36×36 원형, `1px solid var(--div)`, 색 `var(--sub)`. 돋보기 SVG(stroke-width 2.2).

### Component ② 필터칩 행
- 640px 컬럼, 패딩 `12px 16px 4px`, flex, gap `8px`, `overflow-x:auto` (가로 스크롤, 스크롤바 숨김).
- 칩 순서: `전체`, `릴리즈`, `도구`, `API·기술`, `연구`, `비즈니스`, `한국`, `화제`, `🔴 중요`.
- 칩 스타일: `padding:7px 14px; border-radius:999px; font-size:14px; font-weight:600; white-space:nowrap; cursor:pointer; transition:all .15s`.
  - 비활성: `background:var(--chip); color:var(--chipTx); border:1px solid transparent`.
  - 활성: `background:var(--chipOn); color:var(--chipOnTx); border:1px solid var(--chipOn)`.

### Component ③ 피드 항목 (Post) — 핵심
각 항목은 `padding:18px 16px; border-bottom:1px solid var(--div)`. **카드 테두리/배경/그림자 없음** — Threads처럼 하단 헤어라인으로만 구분. 등장 시 `transform: translateY(4px)→0` 만 `.25s ease`로 이동(주의: opacity는 절대 0에서 시작하지 말 것 — 탭이 비활성일 때 애니메이션이 멈춰 내용이 안 보이는 버그가 있었음. transform만 애니메이트).

내부는 flex 2컬럼, gap `12px`:

**(A) 아바타 컬럼 (좌, 고정폭)**
- 42×42 원형. 카테고리를 나타냄.
- 컬러 아바타(기본): `background: color-mix(in srgb, {카테고리색} 18%, var(--bg)); box-shadow: inset 0 0 0 1.5px {카테고리색}`. 가운데에 카테고리 이모지 `font-size:19px`.
- 모노 옵션: `background:var(--chip); box-shadow: inset 0 0 0 1px var(--div)`.

**(B) 콘텐츠 컬럼 (`flex:1; min-width:0`)**, 위→아래 순서:
1. **헤더 행** (flex, gap 6px, 수직 가운데):
   - 카테고리명(=계정명): `font-weight:700; font-size:15px; letter-spacing:-.01em`. 예: `릴리즈`.
   - 중요 표시(중요 항목만): 6×6 원 `background:#f0322e`.
   - 출처·시간: `· {source} · {time}` — `font-size:15px; color:var(--sub)`. 예: `· OpenAI · 2시간`.
   - 우측 끝(`margin-left:auto`): `···` 메뉴 — `color:var(--sub); font-size:18px; cursor:pointer`.
2. **제목**: `font-weight:700; font-size:17px; line-height:1.32; letter-spacing:-.01em; margin-top:5px`. 1–2줄 분량.
3. **본문**: `font-size:15px; line-height:1.5; color:var(--body); margin-top:6px; word-break:break-word`.
   - 기본은 **3줄 클램프**: `display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden` (줄 수는 토큰 `clampLines`, 기본 3, 범위 2–6).
   - 클램프는 **본문이 충분히 길 때만**(레퍼런스 기준: 텍스트 길이 > 90자) 적용. 짧으면 클램프/더보기 없이 전체 표시.
4. **더보기 토글**(클램프 대상일 때만): `margin-top:3px; font-size:15px; font-weight:600; color:var(--sub); cursor:pointer`. 라벨 `더보기` ↔ 펼친 상태 `접기`.
5. **해시태그 행**: flex wrap, gap `8px`, `margin-top:11px`. 각 태그 `#키워드` — `font-size:14px; font-weight:600; color:var(--link); cursor:pointer`.
6. **액션 행** (flex, 수직 가운데, gap 8px, `margin-top:13px`):
   - **원본 읽기** (`<a target="_blank" rel="noopener">`): `padding:7px 13px; border-radius:999px; border:1px solid var(--tx); color:var(--tx); font-size:13px; font-weight:700; text-decoration:none`. 라벨 옆 외부링크 화살표 SVG(↗, 13×13, stroke 2.4). **유일한 외부 이동 수단** — 카드 본체 클릭으로 외부 이동 금지.
   - **번역 보기**: `padding:7px 13px; border-radius:999px; border:1px solid var(--div); color:var(--sub); font-size:13px; font-weight:700; cursor:pointer`. 토글 시 본문을 원문↔번역으로 교체, 라벨 `번역 보기` ↔ `원문 보기`.
   - `flex:1` 스페이서.
   - 우측 아이콘 2개(`color:var(--sub); cursor:pointer`): 북마크(19×19, stroke 1.9), 공유(19×19, stroke 1.9).

### Component ④ 리스트 푸터
- 가운데 정렬 텍스트 `⋯ 스크롤하여 더 불러오기 ⋯` — `padding:24px; color:var(--sub); font-size:14px`. (무한 스크롤/페이지네이션 훅 자리.)

---

## Interactions & Behavior
- **필터칩 클릭**: 활성 필터를 해당 값으로 설정. `전체`=모두, 카테고리명=그 카테고리만, `🔴 중요`=`important:true`인 항목만. 활성 칩은 검정 배경(다크모드는 반전).
- **더보기/접기**: 항목별 펼침 상태 토글. 펼치면 클램프 제거(전체 표시) + 라벨 `접기`. 접으면 다시 3줄.
  - 대안(긴 글): 본문을 카드 안에서 펼치는 대신 상세페이지/새 탭으로 보내고 싶다면 `더보기`를 별도 상세 라우트로 연결해도 됨(레퍼런스 기본은 카드 내 펼침).
- **번역 보기/원문 보기**: 항목별 토글로 본문 텍스트를 번역본↔원문으로 교체. (레퍼런스는 데이터에 `body`(한글)와 `original`(영문)을 모두 보유.)
- **원본 읽기**: 새 탭으로 원문 URL 열기(`target="_blank" rel="noopener"`).
- **등장 애니메이션**: 각 항목 `transform: translateY(4px)→0`, `.25s ease`, `both`. **opacity는 사용하지 않음**(위 주의 참고).
- **transition**: 필터칩 `all .15s`.
- **반응형**: 단일 컬럼이 그대로 모바일 레이아웃. 640px 컬럼이 좁아지며 100%가 됨. 필터 행은 가로 스크롤로 처리.
- 호버 상태는 레퍼런스에서 별도 지정 없음 — 기존 사이트의 관례를 따르거나, 칩/버튼에 미묘한 배경 변화 정도만 추가.

## State Management
- `filter: string` — 현재 활성 필터(기본 `"전체"`).
- `expanded: { [id]: boolean }` — 항목별 더보기 펼침 여부.
- `translated: { [id]: boolean }` — 항목별 번역/원문 표시 여부.
- 데이터: 크롤링 결과 배열을 아래 **데이터 모델**로 매핑. `important` 등 파생값과 `needsMore`(본문 길이>90자) 계산.

### 데이터 모델 (크롤링 데이터 → 카드 매핑)
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string/number | 고유 키 |
| `category` | enum | `릴리즈/도구/API·기술/연구/비즈니스/한국/화제` 중 하나 → 아바타 색·이모지·계정명 |
| `source` | string | 출처(예: OpenAI, arXiv, 네이버) |
| `time` | string | 상대 시간(예: `2시간`, `어제`) |
| `important` | boolean | true면 빨간 점 + `🔴 중요` 필터에 포함 |
| `title` | string | 제목(1–2줄) |
| `body` | string | 한글 번역/요약 본문 |
| `original` | string | 원문(번역 토글용) |
| `tags` | string[] | 해시태그(`#` 없이 키워드) |
| `url` | string | 원문 링크 |

## Design Tokens

### 카테고리 (이모지 / 색)
- 릴리즈 🚀 `#1aa35a`
- 도구 🔧 `#c98a14`
- API·기술 📡 `#0e9aa7`
- 연구 📊 `#2f6fdb`
- 비즈니스 💼 `#9a6b2f`
- 한국 🌏 `#d64545`
- 화제 🔥 `#e8590c`
- 중요 표시 점: `#f0322e`

### 라이트 모드 (CSS 변수)
```
--bg:      #ffffff
--tx:      #0a0a0a   /* 기본 글자, 원본 읽기 테두리 */
--sub:     #999999   /* 출처·시간·더보기·아이콘 */
--body:    #3c3c3c   /* 본문 */
--div:     #ededed   /* 구분선·테두리 */
--link:    #536471   /* 해시태그 */
--chip:    #f4f4f4   /* 비활성 칩 배경 */
--chipTx:  #5a5a5a   /* 비활성 칩 글자 */
--chipOn:  #0a0a0a   /* 활성 칩 배경 */
--chipOnTx:#ffffff   /* 활성 칩 글자 */
```

### 다크(dim) 모드
```
--bg:#0a0a0a  --tx:#f5f5f5  --sub:#8a8a8a  --body:#c9c9c9  --div:#262626
--link:#9bb0c2  --chip:#1a1a1a  --chipTx:#c9c9c9  --chipOn:#f5f5f5  --chipOnTx:#0a0a0a
```

### 타이포그래피 스케일
- 로고 19px / 800 / -.02em
- 제목 17px / 700 / 1.32 / -.01em
- 본문 15px / 1.5
- 계정명(카테고리) 15px / 700 / -.01em
- 출처·시간·더보기 15px / sub색
- 해시태그 14px / 600 / link색
- 필터칩 14px / 600
- 버튼(원본 읽기·번역) 13px / 700
- 아바타 이모지 19px

### 간격·모양
- 콘텐츠 컬럼 max-width **640px**
- 항목 패딩 `18px 16px`, 아바타↔콘텐츠 gap `12px`
- 아바타 42×42 원형
- 칩/버튼 radius `999px` (pill)
- 칩 패딩 `7px 14px`, 버튼 패딩 `7px 13px`
- 구분선 `1px solid var(--div)`
- 등장 애니메이션 `.25s ease`, transform translateY(4px)→0

### 토큰화된 옵션 (구현 시 설정값으로)
- `darkMode` (boolean, 기본 false)
- `coloredAvatars` (boolean, 기본 true) — 카테고리 색 아바타 vs 모노
- `clampLines` (int, 기본 3, 2–6) — 본문 접기 줄 수

## Assets
- 아이콘은 모두 인라인 SVG(돋보기·외부링크 화살표·북마크·공유) — 외부 이미지 의존 없음. 기존 사이트에 아이콘 세트가 있으면 그것으로 대체 가능.
- 카테고리 아바타는 이미지가 아니라 **이모지 + 색 원**으로 구현 — 별도 에셋 불필요.
- 폰트는 시스템 폰트 스택만 사용 — 웹폰트 로딩 불필요.

## Screenshots (`screenshots/`)
구현 시 픽셀 참고용. 모두 라이트 모드 640px 컬럼 기준(다크는 별도).
- `01-feed-light.png` — 기본 피드(라이트), 상단바·필터칩·항목.
- `02-expanded.png` — `더보기`로 본문 펼친 상태(라벨 `접기`).
- `03-translated.png` — `번역 보기`로 본문을 원문(영문)으로 토글한 상태(라벨 `원문 보기`).
- `04-feed-dark.png` — 다크(dim) 모드 피드.

## Files
- `AI-Curi 피드 (Threads 스타일).dc.html` — **구현 기준 hifi 디자인**(인터랙션 포함: 필터/더보기/번역 토글). 시각 참고용으로 브라우저에서 열어볼 것.
- `AI-Curi 피드 와이어프레임.dc.html` — lofi 와이어프레임(구조 결정의 맥락 참고용).

## 구현 메모 (Claude Code용)
- 대상 레포 `ma2jjoo-a11y/AI-Curi-hub`의 기존 카드 렌더링 함수(크롤링 데이터를 DOM으로 그리는 부분)를 찾아, 타일 그리드 마크업을 위 **피드 항목(Post)** 구조로 교체하세요.
- 기존 데이터에 `original`(원문)·`tags`·`category` 정규화가 없다면, 번역 토글/해시태그/아바타가 동작하도록 데이터 파이프라인에 해당 필드를 채우거나 가용 필드로 매핑하세요(없으면 번역 토글/태그는 graceful하게 숨김).
- 카테고리는 위 7종으로 정규화하고, 미분류는 중립 색(`#888`)+`📰`로 폴백.
- 접근성: `원본 읽기`는 실제 `<a>`로(키보드/새탭), 더보기/번역/필터는 `<button>`으로 구현 권장. 본문 클램프는 `-webkit-line-clamp` 사용.
