"""
이음-Detect — 침체 원인 정량 분해

두 층위로 "왜 위험한가"를 분해한다.

[Part A] 위험점수 요인 분해 (정확·비순환)
  위험점수는 4개 지표의 가중합(run_phase2.RISK_WEIGHTS)이므로,
  각 시군의 위험점수를 MI·CPC·LRR·TREND 4개 기여항으로 정확히 분해한다.
  → 누적 막대그래프 + 시군별 1위 요인 csv

[Part B] 소비-유동 불일치(MI)의 구조적 동인 (RandomForest + SHAP, 탐색적)
  MI를 종속변수로, MI 산식에 들어가지 않는 구조지표
  {LRR, CDI, NAR, AGI, YR, STI, TREND}를 독립변수로 RandomForest 회귀를 적합한 뒤
  SHAP으로 "어떤 구조 특성이 MI를 끌어내리는가"를 분해한다.
  ※ 표본 n=13의 탐색적 분석 — 확정 인과가 아니라 패턴 탐지로 해석.
    CPC는 MI와 정의상 공선성이 커 독립변수에서 제외했다.

[산출]
  phase2/detect_risk_factors.csv     : 시군별 위험 4요인 기여도 + 1위 요인
  phase2/detect_shap_drivers.csv     : 시군별 MI 하락 구조요인 Top3 (SHAP)
  phase2/p2_fig7_risk_decomposition.png
  phase2/p2_fig8_shap_importance.png
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
from sklearn.ensemble import RandomForestRegressor
import shap

# 한글 폰트
for font_path in [Path('C:/Windows/Fonts/malgun.ttf'), Path('C:/Windows/Fonts/NanumGothic.ttf')]:
    if font_path.exists():
        fm.fontManager.addfont(str(font_path))
fonts = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
malgun_fonts = [f.name for f in fm.fontManager.ttflist if 'Malgun' in f.name]
plt.rcParams['font.family'] = fonts[0] if fonts else (malgun_fonts[0] if malgun_fonts else 'DejaVu Sans')
plt.rcParams['axes.unicode_minus'] = False

OUT = PROJECT_ROOT / 'phase2'

# run_phase2.py와 동일한 위험점수 산식 (정합성 유지)
RISK_WEIGHTS = {'MI': 0.40, 'CPC': 0.25, 'LRR': 0.20, 'TREND': 0.15}


def minmax(s):
    span = s.max() - s.min()
    return s * 0 if span == 0 else (s - s.min()) / span


print("=" * 70)
print("이음-Detect — 침체 원인 정량 분해")
print("=" * 70)

ind = pd.read_csv(OUT / 'indicators_phase2.csv', encoding='utf-8-sig', index_col=0)
ind.index.name = '시군구명'

# ============================================================
# Part A. 위험점수 요인 분해 (정확)
# ============================================================
print("\n[Part A] 위험점수 4요인 분해")
print("-" * 60)

contrib = pd.DataFrame(index=ind.index)
contrib['MI요인']    = minmax(-ind['MI'])    * RISK_WEIGHTS['MI']
contrib['CPC요인']   = minmax(-ind['CPC'])   * RISK_WEIGHTS['CPC']
contrib['LRR요인']   = minmax(-ind['LRR'])   * RISK_WEIGHTS['LRR']
contrib['TREND요인'] = minmax(-ind['TREND']) * RISK_WEIGHTS['TREND']
contrib['위험점수']  = contrib[['MI요인', 'CPC요인', 'LRR요인', 'TREND요인']].sum(axis=1)

# 검증: run_phase2 위험점수와 일치하는지
diff = (contrib['위험점수'] - ind['위험점수']).abs().max()
print(f"  위험점수 재현 오차(max): {diff:.6f} (≈0이면 정합)")

factor_cols = ['MI요인', 'CPC요인', 'LRR요인', 'TREND요인']
contrib['1위요인'] = contrib[factor_cols].idxmax(axis=1).str.replace('요인', '')
contrib['1위기여율'] = (contrib[factor_cols].max(axis=1) / contrib['위험점수']).round(3)
contrib = contrib.sort_values('위험점수', ascending=False)
contrib.to_csv(OUT / 'detect_risk_factors.csv', encoding='utf-8-sig')

print("  시군별 위험 1위 요인:")
for name, r in contrib.iterrows():
    print(f"    {name}: {r['1위요인']} ({r['1위기여율']*100:.0f}%)  위험={r['위험점수']:.3f}")

# --- Figure 7: 위험점수 누적 분해 막대 ---
fig, ax = plt.subplots(figsize=(11, 8))
bar_palette = {'MI요인': '#A30015', 'CPC요인': '#E63946', 'LRR요인': '#E76F51', 'TREND요인': '#F4A261'}
left = np.zeros(len(contrib))
ypos = range(len(contrib))
for col in factor_cols:
    ax.barh(ypos, contrib[col], left=left, color=bar_palette[col], label=col)
    left += contrib[col].values
ax.set_yticks(list(ypos))
ax.set_yticklabels(contrib.index, fontsize=11)
ax.invert_yaxis()  # 위험 높은 시군을 위로
ax.set_xlabel('위험점수 (요인별 기여 누적)', fontsize=12, fontweight='bold')
ax.set_title('이음-Detect ① 위험점수 요인 분해\n(MI·CPC·LRR·TREND 가중 기여)',
             fontsize=14, fontweight='bold')
ax.legend(loc='lower right', fontsize=11)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / 'p2_fig7_risk_decomposition.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig7_risk_decomposition.png")

# ============================================================
# Part B. MI 구조적 동인 (RandomForest + SHAP)
# ============================================================
print("\n[Part B] MI 구조적 동인 (RandomForest + SHAP, 탐색적 n=13)")
print("-" * 60)

features = ['LRR', 'CDI', 'NAR', 'AGI', 'YR', 'STI', 'TREND']
# 지표 약어에 한글 풀이 병기 (그림 가독성)
GLOSS = {
    'MI': 'MI(소비-유동 불일치)', 'CPC': 'CPC(1인당 월소비)',
    'LRR': 'LRR(경남권 소비자 비중)', 'CDI': 'CDI(업종 다양성)',
    'NAR': 'NAR(야간 활성도)', 'AGI': 'AGI(고령 소비비중)',
    'YR': 'YR(청년 소비비중)', 'STI': 'STI(관광 의존도)',
    'TREND': 'TREND(매출 추세)',
}
X = ind[features].copy()
y = ind['MI'].copy()

rf = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
rf.fit(X, y)
r2 = rf.score(X, y)
print(f"  RandomForest 적합 R²(in-sample): {r2:.3f}  ※ n=13 과적합 경향 — 탐색용")

explainer = shap.TreeExplainer(rf)
shap_vals = explainer.shap_values(X)  # (n, n_features)
shap_df = pd.DataFrame(shap_vals, index=X.index, columns=features)

# 전역 중요도 (평균 |SHAP|)
glob_imp = shap_df.abs().mean().sort_values(ascending=False)
print("  전역 SHAP 중요도 (MI 설명력):")
for f, v in glob_imp.items():
    print(f"    {f}: {v:.4f}")

# 시군별 MI를 '끌어내리는'(음의 SHAP) 구조요인 Top3
rows = []
for name in X.index:
    s = shap_df.loc[name].sort_values()  # 음수(=MI 하락 기여)부터
    top = s.head(3)
    rows.append({
        '시군구명': name, 'MI': round(y[name], 3),
        '동인1': top.index[0], '기여1': round(top.iloc[0], 4),
        '동인2': top.index[1], '기여2': round(top.iloc[1], 4),
        '동인3': top.index[2], '기여3': round(top.iloc[2], 4),
    })
drivers = pd.DataFrame(rows).set_index('시군구명').loc[contrib.index]  # 위험순 정렬
drivers.to_csv(OUT / 'detect_shap_drivers.csv', encoding='utf-8-sig')
print("\n  시군별 MI 하락 구조동인 Top1 (음수=불일치 심화):")
for name, r in drivers.iterrows():
    print(f"    {name}: {r['동인1']} ({r['기여1']:+.3f})")

# --- Figure 8: 전역 SHAP 중요도 막대 ---
fig, ax = plt.subplots(figsize=(9, 6))
gi = glob_imp.sort_values()
ax.barh(range(len(gi)), gi.values, color='#2A6F97')
ax.set_yticks(range(len(gi)))
ax.set_yticklabels([GLOSS.get(f, f) for f in gi.index], fontsize=10)
ax.set_xlabel('평균 |SHAP| (MI 설명 기여도)', fontsize=12, fontweight='bold')
ax.set_title('이음-Detect ② 소비-유동 불일치(MI)의 구조적 동인\n'
             'RandomForest + SHAP (탐색적, n=13)', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / 'p2_fig8_shap_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig8_shap_importance.png")

print("\n[산출 파일]")
for f in ['detect_risk_factors.csv', 'detect_shap_drivers.csv',
          'p2_fig7_risk_decomposition.png', 'p2_fig8_shap_importance.png']:
    print(f"  • {OUT / f}")
