import os
import re
import json
import base64
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

import pandas as pd
import streamlit as st
try:
    import tomllib
except Exception:
    tomllib = None
from jinja2 import Template
from openai import OpenAI

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False


# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(page_title="운동계획서 생성기", layout="wide")

APP_UI_CSS = """
<style>
:root {
  --ui-bg:#f5f8fc;
  --ui-bg-soft:#eef4fa;
  --ui-surface:#ffffff;
  --ui-surface-soft:#f8fbff;
  --ui-line:#d9e5f0;
  --ui-line-strong:#bfd0e0;
  --ui-navy:#15344f;
  --ui-navy-strong:#102a43;
  --ui-blue:#2f5d88;
  --ui-sky:#eaf2fb;
  --ui-gold:#c9a86a;
  --ui-text:#15344f;
  --ui-muted:#5f7286;
  --ui-shadow:0 10px 26px rgba(16,42,67,.08);
}

html, body, [class*="css"] {
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
section.main {
  background:linear-gradient(180deg, var(--ui-bg) 0%, var(--ui-bg-soft) 100%) !important;
  color:var(--ui-text) !important;
}

.block-container {
  max-width:1240px;
  padding-top:2rem;
  padding-bottom:2.75rem;
}

[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#173654 0%, #10273d 100%) !important;
  border-right:1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * {
  color:#f7fbff !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
[data-testid="stSidebar"] [data-baseweb="radio"] *,
[data-testid="stSidebar"] [data-baseweb="checkbox"] *,
[data-testid="stSidebar"] [role="radiogroup"] *,
[data-testid="stSidebar"] .st-emotion-cache-1c7y2kd,
[data-testid="stSidebar"] .st-emotion-cache-ue6h4q {
  color:#f7fbff !important;
  opacity:1 !important;
}
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stTextArea label,
[data-testid="stSidebar"] .stFileUploader label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stCaption {
  color:#eff6ff !important;
  font-weight:700;
  opacity:1 !important;
}
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] input {
  background:rgba(255,255,255,.08) !important;
  border:1px solid rgba(255,255,255,.15) !important;
  color:#f8fbff !important;
  border-radius:14px !important;
}
[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {
  color:rgba(247,251,255,.78) !important;
  opacity:1 !important;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
  background:rgba(255,255,255,.12) !important;
  color:#ffffff !important;
  border:1px solid rgba(255,255,255,.14) !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-baseweb="radio"] label,
[data-testid="stSidebar"] [data-baseweb="checkbox"] label {
  color:#f8fbff !important;
  opacity:1 !important;
}
[data-testid="stSidebar"] hr {
  border:none !important;
  border-top:1px solid rgba(255,255,255,.18) !important;
}

/* 메인 영역 가독성 고정 */
[data-testid="stAppViewContainer"] > .main .block-container,
[data-testid="stAppViewContainer"] > .main .block-container p,
[data-testid="stAppViewContainer"] > .main .block-container li,
[data-testid="stAppViewContainer"] > .main .block-container span,
[data-testid="stAppViewContainer"] > .main .block-container label,
[data-testid="stAppViewContainer"] > .main .block-container div,
[data-testid="stAppViewContainer"] > .main .block-container small,
[data-testid="stAppViewContainer"] > .main .block-container strong {
  color:var(--ui-text);
}

[data-testid="stAppViewContainer"] > .main .block-container h1,
[data-testid="stAppViewContainer"] > .main .block-container h2,
[data-testid="stAppViewContainer"] > .main .block-container h3,
[data-testid="stAppViewContainer"] > .main .block-container h4,
[data-testid="stAppViewContainer"] > .main .block-container h5,
[data-testid="stAppViewContainer"] > .main .block-container h6,
[data-testid="stAppViewContainer"] > .main .block-container .stMarkdown,
[data-testid="stAppViewContainer"] > .main .block-container .stCaption,
[data-testid="stAppViewContainer"] > .main .block-container .st-emotion-cache-10trblm,
[data-testid="stAppViewContainer"] > .main .block-container .st-emotion-cache-16idsys,
[data-testid="stAppViewContainer"] > .main .block-container .st-emotion-cache-1kyxreq {
  color:var(--ui-navy-strong) !important;
}

/* Hero는 예외적으로 흰색 유지 */
.premium-hero,
.premium-hero * {
  color:#ffffff !important;
}

div[data-testid="stVerticalBlock"] div:has(> .premium-hero) {
  margin-bottom:1rem;
}
.premium-hero {
  position:relative;
  overflow:hidden;
  padding:30px 32px;
  border-radius:24px;
  background:
    radial-gradient(circle at right top, rgba(255,255,255,.16), transparent 28%),
    linear-gradient(135deg,#14304a 0%, #1f4e78 58%, #6f8fb3 100%);
  box-shadow:0 18px 42px rgba(21,52,79,.16);
  margin-bottom:1rem;
}
.premium-hero::after {
  content:"";
  position:absolute;
  right:-40px;
  top:-40px;
  width:180px;
  height:180px;
  border-radius:50%;
  background:rgba(255,255,255,.07);
}
.premium-kicker {
  display:inline-block;
  padding:6px 12px;
  border:1px solid rgba(255,255,255,.24);
  border-radius:999px;
  font-size:12px;
  font-weight:800;
  letter-spacing:.04em;
  margin-bottom:14px;
  background:rgba(255,255,255,.08);
}
.premium-hero h1 {
  margin:0 0 10px 0;
  font-size:34px;
  line-height:1.2;
  font-weight:900;
}
.premium-hero p {
  margin:0;
  max-width:860px;
  font-size:15px;
  line-height:1.8;
  color:rgba(255,255,255,.92) !important;
}
.premium-badges {
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  margin-top:16px;
}
.premium-badge {
  display:inline-flex;
  align-items:center;
  padding:8px 12px;
  border-radius:999px;
  background:rgba(255,255,255,.10);
  border:1px solid rgba(255,255,255,.14);
  font-size:12px;
  font-weight:700;
}

.stExpander {
  border:1px solid var(--ui-line) !important;
  border-radius:20px !important;
  background:rgba(255,255,255,.92) !important;
  box-shadow:var(--ui-shadow);
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] .streamlit-expanderHeader {
  color:var(--ui-navy-strong) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap:10px;
  margin-bottom:14px;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  border-radius:999px;
  padding:10px 16px;
  background:#edf3fa;
  color:var(--ui-navy-strong) !important;
  font-weight:800;
  border:1px solid #dbe7f2;
}
[data-testid="stTabs"] [aria-selected="true"] {
  background:linear-gradient(135deg,#163652,#2b5f90) !important;
  color:#ffffff !important;
  border-color:transparent !important;
}

.stButton > button,
.stDownloadButton > button {
  border-radius:16px !important;
  border:1px solid #d5e1ec !important;
  min-height:48px;
  font-weight:800 !important;
  letter-spacing:.01em;
  box-shadow:0 8px 18px rgba(17,24,39,.05);
}
.stButton > button {
  background:#ffffff !important;
  color:var(--ui-navy-strong) !important;
}
.stButton > button[kind="primary"] {
  background:linear-gradient(135deg,#14314b,#245886) !important;
  color:#ffffff !important;
  border:none !important;
}
.stDownloadButton > button {
  background:#ffffff !important;
  color:var(--ui-navy-strong) !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
  border-color:#bfd0e0 !important;
  box-shadow:0 10px 22px rgba(16,42,67,.09);
}

.stTextInput input,
.stNumberInput input,
textarea,
[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
  border-radius:14px !important;
  border:1px solid var(--ui-line) !important;
  background:#ffffff !important;
  color:var(--ui-navy-strong) !important;
}

.stTextInput input::placeholder,
textarea::placeholder,
input::placeholder {
  color:#7d8ea0 !important;
  opacity:1 !important;
}

.stTextInput label,
.stNumberInput label,
.stTextArea label,
.stSelectbox label,
.stMultiSelect label,
.stFileUploader label,
.stCheckbox label,
.stRadio label,
.stMarkdown,
.stCaption {
  color:var(--ui-navy-strong) !important;
}

.stMultiSelect [data-baseweb="tag"] {
  border-radius:999px !important;
  background:#edf4fb !important;
  color:var(--ui-navy-strong) !important;
  border:1px solid #d8e4ef !important;
}

.stAlert {
  border-radius:16px !important;
  border:1px solid #d9e5ef !important;
}

[data-testid="stInfo"],
[data-testid="stSuccess"],
[data-testid="stWarning"],
[data-testid="stError"] {
  color:var(--ui-navy-strong) !important;
}

[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] {
  background:linear-gradient(180deg,#ffffff 0%, #f8fbff 100%) !important;
  border:1px dashed #c7d7e6 !important;
  border-radius:18px !important;
}

.loading-card {
  position:relative;
  overflow:hidden;
  margin:14px 0 18px;
  padding:22px 24px;
  border-radius:22px;
  border:1px solid #d9e5f0;
  background:linear-gradient(135deg,#ffffff 0%, #f6faff 60%, #eef4fb 100%);
  box-shadow:0 14px 32px rgba(16,42,67,.08);
}
.loading-card::after {
  content:"";
  position:absolute;
  inset:0;
  background:linear-gradient(110deg, transparent 0%, rgba(255,255,255,.62) 40%, transparent 80%);
  transform:translateX(-100%);
  animation:loadingShine 2.1s ease-in-out infinite;
}
.loading-kicker {
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:7px 12px;
  border-radius:999px;
  background:#edf4fb;
  color:var(--ui-navy-strong) !important;
  font-size:12px;
  font-weight:800;
  margin-bottom:10px;
}
.loading-title {
  font-size:26px;
  font-weight:900;
  color:var(--ui-navy-strong) !important;
  margin-bottom:8px;
  letter-spacing:-.02em;
}
.loading-desc {
  font-size:14px;
  line-height:1.8;
  color:#44586d !important;
  margin-bottom:16px;
}
.loading-steps {
  display:grid;
  grid-template-columns:repeat(3, 1fr);
  gap:10px;
}
.loading-step {
  position:relative;
  z-index:1;
  border:1px solid #d9e5f0;
  background:#ffffffd9;
  border-radius:16px;
  padding:12px 12px 11px;
}
.loading-step strong {
  display:block;
  font-size:12px;
  color:var(--ui-navy-strong) !important;
  margin-bottom:4px;
}
.loading-step span {
  font-size:12px;
  line-height:1.6;
  color:#597086 !important;
}
@keyframes loadingShine {
  0% { transform:translateX(-100%); }
  100% { transform:translateX(100%); }
}

[data-testid="stAppViewContainer"] .stSlider p,
[data-testid="stAppViewContainer"] .stRadio p,
[data-testid="stAppViewContainer"] .stSelectSlider p {
  color:var(--ui-navy-strong) !important;
}

hr {
  border:none;
  border-top:1px solid var(--ui-line);
  margin:1rem 0;
}

/* ===== 최종 가독성 고정: 사이드바 텍스트/아이콘 ===== */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] legend,
[data-testid="stSidebar"] .stRadio > label,
[data-testid="stSidebar"] .stCheckbox > label,
[data-testid="stSidebar"] .stSelectbox > label,
[data-testid="stSidebar"] .stMultiSelect > label,
[data-testid="stSidebar"] .stTextInput > label,
[data-testid="stSidebar"] .stNumberInput > label,
[data-testid="stSidebar"] .stTextArea > label,
[data-testid="stSidebar"] .stFileUploader > label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] .st-emotion-cache-10trblm,
[data-testid="stSidebar"] .st-emotion-cache-16idsys {
  color:#f7fbff !important;
  opacity:1 !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"] label,
[data-testid="stSidebar"] [data-baseweb="radio"] label *,
[data-testid="stSidebar"] [role="radiogroup"] label,
[data-testid="stSidebar"] [role="radiogroup"] label *,
[data-testid="stSidebar"] [data-baseweb="checkbox"] label,
[data-testid="stSidebar"] [data-baseweb="checkbox"] label * {
  color:#f7fbff !important;
  opacity:1 !important;
}
[data-testid="stSidebar"] svg,
[data-testid="stSidebar"] svg path,
[data-testid="stSidebar"] svg circle,
[data-testid="stSidebar"] svg rect,
[data-testid="stSidebar"] svg line,
[data-testid="stSidebar"] svg polyline {
  fill:currentColor !important;
  stroke:currentColor !important;
  color:#f7fbff !important;
  opacity:1 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] [aria-hidden="true"],
[data-testid="stSidebar"] .stMultiSelect [aria-hidden="true"],
[data-testid="stSidebar"] button[title="Clear all"],
[data-testid="stSidebar"] button[title="Remove"] {
  color:#f7fbff !important;
  opacity:1 !important;
}

/* ===== 메인 입력 UI 아이콘 가독성 ===== */
.stSelectbox svg,
.stMultiSelect svg,
.stTextInput svg,
.stNumberInput svg,
[data-baseweb="select"] svg,
[data-baseweb="tag"] svg,
button[title="Clear all"] svg,
button[title="Remove"] svg {
  color:var(--ui-navy-strong) !important;
  fill:currentColor !important;
  stroke:currentColor !important;
  opacity:1 !important;
}
.stMultiSelect [data-baseweb="tag"] span,
.stMultiSelect [data-baseweb="tag"] button,
.stMultiSelect [data-baseweb="tag"] [aria-hidden="true"] {
  color:var(--ui-navy-strong) !important;
  opacity:1 !important;
}
[data-baseweb="select"] input,
[data-baseweb="select"] span,
[data-baseweb="select"] div {
  color:inherit;
}
</style>
"""

st.markdown(APP_UI_CSS, unsafe_allow_html=True)

APP_TITLE = "운동계획서 생성기"
DEFAULT_TRAINER_NAME = "김기연"
DEFAULT_GYM_NAME = "헬스보이짐 수지점"
TOP_GUIDE_TEXT = (
    "회원님의 현재 상태와 목표를 기준으로 왜 이 기간과 횟수가 필요한지 이해하고 시작하면 등록 만족도와 운동 지속률이 높아집니다. "
    "좋은 세일즈는 과장이 아니라 설득력 있는 근거 제시입니다."
)
ABILITY_OPTIONS = ["하", "중하", "중", "중상", "상"]
SESSION_OPTIONS = ["10회(1개월)", "20회(2개월)", "30회(3개월)", "50회(6개월)", "100회(12개월)"]
TEMPLATE_LABELS = {"자동 추천": "AUTO", "A형": "A", "B형": "B", "C형": "C"}
STRENGTH_OPTIONS = [
    "비율이 좋음",
    "피드백 습득력이 좋음",
    "운동 의지가 강함",
    "출석/약속 이행이 좋음",
    "체형 개선 욕구가 뚜렷함",
    "다이어트 동기가 분명함",
    "근육 반응이 좋은 편",
    "자극 이해가 빠름",
    "기본 체력이 있는 편",
    "통증 표현이 명확함",
    "자기관리 의지가 있음",
    "식단 조절 의사가 있음",
    "생활 루틴이 비교적 안정적",
    "회복력이 좋은 편",
    "개인운동 전환 가능성이 높음",
]
WEAKNESS_OPTIONS = [
    "거북목 경향",
    "라운드숄더 경향",
    "골반 정렬 이슈",
    "코어 안정성 부족",
    "고관절 가동성 부족",
    "햄스트링 유연성 부족",
    "발목 가동성 부족",
    "근지구력 부족",
    "하체 근력 부족",
    "상체 안정성 부족",
    "체지방 관리 필요",
    "식습관 불규칙",
    "수면/회복 부족",
    "운동 지속성 부족",
    "통증/불편감 호소",
]

# 샘플 10개 HWP 기준으로 정리한 레이아웃 메모
HWP_LAYOUT_ANALYSIS = {
    "공통": [
        "상단 남색 타이틀 바 + 중앙 정렬 트레이너명 + 빨간 안내 문구 + 회원명",
        "근력/지구력/가동성/유연성 4칸 요약 표",
        "운동 목표 → 트레이닝 장점 → 현재 바디 상태 → 앞으로의 운동 방향성 흐름",
        "하단에는 단계형 표 또는 상세 관리 표가 반복적으로 등장",
    ],
    "A": {
        "name": "체형교정/바디분석형",
        "samples": ["정대훈", "박지호", "곽정민", "최지운"],
        "features": [
            "체형 분석 문단 비중이 큼",
            "통증, 정렬, 가동성, 자세 인지 내용이 핵심",
            "설명용 참고 이미지 또는 체형 참고 슬롯이 자연스럽게 어울림",
        ],
    },
    "B": {
        "name": "다이어트/스토리텔링형",
        "samples": ["황윤아", "고민정", "최다연", "정은지"],
        "features": [
            "체지방/근육량 목표가 문서 초반에 명확히 제시됨",
            "실패 원인, 식습관, 생활습관 개선 서사가 들어감",
            "추가 식단 가이드 표나 전후 사례 이미지 슬롯이 잘 맞음",
        ],
    },
    "C": {
        "name": "간결 코칭/압축형",
        "samples": ["김태양", "김은정"],
        "features": [
            "간단한 구조 또는 빈 양식에 가까움",
            "상담용 기본 틀, 빠른 작성, 수기 보완에 적합",
            "핵심 표 중심으로 요약된 문서를 만들기 좋음",
        ],
    },
}

ROW_LABELS = [
    "이 단계의 핵심 목표",
    "우선 관리 포인트",
    "수업 진행 방식",
    "회원이 체감할 변화",
    "생활습관/식단 전략",
    "PT 운영 방식",
    "혼자 하는 루틴",
    "우선 보완 포인트",
    "변화 가능성이 높은 이유",
    "트레이너 중점 코칭 포인트",
]


# ============================================================
# 유틸
# ============================================================
def safe_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", "", safe_text(value))


def split_lines(value: str) -> List[str]:
    return [line.strip() for line in safe_text(value).splitlines() if line.strip()]


def uploaded_file_to_data_uri(uploaded_file) -> Optional[str]:
    if uploaded_file is None:
        return None
    try:
        raw = uploaded_file.getvalue()
        if not raw:
            return None
        mime = getattr(uploaded_file, "type", None) or "image/png"
        b64 = base64.b64encode(raw).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    except Exception:
        return None


def uploaded_files_to_data_uris(uploaded_files, max_files: int = 4) -> List[str]:
    if not uploaded_files:
        return []
    items = uploaded_files[:max_files] if isinstance(uploaded_files, list) else [uploaded_files]
    output: List[str] = []
    for item in items:
        uri = uploaded_file_to_data_uri(item)
        if uri:
            output.append(uri)
    return output


def load_local_openai_api_key() -> Optional[str]:
    candidates = [
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path(__file__).resolve().parent / ".streamlit" / "secrets.toml",
    ]
    for candidate in candidates:
        try:
            if not candidate.exists():
                continue
            raw = candidate.read_text(encoding="utf-8")
            if tomllib is not None:
                data = tomllib.loads(raw)
                api_key = safe_text(data.get("OPENAI_API_KEY"))
                if api_key:
                    return api_key
            match = re.search(r"^\s*OPENAI_API_KEY\s*=\s*[\"'](.+?)[\"']\s*$", raw, re.M)
            if match:
                return safe_text(match.group(1))
        except Exception:
            continue
    return None


