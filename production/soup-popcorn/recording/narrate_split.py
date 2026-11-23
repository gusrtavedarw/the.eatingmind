# 한 문장이 두 컷에 걸친 곳(예: C02·C03)은 문장 전체를 한 번에 만들고, 받아쓰기 단어 시간으로 쉼표 뒤 쉼 가운데에서 두 컷으로 나눈다(2026-11-23 합의).
# 숨 처리·음량은 narrate.py와 같다(breath.py cut, -16 LUFS). 잘린 끝은 10ms로 줄이고, 조각마다 앞뒤 무음은 0.05초만 남긴다.
# 실행: VoiceStudio venv python narrate_split.py [--seed N] C02,C03 C07,C08
import io, json, os, re, subprocess, sys
import numpy as np, requests, soundfile as sf, librosa
from mlx_audio.stt.utils import load_model

G = os.path.dirname(os.path.abspath(__file__))
CONTI = os.path.join(G, "..", "storyboard", "review", "conti.json")
PROFILE, SR = "b8e9ff0b", 24000
SEED = "42"; args = sys.argv[1:]
if args[:1] == ["--seed"]: SEED, args = args[1], args[2:]
RAW, FIN = f"{G}/out/raw", f"{G}/out/final"; os.makedirs(RAW, exist_ok=True); os.makedirs(FIN, exist_ok=True)
cuts = {c["id"]: c for s in json.load(open(CONTI))["sections"] for c in s["cuts"]}
asr = load_model("mlx-community/whisper-large-v3-turbo-asr-fp16")

def trim_save(y, sr, path, fade_in, fade_out):
    nz = np.nonzero(np.abs(y) > 10 ** (-50 / 20))[0]
    a, b = max(0, nz[0] - int(sr * 0.05)), min(len(y), nz[-1] + int(sr * 0.05))
    y = y[a:b].copy(); k = int(sr * 0.01)
    if fade_in: y[:k] *= np.linspace(0, 1, k)
    if fade_out: y[-k:] *= np.linspace(1, 0, k)
    sf.write(path, y, sr); return len(y) / sr

for pair in args:
    first, second = pair.split(",")
    head = cuts[first]["text"].strip()
    text = head + " " + cuts[second]["text"].strip()
    raw, whole = f"{RAW}/{first}_{second}.wav", f"{FIN}/{first}_{second}.wav"
    if not os.path.exists(raw):
        r = requests.post("http://localhost:3900/generate", data={"text": text, "language": "Korean", "profile_id": PROFILE, "engine": "omnivoice", "seed": SEED, "denoise": "false"}, timeout=900)
        r.raise_for_status()
        y, sr = sf.read(io.BytesIO(r.content), dtype="float32")
        if y.ndim > 1: y = y.mean(axis=1)
        sf.write(raw, librosa.resample(y, orig_sr=sr, target_sr=SR) if sr != SR else y, SR)
    subprocess.run([sys.executable, f"{G}/breath.py", raw, whole, "cut"], check=True, capture_output=True)
    y, sr = sf.read(whole, dtype="float32")
    words = [w for s in asr.generate(whole, language="ko", word_timestamps=True).segments for w in s.get("words", [])]
    # 앞 컷 글자 수만큼 받아쓰기 단어를 세어 경계를 찾는다(쉼표가 받아쓰기에 없을 수 있어서 글자 수로 맞춘다)
    n_head = len(re.sub(r"[^가-힣]", "", head)); count, k = 0, 0
    while k < len(words) and count < n_head:
        count += len(re.sub(r"[^가-힣]", "", words[k]["word"])); k += 1
    if k == 0 or k >= len(words): raise SystemExit(f"{pair}: 경계를 찾지 못함 {[w['word'] for w in words]}")
    guess = (words[k - 1]["end"] + words[k]["start"]) / 2
    # 받아쓰기 단어 시간은 실제보다 앞서거나 붙어 나올 수 있다(2026-11-23 확인) → 추정 경계 -0.3~+0.5초 안에서 50ms 평균이 가장 조용한 곳에서 자른다
    hop = int(sr * 0.01)
    a, b = max(0, int((guess - 0.3) * sr)), min(len(y) - hop, int((guess + 0.5) * sr))
    db = np.array([20 * np.log10(np.sqrt(np.mean(y[j:j + hop] ** 2)) + 1e-9) for j in range(a, b, hop)])
    sm = np.convolve(db, np.ones(5) / 5, mode="same")
    cut_t = (a + int(np.argmin(sm)) * hop) / sr
    i = int(cut_t * sr)
    d1 = trim_save(y[:i], sr, f"{FIN}/{first}.wav", False, True)
    d2 = trim_save(y[i:], sr, f"{FIN}/{second}.wav", True, False)
    print(f"{pair}: 나눈 곳 {cut_t:.2f}s ('{words[k-1]['word'].strip()}' | '{words[k]['word'].strip()}'), 쉼 {words[k]['start'] - words[k-1]['end']:.2f}s, {first} {d1:.2f}s, {second} {d2:.2f}s", flush=True)
