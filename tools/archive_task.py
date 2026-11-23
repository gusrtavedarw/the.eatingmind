#!/usr/bin/env python3
"""다 만든 편의 큰 파일(저장소에 올리지 않는 파일)을 구글 드라이브로 옮겨 로컬 공간을 비운다.
온봄(youtube_script) .claude/archive_task.py를 이 저장소에 맞게 고쳤다(2026-11-23 합의).

  python3 tools/archive_task.py pack  <편> [--extra 폴더 ...]   드라이브에 복사하고 기대 크기를 출력
  python3 tools/archive_task.py clean <편> --cloud-verified      클라우드 크기를 확인한 뒤 로컬 원본 삭제

- 대상: production/<편>/ 아래에서 .gitignore로 뺀 파일(그림·음성·음원·렌더·캐시). 저장소 파일은 그대로 둔다.
- 단계 폴더(storyboard, shotlist, recording, export …)마다 tar 하나로 묶는다.
  export/upload/의 업로드 파일(영상·썸네일·문구)은 묶지 않고 낱개로 올린다.
- --extra: 저장소 밖에서 함께 보관할 폴더(예: 이 편 목소리 시험 폴더). 폴더마다 tar 하나.
- 보관 위치: 내 드라이브/claude-work-archive/eating-mind/<편>/. 드라이브 폴더는 ~/Library/CloudStorage/GoogleDrive-*에서 찾는다.
- 클라우드 쪽 크기 대조는 Claude가 드라이브 커넥터로 한 뒤 --cloud-verified를 붙여 clean을 실행한다.
  이 플래그 없이는 아무것도 지우지 않는다. clean은 저장소 맨 위 ARCHIVED.md에 기록을 덧붙인다.
- 지운 뒤에도 드라이브 앱이 내려받아 둔 사본이 남으면 공간이 비지 않는다. Finder에서 보관 폴더를 "다운로드 제거"한다.
"""
import argparse, glob, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_NAME = ROOT.name
SCRATCH = Path(os.environ.get("ARCHIVE_SCRATCH", "/private/tmp/claude-501/archive_scratch"))
UPLOAD = "export/upload/"


def drive():
    found = glob.glob(str(Path.home() / "Library/CloudStorage/GoogleDrive-*/내 드라이브"))
    if len(found) != 1:
        sys.exit(f"구글 드라이브 폴더를 하나로 찾지 못함({len(found)}개). Google Drive 앱이 켜져 있는지 확인하세요.")
    return Path(found[0])


def state_path(ep):
    return ROOT / ".claude" / f"archive_{ep}.state.json"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ignored_files(ep):
    """production/<편>/ 아래에서 git이 관리하지 않는 파일(ROOT 기준 상대 경로)."""
    base = f"production/{ep}"
    if not (ROOT / base).is_dir():
        sys.exit(f"없는 편: {base}")
    if subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", base], capture_output=True, text=True).stdout:
        sys.exit(f"{base}에 커밋하지 않은 변경이 있음. 먼저 커밋하세요.")
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--", base],
                         capture_output=True, text=True, check=True).stdout
    return sorted(f for f in out.split("\0") if f and not f.endswith(".DS_Store"))


