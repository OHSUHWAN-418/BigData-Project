// 이음(E-um) 발표자료 v3 — 흑백 미니멀 템플릿, 보고서 v7 순서
const pptxgen = require("pptxgenjs");
const path = require("path");

const MEDIA = "C:/Users/PC/Desktop/빅데이터/깃허브/eum_package/unpacked_v7b/word/media";
const img = (n) => path.join(MEDIA, `image${n}.png`);

const K = "111111";      // 검정
const GRAY = "888888";   // 부제 회색
const MID = "555555";
const LINE = "D9D9D9";
const BG = "F7F7F7";
const FONT = "Malgun Gothic";

const pptx = new pptxgen();
pptx.defineLayout({ name: "W169", width: 13.333, height: 7.5 });
pptx.layout = "W169";

// ── 공통 장식: 상단 바 + 하단 라인/사선 ──
function deco(s) {
  s.background = { color: "FFFFFF" };
  s.addShape("rect", { x: 0, y: 0, w: 13.333, h: 0.55, fill: { color: BG }, line: { color: LINE, width: 0.5 } });
  s.addText([
    { text: "E-um", options: { bold: true, color: K } },
    { text: "  이음", options: { color: "777777" } },
  ], { x: 0.45, y: 0.06, w: 4, h: 0.42, fontFace: FONT, fontSize: 13, align: "left" });
  s.addText("2026 GyeongNam Big Data Contest", {
    x: 8.83, y: 0.06, w: 4.05, h: 0.42, fontFace: "Georgia", italic: true, fontSize: 10, color: "AAAAAA", align: "right",
  });
  s.addShape("rect", { x: 0.45, y: 7.12, w: 12.44, h: 0.035, fill: { color: K } });
  s.addShape("parallelogram", { x: 11.05, y: 6.95, w: 1.84, h: 0.17, fill: { color: K }, line: { type: "none" } });
}

// ── 제목 블록 ──
function head(s, tag, title, sub) {
  if (tag) s.addText(tag, { x: 0.47, y: 0.78, w: 6, h: 0.3, fontFace: FONT, fontSize: 11, color: "999999", bold: true, charSpacing: 2 });
  s.addText(title, { x: 0.42, y: 1.02, w: 12.4, h: 0.62, fontFace: FONT, fontSize: 27, bold: true, color: K });
  if (sub) s.addText(sub, { x: 0.47, y: 1.62, w: 12.3, h: 0.55, fontFace: FONT, fontSize: 12.5, color: GRAY, lineSpacingMultiple: 1.25 });
}

// 밑줄 행 (템플릿 p3 스타일)
function rows(s, items, x, y, w, opt = {}) {
  const gap = opt.gap || 0.62;
  items.forEach((it, i) => {
    s.addText(it, { x, y: y + i * gap, w, h: gap - 0.08, fontFace: FONT, fontSize: opt.size || 13.5, bold: opt.bold !== false, color: opt.color || K, valign: "middle" });
    s.addShape("rect", { x, y: y + (i + 1) * gap - 0.06, w, h: 0.011, fill: { color: LINE } });
  });
}

