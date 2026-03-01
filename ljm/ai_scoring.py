"""
Multi-AI ACW Scoring: 4개 AI 모델을 독립 코더로 활용한 ACW 점수화
GPT-5.1, Claude Sonnet 4.5, Grok-4, HyperCLOVA HCX-007

Usage:
    python ai_scoring.py                # 전체 실행
    python ai_scoring.py --models gpt claude  # 특정 모델만
    python ai_scoring.py --analysis acw       # ACW만
    python ai_scoring.py --analysis inst      # 제도적 구조만
"""

from __future__ import annotations

import argparse
import functools
import json
import math
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import requests
from dotenv import load_dotenv

# ── .env 로드 ──
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

# ── 상수 ──
GOVERNMENTS = ["노무현(2003-2008)", "이명박(2008-2013)", "박근혜(2013-2017)",
               "문재인(2017-2022)", "윤석열(2022-2025)", "이재명(2025-)"]

ACW_CRITERIA = {
    "다양성": [
        ("V1", "문제 프레이밍의 다양성", "정책 문제를 복수의 관점에서 정의하는가"),
        ("V2", "다수준 거버넌스", "중앙-광역-기초 간 다수준 정책 조율 체계가 있는가"),
        ("V3", "다부문 접근", "부처 간 협업 및 통합적 접근이 이루어지는가"),
        ("V4", "솔루션의 다양성", "정책 대안의 폭이 넓은가 (실험, 시범사업 등)"),
    ],
    "학습 역량": [
        ("L1", "과거 경험 활용", "이전 정책 실패/성공에서 체계적으로 학습하는가"),
        ("L2", "제도적 기억", "정부 교체에도 정책 학습이 단절되지 않는가"),
        ("L3", "이중순환 학습", "목표와 전략 자체를 재검토하는 메커니즘이 있는가"),
        ("L4", "모니터링·평가", "정책 성과를 지속적으로 모니터링하는가"),
    ],
    "여유 자원": [
        ("R1", "연속적 접근", "정책을 점진적·반복적으로 수정 가능한가"),
        ("R2", "자원의 가용성", "위기 시 긴급 재원·인력 동원이 가능한가"),
        ("R3", "혁신 여지", "실험적·파일럿 정책이 허용되는 환경인가"),
        ("R4", "자율적 변경 권한", "일선 기관이 자율적으로 대응할 수 있는가"),
    ],
    "리더십": [
        ("Le1", "비전 제시", "리더가 적응적 방향의 비전을 제시하는가"),
        ("Le2", "기업가적 리더십", "혁신적 정책 추진력이 있는가"),
        ("Le3", "협력적 리더십", "이해관계자와의 협력적 의사결정이 이루어지는가"),
        ("Le4", "반응적 리더십", "환경 변화에 민첩하게 반응하는가"),
    ],
    "자원": [
        ("Re1", "재정 자원", "적응적 정책을 위한 재정이 확보되는가"),
        ("Re2", "인적 자원", "전문인력이 충분한가"),
        ("Re3", "권위적 자원", "법적·제도적 권한이 뒷받침되는가"),
    ],
    "공정한 거버넌스": [
        ("F1", "합법성", "적응적 조치가 법적 근거 내에서 이루어지는가"),
        ("F2", "형평성", "정책의 비용과 편익이 공정하게 분배되는가"),
        ("F3", "반응성", "시민의 요구에 대한 정부 반응이 적절한가"),
    ],
}

INST_DIMENSIONS = [
    ("D1", "정책 피드백 제도", "정책 결과를 체계적으로 환류하는 공식 제도 (평가위원회, 환류 메커니즘, 성과관리)"),
    ("D2", "정책 실험 제도", "소규모 실험→확대의 제도적 경로 (규제샌드박스, 특구, 시범사업)"),
    ("D3", "시민참여 채널", "시민의 정책 피드백을 수집·반영하는 채널 (국민청원, 국민제안, 참여예산)"),
    ("D4", "AI/디지털 거버넌스", "AI·디지털 기술 기반 정책 의사결정 구조 (전담 조직, 데이터 플랫폼)"),
]

