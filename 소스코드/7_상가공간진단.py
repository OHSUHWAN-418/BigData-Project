"""
이음(E-um) — 상가정보 기반 공간 진단 (처방전 카드 근거)

[목적] 우선 처방지(하동)에서 '관광 통과 → 체류 전환' 처방을 공간적으로 구체화.
  소상공인 상가(상권)정보로 읍·면별 체류 인프라(숙박+예술·스포츠) 분포를 분석해,
  체류 인프라가 '어디에 쏠려 있고 어디가 공백인지' 식별한다.

[입력] data/상가정보_13시군.csv (소상공인시장진흥공단 상가정보, 경남 13시군 부분집합)
[산출] phase2/p2_fig13_hadong_shop.png, phase2/hadong_shop.csv
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

for fp in [Path('C:/Windows/Fonts/malgun.ttf'), Path('C:/Windows/Fonts/NanumGothic.ttf')]:
    if fp.exists():
        fm.fontManager.addfont(str(fp))
_n = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
_m = [f.name for f in fm.fontManager.ttflist if 'Malgun' in f.name]
plt.rcParams['font.family'] = _n[0] if _n else (_m[0] if _m else 'DejaVu Sans')
plt.rcParams['axes.unicode_minus'] = False

OUT = PROJECT_ROOT / 'phase2'
DATA = PROJECT_ROOT.parent / 'eum_package' / 'data' / '상가정보_13시군.csv'
REGION = '하동군'
STAY = ['숙박', '예술·스포츠']  # 체류 인프라(머무름)

print("=" * 70)
print(f"이음(E-um) — {REGION} 상가 공간 진단")
print("=" * 70)

df = pd.read_csv(DATA, encoding='utf-8-sig', usecols=['시군구명', '상권업종대분류명', '행정동명'])
h = df[df['시군구명'] == REGION]
g = h.groupby('행정동명').agg(
    점포수=('상권업종대분류명', 'size'),
    체류수=('상권업종대분류명', lambda s: s.isin(STAY).sum()),
)
g['체류비중'] = (g['체류수'] / g['점포수'] * 100).round(1)
g = g.sort_values('점포수', ascending=False)
g.to_csv(OUT / 'hadong_shop.csv', encoding='utf-8-sig')
print(g.to_string())
print(f"\n  {REGION} 전체 체류비중: {h['상권업종대분류명'].isin(STAY).sum()/len(h)*100:.1f}%  (점포 {len(h):,}개)")

# --- 산점도: 점포수 vs 체류비중 (사분면) ---
mx = g['점포수'].median()
my = g['체류비중'].median()
fig, ax = plt.subplots(figsize=(11, 7.5))
for name, r in g.iterrows():
    # 점포 많고(우) 체류 낮음(하) = 처방 우선(공백) → 빨강
    gap = (r['점포수'] >= mx) and (r['체류비중'] < my)
    hub = r['체류비중'] >= 25
    color = '#A30015' if gap else ('#2A9D8F' if hub else '#9AA0A6')
    ax.scatter(r['점포수'], r['체류비중'], s=140, c=color, edgecolors='black', linewidth=1, zorder=3)
    ax.annotate(name, (r['점포수'], r['체류비중']), fontsize=10, fontweight='bold',
                xytext=(6, 4), textcoords='offset points')
ax.axvline(mx, color='gray', ls='--', alpha=0.5)
ax.axhline(my, color='gray', ls='--', alpha=0.5)
ax.text(0.98, 0.03, '점포 多·체류 少 = 체류전환 우선(공백)', transform=ax.transAxes,
        ha='right', fontsize=10, color='#A30015', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#FFF0F0', alpha=0.8))
ax.text(0.02, 0.97, '체류 인프라 거점(관광지)', transform=ax.transAxes,
        va='top', fontsize=10, color='#2A9D8F', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#E8F5F2', alpha=0.8))
ax.set_xlabel('읍·면 점포 수', fontsize=12, fontweight='bold')
ax.set_ylabel('체류 인프라 비중 (숙박+여가, %)', fontsize=12, fontweight='bold')
ax.set_title(f'{REGION} 읍·면별 체류 인프라 분포 (소상공인 상가정보)\n'
             '체류 숙박·여가가 화개·청암(관광지)에 편중, 하동읍·진교면은 공백',
             fontsize=13, fontweight='bold')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / 'p2_fig13_hadong_shop.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n  ✓ p2_fig13_hadong_shop.png")
print(f"  ✓ {OUT / 'hadong_shop.csv'}")

# ============================================================
# Part 2. 개선 카드 4곳(하동·합천·남해·거창) 읍·면 체류 인프라 — 2×2 패널
# ============================================================
CARD_REGIONS = ['하동군', '합천군', '남해군', '거창군']
fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.2))
print("\n[개선 카드 4곳 읍·면 체류 인프라]")
for ax, region in zip(axes.flat, CARD_REGIONS):
    r0 = df[df['시군구명'] == region]
    g2 = r0.groupby('행정동명').agg(
        점포수=('상권업종대분류명', 'size'),
        체류수=('상권업종대분류명', lambda s: s.isin(STAY).sum()),
    )
    g2['체류비중'] = (g2['체류수'] / g2['점포수'] * 100).round(1)
    total = r0['상권업종대분류명'].isin(STAY).sum() / len(r0) * 100
    mx2, my2 = g2['점포수'].median(), g2['체류비중'].median()
    gaps = []
    for name, r in g2.iterrows():
        gap = (r['점포수'] >= mx2) and (r['체류비중'] < my2)
        hub = r['체류비중'] >= 25
        if gap:
            gaps.append(name)
        c = '#A30015' if gap else ('#2A9D8F' if hub else '#9AA0A6')
        ax.scatter(r['점포수'], r['체류비중'], s=70, c=c, edgecolors='black', linewidth=0.7, zorder=3)
        ax.annotate(name, (r['점포수'], r['체류비중']), fontsize=7.5, xytext=(4, 3), textcoords='offset points')
    ax.axvline(mx2, color='gray', ls='--', alpha=0.4)
    ax.axhline(my2, color='gray', ls='--', alpha=0.4)
    ax.set_title(f"{region} — 전체 체류비중 {total:.1f}%", fontsize=12, fontweight='bold')
    ax.grid(alpha=0.25)
    ax.tick_params(labelsize=8)
    print(f"  {region}: 전체 {total:.1f}% / 공백(점포多·체류少): {', '.join(gaps) if gaps else '없음'}")
fig.supxlabel('읍·면 점포 수', fontsize=11, fontweight='bold')
fig.supylabel('체류 인프라 비중 (숙박+여가, %)', fontsize=11, fontweight='bold')
fig.suptitle('개선 카드 4곳의 읍·면별 체류 인프라 분포 — 빨강 = 점포 많고 체류 적음(공백), 초록 = 체류 거점',
             fontsize=13, fontweight='bold')
plt.tight_layout(rect=[0.015, 0.015, 1, 0.96])
plt.savefig(OUT / 'p2_fig13b_shop_4regions.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig13b_shop_4regions.png")