def get_openai_client(api_key_override: Optional[str] = None) -> Optional[OpenAI]:
    api_key = safe_text(api_key_override)
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = load_local_openai_api_key()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def extract_session_count(session_label: str) -> int:
    m = re.search(r"(\d+)회", safe_text(session_label))
    return int(m.group(1)) if m else 30


def extract_month_count(session_label: str) -> int:
    m = re.search(r"\((\d+)개월\)", safe_text(session_label))
    return int(m.group(1)) if m else 3


def phase_ranges(session_label: str) -> List[str]:
    months = extract_month_count(session_label)
    if months <= 1:
        return ["1주~2주", "3주~4주", "5주 이후"]
    if months == 2:
        return ["1~2주", "3~5주", "6~8주"]
    if months == 3:
        return ["1개월", "2개월", "3개월"]
    if months == 6:
        return ["1~2개월", "3~4개월", "5~6개월"]
    return ["1~3개월", "4~8개월", "9~12개월"]


def build_phase_cards(session_label: str) -> List[Dict[str, Any]]:
    months = extract_month_count(session_label)
    periods = phase_ranges(session_label)
    if months <= 1:
        titles = [
            "문제 인지 & 급한 패턴 정리",
            "기본 루틴 장착 & 자세 기준 만들기",
            "짧아도 남는 자가관리 시스템 구축",
        ]
        summaries = [
            "짧은 기간 안에 가장 큰 보상 패턴을 먼저 줄이고, 몸이 어디서 버티는지 스스로 이해하도록 돕습니다.",
            "기본 호흡, 정렬, 핵심 운동 감각을 빠르게 익혀 PT가 없는 날에도 흔들리지 않는 기준을 세웁니다.",
            "끝나고 바로 무너지지 않도록 생활 속 체크포인트와 개인 루틴을 정리합니다.",
        ]
        tags = [
            ["문제 인식", "급한 패턴 정리", "기초 적응"],
            ["정렬 기준", "기본 루틴", "감각 학습"],
            ["자가관리", "재발 방지", "생활 연결"],
        ]
    elif months == 2:
        titles = [
            "문제 인식 & 루틴 적응",
            "교정 패턴 연결 & 변화 시작",
            "정착 준비 & 자율운동 연결",
        ]
        summaries = [
            "초반에는 회원님 몸에서 반복되는 문제 패턴을 이해하고, 수업 흐름에 적응하는 단계입니다.",
            "중반에는 교정 요소를 실제 운동 패턴에 연결해 체형과 컨디션 변화를 체감하게 만듭니다.",
            "후반에는 배운 패턴이 생활과 개인운동에서 유지되도록 정착 장치를 심습니다.",
        ]
        tags = [
            ["적응기", "기준 세우기", "몸 이해"],
            ["교정 연결", "운동 효율", "변화 시작"],
            ["정착 준비", "개인운동", "유지 전략"],
        ]
    elif months == 3:
        titles = [
            "기초 교정 & 루틴 적응",
            "체형 변화 & 수행 향상",
            "유지 전략 & 자립 준비",
        ]
        summaries = [
            "현재 몸 상태를 정확히 해석하고, 보상 패턴을 줄이는 기본 루틴을 만드는 단계입니다.",
            "자세가 무너지지 않는 범위 안에서 체형·체력·체성분 변화를 본격화합니다.",
            "좋아진 패턴이 다시 흐트러지지 않도록 생활 속 유지 전략과 자율운동을 연결합니다.",
        ]
        tags = [
            ["자세 인지", "기초 교정", "루틴 적응"],
            ["체형 변화", "체력 상승", "수행 향상"],
            ["유지 전략", "자율운동", "재발 방지"],
        ]
    elif months == 6:
        titles = [
            "기초 재정렬 & 습관 세팅",
            "체형 변화 가속 & 체력 상승",
            "유지 시스템 정착 & 자율운동 확장",
        ]
        summaries = [
            "초반 2개월은 정렬, 호흡, 가동성, 기본 루틴을 안정화해 흔들리지 않는 기반을 만듭니다.",
            "중반 2개월은 눈에 보이는 체형 변화와 운동 수행 향상을 본격적으로 끌어올리는 구간입니다.",
            "후반 2개월은 좋은 결과를 오래 유지할 수 있도록 생활 속 실천 시스템까지 완성하는 단계입니다.",
        ]
        tags = [
            ["기초 재정렬", "통증 완화", "습관 세팅"],
            ["변화 가속", "강도 상승", "체력 향상"],
            ["유지 시스템", "자율운동", "장기 정착"],
        ]
    else:
        titles = [
            "몸 사용법 재학습 & 기준 세우기",
            "교정 완성도 향상 & 변화 가속",
            "장기 유지 시스템 & 독립 운동 완성",
        ]
        summaries = [
            "초기 4개월은 몸의 기본 패턴과 생활 습관을 함께 다듬어, 왜 이 운동을 해야 하는지 스스로 이해하게 만듭니다.",
            "중기 4개월은 교정과 운동 성과를 함께 끌어올리며, 체형·체력·생활 루틴을 한 단계 더 끌어올립니다.",
            "후기 4개월은 PT가 없어도 유지 가능한 루틴과 체크 기준을 완성해 장기 결과를 남기는 단계입니다.",
        ]
        tags = [
            ["기준 세우기", "문제 인식", "몸 재학습"],
            ["교정 심화", "변화 가속", "성과 누적"],
            ["장기 유지", "독립 운동", "생활 정착"],
        ]

    return [
        {
            "step": f"{idx + 1}단계",
            "period": periods[idx],
            "title": titles[idx],
            "summary": summaries[idx],
            "tags": tags[idx],
        }
        for idx in range(3)
    ]


def get_issue_roadmap_profile(issue_id: str) -> Dict[str, str]:
    profile_map = {
        "forward_head": {
            "core": "목·어깨 과긴장과 경추 전방 이동 패턴",
            "release": "흉추, 소흉근, 상부 승모, 후두하근 긴장을 먼저 완화",
            "pattern": "턱당기기, 흉추 가동성, 견갑 안정화, 코어 연결을 순서대로 학습",
            "feel": "목·어깨 뻐근함 감소와 상체 운동 자극 인지 향상",
            "lifestyle": "앉는 자세, 모니터 높이, 휴대폰 사용 습관을 함께 리셋",
            "pt_flow": "거울 피드백과 촉각 코칭으로 경추-흉추-견갑의 순서를 재학습",
            "home": "5~10분 목-흉추 mobility와 벽 기대 정렬 루틴으로 생활 연결",
            "weak": "거북목 경향, 승모 과개입, 흉추 가동성 부족",
            "coach": "목이 아니라 등·코어가 먼저 일하도록 감각을 재교육",
        },
        "rounded_shoulder": {
            "core": "말린 어깨와 흉곽 전면 지배 패턴",
            "release": "흉근, 전면 어깨, 흉추 굴곡 패턴을 우선 완화",
            "pattern": "흉추 신전, 견갑 후인·하강, 등 자극 인지를 단계적으로 연결",
            "feel": "어깨 답답함 감소와 상체 라인 정돈, 등 운동 만족도 향상",
            "lifestyle": "책상 작업, 운전, 스마트폰 사용 자세를 생활 속에서 교정",
            "pt_flow": "견갑 움직임과 팔 궤적을 동시에 잡아 실제 자세 변화를 만듦",
            "home": "폼롤러 흉추 루틴과 밴드 견갑 안정화 루틴을 짧게 반복",
            "weak": "라운드숄더 경향, 흉추 신전 부족, 상체 안정성 부족",
            "coach": "가슴을 펴라는 지시보다 견갑이 자연스럽게 자리 잡는 감각 코칭",
        },
        "pelvic_tilt": {
            "core": "골반 전방경사와 허리 과신전 보상 패턴",
            "release": "고관절 굴곡근, 허리 과긴장, 앞벅지 우세 패턴을 먼저 정리",
            "pattern": "호흡-복압-둔근 연결과 힌지/스쿼트 기초 패턴을 재학습",
            "feel": "허리 부담 감소와 하체 운동 시 엉덩이·복부 사용감 향상",
            "lifestyle": "서 있는 자세, 앉는 습관, 골반 전방 이동 패턴을 같이 점검",
            "pt_flow": "골반 중립 인지부터 하체 기본 패턴까지 단계별로 연결",
            "home": "브레이싱, 힙힌지, 둔근 활성화 루틴을 짧게 습관화",
            "weak": "골반 정렬 이슈, 코어 연결 부족, 둔근 활성 저하",
            "coach": "허리 힘을 빼고 복압과 둔근이 먼저 반응하도록 기준을 심기",
        },
        "low_back": {
            "core": "허리 과사용과 코어 불안정 패턴",
            "release": "허리 주변 과긴장을 줄이고 안전한 가동 범위를 확보",
            "pattern": "호흡, 복압, 힙힌지, 코어 지지 패턴을 다시 배움",
            "feel": "운동 후 허리 뻐근함 감소와 움직임 자신감 회복",
            "lifestyle": "오래 앉기, 무거운 물건 들기, 피로 누적 패턴까지 관리",
            "pt_flow": "통증 회피가 아니라 안전한 범위 안에서 움직임 자신감을 회복",
            "home": "호흡 브레이싱, 버드독, 데드버그, 힙힌지 루틴으로 연결",
            "weak": "허리 통증/불편감, 코어 안정성 부족, 힙힌지 패턴 부족",
            "coach": "허리가 버티는 운동이 아니라 몸통이 지지하는 운동으로 전환",
        },
        "diet": {
            "core": "체지방 정체를 만드는 생활습관 패턴",
            "release": "붓기, 피로, 폭식/야식 트리거를 먼저 파악하고 정리",
            "pattern": "전신 근력 루틴, 활동량, 식사 기준, 주말 패턴을 함께 관리",
            "feel": "체중 숫자보다 먼저 컨디션, 붓기, 식욕 패턴이 안정되는 변화",
            "lifestyle": "식사 기록, 단백질 기준, 음주·야식 대응 전략을 현실적으로 세팅",
            "pt_flow": "수업 외 시간의 실패 패턴까지 점검해 감량 유지력을 높임",
            "home": "걷기, 짧은 근력 루틴, 식사 체크로 PT 없는 날의 결과를 관리",
            "weak": "체지방 관리 필요, 식습관 불규칙, 활동량 부족",
            "coach": "실패 원인을 죄책감이 아니라 체크포인트로 바꾸는 코칭",
        },
        "generic": {
            "core": "현재 체형과 움직임에서 반복되는 보상 패턴",
            "release": "긴장되는 부위는 풀고, 잘 안 쓰는 부위는 깨우는 순서 정리",
            "pattern": "자세 인지, 호흡, 가동성, 안정성, 기본 근력 패턴을 단계적으로 연결",
            "feel": "운동이 덜 막막해지고 원하는 부위 자극과 컨디션이 좋아지는 변화",
            "lifestyle": "직업 특성과 생활 습관 때문에 무너지는 패턴까지 함께 관리",
            "pt_flow": "혼자 운동할 때 놓치기 쉬운 기준을 수업에서 매회 교정",
            "home": "부담 없는 개인 루틴부터 만들어 PT 밖에서도 흐름을 이어감",
            "weak": "현재 몸 상태에 맞는 운동 기준 부족",
            "coach": "문제를 세게 지적하기보다 몸의 순서를 이해시키는 설명 중심 코칭",
        },
    }
    return profile_map.get(issue_id, profile_map["generic"])