OUTPUT_DIR = Path(__file__).resolve().parent / "tables"
OUTPUT_DIR.mkdir(exist_ok=True)


# ── 프롬프트 생성 ──

def build_acw_prompt(gov: str) -> str:
    lines = [
        "당신은 한국 행정학 전문가입니다. Gupta et al.(2010)의 Adaptive Capacity Wheel(ACW) 프레임워크를 사용하여 "
        f"**{gov}** 정부의 적응 역량을 평가해주세요.",
        "",
        "## 점수 척도",
        "- +2: 매우 긍정적 (해당 기준이 체계적·제도적으로 구현되어 작동)",
        "- +1: 긍정적 (해당 기준이 부분적으로 존재하나 일관성 부족)",
        "-  0: 중립/해당 없음",
        "- -1: 부정적 (해당 기준과 반대되는 특성이 관찰됨)",
        "- -2: 매우 부정적 (해당 기준이 구조적으로 억제됨)",
        "",
        "## 평가 기준",
        "아래 22개 기준 각각에 대해 점수(-2~+2)와 간단한 근거(1-2문장)를 제시해주세요.",
        "",
    ]
    for dim, criteria in ACW_CRITERIA.items():
        lines.append(f"### {dim}")
        for code, name, definition in criteria:
            lines.append(f"- **{code}. {name}**: {definition}")
        lines.append("")

    lines.extend([
        "## 출력 형식 (반드시 이 JSON 형식을 준수)",
        "```json",
        "{",
        '  "government": "정부명",',
        '  "scores": {',
        '    "V1": {"score": 0, "rationale": "근거"},',
        '    "V2": {"score": 0, "rationale": "근거"},',
        "    ...(22개 모두)",
        "  }",
        "}",
        "```",
        "",
        "주의사항:",
        "- 정치적 편향 없이 객관적으로 평가하세요.",
        "- 공식 문서, 감사원 보고서, 국회 회의록, 학술 논문에 근거하세요.",
        "- 이재명 정부(2025-)는 임기 초반 데이터에 한정하여 평가하세요.",
        "- 반드시 JSON만 출력하세요. 다른 텍스트를 포함하지 마세요.",
    ])
    return "\n".join(lines)


def build_inst_prompt(gov: str) -> str:
    lines = [
        "당신은 한국 행정학 전문가입니다. Argyris & Schön(1978)의 조직학습 이론에 기반하여 "
        f"**{gov}** 정부의 제도적 적응 메커니즘을 평가해주세요.",
        "",
        "## 점수 척도 (3점)",
        "- 0: 미설계 (해당 제도가 공식적으로 존재하지 않거나 극히 초보적)",
        "- 1: 부분적 (제도가 존재하나 체계성·일관성·실효성이 부족)",
        "- 2: 체계적 (제도가 법적 근거를 갖추고 체계적·지속적으로 운영)",
        "",
        "## 평가 차원",
    ]
    for code, name, definition in INST_DIMENSIONS:
        lines.append(f"- **{code}. {name}**: {definition}")

    lines.extend([
        "",
        "## 출력 형식 (반드시 이 JSON 형식을 준수)",
        "```json",
        "{",
        '  "government": "정부명",',
        '  "scores": {',
        '    "D1": {"score": 0, "rationale": "근거"},',
        '    "D2": {"score": 0, "rationale": "근거"},',
        '    "D3": {"score": 0, "rationale": "근거"},',
        '    "D4": {"score": 0, "rationale": "근거"}',
        "  }",
        "}",
        "```",
        "",
        "주의사항:",
        "- 정치적 편향 없이 객관적으로 평가하세요.",
        "- 공식 문서, 학술 논문, 감사원 보고서에 근거하세요.",
        "- 반드시 JSON만 출력하세요. 다른 텍스트를 포함하지 마세요.",
    ])
    return "\n".join(lines)


# ── API 클라이언트 ──

