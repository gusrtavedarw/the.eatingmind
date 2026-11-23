# 수프·팝콘 편 샷 리스트를 만든다(작업 2단계, 2026-11-23 합의): shotlist/샷리스트.md와 검토 페이지 데이터(storyboard/review/shots.json).
# 콘티 75장면(storyboard/review/conti.json, make_conti.py가 만듦)을 4초에 1컷 기준으로 샷으로 나눈다. 나누는 장면만 아래 SPLITS에 적고,
# 나머지 장면은 콘티 데이터를 그대로 한 샷으로 쓴다. 샷 문장을 이어 붙인 것이 녹음 대본 본문과 같은지 확인한다.
# 시간은 1분 시험 영상의 실제 내레이션 길이로 맞춘 예상치다. 4단계에서 전체 내레이션을 만든 뒤 실제 길이로 다시 맞춘다.
# 실행: python3 production/soup-popcorn/shotlist/make_shots.py
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(HERE)
CONTI = os.path.join(EP, "storyboard", "review", "conti.json")
OUT_JSON = os.path.join(EP, "storyboard", "review", "shots.json")
F, O = "화면 가득", "종이 위 오브제"
# 2026-11-23 1분 시험 영상: C01~C11 실제 58.8초 / 콘티 예상 71.5초. 읽는 장면에만 곱한다(C04 정적, C75 마지막 화면은 그대로).
RATIO = 0.822
DRAWN, NEW = "drawn", "new"

