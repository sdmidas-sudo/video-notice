import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "notices.json"
JS_OUTPUT = DATA_DIR / "notices.js"

KEYWORD_GROUPS = {
    "바우처": ["영상", "영상제작", "홍보영상", "홍보영화"],
    "홈쇼핑/인서트": ["인서트"],
    "라이브커머스": ["숏폼", "롱폼", "유튜브"],
    "입찰": ["영상", "영상제작", "홍보영상", "홍보영화", "숏폼", "롱폼", "유튜브"],
}

SEARCH_TERMS = [
    "영상",
    "영상제작",
    "인서트",
    "홍보영상",
    "홍보영화",
    "숏폼",
    "롱폼",
    "유튜브",
]

EXPORTVOUCHER_SEARCH_TERMS = [
    "영상",
    "영상제작",
    "인서트",
    "홍보영상",
    "홍보영화",
    "숏폼",
    "롱폼",
    "유튜브",
]

SOURCES = [
    {
        "name": "TRN 쇼핑엔티 사업공고",
        "kind": "generic",
        "url": "https://www.trncompany.co.kr/hp/noticeHomeList.do",
    },
    {
        "name": "현대홈쇼핑 입찰/공지",
        "kind": "generic",
        "url": "https://company.hmall.com/news/news_notice.html",
    },
    {
        "name": "나라장터",
        "kind": "search-link",
        "url": "https://www.g2b.go.kr/",
        "searchUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/search/bidSearch.do?taskClCds=5&searchDtType=1&bidNm={query}",
    },
    {
        "name": "기업마당 지원사업 공고",
        "kind": "bizinfo",
        "url": "https://www.bizinfo.go.kr/sii/siia/selectSIIA200View.do",
    },
    {
        "name": "중소벤처24 사업공고",
        "kind": "smes",
        "url": "https://www.smes.go.kr/main/sportsBsnsPolicy",
    },
    {
        "name": "수출바우처 공지사항",
        "kind": "exportvoucher",
        "url": "https://www.exportvoucher.com/portal/board/boardList",
    },
]


def fetch(url, params=None):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(request, timeout=18) as response:
        raw = response.read()
        content_type = response.headers.get("content-type", "").lower()
    charset = "utf-8"
    match = re.search(r"charset=([\w-]+)", content_type)
    if match:
        charset = match.group(1)
    text = raw.decode(charset, errors="replace")
    if text.count("\ufffd") > 20:
        for fallback in ("utf-8", "cp949", "euc-kr"):
            candidate = raw.decode(fallback, errors="replace")
            if candidate.count("\ufffd") < text.count("\ufffd"):
                text = candidate
    return text


def clean_html(value):
    value = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def classify(title):
    hits = []
    for category, keywords in KEYWORD_GROUPS.items():
        matched = [keyword for keyword in keywords if keyword in title]
        if matched:
            hits.append((category, matched))
    if not hits:
        return None
    hits.sort(key=lambda item: len(item[1]), reverse=True)
    category, matched = hits[0]
    return {
        "category": category,
        "matchedKeywords": matched,
        "score": min(100, 60 + len(matched) * 15),
    }


def add_notice(notices, source, title, url, deadline="", detected_from="목록"):
    title = clean_html(title)
    if not title:
        return
    classification = classify(title)
    if not classification:
        return
    notices.append(
        {
            "id": re.sub(r"\W+", "-", f"{source['name']}-{title}")[:120],
            "title": title,
            "source": source["name"],
            "sourceUrl": source["url"],
            "url": url,
            "deadline": deadline or "원문 확인",
            "category": classification["category"],
            "score": classification["score"],
            "matchedKeywords": classification["matchedKeywords"],
            "summary": f"{source['name']}에서 '{', '.join(classification['matchedKeywords'])}' 키워드가 감지되었습니다.",
            "detectedFrom": detected_from,
        }
    )


