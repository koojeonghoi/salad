#!/usr/bin/env python3

"""공식 메뉴 페이지 변경 감지 스크립트.

공식 페이지의 주요 메뉴 관련 텍스트를 이전 스냅샷과 비교합니다.

중요:
- 변경 내용을 index.html에 직접 입력하지 않습니다.
- 페이지 변경 시 candidate 파일과 보고서만 생성합니다.
- 실제 메뉴명, 가격, 판매 기간 및 지점 판매 여부는 사람이 검토합니다.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONFIG_FILE = ROOT / "menu_sources.json"
SNAPSHOT_DIRECTORY = ROOT / "snapshots"
REPORT_FILE = ROOT / "menu-change-report.md"

SNAPSHOT_DIRECTORY.mkdir(exist_ok=True)

CONFIG = json.loads(
    CONFIG_FILE.read_text(encoding="utf-8")
)


class VisibleTextExtractor(HTMLParser):
    """HTML에서 script와 style을 제외한 표시 텍스트를 추출합니다."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {
            "script",
            "style",
            "noscript",
            "svg",
            "template"
        }:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if (
            tag
            in {
                "script",
                "style",
                "noscript",
                "svg",
                "template"
            }
            and self.skip_depth > 0
        ):
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.skip_depth == 0:
            self.parts.append(data)


def encode_url(url: str) -> str:
    """한글 등 비ASCII 문자가 포함된 URL을 안전하게 인코딩합니다."""

    parsed = urllib.parse.urlsplit(url)

    encoded_path = urllib.parse.quote(
        urllib.parse.unquote(parsed.path),
        safe="/:@"
    )

    encoded_query = urllib.parse.quote(
        urllib.parse.unquote(parsed.query),
        safe="=&?/:,+%"
    )

    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            encoded_path,
            encoded_query,
            parsed.fragment
        )
    )


def fetch_page(url: str) -> str:
    """공식 페이지를 다운로드합니다."""

    encoded_url = encode_url(url)

    request = urllib.request.Request(
        encoded_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,"
                "application/xhtml+xml,"
                "application/xml;q=0.9,"
                "image/avif,"
                "image/webp,"
                "*/*;q=0.8"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.7,en;q=0.5",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "close"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=35
    ) as response:

        raw_data = response.read()

        charset = (
            response.headers.get_content_charset()
            or "utf-8"
        )

        return raw_data.decode(
            charset,
            errors="replace"
        )


def normalize_page(
    raw_html: str,
    keywords: list[str]
) -> str:
    """페이지에서 메뉴 관련 영역을 중심으로 비교용 텍스트를 만듭니다."""

    parser = VisibleTextExtractor()
    parser.feed(raw_html)

    full_text = " ".join(parser.parts)

    full_text = re.sub(
        r"\s+",
        " ",
        full_text
    ).strip()

    selected_chunks: list[str] = []
    lowercase_text = full_text.lower()

    for keyword in keywords:
        keyword_lowercase = keyword.lower()
        search_position = 0

        while True:
            found_position = lowercase_text.find(
                keyword_lowercase,
                search_position
            )

            if found_position < 0:
                break

            chunk_start = max(
                0,
                found_position - 180
            )

            chunk_end = min(
                len(full_text),
                found_position + 600
            )

            selected_chunks.append(
                full_text[chunk_start:chunk_end]
            )

            search_position = (
                found_position
                + len(keyword_lowercase)
            )

    if selected_chunks:
        selected_text = "\n".join(
            selected_chunks
        )
    else:
        selected_text = full_text[:30000]

    selected_text = re.sub(
        r"\s+",
        " ",
        selected_text
    ).strip()

    return selected_text[:60000]


def create_digest(text: str) -> str:
    """문자열의 SHA-256 해시를 반환합니다."""

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def extract_tokens(text: str) -> set"""변경 보고서에 사용할 단어 집합을 만듭니다."""

    return set(
        re.findall(
            r"[가-힣A-Za-z0-9&]+",
            text
        )
    )


changed_sources = []
required_errors = []
optional_errors = []
initialized_sources = []


