# 수프·팝콘 편 샷 그림을 그린다(작업 3단계, 2026-11-23 합의): 샷 리스트에서 '새로 그림'인 샷 → shotlist/gen/S###.png
# 2026-11-26: 11/25·11/26 대본 수정으로 다시 나눈 뒤 새로 그리는 58샷을 더함(그 전에 그린 샷은 번호를 옮겨 그대로 둠).
# 그리는 방식은 storyboard/make_cuts.py와 같다: 그림체 문구 + 자막 자리 + 글자 없음 → gpt-image-2(codex, tools/gen-ref.sh) →
# 종이 질감 세기 2(<샷>_paper.png, 본 그림) → 자동 검수(<샷>.check.txt). 검수에 떨어지면 두 번까지 다시 그리고(앞 판은 <샷>_try1·_try2),
# 그래도 떨어지면 FAIL로 알린다(그대로 쓸지 고칠지는 사람에게 묻는다). 마지막에 4부분 비교 화면(compare_1~4.jpg)을 만든다.
# 참고 그림: 앞 샷의 다음 상태는 그 샷, 같은 장소·물건은 처음 그린 그림 1장(밤 거실 C01, 수프 장치 C14, 영화관 C28, 위 C45, 아침 식탁 C68,
# 11/26부터 첫머리 팝콘 통 S001, 옛 영화관 로비 S049, 회의실 S078, 갈비찜 S084, 불판 S087, 결말의 앉은 사람 S104) + 그림체 기준 2장.
# 실행: python3 production/soup-popcorn/shotlist/gen_shots.py [S005 S006 ...]   (이미 있는 파일은 건너뛴다. 다시 그리려면 그 샷의 png를 지운다)
import json, os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(EP, "storyboard"))
from make_cuts import COMMON, PAPER, NOTEXT, VARIANT, FULL, OBJ, GEN, ENV, STYLE, SUB, SUB_BRIEF, STYLE_REFS, PAPER_PNG, OVERLAY, CHECK  # noqa: E402

OUT = os.path.join(HERE, "gen"); os.makedirs(OUT, exist_ok=True)
CUTS = os.path.join(EP, "storyboard", "cuts")
DATA = json.load(open(os.path.join(EP, "storyboard", "review", "shots.json"), encoding="utf-8"))
ALL = [h for s in DATA["sections"] for x in s["scenes"] for h in x["shots"]]
INFO = {h["id"]: h for h in ALL}
FRAME = {"화면 가득": FULL, "종이 위 오브제": OBJ}
RETRIES = 2
PARTS = [("1 오프닝·예상해 보기", 0, 2), ("2 실험과 발견", 2, 5), ("3 작동 원리·적용", 5, 7), ("4 결말·작은 관찰", 7, 10)]  # 구간 번호 [시작, 끝)