def build_direction_rows(member: Dict[str, Any], sales_focus: Dict[str, Any]) -> List[Dict[str, str]]:
    issue = detect_primary_sales_issue(member)
    profile = get_issue_roadmap_profile(issue["id"])
    months = extract_month_count(member["session_plan"])
    goal_focus = safe_text(member.get("goal_focus", ""))
    strengths = member.get("strengths") or ["피드백 습득력이 좋음", "운동 의지가 강함"]
    weaknesses = member.get("weaknesses") or [sales_focus["problem_label"]]
    strengths_text = ", ".join(strengths[:2])
    weaknesses_text = ", ".join(weaknesses[:2])

    is_diet = goal_focus in ["다이어트", "체지방감량"] or issue["id"] == "diet"
    is_strength = goal_focus in ["근력향상", "근력증가", "근육증가"]
    is_posture = goal_focus in ["체형교정", "통증완화"] or issue["id"] in ["forward_head", "rounded_shoulder", "pelvic_tilt", "low_back"]

    if is_diet:
        rows = [
            {"label": "이 단계의 핵심 목표", "v1": "체지방 감량을 방해하는 생활 패턴을 정리하고, 무리 없는 적응 루틴을 만듭니다.", "v2": "식사·활동량·근력운동 흐름을 연결해 감량 효율과 체력 향상을 함께 끌어올립니다.", "v3": "감량 후 반등을 줄일 수 있도록 유지 전략과 자율운동 시스템을 완성합니다."},
            {"label": "우선 관리 포인트", "v1": profile["release"], "v2": "운동 강도만 올리기보다 식사 기준, 수면, 주말 패턴이 흔들리지 않게 관리합니다.", "v3": "회복이 무너지지 않는 범위에서 활동량과 운동 강도를 안정적으로 유지합니다."},
            {"label": "수업 진행 방식", "v1": "전신 근력 루틴과 기초 체력 적응을 중심으로 진행하고, 수업 외 실패 패턴도 함께 점검합니다.", "v2": "부위별 보완 운동과 목적형 유산소를 연결해 체형 변화가 보이도록 설계합니다.", "v3": "회원님 일정에 맞춘 유지형 루틴과 자율운동 비중을 높여 결과가 이어지게 만듭니다."},
            {"label": "회원이 체감할 변화", "v1": "붓기, 피로, 식욕 패턴이 조금씩 안정되고 운동이 덜 버겁게 느껴집니다.", "v2": "체형 라인, 컨디션, 체력 변화가 눈에 보이기 시작하고 감량 흐름이 붙습니다.", "v3": "체중 숫자에만 흔들리지 않고 스스로 조절할 수 있다는 자신감이 생깁니다."},
            {"label": "생활습관/식단 전략", "v1": "식사 간격, 단백질 기준, 야식·음주 대응 전략을 현실적으로 정리합니다.", "v2": "외식, 회식, 주말 일정이 있어도 무너지지 않는 식사 기준을 만듭니다.", "v3": "감량 이후에도 유지 가능한 개인 식사 패턴과 활동 기준을 완성합니다."},
            {"label": "PT 운영 방식", "v1": "주 2회 PT를 기준으로 몸 상태를 점검하고, 수업 사이 실천 과제를 간단히 확인합니다.", "v2": "주 2회 PT + 생활 체크를 묶어 감량이 실제 일상에서 이어지도록 만듭니다.", "v3": "점검형 수업을 병행해 혼자 운동하는 비중이 늘어도 결과 흐름이 유지되게 합니다."},
            {"label": "혼자 하는 루틴", "v1": "걷기, 짧은 전신 루틴, 식사 체크 중심으로 PT 없는 날의 결과를 관리합니다.", "v2": "유산소와 보조운동을 추가해 주간 총 활동량이 꾸준히 확보되게 만듭니다.", "v3": "일정에 맞춰 스스로 운동 계획을 조절하고 유지할 수 있는 루틴을 완성합니다."},
            {"label": "우선 보완 포인트", "v1": weaknesses_text or profile["weak"], "v2": "중기에는 피로하거나 바쁠 때 다시 올라오는 식습관 흔들림을 줄이는 것이 중요합니다.", "v3": "후반에는 감량보다 유지 전략이 무너지지 않도록 회복과 일정 관리까지 같이 봐야 합니다."},
            {"label": "변화 가능성이 높은 이유", "v1": strengths_text or "기본 적응력이 좋아 루틴만 잡히면 변화 속도가 붙을 가능성이 높습니다.", "v2": "체크포인트가 쌓일수록 회원님에게 맞는 감량 공식이 더 선명해질 가능성이 큽니다.", "v3": "유지 기준까지 잡히면 단기 변화가 아니라 생활형 결과로 이어질 가능성이 높습니다."},
            {"label": "트레이너 중점 코칭 포인트", "v1": "체중보다 패턴을 먼저 잡아 드리고, 실패 원인을 죄책감이 아니라 수정 가능한 기준으로 바꿔드립니다.", "v2": "좋아진 흐름이 운동 시간에만 머물지 않고 식사와 생활 안에 자리잡도록 반복 코칭합니다.", "v3": "혼자서도 체중과 컨디션을 안정적으로 관리할 수 있도록 유지 기준을 남기는 데 집중합니다."},
        ]
    elif is_strength:
        rows = [
            {"label": "이 단계의 핵심 목표", "v1": "정확한 기본 패턴과 힘 전달 방식을 익혀 안전한 근력 향상 기반을 만듭니다.", "v2": "중량과 수행 능력을 단계적으로 높이며, 주요 운동의 완성도를 끌어올립니다.", "v3": "혼자서도 중량과 강도를 안정적으로 관리할 수 있는 독립 루틴을 완성합니다."},
            {"label": "우선 관리 포인트", "v1": "코어 안정성, 호흡, 기본 자세, 좌우 밸런스를 먼저 정리합니다.", "v2": "주동근 자극과 보조근 개입 비율을 조절해 효율적인 힘 전달을 만듭니다.", "v3": "강도가 올라가도 폼이 무너지지 않도록 회복과 기술 유지에 집중합니다."},
            {"label": "수업 진행 방식", "v1": "기초 패턴 교육과 머신·프리웨이트 적응을 병행해 운동 감각을 정확히 잡습니다.", "v2": "목적형 분할 루틴으로 주요 리프트와 보완 운동을 체계적으로 연결합니다.", "v3": "회원님 수준에 맞춘 고도화 루틴과 자율운동 프로그램으로 독립성을 높입니다."},
            {"label": "회원이 체감할 변화", "v1": "운동 자극이 더 선명해지고, 같은 동작도 훨씬 안정적으로 느껴집니다.", "v2": "중량, 반복수, 운동 완성도가 함께 올라가며 성취감이 분명해집니다.", "v3": "혼자 운동할 때도 방향을 잃지 않고 스스로 강도를 조절할 수 있게 됩니다."},
            {"label": "생활습관/식단 전략", "v1": "수업 효과를 살릴 수 있도록 수면, 단백질 섭취, 회복 루틴을 먼저 정리합니다.", "v2": "운동 강도에 맞춰 식사량과 회복 전략을 조절해 수행 저하를 줄입니다.", "v3": "바쁜 일정 속에서도 근력 유지가 가능한 개인 기준을 만들고 습관화합니다."},
            {"label": "PT 운영 방식", "v1": "주 2회 PT로 자세와 힘쓰는 순서를 먼저 잡고, 수업마다 수행 데이터를 점검합니다.", "v2": "주 2회 PT + 기록 관리로 중량 상승과 폼 완성도를 함께 확인합니다.", "v3": "점검형 수업을 병행해 혼자 운동 비중이 늘어도 퀄리티가 떨어지지 않게 합니다."},
            {"label": "혼자 하는 루틴", "v1": "복습용 기초 루틴과 코어·보조운동으로 PT 없는 날의 감각을 유지합니다.", "v2": "메인 운동 + 보조운동 조합으로 주간 볼륨을 안정적으로 누적합니다.", "v3": "주간 계획을 스스로 설계하고 조절할 수 있는 독립 루틴으로 정리합니다."},
            {"label": "우선 보완 포인트", "v1": weaknesses_text or profile["weak"], "v2": "중기에는 중량 욕심으로 폼이 무너지는 순간을 줄이는 것이 중요합니다.", "v3": "후반에는 강도 상승과 회복 밸런스를 같이 관리해야 성과가 오래 유지됩니다."},
            {"label": "변화 가능성이 높은 이유", "v1": strengths_text or "피드백 반응이 좋아 기본 패턴만 잡히면 수행 향상이 빠를 가능성이 높습니다.", "v2": "기록이 쌓일수록 회원님에게 맞는 강도와 볼륨이 더 정교해질 가능성이 큽니다.", "v3": "독립 루틴까지 정착되면 눈에 보이는 근력 향상과 자신감이 함께 커질 가능성이 높습니다."},
            {"label": "트레이너 중점 코칭 포인트", "v1": "중량보다 먼저 정확도를 잡아 드리고, 힘이 새지 않는 패턴을 만드는 데 집중합니다.", "v2": "좋아진 수행이 일시적이지 않도록 자극 인지와 기록 관리까지 함께 코칭합니다.", "v3": "혼자서도 안정적으로 중량을 다룰 수 있는 기준을 남기는 데 초점을 둡니다."},
        ]
    elif is_posture:
        rows = [
            {"label": "이 단계의 핵심 목표", "v1": "반복되는 불편 패턴과 정렬 문제를 파악하고, 몸이 편한 기본 움직임을 다시 만듭니다.", "v2": "가동성·안정성·근력 연결을 통해 자세 유지 능력과 운동 완성도를 함께 높입니다.", "v3": "좋아진 정렬이 일상과 운동에서 자연스럽게 유지되도록 시스템을 완성합니다."},
            {"label": "우선 관리 포인트", "v1": profile["release"], "v2": "보상 패턴이 다시 나오지 않도록 호흡, 코어, 관절 정렬을 함께 연결합니다.", "v3": "운동 강도와 일상 피로가 올라가도 무너지지 않는 유지 능력을 키웁니다."},
            {"label": "수업 진행 방식", "v1": "근막이완, 가동성, 자세 인지, 기초 패턴 재교육 순서로 무리 없이 진행합니다.", "v2": "교정 요소를 메인 운동과 연결해 실제 체형 변화와 움직임 개선이 보이게 만듭니다.", "v3": "회원님 생활 패턴에 맞춘 유지 루틴과 자율운동 프로그램을 병행합니다."},
            {"label": "회원이 체감할 변화", "v1": "뻐근함과 답답함이 줄고, 원하는 부위에 힘이 더 잘 들어가기 시작합니다.", "v2": "자세가 한결 편안해지고 운동이 덜 막막해지며 체형 변화가 눈에 보이기 시작합니다.", "v3": "일상에서도 스스로 자세를 인지하고 조절할 수 있는 자신감이 생깁니다."},
            {"label": "생활습관/식단 전략", "v1": "직업 특성, 오래 앉는 시간, 수면 자세, 피로 패턴을 먼저 같이 점검합니다.", "v2": "운동 효과를 유지할 수 있도록 활동량, 스트레칭, 회복 습관을 현실적으로 맞춥니다.", "v3": "바쁜 일정 속에서도 자세가 무너지지 않도록 생활 체크포인트를 개인화합니다."},
            {"label": "PT 운영 방식", "v1": "주 2회 PT로 몸의 기준점을 세우고, 수업마다 정렬과 보상 패턴을 세밀하게 확인합니다.", "v2": "주 2회 PT + 과제 점검으로 좋아진 패턴이 실제 운동 습관에 반영되게 만듭니다.", "v3": "점검형 수업을 병행해 PT 의존도를 줄여도 자세 퀄리티가 유지되도록 설계합니다."},
            {"label": "혼자 하는 루틴", "v1": "짧은 스트레칭, 호흡, 코어 활성 루틴으로 PT 없는 날의 감각을 이어갑니다.", "v2": "교정 운동과 보조운동을 추가해 좋은 패턴이 더 빨리 자리잡게 만듭니다.", "v3": "주간 루틴을 스스로 점검하고 조절할 수 있도록 자율운동 기준을 남깁니다."},
            {"label": "우선 보완 포인트", "v1": weaknesses_text or profile["weak"], "v2": "중기에는 피곤할 때 다시 올라오는 보상 패턴을 줄이는 것이 핵심입니다.", "v3": "후반에는 강도 증가보다 좋은 정렬을 오래 유지하는 능력이 더 중요합니다."},
            {"label": "변화 가능성이 높은 이유", "v1": strengths_text or "피드백 수용이 좋아 기본 기준만 잡히면 체형 변화가 빠르게 보일 가능성이 높습니다.", "v2": "움직임 이해도가 올라갈수록 교정 속도와 운동 만족도가 함께 높아질 가능성이 큽니다.", "v3": "유지 루틴까지 정착되면 체형과 컨디션을 장기적으로 안정시키기 좋습니다."},
            {"label": "트레이너 중점 코칭 포인트", "v1": "문제를 강하게 지적하기보다 몸의 원리를 이해시키고, 회원님이 스스로 납득하도록 설명합니다.", "v2": "좋아진 정렬이 수업 시간에만 머물지 않고 메인 운동과 일상까지 이어지도록 코칭합니다.", "v3": "혼자서도 자세를 체크하고 조절할 수 있는 기준을 남기는 데 집중합니다."},
        ]
    else:
        rows = [
            {"label": "이 단계의 핵심 목표", "v1": f"현재 몸에서 반복되는 '{profile['core']}' 패턴을 이해하고, 무리 없는 기본 루틴에 적응합니다.", "v2": f"정렬과 수행이 무너지지 않는 범위 안에서 {goal_focus or '운동'} 변화를 본격화합니다.", "v3": "좋아진 패턴을 생활 속에서도 유지할 수 있도록 자율운동 시스템을 완성합니다."},
            {"label": "우선 관리 포인트", "v1": profile["release"], "v2": f"{profile['pattern']}을 실제 메인운동과 생활 루틴에 연결합니다.", "v3": "강도가 올라가도 정렬과 회복이 흔들리지 않도록 유지 능력을 키웁니다."},
            {"label": "수업 진행 방식", "v1": f"기초 패턴, 자세 인지, 호흡, 기본 근력 루틴 중심으로 시작합니다. {profile['pt_flow']}", "v2": "목적형 루틴을 적용해 체력 향상과 운동 이해도를 함께 끌어올립니다.", "v3": "자율운동 비중을 늘려도 방향을 잃지 않도록 독립 루틴을 병행합니다."},
            {"label": "회원이 체감할 변화", "v1": profile["feel"], "v2": "운동이 덜 막막해지고 몸선·컨디션·체력 변화가 눈에 보이기 시작합니다.", "v3": "혼자서도 운동 방향을 유지할 수 있다는 자신감이 생깁니다."},
            {"label": "생활습관/식단 전략", "v1": profile["lifestyle"], "v2": "수면, 활동량, 외식 대응, 회복 습관을 목표에 맞게 정리합니다.", "v3": "일정 변화가 있어도 결과 흐름을 크게 흔들지 않는 개인 기준을 완성합니다."},
            {"label": "PT 운영 방식", "v1": "주 2회 PT를 기준으로 몸의 기준점을 세우고, 매 수업마다 실천 여부를 짧게 점검합니다.", "v2": "주 2회 PT + 과제 점검으로 배운 내용을 실제 생활과 운동 수행으로 연결합니다.", "v3": "점검형 수업을 병행해 혼자 운동하는 비중이 늘어도 흐름이 유지되게 합니다."},
            {"label": "혼자 하는 루틴", "v1": profile["home"], "v2": "유산소, 보조운동, 코어 또는 자세 루틴을 추가해 PT 외 시간에도 변화를 누적합니다.", "v3": "주간 운동 계획을 스스로 세우고 실행할 수 있도록 루틴 완성도를 높입니다."},
            {"label": "우선 보완 포인트", "v1": weaknesses_text or profile["weak"], "v2": f"중기에는 '{sales_focus['problem_label']}' 패턴이 피로할 때 다시 올라오지 않게 유지력이 중요합니다.", "v3": "후반에는 강도 증가와 일정 변화 속에서도 회복과 루틴 관리가 함께 유지되어야 합니다."},
            {"label": "변화 가능성이 높은 이유", "v1": strengths_text or "피드백 수용과 기본 적응력이 좋아 변화 속도가 빠를 가능성이 있습니다.", "v2": "피드백이 누적될수록 운동 이해도와 자세 수정 속도가 함께 올라갈 가능성이 큽니다.", "v3": "루틴만 정착되면 결과를 장기적으로 유지할 가능성이 높은 타입입니다."},
            {"label": "트레이너 중점 코칭 포인트", "v1": profile["coach"], "v2": "좋아진 패턴이 실제 메인운동과 일상까지 이어지도록 반복 피드백을 제공합니다.", "v3": "PT 없이도 스스로 체크하고 조절할 수 있는 기준을 남기는 데 초점을 둡니다."},
        ]

    if months <= 1:
        rows[0]["v1"] = "짧은 기간 안에 가장 큰 방해 요소를 파악하고, 바로 실천 가능한 핵심 루틴부터 정리합니다."
        rows[5]["v1"] = "주 2~3회 PT로 기준을 빠르게 세우고, 수업 사이 과제를 바로 반영합니다."
        rows[5]["v3"] = "마지막 구간에는 혼자 해도 되는 루틴과 주의 포인트를 명확히 정리합니다."
    elif months == 2:
        rows[5]["v1"] = "주 2회 PT를 중심으로 기초를 잡고, 매주 생활 습관과 운동 흐름을 함께 점검합니다."
        rows[5]["v3"] = "마지막 구간에서는 자율운동 연결 비중을 높여 종료 후 공백을 줄입니다."
    elif months == 6:
        rows[5]["v2"] = "주 2회 PT + 월 단위 재점검으로 자세·체력·생활습관 변화를 함께 관리합니다."
        rows[5]["v3"] = "후반에는 점검형 수업 비중을 조금씩 높여도 흐름이 유지되도록 설계합니다."
    elif months >= 12:
        rows[0]["v3"] = "좋아진 체형과 운동 능력을 1년 이후에도 유지할 수 있도록 독립적인 운동 시스템을 완성합니다."
        rows[5]["v2"] = "주 2회 PT + 월 단위 재평가로 성과와 생활 습관 정착도를 함께 관리합니다."
        rows[5]["v3"] = "후기에는 유지형 운영으로 전환하며, PT 없이도 관리 가능한 기준을 남깁니다."

    return rows


def contains_any(texts: List[str], keywords: List[str]) -> bool:
    joined = " ".join(texts).lower()
    return any(keyword.lower() in joined for keyword in keywords)


def to_ascii_safe_text(value: Any) -> str:
    text = safe_text(value)
    return text.encode("ascii", "ignore").decode("ascii").strip()


def get_member_issue_text(member: Dict[str, Any]) -> str:
    return " ".join(
        [safe_text(x) for x in member.get("strengths", []) + member.get("weaknesses", []) + member.get("special_notes", []) if safe_text(x)]
        + [
            safe_text(member.get("visceral_note", "")),
            safe_text(member.get("goal_focus", "")),
            safe_text(member.get("session_plan", "")),
        ]
    )