def pack(ep, extras):
    dest = drive() / "claude-work-archive" / PROJECT_NAME / ep
    if dest.exists():
        sys.exit(f"이미 있음: {dest} (다른 이름을 쓰거나 기존 폴더를 확인하세요)")
    files = ignored_files(ep)
    extras = [Path(e).expanduser().resolve() for e in extras]
    missing = [str(e) for e in extras if not e.is_dir()]
    if missing:
        sys.exit("없는 폴더: " + ", ".join(missing))
    if not files and not extras:
        sys.exit("보관할 파일이 없음")

    groups = {}  # tar 이름 → 묶을 파일들
    singles = []
    for f in files:
        rel = f[len(f"production/{ep}/"):]
        if rel.startswith(UPLOAD):
            singles.append(f)
        else:
            groups.setdefault(f"{rel.split('/')[0] if '/' in rel else '_root'}.tar", []).append(f)

    SCRATCH.mkdir(parents=True, exist_ok=True)
    dest.mkdir(parents=True)
    env = {**os.environ, "COPYFILE_DISABLE": "1"}  # ._ 리소스포크 파일 방지
    entries = []

    def put(name, src, sources):
        size, digest = src.stat().st_size, md5(src)
        shutil.copyfile(src, dest / name)
        if src.parent == SCRATCH:
            src.unlink()
        entries.append({"name": name, "sources": sources, "size": size, "md5": digest})
        print(f"복사: {name}  {size:,} B", flush=True)

    for name, members in sorted(groups.items()):
        out = SCRATCH / f"{ep}__{name}"
        subprocess.run(["tar", "-cf", str(out), "--null", "-T", "-", "-C", str(ROOT)],
                       input="\0".join(members).encode(), check=True, env=env)
        put(name, out, members)
    for f in singles:
        put(Path(f).name, ROOT / f, [f])
    for e in extras:
        out = SCRATCH / f"{ep}__extra_{e.name}.tar"
        subprocess.run(["tar", "-cf", str(out), "--exclude", ".DS_Store", "-C", str(e.parent), e.name], check=True, env=env)
        put(f"extra_{e.name}.tar", out, [str(e)])

    (dest / "MANIFEST.json").write_text(json.dumps({
        "episode": ep, "archived_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "restore": "단계 폴더 tar는 저장소 맨 위에서 `tar -xf <이름>.tar`로 풀면 제자리로 돌아간다. "
                   "extra_ tar는 sources에 적힌 폴더의 상위 폴더에서 푼다.",
        "files": entries}, ensure_ascii=False, indent=2))
    state_path(ep).parent.mkdir(exist_ok=True)
    state_path(ep).write_text(json.dumps({"dest": str(dest), "files": entries}, ensure_ascii=False))
    print(f"\n드라이브 경로: claude-work-archive/{PROJECT_NAME}/{ep}")
    print("클라우드에서 이 크기와 일치해야 함:")
    for f in entries:
        print(f"  {f['name']}\t{f['size']}")


def clean(ep, cloud_verified):
    if not cloud_verified:
        sys.exit("--cloud-verified 없이는 삭제하지 않음")
    st = json.loads(state_path(ep).read_text())
    dest = Path(st["dest"])
    for f in st["files"]:  # 마운트에서 본 크기도 한 번 더 확인
        got = (dest / f["name"]).stat().st_size if (dest / f["name"]).exists() else None
        if got != f["size"]:
            sys.exit(f"크기 불일치로 중단: {f['name']} 기대 {f['size']} / 드라이브 {got}. 아무것도 지우지 않음.")
    freed = 0
    for f in st["files"]:
        for s in f["sources"]:
            p = Path(s) if os.path.isabs(s) else ROOT / s
            if p.is_dir():
                freed += sum(x.stat().st_size for x in p.rglob("*") if x.is_file())
                shutil.rmtree(p)
            elif p.exists():
                freed += p.stat().st_size
                p.unlink()
    for d, _, _ in sorted(os.walk(ROOT / "production" / ep), key=lambda w: -len(w[0])):  # 비게 된 폴더 정리
        left = os.listdir(d)
        if left == [".DS_Store"]:
            os.remove(os.path.join(d, ".DS_Store"))
            left = []
        if not left:
            os.rmdir(d)
    singles = [f["name"] for f in st["files"] if not f["name"].endswith(".tar")]
    with open(ROOT / "ARCHIVED.md", "a") as fh:  # 이전 기록은 남기고 덧붙임
        fh.write(f"\n# {ep}\n\n이 편의 큰 파일(저장소에 올리지 않은 파일)을 구글 드라이브로 옮겼습니다: "
                 f"`내 드라이브/claude-work-archive/{PROJECT_NAME}/{ep}`\n"
                 "단계 폴더마다 `.tar`로 묶여 있고, 저장소 맨 위에서 `tar -xf <이름>.tar`로 풀면 제자리로 돌아갑니다. 목록은 같은 폴더의 MANIFEST.json.\n"
                 + (f"업로드 파일({', '.join(singles)})은 묶지 않고 낱개로 두었습니다.\n" if singles else ""))
    print(f"삭제 완료. 확보한 공간: {freed / 1e9:.2f} GB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pack", "clean"])
    ap.add_argument("episode", help="production/ 아래 편 폴더 이름(예: soup-popcorn)")
    ap.add_argument("--cloud-verified", action="store_true")
    ap.add_argument("--extra", nargs="+", default=[], help="저장소 밖에서 함께 보관할 폴더")
    a = ap.parse_args()
    pack(a.episode, a.extra) if a.cmd == "pack" else clean(a.episode, a.cloud_verified)