# 샷: (앞 참조(C## = 이미 그린 컷, S### = 이번에 그린 샷), 장면, 검수 기준). 그림 설명은 shotlist/샷리스트.md의 한국어 설명을 옮긴 것.
SHOTS = {
# ── 생활 속 모순 ──
"S001": (["C28"],
 "Scene (fourteen-day-old popcorn): an extreme close view in the dark movie theater of the FIRST reference image: a tall, slightly tapered plain paper popcorn tub with no"
 " stripes, printing or text stands on a seat armrest, seen from just above the armrest. One narrow shaft of projector light, drawn in thin lines of bare paper white, "
 "falls across the mound of popcorn inside the tub. The popcorn is stale: shrunken, wrinkled, curled and limp kernels. The rest of the theater sinks into dense dark "
 "hatching. No people, no hands. The stale popcorn inside the tub is the only vermilion.",
 "- one plain popcorn tub on a theater armrest, seen very close in the dark\n"
 "- the popcorn looks shrunken and wrinkled (stale)\n"
 "- no people or hands\n"
 "- no printing on the tub\n"
 "- only the popcorn is vermilion"),
"S002": (["S001"],
 "Scene (stale and oily): an extreme close-up of a few stale popcorn kernels resting at the bottom of the same plain paper tub as in the FIRST reference image: the "
 "kernels are shrunken, their hulls curled, their surfaces limp; under them a dark oil stain has soaked and spread into the paper of the tub bottom, drawn in fine black "
 "hatching. No hands, no people. The popcorn kernels are the only vermilion; the oil stain is black ink only.",
 "- a few shrunken, wrinkled popcorn kernels seen extremely close\n"
 "- a dark oil stain soaked into the paper under them\n"
 "- no hands or people\n"
 "- only the kernels are vermilion"),
"S003": (["S001"],
 "Scene (how much could you eat): strong black and white contrast in the dark theater of the FIRST reference image. Out of the darkness, a bare right hand and forearm "
 "with no sleeve, entering from the right edge, slides only its fingertips into the plain popcorn tub on the armrest. The projector light catches the back of the hand in "
 "thin lines of bare paper white. No face, no body. The popcorn inside the tub is the only vermilion.",
 "- exactly one bare hand, its forearm running to the right edge, fingertips going into the tub (the body outside the frame is expected)\n"
 "- no sleeve on the arm\n"
 "- no face\n"
 "- only the popcorn is vermilion"),
"S004": (["S001"],
 "Scene (a silent beat): the same dark theater and the same plain popcorn tub on the armrest as in the FIRST reference image, seen a little farther back: the tub stands "
 "alone on the armrest while the projector beam passes above it diagonally, drawn in thin lines of bare paper white. No hands, no people. The popcorn in the tub is the "
 "only vermilion.",
 "- one plain popcorn tub alone on a theater armrest with the projector beam passing above\n"
 "- no hands or people\n"
 "- only the popcorn is vermilion"),
"S005": (["S001"],
 "Scene (popcorn handed out for a study): a brightly lit movie theater concession counter. On the counter stand rows of identical plain paper popcorn tubs like the tub in"
 " the FIRST reference image, in exactly two sizes, medium and large, lined up in two neat rows, each tub filled with popcorn heaped above its rim. No people, no hands, "
 "no text. The popcorn heaped in the tubs is the only vermilion.",
 "- a lit counter with plain popcorn tubs in exactly two sizes (medium and large) in rows\n"
 "- no people or hands\n"
 "- no printing or text\n"
 "- only the popcorn is vermilion"),
"S006": (["S001"],
 "Scene (the large tub): in a dark theater seat, a large plain paper popcorn tub rests on a lap; the tub is as big as the sitter's torso. A bare right hand and forearm "
 "with no sleeve, entering from the right edge, is plunged into the tub. Only the lap, the tub and the hand are visible; no face, no head. The popcorn in the large tub is"
 " the only vermilion.",
 "- one very large popcorn tub on a lap in a dark seat\n"
 "- exactly one bare hand in the tub, its forearm running to the right edge (the body outside the frame is expected)\n"
 "- no face\n"
 "- only the popcorn is vermilion"),
"S007": (["S046"],
 "Subject (the large tub ate more): an engraved specimen plate on plain cream paper: a medium plain popcorn tub and a large plain popcorn tub stand side by side, like the"
 " tubs in the FIRST reference image but not cut away. In front of each tub lies a small heap of popcorn: the amount eaten from that tub. The heap in front of the large "
 "tub is clearly bigger than the heap in front of the medium tub. No people, no text. The two heaps in front of the tubs are the only vermilion.",
 "- a medium and a large popcorn tub side by side on plain paper\n"
 "- a heap of popcorn in front of each; the heap before the large tub is bigger\n"
 "- no text or people\n"
 "- only the heaps are vermilion"),
"S008": (["S001"],
 "Scene (tasteless from the first bite): an extreme close-up in the dark movie theater of the FIRST reference image (dim theater seats and the screen glow far behind, "
 "no room of a home, no windows, no plants): the tips of a bare thumb and index finger of a right hand hold up one single stale, shrunken "
 "popcorn kernel; a thin edge of projector light outlines the fingertips in bare paper white. No face. The kernel between the fingers is the only vermilion.",
 "- one stale popcorn kernel held between a thumb and an index finger, seen extremely close\n"
 "- the background is a dark movie theater (not a home, no windows or plants)\n"
 "- only one hand (the fingers belong to one hand)\n"
 "- no face\n"
 "- only that kernel is vermilion"),
"S009": (["S001"],
 "Scene (the hand kept going): a close view of the rim of the same plain paper popcorn tub as in the FIRST reference image, in the dark theater. One side of the rim is "
 "pressed down and bent from a hand going in and out at the same spot, and that spot shines with greasy oil marks drawn in glossy black hatching. No hand is visible. A "
 "few popcorn crumbs caught on the bent rim are the only vermilion.",
 "- a close view of a paper tub rim, bent and greasy on one side\n"
 "- no hands or people\n"
 "- only the crumbs on the rim are vermilion"),
# ── 예상해 보기 · 첫 인사 ──
"S010": ([],
 "Scene (stopping when the body feels full): a close view of a table in daylight: a soup bowl with a little tomato soup still left in it, and one bare right hand in a short "
 "sleeve, from the right edge, laying a spoon down beside the bowl. No face or body. The soup left in the bowl is the only vermilion.",
 "- exactly one hand laying a spoon down beside a bowl (the body outside the frame is expected)\n- a little soup left in the bowl; only that soup is vermilion"),
"S011": (["S060"],
 "Subject (the stomach stretches): the FIRST reference image is the previous state of this same stomach: keep the same drawing, position and style, but now the stomach is "
 "filled with food and its wall is visibly stretched, rounder and larger than before. No body outline, no text. The food inside is the only vermilion.",
 "- the same stomach engraving, now fuller and visibly stretched\n- no text, no body outline\n- only the food inside is vermilion"),
"S012": ([],
 "Subject (from a bag to a plate): on plain cream paper, an empty plain foil snack bag lies on its side on the left and an empty plain round plate lies on the right at the same "
 "height, like two specimens on one plate. The bag's open mouth points toward the plate. One single crumb sits at the bag's mouth; it is the only vermilion. The plate is "
 "completely empty. No hands, no people.",
 "- an empty foil bag on the left and an empty plate on the right on plain paper\n- the bag's mouth points toward the plate\n"
 "- exactly one crumb at the bag's mouth is vermilion; the plate is empty\n- no hands or people"),
"S014": ([],
 "Subject (the greeting, up close): a close-up specimen plate of a few snack crumbs on plain cream paper: five or six small irregular crumbs of the twisted puffed snack, "
 "loosely scattered in one small cluster, drawn large and precise like engraved specimens; between them the grain and fibers of the paper are clearly visible. "
 "No bag, no hands, no people. The crumbs are the only vermilion.",
 "- a few snack crumbs on plain paper, seen close\n- no bag, hands or people\n- only the crumbs are vermilion"),
"S016": (["C14"],
 "Subject (back to the first question): on plain cream paper, a soup bowl (like the bowl in the FIRST reference image, without a tube) stands on the left and a plain foil "
 "snack bag lies on the right, far apart. A thin dotted line runs from the bowl to the bag. The bag still holds a few twisted snack pieces visible at its mouth; those snack "
 "pieces are the only vermilion, and the soup is drawn in black ink only. No people.",
 "- a soup bowl and a foil snack bag far apart on plain paper, linked by one thin dotted line\n- only the snack pieces in the bag are vermilion; the soup is not\n- no people"),
# ── 실험과 발견 · 수프 ──
"S017": (["S019"],
 "Scene (a laboratory in 2005): a quiet plain room in the laboratory of the FIRST reference image, seen wider: one table covered with a white tablecloth hanging to the "
 "floor, two chairs, and against the wall a simple metal cart with a soup pot on it. Daylight from a window falls in long shapes of bare paper white across the floor. No "
 "buildings, signs, logos or people. The soup inside the pot (visible under its lifted lid) is the only vermilion.",
 "- a plain room with one table covered by a long tablecloth, two chairs and a cart with a soup pot\n"
 "- window light on the floor\n"
 "- no people, signs or logos\n"
 "- only the soup in the pot is vermilion"),
"S018": (["C14"],
 "Subject (the soup study): two identical plain ceramic soup bowls side by side on plain cream paper, the same kind of bowl as in the FIRST reference image but with no tube "
 "and no table, both full of tomato soup, each with a spoon resting across its rim. From outside the two bowls look exactly alike. No people, no hands. "
 "The soup in the two bowls is the only vermilion.",
 "- two identical soup bowls side by side on plain paper, each with a spoon across the rim\n- both full of soup; the soup is the only vermilion\n"
 "- no tube, no table, no people or hands"),
"S019": (["C14"],
 "Scene (the difference is under the table): a laboratory dining table in a plain room in daylight. A white tablecloth hangs all the way to the floor on every side, so the "
 "space under the table is hidden in shadow. On the table sit two identical bowls of tomato soup with spoons. Seen from the front and slightly low, so the long hanging "
 "tablecloth and the darkness beneath it fill much of the frame. No people, no hands. The soup in the bowls is the only vermilion.",
 "- a table whose cloth hangs to the floor and hides what is under it\n- two identical soup bowls on the table\n- no people or hands\n- only the soup is vermilion"),
"S021": (["C14"],
 "Scene (the hole in the bottom): a close-up cross-section of the bottom of the self-refilling bowl of the FIRST reference image, sliced open and seen from the side: the tube "
 "rises from below and enters the center of the bowl's bottom through a small hole; tiny bubbles and a slow upward current rise through the hole into the bowl, and the soup "
 "fills the bowl to the brim near the top of the frame. The table and the tube fill the lower part of the frame in dark hatching. Only the soup inside the bowl is vermilion; "
 "the soup inside the tube is black ink hatching. No people.",
 "- a close cross-section of a bowl's bottom with a tube entering through a small hole\n- bubbles rising through the hole; the bowl is full\n- no people\n"
 "- only the soup inside the bowl is vermilion"),
"S022": (["C14"],
 "Scene (eating the soup): a close view of the laboratory dining table: one participant's bare adult right hand holds a spoon and lifts a spoonful of tomato soup from a bowl "
 "that is full to the very brim. Only the hand and part of the forearm enter from the right edge; the body and face are outside the frame. The soup is the only vermilion.",
 "- exactly one hand holding a spoon, its forearm entering from the right edge (the body outside the frame is expected)\n- a soup bowl full to the brim\n"
 "- only the soup is vermilion"),
"S023": ([],
 "Subject (the ordinary bowl shows what was eaten): a cutaway cross-section of an ordinary soup bowl like an engraved scientific plate, cut in half to show its inside. "
 "The soup level is now low, near the bottom; on the inner wall above it a series of thin horizontal tide lines marks the higher levels the soup went down through. "
 "No tube, nothing under the bowl, no people. The soup is the only vermilion.",
 "- one soup bowl drawn in cross-section\n- a low soup level with several thin tide lines on the inner wall above it\n- no tube under the bowl, no people\n"
 "- only the soup is vermilion"),
"S024": (["C14"],
 "Scene (staff refill the ordinary bowl): a close view of the laboratory dining table: an ordinary soup bowl about three quarters eaten, and a staff member's hand in a plain "
 "long sleeve pouring tomato soup into it from a ladle. Only the hand, the sleeve and the ladle enter from the top-left edge; no face or body. "
 "The soup in the ladle and in the bowl is the only vermilion.",
 "- exactly one hand in a long sleeve holding a ladle and pouring soup into a bowl (the body outside the frame is expected)\n- only the soup is vermilion"),
"S025": (["C14"],
 "Scene (twenty minutes): the laboratory dining table in daylight with two identical bowls of tomato soup, spoons resting in them. Beside them stands a small analog desk clock "
 "whose face has only tick marks and hands, no numbers. Late light from a window falls across the table and stretches long shadows from the bowls and the clock. "
 "No people, no hands. The soup is the only vermilion.",
 "- two soup bowls and a small desk clock on a table\n- the clock face has tick marks only, no numbers\n- long window shadows\n- no people\n- only the soup is vermilion"),
"S026": ([],
 "Subject (the first result, as a chart): an engraved plate of exactly two vertical bars standing side by side on one shared baseline, like an old printed statistical chart "
 "with fine hatching. Place this pair of bars in the LEFT half of the image; the right half stays empty paper. The left bar (the ordinary bowl) is black ink hatching. "
 "The right bar (the self-refilling bowl) is exactly 1.73 times as tall as the left bar and is filled with flat vermilion. Above each bar a tiny black-ink soup bowl icon "
 "identifies it (the right one with a short tube under it). Leave a band of empty paper above the bars for a caption added later. No axis labels, no numbers, no text. No people.",
 "- exactly two vertical bars on one baseline, in the left half of the image\n- the right bar is clearly taller (about 1.7 times the left) and is the only vermilion element\n"
 "- no text, numbers or axis labels\n- the right half of the image is empty paper"),
"S027": (["C14"],
 "Scene (after the meal, the fullness question): the laboratory dining table after the meal: an emptied soup bowl with only a thin trace of tomato soup at its bottom. "
 "A staff member's hand in a plain long sleeve, from the left edge, hands one blank questionnaire sheet (only empty rating boxes and lines, no writing) to a participant's bare "
 "hand that takes it from the right edge. Only these two hands; no faces or bodies. The thin trace of soup in the bowl is the only vermilion.",
 "- exactly two hands from opposite edges passing one blank questionnaire sheet (the bodies outside the frame are expected)\n"
 "- an emptied soup bowl with only a thin trace of soup; that trace is the only vermilion\n- the sheet has no writing, letters or numbers"),
"S028": ([],
 "Subject (fullness was about the same): two blank questionnaire sheets lie side by side on plain cream paper. Each sheet shows one horizontal rating scale made of a row of "
 "small empty boxes, with no writing, letters or numbers anywhere. On each sheet one box is marked with a small hand-drawn cross; the two marks sit at nearly the same place "
 "on the scale, one box apart. No people, no pencils. The two marks are the only vermilion.",
 "- two blank questionnaire sheets side by side, each with one rating scale of empty boxes\n- one marked box on each; the two marks are at nearly (not exactly) the same position\n"
 "- no text or numbers\n- only the two marks are vermilion"),
# ── 실험과 발견 · 독립 재현 ──
"S029": (["C14"],
 "Subject (how far can we trust the number?): a single self-refilling soup bowl (the bowl of the FIRST reference image, its tube not shown) alone on plain cream paper, "
 "full to the brim with tomato soup. Light from above and slightly behind casts a long shadow forward. Small in the frame, quiet and isolated. No people. "
 "The soup is the only vermilion.",
 "- one soup bowl full to the brim, alone on plain paper with a long shadow\n- no tube, no people\n- only the soup is vermilion"),
"S030": ([],
 "Scene (the university looked again): a research office desk at night under a single desk lamp: tall stacks of blank papers and data sheets with empty grids (no numbers,"
 " no writing), binders and folders. Between two folders one small slip of paper is tucked in, sticking out. No building, logo, nameplate or people. The tucked slip of "
 "paper is the only vermilion.",
 "- a desk at night under a lamp with stacks of blank papers and folders\n"
 "- one small slip tucked between folders\n"
 "- no people, logos or writing\n"
 "- only the slip is vermilion"),
"S031": ([],
 "Subject (misreported data): a close engraved plate of one sheet of a data table on plain cream paper: an empty grid of cells with no numbers or writing. Several cells "
 "are struck through with X marks and overlaid with correction strokes and erasure smudges. No people. The X-marked cells are the only vermilion.",
 "- one sheet with an empty grid (no numbers or letters)\n"
 "- several cells marked with X and correction strokes\n"
 "- only the X-marked cells are vermilion"),
"S032": (["C14"],
 "Scene (a different lab): a different laboratory room from before, with a differently shaped window and different walls, in daylight. On a bare table with a plain cloth sit "
 "two identical, completely empty soup bowls of the same shape as in the FIRST reference image, waiting to be filled. No soup yet, no people, no hands. "
 "The inner surfaces of the two empty bowls carry a soft vermilion tint, the only vermilion.",
 "- a laboratory room with a table and two identical empty bowls\n- no soup, no people or hands\n- only the inner surfaces of the two bowls are vermilion"),
"S033": ([],
 "Subject (the plan fixed in advance): an engraved still life on plain cream paper: a plain closed document folder (no writing) pushed halfway into a large envelope whose flap "
 "is sealed with a round wax seal. Nothing is written anywhere. No people. The wax seal is the only vermilion.",
 "- a folder inside an envelope sealed with a round wax seal\n- no writing anywhere\n- only the wax seal is vermilion"),
"S035": (["C14"],
 "Scene (the same setup, again): the new laboratory table with its cloth lifted on one side to show, underneath, the same reservoir and thin tube rising into the bottom of a "
 "bowl as in the FIRST reference image. Three participants' hands, each coming from a different frame edge (left, top, right) with one clear arm in a plain sleeve, hold "
 "spoons over full bowls of tomato soup. No faces or bodies. The soup is the only vermilion.",
 "- a table with its cloth lifted, showing a reservoir and a tube under one bowl\n"
 "- exactly three hands with spoons, each arm running to a different frame edge (the bodies outside the frame are expected)\n- only the soup is vermilion"),
"S036": (["S026"],
 "Subject (the second result, the same chart grown): the FIRST reference image is the previous state of this same chart: keep its left pair of bars exactly as they are, in the "
 "left half. Now add, in the right half on the same baseline, a second pair of bars in the same engraved style: its left bar is the same height as the original black bar, "
 "its right bar is 1.32 times that height and filled with flat vermilion. The second vermilion bar is clearly shorter than the first vermilion bar. Small black-ink bowl icons "
 "above each bar as before. Keep the empty band above the bars. No numbers, no text, no axis labels.",
 "- two pairs of vertical bars on one baseline (four bars in all)\n- in each pair the right bar is taller and vermilion; the right pair's vermilion bar is shorter than the left pair's\n"
 "- no text or numbers"),
"S037": ([],
 "Subject (the difference shrank): two old engraved balance scales side by side on plain cream paper. Each scale has two pans: the left pan holds a small ordinary soup bowl, "
 "the right pan a small self-refilling bowl drawn with a short tube under it. Both scales tip down toward the right pan; the left scale tips steeply, the right scale only a "
 "little. No people, no text. The soup in the two right-hand bowls is the only vermilion.",
 "- two balance scales side by side\n- both tip toward their right pan; the left scale tips more than the right one\n- no text\n"
 "- only the soup in the right-hand bowls is vermilion"),
"S038": ([],
 "Subject (the result, seen from above): two soup bowls seen from directly above on plain cream paper. The left, ordinary bowl has little soup left and its bottom shows "
 "through; the right, self-refilling bowl is full to the brim. Spoons lie beside them. No people. The soup is the only vermilion.",
 "- two bowls seen from above\n- the left bowl nearly empty with its bottom visible, the right bowl full to the brim\n- no people\n- only the soup is vermilion"),
"S039": (["C14"],
 "Subject (both studies, side by side): two small cutaway diagrams of a laboratory table side by side on plain cream paper, in the same engraved style as the FIRST reference "
 "image: on the left the first study's table, on the right the replication's table with a slightly different table shape. Under each table the same reservoir and tube rise "
 "into the bottom of a bowl. No people, no text. The soup in the two bowls is the only vermilion.",
 "- two small table cutaways side by side, each with a reservoir and a tube under a bowl\n- no people or text\n- only the soup in the two bowls is vermilion"),
# ── 실험과 발견 · 팝콘과 점보 ──
"S041": (["C28"],
 "Scene (handing out popcorn): the lit entrance of the same movie theater as in the FIRST reference image, under a warm overhead lamp drawn in bare paper white. A staff "
 "member's hand in a plain long sleeve, from the left edge, hands a plain paper popcorn tub (no printing) to another bare hand reaching from the right edge. Only the two hands "
 "and the tub; no faces or bodies. The popcorn is the only vermilion.",
 "- exactly two hands from opposite edges passing one plain popcorn tub (the bodies outside the frame are expected)\n- no printing on the tub\n- only the popcorn is vermilion"),
"S042": ([],
 "Subject (fresh and stale popcorn): an engraved specimen plate of two small heaps of popcorn on plain cream paper: the left heap is fresh, plump, crisp popcorn with full, "
 "open kernels; the right heap is fourteen-day-old stale popcorn, shrunken, wrinkled and limp. No containers, no people, no text. Both heaps are vermilion and nothing else is.",
 "- two heaps of popcorn on plain paper\n- the left heap plump and fresh, the right heap shrunken and wrinkled\n- no text or people\n- only the popcorn is vermilion"),
"S043": (["C28"],
 "Scene (medium and large tubs): the dark movie theater of the FIRST reference image, now seen closer along one row of seats from behind and to the side; the projector beam "
 "crosses above in thin lines of bare paper white. On the armrests sit plain popcorn tubs of two sizes, medium and large, alternating. Two hands, one from the left edge and "
 "one from the right edge, each with one arm in a plain sleeve, reach into a tub each. No faces, no heads. The popcorn is the only vermilion.",
 "- dark theater seats with medium and large popcorn tubs on the armrests\n- exactly two hands reaching into tubs, each arm running to a side edge (the bodies outside the frame are expected)\n"
 "- no faces\n- only the popcorn is vermilion"),
"S044": ([],
 "Scene (measuring what was left): after the film, under a plain work lamp in a back room, a large plain popcorn tub sits on a simple mechanical kitchen scale whose dial has "
 "only tick marks, no numbers. One bare hand from the right edge steadies the tub. A row of other collected tubs waits on the table behind. No faces or bodies. "
 "The popcorn left in the tub on the scale is the only vermilion.",
 "- one popcorn tub on a scale whose dial has tick marks only (no numbers)\n- exactly one hand steadying the tub (the body outside the frame is expected)\n"
 "- only the popcorn in that tub is vermilion"),
"S045": ([],
 "Subject (a correction came later): an open scholarly journal lying on plain cream paper; its pages show only gray bars for lines, no readable text. Between the open "
 "pages a small separate correction slip is tucked in, its edge sticking out. No people. The tucked correction slip is the only vermilion.",
 "- an open journal with blank gray line bars instead of text\n"
 "- a small slip tucked between the pages\n"
 "- no readable text\n"
 "- only the slip is vermilion"),
"S046": ([],
 "Subject (the tub size and the amount changed together): an engraved cutaway plate of two plain popcorn tubs side by side on plain cream paper, cut in half to show the "
 "inside: a medium tub and a large tub. Each is filled with popcorn up to near its rim, so the large tub clearly holds more. A thin dashed horizontal line marks the starting "
 "fill height in each tub. No people, no text. The popcorn is the only vermilion.",
 "- a medium and a large popcorn tub in cross-section, side by side\n- each filled near the rim with a dashed fill line; the large tub holds more\n- no text\n"
 "- only the popcorn is vermilion"),
"S047": (["C28"],
 "Scene (after the screening): the same theater as in the FIRST reference image with the house lights now on, seen along an empty row of seats. Nobody is there. On each "
 "armrest a plain popcorn tub was left behind, each with a different amount of popcorn remaining. The screen is blank. The leftover popcorn is the only vermilion.",
 "- an empty, lit theater row with no people\n- several popcorn tubs on armrests with different leftover amounts\n- only the popcorn is vermilion"),
"S048": (["C45", "C14"],
 "Subject (marketing noticed it first): two still lifes on plain cream paper. On the left, receding into faint, pale, loose hatching as if out of focus: an anatomical "
 "stomach engraving like in the FIRST reference image and a soup bowl like the one in the SECOND reference image (science and medicine). On the right, sharp and lit: an "
 "old-fashioned small paper popcorn bag from the 1950s, plain with no printing, filled with popcorn. No people, no text. The popcorn in the old bag is the only vermilion;"
 " the soup and the stomach are black ink only.",
 "- a faint, pale stomach and soup bowl on the left\n"
 "- a sharp old paper popcorn bag on the right\n"
 "- no text\n"
 "- only the popcorn in the bag is vermilion (not the soup)"),
"S049": ([],
 "Scene (a Texas movie theater, 1950s): the lobby of a 1950s–60s movie theater: a patterned tile floor, round globe lamps, a curved concession counter, and an old-"
 "fashioned popcorn machine shaped like a glass cabinet on wheels. Signs and posters are blank shapes with no letters. No people. The popcorn inside the glass machine is "
 "the only vermilion.",
 "- a 1950s theater lobby with a tiled floor, round lamps and a glass-cabinet popcorn machine\n"
 "- no people\n"
 "- signs and posters have no letters\n"
 "- only the popcorn in the machine is vermilion"),
"S050": (["S049"],
 "Scene (the concession manager's worry): on the concession counter of the 1950s lobby in the FIRST reference image, small plain paper popcorn bags are stacked in a neat "
 "pile. Beside them two hands with fingers interlaced rest on the counter, both in the same plain long shirt sleeves; the forearms run to the bottom edge. Only hands and "
 "sleeves; no face or body. The popcorn in the top bag of the pile is the only vermilion.",
 "- a neat pile of small popcorn bags on a counter\n"
 "- exactly two hands with fingers interlaced, both sleeves from the same person at the bottom edge\n"
 "- no face\n"
 "- only the popcorn in the top bag is vermilion"),
"S051": (["S049"],
 "Scene (just one bag): on the 1950s concession counter of the FIRST reference image, one hand in a plain sleeve, from the right edge, picks up one small plain paper "
 "popcorn bag and carries it away, while the identical bag right next to it stays untouched on the counter. No face or body. The popcorn in the bag left on the counter is"
 " the only vermilion.",
 "- exactly one hand taking one small bag, its arm running to the right edge (the body outside the frame is expected)\n"
 "- an identical bag left on the counter\n"
 "- only the popcorn in the left-behind bag is vermilion"),
"S052": ([],
 "Subject (buy one, get one): an engraved plate on plain cream paper: two small plain paper popcorn bags tied together with a string, and beside them one blank matinee "
 "ticket stub with no letters or numbers. Everything lies neat and untouched. No people, no text. The popcorn in the two tied bags is the only vermilion.",
 "- two small popcorn bags tied together with string\n"
 "- one blank ticket stub with no letters or numbers\n"
 "- no people or text\n"
 "- only the popcorn is vermilion"),
"S053": (["S049"],
 "Scene (looking greedy): in front of the 1950s concession counter of the FIRST reference image, one hand in a plain sleeve, from the right edge, reaching toward a second"
 " small popcorn bag on the counter, has frozen in mid-air. On the tiled floor behind, the long shadows of people waiting in line stretch and overlap; only their shadows "
 "are seen, not the people. The popcorn in the second bag is the only vermilion.",
 "- exactly one hand frozen in mid-air before a second bag, its arm running to the right edge\n"
 "- long shadows of a queue on the floor, but no visible people\n"
 "- only the popcorn in that bag is vermilion"),
"S054": (["S049"],
 "Scene (a simple solution): in the 1950s theater lobby of the FIRST reference image (patterned tile floor, round globe lamps, the curved concession counter behind; "
 "no kitchen, no utensils, no plants, no windows), at its glass-cabinet popcorn machine, one hand in a plain sleeve, from the right edge, scoops popcorn with a "
 "metal scoop and pours it into a large plain paper tub with no printing. Only the hand and sleeve; no face. The popcorn on the scoop is the only vermilion.",
 "- exactly one hand with a scoop at an old popcorn machine, its arm running to the right edge\n"
 "- the setting is the 1950s theater lobby, not a kitchen (no utensils, plants or windows)\n"
 "- a large plain paper tub being filled\n"
 "- only the popcorn on the scoop is vermilion"),
"S055": ([],
 "Subject (the jumbo tub): an engraved specimen plate on plain cream paper: one small plain paper popcorn bag stands beside one much larger plain paper popcorn tub that "
 "is filled to overflowing, popcorn spilling over its rim. No printing on either, no people, no text. The popcorn overflowing the large tub is the only vermilion.",
 "- a small bag next to a much larger tub overflowing with popcorn\n"
 "- no printing, text or people\n"
 "- only the popcorn on the large tub is vermilion"),
"S056": (["S049"],
 "Scene (everyone bought the big tub): over the 1950s concession counter of the FIRST reference image, three different customers' hands, each in its own sleeve, come in "
 "from the bottom edge one after another, and each one takes one large plain paper popcorn tub. Exactly three hands and three tubs; no faces or bodies. The popcorn in the"
 " large tubs is the only vermilion.",
 "- exactly three hands, each arm running to the bottom edge, each taking one large tub\n"
 "- no faces\n"
 "- only the popcorn in the tubs is vermilion"),
"S057": ([],
 "Subject (the hand stopped at the second bag): on plain cream paper, one small opened plain paper popcorn bag and one small unopened, folded-shut bag lie side by side. "
 "Above them a bare hand, coming down from the top edge, hovers in the air and has stopped. No face or body. The popcorn in the opened bag is the only vermilion.",
 "- one opened and one unopened small bag on plain paper\n"
 "- exactly one hand hovering above them, its arm running to the top edge\n"
 "- only the popcorn in the opened bag is vermilion"),
"S058": (["C28"],
 "Scene (reaching again in the dark): a close view in the dark theater of the FIRST reference image: one bare hand from the right edge goes back into a large plain popcorn "
 "tub on an armrest; the projector light catches the back of the hand as thin lines of bare paper white. The rest sinks into dark hatching. No face. "
 "The popcorn is the only vermilion.",
 "- exactly one hand reaching into a large popcorn tub in a dark theater (the body outside the frame is expected)\n- only the popcorn is vermilion"),
# ── 작동 원리 ──
"S059": ([],
 "Subject (two bags): on plain cream paper two identical plain foil snack bags lie side by side: the left one is empty and slack, the right one still holds about a third of "
 "its twisted snack pieces, visible at the mouth. No hands, no people. The snack pieces in the right bag are the only vermilion.",
 "- two identical foil bags side by side\n- the left one empty, the right one with snack pieces at its mouth\n- only those snack pieces are vermilion\n- no people or hands"),
"S060": (["C45"],
 "Subject (signals from the body): one anatomical stomach in the manner of an old medical engraving (the same stomach style as in the FIRST reference image), calm and not "
 "gory, alone on plain cream paper without any body outline. A little food is visible inside it through a cutaway window in its wall. No people, no text. "
 "The food inside the stomach is the only vermilion.",
 "- one anatomical stomach engraving alone on plain paper, no body outline\n- a little food visible inside through a cutaway\n- no text\n- only the food inside is vermilion"),
"S061": (["C45"],
 "Subject (to the brain): on plain cream paper, an anatomical stomach engraving (the same style as the FIRST reference image) on the lower left and an anatomical brain "
 "engraving on the upper right, set apart. One thin nerve fiber runs from the stomach up to the brain, and a few tiny dots travel upward along it. No body outline, no text. "
 "The tiny dots along the nerve are the only vermilion.",
 "- a stomach and a brain engraving apart on plain paper, joined by one thin nerve\n- small dots along the nerve are the only vermilion\n- no text, no body outline"),
"S062": (["C45"],
 "Subject (fifteen to twenty minutes): on plain cream paper, an engraved hourglass and a small anatomical stomach (like the stomach in the FIRST reference image) stand "
 "side by side. Most of the sand is still in the upper bulb; a thin stream of sand is falling through the neck. No body outline, no people, no text. The falling stream of"
 " sand is the only vermilion.",
 "- an hourglass and a small stomach side by side on plain paper\n"
 "- most of the sand still in the upper bulb\n"
 "- no text\n"
 "- only the falling sand stream is vermilion"),
"S063": ([],
 "Scene (taste): an extreme close-up of one spoonful of tomato soup held in the air, its handle running out of the frame at the right edge, with steam rising from it in fine "
 "curling lines. Soft dark hatched background. No mouth, no face. The soup in the spoon is the only vermilion.",
 "- one spoonful of soup in the air with rising steam, the handle running out of the frame\n- no mouth or face\n- only the soup is vermilion"),
"S064": ([],
 "Subject (rings of an ordinary bowl): an ordinary soup bowl on plain cream paper, seen from above at an angle so the whole inner wall is visible: the soup has gone down "
 "near the bottom, and the inner wall shows many thin concentric rings left at each level, like the rings of a tree trunk. No tube, no people. The soup is the only vermilion.",
 "- an ordinary bowl seen from above at an angle\n- low soup with many concentric rings on the inner wall\n- no tube, no people\n- only the soup is vermilion"),
"S065": ([],
 "Scene (one spoonful lowers the level): an extreme close-up of the inner wall and rim of an ordinary soup bowl at table height, in daylight: a spoon has just lifted out of "
 "the soup and leaves the frame at the top edge, and the soup surface has dropped by one step, leaving a fresh thin tide line on the wall just above the new level. "
 "No hands. The soup is the only vermilion.",
 "- an extreme close-up of a bowl's inner wall and soup surface\n- a fresh tide line just above the soup level\n- a spoon leaving the frame at the top; no hands\n"
 "- only the soup is vermilion"),
"S066": ([],
 "Subject (fullness was asked on a sheet): a close specimen plate on plain cream paper: one bare hand holding a pencil, from the right edge, marks one box on a single blank "
 "questionnaire sheet; the sheet has one horizontal rating scale of empty boxes and no writing, letters or numbers. The new mark is the only vermilion.",
 "- one hand holding a pencil, marking a box on a blank rating sheet (its arm running to the right edge is expected)\n- no text or numbers\n- only the mark is vermilion"),
"S067": (["C45"],
 "Subject (not measured): on plain cream paper, an anatomical stomach engraving (the same style as the FIRST reference image) with a little food inside, and beside it an old "
 "analog gauge with a round dial showing only tick marks, no numbers; its needle rests at the start of the scale, not moving. Nothing connects them. No text. "
 "The food inside the stomach is the only vermilion.",
 "- a stomach engraving and an analog gauge side by side\n- the gauge dial has tick marks only, its needle at rest\n- no text\n- only the food inside the stomach is vermilion"),
"S068": ([],
 "Subject (unit bias): an engraved specimen plate on plain cream paper: two pretzels of exactly the same knotted shape but very different sizes, one small and one large, "
 "laid side by side. No people, no text. The large pretzel is the only vermilion; the small one is black ink only.",
 "- two pretzels of the same shape, one small and one large\n"
 "- no text\n"
 "- only the large pretzel is vermilion"),
"S069": ([],
 "Subject (one serving, whatever the size): on plain cream paper, in one row from left to right: a small bowl, a medium bowl, and a very large plain paper popcorn tub, "
 "each standing alone with space between them. The two bowls hold a little popcorn each; the tub is full. No people, no text. The popcorn in the very large tub is the "
 "only vermilion.",
 "- a small bowl, a medium bowl and a very large popcorn tub in a row, each apart\n"
 "- no text or people\n"
 "- only the popcorn in the large tub is vermilion"),
"S070": (["S001"],
 "Scene (one unit to finish): a first-person view, looking straight down at one's own lap in a dark theater seat. A large plain paper popcorn tub, like the tub in the "
 "FIRST reference image but bigger, rests on the lap, and two hands in plain sleeves come in from the bottom edge of the frame and wrap around it, hugging it close. "
 "The viewer's own body is not seen: only the tops of the thighs, the tub, the hands and the forearms. No face. The popcorn in the tub is the only vermilion.",
 "- seen from above, as if looking down at one's own lap\n"
 "- exactly two hands wrapped around the tub, both arms coming in from the bottom edge\n"
 "- no chest, torso, shoulders or face visible (only thighs, tub, hands and forearms)\n"
 "- only the popcorn is vermilion"),
"S071": ([],
 "Scene (a second bag feels like starting over): a close view of two hands in plain sleeves holding the top edge of an unopened, sealed plain paper popcorn bag, about to "
 "tear it open but stopped. The bag is taut and closed. No face. A small tear notch at the top of the bag is the only vermilion.",
 "- exactly two hands holding the top of one sealed bag, both from the same person\n"
 "- the bag is still closed\n"
 "- no face\n"
 "- only the tear notch is vermilion"),
"S072": (["S001"],
 "Scene (finishing what was started): looking straight down into a giant plain paper popcorn tub, like the tub in the FIRST reference image but much bigger, half eaten. "
 "On the inner wall a faint greasy band shows how far the level of popcorn has gone down. No hands, no people. The popcorn remaining in the tub is the only vermilion.",
 "- a top-down view into a giant, half-eaten popcorn tub\n"
 "- a visible band on the inner wall where the level dropped\n"
 "- no hands or people\n"
 "- only the remaining popcorn is vermilion"),
"S073": (["S001"],
 "Scene (down to the bottom): an oblique view into a large plain paper popcorn tub that has been almost finished: the paper bottom is showing, and only a few kernels are "
 "left in one corner of the bottom. No hands, no people. The few kernels left in the corner are the only vermilion.",
 "- an almost empty large popcorn tub seen at an angle, its bottom showing\n"
 "- only a few kernels left in a corner\n"
 "- no hands or people\n"
 "- only those kernels are vermilion"),
"S074": (["C28"],
 "Scene (a familiar seat): a close view of one empty seat in the theater of the FIRST reference image. The cup holder in its armrest is worn smooth and shiny from use, "
 "and an empty plain paper popcorn tub is pushed into it. No people. The popcorn crumbs at the bottom of the tub are the only vermilion.",
 "- one empty theater seat with a worn cup holder holding an empty popcorn tub\n"
 "- no people\n"
 "- only the crumbs in the tub are vermilion"),
"S075": (["C28"],
 "Scene (reaching, taking, eating, again): in the dark theater, one bare right hand from the right edge moves between a plain popcorn tub on the armrest and the top edge "
 "of the frame, toward an unseen mouth. Its path is drawn like a printmaker's motion study: one solid hand, plus three faint ghost copies of the same hand along the same "
 "arc, drawn only in thin pale hatching lines. The face and mouth are outside the frame. The popcorn pinched in the fingertips of the solid hand is the only vermilion.",
 "- one solid hand and three faint ghost copies of the same hand along one arc between the tub and the top edge\n"
 "- all copies come from the same arm path at the right edge\n"
 "- no face or mouth\n"
 "- only the popcorn in the solid hand's fingertips is vermilion"),
"S076": (["C28"],
 "Scene (a campus movie theater, 2011): a small movie theater at a university, dark, seen along one row of seats. On each armrest sits a small plain paper popcorn box, "
 "and three hands in sleeves, each from a different seat, hold one box each; every arm runs down toward its own seat. Only the forearms in sleeves, the hands, the "
 "boxes and the armrests are seen: torsos, laps, shoulders and heads stay lost in deep darkness or outside the frame. The popcorn in the boxes is the only vermilion.",
 "- a dark row of theater seats with small popcorn boxes on the armrests\n"
 "- exactly three hands, each holding one box, each arm running toward its own seat\n"
 "- no torsos, laps or heads visible (only forearms, hands, boxes and armrests)\n"
 "- no faces\n"
 "- only the popcorn is vermilion"),
"S077": ([],
 "Subject (stale eaten like fresh): an engraved cutaway plate on plain cream paper: two small plain paper popcorn boxes side by side, cut away to show the inside. The "
 "left box held fresh, plump popcorn; the right box held stale, shrunken popcorn. Both have been eaten down to about the same low level, marked by a thin dashed line "
 "across both. No people, no text. The popcorn left at the bottom of both boxes is the only vermilion.",
 "- two small popcorn boxes in cross-section side by side\n"
 "- fresh popcorn in the left box, shrunken stale popcorn in the right\n"
 "- both eaten down to the same level (dashed line)\n"
 "- no text\n"
 "- only the remaining popcorn is vermilion"),
"S078": ([],
 "Scene (a meeting room instead): a bright, plain meeting room in daylight: a long table with chairs, several small plain paper popcorn boxes set along the table, and on "
 "the wall a small blank screen with nothing on it. Through the windows only plain, anonymous low buildings and open sky are seen: no towers and no landmarks. "
 "No people, no text. The popcorn in the boxes is the only vermilion.",
 "- a bright meeting room with a long table and several small popcorn boxes\n"
 "- a small blank screen on the wall\n"
 "- the windows show only plain buildings and sky, no tower or landmark\n"
 "- no people or text\n"
 "- only the popcorn is vermilion"),
"S079": (["S078", "S001"],
 "Scene (less stale popcorn eaten): on the meeting room table of the FIRST reference image, a close view of one small plain paper popcorn box that has barely been "
 "touched: only a few kernels are gone from the top, so the popcorn sits in a flat layer a little below the rim of the box, about a finger's width down, not heaped "
 "and not rising above the rim. The popcorn is stale like the popcorn in the SECOND reference image: small, shrunken, wrinkled kernels with a dull, dry look, not "
 "fresh and fluffy. Beside the box one hand in a plain sleeve, from the right edge, rests lightly on the table, not reaching in. If a window shows behind, only plain "
 "buildings and sky are seen through it, no tower or landmark. No face. The popcorn left in the box is the only vermilion.",
 "- one small popcorn box on a meeting table, its popcorn in a flat layer a little below the rim (not heaped above the rim)\n"
 "- the popcorn looks stale: small, shrunken, wrinkled kernels, not fluffy\n"
 "- exactly one hand resting beside it, not reaching in, its arm running to the right edge\n"
 "- any window shows only plain buildings and sky, no tower or landmark\n"
 "- only the popcorn is vermilion"),
"S081": ([],
 "Subject (stopping when the plate is empty): one completely empty plain round plate alone on plain cream paper, wiped clean, seen from slightly above; at its center lies one "
 "single last crumb. No people, no utensils. That crumb is the only vermilion.",
 "- one empty plate on plain paper\n- exactly one crumb at its center, the only vermilion\n- no people"),
# ── 내 경험에 적용 ──
"S082": (["S084", "S087"],
 "Subject (two ways to eat meat): two still lifes side by side on plain cream paper. On the left, a plate holding one serving of Korean braised short ribs (galbi-jjim) "
 "like in the FIRST reference image. On the right, a small round tabletop grill like in the SECOND reference image, with a few pieces of meat on it. No people, no hands, "
 "no text. One single piece of meat on the grill is the only vermilion; everything else, including the braised ribs, is black ink.",
 "- a plate of braised short ribs on the left and a small grill with a few pieces of meat on the right\n"
 "- no people, hands or text\n"
 "- exactly one piece of meat on the grill is vermilion"),
"S083": ([],
 "Scene (think of eating meat): a close view of one hand in a plain sleeve, from the right edge, lifting one piece of cooked meat with flat Korean metal chopsticks above "
 "a dining table. Only the hand, sleeve and chopsticks; no face. The piece of meat at the tip of the chopsticks is the only vermilion.",
 "- exactly one hand holding metal chopsticks, its arm running to the right edge (the body outside the frame is expected)\n"
 "- one piece of meat at the chopstick tips\n"
 "- no face\n"
 "- only that piece of meat is vermilion"),
"S084": ([],
 "Scene (cooked all at once, served on a plate): on a home dining table, a pot of Korean braised short ribs (galbi-jjim), already fully cooked, sits with its lid off. One"
 " hand in a plain sleeve, from the right edge, uses a ladle to serve the ribs onto a personal plate beside the pot. Only the hand and sleeve; no face. The one rib on the"
 " ladle is the only vermilion; the ribs in the pot and on the plate are black ink.",
 "- a pot of braised ribs and a personal plate on a table\n"
 "- exactly one hand with a ladle, its arm running to the right edge\n"
 "- no face\n"
 "- only the rib on the ladle is vermilion"),
"S085": (["S084"],
 "Scene (you can see what is left): a top-down view of the personal plate from the FIRST reference image: on one side a few cleaned rib bones, on the other side two "
 "pieces of braised rib still left, and flat metal chopsticks lying beside the plate. No hands, no people. The two pieces of rib still left are the only vermilion; the "
 "bones are black ink.",
 "- a top-down view of one plate with a few bones on one side and two pieces of rib on the other\n"
 "- chopsticks beside the plate\n"
 "- no hands or people\n"
 "- only the remaining rib pieces are vermilion"),
"S086": (["S084"],
 "Scene (the empty plate is a full stop): the personal plate from the FIRST reference image, now empty except for streaks of sauce. One hand in a plain sleeve, from the "
 "right edge, lays flat metal chopsticks down neatly across the plate. No face. One streak of sauce left on the plate is the only vermilion.",
 "- an empty plate with sauce streaks\n"
 "- exactly one hand laying chopsticks down, its arm running to the right edge\n"
 "- no face\n"
 "- only one streak of sauce is vermilion"),
"S087": ([],
 "Scene (grilling and eating at once): a Korean barbecue table grill seen at an angle, with pieces of meat cooking on the grill plate. From the left edge, one hand in a "
 "plain sleeve turns a piece of meat with metal tongs; from the right edge, another hand in a different sleeve picks up a cooked piece with metal chopsticks. Only the two"
 " hands and sleeves; no faces. The piece of meat held by the chopsticks is the only vermilion.",
 "- a table grill with meat cooking\n"
 "- exactly two hands: one with tongs from the left edge, one with chopsticks from the right edge (the bodies outside the frame are expected)\n"
 "- no faces\n"
 "- only the piece held by the chopsticks is vermilion"),
"S088": (["S087"],
 "Scene (new meat fills the gap): a close view of the grill plate from the FIRST reference image: among the cooking pieces there is one empty gap where a piece was just "
 "taken, and metal tongs held by one hand in a plain sleeve, from the left edge, are just setting a new raw piece of meat into that gap. No face. The newly placed piece "
 "of meat is the only vermilion.",
 "- a close view of a grill with an empty gap among the meat\n"
 "- exactly one hand with tongs placing a new piece into the gap, its arm running to the left edge\n"
 "- only the new piece is vermilion"),
"S089": (["S087"],
 "Scene (the grill never empties): a top-down view of the grill from the FIRST reference image, completely covered with pieces of meat with no gaps. In front of it a "
 "small personal plate is perfectly clean, with no bones or traces of what was eaten, and chopsticks lie beside it. No hands, no people. One piece of meat in the center "
 "of the grill is the only vermilion.",
 "- a top-down grill fully covered with meat\n"
 "- a clean empty personal plate in front\n"
 "- no hands or people\n"
 "- exactly one piece of meat in the center is vermilion"),
"S090": (["S087"],
 "Scene (more than usual): the end of the meal at the edge of the barbecue table: several emptied meat trays are stacked on top of one another, and the grill from the "
 "FIRST reference image is turned off. No people, no hands. One piece of meat left on the top tray is the only vermilion.",
 "- several empty meat trays stacked at the table edge\n"
 "- a grill that is turned off\n"
 "- no people or hands\n"
 "- only one piece of meat on the top tray is vermilion"),
"S091": (["S021", "S087"],
 "Subject (just like the soup bowl): two engraved plates side by side on plain cream paper. On the left, the grill from the SECOND reference image seen from the side, "
 "with a new piece of meat being set into an empty gap. On the right, the cutaway soup bowl of the FIRST reference image, with the tube in its base, soup rising up from "
 "below to refill it. No people, no text. The rising soup in the bowl is the only vermilion; the meat is black ink.",
 "- a grill on the left and a cutaway soup bowl with a tube in its base on the right\n"
 "- no people or text\n"
 "- only the soup in the bowl is vermilion"),
"S092": ([],
 "Scene (at home in the daytime): a calm living room in daylight in a modern Korean apartment. On the sofa, next to a cushion, lies a large opened plain foil snack bag (no "
 "printing). A bare adult right forearm and hand in a short sleeve (the same kind of hand as in the scene reference) comes in from the right edge toward the bag; the body and "
 "face are out of frame. The snack pieces visible at the bag's mouth are the only vermilion.",
 "- a daytime living room with a large foil snack bag on a sofa next to a cushion\n- exactly one bare right hand and forearm from the right edge (the body outside the frame is expected)\n"
 "- only the snack pieces at the bag's mouth are vermilion"),
"S093": ([],
 "Subject (inside the puffed bag): the FIRST reference image shows this same bag: draw the same bag cut in half as an engraved cross-section: the outer outline is still "
 "puffed and full, but inside only a few snack pieces lie at the very bottom and most of the bag is empty air. No people. The snack pieces inside are the only vermilion.",
 "- the same bag in cross-section with a puffed outline\n- only a few snack pieces at the bottom inside\n- only those pieces are vermilion"),
"S095": ([],
 "Scene (pouring onto a plate): a daytime living-room table: one bare right hand and forearm in a short sleeve, from the right edge, tilts a large foil snack bag so that "
 "twisted snack pieces pour out onto a plain round plate on the table. No face or body. The snack pieces are the only vermilion.",
 "- exactly one hand tilting a foil bag and pouring snack pieces onto a plate (the body outside the frame is expected)\n- only the snack pieces are vermilion"),
"S096": ([],
 "Scene (the plate is empty, the hand pauses): a close view of a daytime table: an empty plain plate with one crumb on it, and one bare right hand from the right edge "
 "hovering still just above it, fingers relaxed, not touching. No face or body. The single crumb is the only vermilion.",
 "- exactly one hand hovering still above an empty plate (the body outside the frame is expected)\n- exactly one crumb on the plate, the only vermilion"),
"S097": ([],
 "Scene (noticing the body): a close view of a daytime table: beside an empty plate with a few crumbs on it, one bare right hand lies flat and open on the table, palm down, "
 "resting; a glass of water stands next to it. No face or body. The crumbs on the plate are the only vermilion.",
 "- exactly one hand resting flat on a table beside an empty plate and a glass of water (the body outside the frame is expected)\n- only the crumbs on the plate are vermilion"),
# ── 처음 장면을 다시 보기 ──
"S098": (["S001"],
 "Scene (back to the dark theater): a new drawing of the same composition as the FIRST reference image: the same dark theater, the same plain paper popcorn tub on the "
 "same armrest, the same narrow shaft of projector light in thin lines of bare paper white. The popcorn now looks ordinary, not stale. No people, no hands. The popcorn in"
 " the tub is the only vermilion.",
 "- the same dark theater armrest and plain popcorn tub as the reference, with a projector light shaft\n"
 "- no people or hands\n"
 "- only the popcorn is vermilion"),
"S099": (["S001"],
 "Scene (now we sit there): the view from eye level of someone sitting in a dark theater seat: over the back of the seat in front, light from the screen spreads in bare "
 "paper white, and the plain paper popcorn tub from the FIRST reference image rests on the sitter's lap near the middle of the frame. The screen shows nothing. No hands, "
 "no face. The popcorn in the tub is the only vermilion.",
 "- a seated eye-level view over the seat in front toward screen light\n"
 "- a popcorn tub on the lap near the center\n"
 "- the screen shows nothing\n"
 "- no hands or face\n"
 "- only the popcorn is vermilion"),
"S100": (["S001"],
 "Scene (the fingertips touch the bottom): a view from inside the plain paper popcorn tub: the dark curved paper walls, and at the bottom only crumbs and a few unpopped "
 "kernels. Bare fingertips of one hand, coming in from the top edge, touch the paper bottom. No face. The unpopped kernels on the bottom are the only vermilion.",
 "- a view from inside a paper tub with only crumbs and unpopped kernels at the bottom\n"
 "- fingertips of exactly one hand touching the bottom, coming from the top edge\n"
 "- only the unpopped kernels are vermilion"),
"S101": (["S001"],
 "Scene (oh, it's all gone): in the dark theater, a bare right hand and forearm with no sleeve, from the right edge, has just come out of the popcorn tub and is stopped "
 "in the empty air, fingers slightly open. Popcorn crumbs cling to the fingertips. The tub is a dim shape below, out of focus. No face. The crumbs on the fingertips are "
 "the only vermilion.",
 "- exactly one bare hand stopped in the air, its forearm running to the right edge, no sleeve\n"
 "- crumbs on the fingertips\n"
 "- no face\n"
 "- only the crumbs on the fingertips are vermilion"),
"S102": (["S001"],
 "Scene (only one question at first): looking straight down into the mouth of the empty plain paper popcorn tub from the FIRST reference image: the inside is so dark that"
 " it looks like a black hole within the paper rim. No hands, no people. One crumb on the edge of the rim is the only vermilion.",
 "- a top-down view of an empty paper tub whose inside is a dark hole\n"
 "- no hands or people\n"
 "- only one crumb on the rim is vermilion"),
"S103": (["C28", "S001"],
 "Scene (widening the view): one step back in the dark theater of the FIRST reference image: a dark row of seats, a drink cup on one armrest, and light from the screen "
 "washing the seat backs in bare paper white. Between two seats sits the plain paper popcorn tub of the SECOND reference image, now empty. No people. The crumbs inside "
 "that tub are the only vermilion.",
 "- a dark row of seats with a drink cup and an empty popcorn tub between seats\n"
 "- screen light on the seat backs\n"
 "- no people\n"
 "- only the crumbs in the tub are vermilion"),
"S104": (["C28"],
 "Scene (the body appears): in the dark theater of the FIRST reference image, seen from behind: the back silhouette of one person sitting in a seat, wearing a short-"
 "sleeved shirt, facing the bright screen. One bare forearm and hand goes into a plain paper popcorn tub on the lap. The screen is a blank glow drawn in bare paper white "
 "and hatching, with no picture on it. The head is a dark silhouette; no face is visible. The popcorn in the tub is the only vermilion; the screen light is not vermilion.",
 "- one seated person seen from behind as a silhouette, in short sleeves, facing a blank bright screen\n"
 "- one hand in a popcorn tub on the lap; the arm joins the shoulder naturally\n"
 "- no visible face\n"
 "- only the popcorn is vermilion, not the screen"),
"S105": (["S104"],
 "Scene (eyes return to the tub): the same person as in the FIRST reference image, in the same short-sleeved shirt and the same seat, now bows the head slightly to look "
 "down at the popcorn tub on the lap. Seen from behind and a little to the side, so the face stays buried in shadow. The crumbs in the tub are the only vermilion.",
 "- the same seated person from behind, head bowed toward a tub on the lap\n"
 "- the face stays in shadow\n"
 "- arms join the shoulders naturally\n"
 "- only the crumbs in the tub are vermilion"),
"S106": (["C45"],
 "Subject (how did the stomach feel): on plain cream paper, a small anatomical stomach engraving (like the stomach in the FIRST reference image) and one single stale, "
 "shrunken popcorn kernel lie side by side as a still life. No body outline, no people, no text. The popcorn kernel is the only vermilion.",
 "- a small stomach and one shrunken popcorn kernel side by side on plain paper\n"
 "- no text or body outline\n"
 "- only the kernel is vermilion"),
"S107": (["C28"],
 "Scene (was there any cue to stop): an empty plain paper popcorn tub on an armrest in the theater of the FIRST reference image, lit by the screen light; behind it the "
 "rows of seats are soft and out of focus, and the screen is a blank rectangle of white light with nothing on it. No people. The crumbs in the tub are the only vermilion.",
 "- an empty popcorn tub on an armrest lit by screen light\n"
 "- blurred seats behind and a blank white screen\n"
 "- no people\n"
 "- only the crumbs are vermilion"),
"S108": (["C28"],
 "Scene (another empty tub): after the screening, with the house lights on, the theater of the FIRST reference image: on the floor between two rows of seats lies one "
 "crushed, empty plain paper popcorn tub. No people. The crumbs caught in the creases of the crushed tub are the only vermilion.",
 "- a lit theater with one crushed empty popcorn tub on the floor between seats\n"
 "- no people\n"
 "- only the crumbs in the tub are vermilion"),
"S109": ([],
 "Subject (what moved the hand): an engraved specimen plate on plain cream paper: an empty plain paper popcorn tub cut open along its seam and flattened, showing its "
 "inner surface: dark oil stains and a worn, creased area where a hand kept going in and out. No people, no text. The few crumbs still stuck to the paper are the only "
 "vermilion.",
 "- an empty paper tub cut open and flattened on plain paper\n"
 "- oil stains and a worn area on its inner surface\n"
 "- no text or people\n"
 "- only a few crumbs are vermilion"),
# ── 작은 관찰 · 마지막 인사 ──
"S111": (["C68"],
 "Scene (the meal is over): the same morning dining table by the window as in the FIRST reference image, seen from directly above: a rice bowl, side dishes, and a spoon and "
 "chopsticks laid down. No hands, no people. In one side dish exactly one piece of food remains; it is the only vermilion.",
 "- a morning table seen from above with a rice bowl, side dishes, a spoon and chopsticks laid down\n- no hands or people\n- exactly one remaining piece of food, the only vermilion"),
"S112": (["C45"],
 "Subject (one reason: the body is comfortably full): on plain cream paper, a small anatomical stomach engraving (the same style as the FIRST reference image) in the upper "
 "middle, and directly below it one single solid round dot like a full stop. Nothing else. The dot is the only vermilion.",
 "- a small stomach engraving with one round dot below it\n- nothing else\n- only the dot is vermilion"),
"S113": (["S112"],
 "Subject (another reason: the taste no longer pulls): the FIRST reference image is the previous plate of this series: keep the same layout, paper and the round dot at exactly "
 "the same position, but replace the stomach with a small plain plate holding one last piece of side dish, drawn in black ink. The dot is the only vermilion.",
 "- a small plate with one piece of food and one round dot below it, in the same layout as the reference\n- no stomach\n- only the dot is vermilion"),
"S114": (["S113"],
 "Subject (nothing left, or several reasons at once): the FIRST reference image is the previous plate of this series: keep the round dot at exactly the same position and "
 "replace the plate with an empty plain plate. At the left and right sides, smaller and partly overlapping each other, the stomach and the plate with one piece appear as faint "
 "echoes. The dot is the only vermilion.",
 "- an empty plate with one round dot below it\n- a faint small stomach and a faint plate with food at the sides\n- only the dot is vermilion"),
"S115": (["C68"],
 "Scene (what did you see?): a first-person view at the morning dining table of the FIRST reference image: one's own bare right hand at the lower right lays a spoon down on "
 "the table, and in front of it the table spreads out: a rice bowl with a little rice left, side dishes and a cup. No other people. "
 "The little food left in the bowl is the only vermilion.",
 "- a first-person view of a morning table, one own right hand laying a spoon down (the body outside the frame is expected)\n- no other people\n"
 "- only the food left in the bowl is vermilion"),
"S116": (["C68"],
 "Scene (how did the body feel?): at the same morning dining table as in the FIRST reference image, an adult sits leaning back in a dining chair, seen from the side as a dark "
 "silhouette against the bright window behind; the face is in shadow and not readable. Short sleeves; both hands rest in the lap. On the table a little food is left in a "
 "dish; it is the only vermilion.",
 "- exactly one person seen from the side as a silhouette, leaning back, face not readable\n- two arms attached correctly, hands in the lap\n"
 "- only the food left in a dish is vermilion"),
"S117": ([],
 "Subject (looking closely at the end of a meal): an engraved still life on plain cream paper: an empty bowl seen at an angle, and a round magnifying glass on a small stand "
 "held over its inner edge (no hands); through the lens, one last piece of food at the bottom of the bowl appears enlarged. No people. That piece of food is the only vermilion.",
 "- an empty bowl with a magnifying glass on a stand over its edge\n- no hands or people\n- only one piece of food in the bowl is vermilion"),
"S118": (["C68"],
 "Scene (the last greeting): a still life on the morning dining table by the window of the FIRST reference image: an emptied bowl and a glass of water, with morning light "
 "falling across them in long shapes of bare paper white. No people, no hands. A thin trace of soup at the bottom of the bowl is the only vermilion.",
 "- an emptied bowl and a glass of water on a morning table with window light\n- no people or hands\n- only a thin trace of soup in the bowl is vermilion"),
}


