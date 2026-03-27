"""
Blind T/I/D/E Validation Script (Layer 3)

Extracts borderline cases from tide_attribution.md, creates blind profiles (Level 2),
runs them through 5 AI models x 3 rounds, calculates agreement metrics.

Models: GPT-5.2, Claude Sonnet 4.6, Grok-4-1-fast-reasoning, Gemini 3 Flash, HCX-007
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from dotenv import load_dotenv

# ── Paths ──
DATA_DIR = Path(__file__).resolve().parent.parent          # .../data/
PROJECT_DIR = DATA_DIR.parent                               # .../president/
ENV_PATH = PROJECT_DIR / ".env"
TIDE_PATH = DATA_DIR / "verified" / "tide_attribution.md"
RESULTS_PATH = DATA_DIR / "verified" / "blind_validation_results.md"
RAW_RESPONSES_PATH = DATA_DIR / "raw_downloads" / "blind_coding_responses.json"

load_dotenv(ENV_PATH)

# ═══════════════════════════════════════════════════════════
# STEP 1: Extract borderline cases (경계?=Y)
# ═══════════════════════════════════════════════════════════

def extract_borderline_cases(md_path: Path) -> List[Dict[str, str]]:
    """Parse tide_attribution.md and extract all actions with 경계?=Y."""
    text = md_path.read_text(encoding="utf-8")
    cases = []

    # Find all table rows with Y in the last column (경계?)
    # Table format: | ID | Action | T/I/D/E | 신뢰도 | 근거 | 경계? |
    current_president = ""
    for line in text.split("\n"):
        # Detect president section headers
        if re.match(r"^## \d+\.\s+(.+?)\s*\(", line):
            m = re.match(r"^## \d+\.\s+(.+?)\s*\(", line)
            current_president = m.group(1).strip()
            continue

        # Parse table rows
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.split("|")]
        # Remove empty first/last from split
        cols = [c for c in cols if c]
        if len(cols) < 6:
            continue
        # Skip header rows
        if cols[0] in ("ID", "----", "---") or cols[0].startswith("-"):
            continue

        action_id = cols[0]
        action_desc = cols[1]
        tide_code = cols[2].replace("**", "").strip()
        confidence = cols[3]
        rationale = cols[4]
        borderline = cols[5].strip()

        if borderline == "Y":
            cases.append({
                "id": action_id,
                "president": current_president,
                "action": action_desc,
                "researcher_code": tide_code,
                "confidence": confidence,
                "rationale": rationale,
            })

    return cases


# ═══════════════════════════════════════════════════════════
# STEP 2: Create blind profiles (Level 2)
# ═══════════════════════════════════════════════════════════

# President name -> random label mapping (shuffled each run)
PRESIDENT_NAMES = ["노무현", "이명박", "박근혜", "문재인", "윤석열", "이재명"]
GREEK_LABELS = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]

def build_label_map() -> Dict[str, str]:
    """Shuffle and create president -> label mapping."""
    shuffled = GREEK_LABELS.copy()
    random.shuffle(shuffled)
    return {name: label for name, label in zip(PRESIDENT_NAMES, shuffled)}


def anonymize_action(case: Dict, label_map: Dict[str, str]) -> Dict[str, str]:
    """
    Create Level 2 blind profile:
    - Remove president name, party, exact dates, specific law names
    - Keep structural description
    """
    president = case["president"]
    label = label_map.get(president, "Unknown")
    action = case["action"]
    rationale = case["rationale"]

    # Build anonymized description from the action + rationale
    desc = f"{action}. {rationale}"

    # Remove president names
    for name in PRESIDENT_NAMES:
        desc = desc.replace(name, f"정부 {label_map.get(name, 'X')}")

    # Remove specific Korean president references
    desc = re.sub(r"김대중\s*(정부)?", "선행 정부", desc)

    # Remove exact years -> "임기 N년차" or relative references
    # Replace specific year ranges
    desc = re.sub(r"\(20\d{2}\.?\d{0,2}\.?\d{0,2}\)", "", desc)
    desc = re.sub(r"\(20\d{2}\)", "", desc)
    desc = re.sub(r"20\d{2}년", "해당 시기", desc)
    desc = re.sub(r"20\d{2}", "해당연도", desc)

    # Remove specific law names -> functional descriptions
    law_map = {
        "정부업무평가기본법": "정부 업무 평가 관련 기본 법률",
        "전자정부법": "전자정부 관련 법률",
        "규제자유특구법": "규제 유연화 특구 관련 법률",
        "규제프리존 특별법": "규제 유연화 지역 관련 법률",
        "데이터산업법": "데이터 산업 관련 법률",
        "AI기본법": "AI 관련 기본 법률",
        "이태원특별법": "대규모 안전사고 관련 특별법",
        "규제샌드박스법": "규제 유연화 관련 법률",
        "정부3.0": "정부 개방·공유 이니셔티브",
    }
    for law, anon in law_map.items():
        desc = desc.replace(law, anon)

    # Remove party/ideology markers
    for term in ["진보", "보수", "더불어민주당", "국민의힘", "새누리당", "한나라당",
                  "열린우리당", "정권 교체", "야당 출신"]:
        desc = desc.replace(term, "")

    # Remove specific event names
    event_map = {
        "MERS": "대규모 감염병",
        "코로나19": "대규모 감염병",
        "코로나": "대규모 감염병",
        "COVID-19": "대규모 감염병",
        "이태원 참사": "대규모 안전사고",
        "이태원": "안전사고",
        "국정농단": "대통령 직무정지 사태",
        "4대강": "대규모 국토사업",
        "국민청원": "시민 온라인 참여 플랫폼",
    }
    for event, anon in event_map.items():
        desc = desc.replace(event, anon)

    # Clean up multiple spaces
    desc = re.sub(r"\s+", " ", desc).strip()

    return {
        "blind_id": None,  # Will be set sequentially in main
        "original_id": case["id"],
        "government_label": f"정부 {label}",
        "researcher_code": case["researcher_code"],
        "anonymized_description": desc,
    }


# ═══════════════════════════════════════════════════════════
# STEP 3: Anchoring vignettes
# ═══════════════════════════════════════════════════════════

VIGNETTES = [
    {
        "id": "V1",
        "title": "디지털 인프라 확대",
        "expected": "T",
        "text": """가상국 K의 정부 X (임기 5년)

