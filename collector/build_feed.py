#!/usr/bin/env python3
"""
아이큐리허브 자동 큐레이션 파이프라인 (무료판 — Gemini 2.5 Flash).

하는 일(쉽게):
  1) 여러 뉴스 소스(RSS)에서 어제~오늘 새 글을 모은다
  2) 각 글의 원문 본문을 받아온다
  3) 제미나이에게 "중요한 것 골라 한국어 리드+기사 본문으로 정리해줘"라고 시킨다
  4) 결과를 docs/data/feed.json 에 채운다 (URL·출처는 우리가 수집한 값을 그대로 써서 지어내기 방지)
  5) 30일 지난 카드는 archive 로 옮긴다

이 스크립트는 GitHub Actions(무료 서버)에서 매일 자동 실행된다.
실제 게시(push)와 품질 검사(check.py)는 워크플로(.github/workflows)에서 처리한다.

필요 환경변수: GEMINI_API_KEY
"""

import os
import re
import sys
import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import feedparser
from bs4 import BeautifulSoup

# ── 설정 ────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
FEED_PATH = ROOT / "docs" / "data" / "feed.json"
ARCHIVE_DIR = ROOT / "docs" / "data" / "archive"

KST = timezone(timedelta(hours=9))
DAYS_BACK = 2            # 최근 며칠치 글까지 후보로 볼지
PER_SOURCE = 3           # 한 소스에서 최대 몇 건 뽑을지(한 곳이 후보를 독식하지 않게)
MAX_CANDIDATES = 33      # 제미나이에 보낼 최대 후보 수(안전 상한)
ARTICLE_CHARS = 2600     # 원문에서 가져올 본문 길이(글자)
MAX_CARDS = 15           # 하루 최종 카드 상한
ROLLOVER_DAYS = 30
GEMINI_MODEL = "gemini-2.5-flash"
UA = {"User-Agent": "Mozilla/5.0 (AI-Curi collector; +https://github.com/ma2jjoo-a11y/AI-Curi-hub)"}

VALID_CATEGORIES = {
    "🚀 릴리즈", "🔧 도구", "📡 API·기술", "📊 연구",
    "💼 비즈니스", "🌏 한국", "🔥 화제",
}

# (이름, RSS주소) — 개별 기사 링크가 항목별로 들어있는, 실제 살아있는 피드만 사용한다.
# (2026-06 검증: Rundown·TLDR·Ben's Bites는 죽었거나 뉴스레터 묶음이라 제외)
RSS_SOURCES = [
    ("OpenAI Blog",        "https://openai.com/news/rss.xml"),
    ("Google Blog",        "https://blog.google/innovation-and-ai/rss/"),
    ("The Decoder",        "https://the-decoder.com/feed/"),
    ("VentureBeat",        "https://venturebeat.com/feed/"),
    ("TechCrunch AI",      "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge",          "https://www.theverge.com/rss/index.xml"),
    ("MIT Technology Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed/"),
    ("Simon Willison",     "https://simonwillison.net/atom/everything/"),
    ("AI타임스",           "https://www.aitimes.com/rss/allArticle.xml"),
    ("디지털투데이",       "https://www.digitaltoday.co.kr/rss/allArticle.xml"),
]

# 사이트 전체 피드라 비(非)AI 글이 섞이는 소스 — 제목/요약에 AI 키워드가 있을 때만 채택
GENERAL_SOURCES = {"AI타임스", "디지털투데이", "VentureBeat", "The Verge"}
# 명확한 AI 용어만 — 회사명·일반어(메타/모델/반도체 등)는 오탐이 많아 제외.
# 어차피 최종 선별은 제미나이가 하니, 여기선 '확실한 비AI'만 거르면 된다.
AI_KEYWORDS = [
    "ai", "인공지능", "a.i", "llm", "gpt", "챗gpt", "제미나이", "gemini",
    "클로드", "claude", "openai", "오픈ai", "앤트로픽", "anthropic",
    "생성형", "생성 ai", "머신러닝", "딥러닝", "거대언어", "초거대",
    "ai 에이전트", "agentic", "챗봇", "엔비디아", "nvidia", "코파일럿",
    "sllm", "sora", "미드저니", "자율주행", "휴머노이드",
]

# 기사 본문이 들어있을 법한 칸들 — 이 중 글이 가장 많은 칸을 본문으로 채택
CONTENT_SELECTORS = [
    "[itemprop=articleBody]", "#article-view-content-div", ".article-body",
    ".article-content", ".entry-content", ".post-content", ".story-body",
    "article", "main",
]


