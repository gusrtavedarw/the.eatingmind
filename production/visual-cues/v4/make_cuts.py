# 콘티(콘티.md)의 컷 그림을 gpt-image-2(codex, tools/gen-ref.sh)로 그린다 → cuts/
# 그림체 문구는 production/style/make_tests.py에서 가져온다(세 번째 사본을 만들지 않음). 순서는 style_guide.md "앞으로 그릴 때"를 따른다.
# 컷마다: 그리기(<컷>.png) → 종이 질감 세기 2(<컷>_paper.png, 본 컷) → 검수(<컷>.check.txt) → 마지막에 비교 화면(compare.jpg, 저장소 기록이 덜 늘게 JPEG).
# 실행: python3 production/visual-cues/v4/make_cuts.py [C01 C14 ...]   (이미 있는 파일은 건너뛴다. 다시 그리려면 그 컷의 png를 지운다)
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "production", "style"))
from make_tests import COMMON, PAPER, NOTEXT, VARIANT, FULL, OBJ, GEN, ENV  # noqa: E402

OUT = os.path.join(HERE, "cuts"); os.makedirs(OUT, exist_ok=True)
STYLE_REFS = [os.path.join(ROOT, "production", "style", "refs", f) for f in ("style_scene.png", "style_object.png")]
PAPER_PNG = os.path.join(ROOT, "production", "style", "refs", "paper.png")
OVERLAY = os.path.join(ROOT, "tools", "paper_overlay.py")
CHECK = os.path.join(ROOT, "tools", "check-img.sh")
STYLE = "Match the drawing style of the last two reference images (ignore their subjects)."
# 자막 자리(콘티 '정한 것'의 자막 자리, 2026-11-22 C45 시험 뒤 더함). 구성에 따라 프롬프트와 검수 기준에 붙인다.
SUB = {FULL: "Keep the vermilion subject and the key objects out of the bottom quarter of the frame (subtitles go there); only background such as the table surface or the floor may fill that strip.",
       OBJ: "Keep the whole lower third of the image empty cream paper (subtitles go there); the subject sits in the upper two thirds."}
SUB_BRIEF = {FULL: "\n- the vermilion element is not in the bottom quarter of the image", OBJ: "\n- the lower third of the image is empty paper"}

