"""
이음(E-um) — 관광형 시군 '체류 vs 통과' 소비구조 분석

[목적] STI(관광 의존도)로 '관광형'으로 진단된 시군들이, 실제로 관광객을
  '체류 소비'로 잡는지 '통과 소비'에 그치는지를 한국관광 데이터랩
  업종별 관광소비 비중으로 검증한다. (처방 차등화의 데이터 근거)

[정의]
  통과성 = 운송업 + 쇼핑업 (이동·즉석구매, 그냥 지나감)
  체류성 = 숙박업 + 여가서비스업 (머무름)
  식음료 = 중립(둘 다)

[입력] data/관광소비/<시군>.csv (한국관광 데이터랩, 업종대분류 비율)
[산출] phase2/p2_fig12_tourism.png, phase2/tourism_structure.csv
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
TDIR = PROJECT_ROOT.parent / 'eum_package' / 'data' / '관광소비'

PASS_IND = ['운송업', '쇼핑업']      # 통과성
STAY_IND = ['숙박업', '여가서비스업']  # 체류성

print("=" * 70)
print("이음(E-um) — 관광형 시군 체류 vs 통과 소비구조")
print("=" * 70)

rows = []
for f in sorted(TDIR.glob('*.csv')):
    region = f.stem
    df = pd.read_csv(f, encoding='utf-8')
    # 업종대분류별 비율(중복 행 → 첫 값)
    share = {}
    for _, r in df.iterrows():
        k = str(r['업종대분류명'])
        if k not in share:
            share[k] = float(r['업종대분류 비율(%)'])
    pass_ = sum(share.get(k, 0) for k in PASS_IND)
    stay = sum(share.get(k, 0) for k in STAY_IND)
    food = share.get('식음료업', 0)
    rows.append({
        '시군': region, '통과성': pass_, '식음료': food, '체류성': stay,
        '숙박': share.get('숙박업', 0), '여가': share.get('여가서비스업', 0),
        '운송': share.get('운송업', 0), '쇼핑': share.get('쇼핑업', 0),
        '체류전환지수': round(stay / (stay + pass_) * 100, 1),  # 체류/(체류+통과)
    })

t = pd.DataFrame(rows).set_index('시군').sort_values('체류성')
t.to_csv(OUT / 'tourism_structure.csv', encoding='utf-8-sig')
print(t[['통과성', '식음료', '체류성', '체류전환지수']].to_string())

# --- Figure: 체류 vs 통과 누적 막대 ---
fig, ax = plt.subplots(figsize=(11, 6.5))
y = np.arange(len(t))
ax.barh(y, t['통과성'], color='#E76F51', label='통과성 (운송+쇼핑)')
ax.barh(y, t['식음료'], left=t['통과성'], color='#E9C46A', label='식음료 (중립)')
ax.barh(y, t['체류성'], left=t['통과성'] + t['식음료'], color='#2A9D8F', label='체류성 (숙박+여가)')
ax.set_yticks(y)
ax.set_yticklabels(t.index, fontsize=12)
ax.set_xlabel('관광소비 업종 비중 (%)', fontsize=12, fontweight='bold')
ax.set_title('관광형 시군의 체류 vs 통과 소비구조\n'
             '(체류성↑ = 머무는 관광 / 통과성↑ = 지나가는 관광, 한국관광 데이터랩)',
             fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.grid(axis='x', alpha=0.3)
for yi, (r, row) in enumerate(t.iterrows()):
    ax.annotate(f"체류 {row['체류성']:.0f}%", (row['통과성'] + row['식음료'] + row['체류성'] + 1, yi),
                va='center', fontsize=9, color='#2A9D8F', fontweight='bold')
plt.tight_layout()
plt.savefig(OUT / 'p2_fig12_tourism.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n  ✓ p2_fig12_tourism.png")
print(f"  ✓ {OUT / 'tourism_structure.csv'}")
print("\n[해석] 산청(체류 1.8%)·고성·하동은 통과형 → 체류 전환 처방 필요.")
print("       남해(체류 23%, 숙박 비중 높음)는 이미 체류형 → 차등 처방 근거.")
