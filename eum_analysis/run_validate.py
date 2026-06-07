"""
이음(E-um) — MI 구성타당도(construct validity) 검증

[목적]
  MI·위험점수는 카드매출+생활인구로 만든 자체 지표다. 이것이 실제 상권 침체를
  포착하는지, **출처가 독립인** 사업체 데이터로 검증한다.

[독립 검증지표]
  소비업종(도매·소매 + 숙박·음식점) 사업체수의 2023→2024 증감률.
  - 증감률(%)이므로 인구 규모 효과가 제거된 '상권 위축' 신호.
  - 가설: MI 낮을수록(소비전환 취약) 소비업종 사업체 감소 → 양(+)의 상관.
          위험점수 높을수록 사업체 감소 → 음(-)의 상관.

[입력]
  - data/사업체수_시군_2023_2024.xlsx (KOSIS 전국사업체조사, 경남 시군별)
  - phase2/indicators_phase2.csv

[산출]
  - phase2/validation_business.csv
  - phase2/p2_fig9_validation.png
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
from scipy import stats

for font_path in [Path('C:/Windows/Fonts/malgun.ttf'), Path('C:/Windows/Fonts/NanumGothic.ttf')]:
    if font_path.exists():
        fm.fontManager.addfont(str(font_path))
fonts = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
malgun = [f.name for f in fm.fontManager.ttflist if 'Malgun' in f.name]
plt.rcParams['font.family'] = fonts[0] if fonts else (malgun[0] if malgun else 'DejaVu Sans')
plt.rcParams['axes.unicode_minus'] = False

OUT = PROJECT_ROOT / 'phase2'
DATA = PROJECT_ROOT.parent / 'eum_package' / 'data' / '사업체수_시군_2023_2024.xlsx'

TARGET_REGIONS = ['통영시', '사천시', '밀양시', '의령군', '함안군', '창녕군', '고성군',
                  '남해군', '하동군', '산청군', '함양군', '거창군', '합천군']
CONSUMER_INDS = ['도매 및 소매업', '숙박 및 음식점업']

print("=" * 70)
print("이음(E-um) — MI 구성타당도 검증 (독립 데이터: 사업체수)")
print("=" * 70)

# --- 사업체 데이터 파싱 (멀티헤더: 연도/산업/항목) ---
raw = pd.read_excel(DATA, sheet_name='데이터', header=None)
yr, ind, item = raw.iloc[0], raw.iloc[1], raw.iloc[2]

# (연도, 산업, '사업체수 (개)') 인 컬럼만 골라 매핑
cols = {}
for c in range(raw.shape[1]):
    if str(item[c]).strip() == '사업체수 (개)' and str(ind[c]).strip() in CONSUMER_INDS:
        cols[(str(int(float(yr[c]))), str(ind[c]).strip())] = c

body = raw.iloc[3:].copy()
body = body[body[0].isin(TARGET_REGIONS)].set_index(0)
body.index.name = '시군구명'


def consumer_sum(year):
    s = pd.Series(0.0, index=body.index)
    for it in CONSUMER_INDS:
        col = cols[(year, it)]
        s = s + pd.to_numeric(body[col], errors='coerce')
    return s


biz = pd.DataFrame({
    '소비업종_2023': consumer_sum('2023'),
    '소비업종_2024': consumer_sum('2024'),
})
biz['사업체_증감률'] = (biz['소비업종_2024'] - biz['소비업종_2023']) / biz['소비업종_2023'] * 100
print("\n  소비업종(도소매+숙박음식) 사업체수 증감률(%):")
for r, v in biz['사업체_증감률'].sort_values().items():
    print(f"    {r}: {v:+.2f}%  ({int(biz.loc[r,'소비업종_2023'])}→{int(biz.loc[r,'소비업종_2024'])})")

# --- 지표 결합 ---
ind_df = pd.read_csv(OUT / 'indicators_phase2.csv', encoding='utf-8-sig', index_col=0)
m = biz.join(ind_df[['MI', '위험점수', '침체유형']])
m.to_csv(OUT / 'validation_business.csv', encoding='utf-8-sig')

# --- 상관분석 (Spearman, n=13 탐색적) ---
def report_corr(x, y, name):
    rho, p = stats.spearmanr(x, y)
    r2, p2 = stats.pearsonr(x, y)
    print(f"\n  [{name}] Spearman ρ={rho:+.3f} (p={p:.3f}) | Pearson r={r2:+.3f} (p={p2:.3f})")
    return rho, p


print("\n" + "-" * 60)
rho_mi, p_mi = report_corr(m['MI'], m['사업체_증감률'], 'MI vs 사업체 증감률  (가설: 양(+))')
rho_rk, p_rk = report_corr(m['위험점수'], m['사업체_증감률'], '위험점수 vs 사업체 증감률 (가설: 음(-))')

# --- 산점도 (MI vs 증감률) ---
type_colors = {
    '소비전환 취약형': '#E63946', '외부의존+소비전환 취약형': '#A30015',
    '상대적 양호형': '#2A9D8F', '경계형 (혼합)': '#9AA0A6',
}
fig, ax = plt.subplots(figsize=(11, 8))
for t, c in type_colors.items():
    sub = m[m['침체유형'] == t]
    if len(sub):
        ax.scatter(sub['MI'], sub['사업체_증감률'], s=160, c=c, edgecolors='black',
                   linewidth=1.2, label=t, zorder=3)
for r in m.index:
    ax.annotate(r, (m.loc[r, 'MI'], m.loc[r, '사업체_증감률']),
                fontsize=10, fontweight='bold', xytext=(6, 5), textcoords='offset points')

# 추세선
b, a = np.polyfit(m['MI'], m['사업체_증감률'], 1)
xs = np.linspace(m['MI'].min(), m['MI'].max(), 50)
ax.plot(xs, a + b * xs, '--', color='#444', alpha=0.7, zorder=2,
        label=f'추세선 (Spearman ρ={rho_mi:+.2f}, p={p_mi:.3f})')
ax.axhline(0, color='gray', linewidth=0.8, alpha=0.6)

ax.set_xlabel('MI (소비-유동 불일치 지수) →  음수=소비전환 취약', fontsize=12, fontweight='bold')
ax.set_ylabel('소비업종 사업체 증감률 2023→2024 (%)', fontsize=12, fontweight='bold')
ax.set_title('이음 구성타당도 검증 — MI vs 독립 지표(소비업종 사업체 증감률)\n'
             '도매·소매 + 숙박·음식점, KOSIS 전국사업체조사', fontsize=13, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / 'p2_fig9_validation.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n  ✓ p2_fig9_validation.png")
print(f"  ✓ {OUT / 'validation_business.csv'}")