def detect_primary_sales_issue(member: Dict[str, Any]) -> Dict[str, Any]:
    source_text = get_member_issue_text(member)
    goal_focus = safe_text(member.get("goal_focus", ""))
    pbf = float(member.get("pbf", 0) or 0)
    issue_catalog = [
        {
            "id": "forward_head",
            "title": "거북목 / 경추 전방 이동 패턴",
            "compare_title": "정상 경추 정렬 vs 거북목 경추 정렬 비교",
            "normal_label": "정상 정렬",
            "problem_label": "거북목 패턴",
            "normal_points": [
                "귀-어깨 라인이 비교적 수직에 가깝고 목 전면 긴장이 덜합니다.",
                "경추의 자연스러운 곡선이 유지되어 목·어깨 부담이 분산됩니다.",
                "흉추 움직임과 견갑 움직임이 함께 나와 상체 운동 효율이 좋습니다.",
            ],
            "problem_points": [
                "머리가 앞으로 빠지며 경추 앞쪽과 승모 상부에 부담이 집중됩니다.",
                "흉추 굴곡과 라운드숄더가 동반되어 목·어깨 뻐근함이 반복되기 쉽습니다.",
                "가슴 운동, 등 운동 시에도 보상 패턴이 먼저 나와 자극 전달이 떨어집니다.",
            ],
            "causes": [
                "장시간 앉는 자세와 모니터·휴대폰 사용 시간이 긴 생활 패턴",
                "흉추 가동성 저하 + 깊은 목 굴곡근 및 코어 안정성 부족",
                "운동할 때도 목과 승모로 힘을 먼저 쓰는 습관",
            ],
            "risks": [
                "목 결림, 두통, 승모근 과긴장, 어깨 충돌 패턴이 반복될 수 있습니다.",
                "상체 운동을 해도 목·어깨만 더 뻐근해지고 자세가 더 무너질 수 있습니다.",
                "방치 시 라운드숄더, 흉추 굴곡, 호흡 패턴 저하까지 연결되기 쉽습니다.",
            ],
            "pt_need": [
                "혼자 스트레칭만 해서는 정렬 인지 → 가동성 회복 → 안정성 강화 순서가 잘 안 잡힙니다.",
                "PT에서는 거울 피드백과 촉각 코칭으로 경추-흉추-견갑 움직임을 다시 학습시킬 수 있습니다.",
                "초기 몇 회는 통증/불편감 감소, 이후에는 운동 자세 교정과 습관화까지 연결해야 합니다.",
            ],
            "image_title": "정상 경추 vs 거북목 경추 비교 이미지",
            "image_caption": "정상 경추 정렬과 거북목 패턴의 차이를 한눈에 보여주는 비교형 참고 이미지",
        },
        {
            "id": "rounded_shoulder",
            "title": "라운드숄더 / 견갑 전인 패턴",
            "compare_title": "정상 어깨 정렬 vs 라운드숄더 비교",
            "normal_label": "정상 정렬",
            "problem_label": "라운드숄더 패턴",
            "normal_points": [
                "어깨가 귀보다 과하게 말리지 않고 가슴과 등 자극 전달이 자연스럽습니다.",
                "견갑이 안정적으로 움직여 상체 운동 시 힘 전달이 고르게 나옵니다.",
                "흉추 신전과 호흡이 비교적 편안하게 유지됩니다.",
            ],
            "problem_points": [
                "어깨가 말리고 흉근이 짧아져 목과 전면 어깨의 긴장이 커집니다.",
                "등 운동을 해도 광배·중하부 승모보다 상부 승모 보상이 먼저 나옵니다.",
                "가슴을 펴라는 말만으로는 교정이 잘 안 되고 다시 말리기 쉽습니다.",
            ],
            "causes": [
                "책상 작업, 운전, 스마트폰 사용 등 전면 지배적인 생활 패턴",
                "흉추 신전 부족과 견갑 후인/하강 조절 능력 저하",
                "상체 운동 시 가슴·전면 어깨 위주로 반복한 습관",
            ],
            "risks": [
                "어깨 통증, 목 긴장, 등 자극 저하로 운동 만족도가 떨어질 수 있습니다.",
                "벤치프레스·숄더프레스에서 충돌 패턴이 심해질 수 있습니다.",
                "체형 변화가 더디고 상체 라인이 둥글게 굳어 보일 수 있습니다.",
            ],
            "pt_need": [
                "흉곽 위치, 견갑 움직임, 팔의 궤적을 동시에 잡아줘야 실제 교정이 됩니다.",
                "폼롤러, 흉추 가동성, 견갑 안정화, 등 자극 인지를 단계적으로 연결해야 합니다.",
                "혼자 운동 시 놓치기 쉬운 보상 패턴을 PT에서 즉시 피드백할 수 있습니다.",
            ],
            "image_title": "정상 어깨 vs 라운드숄더 비교 이미지",
            "image_caption": "정상 어깨 정렬과 라운드숄더 패턴 차이를 설명하는 비교형 참고 이미지",
        },
        {
            "id": "pelvic_tilt",
            "title": "골반 정렬 문제 / 전방경사 패턴",
            "compare_title": "중립 골반 vs 전방경사 골반 비교",
            "normal_label": "중립 골반",
            "problem_label": "전방경사 패턴",
            "normal_points": [
                "골반과 갈비뼈 정렬이 비교적 안정적이라 허리 부담이 덜합니다.",
                "둔근과 코어를 함께 쓰기 쉬워 하체 운동 효율이 올라갑니다.",
                "서 있을 때도 허리 과신전이 덜해 체형이 정돈돼 보입니다.",
            ],
            "problem_points": [
                "허리가 과하게 꺾이고 복부 힘이 빠져 코어가 무너지기 쉽습니다.",
                "스쿼트·런지에서 허리, 앞벅지 보상이 먼저 나올 수 있습니다.",
                "엉덩이 자극을 찾기 어렵고 하체 라인 불균형이 생길 수 있습니다.",
            ],
            "causes": [
                "장시간 서기/앉기, 고관절 굴곡근 단축, 복압 유지 습관 부족",
                "둔근 활성 저하와 허리 위주 움직임 패턴",
                "자세보다 중량·횟수만 먼저 올린 운동 습관",
            ],
            "risks": [
                "허리 피로 누적, 하체 비대칭, 하복부 힘 빠짐이 심해질 수 있습니다.",
                "하체 운동을 할수록 허리만 더 쓰는 패턴으로 고착될 수 있습니다.",
                "복부·골반 라인이 정리되지 않아 체형 스트레스가 커질 수 있습니다.",
            ],
            "pt_need": [
                "골반 중립 인지와 호흡-복압-둔근 연결을 동시에 잡아야 합니다.",
                "PT에서는 힌지, 스쿼트, 런지 기본 패턴을 몸에 맞게 재교육할 수 있습니다.",
                "교정 없이 강도만 올리면 보상이 심해지므로 초기 교정 단계가 중요합니다.",
            ],
            "image_title": "중립 골반 vs 전방경사 비교 이미지",
            "image_caption": "골반 중립과 전방경사 패턴 차이를 보여주는 비교형 참고 이미지",
        },
        {
            "id": "low_back",
            "title": "허리 통증 / 코어 불안정 패턴",
            "compare_title": "중립 척추 패턴 vs 허리 보상 패턴 비교",
            "normal_label": "중립 척추",
            "problem_label": "허리 보상 패턴",
            "normal_points": [
                "코어와 골반이 안정되어 허리 힘을 과하게 쓰지 않아도 됩니다.",
                "하체·등 운동 시 몸통 지지가 유지되어 힘 전달이 효율적입니다.",
                "일상에서도 허리 피로 누적이 상대적으로 적습니다.",
            ],
            "problem_points": [
                "몸통 지지가 약해 움직일 때 허리로 먼저 버티는 습관이 나타납니다.",
                "코어보다 척추기립근에 힘이 몰려 운동 후 허리 뻐근함이 남기 쉽습니다.",
                "반복될수록 운동 자체가 무섭거나 불편하게 느껴질 수 있습니다.",
            ],
            "causes": [
                "코어 안정성 부족과 복압 유지 미숙",
                "골반-흉곽 정렬 문제, 힙힌지 패턴 부족",
                "통증이 있는데도 자세 교정 없이 운동 강도만 올린 경우",
            ],
            "risks": [
                "허리 불편감이 만성화되어 운동 지속성이 떨어질 수 있습니다.",
                "스쿼트, 데드리프트, 런지에서 보상 패턴이 심화될 수 있습니다.",
                "움직임 자체를 회피하게 되어 체형·체력 저하로 이어질 수 있습니다.",
            ],
            "pt_need": [
                "통증 회피가 아니라 안전한 가동 범위 안에서 패턴을 다시 학습해야 합니다.",
                "PT에서는 호흡, 복압, 힙힌지, 코어 연결을 단계적으로 재교육할 수 있습니다.",
                "허리 부담을 줄이면서도 운동 자신감을 되찾는 과정이 필요합니다.",
            ],
            "image_title": "중립 척추 vs 허리 보상 패턴 비교 이미지",
            "image_caption": "허리 보상 패턴과 중립 척추 차이를 설명하는 비교형 참고 이미지",
        },
        {
            "id": "diet",
            "title": "체지방 관리 실패 패턴 / 생활습관 문제",
            "compare_title": "감량이 되는 생활 패턴 vs 정체를 만드는 생활 패턴 비교",
            "normal_label": "감량 친화 패턴",
            "problem_label": "정체 유발 패턴",
            "normal_points": [
                "식사 간격, 단백질 섭취, 수면, 활동량이 비교적 일정합니다.",
                "PT 수업과 개인운동, 유산소가 연결되어 총 운동량이 확보됩니다.",
                "주말 패턴이 크게 무너지지 않아 체지방 변화가 누적됩니다.",
            ],
            "problem_points": [
                "야식·음주·폭식·수면 부족으로 주중 노력이 상쇄되기 쉽습니다.",
                "운동은 하지만 식습관과 일상 활동량이 정리되지 않아 정체가 길어집니다.",
                "단기 다이어트와 포기가 반복되며 자신감이 떨어질 수 있습니다.",
            ],
            "causes": [
                "식단 기준 부재와 생활 리듬 불안정",
                "주말 보상심리, 음주·야식 빈도, 활동량 부족",
                "운동만 하면 된다는 생각으로 루틴 관리가 빠진 경우",
            ],
            "risks": [
                "감량 정체가 길어져 포기 확률이 높아질 수 있습니다.",
                "체중보다 체지방 비율이 더디게 변해 만족도가 떨어질 수 있습니다.",
                "반복 다이어트로 기초 체력과 식습관 통제가 더 어려워질 수 있습니다.",
            ],
            "pt_need": [
                "감량은 운동 한두 번보다 수업-식습관-활동량-주말 패턴 관리가 핵심입니다.",
                "PT에서는 체크포인트를 만들어 실패 원인을 바로 수정할 수 있습니다.",
                "지속 가능한 일반식 기준과 운동 루틴을 함께 설계해야 실제 변화가 납니다.",
            ],
            "image_title": "감량 성공 패턴 vs 정체 패턴 비교 이미지",
            "image_caption": "감량이 되는 생활 패턴과 정체를 만드는 패턴을 비교하는 세일즈용 참고 이미지",
        },
    ]

    issue_map = {issue["id"]: issue for issue in issue_catalog}
    diet_keywords = ["다이어트", "체지방", "폭식", "야식", "음주", "식습관", "복부비만", "감량", "붓기"]

    # 다이어트 목적이면 체형 키워드가 일부 들어 있어도 우선적으로 감량/생활습관 패턴을 보여주도록 고정
    if goal_focus in ["다이어트", "체지방감량"]:
        return issue_map["diet"]
    if pbf >= 28 and contains_any([source_text], diet_keywords):
        return issue_map["diet"]

    issue_priority = [
        ("diet", diet_keywords),
        ("forward_head", ["거북목", "일자목", "목", "경추", "승모", "두통"]),
        ("rounded_shoulder", ["라운드숄더", "말린어깨", "어깨", "흉추", "견갑"]),
        ("pelvic_tilt", ["골반", "전방경사", "후방경사", "둔근", "힙힌지"]),
        ("low_back", ["허리", "요통", "디스크", "코어", "허리통증"]),
    ]
    for issue_id, keywords in issue_priority:
        if contains_any([source_text], keywords):
            return issue_map[issue_id]

    return {
        "id": "generic",
        "title": "현재 체형/움직임 패턴 분석",
        "compare_title": "효율적인 움직임 패턴 vs 보상 중심 움직임 패턴 비교",
        "normal_label": "효율 패턴",
        "problem_label": "보상 패턴",
        "normal_points": [
            "필요한 부위에 힘이 잘 들어가 운동 효율이 올라갑니다.",
            "통증과 불편감이 적고 운동을 지속하기가 수월합니다.",
            "혼자 운동할 때도 기본 자세를 유지하기 쉽습니다.",
        ],
        "problem_points": [
            "힘이 다른 부위로 새면서 운동 효과 대비 피로감이 커질 수 있습니다.",
            "자세가 무너지면 원하는 변화보다 통증·불편감이 먼저 올 수 있습니다.",
            "혼자 운동할수록 잘못된 패턴이 굳어질 수 있습니다.",
        ],
        "causes": [
            "생활습관과 직업 특성으로 누적된 자세 패턴",
            "기초 가동성·안정성 부족",
            "현재 몸 상태에 맞는 운동 기준 부족",
        ],
        "risks": [
            "운동을 열심히 해도 결과 체감이 늦어질 수 있습니다.",
            "통증 또는 불편감 때문에 중간 이탈 가능성이 커질 수 있습니다.",
            "잘못된 자세가 습관화되어 교정 시간이 더 길어질 수 있습니다.",
        ],
        "pt_need": [
            "PT에서는 회원님 몸 상태에 맞는 시작점을 정확히 잡아줄 수 있습니다.",
            "자세·호흡·가동성·안정성을 순서대로 잡아 운동 효율을 올릴 수 있습니다.",
            "운동 방향을 이해하고 루틴을 정착시키는 데 전문가 피드백이 필요합니다.",
        ],
        "image_title": "현재 상태 vs 목표 패턴 비교 이미지",
        "image_caption": "회원님의 현재 패턴과 개선 방향을 설명하는 세일즈용 참고 이미지",
    }


def detect_image_tags(member: Dict[str, Any]) -> List[str]:
    issue = detect_primary_sales_issue(member)
    tag_map = {
        "forward_head": ["forward head posture", "cervical alignment", "posture comparison"],
        "rounded_shoulder": ["rounded shoulders", "scapular positioning", "posture comparison"],
        "pelvic_tilt": ["anterior pelvic tilt", "pelvic alignment", "movement comparison"],
        "low_back": ["core stability", "neutral spine", "pain-aware exercise"],
        "diet": ["fat loss coaching", "nutrition guidance", "habit comparison"],
        "generic": ["fitness consultation", "movement correction", "healthy lifestyle"],
    }
    return tag_map.get(issue["id"], tag_map["generic"])


def map_goal_focus_to_english(goal_focus: str) -> str:
    goal_focus = safe_text(goal_focus)
    mapping = {
        "체형교정": "posture correction",
        "통증완화": "pain relief and corrective exercise",
        "다이어트": "fat loss",
        "체지방감량": "body fat reduction",
        "근력향상": "strength improvement",
        "근력증가": "strength improvement",
        "근육증가": "muscle gain",
        "재활": "rehabilitation-oriented training",
        "건강관리": "general health improvement",
        "습관형성": "habit building",
    }
    return mapping.get(goal_focus, to_ascii_safe_text(goal_focus) or "fitness improvement")


def build_sales_focus_block(member: Dict[str, Any], template_type: str) -> Dict[str, Any]:
    issue = detect_primary_sales_issue(member)
    member_name = member["member_name"]
    session_plan = member["session_plan"]
    session_count = extract_session_count(session_plan)

    if issue["id"] == "forward_head":
        sales_talk = [
            f"{member_name} 회원님은 목 통증보다 경추-흉추 정렬 재교육이 우선입니다.",
            "스트레칭만으로는 부족하고 견갑 움직임, 흉추 가동성, 코어 안정성이 같이 잡혀야 합니다.",
            f"{session_plan}는 불편 완화와 자세 교정을 함께 보기 위한 현실적인 기간입니다.",
        ]
    elif issue["id"] == "diet":
        sales_talk = [
            f"{member_name} 회원님은 운동량보다 생활 리듬 관리가 결과를 더 크게 좌우합니다.",
            "식사, 활동량, 수면이 같이 정리돼야 감량이 유지됩니다.",
            f"{session_plan}는 체중만 빼는 기간이 아니라 감량 패턴을 만드는 기간입니다.",
        ]
    else:
        sales_talk = [
            f"{member_name} 회원님은 현재 '{issue['title']}' 정리가 우선입니다.",
            "원인 패턴을 먼저 잡아야 운동 효과와 체감 변화가 빨라집니다.",
            f"{session_plan}는 자세 교정과 루틴 정착을 함께 만드는 기간입니다.",
        ]

    coach_takeaway = (
        f"상담 시 '{issue['problem_label']}'을 과장하지 말고 원인, 수정 방향, 예상 기간 순서로 설명하면 설득력이 높습니다. "
        f"{session_count}회 기준으로 초기 적응, 중기 개선, 후기 정착 흐름을 짧게 제시하세요."
    )

    return {
        "title": "4. 문제 인식 & PT 필요성",
        "problem_name": issue["title"],
        "problem_summary": f"현재 상담의 핵심 이슈는 '{issue['title']}'입니다. 비교 설명이 먼저 들어가야 회원이 빠르게 납득합니다.",
        "compare_title": issue["compare_title"],
        "normal_label": issue["normal_label"],
        "problem_label": issue["problem_label"],
        "normal_points": issue["normal_points"],
        "problem_points": issue["problem_points"],
        "causes": issue["causes"],
        "risks": issue["risks"],
        "pt_need": issue["pt_need"],
        "sales_talk": sales_talk,
        "coach_takeaway": coach_takeaway,
        "image_title": issue["image_title"],
        "image_caption": issue["image_caption"],
    }


def build_reference_image_prompt(member: Dict[str, Any], template_type: str) -> str:
    issue = detect_primary_sales_issue(member)
    goal_focus_en = map_goal_focus_to_english(member.get("goal_focus", "fitness improvement"))
    session_count = extract_session_count(safe_text(member.get("session_plan", "30회(3개월)")))
    shared_constraints = (
        "Create a premium clinical educational comparison illustration for a Korean PT sales proposal. "
        "Use a clean white background and brochure-style layout. "
        "Show exactly two clearly separated comparison panels or two full-body side-view figures: left = normal pattern, right = problem pattern. "
        "This must look like an educational posture-analysis board, not a gym action photo. "
        "Do not show squats, lunges, deadlifts, push-ups, dumbbells, barbells, machines, trainers, studio interiors, or workout coaching scenes unless explicitly required. "
        "Avoid generic fitness stock-photo composition. Avoid random English text, watermark, logo, poster headline, or before-after marketing banner. "
    )

    issue_prompts = {
        "forward_head": (
            shared_constraints
            + "Focus on cervical posture comparison only. Left: neutral ear-shoulder alignment and natural cervical curve. "
              "Right: forward head posture with the head translated anteriorly, reduced cervical curve, neck/upper-trap strain emphasis. "
              "Side profile only. Add subtle red guide lines or arrows if helpful. No squat pose. No exercise scene."
        ),
        "rounded_shoulder": (
            shared_constraints
            + "Focus on shoulder alignment comparison only. Left: neutral shoulder and open chest posture. "
              "Right: rounded shoulder posture with protracted scapula and internally rotated shoulder. "
              "Side profile or 3/4 posture-analysis view. No squat pose. No exercise scene."
        ),
        "pelvic_tilt": (
            shared_constraints
            + "Focus on standing posture alignment only. Left: neutral pelvis and stacked ribcage. "
              "Right: anterior pelvic tilt with excessive lumbar arch and rib flare. "
              "Side profile full-body standing comparison. No squat pose. No exercise scene."
        ),
        "low_back": (
            shared_constraints
            + "Focus on spine and core support comparison only. Left: neutral spine with supported core and balanced hip hinge setup. "
              "Right: low-back-dominant compensation with lumbar overuse and poor trunk support. "
              "Keep it posture-analysis style, not a squat workout image."
        ),
        "diet": (
            shared_constraints
            + "Create a split lifestyle comparison, not an exercise pose. Left: sustainable fat-loss lifestyle with regular meals, walking/activity, hydration, sleep rhythm. "
              "Right: stagnation pattern with late-night eating, low activity, irregular routine. No squat pose."
        ),
    }
    if issue["id"] in issue_prompts:
        return issue_prompts[issue["id"]]

    return (
        shared_constraints
        + f"Primary goal: {goal_focus_en}. Suggested package: about {session_count} training sessions. "
          "Show a normal alignment or efficient movement pattern on the left and the member's compensation or problem pattern on the right. "
          "Prefer standing posture comparison or simple anatomy-board style. No squat pose unless the member issue is explicitly squat mechanics."
    )


def choose_template(member: Dict[str, Any]) -> str:
    requested = member["template_mode"]
    if requested != "AUTO":
        return requested

    notes_pool = member["weaknesses"] + member["strengths"] + member["special_notes"]
    goal_focus = member["goal_focus"]
    pbf = float(member["pbf"])

    if goal_focus in ["다이어트", "체지방감량"] or pbf >= 28 or contains_any(notes_pool, ["다이어트", "체지방", "야식", "음주", "식습관", "폭식"]):
        return "B"

    if goal_focus in ["체형교정", "통증완화"] or contains_any(notes_pool, ["거북목", "라운드숄더", "골반", "통증", "역커브", "자세", "척추", "외반슬", "가동성"]):
        return "A"

    return "C"


# ============================================================
# AI JSON 스키마 / 기본값
# ============================================================
def make_empty_phase_rows() -> List[Dict[str, str]]:
    return [{"label": label, "v1": "", "v2": "", "v3": ""} for label in ROW_LABELS]


def build_closing_letter(member: Dict[str, Any], sales_focus: Dict[str, Any]) -> str:
    member_name = member["member_name"]
    goal_focus = safe_text(member.get("goal_focus", ""))

    if goal_focus in ["다이어트", "체지방감량"]:
        return (
            f"{member_name} 회원님은 운동량보다 생활 리듬 정리가 우선입니다.\n"
            "초반에는 식사 간격, 활동량, 수면을 안정시키고 중반부터 근력과 유산소 효율을 올리는 흐름이 적합합니다.\n"
            "이번 과정의 핵심은 단기 감량보다 유지 가능한 감량 패턴을 만드는 것입니다."
        )

    if goal_focus in ["체형교정", "통증완화"]:
        return (
            f"{member_name} 회원님은 강도보다 정렬 회복이 우선입니다.\n"
            "초반에는 자세 인지와 안정성, 중반에는 움직임 완성도와 근력 연결을 잡아야 합니다.\n"
            "이번 과정의 핵심은 통증을 피하는 운동이 아니라 편한 움직임을 다시 만드는 것입니다."
        )

    if goal_focus in ["근력향상", "근력증가", "근육증가"]:
        return (
            f"{member_name} 회원님은 중량보다 기본 패턴 확보가 먼저입니다.\n"
            "초반에는 자세와 힘 전달을 정리하고, 중반부터 수행 능력과 중량을 단계적으로 올려야 합니다.\n"
            "이번 과정의 핵심은 무게를 버티는 몸이 아니라 효율적으로 힘을 쓰는 몸을 만드는 것입니다."
        )

    return (
        f"{member_name} 회원님의 현재 핵심 이슈는 '{sales_focus['problem_name']}'입니다.\n"
        "초반에는 패턴과 생활 루틴을 정리하고, 중반에는 수행 능력을 끌어올리는 접근이 적합합니다.\n"
        "이번 과정의 핵심은 단기 자극보다 오래 유지되는 기준을 만드는 것입니다."
    )


