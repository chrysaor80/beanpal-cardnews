#!/usr/bin/env python3
"""posts/<폴더>/ 의 카드뉴스를 Instagram 캐러셀로 게시한다 (Instagram API with Instagram Login).

- 표준 라이브러리만 사용한다(설치 불필요).
- 게시 대상: post.json 이 있고 published.json 이 없는 폴더. 같은 폴더를 두 번 게시하지 않는다.
- 이미지 주소: 이 저장소의 특정 커밋에 고정된 raw.githubusercontent.com 주소(공개 저장소 필요).
- 환경변수: IG_ACCESS_TOKEN(필수), GITHUB_REPOSITORY, GITHUB_SHA(Actions 가 자동 제공),
  DRY_RUN=1 이면 컨테이너 생성까지만 하고 게시하지 않는다(설정 확인용).

post.json 형식:
  {"type": "brief" | "deepdive", "date": "YYYY-MM-DD", "slides": ["01.jpg", ...], "dry_run": false}
caption.txt: 인스타 캡션 전문 (2,200자 이하, 해시태그 5개 이하)
"""
import json, os, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

API = "https://graph.instagram.com/v25.0"
ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"


def call(method, path, **params):
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    url = f"{API}/{path}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"[API 오류] {method} {path} → HTTP {e.code}: {body}")


def wait_ready(cid, label, tries=30, gap=5):
    """컨테이너가 FINISHED 가 될 때까지 기다린다. ERROR/EXPIRED 면 중단."""
    for _ in range(tries):
        st = call("GET", cid, fields="status_code,status").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise SystemExit(f"[중단] {label} 컨테이너 상태 {st}")
        time.sleep(gap)
    raise SystemExit(f"[중단] {label} 컨테이너가 {tries * gap}초 안에 준비되지 않음")


def validate(folder, meta, caption):
    slides = meta.get("slides") or sorted(p.name for p in folder.glob("*.jpg"))
    if not 2 <= len(slides) <= 10:
        raise SystemExit(f"[중단] {folder.name}: 캐러셀은 2~10장 (현재 {len(slides)}장)")
    for s in slides:
        f = folder / s
        if not f.exists():
            raise SystemExit(f"[중단] {folder.name}: {s} 없음")
        if f.read_bytes()[:3] != b"\xff\xd8\xff":
            raise SystemExit(f"[중단] {folder.name}: {s} 는 JPEG 가 아님 (인스타 API는 JPEG만 받음)")
    if len(caption) > 2200:
        raise SystemExit(f"[중단] {folder.name}: 캡션 {len(caption)}자 (2,200자 초과)")
    tags = [w for w in caption.split() if w.startswith("#")]
    if len(tags) > 5:
        raise SystemExit(f"[중단] {folder.name}: 해시태그 {len(tags)}개 (인스타는 게시물당 5개까지)")
    return slides


def publish(folder):
    meta = json.loads((folder / "post.json").read_text(encoding="utf-8"))
    caption = (folder / "caption.txt").read_text(encoding="utf-8").strip()
    slides = validate(folder, meta, caption)
    dry = os.environ.get("DRY_RUN") == "1" or meta.get("dry_run")
    repo, sha = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_SHA"]
    base = f"https://raw.githubusercontent.com/{repo}/{sha}/posts/{urllib.parse.quote(folder.name)}"
    me = call("GET", "me", fields="user_id,username")
    uid = me["user_id"]
    print(f"계정 @{me.get('username')} · 폴더 {folder.name} · {len(slides)}장 · {'시험(게시 안 함)' if dry else '게시'}")

    children = []
    for i, s in enumerate(slides, 1):
        cid = call("POST", f"{uid}/media", image_url=f"{base}/{urllib.parse.quote(s)}", is_carousel_item="true")["id"]
        wait_ready(cid, f"{i}번째 이미지"); children.append(cid)
        print(f"- 이미지 {i}/{len(slides)} 준비됨")
    parent = call("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(children), caption=caption)["id"]
    wait_ready(parent, "캐러셀")
    if dry:
        print("시험 실행: 캐러셀 컨테이너까지 정상 생성됨. 게시는 하지 않음 (컨테이너는 24시간 후 자동 만료)")
        if meta.get("dry_run"):  # 시험용 폴더는 표시를 남겨 다음 실행에서 다시 처리하지 않는다
            (folder / "dry_run_ok.json").write_text(json.dumps({"tested_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                                                                "commit": sha}) + "\n", encoding="utf-8")
        return None
    limit = call("GET", f"{uid}/content_publishing_limit", fields="quota_usage,config")
    print(f"- 최근 24시간 게시 사용량: {limit.get('data', [{}])[0].get('quota_usage')}")
    mid = call("POST", f"{uid}/media_publish", creation_id=parent)["id"]
    link = None
    for _ in range(3):  # 게시 직후 permalink 조회가 늦게 되는 경우가 있어 몇 번 재시도
        try:
            link = call("GET", mid, fields="permalink").get("permalink"); break
        except SystemExit:
            time.sleep(5)
    rec = {"media_id": mid, "permalink": link, "published_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "commit": sha}
    (folder / "published.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"게시 완료: {link or mid}")
    return rec


def pending():
    """게시할 폴더: published.json 이 없고, 시험용(dry_run)이면 아직 시험하지 않은 폴더."""
    out = []
    for p in POSTS.glob("*/post.json"):
        f = p.parent
        if (f / "published.json").exists() or (f / "dry_run_ok.json").exists():
            continue
        out.append(f)
    return sorted(out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        me = call("GET", "me", fields="user_id,username,account_type")
        lim = call("GET", f"{me['user_id']}/content_publishing_limit", fields="quota_usage,config")
        print(f"토큰 정상 · @{me.get('username')} · 계정 유형 {me.get('account_type')} · 게시 사용량 {lim}")
        sys.exit(0)
    todo = pending()
    if not todo:
        print("게시할 새 폴더 없음"); sys.exit(0)
    for f in todo:
        publish(f)
