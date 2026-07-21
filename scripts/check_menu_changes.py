#!/usr/bin/env python3
"""Detect meaningful changes on official menu pages.

This script does NOT rewrite index.html automatically. It normalizes visible page text,
compares it with the last approved snapshot, and writes menu-change-report.md.
"""
from __future__ import annotations
import hashlib, json, re, sys, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "menu_sources.json").read_text(encoding="utf-8"))
SNAP_DIR = ROOT / "snapshots"
REPORT = ROOT / "menu-change-report.md"
SNAP_DIR.mkdir(exist_ok=True)

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in {"script","style","noscript","svg"}: self.skip += 1
    def handle_endtag(self, tag):
        if tag in {"script","style","noscript","svg"} and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 SaladMenuMonitor/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", errors="replace")

def normalize(raw: str, keywords: list[str]) -> str:
    parser=TextExtractor(); parser.feed(raw)
    text=re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    # Keep nearby text around configured menu words to reduce false positives from headers/footers.
    chunks=[]
    low=text.lower()
    for word in keywords:
        start=0; w=word.lower()
        while True:
            i=low.find(w,start)
            if i<0: break
            chunks.append(text[max(0,i-180):min(len(text),i+500)])
            start=i+len(w)
    selected="\n".join(chunks) if chunks else text[:20000]
    selected=re.sub(r"\s+", " ", selected).strip()
    return selected[:50000]

def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

changed=[]; errors=[]; initialized=[]
for source in CONFIG["sources"]:
    sid=source["id"]; snap=SNAP_DIR/f"{sid}.txt"; meta=SNAP_DIR/f"{sid}.sha256"
    try:
        current=normalize(fetch(source["url"]), source.get("keywords",[]))
        current_hash=digest(current)
        if not snap.exists():
            snap.write_text(current,encoding="utf-8"); meta.write_text(current_hash,encoding="ascii")
            initialized.append(source)
            continue
        old=snap.read_text(encoding="utf-8")
        if digest(old) != current_hash:
            old_tokens=set(re.findall(r"[가-힣A-Za-z0-9&]+",old))
            new_tokens=set(re.findall(r"[가-힣A-Za-z0-9&]+",current))
            additions=sorted(new_tokens-old_tokens,key=lambda x:(-len(x),x))[:40]
            removals=sorted(old_tokens-new_tokens,key=lambda x:(-len(x),x))[:40]
            changed.append((source,additions,removals,current_hash))
            # Write candidate separately. Approved baseline is updated only by a human commit.
            (SNAP_DIR/f"{sid}.candidate.txt").write_text(current,encoding="utf-8")
    except Exception as e:
        errors.append((source,str(e)))

lines=["# 공식 메뉴 변경 감지 보고서","","> 자동 감지 결과입니다. 실제 메뉴명·가격·판매 지점은 사람이 공식 페이지와 마곡나루 지점을 확인한 후 반영하세요.",""]
if changed:
    lines += ["## 변경 감지",""]
    for source,additions,removals,h in changed:
        lines += [f"### {source['name']}",f"- 공식 URL: {source['url']}",f"- 현재 해시: `{h}`",f"- 새로 보인 단어: {', '.join(additions) or '없음'}",f"- 사라진 단어: {', '.join(removals) or '없음'}",f"- 후보 스냅샷: `snapshots/{source['id']}.candidate.txt`",""]
if initialized:
    lines += ["## 최초 기준 생성",""]+[f"- {x['name']}: `snapshots/{x['id']}.txt`" for x in initialized]+[""]
if errors:
    lines += ["## 확인 실패",""]+[f"- {x['name']}: {err}" for x,err in errors]+[""]
if not changed and not errors:
    lines += ["변경이 감지되지 않았습니다.",""]
REPORT.write_text("\n".join(lines),encoding="utf-8")
print(REPORT.read_text(encoding="utf-8"))
# 2 means change; 1 means fetch error; 0 means clean/initialization.
raise SystemExit(2 if changed else (1 if errors else 0))