# 나누는 장면(대본분석.md §6 표, C45는 나누지 않음). 장면 번호 → [(읽는 문장 조각, 그림 출처, 그림, 구성, 주홍, 움직임·전환, 소리)]
# 그림 출처: DRAWN = 이 장면에 이미 그린 그림을 이 샷에 씀, NEW = 새로 그림. 소리 ""는 앞 샷에서 이어짐.
SPLITS = {
"C05": [
 ("별로 좋아하지 않는 과자인 데다,", NEW,
  "밤 거실 탁자 위에 놓인 과자 봉지를 옆에서 가까이 본다. 무늬도 글자도 없는 봉지이고, 화면 밖 TV 빛이 주름에 얇게 걸린다.",
  F, "봉지 입구에 비친 과자", "바로 컷, 아주 느린 밀기", "TV 소리 낮게"),
 ("누군가 먹다 놔둔 과자라서 첫 입은 조금 눅눅한 맛이었던 것 같습니다.", NEW,
  "입구를 한 번 접어 둔 봉지와, 그 앞에 꺼내 놓은 과자 한 조각. 과자 표면이 살짝 휘고 무르다.",
  F, "눅눅한 과자 한 조각", "바로 컷, 느린 밀기", ""),
 ("솔직히 그다음부터는 무슨 맛인지 잘 기억이 나지 않습니다.", DRAWN,
  "위에서 내려다본 탁자. 납작하게 쓰러진 빈 봉지와 흩어진 부스러기. 리모컨 모서리가 화면 끝에 걸린다.",
  F, "흩어진 부스러기", "바로 컷, 아주 느린 패닝", ""),
],
"C06": [
 ("그렇게 맛있지도 않았는데, 그만 먹겠다는 생각 자체가 나지 않았습니다.", DRAWN,
  "손이 봉지로 들어간 궤적이 여러 겹 남은 판화. 같은 손의 잔상 서너 개가 가는 해칭 선으로 겹치며 봉지 입구 한 점으로 모인다.",
  F, "봉지 입구의 과자", "느린 밀기", "봉지 바스락이 일정한 간격으로 서너 번"),
 ("기계적으로 과자를 집어 먹었던 것 같습니다.", NEW,
  "봉지 입구 가장자리를 가까이. 손이 같은 자리로만 드나들어 한쪽 가장자리만 반들반들 눌리고 구겨져 있다. 손은 보이지 않는다.",
  F, "입구 가장자리의 부스러기", "바로 컷, 느린 밀기", ""),
],
"C10": [
 ("먹는 마음을 이해하고, 나를 돌보는 지식.", DRAWN,
  "첫 인사. 빈 봉지가 반쯤 접혀 누워 있고 부스러기 몇 개가 흩어진 정물.",
  O, "부스러기", "정지에 가까운 느린 밀기", "낮은 음 이어짐"),
 ("안녕하세요, 먹는마음의 구스타브입니다.", NEW,
  "종이 위 부스러기 몇 점을 가까이 본 도판. 부스러기 사이로 종이 결이 보인다.",
  O, "부스러기", "바로 컷, 정지에 가까움", ""),
],
"C11": [
 ("오늘은 그 질문에서 한 가지를 살펴보겠습니다.", NEW,
  "빈 과자 봉지와 빈 접시가 종이 위에 나란히 놓인 도판. 봉지 입구가 접시 쪽을 향한다.",
  O, "봉지 입구의 부스러기 한 점", "바로 컷, 정지에 가까움", "낮은 음"),
 ("먹은 만큼 음식이 줄어드는 모습. 그 모습이 달라지면, 우리가 먹는 양도 달라질까요?", DRAWN,
  "같은 접시 세 개가 왼쪽부터 한 줄로 놓인 도판. 과자가 가득, 절반, 몇 조각으로 줄어든다.",
  O, "접시 위 과자", "바로 컷, 왼쪽에서 오른쪽으로 느린 패닝", ""),
],
"C20": [
 ("실험이 끝난 뒤 참가자에게 얼마나 배부른지도 물었습니다.", NEW,
  "빈 수프 그릇 앞에서, 직원의 손이 건넨 글자 없는 설문지 한 장을 참가자의 손이 받는다. 손과 소매만 보인다.",
  F, "그릇 바닥에 남은 수프 한 줄기", "바로 컷, 느린 밀기", "음악"),
 ("그 응답에서는 두 집단 사이에 뚜렷한 차이가 확인되지 않았습니다.", NEW,
  "글자 없는 설문지 두 장이 나란히 놓여 있다. 두 장 모두 눈금 칸의 비슷한 자리에 표시가 있다.",
  O, "두 장의 표시", "바로 컷, 느린 밀기", ""),
],
"C21": [
 ("칠십삼 퍼센트. 이 숫자를 얼마나 믿을 수 있을까요?", NEW,
  "가득 찬 자동 그릇 하나가 종이 위에 홀로 놓여 있고, 위에서 비추는 빛에 그림자가 길다.",
  O, "수프", "디졸브(구간 바뀜), 정지", "음악이 잠시 멈춤"),
 ("다른 팀이 이 실험을 해도 같은 결과가 나올까요?", NEW,
  "다른 실험실의 빈 식탁. 창과 벽이 처음 실험실과 다르고, 아직 아무것도 담기지 않은 같은 모양의 그릇 두 개만 놓여 있다.",
  F, "그릇 안쪽", "바로 컷, 느린 밀기", ""),
],
"C27": [
 ("그래도 수프가 줄어드는 모습이 달라지자", NEW,
  "위에서 본 두 그릇. 일반 그릇은 수프가 줄어 바닥이 보이고, 자동 그릇은 가장자리까지 가득하다.",
  O, "수프", "느린 밀기", "음악"),
 ("먹는 양도 달라진다는 결과는 다시 나왔습니다.", NEW,
  "처음 실험과 다시 한 실험의 식탁 단면이 종이 위에 나란히 놓인 작은 도판. 두 식탁 아래 모두 같은 통과 관이 있다.",
  O, "두 자동 그릇의 수프", "바로 컷, 정지에 가까움", "음악이 잦아듦"),
],
"C34": [
 ("맛이 썩 좋지 않아도 처음 주어진 양에 따라", NEW,
  "어두운 좌석에서 큰 통으로 다시 들어가는 손. 영사광이 손등에 걸린다.",
  F, "팝콘", "느린 밀기", "음악"),
 ("먹는 양이 달라질 수 있다는 사례로 보겠습니다.", NEW,
  "상영이 끝나 불이 켜진 좌석 줄. 팔걸이마다 놓인 통에 팝콘이 서로 다르게 남아 있다. 사람은 없다.",
  F, "통 속 남은 팝콘", "바로 컷, 느린 패닝", "음악이 잦아듦"),
],
"C35": [
 ("처음 질문으로 돌아가 볼까요?", NEW,
  "종이 위에 수프 그릇과 과자 봉지가 멀찍이 놓이고, 가는 점선 하나가 그릇에서 봉지로 이어진다.",
  O, "봉지 속 과자", "디졸브(구간 바뀜), 정지에 가까움", "낮은 음 하나(C07과 같은 음)"),
 ("봉지에 과자가 조금 더 있었다면, 같은 순간에 멈췄을까요?", NEW,
  "종이 위에 빈 봉지와 과자가 남은 봉지가 나란히 놓여 있다.",
  O, "남은 봉지 속 과자", "바로 컷, 느린 밀기", ""),
],
"C36": [
 ("평범한 그릇에서는 수프가 줄어드는 모습을 보고", NEW,
  "줄어드는 그릇. 안쪽 벽에 수프가 내려간 자국이 나이테처럼 여러 겹 남아 있다.",
  O, "수프", "느린 밀기", "차분한 음악"),
 ("얼마나 먹었는지 어림할 수 있습니다.", NEW,
  "숟가락이 막 떠낸 그릇 가장자리를 가까이. 수면이 한 칸 내려가 벽에 새 자국 선이 막 생겼다.",
  F, "수프", "바로 컷, 느린 밀기", ""),
],
"C37": [
 ("아래에서 조금씩 채워지는 그릇에서는 숟가락을 몇 번 움직여도", NEW,
  "가장자리까지 가득한 자동 그릇. 벽에 자국이 없고, 옆에 쓴 숟가락 여러 개가 가지런히 놓여 있다.",
  O, "수프", "느린 패닝", "음악"),
 ("그만큼 줄어든 흔적이 남지 않죠.", NEW,
  "그릇 바닥 가운데의 작은 구멍을 가까이. 구멍에서 수프가 천천히 올라와 수면이 가장자리까지 차 있다.",
  F, "수프", "바로 컷, 아주 느린 밀기", ""),
],
"C46": [
 ("어떤 날은 속이 충분하다고 느낄 때,", NEW,
  "수프가 조금 남은 그릇 옆에 숟가락을 내려놓는 손. 손과 소매만 보인다.",
  F, "남은 수프", "바로 컷, 느린 밀기", "음악"),
 ("어떤 날은 빈 접시를 볼 때 식사의 마침표를 찍습니다.", NEW,
  "깨끗이 빈 접시 하나가 종이 위에 놓인 정물.",
  O, "접시 가운데 마지막 부스러기 한 점", "바로 컷, 정지에 가까움", ""),
],
"C50": [
 ("봉지 안쪽이 잘 보이지 않으면", NEW,
  "불투명한 큰 과자 봉지를 종이 위에 세워 둔 표본 도판. 겉으로는 불룩해 안을 알 수 없다.",
  O, "입구 틈으로 보이는 과자 한 조각", "바로 컷, 정지에 가까움", "음악"),
 ("처음에 얼마나 있었는지, 지금 얼마나 남았는지 한눈에 알기 어렵습니다.", NEW,
  "같은 봉지를 반으로 자른 단면도. 바깥 윤곽은 불룩한데 안의 과자는 바닥에 조금만 있다.",
  O, "봉지 속 과자", "바로 컷, 느린 밀기", ""),
],
"C58": [
 ("같은 접시를 보고 있어도 그 접시가 내게 알려주는 정보는 달라집니다.", NEW,
  "가운데 접시를 수프 실험처럼 단면도로 그린 도판. 위에서 채우는 손이 수프 실험의 관과 같은 자리에 놓인다.",
  O, "접시 위 음식", "느린 밀기", "음악"),
 ("수프 그릇에서 봤던 차이가 조금 익숙하게 느껴지지 않나요?", NEW,
  "수프 실험의 자동 그릇 단면과 식탁 가운데 접시 단면이 종이 위에 나란히 놓인 도판. 채워지는 자리가 서로 닮았다.",
  O, "두 그릇의 음식", "바로 컷, 정지에 가까움", "음악이 잦아듦"),
],
"C66": [
 ("화면에 빠져 있는 동안 손을 멈출 만한 계기가 있었을까요?", NEW,
  "TV 빛을 받은 탁자 위 봉지, 그 뒤로 흐릿한 소파. 화면은 내용 없는 흰 빛 네모다.",
  F, "봉지 속 과자", "느린 밀기", "음악"),
 ("우리는 그날의 이유를 다 알 수 없습니다.", NEW,
  "불 꺼진 거실. TV도 꺼졌고, 소파에는 앉았던 자리만 움푹 남아 있다. 탁자 위 빈 봉지가 어둠 속에 희미하다.",
  F, "빈 봉지 속 부스러기", "바로 컷, 아주 느린 밀기", ""),
],
"C67": [
 ("그래도 빈 봉지 하나를 보고 ‘또 다 먹었네’ 하고 지나갈 때보다,", NEW,
  "손에 구겨 쥐었다가 놓은 듯 뭉쳐진 빈 봉지 한 덩이가 종이 위에 놓인 도판.",
  O, "뭉친 봉지 틈의 부스러기", "바로 컷, 정지", "음악"),
 ("그 사이에 무슨 일이 있었는지 조금 더 구체적으로 물을 수 있습니다.", NEW,
  "빈 봉지를 펼쳐 평평하게 놓은 표본 도판. 안쪽 은박이 드러나 있다.",
  O, "남은 부스러기 몇 점", "바로 컷, 느린 밀기", "음악이 잦아듦"),
],
"C70": [
 ("속이 편안하게 찼을 수도,", NEW,
  "종이 위에 작은 위 해부도 하나, 그 아래에 마침표 점 하나.",
  O, "마침표 점", "바로 컷, 정지에 가까움", "음악"),
 ("맛이 처음만큼 당기지 않았을 수도 있습니다.", NEW,
  "반찬이 한 점 남은 접시 하나, 그 아래에 마침표 점 하나. 점은 앞 그림과 같은 자리에 있다.",
  O, "마침표 점", "바로 컷, 정지에 가까움", ""),
 ("접시에 남은 게 없었거나, 여러 이유가 한꺼번에 겹쳤을 수도 있죠.", NEW,
  "빈 접시 하나와 그 아래 마침표 점. 앞의 위와 반찬 접시가 화면 가장자리에 작게 겹쳐 들어온다.",
  O, "마침표 점", "바로 컷, 왼쪽에서 오른쪽으로 느린 패닝", ""),
],
}
# 나누지 않는 장면 가운데 앞 장면을 이어 그리는 것(콘티 '같은 그림'): 장면 → (관계, 앞 장면)
LINKS = {"C25": ("next", "C19"), "C40": ("next", "C39"), "C59": ("ref", "C02"), "C60": ("ref", "C04")}
NOTES = [
    ("기준 속도", f"1분 시험 영상의 실제 내레이션 길이(콘티 예상의 {RATIO}배)로 맞춘 예상 시간. 읽지 않는 장면(C04 정적, C75 마지막 화면)은 그대로. 4단계에서 전체 녹음 뒤 실제 길이로 다시 맞춘다."),
    ("나누기", "[대본 분석](../storyboard/대본분석.md) §6 표대로 17장면을 나눈다. 핵심 그림 C45는 한 장으로 둔다. 장면 안에서 샷이 바뀔 때는 바로 컷, 장면의 첫 샷은 콘티의 전환을 따른다."),
    ("그림", "샷마다 다른 그림. 이미 그린 19장은 한 번씩만 쓴다. 같은 장면의 상태 변화는 앞 그림을 참고해 새로 그린다."),
    ("화면 가득으로 바꾼 샷", "종이 위 도판이 이어지는 곳을 덜 단조롭게: C20 첫째, C21 둘째, C36 둘째, C37 둘째, C46 첫째."),
    ("사람·주홍·자막 자리", "[콘티](../storyboard/콘티.md)의 '정한 것'과 대본 분석 §4·§5를 따른다."),
    ("그림 설명", "한국어로만 쓴다. 그림을 그릴 영어 문구는 3단계(이미지 제작)에서 쓴다."),
]

