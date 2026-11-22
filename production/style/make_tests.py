# 그림체 시험 그림을 gpt-image-2(codex, tools/gen-ref.sh, 참조 그림 없이)로 그린다 → tests/<VER>/
# 문구는 style_guide.md의 "프롬프트 문구"와 같다. 고칠 때는 두 곳을 함께 고친다. 지난 판의 문구는 tests/<판>/*.prompt.txt에 남아 있다.
# 실행: python3 production/style/make_tests.py [s1a s2a ...]   (이미 있는 파일은 건너뛴다)
# codex 기본 모델(gpt-6.2-sol)은 ChatGPT 계정에서 안 돼서 CODEX_MODEL로 gpt-6.1-sol을 지정한다(2026-11-22 확인).
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

VER = "v3"  # v1: a 동판화/b 목판화 6장. v2: a로 정함, 검정 먹선·연한 크림·탁한 주홍·화면 전체 종이 질감. v3: 주홍을 무광 붉은 주황 잉크로 고정 + 겹칠 종이 질감(paper).
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tests", VER); os.makedirs(OUT, exist_ok=True)
GEN = os.path.join(HERE, "..", "..", "tools", "gen-ref.sh")
ENV = dict(os.environ, CODEX_MODEL=os.environ.get("CODEX_MODEL", "gpt-6.1-sol"))

COMMON = ("Original illustration in the manner of fine-art printmaking: neutral black ink (true black, never brown or sepia) printed on pale cream paper. "
 "Strong chiaroscuro with deep blacks and bright paper whites; all shading is built from hatching and cross-hatching lines, never painted fills or smooth gradients. "
 "Exactly ONE accent color: a matte red-orange printing ink (vermilion, around #D2452B), opaque and flat like screen-print ink; never pink, never salmon, never brown, never neon. "
 "It is used only on the single thing that pulls attention in the scene; everything else stays black ink on cream paper. "
 "Adults have realistic proportions; faces are partly hidden in shadow, cropped or turned away. "
 "Calm, slightly uncanny stillness: tension comes from light, shadow and composition, never horror or gore, and the eater is never shown as guilty, ugly or sinful. "
 "Any visible setting is an ordinary modern Korean home.")
PAPER = ("Paper texture over the WHOLE frame: the image looks printed on real handmade paper, with fine paper grain and faint fibers visible everywhere, "
 "including through the black ink areas and the vermilion, with slight ink unevenness where the ink meets the paper.")
NOTEXT = "No text, letters, numbers, logos, labels or brand marks anywhere; packaging and papers show only blank shapes."
VARIANT = {
 "a": ("Hatching treatment: copperplate etching / steel engraving. Very fine, dense parallel lines and cross-hatching that follow the form; "
       "even large planes such as walls, tablecloth, sky and background are filled with fine parallel line tones. Crisp, meticulous, highly detailed. "
       "Shadows are deep and wide: build broad, strong black areas from very dense cross-hatching so the darks read boldly."),
 "b": ("Hatching treatment: woodcut / wood engraving. Large solid black areas with white lines carved out of them, bold gouged strokes, "
       "fewer but thicker lines, very high contrast, slightly rough hand-carved edges."),
}
FULL = "Compose the scene to fill the entire 16:9 frame edge to edge: no blank margins, no border, no frame."
OBJ = ("No background scene: the subject sits alone on plain cream paper with generous empty paper around it, "
       "like a printed specimen plate, with a soft hatched shadow beneath it.")

SCENES = {
 "s1": (FULL, "Scene: a family dining table at night, seen close and from a low angle. A large opened snack bag (plain, no printing) lies on its side on the table, "
        "half empty, its crinkled foil catching the light, a few crumbs around it. Exactly one adult hand and forearm enter from the lower-right edge of the frame "
        "and reach into the bag again, fingertips just disappearing inside; the person's body and face are out of frame. A single pendant lamp makes a pool of light on the table; "
        "the rest of the room falls into deep hatched shadow. The snack pieces at the bag's mouth are the only vermilion."),
 "s2": (OBJ, "Subject: a cutaway cross-section diagram, like an engraved scientific plate. A soup bowl on a small section of table is cut in half to show its inside; "
        "hidden under the table, a soup reservoir connects through a thin tube up into the bottom of the bowl, quietly refilling it so the bowl never empties. "
        "The flow must clearly read as going UP, from the reservoir into the bowl: inside the tube draw small engraved upward-pointing arrowheads and little bubbles rising upward, "
        "and the bowl stays full to the brim. Nothing drips or pours down. "
        "A spoon rests in the bowl. No people. The soup in the bowl, tube and reservoir is the only vermilion."),
 "s3": (OBJ, "Subject: a symbolic still life of three objects in a row with balanced spacing, like an engraved emblem plate: "
        "(1) a simplified anatomical stomach in the manner of an old medical engraving, calm and not gory, standing for the body's signal; "
        "(2) a large heaped bowl of popcorn, standing for the amount in front of you; "
        "(3) a small plate holding just one small handful of the same popcorn, with a single small round dot pressed into its rim like a full stop, standing for an amount decided in advance. "
        "No labels. Only the popcorn (in the bowl and on the plate) is vermilion."),
}

# 모든 그림 위에 겹칠 종이 질감(tools/paper_overlay.py가 씀). 그림체 문구 없이 종이만.
PAPER_SHEET = ("A flat, evenly lit high-resolution scan of a single sheet of pale cream handmade paper filling the entire 16:9 frame edge to edge. "
 "Visible fine paper grain, faint fibers and very subtle mottling, evenly spread over the whole sheet. "
 "No folds, no creases, no shadows, no vignette, no border, no objects, no ink, no text; uniform brightness from corner to corner.")

def job(name):
    out = os.path.join(OUT, f"{name}.png")
    if os.path.exists(out): return f"{name}: skip (exists)"
    if name == "paper":
        prompt = PAPER_SHEET
    else:
        frame, scene = SCENES[name[:2]]
        prompt = " ".join([COMMON, PAPER, VARIANT[name[2]], frame, scene, NOTEXT])
    with open(os.path.join(OUT, f"{name}.prompt.txt"), "w") as f: f.write(prompt + "\n")
    r = subprocess.run([GEN, "", prompt, out], capture_output=True, text=True, env=ENV)
    with open(os.path.join(OUT, f"{name}.log"), "w") as f: f.write(r.stdout + r.stderr)
    return f"{name}: {'ok' if r.returncode == 0 and os.path.exists(out) else 'FAIL (see .log)'}"

if __name__ == "__main__":  # production/visual-cues/v4/make_cuts.py가 위 문구를 가져다 쓴다
    names = sys.argv[1:] or [s + "a" for s in SCENES] + ["paper"]
    with ThreadPoolExecutor(3) as ex:
        for line in ex.map(job, names): print(line, flush=True)