def path(name, suffix=".png"):
    return os.path.join(OUT, f"{name}{suffix}") if name.startswith("S") else os.path.join(CUTS, f"{name}{suffix}")


def verdict(name):
    p = path(name, ".check.txt")
    lines = [l for l in open(p).read().splitlines() if l.startswith("VERDICT")] if os.path.exists(p) else []
    return lines[0].split(":", 1)[1].strip() if lines else ""


def draw(name):
    lead, scene, brief = SHOTS[name]
    frame = FRAME[INFO[name]["comp"]]
    refs = [path(r) for r in lead] + STYLE_REFS
    prompt = " ".join([COMMON, PAPER, VARIANT["a"], frame, scene, SUB[frame], NOTEXT, STYLE])
    with open(path(name, ".prompt.txt"), "w") as f: f.write(prompt + "\n")
    r = subprocess.run([GEN, ",".join(refs), prompt, path(name)], capture_output=True, text=True, env=ENV)
    with open(path(name, ".log"), "w") as f: f.write(r.stdout + r.stderr)
    if r.returncode or not os.path.exists(path(name)): return False
    subprocess.run(["python3", OVERLAY, PAPER_PNG, path(name), path(name, "_paper.png")], check=True, capture_output=True)
    for _ in range(2):  # 검수가 판정을 못 내면 한 번 더
        r = subprocess.run([CHECK, path(name), brief + SUB_BRIEF[frame]], capture_output=True, text=True, env=ENV)
        with open(path(name, ".check.txt"), "w") as f: f.write(r.stdout + r.stderr)
        if verdict(name): break
    return True