def is_ai_related(text):
    t = (text or "").lower()
    return any(k in t for k in AI_KEYWORDS)


def today_kst_date():
    return datetime.now(KST).strftime("%Y-%m-%d")


def load_feed():
    if FEED_PATH.exists():
        return json.loads(FEED_PATH.read_text(encoding="utf-8"))
    return {"last_updated": "", "items": []}


def entry_dt(entry):
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def collect_candidates(existing_urls):
    """RSS를 돌며 최근 글을 모은다. 소스별로 최대 PER_SOURCE건만 뽑아 한 곳이 독식하지 않게 한다."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    cands = []
    for source, url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url, request_headers=UA)
        except Exception as e:
            print(f"  ⚠️ {source} 파싱 실패: {e}", file=sys.stderr)
            continue
        rows = []
        for e in feed.entries:
            link = (e.get("link") or "").strip()
            title = (e.get("title") or "").strip()
            if not link or not title or link in existing_urls:
                continue
            dt = entry_dt(e)
            if dt and dt < cutoff:
                continue
            snippet = BeautifulSoup(e.get("summary", ""), "html.parser").get_text(" ", strip=True)[:400]
            if source in GENERAL_SOURCES and not is_ai_related(title + " " + snippet):
                continue
            rows.append({
                "source": source, "url": link, "title": title,
                "dt": dt or datetime.now(timezone.utc), "snippet": snippet,
            })
        # 소스 안에서 최신순으로 PER_SOURCE건만
        rows.sort(key=lambda x: x["dt"], reverse=True)
        cands.extend(rows[:PER_SOURCE])

    # 전체를 최신순으로 정렬 + url 중복 제거 + 상한
    seen, uniq = set(), []
    for c in sorted(cands, key=lambda x: x["dt"], reverse=True):
        if c["url"] in seen:
            continue
        seen.add(c["url"])
        uniq.append(c)
    return uniq[:MAX_CANDIDATES]


def fetch_article_text(url):
    """기사 페이지에서 본문 텍스트를 뽑아낸다. 여러 후보 칸 중 글이 가장 많은 칸을 고른다."""
    try:
        r = requests.get(url, headers=UA, timeout=15)
        r.raise_for_status()
    except Exception:
        return ""
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    nodes = []
    for sel in CONTENT_SELECTORS:
        nodes.extend(soup.select(sel))
    if soup.body:
        nodes.append(soup.body)

    best = ""
    for node in nodes:
        paras = [p.get_text(" ", strip=True) for p in node.find_all("p")]
        text = "\n".join(p for p in paras if len(p) > 30)
        if len(text) > len(best):
            best = text
    return best[:ARTICLE_CHARS]


def build_prompt(candidates):
    rules = """너는 'AI-Curi(아이큐리)'의 한국어 뉴스 큐레이터다. 아래 후보 기사들 중 AI 관련으로 가장 중요한 것만 5~15개 고르고, 각각을 한국어 카드로 정리하라.

[고르는 기준]
- 우선: Anthropic·OpenAI·Google·Meta 등 공식 발표, 새 모델·제품 출시, 주목할 연구·도구, 한국 AI 소식.
- 제외: 광고성("TOP 10" 류), 루머, 출처 불분명, 단순 홍보, AI와 무관한 글, 서로 중복되는 같은 사건(가장 정확한 하나만).

[각 카드 작성 규칙]
- summary_ko(리드): 사실 중심 2~3문장 한입 요약. 과장·감탄사 없이.
- body_ko(기사 본문): 제공된 '본문'에 충실히 근거해 한국어로 풀어쓴 기사. 2~4문단, 문단은 \\n\\n 으로 구분. 핵심 사실·수치·인물·인용을 담되 군더더기 없이.
  * 매우 중요: 제공된 본문에 없는 사실을 지어내지 마라. 본문이 비어 있거나 부실하면 그 카드는 고르지 마라.
- category: 다음 중 하나만 — "🚀 릴리즈","🔧 도구","📡 API·기술","📊 연구","💼 비즈니스","🌏 한국","🔥 화제"
- importance: "high"(공식 발표·큰 반향) / "medium" / "low"
- tags: 5~7개 배열. 검색이 한국어·영어 양쪽으로 되게 하는 게 목적이다.
  * 주요 고유명사(회사·모델·인물)는 영문과 한글을 모두 넣는다. 예: "OpenAI","오픈AI" / "Anthropic","앤트로픽" / "Gemini","제미나이".
  * 국내 고유명사는 한글 위주(흔히 영문으로도 찾는 SKT·LG 등은 영문도).
  * 주제 태그는 2~3개("규제","출시","반도체" 등) — 단 의미 있는 것만, 억지로 채우지 말 것. 일반어("AI","모델","기술")는 금지.