배경: 정부 X 취임 시점에 K국의 인터넷 보급률은 85%였다. 정부 X는 "디지털 강국" 비전을 선포하고 디지털 인프라 확대 예산을 전 정부 대비 15% 증액했다. 임기 말 인터넷 보급률은 92%에 도달했다.

그러나:
- K국의 인터넷 보급률은 정부 X 이전 10년간 연평균 2%p씩 증가해왔다.
- 주변 국가들도 동일 기간 유사한 보급률 증가를 보였다.
- 15% 예산 증액분은 인플레이션 조정 시 실질 5% 증가에 그쳤다.

질문: 정부 X 임기 중 인터넷 보급률 7%p 상승은 정부의 의도적 행위(I)인가, 시대적 추세(T)인가?"""
    },
    {
        "id": "V2",
        "title": "위기 대응 체계 구축",
        "expected": "I",
        "text": """가상국 K의 정부 Y (임기 5년)

배경: 정부 Y 취임 직후 대규모 산업재해가 발생했다(광산 붕괴, 200명 사상). 정부 Y는 다음 조치를 취했다:

1. 기존 분산된 3개 안전 기관을 통합하여 "국가안전청" 신설 (조직법 개정)
2. 안전 관련 예산을 GDP 대비 0.3%에서 0.8%로 인상 (3년에 걸쳐)
3. 민관 합동 안전점검위원회를 법정 기구로 격상 (기존은 자문기구)
4. 산업안전 기준을 OECD 최고 수준으로 상향 (37개 시행령 개정)

이전 정부들은 유사한 재해 후 임시 대책을 발표했으나, 조직 신설이나 법정 기구 격상까지는 진행하지 않았다.

질문: 정부 Y의 안전 거버넌스 강화는 T/I/D/E 중 어디에 해당하는가?"""
    },
    {
        "id": "V3",
        "title": "참여 제도의 형식화",
        "expected": "D",
        "text": """가상국 K의 정부 Z (임기 5년)

배경: 정부 Z는 전임 정부가 도입한 "국민정책참여 포털"을 승계했다. 이 포털은 법적 근거가 있으며(시민참여촉진법 제12조), 연간 운영 예산도 배정되어 있다.

정부 Z 임기 중:
- 포털은 계속 운영되었다 (서버 가동, 접수 기능 유지)
- 그러나 접수된 제안 중 정책 반영률이 전 정부 23%에서 4%로 하락했다
- 제안 검토위원회는 5년간 3회만 소집되었다 (전 정부: 연 4회)
- 포털 방문자 수는 전 정부 대비 70% 감소했다
- 정부 Z는 포털 폐지를 선언하지 않았고, 별도 참여 채널도 신설하지 않았다

