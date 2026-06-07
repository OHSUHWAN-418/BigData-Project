# 「이음(E-um)」 분석 코드 패키지

경남 소비-유동 불일치 진단 모델 분석 코드.

## 1. 환경 요구사항

- Python 3.10+
- pandas, numpy, scipy
- scikit-learn
- matplotlib (한글 폰트: NanumGothic 권장)

설치:
```bash
pip install pandas numpy scipy scikit-learn matplotlib
# 한글 폰트 (Linux)
sudo apt-get install fonts-nanum
```

## 2. 디렉토리 구조

```
eum_analysis/
├── modules/
│   ├── data_loader.py          # 카드 데이터 3종 로더 + 시군구명 표준화
│   ├── living_pop_loader.py    # KOSIS 생활인구 로더
│   └── indicators.py           # 9개 지표 계산 함수
│
├── run_analysis.py             # Phase 1 분석 (22개 시군구, 6지표)
├── run_phase2.py               # Phase 2 분석 (13개 인구감소지역, 9지표)
│
├── output/                     # Phase 1 결과
│   ├── indicators_phase1.csv
│   ├── clustering_result.csv
│   ├── priority_targets.csv
│   ├── fig1_indicators.png
│   ├── fig2_pca_cluster.png
│   ├── fig3_diagnosis_matrix.png
│   └── README.md
│
└── phase2/                     # Phase 2 결과
    ├── indicators_phase2.csv
    ├── priority_phase2.csv
    ├── p2_fig1_MI_LRR_matrix.png       # ★ 핵심 진단 매트릭스
    ├── p2_fig2_indicators.png
    ├── p2_fig3_monthly_population.png
    ├── p2_fig4_pca_cluster.png
    └── PHASE2_REPORT.md
```

## 3. 입력 데이터 경로

모든 입력 파일은 `/mnt/user-data/uploads/`에 있어야 함:

**카드 데이터 (3개)**
- `2024년_경상남도_지역별_월별_카드매출현황.csv`
- `2024년_경상남도_지역별_시간대별_카드매출현황.csv`
- `2024년_경상남도_지역별_성연령별_카드매출현황.csv`

**생활인구 데이터 (1개)**
- `101_DT_1YL12002E_20260528202844.csv` (KOSIS 인구감소지역 생활인구)

## 4. 실행 방법

### Phase 1 (22개 시군구 전수, 카드 데이터만)
```bash
cd eum_analysis
python run_analysis.py
```

### Phase 2 (13개 인구감소지역, 카드 + 생활인구)
```bash
cd eum_analysis
python run_phase2.py
```

## 5. 모듈별 설명

### modules/data_loader.py
카드 데이터 3종을 로딩하고 시군구명을 표준화. 시군구명 매핑 사전(`SIGUNGU_STANDARD`)을 통해 표기 변형(공백 유무, 띄어쓰기 차이 등)을 통일.

**주요 함수**:
- `load_monthly()` → 월별 카드 매출 DataFrame
- `load_hourly()` → 시간대별 카드 매출 DataFrame
- `load_demographic()` → 성연령별 카드 매출 DataFrame
- `standardize_sigungu(name)` → 시군구명 표준화

### modules/living_pop_loader.py
KOSIS 인구감소지역 생활인구 CSV를 long 포맷으로 변환.

**주요 함수**:
- `load_living_population()` → 1248행 long DataFrame
- `aggregate_by_region(df_long)` → 시군구 × 월 단위 총 생활인구
- `aggregate_annual(df_long)` → 시군구별 연평균 생활인구
- `TARGET_REGIONS` → 분석 대상 13개 시·군 리스트

### modules/indicators.py
9개 지표를 계산하는 함수 모음.

**Phase 1 지표 (카드만 필요)**:
- `calculate_lrr(monthly_df)` → 지역 자금 환류율
- `calculate_cdi(monthly_df)` → 소비 다양성 지수 (Shannon)
- `calculate_nar(hourly_df)` → 야간 활성도 비율
- `calculate_agi(demographic_df)` → 고령 소비 비중
- `calculate_youth_ratio(demographic_df)` → 청년 소비 비중
- `calculate_sales_trend(monthly_df)` → 매출 추세 (회귀 기울기)

**Phase 2 지표 (생활인구 필요)**:
- `calculate_mi(card_sales, flow_population)` → 소비-유동 불일치 지수
- (STI, CPC는 run_phase2.py 내에서 직접 계산)

**통합 함수**:
- `build_indicator_table(monthly_df, hourly_df, demographic_df, flow_df=None)`
  - flow_df=None이면 Phase 1 지표만 6개
  - flow_df 있으면 MI까지 7개 (이전 버전 호환)

## 6. 새 데이터 추가 시 확장 방법

### 추가 유동인구 데이터(통신사 격자 등)가 들어왔을 때
1. `modules/data_loader.py`의 `SIGUNGU_STANDARD`에 표기 변형 추가
2. 새 로더 모듈 작성 (예: `modules/telecom_flow_loader.py`)
3. `indicators.py`의 `calculate_mi()` 함수의 인자 형식 맞춰서 호출

### 동(洞) 단위 분석으로 확장
- 카드 데이터는 시군구 단위라 직접 결합 불가
- 인구 데이터(집계구)는 동 단위로 집계 가능하므로
  - 인구 측면 지표(AGI, YR)만 동 단위 분석
  - 카드 측면 지표(LRR, CDI, MI)는 시군구 단위 유지
  - **두 단위 혼용 분석은 신중히 명시할 것**

## 7. 코드의 설계 원칙

1. **모듈화**: 로더-지표 계산-시각화 분리. 단위 테스트 용이.
2. **확장성**: 유동인구 데이터가 다른 단위/형식으로 와도 표준화 함수로 대응.
3. **재현성**: K-means random_state=42 고정. 시드 변경 시 군집 일부 변동 가능.
4. **투명성**: 각 지표의 정의와 해석을 docstring에 명시.

## 8. 알려진 한계

- 시군구명 매핑은 SIGUNGU_STANDARD에 등록된 표기만 처리. 새 표기 들어오면 추가 필요.
- K-means는 변수 스케일에 민감 → StandardScaler 필수 (이미 적용됨).
- 클러스터 명명 규칙(name_cluster_v2)은 절대 임계값 기반 → 다른 지역에 적용 시 임계값 재조정 필요.
- 위험점수 가중치(0.30/0.25/0.20/0.15/0.10)는 임의 설정. 정책 우선순위에 따라 조정 가능.

## 9. 분석 결과 요약

| Phase | 분석 대상 | 핵심 발견 |
|-------|---------|----------|
| 1 | 22개 시군구 전수 | 함양·하동 등 출혈+노화 복합형 7개 식별 |
| 2 | 13개 인구감소지역 | MI 지수로 합천·의령·산청의 "소화불량" 진단 가능해짐 |

자세한 내용은 `phase2/PHASE2_REPORT.md` 참조.
