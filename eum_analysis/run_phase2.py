"""
이음(E-um) Phase 2 통합 분석

[입력 데이터]
  1. 2024년 카드 매출 3종 (월별·시간대별·성연령별) — 경남 22개 시군구
  2. 2024년 인구감소지역 생활인구 — 경남 13개 시·군

[분석 대상]
  경남 13개 인구감소지역만 (통영, 사천, 밀양, 의령, 함안, 창녕, 고성,
  남해, 하동, 산청, 함양, 거창, 합천)

[산출 지표]
  - LRR : 경남권 소비자 비중
  - CDI : 소비 다양성 지수 (Shannon Entropy)
  - NAR : 야간 활성도 비율
  - AGI : 고령 소비 비중
  - YR  : 청년 소비 비중
  - TREND : 매출 추세
  - MI  : 소비-유동 불일치 지수 ★ Phase 2 신규
  - STI : 계절 관광 의존도 ★ Phase 2 신규
  - CPC : 1인당 소비 ★ Phase 2 신규

[침체 4유형 분류]
  1) 외지방문 의존형 : 경남 외 소비자 비중이 높고 소비전환도 취약
  2) 방문대비 소비부족형 : 생활인구는 있으나 카드소비가 낮음
  3) 혼합 경계형 : 위험 신호가 섞여 있어 모니터링 필요
  4) 소비 안정형 : 생활인구 대비 소비전환이 상대적으로 양호
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / 'modules'))

import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats

from data_loader import load_monthly, load_hourly, load_demographic
from living_pop_loader import load_living_population, aggregate_by_region, aggregate_annual, TARGET_REGIONS
from indicators import calculate_lrr, calculate_cdi, calculate_nar, calculate_agi, calculate_youth_ratio, calculate_sales_trend

# 한글 폰트
for font_path in [Path('C:/Windows/Fonts/malgun.ttf'), Path('C:/Windows/Fonts/NanumGothic.ttf')]:
    if font_path.exists():
        fm.fontManager.addfont(str(font_path))
fonts = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
malgun_fonts = [f.name for f in fm.fontManager.ttflist if 'Malgun' in f.name]
plt.rcParams['font.family'] = fonts[0] if fonts else (malgun_fonts[0] if malgun_fonts else 'DejaVu Sans')
plt.rcParams['axes.unicode_minus'] = False

OUT = PROJECT_ROOT / 'phase2'
OUT.mkdir(parents=True, exist_ok=True)

# 위험점수 표준 산식 가중치 (심사 방어용으로 보고서에 명시)
# - 모든 지표를 13개 지역 min-max 정규화 후, 낮을수록 위험인 지표는 부호 반전(-)
# - MI: 핵심 지표(소비-유동 불일치), CPC: 1인당 소비력,
#   LRR: 경남 외 소비 의존, TREND: 매출 추세
RISK_WEIGHTS = {'MI': 0.40, 'CPC': 0.25, 'LRR': 0.20, 'TREND': 0.15}

print("="*70)
print("「이음(E-um)」 Phase 2 통합 분석 시작")
print("="*70)

# ============================================================
# STEP 1. 데이터 로딩 + 13개 시·군으로 필터
# ============================================================
print("\n[1/6] 데이터 로딩 및 13개 인구감소지역 필터링")
print("-"*60)

m_all = load_monthly()
h_all = load_hourly()
d_all = load_demographic()

# 인구감소지역 13개만 필터
m = m_all[m_all['시군구명'].isin(TARGET_REGIONS)].copy()
h = h_all[h_all['시군구명'].isin(TARGET_REGIONS)].copy()
d = d_all[d_all['시군구명'].isin(TARGET_REGIONS)].copy()

print(f"  카드 월별 데이터: {m_all.shape} → {m.shape} (13개 시·군 필터)")
print(f"  카드 시간대별   : {h_all.shape} → {h.shape}")
print(f"  카드 성연령별   : {d_all.shape} → {d.shape}")

# 생활인구 데이터
lp_long = load_living_population()
lp_annual = aggregate_annual(lp_long)
lp_monthly = aggregate_by_region(lp_long)
print(f"  생활인구 (long) : {lp_long.shape}")
print(f"  연평균 생활인구  : {len(lp_annual)}개 시·군")

# 인구감소구분 (감소/관심) 정보 추출
pop_decline_status = lp_long[['시군구명', '인구감소구분']].drop_duplicates().set_index('시군구명')
print(f"  인구감소지역: {(pop_decline_status['인구감소구분']=='감소').sum()}개")
print(f"  관심지역    : {(pop_decline_status['인구감소구분']=='관심').sum()}개")

# ============================================================
# STEP 2. Phase 1 지표 계산 (13개 시·군에 대해)
# ============================================================
print("\n[2/6] Phase 1 지표 계산 (LRR, CDI, NAR, AGI, YR, TREND)")
print("-"*60)

indicators = pd.concat([
    calculate_lrr(m),
    calculate_cdi(m),
    calculate_nar(h),
    calculate_agi(d),
    calculate_youth_ratio(d),
    calculate_sales_trend(m),
], axis=1)
print(f"  ✓ 6개 지표 계산 완료. shape={indicators.shape}")

# ============================================================
# STEP 3. Phase 2 신규 지표 계산 (MI, STI, CPC)
# ============================================================
print("\n[3/6] Phase 2 신규 지표 계산 (MI, STI, CPC)")
print("-"*60)

# --- 연간 매출 집계 ---
annual_sales = m.groupby('시군구명')['매출합계(원)'].sum().rename('연간매출')

# --- MI (Mismatch Index) ---
# MI = log(매출 / 생활인구) - 평균
ratio = annual_sales / lp_annual
log_ratio = np.log(ratio)
mi = (log_ratio - log_ratio.mean()).rename('MI')
print(f"  ✓ MI 계산. 범위 [{mi.min():.3f}, {mi.max():.3f}]")

# --- CPC (Consumption Per Capita, 1인당 소비) ---
# CPC = 연간 매출 / 평균 생활인구 (월 단위 환산)
cpc = (annual_sales / lp_annual / 12).rename('CPC')  # 월간 1인당 매출
print(f"  ✓ CPC 계산. 범위 [{cpc.min():,.0f}원/월, {cpc.max():,.0f}원/월]")

# --- STI (Seasonal Tourism Index, 계절 관광 의존도) ---
# 성수기(6~8월) vs 비수기(1~3월) 생활인구 비율
peak_months = [6, 7, 8]
off_months = [1, 2, 3]
peak_lp = lp_monthly[lp_monthly['월'].isin(peak_months)].groupby('시군구명')['생활인구'].mean()
off_lp = lp_monthly[lp_monthly['월'].isin(off_months)].groupby('시군구명')['생활인구'].mean()
sti = ((peak_lp / off_lp) - 1).rename('STI')
print(f"  ✓ STI 계산. 범위 [{sti.min():.3f}, {sti.max():.3f}]")

# 통합
indicators = indicators.join([mi, cpc, sti])
indicators['인구감소구분'] = pop_decline_status['인구감소구분']
indicators['연평균_생활인구'] = lp_annual
indicators['연간매출'] = annual_sales

print(f"\n  최종 지표 테이블 shape: {indicators.shape}")
print(f"  컬럼: {indicators.columns.tolist()}")

# ============================================================
# STEP 4. K-means 군집 분석 (4유형 분류)
# ============================================================
print("\n[4/6] 침체 4유형 자동 분류 (K-means)")
print("-"*60)

# 클러스터링 변수
cluster_features = ['MI', 'LRR', 'AGI', 'CDI', 'NAR', 'CPC', 'TREND']
X = indicators[cluster_features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Elbow Method
inertias = []
for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
print(f"  Elbow inertias (k=2~7): {[f'{x:.1f}' for x in inertias]}")

K = 4
km = KMeans(n_clusters=K, random_state=42, n_init=10)
indicators['Cluster'] = km.fit_predict(X_scaled)

# 클러스터 프로파일
profile = indicators.groupby('Cluster')[cluster_features + ['연평균_생활인구']].mean().round(3)
print(f"\n  클러스터 프로파일 (K={K}):")
print(profile.to_string())

# 클러스터 자동 명명 — 클러스터 평균 프로파일의 절대적 특성으로 명명
def name_cluster_v2(profile_row):
    """
    클러스터 평균 프로파일에 기반한 분류:
    - 소비 안정형: MI 양수 & 경남권 소비자 비중/CPC 우수
    - 외지방문 의존형: LRR 낮음(<0.78) + MI 음수
    - 방문대비 소비부족형: MI 음수 + LRR 양호 (유동은 있는데 소비가 못 따라옴)
    - 혼합 경계형: 특정 단일 유형으로 고정하기 어려운 경계 지역
    """
    mi = profile_row['MI']
    lrr = profile_row['LRR']
    agi = profile_row['AGI']
    cpc = profile_row['CPC']
    lp = profile_row['연평균_생활인구']
    trend = profile_row['TREND']

    # 1. 상대적 양호 그룹
    if mi > 0.5 and lrr > 0.85 and cpc > 50000:
        return '소비 안정형'

    # 2. 경남 외 소비 의존 + 소비전환 취약 복합
    if lrr < 0.78 and mi < -0.3:
        return '외지방문 의존형'

    # 3. 경남 외 소비자 비중이 높은 단독 신호
    if lrr < 0.78:
        return '외지방문 의존형'

    # 4. 소비전환 취약 (MI 매우 낮음, LRR은 양호)
    if mi < -0.5:
        return '방문대비 소비부족형'

    return '혼합 경계형'

profile['유형명'] = profile.apply(name_cluster_v2, axis=1)
cluster_names = profile['유형명'].to_dict()
indicators['침체유형'] = indicators['Cluster'].map(cluster_names)

print(f"\n  자동 명명 결과:")
for c in range(K):
    members = indicators[indicators['Cluster']==c].index.tolist()
    print(f"    [Cluster {c}] {cluster_names[c]}: {len(members)}개")
    print(f"               → {', '.join(members)}")

# ============================================================
# STEP 5. 우선 개선 대상 시군 도출
# ============================================================
print("\n[5/6] 우선 개선 대상 도출")
print("-"*60)

def minmax(s):
    """13개 지역 min-max 정규화 (낮을수록 위험인 지표는 호출 측에서 부호 반전)."""
    span = s.max() - s.min()
    if span == 0:
        return s * 0
    return (s - s.min()) / span


# 위험점수 = Σ minmax(-X_i) * w_i,  X_i ∈ {MI, CPC, LRR, TREND}
# 가중치는 RISK_WEIGHTS 상수로 분리(보고서·심사 방어용).
indicators['위험점수'] = (
    minmax(-indicators['MI'])    * RISK_WEIGHTS['MI']    +
    minmax(-indicators['CPC'])   * RISK_WEIGHTS['CPC']   +
    minmax(-indicators['LRR'])   * RISK_WEIGHTS['LRR']   +
    minmax(-indicators['TREND']) * RISK_WEIGHTS['TREND']
)

priority = indicators.sort_values('위험점수', ascending=False)
print("\n  13개 시·군 위험점수 순위:")
display_cols = ['MI', 'LRR', 'AGI', 'TREND', 'CPC', '침체유형', '위험점수']
print(priority[display_cols].round(4).to_string())

# 저장
indicators.to_csv(f'{OUT}/indicators_phase2.csv', encoding='utf-8-sig')
priority.to_csv(f'{OUT}/priority_phase2.csv', encoding='utf-8-sig')

# ============================================================
# STEP 6. 시각화
# ============================================================
print("\n[6/6] 시각화 생성")
print("-"*60)

# 색상
type_colors = {
    '방문대비 소비부족형':        '#E63946',  # 빨강
    '외지방문 의존형': '#A30015',  # 진빨강
    '소비 안정형':          '#2A9D8F',  # 청록 (건강)
    '혼합 경계형':          '#888888',  # 회색
}

# --- Figure 1: MI × LRR 분석 매트릭스 (핵심 시각화) ---
fig, ax = plt.subplots(figsize=(12, 9))
for type_name, color in type_colors.items():
    mask = indicators['침체유형'] == type_name
    if mask.sum() == 0:
        continue
    ax.scatter(indicators.loc[mask, 'MI'], indicators.loc[mask, 'LRR'],
               s=indicators.loc[mask, '연평균_생활인구']/2000,  # 크기=생활인구
               c=color, alpha=0.7, edgecolors='black', linewidth=1.5,
               label=f'{type_name} ({mask.sum()}개)')

for name in indicators.index:
    ax.annotate(name, (indicators.loc[name, 'MI'], indicators.loc[name, 'LRR']),
                fontsize=10, xytext=(7, 7), textcoords='offset points',
                fontweight='bold')

ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
ax.axhline(indicators['LRR'].median(), color='gray', linestyle='--', alpha=0.5)

# 사분면 라벨
ax.text(0.02, 0.98, '소비-유동 불일치 ↑\n(소비전환 취약 위험)',
        transform=ax.transAxes, fontsize=11, fontweight='bold',
        color='#C00000', va='top',
        bbox=dict(boxstyle='round', facecolor='#FFF0F0', alpha=0.8))
ax.text(0.98, 0.02, '소비-유동 균형 ↑\n경남권 소비자 비중 ↑\n(안정 상권)',
        transform=ax.transAxes, fontsize=11, fontweight='bold',
        color='#2A9D8F', ha='right',
        bbox=dict(boxstyle='round', facecolor='#E8F5F2', alpha=0.8))

ax.set_xlabel('MI (생활인구 대비 카드소비 수준) →  음수=소비전환 취약', fontsize=12, fontweight='bold')
ax.set_ylabel('LRR (경남권 소비자 비중) →  낮음=경남 외 소비 의존', fontsize=12, fontweight='bold')
ax.set_title('「이음(E-um)」 Phase 2 분석 매트릭스 (원 크기 = 연평균 생활인구)',
             fontsize=14, fontweight='bold')
ax.legend(loc='center left', fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUT}/p2_fig1_MI_LRR_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig1_MI_LRR_matrix.png")

# --- Figure 2: 4개 핵심 지표 막대 차트 ---
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
axes = axes.flatten()
metrics = [
    ('MI',  '소비-유동 불일치 (↓일수록 소비전환 취약)', False),
    ('LRR', '경남권 소비자 비중 (↓일수록 경남 외 소비 의존)', False),
    ('CPC', '1인당 월 소비액 (원) (↓일수록 구매력 약함)', False),
    ('STI', '계절 관광 의존도 (↑일수록 관광 의존)', True),
]

for ax, (col, title, reverse) in zip(axes, metrics):
    sorted_df = indicators.sort_values(col, ascending=reverse)
    bar_colors = [type_colors[t] for t in sorted_df['침체유형']]
    bars = ax.barh(range(len(sorted_df)), sorted_df[col], color=bar_colors)
    ax.set_yticks(range(len(sorted_df)))
    ax.set_yticklabels(sorted_df.index, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    mean_val = indicators[col].mean()
    ax.axvline(mean_val, color='gray', linestyle='--', alpha=0.5,
               label=f'평균 {mean_val:,.3f}' if abs(mean_val)<10 else f'평균 {mean_val:,.0f}')
    ax.legend(loc='lower right', fontsize=9)

plt.suptitle('「이음(E-um)」 Phase 2 핵심 지표 - 13개 인구감소지역',
             fontsize=15, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig(f'{OUT}/p2_fig2_indicators.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig2_indicators.png")

# --- Figure 3: 월별 생활인구 추세 (관광 의존도 가시화) ---
fig, ax = plt.subplots(figsize=(14, 8))
for region in TARGET_REGIONS:
    region_data = lp_monthly[lp_monthly['시군구명'] == region].sort_values('월')
    # 정규화 (1월 = 100)
    base = region_data[region_data['월']==1]['생활인구'].values[0]
    normalized = region_data['생활인구'] / base * 100
    color = type_colors.get(indicators.loc[region, '침체유형'], '#888')
    ax.plot(region_data['월'], normalized, marker='o',
            label=region, color=color, alpha=0.8, linewidth=2)

ax.set_xlabel('월', fontsize=12, fontweight='bold')
ax.set_ylabel('생활인구 지수 (1월=100)', fontsize=12, fontweight='bold')
ax.set_title('월별 생활인구 변동 — 관광 성수기 의존도 시각화',
             fontsize=14, fontweight='bold')
ax.set_xticks(range(1, 13))
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9, ncol=1)
ax.grid(alpha=0.3)
ax.axhline(100, color='black', linestyle=':', alpha=0.5)
plt.tight_layout()
plt.savefig(f'{OUT}/p2_fig3_monthly_population.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig3_monthly_population.png")

# --- Figure 4: PCA 군집 시각화 ---
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

fig, ax = plt.subplots(figsize=(12, 9))
for c in range(K):
    mask = indicators['Cluster'] == c
    type_name = cluster_names[c]
    color = type_colors.get(type_name, '#888')
    ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
               s=250, c=color, alpha=0.7, edgecolors='black', linewidth=1.5,
               label=f'{type_name} ({mask.sum()}개)')

for i, name in enumerate(indicators.index):
    ax.annotate(name, (X_pca[i, 0], X_pca[i, 1]),
                fontsize=10, xytext=(7, 7), textcoords='offset points',
                fontweight='bold')

ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', fontsize=11)
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})', fontsize=11)
ax.set_title('이음-Cluster: PCA 평면상 침체 4유형 분류', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(alpha=0.3)
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)
plt.tight_layout()
plt.savefig(f'{OUT}/p2_fig4_pca_cluster.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ p2_fig4_pca_cluster.png")

# ============================================================
# 최종 요약
# ============================================================
print("\n" + "="*70)
print("Phase 2 분석 완료")
print("="*70)
print(f"\n[핵심 인사이트]")
print(f"  • MI 최저 (소비전환 취약 1위): {indicators['MI'].idxmin()} (MI={indicators['MI'].min():.3f})")
print(f"  • MI 최고 (소비-유동 균형): {indicators['MI'].idxmax()} (MI={indicators['MI'].max():.3f})")
print(f"  • LRR 최저 (경남 외 소비 의존): {indicators['LRR'].idxmin()} ({indicators['LRR'].min():.3f})")
print(f"  • CPC 최저 (구매력 약함) : {indicators['CPC'].idxmin()} ({indicators['CPC'].min():,.0f}원/월)")
print(f"  • CPC 최고 (구매력 높음) : {indicators['CPC'].idxmax()} ({indicators['CPC'].max():,.0f}원/월)")
print(f"  • STI 최고 (관광 의존)   : {indicators['STI'].idxmax()} (STI={indicators['STI'].max():.3f})")
print(f"  • 위험점수 1위 (최우선)   : {priority.index[0]} (위험={priority['위험점수'].iloc[0]:.4f})")

print(f"\n[산출 파일]")
print(f"  • {OUT}/indicators_phase2.csv")
print(f"  • {OUT}/priority_phase2.csv")
print(f"  • {OUT}/p2_fig1_MI_LRR_matrix.png")
print(f"  • {OUT}/p2_fig2_indicators.png")
print(f"  • {OUT}/p2_fig3_monthly_population.png")
print(f"  • {OUT}/p2_fig4_pca_cluster.png")