def syl(t): return len(re.findall(r"[가-힣]", t))
def mmss(x): x = round(x); return f"{x // 60}:{x % 60:02d}"
def norm(t): return re.sub(r"\s+", " ", t).strip()

conti = json.load(open(CONTI, encoding="utf-8"))
scenes = {c["id"]: c for s in conti["sections"] for c in s["cuts"]}

# 1) 나누는 장면: 조각을 이어 붙이면 장면 문장과 같고, 이미 그린 그림은 그린 장면에서만 한 번
for cid, parts in SPLITS.items():
    if norm(" ".join(p[0] for p in parts)) != norm(scenes[cid]["text"]):
        sys.exit(f"{cid}: 조각을 이으면 장면 문장과 다르다")
    want = 1 if scenes[cid]["img"] else 0
    if sum(p[1] == DRAWN for p in parts) != want:
        sys.exit(f"{cid}: 이미 그린 그림을 {want}번 써야 한다")

# 2) 샷 만들기
shots, sections, first_shot = [], [], {}
t = 0.0
for sec in conti["sections"]:
    s0, sec_scenes = t, []
    for c in sec["cuts"]:
        dur = c["dur"] * RATIO if c["text"] else c["dur"]
        if c["id"] in SPLITS:
            parts = SPLITS[c["id"]]
        else:
            parts = [(c["text"], DRAWN if c["img"] else NEW, c["pic"], c["comp"], c["accent"], c["motion"], c["sound"])]
        total = sum(syl(p[0]) for p in parts) or 1
        mine = []
        for k, (text, src, pic, comp, acc, mov, snd) in enumerate(parts):
            d = dur * syl(text) / total if len(parts) > 1 else dur
            sid = f"S{len(shots) + 1:03d}"
            label, img = (f"이미 그림({c['id']})", c["img"]) if src == DRAWN else ("새로 그림", None)
            if c["id"] in LINKS:
                rel, prev = LINKS[c["id"]]
                label += f" · {first_shot[prev]}의 다음 상태" if rel == "next" else f" · {first_shot[prev]} 구도 참고"
            shot = dict(id=sid, scene=c["id"], part=f"{k + 1}/{len(parts)}", t0=round(t, 1), dur=round(d, 1), start=mmss(t), end=mmss(t + d),
                        text=text, src=src, src_label=label, pic=pic, comp=comp, accent=acc, motion=mov,
                        sound=snd or "앞 샷에서 이어짐", screen=c["screen"] if k == 0 else "", img=img)
            shots.append(shot); mine.append(shot); t += d
        first_shot[c["id"]] = mine[0]["id"]
        sec_scenes.append(dict(id=c["id"], pic=c["pic"], shots=mine))
    sections.append(dict(name=sec["name"], t0=round(s0, 1), secs=round(t - s0, 1), start=mmss(s0), end=mmss(t), scenes=sec_scenes))

