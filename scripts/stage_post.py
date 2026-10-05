#!/usr/bin/env python3
"""카드뉴스 작성기(예약 작업)가 쓰는 도구: 렌더된 PNG 를 게시용 폴더로 옮긴다.

사용법:
  python3 scripts/stage_post.py --type deepdive --date 2026-10-08 --src /작업폴더/out --caption /작업폴더/caption.txt [--dry-run]

- src 의 01_*.png ~ NN_*.png 를 이름순으로 01.jpg ~ NN.jpg (JPEG, 품질 92)로 바꿔 posts/<date>-<type>/ 에 저장한다.
  00_preview_all.png 와 blog 폴더는 옮기지 않는다.
- caption.txt 와 post.json 을 함께 만든다. 이미 같은 폴더가 있으면 중단한다(중복 게시 방지).
- 저장만 한다. git add/commit/push 는 호출한 쪽에서 한다.
"""
import argparse, json, re, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser()
ap.add_argument("--type", required=True, choices=["brief", "deepdive"])
ap.add_argument("--date", required=True)
ap.add_argument("--src", required=True)
ap.add_argument("--caption", required=True)
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()

if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date):
    sys.exit("[중단] --date 는 YYYY-MM-DD")
src = Path(a.src)
pngs = sorted(p for p in src.glob("[0-9][0-9]_*.png") if not p.name.startswith("00_"))
if not 2 <= len(pngs) <= 10:
    sys.exit(f"[중단] 슬라이드 PNG 가 2~10장이어야 함 (현재 {len(pngs)}장)")
cap = Path(a.caption).read_text(encoding="utf-8").strip()
if not cap:
    sys.exit("[중단] 캡션이 비어 있음")

dest = ROOT / "posts" / f"{a.date}-{a.type}"
if dest.exists():
    sys.exit(f"[중단] 이미 있는 폴더: {dest.name}")
dest.mkdir(parents=True)
slides = []
for i, p in enumerate(pngs, 1):
    im = Image.open(p).convert("RGB")
    if im.size != (1080, 1350):
        sys.exit(f"[중단] {p.name} 크기 {im.size} (1080×1350 이어야 함)")
    name = f"{i:02d}.jpg"
    im.save(dest / name, "JPEG", quality=92, optimize=True, progressive=False)
    slides.append(name)
(dest / "caption.txt").write_text(cap + "\n", encoding="utf-8")
(dest / "post.json").write_text(json.dumps({"type": a.type, "date": a.date, "slides": slides, "dry_run": a.dry_run},
                                           ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"준비 완료: posts/{dest.name} ({len(slides)}장{', 시험 실행' if a.dry_run else ''})")
