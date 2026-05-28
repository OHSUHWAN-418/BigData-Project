"""
이음(E-um) Phase 2: 생활인구 데이터 로더

KOSIS 인구감소지역 생활인구 통계 (101_DT_1YL12002E)
- 출처: 통계청 + 행정안전부 (통신3사 데이터 기반)
- 정의: 월 1회 이상 해당 지역에 3시간 이상 체류한 인구의 월별 합계
- 공간: 경남 13개 시·군 (인구감소지역 11 + 관심지역 2)
- 시간: 2024년 1~12월
- 연령: 7구간 (20세미만, 20대, 30대, 40대, 50대, 60대, 70세 이상)
"""
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR_CANDIDATES = [
    PROJECT_ROOT / 'data',
    PROJECT_ROOT.parent.parent,
    Path('/mnt/user-data/uploads'),
]
FILE_NAME = '101_DT_1YL12002E_20260528202844.csv'


def resolve_living_population_file() -> Path:
    """프로젝트 data 폴더와 원자료 수신 폴더에서 생활인구 CSV를 찾는다."""
    for base_dir in DATA_DIR_CANDIDATES:
        path = base_dir / FILE_NAME
        if path.exists():
            return path
    searched = [str(base_dir / FILE_NAME) for base_dir in DATA_DIR_CANDIDATES]
    raise FileNotFoundError(f"생활인구 CSV를 찾지 못했습니다. 확인 경로: {searched}")

# 카드 데이터의 시군구명 표기와 일치시키는 매핑
LIVING_POP_NAME_MAP = {
    '경상남도 통영시': '통영시',
    '경상남도 사천시': '사천시',
    '경상남도 밀양시': '밀양시',
    '경상남도 의령군': '의령군',
    '경상남도 함안군': '함안군',
    '경상남도 창녕군': '창녕군',
    '경상남도 고성군': '고성군',
    '경상남도 남해군': '남해군',
    '경상남도 하동군': '하동군',
    '경상남도 산청군': '산청군',
    '경상남도 함양군': '함양군',
    '경상남도 거창군': '거창군',
    '경상남도 합천군': '합천군',
}

# 인구감소지역 13개 시·군 (이번 Phase 2 분석 대상)
TARGET_REGIONS = list(LIVING_POP_NAME_MAP.values())


def load_living_population():
    """
    생활인구 데이터 로딩 및 long 포맷 변환.

    Returns
    -------
    DataFrame : columns = [시군구명, 지역구분(감소/관심), 연령대, 월, 생활인구]
    """
    df = pd.read_csv(resolve_living_population_file(), encoding='cp949')

    # 빈 컬럼 제거
    df = df.drop(columns=[c for c in df.columns if 'Unnamed' in c])

    # 시군구명 표준화
    df['시군구명'] = df['행정구역별'].map(LIVING_POP_NAME_MAP)
    df = df.dropna(subset=['시군구명'])

    # 컬럼명 정리
    df = df.rename(columns={'지역구분': '인구감소구분', '항목': '연령대'})

    # 월별 컬럼 wide → long 변환
    month_cols = [c for c in df.columns if '월' in c]
    df_long = df.melt(
        id_vars=['시군구명', '인구감소구분', '연령대'],
        value_vars=month_cols,
        var_name='월',
        value_name='생활인구'
    )

    # 월 정수 변환 (예: '2024.01 월' → 1)
    df_long['월'] = df_long['월'].str.extract(r'2024\.(\d+)').astype(int)

    # 숫자 변환
    df_long['생활인구'] = pd.to_numeric(df_long['생활인구'], errors='coerce')
    df_long = df_long.dropna(subset=['생활인구'])

    return df_long


def aggregate_by_region(df_long):
    """시군구 × 월 단위 총 생활인구 (연령대 합계 = '계(명)')"""
    return df_long[df_long['연령대'] == '계(명)']\
           .groupby(['시군구명', '월'])['생활인구'].sum().reset_index()


def aggregate_annual(df_long):
    """시군구별 연간 평균 생활인구 (계 기준)"""
    monthly = aggregate_by_region(df_long)
    return monthly.groupby('시군구명')['생활인구'].mean().rename('연평균_생활인구')


if __name__ == '__main__':
    df = load_living_population()
    print(f"Shape: {df.shape}")
    print(f"시군구: {df['시군구명'].nunique()}개 — {sorted(df['시군구명'].unique())}")
    print(f"연령대: {df['연령대'].unique().tolist()}")
    print(f"월 범위: {df['월'].min()} ~ {df['월'].max()}")

    annual = aggregate_annual(df)
    print(f"\n=== 연평균 생활인구 (Top 13) ===")
    print(annual.sort_values(ascending=False).astype(int).to_string())