[출력 형식] 반드시 JSON 배열만 출력. 각 원소는:
{"idx": <후보 번호>, "category": "...", "title_ko": "...", "summary_ko": "...", "body_ko": "...", "importance": "...", "tags": ["..."]}
고를 게 없으면 [] 만 출력하라. idx는 아래 후보의 번호를 그대로 쓴다(URL·출처는 시스템이 그 번호로 채운다)."""

    lines = [rules, "\n\n[후보 기사들]"]
    for i, c in enumerate(candidates):
        body = c.get("text") or c.get("snippet") or ""
        lines.append(f"\n### 후보 {i} | 출처: {c['source']}\n제목: {c['title']}\n본문:\n{body}")
    return "\n".join(lines)


def curate_with_gemini(candidates):
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = build_prompt(candidates)
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json", "temperature": 0.3},
    )
    raw = resp.text.strip()
    try:
        picks = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", raw, re.S)
        picks = json.loads(m.group(0)) if m else []
    return picks if isinstance(picks, list) else []


def make_cards(picks, candidates, date_str):
    cards = []
    used_urls = set()
    for p in picks:
        try:
            idx = int(p["idx"])
            c = candidates[idx]
        except (KeyError, ValueError, IndexError, TypeError):
            continue
        if c["url"] in used_urls:
            continue
        if p.get("category") not in VALID_CATEGORIES:
            continue
        body = (p.get("body_ko") or "").strip()
        summary = (p.get("summary_ko") or "").strip()
        title = (p.get("title_ko") or "").strip()
        if not (body and summary and title):
            continue
        used_urls.add(c["url"])
        cards.append({
            "id": hashlib.sha256(c["url"].encode()).hexdigest()[:8],
            "date": date_str,
            "category": p["category"],
            "title_ko": title,
            "summary_ko": summary,
            "body_ko": body,
            "source": c["source"],
            "url": c["url"],
            "importance": p.get("importance", "medium"),
            "tags": [str(t) for t in (p.get("tags") or [])][:4],
        })
    return cards[:MAX_CARDS]


def rollover(feed, today):
    """30일 초과 카드를 월별 archive로 옮기고 feed에서 제거."""
    keep, moved = [], {}
    today_d = datetime.strptime(today, "%Y-%m-%d").date()
    for it in feed["items"]:
        try:
            age = (today_d - datetime.strptime(it["date"], "%Y-%m-%d").date()).days
        except ValueError:
            age = 0
        if age > ROLLOVER_DAYS:
            moved.setdefault(it["date"][:7], []).append(it)
        else:
            keep.append(it)
    feed["items"] = keep
    if moved:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        for month, items in moved.items():
            f = ARCHIVE_DIR / f"{month}.json"
            data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"items": []}
            data["items"].extend(items)
            f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(sum(moved.values(), []))


def main():
    date_str = today_kst_date()
    feed = load_feed()
    existing_urls = {it.get("url") for it in feed["items"]}

    print(f"📡 수집 시작 ({date_str} KST)")
    candidates = collect_candidates(existing_urls)
    print(f"  후보 {len(candidates)}건 수집")
    if not candidates:
        print("  새 후보 없음 — 종료(변경 없음)")
        return

    print("  원문 본문 받아오는 중…")
    for c in candidates:
        c["text"] = fetch_article_text(c["url"])

    print("🤖 제미나이 큐레이션 중…")
    picks = curate_with_gemini(candidates)
    cards = make_cards(picks, candidates, date_str)
    print(f"  새 카드 {len(cards)}개 생성")
    if not cards:
        print("  채택된 카드 없음 — 종료(변경 없음)")
        return

    # 최신 카드를 맨 앞에, 날짜 내림차순 유지
    feed["items"] = cards + feed["items"]
    feed["items"].sort(key=lambda x: x.get("date", ""), reverse=True)
    moved = rollover(feed, date_str)
    if moved:
        print(f"  📦 {moved}개 카드 archive로 이동")

    # 사이트 표기용: 그날 오전 9시 KST(=00:00Z)로 통일
    feed["last_updated"] = f"{date_str}T00:00:00Z"
    FEED_PATH.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ feed.json 갱신 완료 (총 {len(feed['items'])}개 카드)")


if __name__ == "__main__":
    main()