# 3) 확인: 샷 문장을 이으면 녹음 대본 본문과 같다(make_conti.py와 같은 방식), 이미 그린 그림은 모두 한 번씩
lines = open(os.path.join(EP, "내레이션_녹음용.txt"), encoding="utf-8").read().splitlines()[3:]
body = norm(" ".join(l for l in lines if l.strip() and not l.strip().startswith("[")))
if norm(" ".join(s["text"] for s in shots if s["text"])) != body:
    sys.exit("샷 문장이 대본과 다르다")
used = sorted(s["scene"] for s in shots if s["src"] == DRAWN)
if used != sorted(conti["drawn"]):
    sys.exit(f"이미 그린 그림 사용이 맞지 않다: {used}")

n, n_new = len(shots), sum(s["src"] == NEW for s in shots)
n_full = sum(s["comp"] == F for s in shots)
avg = t / n
print(f"샷 {n}개(장면 {len(scenes)}개, 나눈 장면 {len(SPLITS)}개), 전체 {mmss(t)} ({t:.0f}초), 평균 {avg:.1f}초")
print(f"이미 그림 {n - n_new} · 새로 그림 {n_new} · 화면 가득 {n_full} · 종이 위 오브제 {n - n_full}")
for s in sections: print(f"  {s['name']}: {s['start']}–{s['end']} {s['secs']:.0f}초 {sum(len(x['shots']) for x in s['scenes'])}샷")
print("2초 미만:", [(s["id"], s["scene"], s["dur"]) for s in shots if s["dur"] < 2])
print("6초 넘음:", [(s["id"], s["scene"], s["dur"]) for s in shots if s["dur"] > 6 and s["scene"] != "C75"])

