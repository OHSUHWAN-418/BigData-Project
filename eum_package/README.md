# 「이음(E-um)」 분석 패키지 — Claude Code 즉시 실행용

이 폴더는 Claude Code 또는 로컬 환경에서 **압축만 풀면 바로 실행**되도록 구성됨.

## 빠른 시작

```bash
# 1. 의존성 설치
pip install -r requirements.txt
# (Linux 한글 폰트) sudo apt-get install fonts-nanum

# 2. 분석 실행 (어느 위치에서 실행해도 동작)
python eum_analysis/run_phase2.py
```

결과물은 `eum_analysis/phase2/` 에 생성됨 (csv 2개 + png 4개).

## Claude Code에서 시작하는 법

이 폴더를 열고 Claude Code에 다음과 같이 입력:

```
CLAUDE.md를 읽고 현재 상태를 파악한 뒤,
"남은 일 (보고서 동기화)" 작업을 진행해줘.
```

## 폴더 구성

```
.
├── CLAUDE.md                 # ★ 작업 지시서 (먼저 읽을 것)
├── PROJECT_HANDOFF.md        # 프로젝트 전체 맥락 (상세)
├── README.md                 # 이 문서
├── requirements.txt          # 의존성
├── 보고서_초안_v1.md          # 공모전 보고서 초안 (수정 대상)
├── 이음_계획서_v4.docx/pdf    # 학교 제출용 계획서 (완성)
│
├── data/                     # 원본 데이터 4종 (cp949 인코딩)
│   ├── 2024년_경상남도_지역별_월별_카드매출현황.csv
│   ├── 2024년_경상남도_지역별_시간대별_카드매출현황.csv
│   ├── 2024년_경상남도_지역별_성연령별_카드매출현황.csv
│   └── 101_DT_1YL12002E_*.csv
│
└── eum_analysis/
    ├── modules/              # 로더 + 지표 계산 함수
    ├── run_phase2.py         # ★ 메인 분석 (표준 위험점수 산식 반영됨)
    ├── run_analysis.py       # Phase 1 (참고용)
    └── phase2/               # 분석 결과 (csv·png)
```

## 현재 분석 결과 핵심 (검증됨)

- 위험점수 1위: 하동군 (0.865)
- MI 최저: 합천군 (-1.016)
- CPC 최저: 합천군 (11,380원/월) / 최고: 통영시 (86,764원/월)
- STI 최고: 산청군 (0.718, 관광 의존)

자세한 내용은 CLAUDE.md 참조.
