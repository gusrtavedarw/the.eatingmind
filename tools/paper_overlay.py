# 종이 질감 한 장을 그림 위에 같은 세기로 겹친다(soft light). 종이의 밝기 결만 쓰므로 그림의 색은 바뀌지 않는다.
# 실행: python3 tools/paper_overlay.py <paper.png> <in.png> <out.png> [세기=2.0]   (Pillow만 필요, 세기 2는 2026-11-22 그림체 시험에서 정함)
import sys
from PIL import Image, ImageChops, ImageStat

paper_path, in_path, out_path = sys.argv[1:4]
strength = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0

img = Image.open(in_path).convert("RGB")
g = Image.open(paper_path).convert("L").resize(img.size, Image.LANCZOS)
mean = ImageStat.Stat(g).mean[0]
tex = g.point(lambda v: max(0, min(255, round(128 + strength * 4 * (v - mean)))))  # 종이 결을 회색 128 중심으로
ImageChops.soft_light(img, Image.merge("RGB", (tex, tex, tex))).save(out_path)
print(out_path)
