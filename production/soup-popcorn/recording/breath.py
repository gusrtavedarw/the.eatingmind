# 구스타브 복제 내레이션의 숨소리 처리(2026-11-23 합의).
# 문장(컷) 음성마다 첫 유성음 앞의 들숨과, 문장 안 쉼(쉼표 뒤 등)의 숨을 찾아 지우거나(cut) 약 18dB 줄인다(soft).
# 이음매는 15ms로 부드럽게 잇고, 마지막에 음량을 -16 LUFS(순간 최대 -1.5dBTP), 48kHz로 맞춘다. 다른 후처리는 하지 않는다.
# 넣어 둔 완전 무음(0.2초 이상)으로 문장을 나눠 문장마다 따로 처리한다.
# 실행: VoiceStudio venv python breath.py <입력.wav> <출력.wav> cut|soft [--report]
import subprocess, sys, tempfile
import numpy as np, soundfile as sf, librosa

inp, out, mode = sys.argv[1:4]
report = "--report" in sys.argv
GAIN = 0.0 if mode == "cut" else 10 ** (-18 / 20)
y, sr = sf.read(inp, dtype="float32")
if y.ndim > 1: y = y.mean(axis=1)
hop = int(sr * 0.01); fade = int(sr * 0.015)

def chunks(y):
    z = np.abs(y) < 1e-7; out, i, start = [], 0, 0
    while i < len(y):
        if z[i]:
            j = i
            while j < len(y) and z[j]: j += 1
            if j - i >= int(sr * 0.2):
                if i > start: out.append((start, i))
                start = j
            i = j
        else: i += 1
    if start < len(y): out.append((start, len(y)))
    return out

def breaths(seg):
    """문장 하나에서 숨 구간(샘플 단위)을 찾는다."""
    rms = librosa.feature.rms(y=seg, frame_length=hop * 2, hop_length=hop)[0]
    db = 20 * np.log10(rms + 1e-9)
    f0, vflag, _ = librosa.pyin(seg, fmin=65, fmax=350, sr=sr, frame_length=hop * 4, hop_length=hop)
    flat = librosa.feature.spectral_flatness(y=seg, n_fft=hop * 4, hop_length=hop)[0]
    cent = librosa.feature.spectral_centroid(y=seg, sr=sr, n_fft=hop * 4, hop_length=hop)[0]
    n = min(len(db), len(vflag), len(flat), len(cent)); db, vflag, flat, cent = db[:n], vflag[:n], flat[:n], cent[:n]
    sp = np.percentile(db, 95)
    found = []
    # 1) 첫 유성음(3프레임 이상 이어지는 곳) 앞의 들숨
    v_on = next((i for i in range(n - 3) if vflag[i:i + 3].all()), None)
    e_on = next((i for i in range(n - 3) if (db[i:i + 3] > sp - 18).all()), None)  # 말소리 크기로 잡은 시작(숨은 이보다 작다)
    onset = min(x for x in (v_on, e_on) if x is not None) if (v_on or e_on) else None
    if onset and onset > 5:
        end = max(0, onset - 3)  # 첫 소리 30ms 앞까지
        if end > 0 and db[:end].max() > sp - 45: found.append((0, end, "첫 숨"))
    # 2) 문장 안 숨: 유성음 사이의 무성 잡음 0.12초 이상, 말소리보다 12~40dB 작고, 소리가 낮게 퍼진 것(치찰음 ㅅ·ㅆ 제외)
    i = (onset or 0) + 3
    while i < n:
        if not vflag[i] and sp - 40 < db[i] < sp - 12 and flat[i] > 0.01 and cent[i] < 3500:
            j = i
            while j < n and not vflag[j] and db[j] < sp - 10: j += 1
            # 0.2초 이상만 숨으로 보고, 다음 소리 80ms 앞에서 멈춘다(쉼표 뒤 ㅅ·ㅎ 같은 첫소리를 깎지 않게. 2026-11-23 C06 '손은'에서 확인)
            if j - i >= 20 and j < n: found.append((i, j - 8, "문장 안 숨"))
            i = j
        else: i += 1
    return [(a * hop, b * hop, why) for a, b, why in found]

res = y.copy(); log = []
for s, e in chunks(y):
    for a, b, why in breaths(y[s:e]):
        A, B = s + a, s + b
        env = np.full(B - A, GAIN, dtype="float32")
        k = min(fade, (B - A) // 2)
        env[:k] = np.linspace(1, GAIN, k); env[-k:] = np.linspace(GAIN, 1, k)
        res[A:B] *= env
        log.append(f"{why} {A / sr:5.2f}~{B / sr:5.2f}s")
with tempfile.NamedTemporaryFile(suffix=".wav") as t:
    sf.write(t.name, res, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", t.name, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "1", out], check=True)
if report: print("\n".join(log) or "숨 없음")
