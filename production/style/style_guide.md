# 먹는마음 그림체 가이드 (v1)

영상 그림을 그릴 때 따르는 기준이다. 2026-11-22 grill-me로 정하고, 시험 그림 세 판(`tests/v1~v3`)을 거쳐 기준 그림(`refs/`)을 정했다.

## 한 줄 요약

**크림색 종이 위 먹선 판화. 해칭으로만 명암을 만들고, 주홍 하나로 장면이 끌어당기는 것을 가리킨다.**

기존 기획의 시각 방향("종교 판화 같은 강한 명암과 세밀한 선, 먹는 행위에 섞인 여러 감정")을 잇는다.

## 정한 것

| 항목 | 기준 |
|---|---|
| 바탕 | 연한 크림색 종이. **화면 전체에 종이 질감**(결·섬유)이 보이게 한다. 검은 면과 주홍 위에도 비친다. 프롬프트만으로는 화면 가득 장면에서 질감이 약해서, 같은 종이 질감 한 장(`refs/paper.png`)을 모든 그림 위에 **세기 2**로 겹친다(`tools/paper_overlay.py`). |
| 선 | **중성 검정** 먹선(갈색·세피아 아님). 명암은 해칭·크로스해칭으로만 낸다. 칠이나 그라데이션은 쓰지 않는다. |
| 해칭 | **동판화식**(가는 평행선·크로스해칭을 촘촘하게). v1 시험에서 목판화보다 낫다고 정함. |
| 색 | 별색 **주홍(버밀리언) 하나**: 무광 붉은 주황 인쇄 잉크(대략 `#D2452B`). 형광·분홍·연어색·갈색으로 빠지지 않게 색을 구체적으로 적는다("탁하게"라고만 쓰면 v2처럼 분홍·갈색이 됨). 장면에서 끌어당기는 대상(음식, 손이 가는 곳, 감정)에만 칠한다. 나머지는 전부 먹선. |
| 명암 | 강한 명암. 그림자는 깊고 넓게, 촘촘한 크로스해칭으로 검은 면을 크게 만든다. |
| 장면 구성 | 생활 장면은 16:9 화면을 **가득** 채운다. 실험·개념도는 **종이 위 단독 오브제**(표본 도판처럼 여백을 넉넉히). |
| 사람 | 어른 실제 비율. 얼굴은 명암 속에 반쯤 묻히거나 돌려 두어, 누구나 자기 모습으로 볼 수 있게 한다. 구스타브 캐릭터는 넣지 않는다. |
| 글자 | 그림 안에 글자·숫자·로고·상표를 넣지 않는다. 이름표는 편집 단계에서 자막·카드로 얹는다. |
| 정서 | 낯설고 고요한 긴장. 공포·잔혹 표현은 쓰지 않는다. 먹는 사람이나 음식을 죄악·추함으로 그리지 않는다. |
| 배경 | 보이는 공간은 현대 한국의 평범한 생활 공간. |

## 해칭 방식: a 동판화로 정함

| 변형 | 방식 | v1 시험 결과 |
|---|---|---|
| **a 동판화 (채택)** | 가는 평행선과 크로스해칭을 아주 촘촘하게. 하늘·벽·식탁보 같은 넓은 면도 선으로 채운다. v2부터 그림자를 더 깊고 넓게. | 세밀한 선이 기존 방향에 맞음 |
| b 목판화 | 넓은 검은 면에 흰 선을 파낸 듯한 굵은 획. | 굵은 동판화처럼 나와 목판화 느낌이 약함 |

## 참고한 특징 (출처 그림은 저장하지 않음)

Pinterest 보드 `hatching_draw`의 그림 30장을 보고, 아래 특징만 글로 옮겼다. 다른 작가의 그림은 그림 생성기에 참조로 넣지 않는다.

- 하늘과 구름까지 평행선으로 채운 동판화식 밀도
- 판화 해칭과 단순한 도형(줄무늬 원 같은)의 대비
- 목판화의 강한 흑백 명암
- 먹선 인물 위에 별색 하나로 감정을 얹는 방식
- 감정을 머리에서 흘러나오는 선의 흐름으로 보여 주는 방식
- (보조) 펜 스케치·책 삽화의 생활 장면 구도와 소품

## 프롬프트 문구 (영어 그대로 넣는다)

`make_tests.py`가 같은 문구를 쓴다. 고칠 때는 두 곳을 함께 고친다.

공통:
```
Original illustration in the manner of fine-art printmaking: neutral black ink (true black, never brown or sepia) printed on pale cream paper. Strong chiaroscuro with deep blacks and bright paper whites; all shading is built from hatching and cross-hatching lines, never painted fills or smooth gradients. Exactly ONE accent color: a matte red-orange printing ink (vermilion, around #D2452B), opaque and flat like screen-print ink; never pink, never salmon, never brown, never neon. It is used only on the single thing that pulls attention in the scene; everything else stays black ink on cream paper. Adults have realistic proportions; faces are partly hidden in shadow, cropped or turned away. Calm, slightly uncanny stillness: tension comes from light, shadow and composition, never horror or gore, and the eater is never shown as guilty, ugly or sinful. Any visible setting is an ordinary modern Korean home.
```

