# 수프·팝콘 편 1분 시험 영상(C01~C11)을 HyperFrames 장면으로 만든다(2026-11-23 합의).
# 컷 길이 = 내레이션 + 쉼, 자막 = 말소리 구간 안에서 글자 수 비례, 소리 = 콘티 소리 칸, 크기 = 내레이션(-16 LUFS) 기준.
# 자산(그림·음성·음원·글꼴)은 assets/에 복사하고 저장소에는 올리지 않는다(.gitignore).
# 실행: VoiceStudio venv python build.py   → index.html, compositions/pictures.html, compositions/captions.html, timing.json
import glob, html, json, os, re, shutil, subprocess
import numpy as np, soundfile as sf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
V4 = os.path.dirname(HERE)
VOICE = os.path.expanduser("~/Documents/claude-work/voice/gustave/out/final")
SOUNDS = os.path.expanduser("~/Documents/claude-work/voice/gustave/sounds")
FONT = os.path.expanduser("~/Library/Fonts/Pretendard-Medium.otf")
A = os.path.join(HERE, "assets")
CUTS = ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11"]
LEAD = {"C01": 1.0}                                   # C01 앞 1초: 검은 화면에서 밝아짐
GAP = {"C01": 0.5, "C02": 0.15, "C03": 0.3, "C04": 0.0, "C05": 0.6, "C06": 1.2, "C07": 0.15,
       "C08": 1.0, "C09": 0.8, "C10": 0.6, "C11": 1.5}  # 컷 뒤 쉼, C11 뒤 1.5초
SILENT = {"C04": 2.0}                                 # 읽지 않는 컷(2026-11-23 오프닝 수정): 바스락 뒤 정적 2초
DISSOLVE = {"C07": 0.6}                               # 구간이 바뀌는 C06→C07
FADE_END = 0.8                                        # 마지막 검은 화면으로
# 움직임(콘티 '움직임·전환'): push = 느린 밀기(배율), pan = 패닝(가로 비율), still = 정지
MOTION = {"C01": ("push", 1.035), "C02": ("push", 1.04), "C03": ("push", 1.025), "C04": ("still", 0),
          "C05": ("pan", 0.02), "C06": ("push", 1.04), "C07": ("push", 1.012), "C08": ("still", 0),
          "C09": ("push", 1.025), "C10": ("push", 1.015), "C11": ("pan", 0.025)}
# 소리 크기 목표(LUFS): 내레이션 -16, 낮은 음 -34(18dB 아래), TV -40(24dB 아래), 효과음은 깔린 소리보다 4~6dB 위(순간 최대)
T_DRONE, T_TV, T_SFX_TV, T_SFX_DRONE = -34.0, -40.0, -34.0, -30.0

def loud(path, start=None, dur=None, momentary=False):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"] + (["-ss", str(start), "-t", str(dur)] if start is not None else []) + ["-i", path, "-af", "ebur128", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    if momentary:
        ms = [float(m) for m in re.findall(r"M:\s*(-?[\d.]+)", out) if float(m) > -70]
        return max(ms)
    return float(re.findall(r"I:\s*(-?[\d.]+) LUFS", out)[-1])

def gain(target, measured): return round(min(3.98, 10 ** ((target - measured) / 20)), 3)

# 1) 자산 복사
for d in ("img", "voice", "sfx", "fonts"): os.makedirs(f"{A}/{d}", exist_ok=True)
for c in CUTS:
    dst = f"{A}/img/{c}.jpg"; src = f"{V4}/cuts/{c}_paper.png"
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        Image.open(src).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dst, quality=92)
    if c not in SILENT: shutil.copy2(f"{VOICE}/{c}.wav", f"{A}/voice/{c}.wav")
for key in ("bag_b", "crunch_a", "tv_a", "drone_a"):
    shutil.copy2(glob.glob(f"{SOUNDS}/{key}_*.mp3")[0], f"{A}/sfx/{key}.mp3")
shutil.copy2(FONT, f"{A}/fonts/Pretendard-Medium.otf")

