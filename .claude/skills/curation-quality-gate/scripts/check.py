#!/usr/bin/env python3
"""
아이큐리허브 큐레이션 품질 게이트 — 기계 점검기.

게시(push) 직전에 docs/data/feed.json 을 받아 '확정 가능한' 문제만 잡아낸다.
판단이 필요한 항목(실제 과장 여부, 출처 신뢰성, 의미적 중복)은 여기서 잡지 않고
SKILL.md 의 사람/에이전트 검토 단계로 넘긴다. 여기서는 사실관계만 본다.

사용:  python3 check.py [feed.json 경로]
종료코드:  0 = 차단 이슈 없음, 1 = 차단 이슈 있음
"""

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

VALID_CATEGORIES = {
    "🚀 릴리즈", "🔧 도구", "📡 API·기술", "📊 연구",
    "💼 비즈니스", "🌏 한국", "🔥 화제",
}
VALID_IMPORTANCE = {"high", "medium", "low"}
REQUIRED_FIELDS = ["id", "date", "category", "title_ko", "summary_ko",
                   "source", "url", "importance", "tags"]

# 과장·낚시성 어휘 — 잡히면 '검토 필요'로만 표시(자동 차단 아님).
# 사실 보도 맥락에서 정당하게 쓰일 수도 있어 사람이 최종 판단한다.
# 주의: '미친'은 동사 미치다("영향을 미친", "기대에 못 미친")와 충돌하므로
# 슬랭형 '미쳤'만 넣는다. 형태소 분석 없이 부분일치로 잡으니 충돌어는 피한다.
HYPE_WORDS = [
    "충격", "충격적", "대박", "역대급", "최강", "최고의", "압도적", "압도",
    "혁명적", "엄청난", "놀라운", "경악", "소름", "미쳤", "충격과",
    "완벽한", "끝판왕", "초대박", "신드롬", "광풍", "열풍",
    "반드시 알아야", "꼭 알아야", "총정리", "완전정복",
]

MAX_ITEMS = 15
ROLLOVER_DAYS = 30
MAX_SENTENCES = 3


def split_sentences(text):
    # 한국어 종결('다.', '음.', '됨.' 등) + 일반 '.'/'!'/'?' 기준 대략 분할.
    parts = re.split(r"(?<=[.!?다음됨])\s+", text.strip())
    return [p for p in parts if p.strip()]


