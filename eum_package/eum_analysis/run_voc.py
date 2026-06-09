# -*- coding: utf-8 -*-
"""
이음(E-um) — VOC(리뷰) 소량 수집기  [보조 분석: '왜 소비가 안 되나'의 정성 근거]

목적: 산청·하동 핵심 관광지의 방문자 후기를 소량 수집해, 본 보고서가 데이터로
      보인 '통과형 소비구조'(데이터랩: 산청 체류성 1.8%)를 방문자 목소리로 보강한다.

수집 대상(네이버 지도 '방문자 리뷰'):
  - 산청: 동의보감촌, 남사예담촌
  - 하동: 화개장터, 최참판댁(악양)

산출물:
  - eum_analysis/phase2/voc_reviews.csv        (장소, 평점/방문키워드, 작성일, 본문)
  - 콘솔: 소비·체류 관련 키워드 빈도 표 (먹을곳/식당/카페/주차/체류/볼거리/결제 등)

※ 주의
  - 네이버 지도는 동적(JS)·iframe 구조라 Selenium 필요. 사이트 DOM이 바뀌면
    CSS 선택자(SELECTORS)를 콘솔에서 확인 후 한 줄만 고치면 된다.
  - '소량'이 목적이므로 장소당 최근 리뷰 약 40~60개만 수집한다(과수집 금지).

설치:
  pip install selenium webdriver-manager beautifulsoup4 pandas
실행:
  python eum_analysis/run_voc.py
"""
import time, re, csv, sys
from collections import Counter

try:
    import pandas as pd
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
except ImportError as e:
    sys.exit(f"[의존성 누락] {e}\n  pip install selenium webdriver-manager beautifulsoup4 pandas")

# ── 수집 대상 ──────────────────────────────────────────────
TARGETS = [
    ("산청", "동의보감촌"),
    ("산청", "남사예담촌"),
    ("하동", "화개장터"),
    ("하동", "최참판댁"),
]
MAX_REVIEWS_PER_PLACE = 50          # 장소당 상한(소량)
SCROLL_ROUNDS = 12

# 소비전환/체류 진단 키워드(빈도 집계용) — 우리 처방 가설과 직접 연결
KW = {
    "먹거리·식당": ["먹을", "식당", "맛집", "음식", "카페", "메뉴", "밥집"],
    "체류·볼거리": ["볼거리", "둘러볼", "금방", "심심", "할게없", "체류", "머물", "코스", "짧"],
    "주차·접근": ["주차", "교통", "버스", "멀", "접근"],
    "결제·상점": ["결제", "카드", "현금", "상점", "가게", "살게", "살 게", "기념품"],
    "가격·불만": ["비싸", "아쉽", "실망", "별로", "불편"],
}

def make_driver():
    opt = Options()
    opt.add_argument("--headless=new")
    opt.add_argument("--lang=ko_KR")
    opt.add_argument("--window-size=1280,2000")
    opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opt)

def collect_place(driver, region, name):
    """네이버 지도 검색 → 첫 결과 → 리뷰 탭 → 본문 수집."""
    q = f"{region} {name}"
    driver.get(f"https://map.naver.com/p/search/{q}")
    time.sleep(3)
    reviews = []
    try:
        # 검색결과/장소 entryIframe 진입 (네이버 지도 구조)
        driver.switch_to.default_content()
        # searchIframe에서 첫 장소 클릭
        try:
            driver.switch_to.frame("searchIframe")
            driver.find_elements(By.CSS_SELECTOR, "a")[0].click()
            time.sleep(2)
            driver.switch_to.default_content()
        except Exception:
            driver.switch_to.default_content()
        driver.switch_to.frame("entryIframe")
        time.sleep(2)
        # '리뷰' 탭 클릭
        for a in driver.find_elements(By.CSS_SELECTOR, "a, span"):
            if a.text.strip() in ("리뷰", "방문자 리뷰"):
                a.click(); break
        time.sleep(2)
        # 스크롤하며 리뷰 로딩
        for _ in range(SCROLL_ROUNDS):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            # 리뷰 본문 후보(클래스는 사이트 변경 시 콘솔에서 확인 후 수정)
            cand = [t.get_text(" ", strip=True) for t in soup.select("div.pui__vn15t2, span.zPfVt, div.review_text")]
            for c in cand:
                if c and len(c) > 5 and c not in reviews:
                    reviews.append(c)
            if len(reviews) >= MAX_REVIEWS_PER_PLACE:
                break
    except Exception as e:
        print(f"  [경고] {q} 수집 일부 실패: {e}  → 선택자(SELECTORS) 확인 필요")
    return [{"region": region, "place": name, "text": r} for r in reviews[:MAX_REVIEWS_PER_PLACE]]

def main():
    driver = make_driver()
    rows = []
    for region, name in TARGETS:
        print(f"[수집] {region} {name} ...")
        rows += collect_place(driver, region, name)
        print(f"  누적 {len(rows)}건")
    driver.quit()

    if not rows:
        print("\n수집 0건 — 네이버 지도 DOM 변경 가능. collect_place()의 CSS 선택자를 확인하세요.")
        return
    df = pd.DataFrame(rows)
    out = "eum_analysis/phase2/voc_reviews.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n저장: {out}  (총 {len(df)}건)")

    # 소비·체류 키워드 빈도
    print("\n=== 소비전환/체류 관련 VOC 키워드 빈도 ===")
    text_all = " ".join(df["text"])
    n = len(df)
    for theme, words in KW.items():
        hits = sum(text_all.count(w) for w in words)
        docs = sum(any(w in t for w in words) for t in df["text"])
        print(f"{theme:10s} | 언급 {hits:4d}회 | 리뷰 {docs}/{n}건({docs*100//max(n,1)}%)")

if __name__ == "__main__":
    main()