def collect_exportvoucher(source):
    notices = []
    for term in EXPORTVOUCHER_SEARCH_TERMS:
        html = fetch(
            source["url"],
            {
                "pageNo": 1,
                "bbs_id": 1,
                "active_menu_cd": "EZ005004000",
                "pageUnit": 20,
                "search_type": "SJ",
                "search_text": term,
            },
        )
        rows = re.findall(r"<tr[\s\S]*?</tr>", html, flags=re.I)
        for row in rows:
            detail = re.search(r"goDetail\((\d+)\)[^>]*>([\s\S]*?)</a>", row, flags=re.I)
            if not detail:
                continue
            ntt_id, title = detail.groups()
            dates = re.findall(r"<td[^>]*>\s*(\d{4}-\d{2}-\d{2})\s*</td>", row)
            url = f"https://www.exportvoucher.com/portal/board/boardView?pageNo=1&bbs_id=1&ntt_id={ntt_id}&active_menu_cd=EZ005004000&pageUnit=20"
            add_notice(notices, source, title, url, dates[0] if dates else "", term)
    return notices


def collect_bizinfo(source):
    notices = []
    html = fetch(source["url"])
    links = re.findall(r'<a\s+href=\s*"([^"]*selectSIIA200Detail\.do[^"]*)"[^>]*>([\s\S]*?)</a>', html, flags=re.I)
    for href, title in links:
        url = urllib.parse.urljoin(source["url"], unescape(href))
        add_notice(notices, source, title, url, "", "목록")
    return notices


def collect_smes(source):
    notices = []
    for term in SEARCH_TERMS:
        html = fetch(
            source["url"],
            {
                "srchGubun": 3,
                "srchText": term,
            },
        )
        links = re.findall(
            r"<a\s+href=\"javascript:fn_include_popOpen2\('([^']*)','[^']*','[^']*','([^']*)'[\s\S]*?title=\"([^\"]+)\"",
            html,
            flags=re.I,
        )
        for pblanc_seq, pblanc_id, title in links:
            params = urllib.parse.urlencode(
                {
                    "viewPblancSeq": pblanc_seq,
                    "viewPblancId": pblanc_id,
                }
            )
            url = f"https://www.smes.go.kr/main/sportsBsnsPolicy/view?{params}"
            add_notice(notices, source, title, url, "", term)
    return notices


def collect_generic(source):
    fetch(source["url"])
    return []


def collect_all():
    notices = []
    source_status = []
    for source in SOURCES:
        try:
            if source["kind"] == "exportvoucher":
                found = collect_exportvoucher(source)
            elif source["kind"] == "bizinfo":
                found = collect_bizinfo(source)
            elif source["kind"] == "smes":
                found = collect_smes(source)
            elif source["kind"] == "search-link":
                found = []
            else:
                found = collect_generic(source)
            notices.extend(found)
            source_status.append({"name": source["name"], "status": "ok", "count": len(found), "url": source["url"]})
        except Exception as error:
            source_status.append({"name": source["name"], "status": "error", "count": 0, "url": source["url"], "message": str(error)})

    deduped = {}
    for notice in notices:
        deduped[(notice["source"], notice["title"])] = notice

    payload = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "keywords": KEYWORD_GROUPS,
        "sources": source_status,
        "notices": sorted(deduped.values(), key=lambda item: (item["source"], item["title"])),
    }
    return payload


def main():
    DATA_DIR.mkdir(exist_ok=True)
    payload = collect_all()
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    OUTPUT.write_text(json_text, encoding="utf-8")
    JS_OUTPUT.write_text(f"window.NOTICE_DATA = {json_text};\n", encoding="utf-8")
    print(f"saved {len(payload['notices'])} notices to {OUTPUT}")
    for source in payload["sources"]:
        print(f"- {source['name']}: {source['status']} ({source['count']})")
    if not payload["notices"]:
        print("No keyword-matched notices found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