def build_base_report(member: Dict[str, Any], template_type: str) -> Dict[str, Any]:
    member_name = member["member_name"]
    phase_labels = ["1단계", "2단계", "3단계"]
    phase_subtitles = phase_ranges(member["session_plan"])
    phase_cards = build_phase_cards(member["session_plan"])
    sales_focus = build_sales_focus_block(member, template_type)
    direction_rows = build_direction_rows(member, sales_focus)

    if template_type == "A":
        section3_title = "3. 현재 바디 상태"
        section3_paragraphs = [
            f"{member_name} 회원님은 현재 움직임 패턴과 정렬 상태를 우선 확인해야 하는 유형입니다.",
            "운동 전 근막이완과 가동성 확보가 선행되어야 보상 없이 운동 자세를 익히기 좋습니다.",
            "초기에는 통증 감소와 자세 인지가 핵심이며, 이후 근력과 안정성을 단계적으로 올리는 흐름이 적합합니다.",
        ]
        extra_table = {"show": False, "headers": [], "rows": [], "title": ""}
    elif template_type == "B":
        section3_title = "3. 현재까지의 패턴과 개선 포인트"
        section3_paragraphs = [
            f"{member_name} 회원님은 현재 체성분과 생활 패턴을 함께 관리해야 결과가 나는 유형입니다.",
            "극단적인 식단보다 유지 가능한 일반식 기준과 루틴 설계가 중요합니다.",
            "PT 수업 외 개인 유산소, 수면, 음주·야식 빈도까지 같이 관리해야 감량 효율이 올라갑니다.",
        ]
        extra_table = {
            "show": True,
            "title": "식단 가이드",
            "headers": ["구분", "가이드"],
            "rows": [
                ["아침", "단백질 포함 식사 + 과도한 당류 섭취 줄이기"],
                ["점심", "일반식 가능, 밥 양과 단백질 비율을 먼저 조절"],
                ["저녁", "늦은 야식/음주 빈도 줄이고 채소와 단백질 우선"],
                ["간식", "과자 대신 요거트, 과일, 삶은 계란 등으로 대체"],
            ],
        }
    else:
        section3_title = "3. 현재 운동 수행 상태"
        section3_paragraphs = [
            f"{member_name} 회원님은 현재 운동 이해도와 지속성을 같이 키워야 하는 유형입니다.",
            "기초 패턴을 정확히 익히고, 운동 자극을 스스로 느낄 수 있도록 학습시키는 접근이 필요합니다.",
            "혼자 운동할 때도 따라갈 수 있는 간결한 루틴과 체크리스트가 효과적입니다.",
        ]
        extra_table = {
            "show": True,
            "title": "주간 실천 체크",
            "headers": ["항목", "권장 기준"],
            "rows": [
                ["PT 수업", "주 2회 기준 꾸준히 참석"],
                ["개인운동", "주 2~3회 30~50분"],
                ["유산소", "주 2~4회 20~30분"],
                ["수면/회복", "하루 6~8시간 이상 확보"],
            ],
        }

    strengths = member["strengths"] or ["비율이 좋음", "피드백 습득이 빠름", "운동 의지가 있음"]

    return {
        "meta": {
            "template_type": template_type,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "report_version": "sales-focus-v4-roadmap-premium",
        },
        "header": {
            "title": "PT 1:1 맞춤 세일즈 제안서",
            "trainer_line": f"{member['gym_name']} {member['trainer_name']} 트레이너",
            "guide_text": TOP_GUIDE_TEXT,
            "member_display_name": f"{member_name} 회원님",
        },
        "summary_table": {
            "show": True,
            "headers": ["근력", "지구력", "가동성", "유연성"],
            "values": [
                member["scores"]["근력"],
                member["scores"]["지구력"],
                member["scores"]["가동성"],
                member["scores"]["유연성"],
            ],
        },
        "section_1": {
            "title": "1. 회원 목표 및 제안 방향",
            "items": [
                f"{member['goal_focus']} 중심의 맞춤 프로그램 설계",
                f"{extract_session_count(member['session_plan'])}회 진행 동안 몸에 맞는 운동 기준을 익히기",
                "혼자서도 운동 방향을 이해하고 실천할 수 있는 상태 만들기",
            ],
        },
        "section_2": {
            "title": f"2. {member_name} 회원님의 트레이닝 장점",
            "items": strengths,
        },
        "section_3": {
            "title": section3_title,
            "paragraphs": section3_paragraphs + (member["special_notes"][:3] if member["special_notes"] else []),
        },
        "sales_focus": sales_focus,
        "direction_section": {
            "title": "5. 앞으로의 운동 방향성",
            "lead": f"{member_name} 회원님께 필요한 맞춤 변화 로드맵",
            "guide": "현재 상태와 목표를 기준으로 단계 설명과 운영 포인트가 자동 반영된 프리미엄 로드맵입니다.",
            "phase_headings": phase_labels,
            "phase_subtitles": phase_subtitles,
            "phase_cards": phase_cards,
            "rows": direction_rows,
        },
        "closing": {
            "title": "트레이너 코멘트",
            "letter": build_closing_letter(member, sales_focus),
        },
        "reference_block": {
            "show": True,
            "title": sales_focus["image_title"],
            "caption": sales_focus["image_caption"],
            "image_data": None,
            "image_data_list": [],
            "image_captions": [],
            "image_items": [],
        },
        "extra_table": extra_table,
        "image_prompt": build_reference_image_prompt(member, template_type),
    }



def deep_merge(base: Any, incoming: Any) -> Any:
    if isinstance(base, dict) and isinstance(incoming, dict):
        merged = deepcopy(base)
        for key, value in incoming.items():
            if key in merged:
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    if isinstance(base, list) and isinstance(incoming, list):
        return incoming if incoming else base
    return incoming if incoming not in [None, "", [], {}] else base


def report_schema_example(template_type: str) -> Dict[str, Any]:
    example = build_base_report(
        {
            "gym_name": DEFAULT_GYM_NAME,
            "trainer_name": DEFAULT_TRAINER_NAME,
            "member_name": "홍길동",
            "goal_focus": "체형교정",
            "session_plan": "30회(3개월)",
            "scores": {"근력": "중", "지구력": "중하", "가동성": "중", "유연성": "중상"},
            "strengths": ["비율이 좋음", "피드백 습득이 빠름"],
            "weaknesses": ["기초 체력 부족"],
            "special_notes": ["장시간 앉아있는 직업"],
            "pbf": 20,
        },
        template_type,
    )
    example["reference_block"]["image_data"] = None
    example["reference_block"]["image_data_list"] = []
    example["reference_block"]["image_captions"] = []
    example["reference_block"]["image_items"] = []
    return example


def build_member_context_summary(member: Dict[str, Any]) -> str:
    goal_focus = safe_text(member.get("goal_focus", ""))
    session_plan = safe_text(member.get("session_plan", ""))
    gender = safe_text(member.get("gender", ""))
    age = int(member.get("age", 0) or 0)
    pbf = float(member.get("pbf", 0) or 0)
    strengths = ", ".join([safe_text(x) for x in (member.get("strengths") or [])[:2] if safe_text(x)])
    weaknesses = ", ".join([safe_text(x) for x in (member.get("weaknesses") or [])[:3] if safe_text(x)])
    notes = ", ".join([safe_text(x) for x in (member.get("special_notes") or [])[:3] if safe_text(x)])
    scores = member.get("scores", {}) or {}
    score_text = ", ".join([f"{k}:{safe_text(v)}" for k, v in scores.items() if safe_text(v)])
    parts = [
        f"대상: {gender} {age}세" if gender and age else "",
        f"목표: {goal_focus}" if goal_focus else "",
        f"기간: {session_plan}" if session_plan else "",
        f"체지방률: {pbf:.1f}%" if pbf else "",
        f"능력치: {score_text}" if score_text else "",
        f"강점: {strengths}" if strengths else "",
        f"보완 포인트: {weaknesses}" if weaknesses else "",
        f"생활/통증 메모: {notes}" if notes else "",
    ]
    return " / ".join([part for part in parts if part])


def coerce_direction_rows(ai_rows: Any, base_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    ai_list = ai_rows if isinstance(ai_rows, list) else []
    ai_by_label = {}
    for idx, row in enumerate(ai_list):
        if not isinstance(row, dict):
            continue
        label = safe_text(row.get("label"))
        if label:
            ai_by_label[label] = row
        else:
            ai_by_label[f"__idx_{idx}"] = row

    normalized: List[Dict[str, str]] = []
    for idx, base_row in enumerate(base_rows):
        source = ai_by_label.get(base_row["label"]) or ai_by_label.get(f"__idx_{idx}") or {}
        normalized.append({
            "label": base_row["label"],
            "v1": safe_text(source.get("v1")) or base_row.get("v1", ""),
            "v2": safe_text(source.get("v2")) or base_row.get("v2", ""),
            "v3": safe_text(source.get("v3")) or base_row.get("v3", ""),
        })
    return normalized


def tighten_coaching_text(text: str) -> str:
    value = safe_text(text)
    replacements = {
        "가장 중요한 포인트는 단순히": "핵심은",
        "가장 중요한 포인트는": "핵심은",
        "훨씬 중요합니다": "중요합니다",
        "기대할 수 있습니다": "기대됩니다",
        "이라고 보시면 됩니다": "입니다",
        "에 가깝습니다": "입니다",
        "더 크게 좌우합니다": "좌우합니다",
        "몸 상태에 맞게": "현재 상태에 맞게",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.splitlines()]
    return "\n".join([line for line in lines if line]).strip()


def tighten_report_text(payload: Any) -> Any:
    if isinstance(payload, dict):
        tightened = {}
        for key, value in payload.items():
            if key in {"image_data", "image_data_list", "image_items"}:
                tightened[key] = value
            else:
                tightened[key] = tighten_report_text(value)
        return tightened
    if isinstance(payload, list):
        return [tighten_report_text(item) for item in payload]
    if isinstance(payload, str):
        return tighten_coaching_text(payload)
    return payload


def build_prompt(member: Dict[str, Any], template_type: str) -> str:
    example = build_base_report(member, template_type)
    member_context = build_member_context_summary(member)
    return f"""
너는 한국어 PT 상담 제안서 작성 전문가다.
출력은 반드시 JSON 객체만 사용한다. 설명문, 코드블록, 마크다운은 금지한다.

목표:
- template_type={template_type} 형식의 PT 제안서 데이터를 만든다.
- 상단 4칸 능력치 표와 하단 9개 로드맵 표는 반드시 유지한다.
- rows.label 순서는 다음과 같아야 한다:
  {ROW_LABELS}

문체 규칙:
- 짧고 단정하게 쓴다. 과한 친절체, 감성 문구, 가식적인 영업 멘트는 금지한다.
- 모든 문장은 실제 트레이너가 상담 기록지에 적는 수준으로 작성한다.
- 입력 정보에서 최소 1개 이상의 구체 요소를 각 섹션에 직접 반영한다.
- 같은 구조라도 회원마다 표현과 해석이 분명히 달라야 한다.
- '가장 중요한 포인트는', '훨씬', '기대할 수 있습니다' 같은 뜬 문구를 반복하지 않는다.

분량 규칙:
- section_1.items: 3~4개, 항목당 한 문장, 짧고 단정하게
- section_2.items: 3~5개, 강점만 적고 군더더기 금지
- section_3.paragraphs: 2~4개, 문단당 1~2문장
- sales_focus.normal_points / problem_points / causes / risks / pt_need: 각각 3개 이상
- sales_focus.sales_talk: 2~3개, 문장당 한 줄
- direction_section.rows: 정확히 {len(ROW_LABELS)}개, 각 셀은 1문장
- closing.letter: 3~4문장, 짧고 전문가 코멘트처럼 마무리

내용 규칙:
- template_type A는 자세·통증·정렬 중심, B는 감량·생활습관 중심, C는 압축 요약 중심으로 쓴다.
- 표 문구는 목표, 약점, 생활습관, 기간에 맞게 달라져야 하며 generic 반복 문구를 피한다.
- sales_focus.problem_name, compare_title, normal_label, problem_label은 현재 회원 이슈와 맞아야 한다.
- closing.letter에는 내부 영업 용어를 넣지 않는다.
- direction_section.lead와 guide에는 횟수 표기를 반복하지 않는다.
- image_prompt는 영어로 작성한다.

회원 요약:
{member_context}

입력값:
{json.dumps(member, ensure_ascii=False, indent=2)}

반드시 아래 구조를 만족하는 JSON만 출력:
{json.dumps(example, ensure_ascii=False, indent=2)}
"""


SYSTEM_PROMPT = (
    "너는 PT 상담 제안서를 작성하는 수석 트레이너다. "
    "문장은 짧고 전문적으로 쓴다. 입력 회원의 차이를 반드시 반영한다. "
    "출력은 JSON 객체만 반환한다."
)


def generate_report_json(client: Optional[OpenAI], member: Dict[str, Any], template_type: str, model_name: str) -> Dict[str, Any]:
    base = build_base_report(member, template_type)
    if client is None:
        return tighten_report_text(base)

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(member, template_type)},
            ],
            temperature=0.85,
            max_tokens=4000,
        )
        content = response.choices[0].message.content
        ai_data = json.loads(content)
        merged = deep_merge(base, ai_data)

        base_sales_focus = base.get("sales_focus", {})
        merged_sales_focus = merged.setdefault("sales_focus", {})
        locked_sales_focus_keys = [
            "title",
            "problem_name",
            "compare_title",
            "normal_label",
            "problem_label",
            "image_title",
            "image_caption",
        ]
        for key in locked_sales_focus_keys:
            if key in base_sales_focus:
                merged_sales_focus[key] = base_sales_focus[key]

        base_direction = base.get("direction_section", {})
        merged_direction = merged.setdefault("direction_section", {})
        for key in ["title", "phase_cards", "phase_subtitles", "phase_headings"]:
            if key in base_direction:
                merged_direction[key] = base_direction[key]
        merged_direction["rows"] = coerce_direction_rows(merged_direction.get("rows"), base_direction.get("rows", []))
        if not safe_text(merged_direction.get("lead")):
            merged_direction["lead"] = base_direction.get("lead", "")
        if not safe_text(merged_direction.get("guide")):
            merged_direction["guide"] = base_direction.get("guide", "")

        base_closing = base.get("closing", {})
        merged_closing = merged.setdefault("closing", {})
        if "title" in base_closing:
            merged_closing["title"] = base_closing["title"]
        if not safe_text(merged_closing.get("letter")):
            merged_closing["letter"] = base_closing.get("letter", "")

        merged["image_prompt"] = build_reference_image_prompt(member, template_type)
        if isinstance(merged.get("reference_block"), dict):
            merged["reference_block"]["title"] = base["reference_block"]["title"]
            merged["reference_block"]["caption"] = base["reference_block"]["caption"]
            if merged["reference_block"].get("image_data") and not merged["reference_block"].get("image_data_list"):
                merged["reference_block"]["image_data_list"] = [merged["reference_block"]["image_data"]]
            elif not merged["reference_block"].get("image_data_list"):
                merged["reference_block"]["image_data_list"] = []
            if not merged["reference_block"].get("image_captions"):
                merged["reference_block"]["image_captions"] = []
            if not merged["reference_block"].get("image_items"):
                merged["reference_block"]["image_items"] = []

        return tighten_report_text(merged)
    except Exception:
        return tighten_report_text(base)


def maybe_generate_image(client: Optional[OpenAI], enabled: bool, prompt: str):
    if not enabled:
        return None, "참고 이미지 자동생성이 꺼져 있어 기본 플레이스홀더를 표시합니다."
    if client is None:
        return None, "OpenAI API 키를 찾지 못했거나 클라이언트 생성에 실패해 자동 이미지 생성을 건너뛰었습니다."
    if not prompt:
        return None, "이미지 프롬프트가 비어 있어 자동 이미지 생성을 건너뛰었습니다."
    try:
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
        )
        b64_json = getattr(result.data[0], "b64_json", None)
        if b64_json:
            return f"data:image/png;base64,{b64_json}", "AI가 참고 이미지를 자동 생성했습니다."
        url = getattr(result.data[0], "url", None)
        if url:
            return url, "AI가 참고 이미지를 자동 생성했습니다."
        return None, "이미지 생성 응답은 받았지만 실제 이미지 데이터가 없어 플레이스홀더를 표시합니다."
    except Exception as e:
        return None, f"자동 이미지 생성 실패: {safe_text(e) or '원인 미상'}"