for source in CONFIG["sources"]:
    source_id = source["id"]
    source_name = source["name"]
    source_url = source["url"]
    source_keywords = source.get(
        "keywords",
        []
    )
    optional_source = source.get(
        "optional",
        False
    )

    snapshot_file = (
        SNAPSHOT_DIRECTORY
        / f"{source_id}.txt"
    )

    hash_file = (
        SNAPSHOT_DIRECTORY
        / f"{source_id}.sha256"
    )

    candidate_file = (
        SNAPSHOT_DIRECTORY
        / f"{source_id}.candidate.txt"
    )

    try:
        raw_html = fetch_page(
            source_url
        )

        current_text = normalize_page(
            raw_html,
            source_keywords
        )

        if not current_text:
            raise RuntimeError(
                "페이지에서 비교할 텍스트를 추출하지 못했습니다."
            )

        current_hash = create_digest(
            current_text
        )

        if not snapshot_file.exists():
            snapshot_file.write_text(
                current_text,
                encoding="utf-8"
            )

            hash_file.write_text(
                current_hash,
                encoding="ascii"
            )

            initialized_sources.append(
                source
            )

            continue

        previous_text = snapshot_file.read_text(
            encoding="utf-8"
        )

        previous_hash = create_digest(
            previous_text
        )

        if previous_hash != current_hash:
            previous_tokens = extract_tokens(
                previous_text
            )

            current_tokens = extract_tokens(
                current_text
            )

            added_tokens = sorted(
                current_tokens - previous_tokens,
                key=lambda value: (
                    -len(value),
                    value
                )
            )[:50]

            removed_tokens = sorted(
                previous_tokens - current_tokens,
                key=lambda value: (
                    -len(value),
                    value
                )
            )[:50]

            candidate_file.write_text(
                current_text,
                encoding="utf-8"
            )

            changed_sources.append(
                {
                    "source": source,
                    "added": added_tokens,
                    "removed": removed_tokens,
                    "hash": current_hash,
                    "candidate": candidate_file.name
                }
            )

    except Exception as error:
        error_record = {
            "source": source,
            "error": str(error)
        }

        if optional_source:
            optional_errors.append(
                error_record
            )
        else:
            required_errors.append(
                error_record
            )


report_lines = [
    "# 공식 메뉴 변경 감지 보고서",
    "",
    (
        "> 자동 감지 결과입니다. 실제 메뉴명·가격·판매 지점은 "
        "사람이 공식 페이지와 마곡나루 지점을 확인한 후 반영하세요."
    ),
    ""
]


if changed_sources:
    report_lines.extend(
        [
            "## 변경 감지",
            ""
        ]
    )

    for item in changed_sources:
        source = item["source"]

        report_lines.extend(
            [
                f"### {source['name']}",
                "",
                f"- 공식 URL: {source['url']}",
                f"- 현재 해시: `{item['hash']}`",
                (
                    "- 새로 보인 단어: "
                    + (
                        ", ".join(item["added"])
                        if item["added"]
                        else "없음"
                    )
                ),
                (
                    "- 사라진 단어: "
                    + (
                        ", ".join(item["removed"])
                        if item["removed"]
                        else "없음"
                    )
                ),
                (
                    "- 후보 스냅샷: "
                    f"`snapshots/{item['candidate']}`"
                ),
                ""
            ]
        )


if initialized_sources:
    report_lines.extend(
        [
            "## 최초 기준 생성",
            ""
        ]
    )

    for source in initialized_sources:
        report_lines.append(
            f"- {source['name']}: "
            f"`snapshots/{source['id']}.txt`"
        )

    report_lines.append("")


if required_errors:
    report_lines.extend(
        [
            "## 확인 실패",
            ""
        ]
    )

    for item in required_errors:
        report_lines.append(
            f"- {item['source']['name']}: "
            f"{item['error']}"
        )

    report_lines.append("")


if optional_errors:
    report_lines.extend(
        [
            "## 선택 확인 대상 오류",
            "",
            (
                "아래 페이지는 선택 확인 대상으로 설정되어 있어 "
                "실패해도 전체 감지 작업을 실패 처리하지 않습니다."
            ),
            ""
        ]
    )

    for item in optional_errors:
        report_lines.append(
            f"- {item['source']['name']}: "
            f"{item['error']}"
        )

    report_lines.append("")


if (
    not changed_sources
    and not required_errors
    and not initialized_sources
):
    report_lines.extend(
        [
            "변경이 감지되지 않았습니다.",
            ""
        ]
    )


REPORT_FILE.write_text(
    "\n".join(report_lines),
    encoding="utf-8"
)

print(
    REPORT_FILE.read_text(
        encoding="utf-8"
    )
)


# 종료 코드
# 0: 정상 또는 최초 스냅샷 생성
# 1: 필수 공식 페이지 접근 실패
# 2: 공식 메뉴 변경 감지

if changed_sources:
    raise SystemExit(2)

if required_errors:
    raise SystemExit(1)

raise SystemExit(0)