종이 질감 (화면 전체):
```
Paper texture over the WHOLE frame: the image looks printed on real handmade paper, with fine paper grain and faint fibers visible everywhere, including through the black ink areas and the vermilion, with slight ink unevenness where the ink meets the paper.
```

글자 금지:
```
No text, letters, numbers, logos, labels or brand marks anywhere; packaging and papers show only blank shapes.
```

해칭 (a 동판화):
```
Hatching treatment: copperplate etching / steel engraving. Very fine, dense parallel lines and cross-hatching that follow the form; even large planes such as walls, tablecloth, sky and background are filled with fine parallel line tones. Crisp, meticulous, highly detailed. Shadows are deep and wide: build broad, strong black areas from very dense cross-hatching so the darks read boldly.
```

화면 가득 (생활 장면):
```
Compose the scene to fill the entire 16:9 frame edge to edge: no blank margins, no border, no frame.
```

종이 위 오브제 (실험·개념도):
```
No background scene: the subject sits alone on plain cream paper with generous empty paper around it, like a printed specimen plate, with a soft hatched shadow beneath it.
```

## 시험 기록 (수프·팝콘 편 장면)

| 장면 | 내용 | 구성 |
|---|---|---|
| s1 | 식탁 위 과자 봉지로 다시 들어가는 손 (오프닝) | 화면 가득 |
| s2 | 아래 통에서 관으로 그릇을 다시 채우는 식탁 단면도 (실험). 관 안에 위쪽 화살표와 올라가는 기포로 방향을 보인다. | 종이 위 오브제 |
| s3 | 위 · 팝콘 그릇 · 같은 팝콘 한 줌을 담은 작은 접시(테두리에 마침표 같은 점) (개념도) | 종이 위 오브제 |

| 판 | 폴더 | 내용 | 결과 |
|---|---|---|---|
| v1 | `tests/v1/` | 3장면 × a 동판화·b 목판화, 6장 | a로 정함. 갈색 세피아 톤, 형광 같은 주홍, s2 흐름이 아래로 읽힘, s3 접시가 패티처럼 보임 |
| v2 | `tests/v2/` | 3장면 × a, 3장. 검정 먹선·연한 크림·탁한 주홍·더 깊은 그림자·화면 전체 종이 질감, s2·s3 고침 | 방향 확정. 주홍이 s3 분홍·s1 갈색으로 흔들림, s1 어두운 부분에 종이 결이 거의 없음 |
| v3 | `tests/v3/` | 3장면 + 종이 질감 1장. 주홍을 색으로 고정, 종이 질감을 겹친 판(`*_paper.png`, 세기 1)과 비교 | 주홍이 세 장면 모두 같은 붉은 주황으로 나옴. 세기 1은 거의 안 보여서 세기 0~4를 원본 크기로 비교한 뒤 **세기 2**로 정함. s1·s3·종이를 기준 그림으로 정함 |

저장소에는 판마다 비교 화면(`tests/v*/compare.png`)과 프롬프트(`*.prompt.txt`)만 올린다. 시험 그림 낱장과 로그는 이 컴퓨터에만 있다(`.gitignore`).

크기 1536×864. 그리기: `python3 production/style/make_tests.py` (판은 스크립트의 `VER`, 이미 있는 파일은 건너뛴다). 참조 그림 없이 `tools/gen-ref.sh`로 그리고, codex 모델은 `CODEX_MODEL=gpt-6.1-sol`로 지정한다(기본 모델은 ChatGPT 계정에서 거부됨). 사람 손이 나오는 s1은 `tools/check-img.sh`로 손·팔을 검수한다.

## 기준 그림 (`refs/`)

| 파일 | 내용 | 쓰는 곳 |
|---|---|---|
| `style_scene.png` | v3 s1, 과자 봉지로 들어가는 손 | 화면 가득 장면의 그림체 기준 |
| `style_object.png` | v3 s3, 위·팝콘 그릇·팝콘 한 줌 접시 | 종이 위 오브제의 그림체 기준 |
| `paper.png` | 연한 크림색 수제 종이 | 다 그린 뒤 모든 그림에 겹칠 종이 질감 |

## 앞으로 그릴 때

1. 프롬프트는 위의 공통 + 종이 질감 + 해칭 + (화면 가득 또는 종이 위 오브제) + 장면 설명 + 글자 금지 순서로 쓴다.
2. 그리기: `CODEX_MODEL=gpt-6.1-sol tools/gen-ref.sh "production/style/refs/style_scene.png,production/style/refs/style_object.png" "<프롬프트>" <out.png>`. 앞 장면을 이어받는 그림이면 그 그림을 목록 맨 앞에 쉼표로 더한다. 기준 그림 두 장은 늘 목록 끝에 두고, 프롬프트에 "match the drawing style of the last two reference images (ignore their subjects)"를 넣는다.
3. 사람이 나오면 `tools/check-img.sh`로 손·팔을 검수하고, 팔 부분은 확대해서 직접 본다.
4. 마지막에 종이 질감을 겹친다: `python3 tools/paper_overlay.py production/style/refs/paper.png <그림.png> <결과.png>` (기본 세기 2). 종이의 밝기 결만 soft light로 겹쳐 그림 색은 바꾸지 않는다.