# ============================================================
# HTML 템플릿
# ============================================================
COMMON_CSS = r"""
<style>
  @page { size: A4; margin: 13mm 14mm; }
  :root {
    --navy:#14314b;
    --navy-dark:#0f2438;
    --navy-soft:#284f73;
    --blue:#4f86b7;
    --sky:#e8f0f8;
    --sky2:#f6f9fd;
    --sky3:#edf4fb;
    --gold:#caa66a;
    --gold-soft:#f4ece0;
    --mint:#eef8f4;
    --rose:#fff7f4;
    --line:#d8e3ee;
    --line-strong:#93abc0;
    --muted:#5f7082;
    --paper:#ffffff;
    --bg:#eef3f8;
    --ink:#1c2733;
    --shadow:0 12px 28px rgba(15,36,56,.08);
  }
  * {
    box-sizing:border-box;
    -webkit-print-color-adjust:exact;
    print-color-adjust:exact;
  }
  html, body {
    -webkit-print-color-adjust:exact;
    print-color-adjust:exact;
  }
  body {
    margin:0; padding:18px; background:linear-gradient(180deg,#f4f7fb 0%, #eaf0f6 100%);
    font-family:"Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",sans-serif;
    color:var(--ink);
  }
  .sheet {
    width:210mm; min-height:297mm; margin:0 auto; background:var(--paper);
    box-shadow:0 10px 38px rgba(15,36,56,.12); padding:10mm 11mm 12mm;
    border-radius:18px; overflow:hidden; position:relative;
  }
  .sheet::before {
    content:""; position:absolute; inset:0 0 auto 0; height:7px;
    background:linear-gradient(90deg,var(--navy), var(--blue), var(--gold));
  }
  .topbar {
    background:linear-gradient(135deg,var(--navy-dark) 0%, var(--navy) 60%, var(--navy-soft) 100%);
    color:#fff; text-align:center; font-weight:900; font-size:22px;
    padding:13px 14px; margin-bottom:12px; border-radius:16px;
    letter-spacing:.01em; box-shadow:0 10px 24px rgba(20,49,75,.18);
  }
  .trainer-line {
    text-align:center; font-size:24px; font-weight:900; margin:2px 0 8px; color:var(--navy-dark);
  }
  .guide-line {
    text-align:center; color:#7f4d17; font-size:12.8px; line-height:1.75; font-weight:700;
    max-width:90%; margin:0 auto 14px; padding:9px 14px; border-radius:999px;
    background:linear-gradient(180deg,#fff7eb,#f8efe0); border:1px solid #eddcc0;
  }
  .member-name {
    text-align:center; font-size:25px; font-weight:900; margin:10px 0 14px; color:var(--navy);
    letter-spacing:-.02em;
  }
  .score-wrap {
    margin:8px auto 18px; width:76%; background:#fff; border:1px solid var(--line);
    border-radius:16px; padding:10px; box-shadow:0 8px 22px rgba(20,49,75,.05);
  }
  table { width:100%; border-collapse:collapse; }
  .score-table th {
    background:linear-gradient(180deg,#336892,#244d70); color:#fff; border:1px solid #fff;
    padding:10px 8px; font-size:13px; font-weight:900;
  }
  .score-table td {
    background:linear-gradient(180deg,#eef5fb,#e0ecf8); border:1px solid #fff; padding:11px 8px;
    text-align:center; font-weight:900; font-size:14px; color:var(--navy-dark);
  }
  .section, .sales-focus-card, .ref-card, .coach-box {
    margin-top:14px; border:1px solid var(--line); border-radius:18px; background:#fff;
    box-shadow:0 10px 24px rgba(15,36,56,.05);
  }
  .section {
    padding:16px 16px 14px; background:linear-gradient(180deg,#ffffff 0%, #fbfdff 100%);
  }
  .section-title {
    position:relative; font-size:17px; font-weight:900; margin-bottom:12px; color:var(--navy-dark);
    padding-left:14px; letter-spacing:-.01em;
  }
  .section-title::before {
    content:""; position:absolute; left:0; top:2px; width:5px; height:20px;
    border-radius:999px; background:linear-gradient(180deg,var(--gold), var(--navy));
  }
  .bullet-list { margin:0; padding:0; list-style:none; }
  .bullet-item {
    position:relative; padding:0 0 0 16px; font-size:13.6px; line-height:1.82; margin-bottom:4px; white-space:pre-wrap;
    color:#2d3b49;
  }
  .bullet-item::before {
    content:"•"; position:absolute; left:0; top:0; font-weight:900; color:var(--blue);
  }
  .paragraph { font-size:13.7px; line-height:1.9; margin-bottom:8px; white-space:pre-wrap; color:#2f3d4b; }
  .direction-lead {
    text-align:center; font-size:18px; font-weight:900; margin:6px 0 8px; color:var(--navy-dark); letter-spacing:-.01em;
  }
  .direction-note {
    text-align:center; font-size:12.6px; line-height:1.75; color:var(--muted);
    margin:0 auto 14px; max-width:88%; padding:9px 14px; border-radius:999px;
    background:#f5f8fc; border:1px solid #e1eaf3;
  }
  .phase-strip { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:14px 0 16px; }
  .phase-box {
    border-radius:18px; padding:16px 16px 14px; text-align:left; min-height:166px;
    border:1px solid #d8e3ee; background:linear-gradient(180deg,#fbfdff,#f4f8fc);
    box-shadow:0 10px 22px rgba(20,49,75,.07);
  }
  .phase-box.phase-1 { background:linear-gradient(180deg,#f8fbff,#eef6fc); }
  .phase-box.phase-2 { background:linear-gradient(180deg,#fbfdfc,#f1f9f5); }
  .phase-box.phase-3 { background:linear-gradient(180deg,#fffdf9,#fff5eb); }
  .phase-step {
    display:inline-block; font-size:11px; font-weight:900; color:#fff; letter-spacing:.04em;
    margin-bottom:6px; padding:5px 9px; border-radius:999px; background:linear-gradient(135deg,var(--navy), var(--blue));
  }
  .phase-period { font-size:12px; font-weight:800; color:#6b7b8c; margin-bottom:8px; }
  .phase-title { font-size:15px; line-height:1.45; font-weight:900; color:var(--navy-dark); margin-bottom:6px; }
  .phase-summary { font-size:12.5px; line-height:1.68; color:#3d4b59; margin-bottom:10px; }
  .phase-tags { display:flex; flex-wrap:wrap; gap:6px; }
  .phase-tag {
    display:inline-block; padding:4px 8px; border-radius:999px; background:#ffffffd9;
    border:1px solid #dbe6f0; color:#244967; font-size:10.8px; font-weight:800;
  }
  .program-table {
    table-layout:fixed; margin-top:8px; border:1px solid var(--line-strong); border-radius:18px;
    overflow:hidden; box-shadow:0 8px 20px rgba(20,49,75,.05);
  }
  .program-table th, .program-table td {
    border:1px solid #c9d7e3; padding:12px 11px; vertical-align:top; font-size:12.5px; line-height:1.72;
    word-break:keep-all; white-space:pre-wrap;
  }
  .program-table thead th {
    background:linear-gradient(180deg,#eff5fb,#e2edf8); text-align:center; font-weight:900; color:var(--navy-dark);
  }
  .table-phase-period { display:block; margin-top:4px; font-size:11px; font-weight:700; color:#6a7c8e; }
  .program-table tbody tr:nth-child(odd) td.value-cell { background:#fcfdff; }
  .program-table tbody tr:nth-child(even) td.value-cell { background:#f8fbfe; }
  .program-table .label-cell {
    width:17%; text-align:center; background:linear-gradient(180deg,#f4f7fa,#eef3f8); font-weight:900; color:#213547;
  }
  .program-table .value-cell { width:27.666%; }
  .ref-card {
    padding:14px; background:linear-gradient(180deg,#ffffff 0%, #fbfdff 100%);
  }
  .ref-title { font-size:15px; font-weight:900; margin-bottom:10px; color:var(--navy-dark); }
  .ref-grid { display:grid; grid-template-columns:1.2fr .95fr; gap:14px; align-items:center; }
  .ref-grid.multi-ref { grid-template-columns:1.25fr .95fr; align-items:start; }
  .ref-gallery { display:grid; grid-template-columns:repeat(2, 1fr); gap:12px; }
  .ref-item { display:flex; flex-direction:column; gap:8px; }
  .ref-image {
    min-height:228px; border:1px dashed #bfd0df; background:linear-gradient(180deg,#fbfdff,#f2f7fc);
    border-radius:14px; display:flex; align-items:center; justify-content:center; overflow:hidden; padding:8px;
  }
  .ref-image.ref-image-multi { min-height:160px; }
  .ref-image img { width:100%; max-height:320px; object-fit:contain; border-radius:10px; }
  .ref-item-caption {
    min-height:42px; padding:8px 10px; border-radius:12px; background:linear-gradient(180deg,#ffffff,#f7fafd);
    border:1px solid #dde7f0; color:#304254; font-size:11.8px; line-height:1.6; text-align:center;
  }
  .ref-placeholder { color:#7b8a98; font-size:13px; text-align:center; padding:20px; line-height:1.8; }
  .ref-caption {
    font-size:13px; line-height:1.82; color:#364555; white-space:pre-wrap; padding:10px 0;
  }
  .extra-title { font-size:17px; font-weight:900; margin:18px 0 9px; color:var(--navy-dark); }
  .extra-table {
    border:1px solid #cbd9e6; border-radius:16px; overflow:hidden; box-shadow:0 8px 18px rgba(20,49,75,.04);
  }
  .extra-table th, .extra-table td {
    border:1px solid #c8d6e3; padding:10px; font-size:13px; line-height:1.7; vertical-align:top;
  }
  .extra-table th { background:linear-gradient(180deg,#edf4fb,#dfeaf6); text-align:center; font-weight:900; color:var(--navy-dark); }
  .coach-box {
    padding:16px; background:linear-gradient(135deg,#fbfdff 0%, #f5f8fc 100%); position:relative;
  }
  .coach-box::after {
    content:""; position:absolute; right:18px; top:16px; width:44px; height:44px; border-radius:50%;
    background:radial-gradient(circle, rgba(202,166,106,.18) 0%, rgba(202,166,106,0) 70%);
  }
  .coach-title { font-size:17px; font-weight:900; margin-bottom:8px; color:var(--navy-dark); }
  .coach-letter { font-size:13.8px; line-height:1.95; white-space:pre-wrap; color:#2d3d4d; }
  .footer-meta {
    margin-top:14px; text-align:right; font-size:11px; color:#7a8694;
    letter-spacing:.02em;
  }
  .tag {
    display:inline-block; padding:5px 10px; border-radius:999px; background:linear-gradient(180deg,#f3f7fc,#e8f1fa);
    color:var(--navy); font-size:11.6px; font-weight:800; margin-right:7px; margin-bottom:7px; border:1px solid #d8e4ef;
  }
  .mini-boxes { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:10px; }
  .mini-box {
    border:1px solid #dce6ef; background:linear-gradient(180deg,#ffffff,#f7fafd); padding:10px 11px;
    border-radius:14px; font-size:12.2px; line-height:1.72; box-shadow:0 6px 14px rgba(20,49,75,.04);
  }
  .sales-focus-card {
    padding:16px; background:linear-gradient(180deg,#ffffff 0%, #f8fbfe 100%);
    border:1px solid #d8e3ef;
  }
  .sales-problem-chip {
    display:inline-block; padding:6px 11px; border-radius:999px; background:linear-gradient(180deg,#eef5fc,#e4eef8);
    color:var(--navy); font-size:12px; font-weight:900; margin-bottom:10px; border:1px solid #d8e4ef;
  }
  .compare-title { font-size:15px; font-weight:900; margin:8px 0 11px; color:var(--navy-dark); }
  .compare-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .compare-pane {
    border:1px solid #dbe5ef; border-radius:16px; padding:13px; background:#fff;
    box-shadow:0 8px 18px rgba(20,49,75,.04);
  }
  .compare-pane.good { background:linear-gradient(180deg,#fbfefa,#f5fbf7); }
  .compare-pane.bad { background:linear-gradient(180deg,#fffdfc,#fff7f5); }
  .compare-head { font-size:13.5px; font-weight:900; margin-bottom:9px; }
  .compare-head.good { color:#2d7a49; }
  .compare-head.bad { color:#be4c3b; }
  .sales-columns { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:12px; }
  .sales-box {
    border:1px solid #dce5ee; border-radius:16px; padding:11px; background:#fff;
    box-shadow:0 8px 18px rgba(20,49,75,.04);
  }
  .sales-box-title { font-size:13px; font-weight:900; margin-bottom:7px; color:var(--navy-dark); }
  .sales-list { margin:0; padding-left:18px; }
  .sales-list li { margin-bottom:6px; font-size:12.6px; line-height:1.72; color:#31404f; }
  .talk-box {
    margin-top:12px; border:1px solid #eadcc6; background:linear-gradient(180deg,#fffdf9,#fff7ee);
    border-radius:16px; padding:13px;
  }
  .talk-line { font-size:13px; line-height:1.85; margin-bottom:6px; white-space:pre-wrap; color:#374455; }
  .coach-takeaway { margin-top:8px; font-size:12.3px; line-height:1.75; color:#5c6774; }
  @media print {
    html, body {
      background:#ffffff !important;
      padding:0;
      -webkit-print-color-adjust:exact !important;
      print-color-adjust:exact !important;
    }
    .sheet {
      box-shadow:none;
      margin:0;
      border-radius:0;
      border:1px solid #d8e3ee;
      background:#ffffff !important;
    }
    .sheet::before {
      height:5px;
      background:linear-gradient(90deg,var(--navy), var(--blue), var(--gold)) !important;
    }
    .topbar {
      background:var(--navy) !important;
      color:#ffffff !important;
      box-shadow:none !important;
    }
    .guide-line {
      background:#fff7eb !important;
      border:1px solid #eddcc0 !important;
      color:#7f4d17 !important;
    }
    .score-wrap,
    .section,
    .sales-focus-card,
    .ref-card,
    .coach-box,
    .sales-box,
    .compare-pane,
    .mini-box,
    .phase-box,
    .talk-box,
    .extra-table,
    .program-table,
    .ref-image,
    .ref-item-caption {
      box-shadow:none !important;
    }
    .score-table th {
      background:#244d70 !important;
      color:#ffffff !important;
    }
    .score-table td {
      background:#e7f0f8 !important;
      color:var(--navy-dark) !important;
    }
    .section,
    .ref-card,
    .coach-box,
    .sales-focus-card {
      background:#ffffff !important;
      border:1px solid #d8e3ee !important;
    }
    .phase-box.phase-1 { background:#eef6fc !important; }
    .phase-box.phase-2 { background:#f1f9f5 !important; }
    .phase-box.phase-3 { background:#fff5eb !important; }
    .phase-step {
      background:var(--navy) !important;
      color:#ffffff !important;
    }
    .program-table thead th,
    .extra-table th {
      background:#e5eef7 !important;
      color:var(--navy-dark) !important;
    }
    .program-table .label-cell {
      background:#f0f4f8 !important;
      color:#213547 !important;
    }
    .program-table tbody tr:nth-child(odd) td.value-cell { background:#fcfdff !important; }
    .program-table tbody tr:nth-child(even) td.value-cell { background:#f8fbfe !important; }
    .sales-problem-chip,
    .tag {
      background:#edf4fb !important;
      color:var(--navy) !important;
      border:1px solid #d8e4ef !important;
    }
    .talk-box {
      background:#fff7ee !important;
      border:1px solid #eadcc6 !important;
    }
    .compare-pane.good { background:#f5fbf7 !important; }
    .compare-pane.bad { background:#fff7f5 !important; }
    .footer-meta { color:#7a8694 !important; }
  }
</style>
"""

HTML_BASE_HEAD = """<!DOCTYPE html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>{{ css }}</head><body>"""
HTML_BASE_FOOT = "</body></html>"

TEMPLATE_A = Template(
    HTML_BASE_HEAD
    + r"""
<div class="sheet">
  <div class="topbar">{{ header.title }}</div>
  <div class="trainer-line">{{ header.trainer_line }}</div>
  <div class="guide-line">{{ header.guide_text }}</div>
  <div class="member-name">{{ header.member_display_name }}</div>

  <div class="score-wrap">
    <table class="score-table">
      <thead><tr>{% for h in summary_table.headers %}<th>{{ h }}</th>{% endfor %}</tr></thead>
      <tbody><tr>{% for v in summary_table["values"] %}<td>{{ v }}</td>{% endfor %}</tr></tbody>
    </table>
  </div>

  <div class="section">
    <div class="section-title">{{ section_1.title }}</div>
    <ul class="bullet-list">{% for item in section_1["items"] %}<li class="bullet-item">{{ item }}</li>{% endfor %}</ul>
  </div>

  <div class="section">
    <div class="section-title">{{ section_2.title }}</div>
    <ul class="bullet-list">{% for item in section_2["items"] %}<li class="bullet-item">{{ item }}</li>{% endfor %}</ul>
  </div>

  <div class="section">
    <div class="section-title">{{ section_3.title }}</div>
    {% for p in section_3.paragraphs %}<div class="paragraph">{{ p }}</div>{% endfor %}
  </div>

  <div class="sales-focus-card">
    <div class="section-title">{{ sales_focus.title }}</div>
    <div class="sales-problem-chip">핵심 이슈: {{ sales_focus.problem_name }}</div>
    <div class="paragraph">{{ sales_focus.problem_summary }}</div>
    <div class="compare-title">{{ sales_focus.compare_title }}</div>
    <div class="compare-grid">
      <div class="compare-pane good">
        <div class="compare-head good">{{ sales_focus.normal_label }}</div>
        <ul class="sales-list">{% for item in sales_focus.normal_points %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="compare-pane bad">
        <div class="compare-head bad">{{ sales_focus.problem_label }}</div>
        <ul class="sales-list">{% for item in sales_focus.problem_points %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
    </div>
    <div class="sales-columns">
      <div class="sales-box">
        <div class="sales-box-title">문제 원인</div>
        <ul class="sales-list">{% for item in sales_focus.causes %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="sales-box">
        <div class="sales-box-title">방치 시 위험</div>
        <ul class="sales-list">{% for item in sales_focus.risks %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="sales-box">
        <div class="sales-box-title">왜 PT가 필요한가</div>
        <ul class="sales-list">{% for item in sales_focus.pt_need %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
    </div>
    <div class="talk-box">
      <div class="sales-box-title">상담 멘트</div>
      {% for line in sales_focus.sales_talk %}<div class="talk-line">{{ line }}</div>{% endfor %}
      <div class="coach-takeaway">{{ sales_focus.coach_takeaway }}</div>
    </div>
  </div>

  {% if reference_block.image_items or reference_block.image_data_list or reference_block.image_data %}
  <div class="ref-card">
    <div class="ref-title">{{ reference_block.title }}</div>
    {% set ref_items = reference_block.image_items if reference_block.image_items else ([{"src": reference_block.image_data, "caption": ""}] if reference_block.image_data and not reference_block.image_data_list else []) %}
    {% if not ref_items and reference_block.image_data_list %}
      {% set ref_items = [] %}
      {% for img in reference_block.image_data_list[:4] %}
        {% set _ = ref_items.append({"src": img, "caption": (reference_block.image_captions[loop.index0] if reference_block.image_captions and reference_block.image_captions|length > loop.index0 else "")}) %}
      {% endfor %}
    {% endif %}
    <div class="ref-grid {% if ref_items|length > 1 %}multi-ref{% endif %}">
      {% if ref_items|length > 1 %}
      <div class="ref-gallery">
        {% for item in ref_items[:4] %}
        <div class="ref-item">
          <div class="ref-image ref-image-multi"><img src="{{ item.src }}" alt="참고 이미지 {{ loop.index }}"></div>
          {% if item.caption %}<div class="ref-item-caption">{{ item.caption }}</div>{% endif %}
        </div>
        {% endfor %}
      </div>
      {% else %}
      <div class="ref-item">
        <div class="ref-image">
          <img src="{{ ref_items[0].src if ref_items else reference_block.image_data }}" alt="참고 이미지">
        </div>
        {% if ref_items and ref_items[0].caption %}<div class="ref-item-caption">{{ ref_items[0].caption }}</div>{% endif %}
      </div>
      {% endif %}
      <div class="ref-caption">{{ reference_block.caption }}

초기 단계에서는 몸의 정렬, 관절 가동 범위, 불필요한 보상 패턴을 먼저 인식하고 조절하는 것이 중요합니다.</div>
    </div>
  </div>
  {% endif %}

  <div class="section">
    <div class="section-title">{{ direction_section.title }}</div>
    <div class="direction-lead">{{ direction_section.lead }}</div>
    <div class="direction-note">{{ direction_section.guide }}</div>
    <div class="phase-strip">{% for card in direction_section.phase_cards %}<div class="phase-box phase-{{ loop.index }}"><div class="phase-step">{{ card.step }}</div><div class="phase-period">{{ card.period }}</div><div class="phase-title">{{ card.title }}</div><div class="phase-summary">{{ card.summary }}</div><div class="phase-tags">{% for tag in card.tags %}<span class="phase-tag">{{ tag }}</span>{% endfor %}</div></div>{% endfor %}</div>
    <table class="program-table">
      <thead><tr><th>구분</th>{% for card in direction_section.phase_cards %}<th>{{ card.step }}<span class="table-phase-period">{{ card.period }}</span></th>{% endfor %}</tr></thead>
      <tbody>
      {% for row in direction_section.rows %}
        <tr><td class="label-cell">{{ row.label }}</td><td class="value-cell">{{ row.v1 }}</td><td class="value-cell">{{ row.v2 }}</td><td class="value-cell">{{ row.v3 }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>

  <div class="coach-box">
    <div class="coach-title">{{ closing.title }}</div>
    <div class="coach-letter">{{ closing.letter }}</div>
  </div>

  <div class="footer-meta">A형 · 생성일시 {{ meta.created_at }}</div>
</div>
"""
    + HTML_BASE_FOOT
)

