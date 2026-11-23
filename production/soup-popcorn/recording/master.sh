#!/usr/bin/env bash
# 구스타브 내레이션 후처리(2026-11-23): 저음 자르기 → 잡음 줄이기(anlmdn+afftdn) → 치찰음 누르기 → 쉼 잡음 낮추기(게이트) → 가벼운 압축 → -16 LUFS, 최대 -1.5dBTP, 48kHz. 쉼 잡음이 말소리보다 약 50dB 낮아짐(v3)
# 사용: master.sh <입력.wav> <출력.wav>
set -euo pipefail
ffmpeg -v error -y -i "$1" -af "highpass=f=75,anlmdn=s=0.0008,afftdn=nr=15:nf=-50:tn=1,deesser=i=0.4,agate=threshold=0.016:ratio=4:range=0.03:attack=3:release=200,acompressor=threshold=-22dB:ratio=2:attack=8:release=150,loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -ac 1 "$2"
