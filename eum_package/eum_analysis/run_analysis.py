"""
이음-Cluster: 22개 시군구 침체 유형 분류
+ 결과 시각화
"""
import sys
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from data_loader import load_monthly, load_hourly, load_demographic
from indicators import build_indicator_table

# 한글 폰트
import matplotlib.font_manager as fm
import subprocess

# 시스템에 설치된 한글 폰트 찾기
fonts = [f.name for f in fm.fontManager.ttflist if any(k in f.name for k in ['Nanum', 'Malgun', 'Gothic', 'AppleGothic'])]
if fonts:
    plt.rcParams['font.family'] = fonts[0]
else:
    # 나눔폰트 설치 시도
    try:
        subprocess.run(['apt-get', 'install', '-y', 'fonts-nanum'], capture_output=True, timeout=30)
        fm._load_fontmanager(try_read_cache=False)
        plt.rcParams['font.family'] = 'NanumGothic'
    except:
        pass

plt.rcParams['axes.unicode_minus'] = False

# === 1. 지표 계산 ===
print("[1/5] 데이터 로딩 및 지표 계산...")
m = load_monthly()
h = load_hourly()
d = load_demographic()
indicators = build_indicator_table(m, h, d)
print(f"  ✓ 22개 시군구 × 6개 지표 산출 완료")

# CSV 저장
indicators.to_csv('os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')/indicators_phase1.csv', encoding='utf-8-sig')

# === 2. K-means 군집 ===
print("\n[2/5] K-means 군집 분석...")
features = ['LRR', 'CDI', 'NAR', 'AGI', 'YR', 'TREND']
X = indicators[features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Elbow Method (정보용)
inertias = []
for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
print(f"  Elbow inertias (k=2~7): {[f'{x:.1f}' for x in inertias]}")

# K=3 또는 4 (Phase 1은 3유형, 추후 유동 데이터 결합 시 4유형 확장)
K = 3
km = KMeans(n_clusters=K, random_state=42, n_init=10)
indicators['Cluster'] = km.fit_predict(X_scaled)

# 클러스터별 평균 프로파일
profile = indicators.groupby('Cluster')[features].mean().round(3)
print(f"\n  클러스터 프로파일 (K={K}):")
print(profile.to_string())

# 클러스터 해석 자동 명명
def name_cluster(row):
    if row['LRR'] < 0.80 and row['AGI'] > 0.20:
        return '출혈성+노화 복합형'
    elif row['LRR'] < 0.85:
        return '출혈성(자금 유출형)'
    elif row['AGI'] > 0.20:
        return '노화형(고령 의존)'
    elif row['CDI'] < 1.5:
        return '단조형(업종 집중)'
    else:
        return '건강 상권'

profile['유형명'] = profile.apply(name_cluster, axis=1)
cluster_names = profile['유형명'].to_dict()
indicators['유형'] = indicators['Cluster'].map(cluster_names)

print(f"\n  자동 명명 결과:")
for c, name in cluster_names.items():
    members = indicators[indicators['Cluster'] == c].index.tolist()
    print(f"    [{c}] {name}: {len(members)}개 — {', '.join(members)}")

indicators.to_csv('os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')/clustering_result.csv', encoding='utf-8-sig')

# === 3. 시각화 ===
print("\n[3/5] 시각화 생성...")
mpl.rcParams['figure.dpi'] = 120

# 색상 팔레트
colors = {0: '#E63946', 1: '#F4A261', 2: '#2A9D8F', 3: '#4A90E2'}

# --- Figure 1: 지표 막대 차트 (4개 subplot) ---
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
axes = axes.flatten()
metrics = [('LRR', '지역 자금 환류율 (↓일수록 위험)', False),
           ('CDI', '소비 다양성 지수 (↓일수록 위험)', False),
           ('NAR', '야간 활성도 비율 (↓일수록 위험)', False),
           ('AGI', '고령 소비 비중 (↑일수록 노화)', True)]

for ax, (col, title, reverse) in zip(axes, metrics):
    sorted_df = indicators.sort_values(col, ascending=reverse)
    bar_colors = [colors.get(c, '#888') for c in sorted_df['Cluster']]
    ax.barh(range(len(sorted_df)), sorted_df[col], color=bar_colors)
    ax.set_yticks(range(len(sorted_df)))
    ax.set_yticklabels(sorted_df.index, fontsize=9)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    # 평균선
    mean_val = indicators[col].mean()
    ax.axvline(mean_val, color='gray', linestyle='--', alpha=0.5,
               label=f'평균 {mean_val:.3f}')
    ax.legend(loc='lower right', fontsize=8)

plt.suptitle('「이음(E-um)」 경남 22개 시군구 침체 진단 지표 (Phase 1)',
             fontsize=14, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')/fig1_indicators.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ fig1_indicators.png")

# --- Figure 2: PCA 군집 산점도 ---
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

fig, ax = plt.subplots(figsize=(12, 9))
for c in range(K):
    mask = indicators['Cluster'] == c
    ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
               s=200, c=colors[c], alpha=0.7,
               edgecolors='black', linewidth=1.5,
               label=f'{cluster_names[c]} ({mask.sum()}개)')

for i, name in enumerate(indicators.index):
    ax.annotate(name, (X_pca[i, 0], X_pca[i, 1]),
                fontsize=9, xytext=(5, 5), textcoords='offset points')

ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', fontsize=11)
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})', fontsize=11)
ax.set_title('「이음-Cluster」 PCA 평면상 침체 유형 분류', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(alpha=0.3)
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)
plt.tight_layout()
plt.savefig('os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')/fig2_pca_cluster.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ fig2_pca_cluster.png")