# 컷: (이름표, 구성, 앞 참조(컷 번호 또는 저장소 경로), 장면, 검수 기준)
CUTS = {
 "C01": ("C01 오프닝 첫 화면", FULL, [],
  "Scene (opening shot): a living room at night. Extreme close-up at table height, looking straight into the open mouth of a plain foil snack bag (no printing) "
  "that lies fallen on its side on a low coffee table in front of a sofa. Inside the bag, in the shadowed hollow, only ONE last twisted snack piece remains "
  "(the same twisted puffed snack shape as in the scene reference); there are no other pieces in or out of the bag, only a few tiny crumbs. "
  "The only light is the cold glow of a television outside the frame to the left: it catches the crinkled foil as thin, bright, sharp streaks of bare paper white "
  "between dense hatching, with no color. No ceiling lamp. No people and no hands. Everything else sinks into deep cross-hatched darkness. "
  "The single remaining snack piece is the only vermilion.",
  "- no people, no hands or arms\n- a plain opened foil snack bag lying on its side, seen up close at its open mouth\n"
  "- inside the bag exactly ONE snack piece remains, and it is the only vermilion element\n- the light streaks on the foil are not colored\n- no lamp visible"),
 "C14": ("C14 수프 실험 단면도", OBJ, ["production/style/tests/v3/s2a.png"],
  "Subject (soup experiment): a cutaway cross-section diagram like an engraved scientific plate. The FIRST reference image is an earlier drawing of this same cutaway: "
  "keep its design, but draw the whole diagram smaller so that the bowl, table, tube and reservoir all fit in the upper two thirds of the image. A soup bowl sits on a section of table, cut in half to show its inside; hidden under the table, a soup reservoir connects through a thin tube "
  "up into the bottom of the bowl, quietly refilling it so the bowl never empties. The flow must clearly read as going UP: inside the tube draw a few small engraved "
  "upward-pointing arrowheads and little round bubbles rising upward, and the bowl stays full to the brim. Nothing drips or pours down. A spoon rests in the bowl. "
  "No people. The soup in the bowl, tube and reservoir is the only vermilion.",
  "- a soup bowl on a table, cut in half\n- a reservoir under the table connected by a tube up into the bottom of the bowl\n"
  "- upward arrowheads and rising bubbles inside the tube; nothing drips down\n- the bowl is full; a spoon rests in it\n- no people\n- only the soup is vermilion"),
 "C45": ("C45 핵심 그림", OBJ, [],
  "Subject (key concept plate): an engraved emblem plate with two objects and two lines. Upper left: a simplified anatomical stomach in the manner of an old medical "
  "engraving (the same stomach style as in the object reference), calm and not gory, kept small in the upper left area. Upper right, at the same height: a plain ceramic "
  "soup bowl with a little soup in it, drawn in black ink only, also kept small. From the bottom of the stomach one thin, fine engraved line slants down to the right, "
  "and from the bottom of the bowl another thin, fine line slants down to the left; the two lines meet at a clear angle, forming a V, at one single solid round dot "
  "placed at the exact center of the image (half way down), like a full stop. The dot is small but clearly visible, a little thicker than the lines. "
  "The two lines never form one straight line, and they end exactly at the dot. The whole lower third of the image is empty cream paper (subtitles go there). "
  "No arrows, no other marks. No people. The round dot is the only vermilion; everything else is black ink.",
  "- an anatomical stomach on the upper left\n- a soup bowl on the upper right\n- exactly two thin lines, one from the stomach and one from the bowl, slanting down and meeting at an angle (a V shape, not one straight line) at one round dot near the middle of the image\n"
  "- the dot is above the lower third of the image; the lower third is empty paper\n"
  "- the dot is the only vermilion element; the soup is not vermilion\n- no people, no arrows"),
 "C63": ("C63 결말, 처음 보이는 몸", FULL, ["C01"],
  "Scene (the same night, seen wider): a living room at night. The FIRST reference image is the opening close-up of this same night: keep the same foil snack bag, "
  "the same crumbs and the same cold TV light, but the last snack piece is gone. Now the view is wide, from behind and slightly above a low sofa. For the first time a person's body is seen: "
  "exactly one adult sitting on the sofa, seen from behind, a dark cross-hatched silhouette of the back of the head, neck, shoulders and back in a short-sleeved T-shirt; "
  "the face is not visible. Across the room in front of them a switched-on television glows: the screen is a blank bright rectangle of bare paper white with nothing "
  "shown on it, and its cold light rims the person's outline and falls on a low coffee table between the sofa and the TV. The opened foil snack bag lies on its side "
  "on that coffee table. The person's bare right arm comes from their right shoulder (image right) and reaches forward and down; the right hand rests at the mouth "
  "of the bag, fingertips just inside. The left arm stays down at their side, hidden by the body. The head is turned toward the TV screen, not toward the bag. "
  "The bag is already empty: its inside is a dark hatched hollow and the hand reaches into darkness. No whole snack pieces are left anywhere, "
  "only a few tiny crumbs at the bag's mouth and on the table. Everything else sinks into deep hatched darkness. "
  "Those few tiny crumbs are the only vermilion; the TV light is never colored.",
  "- exactly one person, seen from behind, sitting on a sofa; the face is not visible\n- short sleeves; one bare right arm from the image-right shoulder reaches to a snack bag on a low table, the hand at the bag's mouth\n"
  "- a switched-on TV in front of the person; the screen is blank light with no picture\n- the head faces the TV, not the bag\n"
  "- the bag is empty and dark inside: no whole snack pieces anywhere, only tiny crumbs\n- only the tiny crumbs are vermilion; the TV light is not vermilion"),
 "C11": ("C11 예상해 보기 · 줄어드는 접시", OBJ, [],
  "Subject (the video's question): an engraved specimen plate of three identical plain round plates in one horizontal row with even spacing, seen from slightly above. "
  "The left plate is heaped full of twisted puffed snack pieces (the same twisted snack shape as in the scene reference), the middle plate holds about half as many, "
  "and the right plate holds only three or four pieces with a few crumbs. The three plates are identical in size and shape; only the amount changes from left to right. "
  "No hands, no people. The snack pieces are the only vermilion.",
  "- exactly three identical plates in a row\n- the left plate is full of snack pieces, the middle about half, the right only three or four pieces\n"
  "- no people or hands\n- only the snack pieces are vermilion"),
 "C23": ("C23 독립 재현 · 그릇 수백 개", OBJ, [],
  "Subject (a replication study with several hundred participants): an engraved specimen plate showing many rows of tiny identical soup bowls seen from slightly above, "
  "arranged in a tight, orderly grid like a printed specimen sheet, several hundred bowls in all, each filled with soup. The grid forms one neat rectangular block. "
  "Every bowl stays a separate, readable little bowl. No people, no hands, no table. The soup in the bowls is the only vermilion.",
  "- many rows of tiny identical soup bowls (hundreds) in an orderly grid\n- each bowl holds soup and the soup is the only vermilion\n- no people or hands\n"
  "- the bowls stay readable as separate bowls and do not melt into a texture"),
 "C28": ("C28 팝콘 · 영화관", FULL, [],
  "Scene (the popcorn study): the inside of a dark movie theater, seen from behind and slightly above the back rows. Rows of tall upholstered seat backs fill the frame "
  "in deep cross-hatched darkness; the seat backs hide everyone, so no people, heads or hands are visible. A single projector light beam, drawn as fine parallel lines "
  "of bare paper white, cuts diagonally across the frame above the rows toward a screen at the far end; the screen is a blank pale rectangle with nothing on it. "
  "On one armrest in the middle distance sits a plain paper popcorn tub (no printing), lit by the spill of the beam; the popcorn in that tub is small in the frame "
  "and is the only vermilion.",
  "- a dark movie theater seen from behind the rows of seats\n- no people, heads or hands visible\n- a projector beam crosses the frame; the screen is blank\n"
  "- one plain popcorn tub on an armrest; only its popcorn is vermilion"),
 "C56": ("C56 적용 · 함께 먹는 식탁", FULL, [],
  "Scene (eating together): a shared family dinner table seen from above at an angle, in a modern Korean home in the evening. In the center sits one large plate of "
  "Korean savory pancakes (jeon) cut into pieces, surrounded by small side-dish plates, rice bowls and a water glass. Four hands, each belonging to a different person, "
  "reach in toward the center plate from different edges of the frame (two from the top edge, one from the left edge, one from the right edge); each hand holds one pair "
  "of flat metal chopsticks and is picking up a piece of jeon. Each hand has five fingers and one clear arm in a plain sleeve running straight to the frame edge; "
  "the bodies and faces stay outside the frame. The jeon on the central plate is the only vermilion.",
  "- exactly four hands, each holding one pair of chopsticks, each with one arm running continuously to a frame edge (the bodies are outside the frame, which is expected)\n"
  "- no faces or bodies visible\n- one large central plate of jeon (savory pancake pieces); only that food is vermilion\n- no extra or floating hands, no chopsticks without a hand"),
 "C68": ("C68 작은 관찰 · 아침 식탁", FULL, [],
  "Scene (a morning after the meal): a small dining table by a window in the morning, in a modern Korean apartment. Morning sunlight comes through the window from the left "
  "and lays long bright shapes of bare paper white across the table; the rest is fine hatching, lighter and calmer than a night scene. On the table: a rice bowl with "
  "a little rice left, two or three small side-dish plates, and a spoon and chopsticks laid down beside them. In one small side dish exactly ONE last piece of food remains; "
  "that single piece is the only vermilion. One adult's bare right forearm and hand (short sleeve) rest relaxed on the table beside the spoon, entering from the right edge "
  "of the frame; the body and face are out of frame.",
  "- a morning dining table with window light\n- exactly one hand: a bare right forearm entering from the right edge and resting on the table (the body outside the frame is expected)\n"
  "- a rice bowl, small side dishes, a spoon and chopsticks laid down\n- exactly one remaining piece of food in a side dish, and it is the only vermilion"),
 "C75": ("C75 마지막 화면", OBJ, [],
  "Subject (the closing still life): an empty soup bowl with a spoon laid down beside it, placed in the LEFT half of the plate. The bowl is empty except for one thin trace "
  "of soup along the inside bottom; that thin trace is the only vermilion. The whole RIGHT half of the plate is empty cream paper (end-screen elements will go there). No people.",
  "- one empty soup bowl with a spoon beside it, in the left half\n- the right half of the image is empty paper\n- only a thin trace of soup in the bowl is vermilion\n- no people"),
 "C02": ("C02 다시 넣는 손", FULL, ["C01"],
  "Scene (opening, the same night as the FIRST reference image): keep the same fallen foil snack bag on the same low coffee table, the same living room and the same cold TV light "
  "from outside the frame on the left. The last snack piece is gone: the bag is empty. A bare adult right hand and forearm (the same kind of hand as in the scene reference) "
  "enters from the right edge of the frame and reaches into the bag's open mouth, fingertips just disappearing into the dark inside; only the back of the hand and the forearm "
  "are visible, the body is out of frame. A few tiny crumbs cling to the edge of the bag's mouth; those crumbs are the only vermilion.",
  "- the same kind of fallen foil snack bag, now empty\n- exactly one hand: a bare right forearm and hand entering from the right edge and reaching into the bag's mouth "
  "(the body outside the frame is expected)\n- only a few tiny crumbs at the bag's mouth are vermilion; no whole snack pieces"),
 "C03": ("C03 봉지 안 손끝", FULL, ["C01"],
  "Scene (inside the bag): a view from INSIDE the dark foil snack bag of the FIRST reference image, looking toward its open mouth, which shows only as a pale opening of cold light: "
  "nothing of the room is visible through it (no TV, no screen, no furniture, no plants, no window), just soft bright light. "
  "Crinkled foil walls fill the frame in dense cross-hatching. The index and middle fingertips of one bare adult right hand come in through the mouth and touch the foil floor. "
  "There is nothing on the floor but a few tiny crumbs next to the fingertips; those crumbs are the only vermilion. No whole snack pieces.",
  "- a view from inside a foil bag toward its open mouth\n- the fingertips of one hand come in through the mouth and touch the bottom (only part of one hand is visible, which is expected)\n"
  "- only a few tiny crumbs are vermilion; no whole snack pieces"),
 "C04": ("C04 멈춘 손", FULL, ["C01"],
  "Scene (the hand stops): the same night living room and the same empty fallen foil bag on the low coffee table as in the FIRST reference image. A bare adult right hand, just pulled "
  "out of the bag, hangs still in the air above the table near the bag's mouth, fingers slightly curled and empty; it enters from the right edge with its forearm and the body is "
  "out of frame. A few tiny crumbs stick to the fingertips; those crumbs are the only vermilion. Calm, suspended stillness.",
  "- exactly one bare right hand and forearm from the right edge, empty, held still in the air above the table\n- the empty foil bag lies on the table\n"
  "- only tiny crumbs on the fingertips are vermilion"),
 "C05": ("C05 위에서 본 탁자", FULL, ["C01"],
  "Scene (looking down): a top-down view of the same low coffee table at night as in the FIRST reference image. The empty foil snack bag lies flattened on the table with crumbs "
  "scattered around it. The corner of a TV remote control just enters the edge of the frame. Cold TV light from one side falls across the table surface. No people, no hands. "
  "The scattered crumbs are the only vermilion.",
  "- a top-down view of a table with a flattened empty foil bag and scattered crumbs\n- the corner of a remote control at the frame edge\n- no people or hands\n- only the crumbs are vermilion"),
 "C06": ("C06 같은 자리로 가는 손", FULL, ["C01"],
  "Scene (the repeated reach, an engraved motion study): the same night table and the same foil snack bag as in the FIRST reference image, seen close. Three or four ghost repetitions "
  "of the SAME bare right hand and forearm, drawn as fine, faint hatched outlines at slightly different positions like a printed motion study, all reach in from the right edge and "
  "converge on one point: the bag's mouth. Only the frontmost repetition is drawn fully; the others are lighter echoes made of thin lines. At the bag's mouth a single snack piece "
  "of the same twisted shape is the only vermilion.",
  "- three or four faint, intentional ghost repetitions of the same right hand reaching toward the bag's mouth (an intended motion trail of one hand, not extra people)\n"
  "- the repetitions come from the right edge and converge on the bag's mouth\n- only one twisted snack piece at the bag's mouth is vermilion"),
 "C07": ("C07 조금 더 남은 봉지", OBJ, [],
  "Subject (what if a little more were left?): a plain crinkled foil snack bag (no printing) lying alone on its side on plain cream paper like a specimen plate, its open mouth "
  "toward the viewer, with about one third of its twisted puffed snack pieces (the same twisted shape as in the scene reference) still inside and visible through the mouth. "
  "Keep the bag small enough that the bag and its shadow stay entirely in the upper two thirds of the image. "
  "No table, no room, no hands, no people. The snack pieces inside the bag are the only vermilion.",
  "- one foil snack bag lying on its side on plain paper, about one third full of snack pieces visible at the mouth\n- no people or hands\n- only the snack pieces are vermilion"),
 "C08": ("C08 멈춘 손(종이 위)", OBJ, [],
  "Subject (would the hand stop?): on plain cream paper like a specimen plate, a plain foil snack bag lies on its side with about one third of its twisted snack pieces visible "
  "at the open mouth. Above the mouth, one bare adult right hand hovers, paused, fingers slightly open, not touching anything; its forearm runs to the right edge of the image. "
  "Nothing else: no table, no room. The snack pieces at the bag's mouth are the only vermilion.",
  "- a foil bag with snack pieces at its mouth on plain paper\n- exactly one bare right hand hovering above the mouth, its forearm running to the right edge\n- only the snack pieces are vermilion"),
 "C09": ("C09 한 조각 집기", OBJ, [],
  "Subject (one more piece): a close-up specimen plate on plain cream paper: the thumb and index finger of one bare adult right hand pick up one twisted snack piece and lift it "
  "slightly into the air; the hand comes in from the right edge. A few crumbs lie below. Nothing else. The lifted snack piece is the only vermilion.",
  "- one hand's thumb and index finger holding one twisted snack piece in the air (the rest of the hand and arm toward the right edge)\n- only that snack piece is vermilion\n"
  "- no other people or hands"),
 "C10": ("C10 첫 인사 정물", OBJ, [],
  "Subject (the greeting still life): on plain cream paper, an empty plain foil snack bag, half folded over and lying flat, with a few crumbs scattered around it, like a quiet "
  "still-life specimen plate. No hands, no people. The few crumbs are the only vermilion.",
  "- an empty, half-folded foil bag lying flat on plain paper\n- a few scattered crumbs, the only vermilion\n- no people or hands"),
}


