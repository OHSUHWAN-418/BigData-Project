# -*- coding: utf-8 -*-
"""그림1(1차 관찰) 2패널: (a) 1인당 월 소비 양극화 막대 + (b) 월별 생활인구 계절성(기존 fig3)"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.image as mpimg

ROOT = Path(__file__).resolve().parent
for fp in [Path("C:/Windows/Fonts/malgun.ttf")]:
    if fp.exists():
        fm.fontManager.addfont(str(fp))
plt.rcParams["font.family"] = [f.name for f in fm.fontManager.ttflist if "Malgun" in f.name][0]
plt.rcParams["axes.unicode_minus"] = False

ind = pd.read_csv(ROOT / "phase2/indicators_phase2.csv", encoding="utf-8-sig", index_col=0)
cpc = ind["CPC"].sort_values()

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13.8, 5.4), gridspec_kw={"width_ratios": [1, 1.45]})

colors = ["#A30015" if v < 17000 else ("#2A9D8F" if v > 50000 else "#9AA1AC") for v in cpc.values]
ax.barh(range(len(cpc)), cpc.values, color=colors)
ax.set_yticks(range(len(cpc)))
ax.set_yticklabels(cpc.index, fontsize=10.5)
ax.set_xlabel("방문 1인당 월 소비액 (원) = 연간 카드매출 ÷ 생활인구 ÷ 12", fontsize=10.5, fontweight="bold")
ax.set_title("(a) 1인당 소비의 양극화 — 최대 7.6배", fontsize=12.5, fontweight="bold")
ax.axvline(cpc.mean(), color="#555555", lw=1, ls="--")
ax.text(cpc.mean() + 800, 0.2, f"평균 {cpc.mean():,.0f}원", fontsize=9, color="#555555")
for i, (name, v) in enumerate(cpc.items()):
    ax.text(v + 800, i, f"{v:,.0f}", va="center", fontsize=8.5, color="#333333")
ax.set_xlim(0, cpc.max() * 1.16)
ax.grid(axis="x", alpha=0.3)

img = mpimg.imread(ROOT / "phase2/p2_fig3_monthly_population.png")
ax2.imshow(img)
ax2.axis("off")
ax2.set_title("(b) 월별 생활인구 — 계절 편중 (1월=100)", fontsize=12.5, fontweight="bold")

fig.suptitle("1차 관찰 — 방문(생활인구)과 소비(카드매출)는 비례하지 않는다", fontsize=14, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(ROOT / "phase2/p2_fig0_observations.png", dpi=150, bbox_inches="tight")
print("OK p2_fig0_observations.png")