TEMPLATE_B = Template(
    HTML_BASE_HEAD
    + r"""
<div class="sheet">
  <div class="topbar">{{ header.title }}</div>
  <div class="trainer-line">{{ header.trainer_line }}</div>
  <div class="guide-line">{{ header.guide_text }}</div>
  <div class="member-name">{{ header.member_display_name }}</div>

  <div class="score-wrap">
    <table class="score-table">
      <thead><tr>{% for h in summary_table.headers %}<th>{{ h }}</th>{% endfor %}</tr></thead>
      <tbody><tr>{% for v in summary_table["values"] %}<td>{{ v }}</td>{% endfor %}</tr></tbody>
    </table>
  </div>

  <div class="section">
    <div class="section-title">{{ section_1.title }}</div>
    <ul class="bullet-list">{% for item in section_1["items"] %}<li class="bullet-item">{{ item }}</li>{% endfor %}</ul>
  </div>

  <div class="section">
    <div class="section-title">{{ section_2.title }}</div>
    <ul class="bullet-list">{% for item in section_2["items"] %}<li class="bullet-item">{{ item }}</li>{% endfor %}</ul>
  </div>

  <div class="section">
    <div class="section-title">{{ section_3.title }}</div>
    {% for p in section_3.paragraphs %}<div class="paragraph">{{ p }}</div>{% endfor %}
  </div>

  <div class="sales-focus-card">
    <div class="section-title">{{ sales_focus.title }}</div>
    <div class="sales-problem-chip">핵심 이슈: {{ sales_focus.problem_name }}</div>
    <div class="paragraph">{{ sales_focus.problem_summary }}</div>
    <div class="compare-title">{{ sales_focus.compare_title }}</div>
    <div class="compare-grid">
      <div class="compare-pane good">
        <div class="compare-head good">{{ sales_focus.normal_label }}</div>
        <ul class="sales-list">{% for item in sales_focus.normal_points %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="compare-pane bad">
        <div class="compare-head bad">{{ sales_focus.problem_label }}</div>
        <ul class="sales-list">{% for item in sales_focus.problem_points %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
    </div>
    <div class="sales-columns">
      <div class="sales-box">
        <div class="sales-box-title">문제 원인</div>
        <ul class="sales-list">{% for item in sales_focus.causes %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="sales-box">
        <div class="sales-box-title">방치 시 위험</div>
        <ul class="sales-list">{% for item in sales_focus.risks %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="sales-box">
        <div class="sales-box-title">왜 PT가 필요한가</div>
        <ul class="sales-list">{% for item in sales_focus.pt_need %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
    </div>
    <div class="talk-box">
      <div class="sales-box-title">상담 멘트</div>
      {% for line in sales_focus.sales_talk %}<div class="talk-line">{{ line }}</div>{% endfor %}
      <div class="coach-takeaway">{{ sales_focus.coach_takeaway }}</div>
    </div>
  </div>

  <div class="ref-card">
    <div class="ref-title">{{ reference_block.title }}</div>
    <div class="mini-boxes">
      <div class="mini-box">
        <strong>핵심 원칙</strong><br>
        극단적인 식단보다 유지 가능한 기준을 만드는 것이 가장 중요합니다.
      </div>
      <div class="mini-box">
        <strong>운동 원칙</strong><br>
        PT 수업 + 개인 유산소 + 일상 활동량을 함께 관리해야 체지방 변화가 커집니다.
      </div>
      <div class="mini-box">
        <strong>생활 원칙</strong><br>
        수면, 음주, 야식, 주말 패턴까지 결과에 직접 영향을 줍니다.
      </div>
    </div>
    {% if reference_block.image_items or reference_block.image_data_list or reference_block.image_data %}
    {% set ref_items = reference_block.image_items if reference_block.image_items else ([{"src": reference_block.image_data, "caption": ""}] if reference_block.image_data and not reference_block.image_data_list else []) %}
    {% if not ref_items and reference_block.image_data_list %}
      {% set ref_items = [] %}
      {% for img in reference_block.image_data_list[:4] %}
        {% set _ = ref_items.append({"src": img, "caption": (reference_block.image_captions[loop.index0] if reference_block.image_captions and reference_block.image_captions|length > loop.index0 else "")}) %}
      {% endfor %}
    {% endif %}
    <div class="ref-grid {% if ref_items|length > 1 %}multi-ref{% endif %}" style="margin-top:10px;">
      {% if ref_items|length > 1 %}
      <div class="ref-gallery">
        {% for item in ref_items[:4] %}
        <div class="ref-item">
          <div class="ref-image ref-image-multi"><img src="{{ item.src }}" alt="참고 이미지 {{ loop.index }}"></div>
          {% if item.caption %}<div class="ref-item-caption">{{ item.caption }}</div>{% endif %}
        </div>
        {% endfor %}
      </div>
      {% else %}
      <div class="ref-item">
        <div class="ref-image">
          <img src="{{ ref_items[0].src if ref_items else reference_block.image_data }}" alt="참고 이미지">
        </div>
        {% if ref_items and ref_items[0].caption %}<div class="ref-item-caption">{{ ref_items[0].caption }}</div>{% endif %}
      </div>
      {% endif %}
      <div class="ref-caption">{{ reference_block.caption }}

이 참고 이미지는 회원님의 현재 패턴과 개선 방향을 비교해 이해시키는 설명용 자료입니다.</div>
    </div>
    {% endif %}
  </div>

  <div class="section">
    <div class="section-title">{{ direction_section.title }}</div>
    <div class="direction-lead">{{ direction_section.lead }}</div>
    <div class="direction-note">{{ direction_section.guide }}</div>
    <div class="phase-strip">{% for card in direction_section.phase_cards %}<div class="phase-box phase-{{ loop.index }}"><div class="phase-step">{{ card.step }}</div><div class="phase-period">{{ card.period }}</div><div class="phase-title">{{ card.title }}</div><div class="phase-summary">{{ card.summary }}</div><div class="phase-tags">{% for tag in card.tags %}<span class="phase-tag">{{ tag }}</span>{% endfor %}</div></div>{% endfor %}</div>
    <table class="program-table">
      <thead><tr><th>구분</th>{% for card in direction_section.phase_cards %}<th>{{ card.step }}<span class="table-phase-period">{{ card.period }}</span></th>{% endfor %}</tr></thead>
      <tbody>
      {% for row in direction_section.rows %}
        <tr><td class="label-cell">{{ row.label }}</td><td class="value-cell">{{ row.v1 }}</td><td class="value-cell">{{ row.v2 }}</td><td class="value-cell">{{ row.v3 }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>

  {% if extra_table.show %}
  <div class="extra-title">{{ extra_table.title }}</div>
  <table class="extra-table">
    <thead><tr>{% for h in extra_table.headers %}<th>{{ h }}</th>{% endfor %}</tr></thead>
    <tbody>
    {% for row in extra_table.rows %}
      <tr><td style="width:20%; font-weight:700; text-align:center;">{{ row[0] }}</td><td>{{ row[1] }}</td></tr>
    {% endfor %}
    </tbody>
  </table>
  {% endif %}

  <div class="coach-box">
    <div class="coach-title">{{ closing.title }}</div>
    <div class="coach-letter">{{ closing.letter }}</div>
  </div>

  <div class="footer-meta">B형 · 생성일시 {{ meta.created_at }}</div>
</div>
"""
    + HTML_BASE_FOOT
)

TEMPLATE_C = Template(
    HTML_BASE_HEAD
    + r"""
<div class="sheet">
  <div class="topbar">{{ header.title }}</div>
  <div class="trainer-line">{{ header.trainer_line }}</div>
  <div class="guide-line">{{ header.guide_text }}</div>
  <div class="member-name">{{ header.member_display_name }}</div>

  <div class="score-wrap">
    <table class="score-table">
      <thead><tr>{% for h in summary_table.headers %}<th>{{ h }}</th>{% endfor %}</tr></thead>
      <tbody><tr>{% for v in summary_table["values"] %}<td>{{ v }}</td>{% endfor %}</tr></tbody>
    </table>
  </div>

  <div class="section">
    <div class="section-title">{{ section_1.title }}</div>
    <ul class="bullet-list">{% for item in section_1["items"] %}<li class="bullet-item">{{ item }}</li>{% endfor %}</ul>
  </div>

  <div class="section">
    <div class="section-title">{{ section_2.title }}</div>
    <div>
      {% for item in section_2["items"] %}<span class="tag">{{ item }}</span>{% endfor %}
    </div>
  </div>

  <div class="section">
    <div class="section-title">{{ section_3.title }}</div>
    {% for p in section_3.paragraphs %}<div class="paragraph">{{ p }}</div>{% endfor %}
  </div>

  <div class="sales-focus-card">
    <div class="section-title">{{ sales_focus.title }}</div>
    <div class="sales-problem-chip">핵심 이슈: {{ sales_focus.problem_name }}</div>
    <div class="paragraph">{{ sales_focus.problem_summary }}</div>
    <div class="compare-title">{{ sales_focus.compare_title }}</div>
    <div class="compare-grid">
      <div class="compare-pane good">
        <div class="compare-head good">{{ sales_focus.normal_label }}</div>
        <ul class="sales-list">{% for item in sales_focus.normal_points %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="compare-pane bad">
        <div class="compare-head bad">{{ sales_focus.problem_label }}</div>
        <ul class="sales-list">{% for item in sales_focus.problem_points %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
    </div>
    <div class="sales-columns">
      <div class="sales-box">
        <div class="sales-box-title">문제 원인</div>
        <ul class="sales-list">{% for item in sales_focus.causes %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="sales-box">
        <div class="sales-box-title">방치 시 위험</div>
        <ul class="sales-list">{% for item in sales_focus.risks %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
      <div class="sales-box">
        <div class="sales-box-title">왜 PT가 필요한가</div>
        <ul class="sales-list">{% for item in sales_focus.pt_need %}<li>{{ item }}</li>{% endfor %}</ul>
      </div>
    </div>
    <div class="talk-box">
      <div class="sales-box-title">상담 멘트</div>
      {% for line in sales_focus.sales_talk %}<div class="talk-line">{{ line }}</div>{% endfor %}
      <div class="coach-takeaway">{{ sales_focus.coach_takeaway }}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">{{ direction_section.title }}</div>
    <div class="direction-lead">{{ direction_section.lead }}</div>
    <div class="direction-note">{{ direction_section.guide }}</div>
    <div class="phase-strip">{% for card in direction_section.phase_cards %}<div class="phase-box phase-{{ loop.index }}"><div class="phase-step">{{ card.step }}</div><div class="phase-period">{{ card.period }}</div><div class="phase-title">{{ card.title }}</div><div class="phase-summary">{{ card.summary }}</div><div class="phase-tags">{% for tag in card.tags %}<span class="phase-tag">{{ tag }}</span>{% endfor %}</div></div>{% endfor %}</div>
    <table class="program-table">
      <thead><tr><th>구분</th>{% for card in direction_section.phase_cards %}<th>{{ card.step }}<span class="table-phase-period">{{ card.period }}</span></th>{% endfor %}</tr></thead>
      <tbody>
      {% for row in direction_section.rows %}
        <tr><td class="label-cell">{{ row.label }}</td><td class="value-cell">{{ row.v1 }}</td><td class="value-cell">{{ row.v2 }}</td><td class="value-cell">{{ row.v3 }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>

  {% if extra_table.show %}
  <div class="extra-title">{{ extra_table.title }}</div>
  <table class="extra-table">
    <thead><tr>{% for h in extra_table.headers %}<th>{{ h }}</th>{% endfor %}</tr></thead>
    <tbody>
    {% for row in extra_table.rows %}
      <tr><td style="width:22%; font-weight:700; text-align:center;">{{ row[0] }}</td><td>{{ row[1] }}</td></tr>
    {% endfor %}
    </tbody>
  </table>
  {% endif %}

  {% if reference_block.image_items or reference_block.image_data_list or reference_block.image_data %}
  <div class="ref-card">
    <div class="ref-title">{{ reference_block.title }}</div>
    {% set ref_items = reference_block.image_items if reference_block.image_items else ([{"src": reference_block.image_data, "caption": ""}] if reference_block.image_data and not reference_block.image_data_list else []) %}
    {% if not ref_items and reference_block.image_data_list %}
      {% set ref_items = [] %}
      {% for img in reference_block.image_data_list[:4] %}
        {% set _ = ref_items.append({"src": img, "caption": (reference_block.image_captions[loop.index0] if reference_block.image_captions and reference_block.image_captions|length > loop.index0 else "")}) %}
      {% endfor %}
    {% endif %}
    <div class="ref-grid {% if ref_items|length > 1 %}multi-ref{% endif %}">
      {% if ref_items|length > 1 %}
      <div class="ref-gallery">
        {% for item in ref_items[:4] %}
        <div class="ref-item">
          <div class="ref-image ref-image-multi"><img src="{{ item.src }}" alt="참고 이미지 {{ loop.index }}"></div>
          {% if item.caption %}<div class="ref-item-caption">{{ item.caption }}</div>{% endif %}
        </div>
        {% endfor %}
      </div>
      {% else %}
      <div class="ref-item">
        <div class="ref-image">
          <img src="{{ ref_items[0].src if ref_items else reference_block.image_data }}" alt="참고 이미지">
        </div>
        {% if ref_items and ref_items[0].caption %}<div class="ref-item-caption">{{ ref_items[0].caption }}</div>{% endif %}
      </div>
      {% endif %}
      <div class="ref-caption">핵심 동작을 너무 많이 넣기보다, 회원님이 반복해서 기억해야 할 포인트 중심으로 안내하는 구조입니다.</div>
    </div>
  </div>
  {% endif %}

  <div class="coach-box">
    <div class="coach-title">{{ closing.title }}</div>
    <div class="coach-letter">{{ closing.letter }}</div>
  </div>

  <div class="footer-meta">C형 · 생성일시 {{ meta.created_at }}</div>
</div>
"""
    + HTML_BASE_FOOT
)


def render_html(report_data: Dict[str, Any]) -> str:
    template_type = report_data.get("meta", {}).get("template_type", "A")
    payload = deepcopy(report_data)
    payload["css"] = COMMON_CSS
    if template_type == "B":
        return TEMPLATE_B.render(**payload)
    if template_type == "C":
        return TEMPLATE_C.render(**payload)
    return TEMPLATE_A.render(**payload)


def html_to_pdf_bytes(html: str) -> Optional[bytes]:
    if not WEASYPRINT_AVAILABLE:
        return None
    try:
        return HTML(string=html).write_pdf()
    except Exception:
        return None


def refresh_rendered_report(report: Dict[str, Any]) -> None:
    html = render_html(report)
    st.session_state["report_json"] = report
    st.session_state["report_html"] = html
    st.session_state["report_pdf"] = html_to_pdf_bytes(html)


def direction_rows_to_editor_df(rows: List[Dict[str, str]]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "구분": row.get("label", ""),
            "1단계": row.get("v1", ""),
            "2단계": row.get("v2", ""),
            "3단계": row.get("v3", ""),
        }
        for row in rows
    ])