def path(name, suffix=".png"):
    return os.path.join(OUT, f"{name}{suffix}")


def job(name):
    _, frame, lead, scene, brief = CUTS[name]
    out = path(name)
    if not os.path.exists(out):
        refs = [path(r) if r in CUTS else os.path.join(ROOT, r) for r in lead] + STYLE_REFS
        prompt = " ".join([COMMON, PAPER, VARIANT["a"], frame, scene, SUB[frame], NOTEXT, STYLE])
        with open(path(name, ".prompt.txt"), "w") as f: f.write(prompt + "\n")
        r = subprocess.run([GEN, ",".join(refs), prompt, out], capture_output=True, text=True, env=ENV)
        with open(path(name, ".log"), "w") as f: f.write(r.stdout + r.stderr)
        if r.returncode or not os.path.exists(out): return f"{name}: FAIL (see .log)"
    if not os.path.exists(path(name, "_paper.png")):
        subprocess.run(["python3", OVERLAY, PAPER_PNG, out, path(name, "_paper.png")], check=True, capture_output=True)
    if not os.path.exists(path(name, ".check.txt")):
        r = subprocess.run([CHECK, out, brief + SUB_BRIEF[frame]], capture_output=True, text=True, env=ENV)
        with open(path(name, ".check.txt"), "w") as f: f.write(r.stdout + r.stderr)
    verdict = [l for l in open(path(name, ".check.txt")).read().splitlines() if l.startswith("VERDICT")]
    return f"{name}: ok, {verdict[0] if verdict else 'check failed (see .check.txt)'}"


def compare():
    names = sorted(n for n in CUTS if os.path.exists(path(n, "_paper.png")))
    tw, th, band, gap, cols = 768, 432, 48, 16, 2
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (gap + cols * (tw + gap), gap + rows * (band + th + gap)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 26, index=6)
    for i, n in enumerate(names):
        x, y = gap + (i % cols) * (tw + gap), gap + (i // cols) * (band + th + gap)
        draw.text((x, y + 8), CUTS[n][0], fill="black", font=font)
        sheet.paste(Image.open(path(n, "_paper.png")).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + band))
    sheet.save(path("compare", ".jpg"), quality=85)


if __name__ == "__main__":
    names = sys.argv[1:] or list(CUTS)
    first = [n for n in names if not any(r in names for r in CUTS[n][2])]  # 이번에 함께 그리는 컷을 참조하지 않는 컷부터 함께 그린다
    with ThreadPoolExecutor(3) as ex:
        for line in ex.map(job, first): print(line, flush=True)
    for n in names:
        if n not in first: print(job(n), flush=True)
    compare(); print(path("compare", ".jpg"))
