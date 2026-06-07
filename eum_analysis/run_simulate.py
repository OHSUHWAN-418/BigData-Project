"""
이음-Simulate — 처방 효과 시뮬레이션 + 위험점수 민감도

[설계] 창원 우승작이 'E2SFCA 재실행 before/after'로 효과를 증명했듯,
  이음도 처방을 반사실(counterfactual) 입력으로 넣고 자체 모델을 재계산해
  위험점수·지도의 before/after를 제시한다. (외부 데이터 불필요, 비순환)

[시나리오] 처방 대상(방문대비 소비부족형 산청·의령·합천 + 외지방문 의존형 하동·함양)에
  '방문 1인당 월 +1,000원' 객단가 개선이 달성된다고 가정.
    추가 연간매출 = 생활인구 × 12 × 1,000원   (부록 A와 동일 가정)
    → 매출↑ → MI·CPC 재계산 → 위험점수 재산정 (LRR·TREND는 보수적으로 고정)

[민감도] 위험점수 가중치를 base±0.05 범위에서 무작위 교란(N=3000)해도
  우선순위 TOP5가 유지되는지 검증.

[산출]
  phase2/simulate_result.csv
  phase2/p2_fig10_simulate_risk.png   (위험점수 before/after 막대)
  phase2/p2_fig11_simulate_map.png    (위험 지도 before/after)
  phase2/sensitivity_topk.csv
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

for fp in [Path('C:/Windows/Fonts/malgun.ttf'), Path('C:/Windows/Fonts/NanumGothic.ttf')]:
    if fp.exists():
        fm.fontManager.addfont(str(fp))
_n = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
_m = [f.name for f in fm.fontManager.ttflist if 'Malgun' in f.name]
plt.rcParams['font.family'] = _n[0] if _n else (_m[0] if _m else 'DejaVu Sans')
plt.rcParams['axes.unicode_minus'] = False

OUT = PROJECT_ROOT / 'phase2'
GEO = PROJECT_ROOT / 'geo' / 'skorea_municipalities.json'

RISK_WEIGHTS = {'MI': 0.40, 'CPC': 0.25, 'LRR': 0.20, 'TREND': 0.15}
TREATED = ['산청군', '의령군', '합천군', '하동군', '함양군']   # 처방 대상 (§5.1+§5.2)
PER_CAPITA_WON = 1000  # 방문 1인당 월 추가 소비


def minmax(s):
    span = s.max() - s.min()
    return s * 0 if span == 0 else (s - s.min()) / span


def risk_from(MI, CPC, LRR, TREND, w=RISK_WEIGHTS):
    return (minmax(-MI) * w['MI'] + minmax(-CPC) * w['CPC']
            + minmax(-LRR) * w['LRR'] + minmax(-TREND) * w['TREND'])


print("=" * 70)
print("이음-Simulate — 처방 효과 시뮬레이션 + 민감도")
print("=" * 70)

ind = pd.read_csv(OUT / 'indicators_phase2.csv', encoding='utf-8-sig', index_col=0)
ind.index.name = '시군구명'

pop = ind['연평균_생활인구']
sales0 = ind['연간매출']
LRR, TREND = ind['LRR'], ind['TREND']

# --- baseline 지표 ---
# 반사실(counterfactual) 정합성을 위해 ① MI 중심화 평균과 ② 위험점수 정규화 척도를
#   모두 '현행' 기준으로 고정한다. 그래야 처방받지 않은 시군은 그대로 두고
#   처방 시군만 개선되는 순수 정책효과를 분리할 수 있다(min-max 상대성 아티팩트 제거).
log_ratio0 = np.log(sales0 / pop)
MEAN0 = log_ratio0.mean()
MI0 = log_ratio0 - MEAN0
CPC0 = sales0 / pop / 12

# 부호 반전 성분의 현행 min/max(고정 척도)
comps0 = {'MI': -MI0, 'CPC': -CPC0, 'LRR': -LRR, 'TREND': -TREND}
SCALE = {k: (v.min(), v.max()) for k, v in comps0.items()}


def risk_fixed(MI, CPC):
    """현행 척도·평균 고정 위험점수 (반사실 계산용)."""
    comps = {'MI': -MI, 'CPC': -CPC, 'LRR': -LRR, 'TREND': -TREND}
    total = pd.Series(0.0, index=MI.index)
    for k, w in RISK_WEIGHTS.items():
        lo, hi = SCALE[k]
        total = total + (comps[k] - lo) / (hi - lo) * w
    return total


risk0 = risk_fixed(MI0, CPC0)
err = (risk0 - ind['위험점수']).abs().max()
print(f"\n  baseline 위험점수 재현 오차: {err:.6f}")

# --- 시나리오: 처방 대상 매출 증가 (현행 평균·척도 고정) ---
add = pd.Series(0.0, index=ind.index)
add[TREATED] = pop[TREATED] * 12 * PER_CAPITA_WON
sales1 = sales0 + add
MI1 = np.log(sales1 / pop) - MEAN0      # 평균 고정 → 미처방 시군 불변
CPC1 = sales1 / pop / 12
risk1 = risk_fixed(MI1, CPC1)

res = pd.DataFrame({
    'CPC_현행': CPC0, 'CPC_처방후': CPC1,
    '위험점수_현행': risk0, '위험점수_처방후': risk1,
    'Δ위험점수': risk1 - risk0, '처방대상': ind.index.isin(TREATED),
    '추가매출_억': add / 1e8,
}).sort_values('위험점수_현행', ascending=False)
res.to_csv(OUT / 'simulate_result.csv', encoding='utf-8-sig')

print("\n  [시나리오] 처방 대상(±1,000원/월) 위험점수 변화:")
for r, row in res.iterrows():
    mark = '◀처방' if row['처방대상'] else ''
    print(f"    {r}: {row['위험점수_현행']:.3f} → {row['위험점수_처방후']:.3f} "
          f"(Δ{row['Δ위험점수']:+.3f}) {mark}")

# ============================================================
# Figure 10: 위험점수 before/after 막대
# ============================================================
order = res.index.tolist()
y = np.arange(len(order))
fig, ax = plt.subplots(figsize=(11, 8))
ax.barh(y - 0.2, res['위험점수_현행'], height=0.38, color='#C0C0C0', label='현행')
colors_after = ['#A30015' if t else '#7FB3D5' for t in res['처방대상']]
ax.barh(y + 0.2, res['위험점수_처방후'], height=0.38, color=colors_after, label='처방 후(처방대상=진빨강)')
ax.set_yticks(y)
ax.set_yticklabels(order, fontsize=11)
ax.invert_yaxis()
ax.set_xlabel('위험점수', fontsize=12, fontweight='bold')
ax.set_title('이음-Simulate ① 처방 전·후 위험점수\n'
             '(처방 대상 5곳에 방문 1인당 월 +1,000원 가정)', fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.grid(axis='x', alpha=0.3)
for yi, r in enumerate(order):
    if res.loc[r, '처방대상']:
        ax.annotate(f"{res.loc[r,'Δ위험점수']:+.3f}",
                    (res.loc[r, '위험점수_처방후'], yi + 0.2),
                    fontsize=9, va='center', xytext=(4, 0), textcoords='offset points', color='#A30015')
plt.tight_layout()
plt.savefig(OUT / 'p2_fig10_simulate_risk.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig10_simulate_risk.png")

# ============================================================
# Figure 11: 위험 지도 before/after
# ============================================================
TARGETS = ['통영시', '사천시', '밀양시', '의령군', '함안군', '창녕군', '고성군',
           '남해군', '하동군', '산청군', '함양군', '거창군', '합천군']
gdf = gpd.read_file(GEO)
gdf['code'] = gdf['code'].astype(str)
gn = gdf[gdf['code'].str.startswith('38') & gdf['name'].isin(TARGETS)][['name', 'geometry']]
gn = gn.dissolve(by='name', as_index=False).to_crs(epsg=5179)
gn['cx'] = gn.geometry.centroid.x
gn['cy'] = gn.geometry.centroid.y
gn = gn.merge(res[['위험점수_현행', '위험점수_처방후']], left_on='name', right_index=True)

vmax = float(res['위험점수_현행'].max())
fig, axes = plt.subplots(1, 2, figsize=(20, 11))
for ax, col, title in [(axes[0], '위험점수_현행', '현행'), (axes[1], '위험점수_처방후', '처방 후')]:
    gn.plot(ax=ax, column=col, cmap='Reds', vmin=0, vmax=vmax,
            edgecolor='#444', linewidth=0.8, legend=True,
            legend_kwds={'label': '위험점수', 'shrink': 0.5})
    for _, r in gn.iterrows():
        ax.annotate(f"{r['name']}\n{r[col]:.2f}", (r['cx'], r['cy']),
                    ha='center', va='center', fontsize=8.5, fontweight='bold')
    ax.set_title(f'이음-Simulate ② 위험 지도 — {title}', fontsize=14, fontweight='bold')
    ax.axis('off')
plt.tight_layout()
plt.savefig(OUT / 'p2_fig11_simulate_map.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig11_simulate_map.png")

# ============================================================
# 민감도 분석: 가중치 ±0.05 무작위 교란 → TOP5 안정성
# ============================================================
print("\n  [민감도] 가중치 base±0.05 무작위 교란 (N=3000)")
rng = np.random.default_rng(42)
base = np.array([RISK_WEIGHTS['MI'], RISK_WEIGHTS['CPC'], RISK_WEIGHTS['LRR'], RISK_WEIGHTS['TREND']])
base_top5 = set(risk0.sort_values(ascending=False).index[:5])
N = 3000
same_top5 = 0
top2_ok = 0
rank_track = {r: [] for r in ind.index}
for _ in range(N):
    w = base + rng.uniform(-0.05, 0.05, 4)
    w = np.clip(w, 0.01, None); w = w / w.sum()
    wd = {'MI': w[0], 'CPC': w[1], 'LRR': w[2], 'TREND': w[3]}
    rk = risk_from(MI0, CPC0, LRR, TREND, wd).sort_values(ascending=False)
    if set(rk.index[:5]) == base_top5:
        same_top5 += 1
    if set(rk.index[:2]) == {'하동군', '함양군'}:
        top2_ok += 1
    for pos, r in enumerate(rk.index):
        rank_track[r].append(pos + 1)

print(f"    TOP5 집합 동일: {same_top5/N*100:.1f}%")
print(f"    TOP2 = {{하동,함양}} 유지: {top2_ok/N*100:.1f}%")
sens = pd.DataFrame({
    '평균순위': {r: np.mean(v) for r, v in rank_track.items()},
    '최저순위': {r: np.min(v) for r, v in rank_track.items()},
    '최고순위': {r: np.max(v) for r, v in rank_track.items()},
}).sort_values('평균순위')
sens.to_csv(OUT / 'sensitivity_topk.csv', encoding='utf-8-sig')
print("    시군별 순위 분포(평균/최저~최고):")
for r, row in sens.iterrows():
    print(f"      {r}: 평균 {row['평균순위']:.1f}위 (범위 {int(row['최저순위'])}~{int(row['최고순위'])}위)")

print("\n[산출 파일]")
for f in ['simulate_result.csv', 'p2_fig10_simulate_risk.png',
          'p2_fig11_simulate_map.png', 'sensitivity_topk.csv']:
    print(f"  • {OUT / f}")