def _repair_json(raw: str) -> str:
    """손상된 JSON 문자열 복구 (trailing comma, truncated strings 등)"""
    s = raw.strip()

    # 1) trailing comma 제거: ,\s*} 또는 ,\s*]
    s = re.sub(r",\s*([}\]])", r"\1", s)

    # 2) truncated field names 복구: "rational" → "rationale" (가장 흔한 케이스)
    s = re.sub(r'"rational"(\s*:)', r'"rationale"\1', s)

    # 3) 닫히지 않은 문자열 복구
    #    JSON에서 { 다음에 " 로 시작했는데 줄 끝에서 닫히지 않은 경우
    #    각 줄에서 홀수 개의 따옴표가 있으면 끝에 " 추가
    lines = s.split("\n")
    fixed_lines = []
    for line in lines:
        # 줄에서 이스케이프되지 않은 따옴표 수 카운트
        unescaped_quotes = len(re.findall(r'(?<!\\)"', line))
        if unescaped_quotes % 2 != 0:
            # 홀수 = 닫히지 않은 문자열 → 끝에 " 추가
            line = line.rstrip()
            # 마지막 문자가 , } ] 이면 그 앞에 " 삽입
            if line and line[-1] in (",", "}", "]"):
                line = line[:-1] + '"' + line[-1]
            else:
                line = line + '"'
        fixed_lines.append(line)
    s = "\n".join(fixed_lines)

    # 4) 닫히지 않은 중괄호/대괄호 복구
    open_braces = s.count("{") - s.count("}")
    open_brackets = s.count("[") - s.count("]")
    if open_braces > 0:
        s = s.rstrip()
        # 마지막 완전한 항목 뒤에 닫기
        s += "\n" + "}" * open_braces
    if open_brackets > 0:
        s += "]" * open_brackets

    # 5) trailing comma 한번 더 정리 (복구 과정에서 생길 수 있음)
    s = re.sub(r",\s*([}\]])", r"\1", s)

    return s


def extract_json(text: str) -> dict:
    """응답 텍스트에서 JSON 추출 (thinking 블록 등 노이즈 제거, 손상된 JSON 복구)"""
    candidates = []

    # ```json ... ``` 블록 시도
    m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if m:
        candidates.append(m.group(1).strip())

    # { ... } 블록 추출 (thinking 텍스트 앞뒤 무시)
    m = re.search(r"\{[\s\S]*\"scores\"[\s\S]*\}", text)
    if m:
        candidates.append(m.group(0))

    # "scores"가 포함된 { 부터 끝까지 (truncated JSON 대비)
    m = re.search(r'(\{[\s\S]*"scores"[\s\S]*)', text)
    if m:
        candidates.append(m.group(1))

    # 전체 텍스트가 JSON인 경우
    stripped = text.strip()
    if stripped.startswith("{"):
        candidates.append(stripped)

    # 각 후보에 대해 파싱 시도 (원본 → 복구)
    for candidate in candidates:
        # 원본 시도
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        # 복구 후 시도
        try:
            repaired = _repair_json(candidate)
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"JSON을 추출할 수 없습니다: {text[:300]}...")