# 2) 컷 시간
cuts = {c["id"]: c for s in json.load(open(f"{V4}/review/conti.json"))["sections"] for c in s["cuts"]}
t, T = 0.0, {}
for c in CUTS:
    lead = LEAD.get(c, 0.0)
    if c in SILENT: vd, extra = 0.0, SILENT[c]
    else:
        y, sr = sf.read(f"{A}/voice/{c}.wav", dtype="float32"); vd, extra = len(y) / sr, 0.0
    T[c] = {"start": round(t, 3), "voice_start": round(t + lead, 3), "voice_dur": round(vd, 3), "dur": round(lead + vd + extra + GAP[c], 3)}
    t += lead + vd + extra + GAP[c]
TOTAL = round(t, 3)

# 3) 자막: 문장·쉼표 단위로 나누고, 말소리 덩어리(0.25초 이상 쉼으로 나뉜 구간)에 글자 수 비례로 맞춘다
def speech_runs(y, sr):
    hop = int(sr * 0.01); db = np.array([20 * np.log10(np.sqrt(np.mean(y[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(y) - hop, hop)])
    on = db > -45; runs, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and (on[j] or on[j:j + 25].any()): j += 1
            runs.append([i * 0.01, j * 0.01]); i = j
        else: i += 1
    return runs

syl = lambda s: max(1, len(re.findall(r"[가-힣]", s)))

def chunks(text):
    """문장 끝에서는 늘 나누고, 쉼표에서는 앞뒤가 모두 9음절 이상일 때만 나눈다('아,'·'안녕하세요,'가 혼자 스쳐 가지 않게)."""
    out = []
    for sent in [p.strip() for p in re.split(r"(?<=[.?!])\s+", text) if p.strip()]:
        parts = [p.strip() for p in re.split(r"(?<=,)\s+", sent) if p.strip()]
        merged = [parts[0]]
        for p in parts[1:]:
            if syl(merged[-1]) >= 9 and syl(p) >= 9: merged.append(p)
            else: merged[-1] = merged[-1] + " " + p
        out += merged
    return [re.sub(r"[.,]$", "", p) for p in out]  # 줄 끝 마침표·쉼표는 자막에서 뺀다(물음표는 둔다)
CAPS = []
for c in CUTS:
    if c in SILENT: continue
    y, sr = sf.read(f"{A}/voice/{c}.wav", dtype="float32")
    runs, parts = speech_runs(y, sr), chunks(cuts[c]["text"])
    a0, a1 = runs[0][0], runs[-1][1]
    weights = np.cumsum([0] + [syl(p) for p in parts]); total = weights[-1]
    for k, p in enumerate(parts):
        s = a0 + (a1 - a0) * weights[k] / total; e = a0 + (a1 - a0) * weights[k + 1] / total
        # 경계 가까이에 쉼이 있으면 그 쉼에 맞춘다
        for r0, r1 in zip(runs, runs[1:]):
            gap_mid = (r0[1] + r1[0]) / 2
            if abs(gap_mid - e) < 0.6 and k < len(parts) - 1: e = r0[1]
            if abs(gap_mid - s) < 0.6 and k > 0: s = r1[0]
        st = T[c]["voice_start"] + s - 0.08; en = T[c]["voice_start"] + e + 0.25
        CAPS.append({"cut": c, "text": p, "start": round(st, 3), "end": round(en, 3)})
for a, b in zip(CAPS, CAPS[1:]):  # 한 번에 한 자막만
    if a["end"] > b["start"] - 0.02: a["end"] = round(b["start"] - 0.02, 3)

# 4) 소리 배치
sfx_dir = f"{A}/sfx"
g_tv = gain(T_TV, loud(f"{sfx_dir}/tv_a.mp3"))
d_media = 6.0  # 낮은 음은 조용한 도입을 지나 6초 지점부터
g_drone = gain(T_DRONE, loud(f"{sfx_dir}/drone_a.mp3", d_media, 40))
AUD = []
MASTER = 0.74  # 전체 -2.6dB: 한 채널 음성이 렌더에서 좌우 두 채널로 복사돼 약 +3dB로 재지므로, 렌더 결과를 -16~-14 LUFS에 맞춘다(2026-11-23 첫 렌더 -13.2 LUFS 확인)
def aud(id_, src, start, dur, vol, media=0.0, fin=0.0, fout=0.0, lane=11):
    vol = round(vol * MASTER, 3)
    AUD.append(dict(id=id_, src=src, start=round(start, 3), dur=round(dur, 3), vol=vol, media=round(media, 3), fin=fin, fout=fout, lane=lane))
for c in [c for c in CUTS if c not in SILENT]: aud(f"v-{c}", f"assets/voice/{c}.wav", T[c]["voice_start"], T[c]["voice_dur"], 1, lane=10)
sil0, sil1 = T["C04"]["start"] + 0.4, T["C04"]["start"] + T["C04"]["dur"]  # C04 바스락 뒤 정적
c07 = T["C07"]["start"] - DISSOLVE["C07"]
aud("tv-1", "assets/sfx/tv_a.mp3", 0, sil0 + 0.15, g_tv, 0, 1.0, 0.3, 12)
aud("tv-2", "assets/sfx/tv_a.mp3", sil0 - 0.15, sil1 - sil0 + 0.3, round(g_tv * 0.15, 3), sil0 - 0.15, 0.3, 0.3, 13)  # 정적: 거의 안 들리게
aud("tv-3", "assets/sfx/tv_a.mp3", sil1 - 0.15, c07 + 0.6 - (sil1 - 0.15), g_tv, sil1 - 0.15, 0.4, 0.6, 12)
aud("drone", "assets/sfx/drone_a.mp3", c07, TOTAL - c07, g_drone, d_media, 1.0, 1.0, 14)
BAG = {  # (컷, 컷 안 시작, 파일 구간 시작, 끝, 끝 페이드)
 "bag-c02": ("C02", 0.0, 0.25, 1.20, 0.15), "bag-c03": ("C03", 0.05, 2.10, 2.55, 0.03),
 "bag-c04": ("C04", 0.0, 4.80, 5.60, 0.15), "bag-c06a": ("C06", 0.3, 11.85, 12.35, 0.1),
 "bag-c06b": ("C06", 2.3, 13.35, 13.95, 0.1), "bag-c06c": ("C06", 4.3, 16.55, 17.10, 0.1), "bag-c06d": ("C06", 6.3, 17.30, 17.85, 0.1)}
for k, (c, off, m0, m1, fo) in BAG.items():
    aud(k, "assets/sfx/bag_b.mp3", T[c]["start"] + off, m1 - m0, gain(T_SFX_TV, loud(f"{sfx_dir}/bag_b.mp3", m0, m1 - m0, True)), m0, 0.02, fo, 11)
aud("crunch-c09", "assets/sfx/crunch_a.mp3", T["C09"]["start"] + 0.2, 1.2, gain(T_SFX_DRONE, loud(f"{sfx_dir}/crunch_a.mp3", 0, 1.2, True)), 0, 0.0, 0.3, 11)

# 5) HTML 쓰기
def pictures():
    clips, js, z = [], [], 1
    for c in CUTS:
        st, du = T[c]["start"], T[c]["dur"]
        if c in DISSOLVE: st, du = st - DISSOLVE[c], du + DISSOLVE[c]
        clips.append(f'    <div id="p-{c}" class="clip pic" data-start="{st:.3f}" data-duration="{du:.3f}" data-track-index="1" style="z-index:{z}"><img id="img-{c}" src="assets/img/{c}.jpg" alt="{c}"></div>')
        kind, amt = MOTION[c]
        if kind == "push": js.append(f'tl.fromTo("#img-{c}", {{ scale: 1 }}, {{ scale: {amt}, duration: {du:.3f}, ease: "none" }}, {st:.3f});')
        if kind == "pan": js.append(f'tl.fromTo("#img-{c}", {{ scale: {1 + 2 * amt:.3f}, xPercent: {amt * 100:.2f} }}, {{ scale: {1 + 2 * amt:.3f}, xPercent: {-amt * 100:.2f}, duration: {du:.3f}, ease: "none" }}, {st:.3f});')
        if c == "C01": js.append(f'tl.fromTo("#img-C01", {{ opacity: 0 }}, {{ opacity: 1, duration: {LEAD["C01"]}, ease: "none" }}, 0);')
        if c in DISSOLVE: js.append(f'tl.fromTo("#img-{c}", {{ opacity: 0 }}, {{ opacity: 1, duration: {DISSOLVE[c]}, ease: "none" }}, {st:.3f});')
        if c == CUTS[-1]: js.append(f'tl.fromTo("#img-{c}", {{ opacity: 1 }}, {{ opacity: 0, duration: {FADE_END}, ease: "none" }}, {TOTAL - FADE_END - 0.04:.3f});')
        z += 1
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; background: #000; overflow: hidden; }}
    .pic {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden; }}
    .pic img {{ display: block; width: 1920px; height: 1080px; object-fit: cover; }}
  </style>
  <div id="root" data-composition-id="pictures" data-width="1920" data-height="1080">
{chr(10).join(clips)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js)}
    window.__timelines["pictures"] = tl;
  </script>
</template>
"""

def captions():
    groups, js = [], []
    for i, cp in enumerate(CAPS):
        gid = f"cap-{i:02d}"; du = cp["end"] - cp["start"]
        groups.append(f'    <div id="{gid}" class="clip cap" data-start="{cp["start"]:.3f}" data-duration="{du:.3f}" data-track-index="2"><span id="{gid}-t" class="cap-t">{html.escape(cp["text"])}</span></div>')
        js.append(f'tl.fromTo("#{gid}-t", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "power2.out" }}, {cp["start"]:.3f});')
        js.append(f'tl.to("#{gid}-t", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, {cp["end"] - 0.12:.3f});')
        js.append(f'tl.set("#{gid}-t", {{ opacity: 0, visibility: "hidden" }}, {cp["end"]:.3f});')
    return f"""<template>
  <style>
    @font-face {{ font-family: "Pretendard"; src: url('assets/fonts/Pretendard-Medium.otf'); font-weight: 500; }}
    #root {{ position: absolute; inset: 0; }}
    .cap {{ position: absolute; left: 0; right: 0; bottom: 96px; text-align: center; overflow: visible; }}
    .cap-t {{
      display: inline-block; max-width: 1560px; padding: 10px 30px 13px; border-radius: 6px;
      background: rgba(18, 16, 14, 0.62); color: #F3EBDD;
      font-family: "Pretendard", sans-serif; font-weight: 500; font-size: 54px; line-height: 1.38; letter-spacing: -0.01em;
      word-break: keep-all;
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1920" data-height="1080">
{chr(10).join(groups)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""

def index():
    audios = "\n".join(
        f'      <audio id="{a["id"]}" class="clip" src="{a["src"]}" data-start="{a["start"]:.3f}" data-duration="{a["dur"]:.3f}" data-media-start="{a["media"]:.3f}" data-volume="{a["vol"]}"'
        + (f' data-fade-in="{a["fin"]}"' if a["fin"] else "") + (f' data-fade-out="{a["fout"]}"' if a["fout"] else "") + f' data-track-index="{a["lane"]}"></audio>'
        for a in AUD)
    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <!-- 먹는마음 수프·팝콘 편 1분 시험 영상(C01~C11). build.py가 만든다: 고칠 때는 build.py를 고치고 다시 실행한다. -->
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #root {{ width: 100%; height: 100%; position: relative; background: #000; }}
      #pictures {{ z-index: 1; }}
      #captions {{ z-index: 2; }}  /* 자막이 그림 위에 오도록(쌓는 순서는 z-index) */
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080">
      <div id="pictures" data-composition-id="pictures" data-composition-src="compositions/pictures.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="2" data-track-kind="captions" data-width="1920" data-height="1080"></div>
{audios}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

os.makedirs(f"{HERE}/compositions", exist_ok=True)
open(f"{HERE}/compositions/pictures.html", "w").write(pictures())
open(f"{HERE}/compositions/captions.html", "w").write(captions())
open(f"{HERE}/index.html", "w").write(index())
json.dump({"total": TOTAL, "cuts": T, "captions": CAPS, "audio": AUD}, open(f"{HERE}/timing.json", "w"), ensure_ascii=False, indent=1)
print(f"전체 {TOTAL:.1f}초, 자막 {len(CAPS)}개, 소리 {len(AUD)}개 (TV 볼륨 {g_tv}, 낮은 음 볼륨 {g_drone})")
for c in CUTS: print(f"  {c} {T[c]['start']:6.2f}s +{T[c]['dur']:.2f}s  {MOTION[c][0]}")