def direction_editor_df_to_rows(df: pd.DataFrame, fallback_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    records = df.to_dict("records") if hasattr(df, "to_dict") else []
    output: List[Dict[str, str]] = []
    for idx, row in enumerate(records):
        fallback = fallback_rows[idx] if idx < len(fallback_rows) else {"label": "", "v1": "", "v2": "", "v3": ""}
        output.append({
            "label": safe_text(row.get("구분")) or fallback.get("label", ""),
            "v1": safe_text(row.get("1단계")) or fallback.get("v1", ""),
            "v2": safe_text(row.get("2단계")) or fallback.get("v2", ""),
            "v3": safe_text(row.get("3단계")) or fallback.get("v3", ""),
        })
    return output or fallback_rows


# ============================================================
# 입력 UI
# ============================================================
with st.sidebar:
    st.title("💪🏻 기본 설정")
    trainer_name = st.text_input("트레이너 성함", value=DEFAULT_TRAINER_NAME)
    gym_name = st.text_input("소속 지점", value=DEFAULT_GYM_NAME)
    model_name = st.text_input("텍스트 생성 모델", value="gpt-4o")
    manual_api_key = st.text_input("OpenAI API 키 직접 입력 (문제 있을 때만)", value="", type="password", help="secrets.toml 인식이 안 될 때 여기 붙여넣으면 이 실행에서 바로 사용됩니다.")
    if manual_api_key:
        st.success("이 실행에서는 직접 입력한 API 키를 우선 사용합니다.")
    image_enabled = st.checkbox("참고 이미지 자동생성", value=False)
    manual_reference_images = st.file_uploader(
        "참고 이미지 직접 업로드 (선택, 최대 4장)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        help="직접 업로드하면 AI 자동생성보다 우선 적용됩니다. 최대 4장까지 업로드할 수 있습니다.",
    )
    manual_reference_captions = []
    if manual_reference_images:
        if len(manual_reference_images) > 4:
            st.warning("업로드 이미지는 최대 4장까지 반영됩니다. 앞의 4장만 사용합니다.")
            manual_reference_images = manual_reference_images[:4]
        st.success(f"직접 업로드 이미지 {len(manual_reference_images)}장 선택됨")
        for idx, uploaded_image in enumerate(manual_reference_images, start=1):
            st.image(uploaded_image, caption=f"업로드 이미지 미리보기 {idx}", use_container_width=True)
            caption_value = st.text_input(
                f"이미지 {idx} 캡션",
                value="",
                key=f"manual_reference_caption_{idx}",
                placeholder="예: 정면 자세 / 측면 자세 / 전완·견갑 참고 / 체형 비교 포인트",
            )
            manual_reference_captions.append(caption_value.strip())
        st.caption("직접 업로드한 이미지가 우선 사용됩니다. 문서 생성 시 최대 4장까지 2x2 그리드로 보고서 안에 반영됩니다.")
    else:
        st.caption("직접 업로드한 이미지가 없으면 AI가 상세 소견/통증/생활습관/식습관/직업 특성 메모를 반영해 참고 이미지를 자동 생성합니다(체크 시).")

    st.markdown("---")
    template_label = st.radio("템플릿 선택", list(TEMPLATE_LABELS.keys()), index=0)
    template_mode = TEMPLATE_LABELS[template_label]

    st.caption("AUTO는 입력값을 보고 A/B/C 중 자동 분기합니다.")
    st.markdown("---")
    st.subheader("💪🏻회원 기본정보")
    member_name = st.text_input("회원 성함", placeholder="예: 정대훈")
    gender = st.radio("성별", ["남성", "여성"], horizontal=True)
    age = st.number_input("나이", min_value=10, max_value=90, value=30)
    session_plan = st.selectbox("기간(횟수)", SESSION_OPTIONS, index=2)
    goal_focus = st.selectbox("주요 목표", ["체형교정", "다이어트", "근력향상", "통증완화", "습관형성"], index=0)

st.markdown(
    """
    <div class="premium-hero">
      <div class="premium-kicker">PREMIUM PT SALES REPORT BUILDER</div>
      <h1>PT 세일즈 자료 생성기</h1>
      <p>회원 상태 분석, 설득 포인트, 단계별 로드맵을 한 번에 정리합니다.</p>
      <div class="premium-badges">
        <span class="premium-badge">회원 맞춤 분석</span>
        <span class="premium-badge">즉시 수정 가능</span>
        <span class="premium-badge">로드맵 자동 반영</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("샘플 10개 HWP 분석 요약 보기", expanded=False):
    st.markdown("### 공통 레이아웃")
    for item in HWP_LAYOUT_ANALYSIS["공통"]:
        st.write(f"- {item}")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### A형")
        st.write(HWP_LAYOUT_ANALYSIS["A"]["name"])
        st.write("샘플:", ", ".join(HWP_LAYOUT_ANALYSIS["A"]["samples"]))
        for f in HWP_LAYOUT_ANALYSIS["A"]["features"]:
            st.write(f"- {f}")
    with c2:
        st.markdown("### B형")
        st.write(HWP_LAYOUT_ANALYSIS["B"]["name"])
        st.write("샘플:", ", ".join(HWP_LAYOUT_ANALYSIS["B"]["samples"]))
        for f in HWP_LAYOUT_ANALYSIS["B"]["features"]:
            st.write(f"- {f}")
    with c3:
        st.markdown("### C형")
        st.write(HWP_LAYOUT_ANALYSIS["C"]["name"])
        st.write("샘플:", ", ".join(HWP_LAYOUT_ANALYSIS["C"]["samples"]))
        for f in HWP_LAYOUT_ANALYSIS["C"]["features"]:
            st.write(f"- {f}")

st.subheader("1) 체성분 / 인바디")
col1, col2, col3 = st.columns(3)
with col1:
    height = st.number_input("신장(cm)", min_value=100.0, max_value=230.0, value=170.0, step=0.1)
    weight = st.number_input("현재 체중(kg)", min_value=20.0, max_value=250.0, value=70.0, step=0.1)
with col2:
    muscle = st.number_input("골격근량(kg)", min_value=5.0, max_value=80.0, value=30.0, step=0.1)
    fat_mass = st.number_input("체지방량(kg)", min_value=1.0, max_value=100.0, value=15.0, step=0.1)
with col3:
    pbf = st.number_input("체지방률(%)", min_value=1.0, max_value=70.0, value=20.0, step=0.1)
    visceral_note = st.text_input("복부/내장지방 참고 메모", placeholder="예: 복부비만 경향, 내장지방 레벨 높음")

st.subheader("2) 기초 능력치")
a1, a2, a3, a4 = st.columns(4)
with a1:
    score_strength = st.select_slider("근력", options=ABILITY_OPTIONS, value="중")
with a2:
    score_endurance = st.select_slider("지구력", options=ABILITY_OPTIONS, value="중")
with a3:
    score_mobility = st.select_slider("가동성", options=ABILITY_OPTIONS, value="중")
with a4:
    score_flexibility = st.select_slider("유연성", options=ABILITY_OPTIONS, value="중")

st.subheader("3) 트레이너 진단")
st.caption("강점/단점은 복수 선택하고, 기타 내용은 직접 입력해 세일즈 설득 포인트를 더할 수 있습니다.")
left, right = st.columns(2)
with left:
    strengths_selected = st.multiselect(
        "현재의 강점 (복수 선택)",
        options=STRENGTH_OPTIONS,
        default=["비율이 좋음", "피드백 습득력이 좋음", "운동 의지가 강함"],
        help="여러 개 선택 가능합니다.",
    )
    strengths_extra = st.text_area(
        "강점 기타 (한 줄에 하나씩)",
        placeholder="예: 스쿼트 패턴 이해가 빠름\n상담 시 반응이 좋음",
        height=120,
    )
with right:
    weaknesses_selected = st.multiselect(
        "현재의 단점 / 교정 포인트 (복수 선택)",
        options=WEAKNESS_OPTIONS,
        default=["거북목 경향", "코어 안정성 부족", "근지구력 부족"],
        help="여러 개 선택 가능합니다.",
    )
    weaknesses_extra = st.text_area(
        "단점 기타 / 추가 교정 포인트 (한 줄에 하나씩)",
        placeholder="예: 스쿼트 시 무릎 안쪽 붕괴\n좌우 밸런스 차이 큼",
        height=120,
    )

special_notes = st.text_area(
    "상세 소견 / 통증 / 생활습관 / 식습관 / 직업 특성 / 세일즈 메모",
    placeholder="예: 오래 앉아있는 직업, 잦은 야식, 라운드숄더, 허리 통증, 하체 부종, 운동 경험 부족, 등록 망설이는 이유 등",
    height=150,
)


# ============================================================
# 입력 수집 / 검증
# ============================================================
def collect_input() -> Dict[str, Any]:
    strengths = list(dict.fromkeys(strengths_selected + split_lines(strengths_extra)))
    weaknesses = list(dict.fromkeys(weaknesses_selected + split_lines(weaknesses_extra)))
    return {
        "trainer_name": safe_text(trainer_name) or DEFAULT_TRAINER_NAME,
        "gym_name": safe_text(gym_name) or DEFAULT_GYM_NAME,
        "member_name": normalize_name(member_name),
        "gender": gender,
        "age": int(age),
        "session_plan": session_plan,
        "goal_focus": goal_focus,
        "height": float(height),
        "weight": float(weight),
        "muscle": float(muscle),
        "fat_mass": float(fat_mass),
        "pbf": float(pbf),
        "visceral_note": safe_text(visceral_note),
        "template_mode": template_mode,
        "scores": {
            "근력": score_strength,
            "지구력": score_endurance,
            "가동성": score_mobility,
            "유연성": score_flexibility,
        },
        "strengths": strengths or STRENGTH_OPTIONS[:3],
        "weaknesses": weaknesses or WEAKNESS_OPTIONS[:3],
        "special_notes": split_lines(special_notes) + ([visceral_note] if safe_text(visceral_note) else []),
    }


def validate(member: Dict[str, Any]) -> List[str]:
    errors = []
    if not member["member_name"]:
        errors.append("회원 성함을 입력해주세요.")
    if len(member["member_name"]) < 2:
        errors.append("회원 이름은 2자 이상으로 입력해주세요.")
    return errors


btn1, btn2, btn3 = st.columns([1, 1, 2])
with btn1:
    generate_clicked = st.button("🚀 세일즈 자료 생성", use_container_width=True)
with btn2:
    demo_clicked = st.button("🧪 데모 값으로 생성", use_container_width=True)
with btn3:
    st.info("A=체형교정 / B=감량 / C=요약형")

current_run_generating = generate_clicked or demo_clicked

if demo_clicked:
    demo_member = {
        "trainer_name": DEFAULT_TRAINER_NAME,
        "gym_name": DEFAULT_GYM_NAME,
        "member_name": "정대훈",
        "gender": "남성",
        "age": 33,
        "session_plan": "30회(3개월)",
        "goal_focus": "체형교정",
        "height": 176.0,
        "weight": 78.0,
        "muscle": 31.5,
        "fat_mass": 18.2,
        "pbf": 23.3,
        "visceral_note": "내장지방 관리 필요",
        "template_mode": "A" if template_mode == "AUTO" else template_mode,
        "scores": {"근력": "중", "지구력": "중하", "가동성": "하", "유연성": "중하"},
        "strengths": ["비율이 좋음", "피드백을 잘 수용함", "체형교정 의지가 강함"],
        "weaknesses": ["경추/흉추 정렬 이슈", "코어 안정성 부족", "운동 지속성 부족"],
        "special_notes": ["장시간 앉아있는 직업", "운동 전 근막이완 필요"],
    }
    st.session_state["demo_member"] = demo_member
    generate_clicked = True

if generate_clicked:
    client = get_openai_client(manual_api_key)
    member = st.session_state.get("demo_member") or collect_input()
    st.session_state.pop("demo_member", None)
    errors = validate(member)

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    selected_template = choose_template(member)

    with st.spinner("회원 맞춤 PT 세일즈 자료를 생성하는 중입니다..."):
        report = generate_report_json(client, member, selected_template, model_name=model_name)

    manual_image_data_list = uploaded_files_to_data_uris(manual_reference_images, max_files=4)
    if manual_image_data_list:
        image_items = [
            {"src": img, "caption": manual_reference_captions[idx] if idx < len(manual_reference_captions) else ""}
            for idx, img in enumerate(manual_image_data_list)
        ]
        report.setdefault("reference_block", {})["image_data_list"] = manual_image_data_list
        report.setdefault("reference_block", {})["image_captions"] = manual_reference_captions[:len(manual_image_data_list)]
        report.setdefault("reference_block", {})["image_items"] = image_items
        report.setdefault("reference_block", {})["image_data"] = manual_image_data_list[0]
        image_status = f"직접 업로드한 참고 이미지 {len(manual_image_data_list)}장을 사용했습니다."
        image_source = "manual_upload"
    elif image_enabled:
        with st.spinner("참고 이미지를 생성하는 중입니다..."):
            image_data, image_status = maybe_generate_image(client, True, report.get("image_prompt", ""))
            if not image_data and manual_api_key:
                image_status += " / 직접 입력한 API 키로도 이미지 생성에 실패했습니다. 키 권한 또는 잔액도 확인해주세요."
            elif not image_data and not manual_api_key:
                image_status += " / 사이드바의 'OpenAI API 키 직접 입력' 칸에 키를 붙여넣고 다시 시도해보세요."
            report.setdefault("reference_block", {})["image_data"] = image_data
            report.setdefault("reference_block", {})["image_data_list"] = [image_data] if image_data else []
            report.setdefault("reference_block", {})["image_captions"] = []
            report.setdefault("reference_block", {})["image_items"] = [{"src": image_data, "caption": ""}] if image_data else []
            image_source = "ai_generated" if image_data else "placeholder"
    else:
        report.setdefault("reference_block", {})["image_data"] = None
        report.setdefault("reference_block", {})["image_data_list"] = []
        report.setdefault("reference_block", {})["image_captions"] = []
        report.setdefault("reference_block", {})["image_items"] = []
        image_status = "참고 이미지 자동생성이 꺼져 있어 기본 플레이스홀더를 표시합니다."
        image_source = "placeholder"

    report["meta"]["template_type"] = selected_template
    refresh_rendered_report(report)
    st.session_state["selected_template"] = selected_template
    st.session_state["member_name_saved"] = member["member_name"]
    st.session_state["image_status"] = image_status
    st.session_state["image_source"] = image_source
    st.session_state["reference_image_data"] = report.get("reference_block", {}).get("image_data")
    st.session_state["reference_image_data_list"] = report.get("reference_block", {}).get("image_data_list", [])
    st.session_state["reference_image_items"] = report.get("reference_block", {}).get("image_items", [])
    st.session_state["report_json_original"] = deepcopy(report)


# ============================================================
# 출력
# ============================================================
if st.session_state.get("report_html"):
    member_name_saved = st.session_state.get("member_name_saved", "회원")
    selected_template = st.session_state.get("selected_template", "A")

    editor_notice = st.session_state.pop("editor_notice", "")
    if editor_notice:
        st.success(editor_notice)
    else:
        st.success(f"{selected_template}형 리포트 생성 완료")

    tabs = st.tabs(["세일즈 자료 미리보기", "생성 JSON", "HTML 소스"])

    with tabs[0]:
        image_status = st.session_state.get("image_status")
        image_source = st.session_state.get("image_source")
        ref_image = st.session_state.get("reference_image_data")
        ref_images = st.session_state.get("reference_image_data_list", [])
        ref_items = st.session_state.get("reference_image_items", [])
        if image_status:
            if "실패" in image_status or "없" in image_status or "비어" in image_status:
                st.warning(image_status)
            elif "업로드" in image_status:
                st.success(image_status)
            else:
                st.info(image_status)
        if image_source == "manual_upload":
            st.caption("현재 문서에는 직접 업로드한 이미지가 적용되어 있습니다.")
        elif image_source == "ai_generated":
            st.caption("현재 문서에는 AI가 생성한 참고 이미지가 적용되어 있습니다.")
        else:
            st.caption("현재 문서에는 실제 이미지가 없어서 이미지 박스를 숨겼습니다.")
        if ref_items:
            if len(ref_items) == 1:
                st.image(ref_items[0]["src"], caption=ref_items[0].get("caption") or "문서에 들어간 참고 이미지 확인", use_container_width=True)
            else:
                preview_cols = st.columns(2)
                for idx, item in enumerate(ref_items[:4]):
                    with preview_cols[idx % 2]:
                        st.image(item["src"], caption=item.get("caption") or f"문서 반영 이미지 {idx + 1}", use_container_width=True)
        elif ref_images:
            if len(ref_images) == 1:
                st.image(ref_images[0], caption="문서에 들어간 참고 이미지 확인", use_container_width=True)
            else:
                preview_cols = st.columns(2)
                for idx, img in enumerate(ref_images[:4]):
                    with preview_cols[idx % 2]:
                        st.image(img, caption=f"문서 반영 이미지 {idx + 1}", use_container_width=True)
        elif ref_image:
            st.image(ref_image, caption="문서에 들어간 참고 이미지 확인", use_container_width=True)
        st.components.v1.html(st.session_state["report_html"], height=1650, scrolling=True)

        current_report = deepcopy(st.session_state["report_json"])
        st.markdown("### 문서 수정")
        st.caption("미리보기 아래에서 바로 수정하고 다시 렌더링할 수 있습니다.")
        with st.form("report_editor_form"):
            e1, e2 = st.columns(2)
            with e1:
                section_1_text = st.text_area(
                    "1. 회원 목표 및 제안 방향",
                    value="\n".join(current_report.get("section_1", {}).get("items", [])),
                    height=120,
                )
                section_2_text = st.text_area(
                    "2. 트레이닝 장점",
                    value="\n".join(current_report.get("section_2", {}).get("items", [])),
                    height=120,
                )
                section_3_text = st.text_area(
                    "3. 현재 상태 요약",
                    value="\n".join(current_report.get("section_3", {}).get("paragraphs", [])),
                    height=140,
                )
            with e2:
                direction_lead_text = st.text_input(
                    "로드맵 리드 문구",
                    value=current_report.get("direction_section", {}).get("lead", ""),
                )
                direction_guide_text = st.text_input(
                    "로드맵 보조 문구",
                    value=current_report.get("direction_section", {}).get("guide", ""),
                )
                sales_talk_text = st.text_area(
                    "상담 핵심 멘트",
                    value="\n".join(current_report.get("sales_focus", {}).get("sales_talk", [])),
                    height=120,
                )
                closing_text = st.text_area(
                    "트레이너 코멘트",
                    value=current_report.get("closing", {}).get("letter", ""),
                    height=160,
                )

            st.markdown("#### 단계별 로드맵 표 수정")
            direction_df = direction_rows_to_editor_df(current_report.get("direction_section", {}).get("rows", []))
            edited_direction_df = st.data_editor(
                direction_df,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
            )

            b1, b2 = st.columns(2)
            apply_edits = b1.form_submit_button("수정 반영", use_container_width=True)
            restore_original = b2.form_submit_button("초기 생성본 복원", use_container_width=True)

        if apply_edits:
            updated_report = deepcopy(current_report)
            updated_report.setdefault("section_1", {})["items"] = split_lines(section_1_text) or current_report.get("section_1", {}).get("items", [])
            updated_report.setdefault("section_2", {})["items"] = split_lines(section_2_text) or current_report.get("section_2", {}).get("items", [])
            updated_report.setdefault("section_3", {})["paragraphs"] = split_lines(section_3_text) or current_report.get("section_3", {}).get("paragraphs", [])
            updated_report.setdefault("sales_focus", {})["sales_talk"] = split_lines(sales_talk_text) or current_report.get("sales_focus", {}).get("sales_talk", [])
            updated_report.setdefault("closing", {})["letter"] = tighten_coaching_text(closing_text) or current_report.get("closing", {}).get("letter", "")
            updated_report.setdefault("direction_section", {})["lead"] = tighten_coaching_text(direction_lead_text) or current_report.get("direction_section", {}).get("lead", "")
            updated_report.setdefault("direction_section", {})["guide"] = tighten_coaching_text(direction_guide_text) or current_report.get("direction_section", {}).get("guide", "")
            updated_report.setdefault("direction_section", {})["rows"] = direction_editor_df_to_rows(
                edited_direction_df,
                current_report.get("direction_section", {}).get("rows", []),
            )
            updated_report = tighten_report_text(updated_report)
            refresh_rendered_report(updated_report)
            st.session_state["editor_notice"] = "수정 내용을 반영했습니다."
            st.rerun()

        if restore_original:
            original_report = deepcopy(st.session_state.get("report_json_original", current_report))
            refresh_rendered_report(original_report)
            st.session_state["editor_notice"] = "초기 생성본으로 복원했습니다."
            st.rerun()
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                "HTML 다운로드",
                data=st.session_state["report_html"],
                file_name=f"{member_name_saved}_PT세일즈자료_{selected_template}형.html",
                mime="text/html",
                use_container_width=True,
            )
        with d2:
            if st.session_state.get("report_pdf"):
                st.download_button(
                    "PDF 다운로드",
                    data=st.session_state["report_pdf"],
                    file_name=f"{member_name_saved}_PT세일즈자료_{selected_template}형.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.button("PDF 다운로드(비활성)", disabled=True, use_container_width=True)
        with d3:
            st.download_button(
                "JSON 다운로드",
                data=json.dumps(st.session_state["report_json"], ensure_ascii=False, indent=2),
                file_name=f"{member_name_saved}_PT세일즈자료_{selected_template}형.json",
                mime="application/json",
                use_container_width=True,
            )

        if not WEASYPRINT_AVAILABLE:
            st.warning("현재 환경에서는 WeasyPrint가 없어 PDF 다운로드가 비활성화되었습니다. requirements.txt 설치 후 사용할 수 있습니다.")

    with tabs[1]:
        st.json(st.session_state["report_json"])

    with tabs[2]:
        st.code(st.session_state["report_html"], language="html")
else:
    if current_run_generating:
        st.markdown(
            """
            <div class="loading-card">
              <div class="loading-kicker">⏳ PT SALES REPORT GENERATING</div>
              <div class="loading-title">회원 맞춤 리포트 생성 중</div>
              <div class="loading-desc">입력 정보를 바탕으로 핵심 분석과 로드맵을 정리하고 있습니다.</div>
              <div class="loading-steps">
                <div class="loading-step"><strong>1. 상태 분석</strong><span>목표와 현재 패턴을 정리합니다.</span></div>
                <div class="loading-step"><strong>2. 문구 생성</strong><span>상담용 핵심 문장을 만듭니다.</span></div>
                <div class="loading-step"><strong>3. 문서 렌더링</strong><span>최종 제안서로 조합합니다.</span></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<div style="background:#ffffff;border:1px solid #d9e5f0;border-radius:22px;padding:24px 26px;box-shadow:0 10px 26px rgba(16,42,67,.06);">

### 사용 방법
1. 좌측에서 템플릿을 선택합니다.  
2. 회원 정보와 트레이너 메모를 입력합니다.  
3. **세일즈 자료 생성**을 누릅니다.  
4. 생성 후 미리보기 아래에서 바로 수정할 수 있습니다.  
5. 필요하면 HTML / PDF / JSON으로 다운로드합니다.  

### 이 버전의 핵심
- 회원 정보에 따라 문구 차이를 더 크게 반영합니다.  
- 문장을 짧고 상담 기록지 톤에 맞게 정리합니다.  
- 결과물은 단순 운동계획서가 아니라 **회원 상태 분석 + 횟수 제안 + 등록 설득 포인트**를 담는 PT 세일즈 자료입니다.  
- 표는 **구분 / 1단계 / 2단계 / 3단계** 구조의 세로형 관리 표를 유지해 제안 근거를 명확히 보여줍니다.  
- 레이아웃은 템플릿이 책임지고, AI는 세일즈 설득 문구를 채우는 방식이라 현장 상담에서 바로 활용하기 쉽습니다.  

</div>
            """,
            unsafe_allow_html=True,
        )
