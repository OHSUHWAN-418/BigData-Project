"""
이음(E-um) 지표 계산 모듈
- 현재(Phase 1): LRR, CDI, NAR, AGI (유동 데이터 불필요)
- 추후(Phase 2): MI (유동 데이터 결합 후)
"""
import pandas as pd
import numpy as np
from scipy import stats


def calculate_lrr(monthly_df):
    """
    LRR (Local Return Ratio, 지역 자금 환류율)

    LRR = 경남 내 유입 매출 / 전체 매출

    값이 낮을수록 자금이 역외로 유출됨 = 출혈성 침체 후보.

    Returns
    -------
    pd.Series : index=시군구명, value=LRR (0~1)
    """
    total = monthly_df.groupby('시군구명')['매출합계(원)'].sum()
    local = monthly_df[monthly_df['유입지'] == '경남'].groupby('시군구명')['매출합계(원)'].sum()
    lrr = (local / total).fillna(0)
    return lrr.rename('LRR')


def calculate_cdi(monthly_df):
    """
    CDI (Consumption Diversity Index, 소비 다양성 지수)

    13개 업종별 매출 비중의 Shannon Entropy.
    값이 낮을수록 특정 업종 의존도 높음 = 단조형 침체 후보.

    Returns
    -------
    pd.Series : index=시군구명, value=CDI (0 ~ log(13)≈2.56)
    """
    sales_by_cat = monthly_df.groupby(['시군구명', '분류'])['매출합계(원)'].sum().reset_index()

    def shannon(group):
        p = group['매출합계(원)'] / group['매출합계(원)'].sum()
        p = p[p > 0]
        return -(p * np.log(p)).sum()

    cdi = sales_by_cat.groupby('시군구명').apply(shannon, include_groups=False)
    return cdi.rename('CDI')


def calculate_nar(hourly_df):
    """
    NAR (Night Activity Ratio, 야간 활성도 비율)

    NAR = (18시~23시 매출) / 전체 매출.
    값이 낮을수록 낮에만 활동하는 통과형 상권.

    Returns
    -------
    pd.Series : index=시군구명, value=NAR (0~1)
    """
    total = hourly_df.groupby('시군구명')['매출합계(원)'].sum()
    night = hourly_df[hourly_df['시간대'].between(18, 23)].groupby('시군구명')['매출합계(원)'].sum()
    nar = (night / total).fillna(0)
    return nar.rename('NAR')


def calculate_agi(demographic_df):
    """
    AGI (Aging Index, 고령 소비 지수)

    60대 이상 매출 비중. 높을수록 노화형 침체 후보.

    Returns
    -------
    pd.Series : index=시군구명, value=AGI (0~1)
    """
    elderly_ages = ['60대', '70대이상']
    total = demographic_df.groupby('시군구명')['매출합계(원)'].sum()
    elderly = demographic_df[demographic_df['연령대'].isin(elderly_ages)]\
              .groupby('시군구명')['매출합계(원)'].sum()
    agi = (elderly / total).fillna(0)
    return agi.rename('AGI')


def calculate_youth_ratio(demographic_df):
    """
    YR (Youth Ratio, 청년 소비 비중) — 보조 지표

    20대~30대 매출 비중. 낮으면 청년 인구 유출 가능성.
    """
    youth_ages = ['20대미만', '20대', '30대']
    total = demographic_df.groupby('시군구명')['매출합계(원)'].sum()
    youth = demographic_df[demographic_df['연령대'].isin(youth_ages)]\
            .groupby('시군구명')['매출합계(원)'].sum()
    yr = (youth / total).fillna(0)
    return yr.rename('YR')


def calculate_sales_trend(monthly_df):
    """
    Sales Trend — 월별 매출 추세 (회귀 기울기)

    2024년 1월 → 12월 매출 변화의 선형 추세 기울기.
    음수일수록 매출 감소 추세.

    Returns
    -------
    pd.Series : index=시군구명, value=정규화된 추세 (slope/mean)
    """
    monthly_sales = monthly_df.groupby(['시군구명', '월'])['매출합계(원)'].sum().reset_index()

    def trend(group):
        if len(group) < 3:
            return np.nan
        slope, _, _, _, _ = stats.linregress(group['월'], group['매출합계(원)'])
        return slope / group['매출합계(원)'].mean()  # 정규화

    result = monthly_sales.groupby('시군구명').apply(trend, include_groups=False)
    return result.rename('TREND')


# ===== Phase 2: 유동 데이터 도착 시 추가 =====
def calculate_mi(card_sales, flow_population):
    """
    MI (Mismatch Index, 소비-유동 불일치 지수) — 유동 데이터 도착 후 활성화

    MI = log(매출액 / 유동인구) - 경남 평균

    Parameters
    ----------
    card_sales : pd.Series
        시군구별 평균 매출액
    flow_population : pd.Series
        시군구별 평균 유동인구 (인덱스가 표준화된 시군구명이어야 함)

    Returns
    -------
    pd.Series : MI 지수
    """
    # 인덱스 정합성 확인
    common = card_sales.index.intersection(flow_population.index)
    if len(common) == 0:
        raise ValueError("카드와 유동 데이터 시군구명이 일치하지 않음. 표준화 확인 필요.")

    sales = card_sales.loc[common]
    flow = flow_population.loc[common]
    ratio = sales / flow
    mi = np.log(ratio) - np.log(ratio).mean()
    return mi.rename('MI')


def build_indicator_table(monthly_df, hourly_df, demographic_df, flow_df=None):
    """
    모든 지표를 결합한 시군구별 지표 테이블 생성.

    flow_df가 None이면 Phase 1 지표만, 있으면 MI 포함하여 Phase 2 지표까지 생성.
    """
    indicators = pd.concat([
        calculate_lrr(monthly_df),
        calculate_cdi(monthly_df),
        calculate_nar(hourly_df),
        calculate_agi(demographic_df),
        calculate_youth_ratio(demographic_df),
        calculate_sales_trend(monthly_df),
    ], axis=1)

    if flow_df is not None:
        # Phase 2: MI 추가
        card_sales = monthly_df.groupby('시군구명')['매출합계(원)'].sum()
        flow_pop = flow_df.groupby('시군구명')['유동인구'].sum()
        indicators['MI'] = calculate_mi(card_sales, flow_pop)

    return indicators


if __name__ == '__main__':
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent))
    from data_loader import load_monthly, load_hourly, load_demographic

    print("지표 계산 테스트...")
    m = load_monthly()
    h = load_hourly()
    d = load_demographic()

    table = build_indicator_table(m, h, d)
    print(f"\n지표 테이블 shape: {table.shape}")
    print(table.head())