def call_openai(prompt: str) -> str:
    """OpenAI GPT API 호출"""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.2")
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "당신은 한국 행정학·정책학 전문가입니다. 요청된 형식에 맞춰 정확히 응답하세요."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_completion_tokens": 8192,
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_claude(prompt: str) -> str:
    """Anthropic Claude API 호출"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 4096,
            "system": "당신은 한국 행정학·정책학 전문가입니다. 요청된 형식에 맞춰 정확히 응답하세요.",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]


def call_grok(prompt: str) -> str:
    """xAI Grok API 호출 (OpenAI-compatible)"""
    api_key = os.getenv("XAI_API_KEY")
    model = os.getenv("GROK_MODEL", "grok-4-fast-reasoning-20251119")
    resp = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "당신은 한국 행정학·정책학 전문가입니다. 요청된 형식에 맞춰 정확히 응답하세요."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_clova(prompt: str) -> str:
    """CLOVA Studio HCX-007 API 호출"""
    api_key = os.getenv("CLOVA_STUDIO_API_KEY")
    model = os.getenv("CLOVA_STUDIO_MODEL", "HCX-007")
    base_url = (os.getenv("CLOVA_STUDIO_BASE_URL") or "https://clovastudio.stream.ntruss.com").rstrip("/")

    resp = requests.post(
        f"{base_url}/v3/chat-completions/{model}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": "당신은 한국 행정학·정책학 전문가입니다. 요청된 형식에 맞춰 정확히 응답하세요."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "thinking": {"type": "medium"},
        },
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    # CLOVA Studio v3 응답 구조
    result = data.get("result", data)
    message = result.get("message", {})
    return message.get("content", "")


MODEL_CALLERS = {
    "gpt": ("GPT-5.1", call_openai),
    "claude": ("Claude Sonnet 4.5", call_claude),
    "grok": ("Grok-4", call_grok),
    "clova": ("HyperCLOVA HCX-007", call_clova),
}


# ── 실행 로직 ──

def _print(msg: str) -> None:
    """Flush-safe print for background execution"""
    print(msg, flush=True)


def score_one(model_key: str, prompt: str, gov: str, analysis: str, retry: int = 2) -> Optional[dict]:
    """단일 모델의 단일 정부 평가 실행"""
    label, caller = MODEL_CALLERS[model_key]
    for attempt in range(retry + 1):
        try:
            _print(f"  [{label}] {gov} 평가 중... (시도 {attempt+1})")
            raw = caller(prompt)
            result = extract_json(raw)
            _print(f"  [{label}] {gov} 완료 ✓")
            return result
        except Exception as e:
            _print(f"  [{label}] {gov} 오류 (시도 {attempt+1}): {e}")
            if attempt < retry:
                time.sleep(3 * (attempt + 1))
    _print(f"  [{label}] {gov} 최종 실패 ✗")
    return None


def run_scoring(models: List[str], analysis: str) -> Dict[str, Dict[str, dict]]:
    """
    전체 스코어링 실행.
    Returns: {model_key: {gov: {scores: ...}}}
    """
    results: Dict[str, Dict[str, dict]] = {}

    for model_key in models:
        label, _ = MODEL_CALLERS[model_key]
        _print(f"\n{'='*60}")
        _print(f"모델: {label}")
        _print(f"{'='*60}")
        results[model_key] = {}

        for gov in GOVERNMENTS:
            if analysis == "acw":
                prompt = build_acw_prompt(gov)
            else:
                prompt = build_inst_prompt(gov)

            result = score_one(model_key, prompt, gov, analysis)
            if result:
                results[model_key][gov] = result
            time.sleep(1)  # rate limit

    return results


# ── 통계 분석 ──

def fleiss_kappa(ratings_matrix: List[List[int]], k: int) -> float:
    """
    Fleiss' kappa 계산.
    ratings_matrix: N개 항목 × k개 카테고리의 빈도 행렬
    k: 카테고리 수
    """
    N = len(ratings_matrix)
    n = sum(ratings_matrix[0])  # 코더 수

    if N == 0 or n <= 1:
        return 0.0

    # 각 항목의 관찰 일치도
    P_i = []
    for row in ratings_matrix:
        sum_sq = sum(r * r for r in row)
        P_i.append((sum_sq - n) / (n * (n - 1)))

    P_bar = sum(P_i) / N

    # 각 카테고리의 비율
    p_j = []
    for j in range(k):
        total_j = sum(row[j] for row in ratings_matrix)
        p_j.append(total_j / (N * n))

    P_e = sum(p * p for p in p_j)

    if abs(1 - P_e) < 1e-10:
        return 1.0 if abs(P_bar - 1.0) < 1e-10 else 0.0

    return (P_bar - P_e) / (1 - P_e)


def compute_acw_reliability(results: Dict[str, Dict[str, dict]]) -> Dict[str, Any]:
    """ACW 점수의 코더 간 신뢰도 계산"""
    models = list(results.keys())
    n_coders = len(models)
    criteria_codes = [code for criteria in ACW_CRITERIA.values() for code, _, _ in criteria]

    # 점수 범위: -2 ~ +2 → 카테고리 5개 (index 0~4)
    score_to_cat = {-2: 0, -1: 1, 0: 2, 1: 3, 2: 4}
    n_categories = 5

    gov_kappas = {}
    all_ratings = []

    for gov in GOVERNMENTS:
        ratings_matrix = []
        for code in criteria_codes:
            row = [0] * n_categories
            for model_key in models:
                gov_data = results.get(model_key, {}).get(gov, {})
                scores = gov_data.get("scores", {})
                item = scores.get(code, {})
                score = item.get("score", 0)
                score = max(-2, min(2, int(score)))
                cat = score_to_cat[score]
                row[cat] += 1
            ratings_matrix.append(row)
            all_ratings.append(row)

        kappa = fleiss_kappa(ratings_matrix, n_categories)
        gov_kappas[gov] = round(kappa, 3)

    overall_kappa = fleiss_kappa(all_ratings, n_categories)

    return {
        "n_coders": n_coders,
        "n_items_per_gov": len(criteria_codes),
        "overall_kappa": round(overall_kappa, 3),
        "gov_kappas": gov_kappas,
        "interpretation": interpret_kappa(overall_kappa),
    }


def compute_inst_reliability(results: Dict[str, Dict[str, dict]]) -> Dict[str, Any]:
    """제도적 구조 점수의 코더 간 신뢰도 계산"""
    models = list(results.keys())
    n_coders = len(models)
    dim_codes = [code for code, _, _ in INST_DIMENSIONS]

    score_to_cat = {0: 0, 1: 1, 2: 2}
    n_categories = 3

    all_ratings = []
    for gov in GOVERNMENTS:
        for code in dim_codes:
            row = [0] * n_categories
            for model_key in models:
                gov_data = results.get(model_key, {}).get(gov, {})
                scores = gov_data.get("scores", {})
                item = scores.get(code, {})
                score = item.get("score", 0)
                score = max(0, min(2, int(score)))
                cat = score_to_cat[score]
                row[cat] += 1
            all_ratings.append(row)

    overall_kappa = fleiss_kappa(all_ratings, n_categories)

    return {
        "n_coders": n_coders,
        "overall_kappa": round(overall_kappa, 3),
        "interpretation": interpret_kappa(overall_kappa),
    }


def interpret_kappa(kappa: float) -> str:
    if kappa < 0:
        return "일치도 없음 (poor)"
    elif kappa < 0.21:
        return "약한 일치 (slight)"
    elif kappa < 0.41:
        return "보통 일치 (fair)"
    elif kappa < 0.61:
        return "중간 일치 (moderate)"
    elif kappa < 0.81:
        return "상당한 일치 (substantial)"
    else:
        return "거의 완벽한 일치 (almost perfect)"


# ── 결과 집계 ──

def compute_consensus_scores(results: Dict[str, Dict[str, dict]], criteria_codes: List[str]) -> Dict[str, Dict[str, float]]:
    """모델 간 합의 점수(평균) 계산"""
    models = list(results.keys())
    consensus = {}

    for gov in GOVERNMENTS:
        scores = {}
        for code in criteria_codes:
            values = []
            for model_key in models:
                gov_data = results.get(model_key, {}).get(gov, {})
                item = gov_data.get("scores", {}).get(code, {})
                score = item.get("score", None)
                if score is not None:
                    values.append(int(score))
            if values:
                scores[code] = round(sum(values) / len(values), 2)
            else:
                scores[code] = 0.0
        consensus[gov] = scores

    return consensus


def generate_report(acw_results: Optional[dict], inst_results: Optional[dict],
                    acw_reliability: Optional[dict], inst_reliability: Optional[dict],
                    acw_consensus: Optional[dict], inst_consensus: Optional[dict]) -> str:
    """마크다운 보고서 생성"""
    lines = [
        "# 다중 AI 코더 독립 평가 결과",
        "",
        f"> **생성일**: {time.strftime('%Y-%m-%d %H:%M')}",
        f"> **코더**: GPT-5.1, Claude Sonnet 4.5, Grok-4, HyperCLOVA HCX-007",
        "",
    ]

    if acw_results and acw_reliability:
        lines.extend(_acw_report_section(acw_results, acw_reliability, acw_consensus))
    if inst_results and inst_reliability:
        lines.extend(_inst_report_section(inst_results, inst_reliability, inst_consensus))

    return "\n".join(lines)


def _acw_report_section(results, reliability, consensus) -> List[str]:
    models = list(results.keys())
    criteria_codes = [code for criteria in ACW_CRITERIA.values() for code, _, _ in criteria]
    dim_criteria = {dim: [c[0] for c in criteria] for dim, criteria in ACW_CRITERIA.items()}

    lines = [
        "---",
        "## A. ACW 점수화 — 다중 코더 결과",
        "",
        f"### 코더 간 신뢰도 (Fleiss' kappa)",
        "",
        f"- **전체 kappa**: {reliability['overall_kappa']} ({reliability['interpretation']})",
        f"- **코더 수**: {reliability['n_coders']}",
        f"- **항목 수(정부당)**: {reliability['n_items_per_gov']}",
        "",
        "| 정부 | kappa |",
        "|------|-------|",
    ]
    for gov, k in reliability["gov_kappas"].items():
        lines.append(f"| {gov} | {k} |")

    # 모델별 총 평균
    lines.extend(["", "### 모델별 정부 총 평균 점수", ""])
    header = "| 정부 | " + " | ".join(MODEL_CALLERS[m][0] for m in models) + " | **합의(평균)** |"
    sep = "|------|" + "|".join(["------"] * len(models)) + "|---------|"
    lines.extend([header, sep])

    for gov in GOVERNMENTS:
        row = f"| {gov} |"
        for m in models:
            gov_data = results.get(m, {}).get(gov, {})
            scores = gov_data.get("scores", {})
            vals = [int(scores.get(c, {}).get("score", 0)) for c in criteria_codes]
            avg = sum(vals) / len(vals) if vals else 0
            row += f" {avg:+.2f} |"
        # consensus
        if consensus and gov in consensus:
            c_vals = list(consensus[gov].values())
            c_avg = sum(c_vals) / len(c_vals) if c_vals else 0
            row += f" **{c_avg:+.2f}** |"
        else:
            row += " — |"
        lines.append(row)

    # 차원별 합의 점수
    if consensus:
        lines.extend(["", "### 합의 점수 — 차원별 비교", ""])
        header = "| 차원 | " + " | ".join(gov.split("(")[0] for gov in GOVERNMENTS) + " |"
        sep = "|------|" + "|".join(["------"] * len(GOVERNMENTS)) + "|"
        lines.extend([header, sep])

        for dim, codes in dim_criteria.items():
            row = f"| {dim} |"
            for gov in GOVERNMENTS:
                vals = [consensus.get(gov, {}).get(c, 0) for c in codes]
                avg = sum(vals) / len(vals) if vals else 0
                row += f" {avg:+.2f} |"
            lines.append(row)

        # 총 평균 행
        row = "| **총 평균** |"
        for gov in GOVERNMENTS:
            all_vals = list(consensus.get(gov, {}).values())
            avg = sum(all_vals) / len(all_vals) if all_vals else 0
            row += f" **{avg:+.2f}** |"
        lines.append(row)

    lines.append("")
    return lines


def _inst_report_section(results, reliability, consensus) -> List[str]:
    models = list(results.keys())
    dim_codes = [code for code, _, _ in INST_DIMENSIONS]

    lines = [
        "---",
        "## D. 제도적 적응 메커니즘 — 다중 코더 결과",
        "",
        f"### 코더 간 신뢰도 (Fleiss' kappa)",
        "",
        f"- **전체 kappa**: {reliability['overall_kappa']} ({reliability['interpretation']})",
        "",
        "### 모델별 정부 합계 점수 (/8)",
        "",
    ]
    header = "| 정부 | " + " | ".join(MODEL_CALLERS[m][0] for m in models) + " | **합의** |"
    sep = "|------|" + "|".join(["------"] * len(models)) + "|--------|"
    lines.extend([header, sep])

    for gov in GOVERNMENTS:
        row = f"| {gov} |"
        for m in models:
            gov_data = results.get(m, {}).get(gov, {})
            scores = gov_data.get("scores", {})
            total = sum(scores.get(c, {}).get("score", 0) for c in dim_codes)
            row += f" {total} |"
        if consensus and gov in consensus:
            c_total = sum(consensus[gov].get(c, 0) for c in dim_codes)
            row += f" **{c_total:.1f}** |"
        else:
            row += " — |"
        lines.append(row)

    lines.append("")
    return lines


# ── 메인 ──

def main():
    parser = argparse.ArgumentParser(description="Multi-AI ACW/Institutional Scoring")
    parser.add_argument("--models", nargs="+", default=["gpt", "claude", "grok", "clova"],
                        choices=["gpt", "claude", "grok", "clova"],
                        help="사용할 모델 (기본: 전체)")
    parser.add_argument("--analysis", default="all", choices=["acw", "inst", "all"],
                        help="분석 유형 (기본: all)")
    args = parser.parse_args()

    _print("=" * 60)
    _print("Multi-AI ACW Scoring System")
    _print(f"모델: {', '.join(MODEL_CALLERS[m][0] for m in args.models)}")
    _print(f"분석: {args.analysis}")
    _print("=" * 60)

    acw_results = None
    inst_results = None
    acw_reliability = None
    inst_reliability = None
    acw_consensus = None
    inst_consensus = None

    criteria_codes = [code for criteria in ACW_CRITERIA.values() for code, _, _ in criteria]
    dim_codes = [code for code, _, _ in INST_DIMENSIONS]

    if args.analysis in ("acw", "all"):
        _print("\n▶ ACW 스코어링 시작")
        acw_results = run_scoring(args.models, "acw")

        # 원시 결과 저장
        with open(OUTPUT_DIR / "acw_raw_results.json", "w", encoding="utf-8") as f:
            json.dump(acw_results, f, ensure_ascii=False, indent=2)
        _print(f"\n원시 결과 저장: {OUTPUT_DIR / 'acw_raw_results.json'}")

        # 신뢰도 계산
        acw_reliability = compute_acw_reliability(acw_results)
        _print(f"\nACW Fleiss' kappa: {acw_reliability['overall_kappa']} ({acw_reliability['interpretation']})")

        # 합의 점수
        acw_consensus = compute_consensus_scores(acw_results, criteria_codes)

    if args.analysis in ("inst", "all"):
        _print("\n▶ 제도적 구조 스코어링 시작")
        inst_results = run_scoring(args.models, "inst")

        with open(OUTPUT_DIR / "inst_raw_results.json", "w", encoding="utf-8") as f:
            json.dump(inst_results, f, ensure_ascii=False, indent=2)
        _print(f"\n원시 결과 저장: {OUTPUT_DIR / 'inst_raw_results.json'}")

        inst_reliability = compute_inst_reliability(inst_results)
        _print(f"\n제도적 구조 Fleiss' kappa: {inst_reliability['overall_kappa']} ({inst_reliability['interpretation']})")

        inst_consensus = compute_consensus_scores(inst_results, dim_codes)

    # 보고서 생성
    report = generate_report(acw_results, inst_results, acw_reliability, inst_reliability, acw_consensus, inst_consensus)
    report_path = OUTPUT_DIR / "multi_ai_scoring_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    _print(f"\n보고서 저장: {report_path}")

    # 신뢰도 요약 저장
    reliability_data = {}
    if acw_reliability:
        reliability_data["acw"] = acw_reliability
    if inst_reliability:
        reliability_data["inst"] = inst_reliability
    with open(OUTPUT_DIR / "reliability_summary.json", "w", encoding="utf-8") as f:
        json.dump(reliability_data, f, ensure_ascii=False, indent=2)

    _print("\n" + "=" * 60)
    _print("완료!")
    _print("=" * 60)


if __name__ == "__main__":
    main()
