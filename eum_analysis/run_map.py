"""
이음(E-um) 지도 시각화 — 경남 13개 인구감소지역 Choropleth

[입력]
  - geo/skorea_municipalities.json : 통계청 2013 시군구 경계 GeoJSON
    (출처: github.com/southkorea/southkorea-maps, KOSTAT 2013)
  - phase2/indicators_phase2.csv   : run_phase2.py 산출 지표·침체유형·위험점수

[산출]
  - phase2/p2_fig5_map_type.png   : 침체 4유형 색상 지도
  - phase2/p2_fig6_map_risk.png   : 위험점수 단계 색상 지도(라벨에 순위)

경남 13개 시군은 통계청 코드 '38'로 필터링한다(고성군이 강원/경남 2곳이라 코드로 구분).
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트
for font_path in [Path('C:/Windows/Fonts/malgun.ttf'), Path('C:/Windows/Fonts/NanumGothic.ttf')]:
    if font_path.exists():
        fm.fontManager.addfont(str(font_path))
fonts = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
malgun_fonts = [f.name for f in fm.fontManager.ttflist if 'Malgun' in f.name]
plt.rcParams['font.family'] = fonts[0] if fonts else (malgun_fonts[0] if malgun_fonts else 'DejaVu Sans')
plt.rcParams['axes.unicode_minus'] = False

OUT = PROJECT_ROOT / 'phase2'
GEO = PROJECT_ROOT / 'geo' / 'skorea_municipalities.json'

TARGET_REGIONS = ['통영시', '사천시', '밀양시', '의령군', '함안군', '창녕군', '고성군',
                  '남해군', '하동군', '산청군', '함양군', '거창군', '합천군']

# 보고서와 통일한 유형 색상
type_colors = {
    '방문대비 소비부족형':        '#E63946',
    '외지방문 의존형': '#A30015',
    '소비 안정형':          '#2A9D8F',
    '혼합 경계형':          '#9AA0A6',
}

print("=" * 70)
print("「이음(E-um)」 지도 시각화 (경남 13개 인구감소지역)")
print("=" * 70)

# --- 지표 로딩 ---
ind = pd.read_csv(OUT / 'indicators_phase2.csv', encoding='utf-8-sig', index_col=0)
ind.index.name = '시군구명'
print(f"  지표 테이블: {ind.shape}, 시군 {ind.shape[0]}개")

# --- 경계 로딩 + 경남 13개 필터 (코드 38) ---
gdf = gpd.read_file(GEO)
gdf['code'] = gdf['code'].astype(str)
gn = gdf[gdf['code'].str.startswith('38') & gdf['name'].isin(TARGET_REGIONS)].copy()
gn = gn[['code', 'name', 'geometry']].dissolve(by='name', as_index=False)  # 멀티폴리곤 통합
print(f"  경남 경계 매칭: {gn['name'].tolist()}")
assert set(gn['name']) == set(TARGET_REGIONS), f"누락: {set(TARGET_REGIONS)-set(gn['name'])}"

# --- 지표 결합 ---
m = gn.merge(ind, left_on='name', right_index=True, how='left')
m = m.to_crs(epsg=5179)  # 한국 평면좌표(라벨 위치 계산용)
m['cx'] = m.geometry.centroid.x
m['cy'] = m.geometry.centroid.y


def _annotate(ax, frame, extra=None):
    """시군명(+부가텍스트)을 중심점에 라벨."""
    for _, r in frame.iterrows():
        label = r['name'] if extra is None else f"{r['name']}\n{extra(r)}"
        ax.annotate(label, (r['cx'], r['cy']), ha='center', va='center',
                    fontsize=9, fontweight='bold',
                    path_effects=None)


# ============================================================
# Figure 5: 침체 4유형 색상 지도
# ============================================================
fig, ax = plt.subplots(figsize=(11, 11))
used_types = [t for t in type_colors if (m['침체유형'] == t).any()]
for t in used_types:
    sub = m[m['침체유형'] == t]
    sub.plot(ax=ax, color=type_colors[t], edgecolor='white', linewidth=1.2)
m.boundary.plot(ax=ax, color='white', linewidth=1.2)
_annotate(ax, m)

# 범례
from matplotlib.patches import Patch
handles = [Patch(facecolor=type_colors[t], edgecolor='white',
                 label=f"{t} ({(m['침체유형']==t).sum()}개)") for t in used_types]
ax.legend(handles=handles, loc='upper right', fontsize=11, title='침체유형', title_fontsize=12)

ax.set_title('「이음(E-um)」 경남 13개 인구감소지역 침체유형 지도',
             fontsize=16, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig(OUT / 'p2_fig5_map_type.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig5_map_type.png")

# ============================================================
# Figure 6: 위험점수 Choropleth (+순위 라벨)
# ============================================================
rank = m.sort_values('위험점수', ascending=False).reset_index(drop=True)
rank_map = {name: i + 1 for i, name in enumerate(rank['name'])}
m['순위'] = m['name'].map(rank_map)

fig, ax = plt.subplots(figsize=(11, 11))
m.plot(ax=ax, column='위험점수', cmap='Reds', edgecolor='#444', linewidth=0.8,
       legend=True, legend_kwds={'label': '위험점수 (높을수록 우선 처방)', 'shrink': 0.6})
_annotate(ax, m, extra=lambda r: f"{r['순위']}위·{r['위험점수']:.2f}")

ax.set_title('「이음(E-um)」 위험점수 지도 — 우선 개선 대상',
             fontsize=16, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig(OUT / 'p2_fig6_map_risk.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig6_map_risk.png")

print("\n[산출 파일]")
print(f"  • {OUT / 'p2_fig5_map_type.png'}")
print(f"  • {OUT / 'p2_fig6_map_risk.png'}")
print("\n위험점수 순위:")
for i, r in rank.iterrows():
    print(f"  {i+1:2d}. {r['name']} {r['위험점수']:.3f}  ({r['침체유형']})")
