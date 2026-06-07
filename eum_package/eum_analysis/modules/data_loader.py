"""
이음(E-um) 데이터 로더
- 카드 데이터 3종 로딩
- 시군구명 표준화 (key 통일)
- 유동인구 데이터 추후 결합용 인터페이스 제공
"""
import pandas as pd
import numpy as np
from pathlib import Path

# 프로젝트 루트 기준 data 폴더 자동 탐색
# (modules/ -> eum_analysis/ -> 프로젝트루트/data)
_HERE = Path(__file__).resolve()
_PROJECT_ROOT = _HERE.parent.parent.parent  # modules -> eum_analysis -> root
UPLOAD_DIR = _PROJECT_ROOT / 'data'
# 환경변수로 덮어쓰기 가능
import os
if os.environ.get('EUM_DATA_DIR'):
    UPLOAD_DIR = Path(os.environ['EUM_DATA_DIR'])

# 시군구명 표준화 매핑 (유동 데이터가 다른 표기로 와도 통일)
SIGUNGU_STANDARD = {
    # 표준 표기 (카드 데이터 기준)
    '창원시 의창구': '창원시 의창구',
    '창원시 성산구': '창원시 성산구',
    '창원시 마산합포구': '창원시 마산합포구',
    '창원시 마산회원구': '창원시 마산회원구',
    '창원시 진해구': '창원시 진해구',
    '진주시': '진주시', '통영시': '통영시', '사천시': '사천시', '김해시': '김해시',
    '밀양시': '밀양시', '거제시': '거제시', '양산시': '양산시',
    '의령군': '의령군', '함안군': '함안군', '창녕군': '창녕군', '고성군': '고성군',
    '남해군': '남해군', '하동군': '하동군', '산청군': '산청군', '함양군': '함양군',
    '거창군': '거창군', '합천군': '합천군',
    # 자주 발생하는 변형 표기들
    '창원시의창구': '창원시 의창구',
    '창원의창구': '창원시 의창구',
    '창원 의창구': '창원시 의창구',
}


def standardize_sigungu(name: str) -> str:
    """시군구명을 표준 표기로 변환. 유동 데이터 결합 시 핵심."""
    if pd.isna(name):
        return None
    name = str(name).strip()
    return SIGUNGU_STANDARD.get(name, name)


def load_monthly():
    """월별 카드 매출 데이터 로딩"""
    df = pd.read_csv(UPLOAD_DIR / '2024년_경상남도_지역별_월별_카드매출현황.csv',
                     encoding='cp949')
    df['시군구명'] = df['시군구명'].apply(standardize_sigungu)
    df['연월'] = df['연월'].astype(str)
    df['월'] = df['연월'].str[-2:].astype(int)
    return df


def load_hourly():
    """시간대별 카드 매출 데이터 로딩"""
    df = pd.read_csv(UPLOAD_DIR / '2024년_경상남도_지역별_시간대별_카드매출현황.csv',
                     encoding='cp949')
    df['시군구명'] = df['시군구명'].apply(standardize_sigungu)
    return df


def load_demographic():
    """성연령별 카드 매출 데이터 로딩"""
    df = pd.read_csv(UPLOAD_DIR / '2024년_경상남도_지역별_성연령별_카드매출현황.csv',
                     encoding='cp949')
    df['시군구명'] = df['시군구명'].apply(standardize_sigungu)
    df['연월'] = df['연월'].astype(str)
    return df


# ===== 유동인구 데이터 결합 인터페이스 (Phase 2) =====
def load_flow_data(filepath, spatial_unit='auto', time_unit='auto'):
    """
    유동인구 데이터 로딩 (추후 추가될 데이터용).

    Parameters
    ----------
    filepath : str
        유동 데이터 파일 경로
    spatial_unit : str
        'sigungu' (시군구) | 'dong' (행정동) | 'auto' (컬럼명으로 자동 추론)
    time_unit : str
        'month' | 'day' | 'hour' | 'auto'

    Returns
    -------
    df : DataFrame
        표준화된 컬럼: [지역키, 시간키, 유동인구]
    """
    # 추후 구현 - 실제 데이터 형식 확인 후 작성
    raise NotImplementedError(
        "유동인구 데이터 도착 시 형식 확인 후 구현 예정. "
        "필요 표준 컬럼: 지역키, 시간키, 유동인구"
    )


def merge_card_flow(card_df, flow_df, on='시군구명'):
    """카드 데이터와 유동인구 데이터 결합. 표준화된 키 기준."""
    return card_df.merge(flow_df, on=on, how='left')


if __name__ == '__main__':
    print("데이터 로딩 테스트...")
    m = load_monthly()
    print(f"월별 데이터: {m.shape}, 시군구 수: {m['시군구명'].nunique()}")
    h = load_hourly()
    print(f"시간대별: {h.shape}, 시군구 수: {h['시군구명'].nunique()}")
    d = load_demographic()
    print(f"성연령별: {d.shape}, 시군구 수: {d['시군구명'].nunique()}")