# 4) 샷리스트.md
summary = "\n".join(f"| {s['name']} | {s['start']}–{s['end']} | {s['secs']:.0f}초 | {len(s['scenes'])} | {sum(len(x['shots']) for x in s['scenes'])} |" for s in sections)
out = [f"""# 먹는마음 · 수프·팝콘 편 샷 리스트 (v1)

작업 2단계 문서입니다. [화면 콘티](../storyboard/콘티.md)의 75장면을 4초에 1컷 기준으로 나눴습니다. 이 문서와 검토 페이지 데이터(`storyboard/review/shots.json`)는 [make_shots.py](make_shots.py)가 함께 만듭니다. 샷의 '읽는 문장'을 이어 붙이면 [녹음 대본](../내레이션_녹음용.txt) 본문과 같습니다.

**{n}샷 · 약 {mmss(t)}(마지막 화면 10초 포함) · 샷 평균 {avg:.1f}초 · 이미 그린 그림 {n - n_new}장 · 새로 그릴 그림 {n_new}장 · 화면 가득 {n_full}샷, 종이 위 오브제 {n - n_full}샷**

## 정한 것

| 항목 | 기준 |
|---|---|
""" + "\n".join(f"| {k} | {v} |" for k, v in NOTES) + f"""

## 구간별 시간

| 구간 | 시간 | 길이 | 장면 | 샷 |
|---|---|---|---|---|
{summary}
"""]
for s in sections:
    out.append(f"\n## {s['name']} · {s['start']}–{s['end']} · {sum(len(x['shots']) for x in s['scenes'])}샷\n")
    out.append("| 샷 | 장면 | 시간 | 읽는 문장 | 그림 출처 | 그림 | 구성 | 주홍 | 움직임·전환 | 소리 | 화면 글자 |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for x in s["scenes"]:
        for h in x["shots"]:
            scene = h["scene"] + (f" ({h['part']})" if h["part"] != "1/1" else "")
            out.append(f"| {h['id']} | {scene} | {h['start']}–{h['end']} ({h['dur']:.1f}초) | {h['text'] or '(읽지 않음)'} | {h['src_label']} | {h['pic']} | {h['comp']} | {h['accent']} | {h['motion']} | {h['sound']} | {h['screen'] or '—'} |")
open(os.path.join(HERE, "샷리스트.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")

json.dump(dict(title="수프·팝콘 편", shots=n, scenes=len(scenes), splits=len(SPLITS), total=round(t, 1), total_mmss=mmss(t), avg=round(avg, 1),
               ratio=RATIO, drawn=n - n_new, new=n_new, full=n_full, obj=n - n_full, notes=NOTES, sections=sections),
          open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