질문: 정부 Z의 시민참여 수준은 T/I/D/E 중 어디에 해당하는가?"""
    },
]


# ═══════════════════════════════════════════════════════════
# STEP 4: API callers for 5 models
# ═══════════════════════════════════════════════════════════

def _retry(func, max_attempts=3):
    """Retry with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            wait = 2 ** attempt * 2
            print(f"  [Retry {attempt+1}/{max_attempts}] Error: {e}")
            if attempt < max_attempts - 1:
                print(f"  Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


def call_openai(system: str, user: str, model: str = "gpt-5.2",
                base_url: str | None = None, api_key: str | None = None) -> str:
    """Call OpenAI-compatible API."""
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
        base_url=base_url,
    )
    # GPT-5+ requires max_completion_tokens; Grok and others use max_tokens
    token_param = {}
    if base_url and "x.ai" in base_url:
        token_param["max_tokens"] = 16384
    else:
        token_param["max_completion_tokens"] = 16384
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        **token_param,
    )
    return resp.choices[0].message.content


def call_anthropic(system: str, user: str) -> str:
    """Call Anthropic Claude API."""
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16384,
        temperature=0.2,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


def call_gemini(system: str, user: str) -> str:
    """Call Google Gemini API via REST (same pattern as ai_scoring_v2.py)."""
    import requests as _requests
    api_key = os.getenv("GEMINI_API_KEY")
    for model_name in ["gemini-3-flash-preview", "gemini-2.5-flash-preview-04-17"]:
        try:
            resp = _requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent",
                params={"key": api_key},
                json={
                    "system_instruction": {"parts": [{"text": system}]},
                    "contents": [{"parts": [{"text": user}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 16384},
                },
                timeout=180,
            )
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError(f"Gemini no candidates: {data}")
            parts = candidates[0].get("content", {}).get("parts", [])
            return parts[0].get("text", "") if parts else ""
        except Exception as e:
            if model_name != "gemini-2.5-flash-preview-04-17":
                print(f"  {model_name} failed ({e}), trying next...")
                continue
            raise


def call_clova(system: str, user: str) -> str:
    """Call CLOVA HyperCLOVA HCX-007 via v3 (same pattern as ai_scoring_v2.py)."""
    import requests as _requests
    api_key = os.getenv("CLOVA_STUDIO_API_KEY", "").strip()
    model = os.getenv("CLOVA_STUDIO_MODEL", "HCX-007")
    base_url = (os.getenv("CLOVA_STUDIO_BASE_URL") or "https://clovastudio.stream.ntruss.com").rstrip("/")
    resp = _requests.post(
        f"{base_url}/v3/chat-completions/{model}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        },
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    result = data.get("result", data)
    message = result.get("message", {})
    return message.get("content", "")


# Model registry
MODEL_CALLERS = {
    "GPT-5.2": lambda sys, usr: call_openai(sys, usr, model="gpt-5.2"),
    "Claude-Sonnet-4.6": lambda sys, usr: call_anthropic(sys, usr),
    "Grok-4-1": lambda sys, usr: call_openai(
        sys, usr,
        model="grok-4-1-fast-reasoning",
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY"),
    ),
    "Gemini-3-Flash": lambda sys, usr: call_gemini(sys, usr),
    "HCX-007": lambda sys, usr: call_clova(sys, usr),
}


# ═══════════════════════════════════════════════════════════
# STEP 4b: Build prompts
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """당신은 비교행정학 전문 연구원입니다. 아래에 익명화된 정부의 정책 행위가 제시됩니다. 정부의 이름, 정당, 이념 성향은 알려지지 않았습니다. 오직 제시된 정보만으로 판단하십시오."""

def build_vignette_prompt() -> str:
    """Build the anchoring vignette calibration prompt."""
    parts = ["## 앵커링 비네트 교정 과제\n\n다음 세 가지 가상 사례를 읽고, 각각 T/I/D/E로 분류하십시오.\n"]
    for v in VIGNETTES:
        parts.append(f"### 비네트 {v['id']}: {v['title']}\n\n{v['text']}\n")

    parts.append("""### 응답 형식 (JSON)

반드시 아래 형식의 JSON만 반환하십시오. 다른 텍스트를 포함하지 마십시오.

{
  "vignette_1": {
    "classification": "T 또는 I 또는 D 또는 E",
    "confidence": 0.0~1.0,
    "reasoning": "분류 근거 (3문장 이내)"
  },
  "vignette_2": {
    "classification": "T 또는 I 또는 D 또는 E",
    "confidence": 0.0~1.0,
    "reasoning": "분류 근거 (3문장 이내)"
  },
  "vignette_3": {
    "classification": "T 또는 I 또는 D 또는 E",
    "confidence": 0.0~1.0,
    "reasoning": "분류 근거 (3문장 이내)"
  }
}""")
    return "\n".join(parts)


def build_classification_prompt(blind_items: List[Dict]) -> str:
    """Build the T/I/D/E classification prompt for all blind items."""
    parts = ["## 귀인 분류 과제\n\n다음은 가상국 K의 여러 정부가 수행한 정책 행위에 대한 익명화된 기술입니다. 각 행위를 T/I/D/E로 분류하십시오.\n"]

    for i, item in enumerate(blind_items, 1):
        parts.append(f"### 항목 {i} ({item['blind_id']}): {item['government_label']}")
        parts.append(f"\n{item['anonymized_description']}\n")

    parts.append("""### 분류 지침

위 각 행위를 다음 네 가지 귀인 유형 중 하나로 분류하십시오:

- **T (추세)**: 어떤 정부든 일어났을 시대적·기술적·사회적 축적. 국제적 보편 추세이거나, 이전 정부에서 이미 시작된 경로의 자연스러운 연장.
- **I (의도적)**: 해당 정부의 의도적 정책 결정. 새로운 제도 신설, 기존 제도의 의미 있는 변경, 예산의 대폭적 재배분 등.
- **D (표류)**: 관련 제도가 법적으로 존재하나, 해당 정부 임기 중 실질적으로 작동하지 않았거나 형식화된 경우.
- **E (외부)**: 정부 통제 밖의 외부 충격이 주된 원인. 글로벌 경제위기, 팬데믹, 국제 규범 변화 등.

혼합 귀인(예: T+I)도 허용됩니다. 이 경우 주된 귀인을 classification에 기재하고, 비율을 component에 표시하십시오.

### 응답 형식 (JSON)

반드시 아래 형식의 JSON 배열만 반환하십시오. 다른 텍스트를 포함하지 마십시오.

[
  {
    "blind_id": "항목의 blind_id",
    "classification": "T 또는 I 또는 D 또는 E 또는 T+I 등",
    "confidence": 0.0~1.0,
    "reasoning": "분류 근거 (3문장 이내)",
    "t_component": 0.0~1.0,
    "i_component": 0.0~1.0,
    "d_component": 0.0~1.0,
    "e_component": 0.0~1.0
  },
  ...
]

주의: t_component + i_component + d_component + e_component = 1.0이어야 합니다.""")
    return "\n".join(parts)


def build_identification_prompt(blind_items: List[Dict], label_map: Dict[str, str]) -> str:
    """Build the identification test prompt."""
    labels_used = sorted(set(item["government_label"] for item in blind_items))
    labels_str = ", ".join(labels_used)

    parts = [f"""## 정부 식별 과제

이전에 분석한 {labels_str}에 대해, 각 정부가 실제로 어느 나라의 어떤 시기 정부인지 추측하십시오. 모르는 경우 "식별 불가"로 답하십시오.

이전 과제에서 제시된 정책 행위 기술만을 근거로 판단하십시오.

### 응답 형식 (JSON)

반드시 아래 형식의 JSON만 반환하십시오.

{{"""]

    for label in labels_used:
        parts.append(f"""  "{label}": {{
    "guess": "식별 불가 또는 추측한 정부명",
    "confidence": 0.0~1.0,
    "clues": "식별 근거가 된 단서 (있는 경우)"
  }},""")

    parts.append("}")
    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════
# STEP 5: Parse JSON from model responses
# ═══════════════════════════════════════════════════════════

def extract_json(text: str) -> Any:
    """Extract JSON from model response, handling markdown code blocks."""
    # Try to find JSON in code blocks first
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", text)
    if m:
        text = m.group(1).strip()

    # Try parsing directly
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try finding first { or [ and matching
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        if start == -1:
            continue
        # Find matching end
        depth = 0
        for i in range(start, len(text)):
            if text[i] == start_char:
                depth += 1
            elif text[i] == end_char:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break

    return None


# ═══════════════════════════════════════════════════════════
# STEP 5b: Calculate agreement metrics
# ═══════════════════════════════════════════════════════════

def normalize_code(code: str) -> str:
    """Normalize T/I/D/E codes for comparison."""
    code = code.strip().upper()
    # Map complex codes to primary
    if "I-" in code or "I−" in code:
        return "I"
    if "+" in code:
        # T+I -> take the first (primary)
        parts = code.split("+")
        return parts[0].strip()
    if code in ("T", "I", "D", "E"):
        return code
    # Try to find the main letter
    for c in ["T", "I", "D", "E"]:
        if c in code:
            return c
    return code


def calculate_agreement(results: Dict, blind_items: List[Dict]) -> Dict:
    """Calculate researcher vs model agreement and Krippendorff's alpha."""
    import krippendorff

    # Build researcher codes
    researcher_codes = {}
    for item in blind_items:
        researcher_codes[item["blind_id"]] = normalize_code(item["researcher_code"])

    # Per-model agreement with researcher
    model_agreement = {}
    all_item_ids = sorted(researcher_codes.keys())

    # Build matrix for Krippendorff's alpha: rows = raters, cols = items
    # Rater 0 = researcher, then models
    code_to_num = {"T": 1, "I": 2, "D": 3, "E": 4}
    rater_data = []

    # Researcher row
    researcher_row = []
    for bid in all_item_ids:
        code = researcher_codes.get(bid, "")
        researcher_row.append(code_to_num.get(normalize_code(code), np.nan))
    rater_data.append(researcher_row)

    for model_name, rounds in results.items():
        if model_name.startswith("_"):
            continue
        agree_count = 0
        total = 0
        model_row = []

        # Aggregate across rounds (majority vote)
        item_votes = {}
        for rnd_data in rounds:
            if not isinstance(rnd_data, dict) or "classification" not in str(rnd_data):
                continue
            classifications = rnd_data.get("classifications", [])
            for cls in classifications:
                bid = cls.get("blind_id", "")
                code = normalize_code(cls.get("classification", ""))
                if bid and code:
                    item_votes.setdefault(bid, []).append(code)

        # Majority vote per item
        model_codes = {}
        for bid, votes in item_votes.items():
            from collections import Counter
            most_common = Counter(votes).most_common(1)
            if most_common:
                model_codes[bid] = most_common[0][0]

        for bid in all_item_ids:
            rc = researcher_codes.get(bid, "")
            mc = model_codes.get(bid, "")
            if rc and mc:
                total += 1
                if rc == mc:
                    agree_count += 1
            model_row.append(code_to_num.get(mc, np.nan))

        rater_data.append(model_row)
        model_agreement[model_name] = {
            "agree": agree_count,
            "total": total,
            "rate": agree_count / total if total > 0 else 0,
        }

    # Krippendorff's alpha (among models only, excluding researcher)
    alpha = np.nan
    model_matrix = np.array(rater_data[1:])  # exclude researcher
    if len(model_matrix) >= 2:
        try:
            alpha = krippendorff.alpha(
                reliability_data=model_matrix,
                level_of_measurement="nominal",
            )
        except Exception as e:
            print(f"  Krippendorff alpha error: {e}")

    # Also compute alpha with researcher included
    alpha_with_researcher = np.nan
    full_matrix = np.array(rater_data)
    if len(full_matrix) >= 2:
        try:
            alpha_with_researcher = krippendorff.alpha(
                reliability_data=full_matrix,
                level_of_measurement="nominal",
            )
        except Exception as e:
            print(f"  Krippendorff alpha (with researcher) error: {e}")

    return {
        "model_agreement": model_agreement,
        "krippendorff_alpha_models": float(alpha) if not np.isnan(alpha) else None,
        "krippendorff_alpha_all": float(alpha_with_researcher) if not np.isnan(alpha_with_researcher) else None,
    }


def calculate_identification_rate(results: Dict, label_map: Dict[str, str]) -> Dict:
    """Calculate identification rate from identification test results."""
    reverse_map = {f"정부 {v}": k for k, v in label_map.items()}
    model_id_rates = {}

    for model_name, rounds in results.items():
        if model_name.startswith("_"):
            continue
        correct = 0
        total = 0
        details = []

        for rnd_data in rounds:
            if not isinstance(rnd_data, dict):
                continue
            id_results = rnd_data.get("identification", {})
            if not id_results:
                continue
            for label, info in id_results.items():
                if not isinstance(info, dict):
                    continue
                guess = info.get("guess", "식별 불가")
                actual = reverse_map.get(label, "")
                total += 1
                is_correct = False
                if actual and actual in guess:
                    correct += 1
                    is_correct = True
                details.append({
                    "label": label,
                    "actual": actual,
                    "guess": guess,
                    "correct": is_correct,
                })

        model_id_rates[model_name] = {
            "correct": correct,
            "total": total,
            "rate": correct / total if total > 0 else 0,
            "details": details,
        }

    return model_id_rates


# ═══════════════════════════════════════════════════════════
# STEP 6: Main execution
# ═══════════════════════════════════════════════════════════

def save_raw_responses(raw_responses: Dict, path: Path):
    """Incrementally save raw API responses."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw_responses, f, ensure_ascii=False, indent=2)
    print(f"  Raw responses saved to {path}")


def save_results_md(agreement: Dict, vignette_results: Dict,
                    identification: Dict, blind_items: List[Dict],
                    label_map: Dict[str, str], raw_results: Dict, path: Path):
    """Save complete results to markdown."""
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Blind T/I/D/E Validation Results")
    lines.append("")
    lines.append(f"> 실행일: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> 모델: {', '.join(MODEL_CALLERS.keys())}")
    lines.append(f"> 라운드: 3회")
    lines.append(f"> Temperature: 0.2")
    lines.append(f"> 검증 항목: {len(blind_items)}개 경계 사례")
    lines.append("")

    # Label mapping
    lines.append("## 1. 블라인드 레이블 매핑 (본 세션)")
    lines.append("")
    lines.append("| 레이블 | 실제 정부 |")
    lines.append("|--------|----------|")
    for name, label in label_map.items():
        lines.append(f"| 정부 {label} | {name} |")
    lines.append("")

    # Vignette results
    lines.append("## 2. 앵커링 비네트 결과")
    lines.append("")
    lines.append("| 모델 | V1 (정답:T) | V2 (정답:I) | V3 (정답:D) | 정확도 | 신뢰 가중치 |")
    lines.append("|------|:---:|:---:|:---:|:---:|:---:|")
    weight_map = {3: 1.0, 2: 0.7, 1: 0.3, 0: 0.0}
    model_weights = {}
    for model_name, vdata in vignette_results.items():
        v1 = vdata.get("V1", "?")
        v2 = vdata.get("V2", "?")
        v3 = vdata.get("V3", "?")
        correct = sum([
            1 if normalize_code(v1) == "T" else 0,
            1 if normalize_code(v2) == "I" else 0,
            1 if normalize_code(v3) == "D" else 0,
        ])
        weight = weight_map.get(correct, 0.0)
        model_weights[model_name] = weight
        v1_mark = "✓" if normalize_code(v1) == "T" else f"✗({v1})"
        v2_mark = "✓" if normalize_code(v2) == "I" else f"✗({v2})"
        v3_mark = "✓" if normalize_code(v3) == "D" else f"✗({v3})"
        lines.append(f"| {model_name} | {v1_mark} | {v2_mark} | {v3_mark} | {correct}/3 | {weight} |")
    lines.append("")

    # Classification agreement
    lines.append("## 3. T/I/D/E 분류 일치도")
    lines.append("")
    ma = agreement.get("model_agreement", {})
    lines.append("### 3.1 연구자 vs 모델 일치율")
    lines.append("")
    lines.append("| 모델 | 일치 항목 | 전체 | 일치율 | 가중 일치율 |")
    lines.append("|------|:---:|:---:|:---:|:---:|")
    for model_name, stats in ma.items():
        w = model_weights.get(model_name, 1.0)
        weighted_rate = stats["rate"] * w
        lines.append(f"| {model_name} | {stats['agree']} | {stats['total']} | {stats['rate']:.1%} | {weighted_rate:.1%} |")
    lines.append("")

    lines.append("### 3.2 Krippendorff's Alpha")
    lines.append("")
    ka_models = agreement.get("krippendorff_alpha_models")
    ka_all = agreement.get("krippendorff_alpha_all")
    lines.append(f"- **모델 간 (5 AI models)**: α = {ka_models:.4f}" if ka_models is not None else "- **모델 간**: 계산 불가")
    lines.append(f"- **연구자 포함 (연구자 + 5 models)**: α = {ka_all:.4f}" if ka_all is not None else "- **연구자 포함**: 계산 불가")
    lines.append("")

    # Identification test
    lines.append("## 4. 식별 테스트 (Identification Test)")
    lines.append("")
    lines.append("기준 확률: 1/6 = 16.7% (무작위)")
    lines.append("")
    lines.append("| 모델 | 정확 식별 | 전체 | 식별률 | 판정 |")
    lines.append("|------|:---:|:---:|:---:|------|")
    for model_name, stats in identification.items():
        rate = stats["rate"]
        if rate <= 1/6:
            verdict = "블라인딩 완전 성공"
        elif rate <= 1/3:
            verdict = "부분 성공"
        elif rate <= 0.5:
            verdict = "부분 실패"
        else:
            verdict = "블라인딩 실패"
        lines.append(f"| {model_name} | {stats['correct']} | {stats['total']} | {rate:.1%} | {verdict} |")
    lines.append("")

    # Per-item detail
    lines.append("## 5. 항목별 상세 결과")
    lines.append("")
    lines.append("| blind_id | original_id | 연구자 | " + " | ".join(ma.keys()) + " |")
    lines.append("|----------|-------------|:---:|" + "|".join([":---:" for _ in ma]) + "|")

    # Build per-item model codes
    item_model_codes = {}
    for model_name, rounds in raw_results.items():
        if model_name.startswith("_"):
            continue
        item_votes = {}
        for rnd_data in rounds:
            if not isinstance(rnd_data, dict):
                continue
            for cls in rnd_data.get("classifications", []):
                bid = cls.get("blind_id", "")
                code = cls.get("classification", "")
                if bid:
                    item_votes.setdefault(bid, []).append(code)
        for bid, votes in item_votes.items():
            from collections import Counter
            mc = Counter(votes).most_common(1)
            if mc:
                item_model_codes.setdefault(bid, {})[model_name] = mc[0][0]

    for item in blind_items:
        bid = item["blind_id"]
        oid = item["original_id"]
        rc = item["researcher_code"]
        model_cols = []
        for model_name in ma.keys():
            mc = item_model_codes.get(bid, {}).get(model_name, "—")
            match = "✓" if normalize_code(mc) == normalize_code(rc) else ""
            model_cols.append(f"{mc}{match}")
        lines.append(f"| {bid} | {oid} | {rc} | " + " | ".join(model_cols) + " |")
    lines.append("")

    # Disagreement analysis
    lines.append("## 6. 불일치 항목 분석")
    lines.append("")
    for item in blind_items:
        bid = item["blind_id"]
        rc = normalize_code(item["researcher_code"])
        disagreements = []
        for model_name in ma.keys():
            mc = normalize_code(item_model_codes.get(bid, {}).get(model_name, ""))
            if mc and mc != rc:
                disagreements.append((model_name, mc))
        if disagreements:
            lines.append(f"### {bid} ({item['original_id']})")
            lines.append(f"- 연구자: {item['researcher_code']}")
            for mn, mc in disagreements:
                lines.append(f"- {mn}: {mc}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Generated by blind_coding.py on {time.strftime('%Y-%m-%d %H:%M:%S')}*")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nResults saved to {path}")


def main():
    print("=" * 60)
    print("BLIND T/I/D/E VALIDATION (Layer 3)")
    print("=" * 60)

    # Step 1: Extract borderline cases
    print("\n[Step 1] Extracting borderline cases...")
    borderline_cases = extract_borderline_cases(TIDE_PATH)
    print(f"  Found {len(borderline_cases)} borderline cases")

    # Step 2: Create blind profiles
    print("\n[Step 2] Creating blind profiles (Level 2)...")
    label_map = build_label_map()
    print(f"  Label mapping: {label_map}")

    blind_items = []
    for i, case in enumerate(borderline_cases, 1):
        blind = anonymize_action(case, label_map)
        blind["blind_id"] = f"B{i:02d}"
        blind_items.append(blind)
    print(f"  Created {len(blind_items)} blind items")

    # Prepare prompts
    vignette_prompt = build_vignette_prompt()
    classification_prompt = build_classification_prompt(blind_items)

    raw_responses = {
        "_metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "label_map": label_map,
            "n_borderline_cases": len(borderline_cases),
            "n_blind_items": len(blind_items),
            "rounds": 3,
            "temperature": 0.2,
        },
        "_blind_items": [item for item in blind_items],
    }

    # Verify .env loaded
    print(f"\n  ENV check: OPENAI={bool(os.getenv('OPENAI_API_KEY'))}, "
          f"ANTHROPIC={bool(os.getenv('ANTHROPIC_API_KEY'))}, "
          f"XAI={bool(os.getenv('XAI_API_KEY'))}, "
          f"GEMINI={bool(os.getenv('GEMINI_API_KEY'))}, "
          f"CLOVA={bool(os.getenv('CLOVA_STUDIO_API_KEY'))}")

    # Step 3-4: Call 5 AI models x 3 rounds
    model_results = {}  # model_name -> list of round results
    vignette_results = {}

    for model_idx, (model_name, caller) in enumerate(MODEL_CALLERS.items()):
        print(f"\n{'='*50}")
        print(f"[Step 4] Model: {model_name}")
        print(f"{'='*50}")

        model_results[model_name] = []
        raw_responses[model_name] = []

        for rnd in range(1, 4):
            print(f"\n  --- Round {rnd}/3 ---")
            round_result = {}
            round_raw = {"round": rnd}

            # 4a: Vignettes (only round 1)
            if rnd == 1:
                print(f"  [Vignette] Sending calibration vignettes...")
                try:
                    vignette_resp = _retry(lambda: caller(SYSTEM_PROMPT, vignette_prompt))
                    round_raw["vignette_raw"] = vignette_resp
                    parsed = extract_json(vignette_resp)
                    if parsed:
                        v_codes = {}
                        for key in ["vignette_1", "vignette_2", "vignette_3"]:
                            if key in parsed:
                                v_codes[key.replace("vignette_", "V")] = parsed[key].get("classification", "?")
                        vignette_results[model_name] = v_codes
                        print(f"  [Vignette] Results: {v_codes}")
                    else:
                        print(f"  [Vignette] Could not parse JSON response")
                        vignette_results[model_name] = {"V1": "?", "V2": "?", "V3": "?"}
                except Exception as e:
                    print(f"  [Vignette] ERROR: {e}")
                    vignette_results[model_name] = {"V1": "?", "V2": "?", "V3": "?"}

            # 4b: Classification
            print(f"  [Classification] Sending {len(blind_items)} items...")
            try:
                cls_resp = _retry(lambda: caller(SYSTEM_PROMPT, classification_prompt))
                round_raw["classification_raw"] = cls_resp
                parsed = extract_json(cls_resp)
                if parsed and isinstance(parsed, list):
                    # Normalize blind_ids: model may return "B01 (항목 1)" -> extract "B01"
                    for item in parsed:
                        bid = item.get("blind_id", "")
                        # Extract the B## pattern
                        m = re.match(r"(B\d+)", bid)
                        if m:
                            item["blind_id"] = m.group(1)
                        else:
                            # Try to extract item number from various formats
                            m2 = re.search(r"항목\s*(\d+)", bid)
                            if m2:
                                item["blind_id"] = f"B{int(m2.group(1)):02d}"
                    round_result["classifications"] = parsed
                    print(f"  [Classification] Got {len(parsed)} classifications")
                elif parsed and isinstance(parsed, dict):
                    # Some models may return a dict with items keyed by id
                    items = []
                    for k, v in parsed.items():
                        if isinstance(v, dict):
                            v["blind_id"] = k
                            items.append(v)
                    round_result["classifications"] = items
                    print(f"  [Classification] Got {len(items)} classifications (from dict)")
                else:
                    print(f"  [Classification] Could not parse JSON")
                    round_result["classifications"] = []
            except Exception as e:
                print(f"  [Classification] ERROR: {e}")
                traceback.print_exc()
                round_result["classifications"] = []

            # 4c: Identification test (only round 1)
            if rnd == 1:
                print(f"  [Identification] Running identification test...")
                id_prompt = build_identification_prompt(blind_items, label_map)
                try:
                    id_resp = _retry(lambda: caller(SYSTEM_PROMPT, id_prompt))
                    round_raw["identification_raw"] = id_resp
                    parsed = extract_json(id_resp)
                    if parsed:
                        round_result["identification"] = parsed
                        print(f"  [Identification] Got responses for {len(parsed)} governments")
                    else:
                        print(f"  [Identification] Could not parse JSON")
                        round_result["identification"] = {}
                except Exception as e:
                    print(f"  [Identification] ERROR: {e}")
                    round_result["identification"] = {}

            model_results[model_name].append(round_result)
            raw_responses[model_name].append(round_raw)

            # Incremental save
            save_raw_responses(raw_responses, RAW_RESPONSES_PATH)

            # Rate limiting delay between rounds
            if rnd < 3:
                time.sleep(3)

        print(f"\n  {model_name} complete.")
        # Delay between models
        if model_idx < len(MODEL_CALLERS) - 1:
            time.sleep(2)

    # Step 5: Calculate agreement
    print(f"\n{'='*50}")
    print("[Step 5] Calculating agreement metrics...")
    print(f"{'='*50}")

    agreement = calculate_agreement(model_results, blind_items)
    print(f"\n  Researcher vs Model agreement:")
    for mn, stats in agreement.get("model_agreement", {}).items():
        print(f"    {mn}: {stats['agree']}/{stats['total']} ({stats['rate']:.1%})")
    ka = agreement.get("krippendorff_alpha_models")
    print(f"\n  Krippendorff's alpha (models): {ka:.4f}" if ka else "\n  Krippendorff's alpha: N/A")

    identification = calculate_identification_rate(model_results, label_map)
    print(f"\n  Identification rates:")
    for mn, stats in identification.items():
        print(f"    {mn}: {stats['correct']}/{stats['total']} ({stats['rate']:.1%})")

    # Step 6: Save results
    print(f"\n{'='*50}")
    print("[Step 6] Saving results...")
    print(f"{'='*50}")

    save_results_md(agreement, vignette_results, identification,
                    blind_items, label_map, model_results, RESULTS_PATH)
    save_raw_responses(raw_responses, RAW_RESPONSES_PATH)

    print("\n" + "=" * 60)
    print("BLIND VALIDATION COMPLETE")
    print("=" * 60)
    print(f"Results: {RESULTS_PATH}")
    print(f"Raw data: {RAW_RESPONSES_PATH}")


if __name__ == "__main__":
    main()