def job(name):
    if not os.path.exists(path(name)) and not draw(name):
        return f"{name}: FAIL to draw (see .log)"
    tries = 0
    while verdict(name) == "FAIL" and tries < RETRIES:  # 앞 판은 _try1·_try2로 남기고 다시 그린다
        tries += 1
        for suf in (".png", "_paper.png", ".check.txt", ".log"):
            if os.path.exists(path(name, suf)): shutil.move(path(name, suf), path(name, f"_try{tries}{suf}"))
        if not draw(name): return f"{name}: FAIL to draw (see .log)"
    return f"{name}: {verdict(name) or 'NO VERDICT'}" + (f" (다시 그림 {tries}번)" if tries else "")


def compare():
    font = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 22, index=6)
    tw, th, band, gap, cols = 480, 270, 34, 14, 4
    for k, (title, a, b) in enumerate(PARTS, 1):
        shots = [h for s in DATA["sections"][a:b] for x in s["scenes"] for h in x["shots"]]
        rows = (len(shots) + cols - 1) // cols
        sheet = Image.new("RGB", (gap + cols * (tw + gap), gap + rows * (band + th + gap)), "white")
        d = ImageDraw.Draw(sheet)
        for i, h in enumerate(shots):
            x, y = gap + (i % cols) * (tw + gap), gap + (i // cols) * (band + th + gap)
            src = path(h["id"], "_paper.png")
            d.text((x, y + 6), f"{h['id']} · {h['scene']}" + (f" (옛 {h['old']})" if h["old"] else ""), fill="black", font=font)
            if os.path.exists(src): sheet.paste(Image.open(src).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + band))
            else: d.rectangle((x, y + band, x + tw, y + band + th), outline="gray")
        sheet.save(os.path.join(HERE, f"compare_{k}.jpg"), quality=72, optimize=True)


if __name__ == "__main__":
    new = [h["id"] for h in ALL if h["src"] == "new" and not h["mg"]]  # 그림이 아직 없는 샷
    assert set(new) <= set(SHOTS), sorted(set(new) - set(SHOTS))
    todo = sys.argv[1:] or new
    done = set()
    while len(done) < len(todo):  # 이번에 함께 그리는 샷을 참조하는 샷은 그 샷이 끝난 뒤에
        wave = [n for n in todo if n not in done and not any(r in todo and r not in done for r in SHOTS[n][0])]
        with ThreadPoolExecutor(3) as ex:
            for line in ex.map(job, wave): print(line, flush=True)
        done.update(wave)
    compare(); print("비교 화면:", ", ".join(f"compare_{k}.jpg" for k in range(1, 5)))