# --- Figure 3: LRR vs AGI 산점도 (4사분면 진단) ---
fig, ax = plt.subplots(figsize=(11, 9))
for c in range(K):
    mask = indicators['Cluster'] == c
    ax.scatter(indicators.loc[mask, 'LRR'], indicators.loc[mask, 'AGI'],
               s=200, c=colors[c], alpha=0.7,
               edgecolors='black', linewidth=1.5,
               label=cluster_names[c])

for name in indicators.index:
    ax.annotate(name, (indicators.loc[name, 'LRR'], indicators.loc[name, 'AGI']),
                fontsize=8.5, xytext=(5, 5), textcoords='offset points')

# 평균선으로 4사분면 분할
lrr_mean = indicators['LRR'].mean()
agi_mean = indicators['AGI'].mean()
ax.axvline(lrr_mean, color='gray', linestyle='--', alpha=0.5)
ax.axhline(agi_mean, color='gray', linestyle='--', alpha=0.5)

# 사분면 라벨
xlim = ax.get_xlim(); ylim = ax.get_ylim()
ax.text(xlim[0]+0.01, ylim[1]-0.005, '◀ 출혈성+노화\n(이중 위험)',
        fontsize=11, fontweight='bold', color='#C00000', va='top',
        bbox=dict(boxstyle='round', facecolor='#FFF0F0', alpha=0.7))
ax.text(xlim[1]-0.01, ylim[1]-0.005, '노화형 ▶\n(고령 의존)',
        fontsize=11, fontweight='bold', color='#D67E00', va='top', ha='right',
        bbox=dict(boxstyle='round', facecolor='#FFF8E0', alpha=0.7))
ax.text(xlim[0]+0.01, ylim[0]+0.005, '◀ 출혈형\n(자금 유출)',
        fontsize=11, fontweight='bold', color='#C00000',
        bbox=dict(boxstyle='round', facecolor='#FFF0F0', alpha=0.7))
ax.text(xlim[1]-0.01, ylim[0]+0.005, '건강 상권 ▶',
        fontsize=11, fontweight='bold', color='#2A9D8F', ha='right',
        bbox=dict(boxstyle='round', facecolor='#E8F5F2', alpha=0.7))

ax.set_xlabel('LRR (지역 자금 환류율) →', fontsize=12, fontweight='bold')
ax.set_ylabel('AGI (고령 소비 비중) →', fontsize=12, fontweight='bold')
ax.set_title('「이음(E-um)」 진단 매트릭스: LRR × AGI 4사분면',
             fontsize=14, fontweight='bold')
ax.legend(loc='center right', fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')/fig3_diagnosis_matrix.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ fig3_diagnosis_matrix.png")

# === 4. 우선순위 진단 리스트 ===
print("\n[4/5] 우선 처방 대상 시군구 도출...")

# 위험 점수: LRR 낮을수록↑, AGI 높을수록↑, TREND 낮을수록↑
indicators['위험점수'] = (
    (1 - indicators['LRR']) * 0.4 +
    indicators['AGI'] * 0.3 +
    (-indicators['TREND']) * 100 * 0.2 +
    (1 - indicators['CDI'] / indicators['CDI'].max()) * 0.1
)

priority = indicators.sort_values('위험점수', ascending=False).head(8)
print(f"\n  우선 처방 대상 TOP 8:")
print(priority[['LRR', 'AGI', 'TREND', 'CDI', '유형', '위험점수']].round(4).to_string())

priority.to_csv('os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')/priority_targets.csv', encoding='utf-8-sig')

# === 5. 요약 보고 ===
print("\n[5/5] 분석 요약")
print("="*60)
print(f"분석 대상: 경남 22개 시군구")
print(f"적용 지표: LRR, CDI, NAR, AGI, YR, TREND (6종)")
print(f"군집 결과: {K}개 침체 유형 자동 분류")
print(f"\n주요 인사이트:")
print(f"  - LRR 최저(자금 유출 심각): {indicators['LRR'].idxmin()} ({indicators['LRR'].min():.3f})")
print(f"  - LRR 최고(자금 환류 양호): {indicators['LRR'].idxmax()} ({indicators['LRR'].max():.3f})")
print(f"  - AGI 최고(고령 의존 심각): {indicators['AGI'].idxmax()} ({indicators['AGI'].max():.3f})")
print(f"  - TREND 최악(매출 감소세): {indicators['TREND'].idxmin()} ({indicators['TREND'].min():.4f})")
print("="*60)
print("\n출력 파일:")
print("  • output/indicators_phase1.csv")
print("  • output/clustering_result.csv")
print("  • output/priority_targets.csv")
print("  • output/fig1_indicators.png")
print("  • output/fig2_pca_cluster.png")
print("  • output/fig3_diagnosis_matrix.png")