/* ════════ 1. 표지 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  s.addText("생활인구는 왜\n지역 소비로 이어지지 않는가", {
    x: 0.7, y: 2.0, w: 11.93, h: 2.2, fontFace: FONT, fontSize: 41, bold: true, color: K, align: "center", lineSpacingMultiple: 1.15,
  });
  s.addText("경남 13개 인구감소지역 · 카드매출 3종 × KOSIS 생활인구 — 위험도 분석과 지역 유형 분류", {
    x: 0.7, y: 4.25, w: 11.93, h: 0.4, fontFace: FONT, fontSize: 14, color: GRAY, align: "center",
  });
  s.addText([
    { text: "팀 E-um", options: { bold: true, color: K } },
    { text: "   김재민 · 강원준 · 오수환", options: { color: MID } },
  ], { x: 0.7, y: 4.95, w: 11.93, h: 0.45, fontFace: FONT, fontSize: 15, align: "center" });
  s.addText("2026.06", { x: 0.45, y: 6.62, w: 2, h: 0.4, fontFace: FONT, fontSize: 13, color: K });
}

/* ════════ 2. 목차 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  s.addText("목차", { x: 1.4, y: 3.0, w: 3.2, h: 1.2, fontFace: FONT, fontSize: 44, bold: true, color: K });
  const toc1 = [["01", "개요"], ["02", "분석 대상"], ["03", "데이터 분석"], ["04", "이음(E-um)의 설계"]];
  const toc2 = [["05", "분석 결과"], ["06", "유형별 정책 방안"], ["07", "결론 및 기대효과"], ["08", "한계 및 향후 과제"]];
  const draw = (list, x) => list.forEach(([n, t], i) => {
    const y = 1.85 + i * 1.0;
    s.addText([
      { text: n + "  ", options: { color: "BBBBBB", bold: true } },
      { text: t, options: { color: K, bold: true } },
    ], { x, y, w: 3.6, h: 0.55, fontFace: FONT, fontSize: 17 });
    s.addShape("rect", { x, y: y + 0.62, w: 3.5, h: 0.011, fill: { color: LINE } });
  });
  draw(toc1, 5.6); draw(toc2, 9.45);
}

/* ════════ 3. 01 문제 제기 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "01 · 개요", "문제 제기", "경남 인구감소지역 상권 정책의 오랜 전제 — “사람이 없으니 상권이 죽는다” — 는 현실의 절반만 설명한다.");
  s.addText("“문제는 사람이 없는 것인가,\n있는 사람이 소비로 이어지지 않는 것인가?”", {
    x: 0.9, y: 2.55, w: 11.5, h: 1.5, fontFace: FONT, fontSize: 25, bold: true, color: K, align: "center", lineSpacingMultiple: 1.25,
  });
  rows(s, [
    "2024년 경남 순이동 −9,069명(통계청) — 정주인구 감소는 구조적 상수",
    "방문 인구가 적지 않은데도 지역 소비가 일어나지 않는 지역이 있다",
    "남은 정책 여력은 ‘생활인구를 소비로 전환’하는 데 집중될 수밖에 없다",
  ], 1.5, 4.45, 10.4, { gap: 0.72, size: 14.5 });
}

/* ════════ 4. 02 분석 대상 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "02 · 분석 대상", "왜 13개 시군인가", "행정안전부 지정 인구감소지역 11곳 + 관심지역 2곳 — KOSIS 생활인구가 제공되는 전체");
  s.addShape("rect", { x: 0.45, y: 2.45, w: 4.9, h: 3.9, fill: { color: BG }, line: { type: "none" } });
  s.addShape("rect", { x: 0.45, y: 2.45, w: 0.05, h: 3.9, fill: { color: K } });
  s.addText([
    { text: "인구감소지역 (11)\n", options: { bold: true, fontSize: 14.5, color: K } },
    { text: "밀양 · 의령 · 함안 · 창녕 · 고성 · 남해\n하동 · 산청 · 함양 · 거창 · 합천\n\n", options: { fontSize: 13, color: MID } },
    { text: "관심지역 (2)\n", options: { bold: true, fontSize: 14.5, color: K } },
    { text: "통영 · 사천", options: { fontSize: 13, color: MID } },
  ], { x: 0.75, y: 2.75, w: 4.4, h: 3.3, fontFace: FONT, lineSpacingMultiple: 1.3 });
  const reasons = [
    ["01", "정책 시급성", "행안부 지정 인구감소·관심지역 — 정책 우선 대상"],
    ["02", "데이터 가용성", "이 13곳만 KOSIS 생활인구 제공 → 핵심 지표 MI·CPC 산출 가능"],
    ["03", "공간 대표성", "도시(통영·사천·밀양)–산간(산청·함양)–해안(남해·고성) 포괄"],
  ];
  reasons.forEach(([n, t, d], i) => {
    const y = 2.5 + i * 1.25;
    s.addText([
      { text: n + "   ", options: { color: "BBBBBB", bold: true, fontSize: 18 } },
      { text: t, options: { color: K, bold: true, fontSize: 16 } },
    ], { x: 5.95, y, w: 6.9, h: 0.45, fontFace: FONT });
    s.addText(d, { x: 6.6, y: y + 0.42, w: 6.3, h: 0.4, fontFace: FONT, fontSize: 12.5, color: MID });
    s.addShape("rect", { x: 5.95, y: y + 0.95, w: 6.9, h: 0.011, fill: { color: LINE } });
  });
  s.addText("경남 22개 전수(Phase 1) 분석 후 13곳(Phase 2)으로 정밀 분석 — 보고서의 중심은 Phase 2", {
    x: 5.95, y: 6.35, w: 6.9, h: 0.4, fontFace: FONT, fontSize: 11.5, color: GRAY,
  });
}

/* ════════ 5. 03 수집 데이터 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "03 · 데이터 분석", "수집 데이터", "공공 빅데이터 5종을 결합 — 카드매출(소비)과 생활인구(방문 흐름)의 결합이 분석의 출발점");
  const th = { fill: { color: K }, color: "FFFFFF", bold: true, fontFace: FONT, fontSize: 12.5, align: "center", valign: "middle" };
  const td = { fontFace: FONT, fontSize: 12, color: K, valign: "middle", fill: { color: "FFFFFF" } };
  const tg = { ...td, color: MID };
  s.addTable([
    [{ text: "데이터", options: th }, { text: "출처", options: th }, { text: "용도", options: th }],
    [{ text: "카드매출 3종 (월별 · 시간대별 · 성연령별)", options: { ...td, bold: true } }, { text: "경남 빅데이터 허브플랫폼 (2024)", options: tg }, { text: "LRR · CDI · TREND · NAR · AGI · YR", options: tg }],
    [{ text: "생활인구 (인구감소지역)", options: { ...td, bold: true } }, { text: "KOSIS — 통계청 · 행안부, 통신3사 기반", options: tg }, { text: "MI · CPC · STI  (핵심 지표)", options: { ...tg, bold: true, color: K } }],
    [{ text: "시군구 행정경계", options: { ...td, bold: true } }, { text: "통계청 KOSTAT", options: tg }, { text: "침체유형 · 위험점수 지도", options: tg }],
    [{ text: "관광소비 (업종 · 체류/통과)", options: { ...td, bold: true } }, { text: "한국관광 데이터랩 (신한카드)", options: tg }, { text: "관광형 개선 — 체류 전환", options: tg }],
    [{ text: "상가정보 (읍·면별 점포)", options: { ...td, bold: true } }, { text: "소상공인시장진흥공단", options: tg }, { text: "개선 카드의 공간 근거", options: tg }],
  ], {
    x: 0.45, y: 2.35, w: 12.44, colW: [4.6, 4.2, 3.64], rowH: [0.5, 0.62, 0.62, 0.62, 0.62, 0.62],
    border: [{ pt: 0, color: "FFFFFF" }, { pt: 0, color: "FFFFFF" }, { pt: 0.75, color: LINE }, { pt: 0, color: "FFFFFF" }],
  });
  s.addText("전 과정 재현 가능 — K-means · RandomForest 모두 random_state=42 고정, 시군명 표준화 사전으로 표기 통일", {
    x: 0.45, y: 6.45, w: 12.4, h: 0.4, fontFace: FONT, fontSize: 11.5, color: GRAY,
  });
}

/* ════════ 6. 03 두 가지 발견 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "03 · 데이터 분석", "데이터가 보여준 두 가지", "가설 없이 데이터를 먼저 보았다 — 두 관찰이 연구의 방향을 결정했다");
  s.addText([
    { text: "발견 ①  인구감소지역 안에도 양극화 — 7.6배\n", options: { bold: true, fontSize: 15.5, color: K } },
    { text: "방문 1인당 월 소비: 합천 11,380원 vs 통영 86,764원. 같은 군 단위인 거창과 합천도 5.7배.", options: { fontSize: 12, color: MID } },
  ], { x: 0.45, y: 2.2, w: 6.1, h: 1.1, fontFace: FONT, lineSpacingMultiple: 1.2 });
  s.addText([
    { text: "발견 ②  산청 — 방문은 최고, 소비는 절반\n", options: { bold: true, fontSize: 15.5, color: K } },
    { text: "성수기 생활인구 +72%(13곳 최대), 1인당 월 16,536원(평균의 절반), 야간 매출 19.2%. “낮에 왔다 그냥 가는” 방문.", options: { fontSize: 12, color: MID } },
  ], { x: 6.85, y: 2.2, w: 6.05, h: 1.1, fontFace: FONT, lineSpacingMultiple: 1.2 });
  s.addImage({ path: img(1), x: 2.78, y: 3.4, w: 7.77, h: 3.14 });
  s.addText("그림 1.  (a) 방문 1인당 월 소비액(2024) · (b) 월별 생활인구(1월=100)", { x: 2.06, y: 6.6, w: 9.2, h: 0.3, fontFace: FONT, fontSize: 10.5, color: GRAY, align: "center" });
}

/* ════════ 7. 03 소결 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "03 · 데이터 분석", "소결 — 측정되지 않는 ‘소비 전환’", null);
  s.addText("방문(생활인구)의 크기와 소비(카드매출)의 크기는\n비례하지 않는다.", {
    x: 0.9, y: 2.4, w: 11.5, h: 1.4, fontFace: FONT, fontSize: 24, bold: true, color: K, align: "center", lineSpacingMultiple: 1.25,
  });
  s.addText("간극의 크기와 원인은 지역마다 다르다.\n그러나 기존 통계와 분석 어디에도 “방문이 소비로 전환되는 정도”를 직접 재는 지표는 없었다.", {
    x: 1.5, y: 4.1, w: 10.3, h: 0.95, fontFace: FONT, fontSize: 14.5, color: MID, align: "center", lineSpacingMultiple: 1.35,
  });
  s.addShape("rect", { x: 4.42, y: 5.45, w: 4.5, h: 0.7, fill: { color: K } });
  s.addText("이 공백을 메우기 위해 이음(E-um)을 설계했다", {
    x: 4.42, y: 5.45, w: 4.5, h: 0.7, fontFace: FONT, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle",
  });
}

/* ════════ 8. 04 MI를 만든 이유 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "04 · 이음(E-um)의 설계", "MI를 만든 이유", "방문과 소비를 ‘잇는’ 지표 — 생활인구가 지역 소비로 전환되는 정도를 직접 잰다");
  s.addShape("rect", { x: 0.45, y: 2.35, w: 12.44, h: 1.05, fill: { color: BG }, line: { type: "none" } });
  s.addShape("rect", { x: 0.45, y: 2.35, w: 0.06, h: 1.05, fill: { color: K } });
  s.addText([
    { text: "MI (Mismatch Index)  =  ", options: { bold: true, fontSize: 17 } },
    { text: "Log( 연간매출 / 연평균 생활인구 ) − 13곳 평균", options: { fontSize: 17 } },
  ], { x: 0.85, y: 2.35, w: 11.8, h: 1.05, fontFace: FONT, color: K, valign: "middle" });
  rows(s, [
    "분모가 정주인구가 아니라 생활인구 — 실제 체류 흐름 기준 (「인구감소지역 지원 특별법」 2022 공식 지표)",
    "생활인구는 등록인구의 약 4배(통계청 2024) — 정주인구 기준 분석은 체류 흐름을 크게 과소평가",
    "음수 = 방문 대비 소비 부진(소비전환 취약) — 13곳 상대 비교 지표",
    "기존 상권분석은 생활인구를 ‘규모’로만 활용 — 소비 전환 효율은 어디서도 측정하지 않았다",
  ], 0.75, 3.85, 11.9, { gap: 0.68, size: 13.5 });
}

/* ════════ 9. 04 지표 체계 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "04 · 이음(E-um)의 설계", "9개 지표 체계", "3장의 관찰을 그대로 산식으로 — ★ 생활인구 결합으로 새로 가능해진 핵심 지표");
  const th = { fill: { color: K }, color: "FFFFFF", bold: true, fontFace: FONT, fontSize: 11, align: "center", valign: "middle" };
  const c1 = { fontFace: FONT, fontSize: 10.5, bold: true, color: K, valign: "middle" };
  const c2 = { fontFace: FONT, fontSize: 10.5, color: MID, valign: "middle" };
  const rowsData = [
    ["★ MI", "Log(연간매출/연평균 생활인구) − 13곳 평균", "음수 = 소비전환 취약"],
    ["★ CPC", "연간매출 / 생활인구 / 12", "방문 1인당 월 소비 흡수력"],
    ["★ STI", "성수기(6~8월)/비수기(1~3월) 생활인구 − 1", "높음 = 관광·계절 의존"],
    ["LRR", "유입지가 경남인 매출 / 전체", "낮음 = 외부유입 소비 의존"],
    ["CDI", "업종별 매출 Shannon Entropy", "낮음 = 업종 집중"],
    ["NAR", "18~23시 매출 / 전체", "낮음 = 야간 체류 약함"],
    ["AGI", "60대+ 매출 비중", "높음 = 고령 소비 의존"],
    ["YR", "30대 이하 매출 비중", "낮음 = 청년 소비 이탈"],
    ["TREND", "월별 매출 회귀 기울기 / 평균", "음수 = 2024년 내 감소세"],
  ];
  s.addTable(
    [[{ text: "지표", options: th }, { text: "정의", options: th }, { text: "해석", options: th }]].concat(
      rowsData.map(r => [{ text: r[0], options: c1 }, { text: r[1], options: c2 }, { text: r[2], options: c2 }])
    ),
    { x: 0.45, y: 2.3, w: 12.44, colW: [1.7, 6.4, 4.34], rowH: 0.385, border: [{ pt: 0, color: "FFFFFF" }, { pt: 0, color: "FFFFFF" }, { pt: 0.5, color: LINE }, { pt: 0, color: "FFFFFF" }] }
  );
  s.addText("위험점수 = 0.40·MI′ + 0.25·CPC′ + 0.20·LRR′ + 0.15·TREND′   (13곳 min-max 정규화 · 낮을수록 위험인 지표는 부호 반전)", {
    x: 0.45, y: 6.42, w: 12.4, h: 0.4, fontFace: FONT, fontSize: 11.5, color: GRAY,
  });
}

/* ════════ 10. 05 유형화 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "05 · 분석 결과", "유형화 — 침체 4유형", "7개 지표 표준화 → K-means(k=4, random_state=42) — 탐색적 분류, 유형명은 사후 해석 라벨");
  const cards = [
    ["방문대비 소비부족형", "산청 · 의령 · 합천", "MI 전부 < −0.6 · CPC < 1.7만 원\n방문 대비 소비가 끊긴다"],
    ["외지방문 의존형", "하동 · 함양", "경남 외 소비자 의존(LRR↓) + 매출 감소세\n이중 위험"],
    ["혼합 경계형", "남해 · 창녕 · 고성 · 함안", "침체·안정 특성 혼재\n악화 시 전락 위험 — 감시 대상"],
    ["소비 안정형", "밀양 · 거창 · 사천 · 통영", "MI 양수 · CPC 상위\n광역 소비 연계 거점으로 활용"],
  ];
  cards.forEach(([t, r, d], i) => {
    const x = 0.45 + (i % 2) * 3.85, y = 2.35 + Math.floor(i / 2) * 2.2;
    s.addShape("rect", { x, y, w: 3.65, h: 0.52, fill: { color: i < 2 ? K : "666666" } });
    s.addText(t, { x, y, w: 3.65, h: 0.52, fontFace: FONT, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    s.addText([
      { text: r + "\n", options: { bold: true, fontSize: 12.5, color: K } },
      { text: d, options: { fontSize: 10.5, color: MID } },
    ], { x, y: y + 0.6, w: 3.65, h: 1.4, fontFace: FONT, lineSpacingMultiple: 1.2 });
  });
  s.addImage({ path: img(3), x: 8.5, y: 2.45, w: 4.35, h: 3.27 });
  s.addText("그림 3. PCA 평면 — 네 군집이 겹치지 않는다", { x: 8.5, y: 5.78, w: 4.35, h: 0.3, fontFace: FONT, fontSize: 10.5, color: GRAY, align: "center" });
}

/* ════════ 11. 05 핵심 지표 표 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "05 · 분석 결과", "13개 지역 핵심 지표", "위험점수 = 0.40·MI′ + 0.25·CPC′ + 0.20·LRR′ + 0.15·TREND′ — 음영 = 우선 개선 TOP 5");
  const th = { fill: { color: K }, color: "FFFFFF", bold: true, fontFace: FONT, fontSize: 10.5, align: "center", valign: "middle" };
  const data = [
    ["하동군", "−0.865", "13,240", "−0.132", "0.729", "−0.004", "외지방문 의존형", "0.865", true],
    ["함양군", "−0.151", "27,037", "0.602", "0.655", "−0.014", "외지방문 의존형", "0.778", true],
    ["합천군", "−1.016", "11,380", "0.065", "0.767", "0.016", "방문대비 소비부족형", "0.775", true],
    ["남해군", "−0.610", "17,074", "0.154", "0.743", "0.013", "혼합 경계형", "0.709", true],
    ["의령군", "−0.963", "12,001", "0.022", "0.870", "0.015", "방문대비 소비부족형", "0.702", true],
    ["산청군", "−0.642", "16,536", "0.718", "0.930", "0.009", "방문대비 소비부족형", "0.613", false],
    ["창녕군", "0.016", "31,927", "−0.088", "0.772", "0.004", "혼합 경계형", "0.561", false],
    ["고성군", "0.168", "37,170", "0.048", "0.928", "−0.002", "혼합 경계형", "0.439", false],
    ["밀양시", "0.529", "53,357", "0.182", "0.807", "0.006", "소비 안정형", "0.358", false],
    ["함안군", "0.822", "71,516", "0.069", "0.787", "0.005", "혼합 경계형", "0.255", false],
    ["거창군", "0.727", "65,036", "0.226", "0.896", "0.004", "소비 안정형", "0.227", false],
    ["사천시", "0.969", "82,844", "0.083", "0.901", "0.009", "소비 안정형", "0.093", false],
    ["통영시", "1.015", "86,764", "0.101", "0.955", "0.003", "소비 안정형", "0.065", false],
  ];
  const headRow = [["지역", 1.5], ["MI", 1.25], ["CPC(원/월)", 1.55], ["STI", 1.2], ["LRR", 1.2], ["TREND", 1.3], ["침체유형", 2.94], ["위험점수", 1.5]];
  s.addTable(
    [headRow.map(h => ({ text: h[0], options: th }))].concat(
      data.map(r => {
        const top5 = r[8];
        const base = { fontFace: FONT, fontSize: 9.8, valign: "middle", align: "center", fill: { color: top5 ? "EDEDED" : "FFFFFF" } };
        return [
          { text: r[0], options: { ...base, bold: true, color: K } },
          { text: r[1], options: { ...base, color: MID } },
          { text: r[2], options: { ...base, color: MID } },
          { text: r[3], options: { ...base, color: MID } },
          { text: r[4], options: { ...base, color: MID } },
          { text: r[5], options: { ...base, color: MID } },
          { text: r[6], options: { ...base, color: MID } },
          { text: r[7], options: { ...base, bold: top5, color: K } },
        ];
      })
    ),
    { x: 0.45, y: 2.28, w: 12.44, colW: headRow.map(h => h[1]), rowH: 0.3, border: [{ pt: 0, color: "FFFFFF" }, { pt: 0, color: "FFFFFF" }, { pt: 0.5, color: LINE }, { pt: 0, color: "FFFFFF" }] },
  );
  s.addText("우선 개선 대상 TOP 5: 하동 · 함양 · 합천 · 남해 · 의령 — 가중치 ±0.05 무작위 교란(N=3,000)에도 집합 100% 동일", {
    x: 0.45, y: 6.68, w: 12.4, h: 0.32, fontFace: FONT, fontSize: 11, color: GRAY,
  });
}

/* ════════ 12. 05 공간 분포 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "05 · 분석 결과", "공간 분포 — 서부 내륙의 침체 벨트", "침체는 단발 사례가 아니라 공간적으로 인접한 구조다 — 광역 단위 개선의 근거");
  rows(s, [
    "하동·함양·산청·합천·의령이 서부 내륙에 띠처럼 연속 분포",
    "해안·도심 접근성이 좋은 통영·사천·밀양은 소비 안정형으로 분리",
    "위험점수 지도: 하동·함양이 가장 진하다 — 최우선 개선 대상",
  ], 0.45, 2.6, 4.7, { gap: 0.95, size: 13 });
  s.addImage({ path: img(5), x: 5.55, y: 2.3, w: 3.55, h: 3.98 });
  s.addImage({ path: img(6), x: 9.35, y: 2.3, w: 3.55, h: 3.46 });
  s.addText("그림 5. 침체유형 지도", { x: 5.55, y: 6.32, w: 3.55, h: 0.3, fontFace: FONT, fontSize: 10.5, color: GRAY, align: "center" });
  s.addText("그림 6. 위험점수 지도 (라벨 = 순위·점수)", { x: 9.35, y: 6.32, w: 3.55, h: 0.3, fontFace: FONT, fontSize: 10.5, color: GRAY, align: "center" });
}

/* ════════ 13. 05 위험점수 구성 요인 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "05 · 분석 결과", "위험점수 구성 요인 분석 (이음-Detect)", "“어디가 위험한가”에서 “무엇 때문에 위험한가”로 — 원인을 두 층위로 분해");
  s.addText([
    { text: "층위 ① 위험점수 정확 분해 (재현 오차 0)\n", options: { bold: true, fontSize: 14, color: K } },
    { text: "위험 상위 8개 시군 전부에서 MI(소비전환 부족)가 1위 요인 — 기여율 30~56%\n\n", options: { fontSize: 12, color: MID } },
    { text: "층위 ② MI의 구조적 동인 (RandomForest + SHAP)\n", options: { bold: true, fontSize: 14, color: K } },
    { text: "전역: TREND(감소세) > CDI(업종 집중) > NAR(야간 약함)\n시군별 1순위 — 합천·남해·의령: TREND / 하동: NAR / 함양·산청: CDI\n\n", options: { fontSize: 12, color: MID } },
    { text: "→ 같은 유형 안에서도 개선 우선순위가 달라야 한다", options: { bold: true, fontSize: 13, color: K } },
  ], { x: 0.45, y: 2.4, w: 6.3, h: 3.9, fontFace: FONT, lineSpacingMultiple: 1.25 });
  s.addImage({ path: img(7), x: 7.15, y: 2.3, w: 5.75, h: 4.16 });
  s.addText("그림 7. 위험점수 요인 분해 — 진빨강 = MI 기여", { x: 7.15, y: 6.5, w: 5.75, h: 0.3, fontFace: FONT, fontSize: 10.5, color: GRAY, align: "center" });
}

/* ════════ 14. 05 시뮬레이션 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "05 · 분석 결과", "개선 효과 시뮬레이션 (이음-Simulate)", "“개선을 적용하면 정말 나아지는가” — 반사실(counterfactual) 입력으로 지표 체계 재계산");
  s.addText([
    { text: "방문 1인당 월 +1,000원 — 커피 한 잔 값 미만\n", options: { bold: true, fontSize: 14.5, color: K } },
    { text: "개선 대상 5곳(소비부족형 3 + 외지의존형 2)의 객단가 개선 가정\n\n", options: { fontSize: 12, color: MID } },
    { text: "개선 대상만 위험점수 하락, 미적용 8곳은 Δ=0\n", options: { bold: true, fontSize: 13.5, color: K } },
    { text: "합천 0.775→0.756 · 의령 0.702→0.683 · 하동 0.865→0.848\n효과가 대상 지역에 온전히 귀속됨을 확인\n\n", options: { fontSize: 12, color: MID } },
    { text: "강건성: 가중치 ±0.05 교란 N=3,000 → TOP 5 집합 100% 유지\n", options: { bold: true, fontSize: 13.5, color: K } },
    { text: "하동은 모든 경우 1위 — 우선순위는 가중치 선택에 흔들리지 않는다", options: { fontSize: 12, color: MID } },
  ], { x: 0.45, y: 2.35, w: 6.3, h: 4.1, fontFace: FONT, lineSpacingMultiple: 1.25 });
  s.addImage({ path: img(9), x: 7.15, y: 2.3, w: 5.75, h: 4.17 });
  s.addText("그림 9. 개선 전·후 위험점수 — 개선 대상(진빨강)만 하락", { x: 7.15, y: 6.5, w: 5.75, h: 0.3, fontFace: FONT, fontSize: 10.5, color: GRAY, align: "center" });
}

/* ════════ 15. 05 우연이 아니다 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "05 · 분석 결과", "방문대비 소비부족형은 우연이 아니다", "세 근거가 같은 방향을 가리킨다 — 유형의 실재성이 6장 정책 설계의 출발점");
  const steps = [
    ["01", "C8C8C8", "333333", "같은 증상이 반복된다", "서로 다른 생활권인 산청·의령·합천이 MI < −0.6 · CPC < 1.7만 원 — 동일한 수치 조합. 세 곳이 서로를 교차 입증하는 반복 패턴"],
    ["02", "777777", "FFFFFF", "알고리즘이 묶었다", "K-means는 가설을 모른 채 7개 지표만으로 군집화 — 정확히 이 세 곳을 한 유형으로 분류. PCA 평면에서 네 군집 분리(그림 3)"],
    ["03", "111111", "FFFFFF", "공간적으로 연속된다", "우연이라면 산발적으로 흩어져야 한다 — 세 지역은 서부 내륙에 몰려 있고 하동·함양까지 띠처럼 이어진 침체 벨트(그림 5)"],
  ];
  steps.forEach(([n, fill, txt, t, d], i) => {
    const x = 0.55 + i * 4.25;
    s.addShape("chevron", { x, y: 2.6, w: 4.0, h: 0.62, fill: { color: fill }, line: { type: "none" } });
    s.addText(n + "  " + t, { x: x + 0.25, y: 2.6, w: 3.6, h: 0.62, fontFace: FONT, fontSize: 13.5, bold: true, color: txt, valign: "middle" });
    s.addText(d, { x: x + 0.15, y: 3.45, w: 3.75, h: 2.2, fontFace: FONT, fontSize: 11.5, color: MID, lineSpacingMultiple: 1.3 });
    s.addShape("rect", { x: x + 0.15, y: 3.38, w: 0.011, h: 2.3, fill: { color: LINE } });
  });
  s.addText("단, 표본 13개의 탐색적 유형화라는 한계(8장) 안에서의 판단 — 그럼에도 세 근거가 모두 같은 방향을 가리킨다", {
    x: 0.55, y: 6.25, w: 12.3, h: 0.4, fontFace: FONT, fontSize: 11.5, color: GRAY,
  });
}

/* ════════ 16. 06 유형별 정책 방안 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "06 · 유형별 정책 방안", "“넓게 분석, 좁게 해결”", "13개 분석은 유형의 실재성을 입증하는 근거 — 개선은 유형군 단위로 심화 (단일 사례 편향 회피)");
  const cols = [
    ["정주형 소비부족", "합천 · 의령", "생활밀착 업종 객단가 제고\n지역화폐·페이백으로 소비 회수", "합천 +30.6억 · 의령 +17.5억"],
    ["관광 통과형", "산청", "관광 동선 위 결제 가능 로컬 상점\n야간·숙박 연계 — 1일을 1박으로", "산청 +30.2억"],
    ["외지방문 의존형", "하동 · 함양", "외부 방문객을 묶는 체류·연계 상품\n계절 편중 완화(비수기 보완)", "하동 +30.5억 · 함양 +22.2억"],
    ["소비 연계 거점", "거창 · 통영", "안정 지역을 인접 침체지역과 잇는\n광역 소비 연계 거점으로", "거점·완충 역할"],
  ];
  cols.forEach(([t, r, d, e], i) => {
    const x = 0.45 + i * 3.18;
    s.addShape("rect", { x, y: 2.4, w: 2.98, h: 0.55, fill: { color: i === 3 ? "666666" : K } });
    s.addText(t, { x, y: 2.4, w: 2.98, h: 0.55, fontFace: FONT, fontSize: 12.5, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    s.addText(r, { x, y: 3.05, w: 2.98, h: 0.4, fontFace: FONT, fontSize: 13, bold: true, color: K, align: "center" });
    s.addText(d, { x: x + 0.08, y: 3.55, w: 2.82, h: 1.5, fontFace: FONT, fontSize: 11, color: MID, align: "center", lineSpacingMultiple: 1.25 });
    s.addShape("rect", { x: x + 0.3, y: 5.22, w: 2.38, h: 0.011, fill: { color: LINE } });
    s.addText(e, { x: x + 0.05, y: 5.32, w: 2.88, h: 0.65, fontFace: FONT, fontSize: 10.5, bold: true, color: K, align: "center" });
  });
  s.addText("기대효과는 ‘방문 1인당 월 +1,000원’ 가정의 탐색적 추정 (산출 근거: 보고서 부록 A)", {
    x: 0.45, y: 6.35, w: 12.4, h: 0.35, fontFace: FONT, fontSize: 11, color: GRAY,
  });
}

/* ════════ 17. 06 실현 가능성 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "06 · 유형별 정책 방안", "실현 가능성 — 새 재원도, 새 제도도 필요 없다", "이미 편성된 기금 · 법제화된 지표 · 검증된 성과 위에 서 있는 실행안");
  const items = [
    ["재원", "지방소멸대응기금과 정확히 맞물린다", "매년 1조 원 × 10년, 기초지원계정 95%를 인구감소지역에 배분 — 분석 대상 11곳 전부 해당. 2026년 운용방향이 ‘사람이 들어오고 머무는 사업’ 우선으로 전환 = 본 연구의 개선 방향과 일치"],
    ["제도", "생활인구는 법제화된 공식 통계", "「인구감소지역 지원 특별법」(2022)이 생활인구를 공식 지표화 — MI·CPC의 분모는 행정이 매년 갱신·검증, 별도 데이터 구축 없이 개선 효과 추적 가능"],
    ["검증", "같은 방안이 이미 성과를 냈다 — 전남 강진", "‘반값여행’(소비액 50% 지역화폐 환급): 2025년 1~5월 초 4만 724팀, 군내 1,453개 업소에서 58.7억 원 소비 — 체류형 관광도시 대상 수상"],
  ];
  items.forEach(([tag, t, d], i) => {
    const y = 2.45 + i * 1.42;
    s.addShape("rect", { x: 0.45, y, w: 1.05, h: 0.5, fill: { color: K } });
    s.addText(tag, { x: 0.45, y, w: 1.05, h: 0.5, fontFace: FONT, fontSize: 12.5, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    s.addText(t, { x: 1.75, y, w: 11.1, h: 0.5, fontFace: FONT, fontSize: 14.5, bold: true, color: K, valign: "middle" });
    s.addText(d, { x: 1.75, y: y + 0.52, w: 11.1, h: 0.75, fontFace: FONT, fontSize: 11.5, color: MID, lineSpacingMultiple: 1.2 });
    if (i < 2) s.addShape("rect", { x: 0.45, y: y + 1.3, w: 12.4, h: 0.011, fill: { color: LINE } });
  });
}

/* ════════ 18. 07 결론 및 기대효과 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "07 · 결론 및 기대효과", "침체의 축은 인구가 아니라 ‘소비 전환’이다", null);
  const stats = [
    ["7.6배", "인구감소지역 내부의 양극화", "합천 11,380원 vs 통영 86,764원\n“일률적 침체” 통념을 데이터가 반박"],
    ["TOP 5", "하동 · 함양 · 합천 · 남해 · 의령", "위험점수 기준 우선 개선 대상\n유형별로 개선 방향이 다르다"],
    ["+78억/년", "방문대비 소비부족형 3곳", "1인당 월 +1,000원만으로 (탐색적 추정)\n강진 실측 58.7억이 외부 준거"],
  ];
  stats.forEach(([n, t, d], i) => {
    const x = 0.55 + i * 4.25;
    s.addText(n, { x, y: 2.35, w: 4.0, h: 1.0, fontFace: FONT, fontSize: 40, bold: true, color: K, align: "center" });
    s.addText(t, { x, y: 3.45, w: 4.0, h: 0.4, fontFace: FONT, fontSize: 13.5, bold: true, color: K, align: "center" });
    s.addText(d, { x: x + 0.1, y: 3.95, w: 3.8, h: 0.95, fontFace: FONT, fontSize: 11, color: MID, align: "center", lineSpacingMultiple: 1.25 });
    s.addShape("rect", { x: x + 0.55, y: 3.38, w: 2.9, h: 0.011, fill: { color: LINE } });
  });
  s.addShape("rect", { x: 2.37, y: 5.45, w: 8.6, h: 0.85, fill: { color: K } });
  s.addText("E-um은 “어디가 침체됐는가”를 넘어 “왜, 그래서 무엇을”까지\n데이터로 답하는 재현 가능한 분석 프레임이다", {
    x: 2.37, y: 5.45, w: 8.6, h: 0.85, fontFace: FONT, fontSize: 13.5, bold: true, color: "FFFFFF", align: "center", valign: "middle", lineSpacingMultiple: 1.2,
  });
}

/* ════════ 19. 08 한계 및 향후 과제 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  head(s, "08 · 한계 및 향후 과제", "정직한 경계선", "탐색적 분석의 한계를 명시한다 — 한계가 곧 다음 과제다");
  rows(s, [
    "표본 13개 — K-means는 탐색적 유형화이며 확정 분류가 아니다",
    "MI 외부 타당성 검증 미완 — 시군 단위 폐업률·다년 매출 패널 교차 검증이 핵심 후속 과제",
    "생활인구는 월별 방문 흐름의 합계 — MI·CPC는 상대 비교 지표로 해석",
    "기대효과는 가정 기반 탐색적 추정 (객단가 개선이 방문을 위축시키지 않는다는 전제)",
    "향후: 시군 전입·전출 마이크로데이터 확보 시 외부의존 구조 직접 검증, 인터랙티브 지도 대시보드",
  ], 0.6, 2.5, 12.1, { gap: 0.78, size: 13.5 });
}

/* ════════ 20. 클로징 ════════ */
{
  const s = pptx.addSlide(); deco(s);
  s.addText("감사합니다", { x: 0.7, y: 2.7, w: 11.93, h: 1.1, fontFace: FONT, fontSize: 44, bold: true, color: K, align: "center" });
  s.addText("생활인구와 지역 소비를 잇다 — 이음(E-um)", {
    x: 0.7, y: 4.0, w: 11.93, h: 0.5, fontFace: FONT, fontSize: 15, color: MID, align: "center",
  });
  s.addText([
    { text: "팀 E-um", options: { bold: true, color: K } },
    { text: "   김재민 · 강원준 · 오수환", options: { color: MID } },
  ], { x: 0.7, y: 4.75, w: 11.93, h: 0.45, fontFace: FONT, fontSize: 13, align: "center" });
}

pptx.writeFile({ fileName: "C:/Users/PC/Desktop/빅데이터/깃허브/eum_package/이음_발표자료_v3.pptx" })
  .then(f => console.log("OK", f));