def days_old(item_date, today):
    try:
        d = datetime.strptime(item_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    return (today - d).days


def load_archive_urls(feed_path):
    urls = set()
    archive_dir = feed_path.parent / "archive"
    if not archive_dir.is_dir():
        return urls
    for f in archive_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for it in data.get("items", []):
                if it.get("url"):
                    urls.add(it["url"])
        except (json.JSONDecodeError, OSError):
            continue
    return urls


def main():
    feed_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/data/feed.json")
    if not feed_path.exists():
        print(f"❌ 파일 없음: {feed_path}")
        return 1

    try:
        feed = json.loads(feed_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {e}")
        return 1

    today = date.today()
    blockers = []   # 게시 차단 (반드시 고쳐야 함)
    reviews = []    # 검토 필요 (사람/에이전트 판단)

    # --- 최상위 구조 ---
    if "last_updated" not in feed:
        blockers.append("last_updated 필드 없음")
    else:
        try:
            datetime.fromisoformat(feed["last_updated"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            blockers.append(f"last_updated 형식 이상: {feed.get('last_updated')!r}")

    items = feed.get("items")
    if not isinstance(items, list):
        print("❌ items 배열 없음")
        return 1

    # --- 카드 수 ---
    if len(items) > MAX_ITEMS:
        blockers.append(f"카드 {len(items)}개 — 하루 최대 {MAX_ITEMS}개 초과 (품질 우선)")

    archive_urls = load_archive_urls(feed_path)
    seen_ids, seen_urls = {}, {}

    for i, it in enumerate(items):
        tag = it.get("title_ko") or it.get("id") or f"#{i}"

        # 필수 필드
        for field in REQUIRED_FIELDS:
            if field not in it or it[field] in (None, "", []):
                blockers.append(f"[{tag}] 필수 필드 누락/빈값: {field}")

        # id / url 중복
        _id, url = it.get("id"), it.get("url")
        if _id in seen_ids:
            blockers.append(f"[{tag}] id 중복: {_id} (이미 #{seen_ids[_id]})")
        elif _id:
            seen_ids[_id] = i
        if url in seen_urls:
            # 서로 다른 카드가 같은 URL을 가리킴 — 보통 구체 기사 대신 대문(랜딩) 링크.
            # 스키마 오류는 아니라서 검토 항목으로 둔다(구체 기사 URL로 교체 권장).
            reviews.append(
                f"[{tag}] url 이 다른 카드(#{seen_urls[url]})와 동일: {url} "
                "— 구체 기사 링크 대신 대문 페이지일 가능성, 개별 기사 URL로 교체 검토")
        elif url:
            seen_urls[url] = i
        if url and url in archive_urls:
            reviews.append(f"[{tag}] url 이 archive 에 이미 존재 — 과거 게시분과 중복인지 확인")

        # 카테고리 / 중요도
        if it.get("category") not in VALID_CATEGORIES:
            blockers.append(f"[{tag}] 알 수 없는 카테고리: {it.get('category')!r}")
        if it.get("importance") not in VALID_IMPORTANCE:
            blockers.append(f"[{tag}] importance 값 이상: {it.get('importance')!r}")

        # url 형식
        if url and not re.match(r"^https?://", str(url)):
            blockers.append(f"[{tag}] url 형식 이상(http/https 아님): {url}")

        # 날짜 / 롤오버
        age = days_old(it.get("date", ""), today)
        if age is None:
            blockers.append(f"[{tag}] date 형식 이상: {it.get('date')!r}")
        elif age > ROLLOVER_DAYS:
            reviews.append(f"[{tag}] {age}일 지난 항목 — 30일 롤오버 대상 (archive 이동 검토)")
        elif age < 0:
            reviews.append(f"[{tag}] date 가 미래({it.get('date')}) — 오타 확인")

        # 요약 길이/문장 수
        summary = it.get("summary_ko", "") or ""
        n_sent = len(split_sentences(summary))
        if n_sent > MAX_SENTENCES:
            reviews.append(f"[{tag}] 요약 {n_sent}문장 — 2~3문장 권장, 늘어졌는지 확인")
        if len(summary) > 220:
            reviews.append(f"[{tag}] 요약 {len(summary)}자 — 다소 김, 군더더기 확인")

        # 과장·낚시성 어휘 (자동 차단 아님 — 검토용)
        blob = f"{it.get('title_ko','')} {summary}"
        hits = sorted({w for w in HYPE_WORDS if w in blob})
        if hits:
            reviews.append(f"[{tag}] 과장·낚시 의심어: {', '.join(hits)} — 사실 보도 맥락인지 확인")
        if "!" in blob or "！" in blob:
            reviews.append(f"[{tag}] 느낌표 사용 — 과장 톤 아닌지 확인")

    # --- 출력 ---
    print(f"📋 점검 대상: {feed_path}  (카드 {len(items)}개, 기준일 {today})\n")

    if blockers:
        print(f"🛑 차단 이슈 {len(blockers)}건 — 고치기 전 게시 금지:")
        for b in blockers:
            print(f"   • {b}")
        print()
    else:
        print("✅ 차단 이슈 없음 (스키마·중복·규칙 통과)\n")

    if reviews:
        print(f"🔎 검토 필요 {len(reviews)}건 — SKILL.md 판단 기준으로 사람이 확인:")
        for r in reviews:
            print(f"   • {r}")
        print()
    else:
        print("✅ 검토 플래그 없음\n")

    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
