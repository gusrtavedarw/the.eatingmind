# 수프·팝콘 편 내레이션을 VoiceStudio '구스타브 v2' 프로필(OmniVoice)로 컷마다 만든다(2026-11-23 합의).
# 컷 안의 문장은 하나씩 만들어 0.45초 쉼으로 잇고, breath.py로 문장 앞 숨을 지운 뒤 -16 LUFS로 맞춘다. 마지막에 받아쓰기로 대본과 대조한다.
# 실행: VoiceStudio venv python narrate.py [--seed N] C01 C04 ...   (이미 있는 컷은 건너뛴다. 다시 만들려면 out/raw/<컷>.wav를 지운다)
# 받아쓰기에서 틀리게 읽힌 컷은 시드만 바꿔 다시 만든다(같은 시드는 같은 소리가 나온다).
import io, json, os, re, subprocess, sys
import numpy as np, requests, soundfile as sf, librosa

G = os.path.dirname(os.path.abspath(__file__))
CONTI = os.path.join(G, "..", "storyboard", "review", "conti.json")
PROFILE, SR, GAP = "b8e9ff0b", 24000, 0.45
PY = sys.executable
RAW, FIN = f"{G}/out/raw", f"{G}/out/final"; os.makedirs(RAW, exist_ok=True); os.makedirs(FIN, exist_ok=True)
SEED = "42"
args = sys.argv[1:]
if args[:1] == ["--seed"]: SEED, args = args[1], args[2:]
cuts = {c["id"]: c for s in json.load(open(CONTI))["sections"] for c in s["cuts"]}

def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]

def tts(text):
    r = requests.post("http://localhost:3900/generate", data={"text": text, "language": "Korean", "profile_id": PROFILE, "engine": "omnivoice", "seed": SEED, "denoise": "false"}, timeout=900)
    r.raise_for_status()
    y, sr = sf.read(io.BytesIO(r.content), dtype="float32")
    if y.ndim > 1: y = y.mean(axis=1)
    return librosa.resample(y, orig_sr=sr, target_sr=SR) if sr != SR else y

for cid in args:
    raw, fin = f"{RAW}/{cid}.wav", f"{FIN}/{cid}.wav"
    if not os.path.exists(raw):
        parts = []
        for s in sentences(cuts[cid]["text"]):
            parts += [tts(s), np.zeros(int(SR * GAP), dtype="float32")]
        sf.write(raw, np.concatenate(parts[:-1]), SR)
    subprocess.run([PY, f"{G}/breath.py", raw, fin, "cut"], check=True, capture_output=True)
    # 앞뒤 무음을 0.05초만 남기고 자른다(컷 길이는 조립할 때 맞춘다)
    y, sr = sf.read(fin, dtype="float32")
    nz = np.nonzero(np.abs(y) > 10 ** (-50 / 20))[0]
    a, b = max(0, nz[0] - int(sr * 0.05)), min(len(y), nz[-1] + int(sr * 0.05))
    sf.write(fin, y[a:b], sr)
    print(cid, f"{(b - a) / sr:.2f}s", flush=True)
