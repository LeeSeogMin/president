"""
Multi-AI 2-Panel Scoring v2: 5개 AI 모델을 독립 코더로 활용한 ACW/제도적/Lowi 점수화

Panel 1: 중앙정부 6개 대통령 — ACW(22기준) + 제도적 메커니즘(4차원)
Panel 2: 이재명 지방정부 (성남시장/경기도지사) — ACW sub-wheel + 제도적(기능적 등가) + Lowi 유형
모델: GPT-5.2, Claude Sonnet 4.6, Grok-4-1, HyperCLOVA HCX-007, Gemini 3 Flash

Usage:
    python ai_scoring_v2.py                          # 전체 실행
    python ai_scoring_v2.py --reuse-panel1           # 기존 Panel 1 결과 재사용
    python ai_scoring_v2.py --panel 1                # Panel 1만
    python ai_scoring_v2.py --panel 2                # Panel 2만
    python ai_scoring_v2.py --models gpt gemini      # 특정 모델만
    python ai_scoring_v2.py --analysis acw           # ACW만
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from dotenv import load_dotenv

# ── .env 로드 ──
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════

# Panel 1: 중앙정부
GOVERNMENTS = [
    "노무현(2003-2008)", "이명박(2008-2013)", "박근혜(2013-2017)",
    "문재인(2017-2022)", "윤석열(2022-2025)", "이재명(2025-)",
]

# Panel 2: 지방정부
LOCAL_GOVERNMENTS = [
    "이재명 성남시장(2010-2018)",
    "이재명 경기도지사(2018-2022)",
]

# ACW 22개 기준 (전체)
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

ALL_ACW_CODES = [code for criteria in ACW_CRITERIA.values() for code, _, _ in criteria]

# Panel 2 ACW 제외 기준
ACW_EXCLUDE_SEONGNAM: Set[str] = {"V2", "Re3", "L2"}  # 19/22
ACW_EXCLUDE_GYEONGGI: Set[str] = {"Re3", "L2"}        # 20/22

# Panel 1 제도적 메커니즘 (중앙정부)
INST_DIMENSIONS = [
    ("D1", "정책 피드백 제도", "정책 결과를 체계적으로 환류하는 공식 제도 (평가위원회, 환류 메커니즘, 성과관리)"),
    ("D2", "정책 실험 제도", "소규모 실험→확대의 제도적 경로 (규제샌드박스, 특구, 시범사업)"),
    ("D3", "시민참여 채널", "시민의 정책 피드백을 수집·반영하는 채널 (국민청원, 국민제안, 참여예산)"),
    ("D4", "AI/디지털 거버넌스", "AI·디지털 기술 기반 정책 의사결정 구조 (전담 조직, 데이터 플랫폼)"),
]

# Panel 2 제도적 메커니즘 (지방정부 – 기능적 등가성 적용)
INST_LOCAL_DIMENSIONS = [
    ("D1", "정책 피드백 제도", "정책 결과를 체계적으로 환류하는 공식 제도 (자체평가, 성과관리, 감사). 조례·규칙이 법률·대통령령과 기능적으로 등가함을 고려."),
    ("D2", "정책 실험 제도", "소규모 실험→확대의 제도적 경로 (시범사업, 파일럿, 특화사업). 지방정부 조례 기반 실험을 중앙의 법률 기반 실험과 기능적으로 등가하게 평가."),
    ("D3", "시민참여 채널", "시민의 정책 피드백을 수집·반영하는 채널 (주민참여예산, 시민감사관, 주민자치). 지방의회·위원회가 국회·국가위원회와 기능적으로 등가함을 고려."),
    ("D4", "디지털 거버넌스", "디지털 기술 기반 행정 의사결정 구조 (데이터 기반 행정, 디지털 민원, 공공플랫폼). 지방 수준 디지털 인프라를 중앙 수준과 기능적으로 등가하게 평가."),
]

# Panel 2 국정과제(시·도정과제) 유형 분류 (Lowi 분류)
AGENDA_CRITERIA = [
    ("E1", "분배정책 비율", "전체 과제 중 분배정책(배분적 정책)의 비율 (%)"),
    ("E2", "규제정책 비율", "전체 과제 중 규제정책의 비율 (%)"),
    ("E3", "재분배정책 비율", "전체 과제 중 재분배정책의 비율 (%)"),
    ("E4", "구성정책 비율", "전체 과제 중 구성정책(제도 설계)의 비율 (%)"),
    ("E5", "적응적 도구 비율", "전체 과제 중 적응적 정책 도구(파일럿, 데이터기반, 참여형, 실험적 접근)를 사용하는 과제의 비율 (%)"),
]

OUTPUT_DIR = Path(__file__).resolve().parent / "tables"
OUTPUT_DIR.mkdir(exist_ok=True)

DATA_DIR = Path(__file__).resolve().parent / "data"

# ═══════════════════════════════════════════════════════════
# API CLIENTS (5 models)
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = "당신은 한국 행정학·정책학 전문가입니다. 요청된 형식에 맞춰 정확히 응답하세요."


def call_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.2")
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_completion_tokens": 8192,
            "response_format": {"type": "json_object"},
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_claude(prompt: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 8192,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]


def call_grok(prompt: str) -> str:
    api_key = os.getenv("XAI_API_KEY")
    model = os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning")
    resp = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_completion_tokens": 8192,
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_clova(prompt: str) -> str:
    api_key = os.getenv("CLOVA_STUDIO_API_KEY")
    model = os.getenv("CLOVA_STUDIO_MODEL", "HCX-007")
    base_url = (os.getenv("CLOVA_STUDIO_BASE_URL") or "https://clovastudio.stream.ntruss.com").rstrip("/")
    resp = requests.post(
        f"{base_url}/v3/chat-completions/{model}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "thinking": {"type": "medium"},
        },
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    result = data.get("result", data)
    message = result.get("message", {})
    return message.get("content", "")


def call_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-3-flash-preview"
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        json={
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8192},
        },
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError(f"Gemini 응답에 candidates 없음: {data}")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise ValueError(f"Gemini 응답에 parts 없음: {candidates[0]}")
    return parts[0].get("text", "")


MODEL_CALLERS = {
    "gpt":    ("GPT-5.2",              call_openai),
    "claude": ("Claude Sonnet 4.6",    call_claude),
    "grok":   ("Grok-4-1",            call_grok),
    "clova":  ("HyperCLOVA HCX-007",  call_clova),
    "gemini": ("Gemini 3 Flash",       call_gemini),
}


# ═══════════════════════════════════════════════════════════
# JSON PARSER (강화 버전)
# ═══════════════════════════════════════════════════════════

def _repair_json(raw: str) -> str:
    s = raw.strip()
    s = re.sub(r",\s*([}\]])", r"\1", s)
    s = re.sub(r'"rational"(\s*:)', r'"rationale"\1', s)

    lines = s.split("\n")
    fixed_lines = []
    for line in lines:
        unescaped_quotes = len(re.findall(r'(?<!\\)"', line))
        if unescaped_quotes % 2 != 0:
            line = line.rstrip()
            if line and line[-1] in (",", "}", "]"):
                line = line[:-1] + '"' + line[-1]
            else:
                line = line + '"'
        fixed_lines.append(line)
    s = "\n".join(fixed_lines)

    open_braces = s.count("{") - s.count("}")
    open_brackets = s.count("[") - s.count("]")
    if open_braces > 0:
        s = s.rstrip()
        s += "\n" + "}" * open_braces
    if open_brackets > 0:
        s += "]" * open_brackets

    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s


def extract_json(text: str) -> dict:
    candidates = []

    m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if m:
        candidates.append(m.group(1).strip())

    m = re.search(r"\{[\s\S]*\"scores\"[\s\S]*\}", text)
    if m:
        candidates.append(m.group(0))

    m = re.search(r'(\{[\s\S]*"scores"[\s\S]*)', text)
    if m:
        candidates.append(m.group(1))

    stripped = text.strip()
    if stripped.startswith("{"):
        candidates.append(stripped)

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        try:
            repaired = _repair_json(candidate)
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"JSON을 추출할 수 없습니다: {text[:300]}...")


# ═══════════════════════════════════════════════════════════
# LOCAL CONTEXT LOADER
# ═══════════════════════════════════════════════════════════

def load_local_context() -> str:
    ctx_path = DATA_DIR / "ljm_local_context.md"
    if ctx_path.exists():
        return ctx_path.read_text(encoding="utf-8")
    return ""


# ═══════════════════════════════════════════════════════════
# PROMPT BUILDERS
# ═══════════════════════════════════════════════════════════

def _rationale_instruction() -> str:
    return (
        "- rationale은 반드시 1문장, 최대 50자로 작성하세요.\n"
        "- 반드시 유효한 JSON만 출력하세요. 다른 텍스트를 포함하지 마세요."
    )


# ── Panel 1: ACW (중앙정부) ──

def build_acw_prompt(gov: str) -> str:
    is_ljm = "이재명" in gov
    local_ctx = load_local_context() if is_ljm else ""

    lines = [
        "당신은 한국 행정학 전문가입니다. Gupta et al.(2010)의 Adaptive Capacity Wheel(ACW) 프레임워크를 사용하여 "
        f"**{gov}** 정부의 적응 역량을 평가해주세요.",
        "",
    ]

    if is_ljm and local_ctx:
        lines.extend([
            "## 참고: 이재명의 지방행정 경력 컨텍스트",
            "이재명 대통령은 성남시장(2010-2018)과 경기도지사(2018-2022)를 역임했습니다. "
            "아래는 지방행정 경력의 핵심 사실입니다. 대통령 정부 평가 시 이 경력에서의 정책 연속성·경험 이전을 참고할 수 있습니다.",
            "",
            local_ctx[:2000],
            "",
        ])

    lines.extend([
        "## 점수 척도",
        "- +2: 매우 긍정적 (해당 기준이 체계적·제도적으로 구현되어 작동)",
        "- +1: 긍정적 (해당 기준이 부분적으로 존재하나 일관성 부족)",
        "-  0: 중립/해당 없음",
        "- -1: 부정적 (해당 기준과 반대되는 특성이 관찰됨)",
        "- -2: 매우 부정적 (해당 기준이 구조적으로 억제됨)",
        "",
        "## 평가 기준",
        "아래 22개 기준 각각에 대해 점수(-2~+2)와 간단한 근거를 제시해주세요.",
        "",
    ])
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
        _rationale_instruction(),
    ])
    return "\n".join(lines)


# ── Panel 2: ACW sub-wheel (지방정부) ──

def _get_acw_exclude(gov: str) -> Set[str]:
    if "성남" in gov:
        return ACW_EXCLUDE_SEONGNAM
    elif "경기" in gov:
        return ACW_EXCLUDE_GYEONGGI
    return set()


def _get_acw_local_codes(gov: str) -> List[str]:
    exclude = _get_acw_exclude(gov)
    return [c for c in ALL_ACW_CODES if c not in exclude]


def build_acw_local_prompt(gov: str) -> str:
    exclude = _get_acw_exclude(gov)
    local_ctx = load_local_context()
    applicable_codes = _get_acw_local_codes(gov)
    n_codes = len(applicable_codes)

    lines = [
        "당신은 한국 행정학 전문가입니다. Gupta et al.(2010)의 Adaptive Capacity Wheel(ACW) 프레임워크를 사용하여 "
        f"**{gov}** 시기의 적응 역량을 평가해주세요.",
        "",
        f"이 평가는 지방정부 수준이므로, 중앙정부에만 해당하는 기준을 제외한 {n_codes}개 기준으로 평가합니다.",
        f"제외 기준: {', '.join(sorted(exclude))}",
        "",
    ]

    if local_ctx:
        lines.extend([
            "## 참고: 이재명 지방행정 경력 팩트시트",
            local_ctx[:3000],
            "",
        ])

    lines.extend([
        "## 점수 척도",
        "- +2: 매우 긍정적 (해당 기준이 체계적·제도적으로 구현되어 작동)",
        "- +1: 긍정적 (해당 기준이 부분적으로 존재하나 일관성 부족)",
        "-  0: 중립/해당 없음",
        "- -1: 부정적 (해당 기준과 반대되는 특성이 관찰됨)",
        "- -2: 매우 부정적 (해당 기준이 구조적으로 억제됨)",
        "",
        "## 평가 기준",
        f"아래 {n_codes}개 기준 각각에 대해 점수(-2~+2)와 간단한 근거를 제시해주세요.",
        "",
    ])
    for dim, criteria in ACW_CRITERIA.items():
        applicable = [(c, n, d) for c, n, d in criteria if c not in exclude]
        if applicable:
            lines.append(f"### {dim}")
            for code, name, definition in applicable:
                lines.append(f"- **{code}. {name}**: {definition}")
            lines.append("")

    example_codes = applicable_codes[:2]
    lines.extend([
        "## 출력 형식 (반드시 이 JSON 형식을 준수)",
        "```json",
        "{",
        f'  "government": "{gov}",',
        '  "scores": {',
    ])
    for ec in example_codes:
        lines.append(f'    "{ec}": {{"score": 0, "rationale": "근거"}},')
    lines.append(f"    ...({n_codes}개 모두)")
    lines.extend([
        "  }",
        "}",
        "```",
        "",
        "주의사항:",
        "- 지방정부 수준의 행정 역량을 평가하세요. 중앙정부 기준으로 판단하지 마세요.",
        "- 공식 문서, 조례, 감사보고서, 언론보도, 학술 논문에 근거하세요.",
        _rationale_instruction(),
    ])
    return "\n".join(lines)


# ── Panel 1: 제도적 메커니즘 (중앙정부) ──

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
        _rationale_instruction(),
    ])
    return "\n".join(lines)


# ── Panel 2: 제도적 메커니즘 (지방정부 – 기능적 등가성) ──

def build_inst_local_prompt(gov: str) -> str:
    local_ctx = load_local_context()
    lines = [
        "당신은 한국 행정학 전문가입니다. Argyris & Schön(1978)의 조직학습 이론에 기반하여 "
        f"**{gov}** 시기의 제도적 적응 메커니즘을 평가해주세요.",
        "",
        "## 기능적 등가성 원칙",
        "지방정부 제도를 중앙정부와 비교 가능하게 평가하기 위해 다음의 기능적 등가성을 적용합니다:",
        "- 법률 ↔ 조례: 중앙정부의 법률 제정은 지방정부의 조례 제정과 기능적으로 등가",
        "- 대통령령 ↔ 시행규칙: 중앙 행정입법은 지방 규칙·지침과 기능적으로 등가",
        "- 국가위원회 ↔ 지방위원회: 국무회의·위원회는 지방의 도정회의·위원회와 기능적으로 등가",
        "",
    ]

    if local_ctx:
        lines.extend([
            "## 참고: 이재명 지방행정 경력 팩트시트",
            local_ctx[:2000],
            "",
        ])

    lines.extend([
        "## 점수 척도 (3점)",
        "- 0: 미설계 (해당 제도가 공식적으로 존재하지 않거나 극히 초보적)",
        "- 1: 부분적 (제도가 존재하나 체계성·일관성·실효성이 부족)",
        "- 2: 체계적 (제도가 조례 근거를 갖추고 체계적·지속적으로 운영)",
        "",
        "## 평가 차원",
    ])
    for code, name, definition in INST_LOCAL_DIMENSIONS:
        lines.append(f"- **{code}. {name}**: {definition}")

    lines.extend([
        "",
        "## 출력 형식 (반드시 이 JSON 형식을 준수)",
        "```json",
        "{",
        f'  "government": "{gov}",',
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
        "- 지방정부 수준의 제도적 메커니즘을 평가하세요.",
        "- 조례, 자체 평가 결과, 지방의회 회의록, 감사보고서에 근거하세요.",
        _rationale_instruction(),
    ])
    return "\n".join(lines)


# ── Panel 2: 국정과제(시·도정과제) 유형 분류 (Lowi) ──

def build_agenda_prompt(gov: str) -> str:
    local_ctx = load_local_context()
    lines = [
        "당신은 한국 행정학 전문가입니다. Theodore Lowi(1964)의 정책유형 분류 이론을 사용하여 "
        f"**{gov}** 시기의 주요 정책과제(시정/도정 공약 및 핵심과제)를 유형별로 분류하고, "
        "적응적 정책 도구의 사용 비율을 평가해주세요.",
        "",
    ]

    if local_ctx:
        lines.extend([
            "## 참고: 이재명 지방행정 경력 팩트시트",
            local_ctx[:2000],
            "",
        ])

    lines.extend([
        "## Lowi 정책유형 정의",
        "- **분배정책**: 특정 집단에 재화·서비스를 배분 (보조금, 인프라 투자, 공공서비스 제공)",
        "- **규제정책**: 행위를 제한·통제 (규제, 단속, 인허가)",
        "- **재분배정책**: 자원을 한 집단에서 다른 집단으로 이전 (복지, 기본소득, 누진세)",
        "- **구성정책**: 제도·구조·규칙을 설계·변경 (조직 개편, 조례 제정, 거버넌스 개혁)",
        "",
        "## 적응적 정책 도구 정의",
        "다음 중 하나 이상을 사용하는 과제를 '적응적 도구 사용'으로 분류:",
        "- 파일럿/시범사업 → 확대",
        "- 데이터 기반 의사결정",
        "- 시민 참여형 설계",
        "- 실험적·혁신적 접근 (기존에 없던 새로운 방식)",
        "",
        "## 평가 항목",
    ])
    for code, name, definition in AGENDA_CRITERIA:
        lines.append(f"- **{code}. {name}**: {definition}")

    lines.extend([
        "",
        "## 출력 형식 (반드시 이 JSON 형식을 준수)",
        "```json",
        "{",
        f'  "government": "{gov}",',
        '  "total_agenda_items": 0,',
        '  "scores": {',
        '    "E1": {"score": 0, "rationale": "근거"},',
        '    "E2": {"score": 0, "rationale": "근거"},',
        '    "E3": {"score": 0, "rationale": "근거"},',
        '    "E4": {"score": 0, "rationale": "근거"},',
        '    "E5": {"score": 0, "rationale": "근거"}',
        "  }",
        "}",
        "```",
        "",
        "주의사항:",
        "- score 값은 해당 유형의 비율(%)을 정수로 기입하세요 (E1+E2+E3+E4 = 100%).",
        "- E5는 별도 계산 (적응적 도구 사용 과제 / 전체 과제 × 100).",
        "- 지방정부 수준의 공약·과제를 기준으로 분류하세요.",
        _rationale_instruction(),
    ])
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# EXECUTION ENGINE
# ═══════════════════════════════════════════════════════════

def _print(msg: str) -> None:
    print(msg, flush=True)


@dataclass
class CompletionTracker:
    """모델×정부×분석별 성공/실패 추적"""
    results: Dict[str, Dict[str, Dict[str, Any]]] = field(default_factory=dict)
    # results[panel][model_key][gov] = {"status": "success"/"fail", "data": ..., "error": ...}

    def record(self, panel: str, model_key: str, gov: str, data: Optional[dict], error: str = ""):
        self.results.setdefault(panel, {}).setdefault(model_key, {})[gov] = {
            "status": "success" if data else "fail",
            "data": data,
            "error": error,
        }

    def get_data(self, panel: str, model_key: str, gov: str) -> Optional[dict]:
        return self.results.get(panel, {}).get(model_key, {}).get(gov, {}).get("data")

    def get_failures(self, panel: str) -> List[Tuple[str, str]]:
        """실패한 (model_key, gov) 목록 반환"""
        failures = []
        for model_key, govs in self.results.get(panel, {}).items():
            for gov, info in govs.items():
                if info["status"] == "fail":
                    failures.append((model_key, gov))
        return failures

    def get_panel_results(self, panel: str) -> Dict[str, Dict[str, dict]]:
        """패널의 성공 데이터를 {model_key: {gov: data}} 형태로 반환"""
        out: Dict[str, Dict[str, dict]] = {}
        for model_key, govs in self.results.get(panel, {}).items():
            out[model_key] = {}
            for gov, info in govs.items():
                if info["data"]:
                    out[model_key][gov] = info["data"]
        return out

    def completion_matrix(self) -> dict:
        """전체 완료 매트릭스 생성"""
        matrix = {}
        for panel, models in self.results.items():
            matrix[panel] = {}
            for model_key, govs in models.items():
                matrix[panel][model_key] = {
                    gov: info["status"] for gov, info in govs.items()
                }
        return matrix

    def completion_rate(self) -> Tuple[int, int]:
        total = 0
        success = 0
        for panel, models in self.results.items():
            for model_key, govs in models.items():
                for gov, info in govs.items():
                    total += 1
                    if info["status"] == "success":
                        success += 1
        return success, total


def score_one(model_key: str, prompt: str, gov: str, analysis: str,
              max_retries: int = 5) -> Tuple[Optional[dict], str]:
    """단일 모델의 단일 정부 평가 실행 (지수 백오프, 최대 5회 재시도)"""
    label, caller = MODEL_CALLERS[model_key]
    last_error = ""

    for attempt in range(max_retries):
        try:
            _print(f"  [{label}] {gov} ({analysis}) 평가 중... (시도 {attempt+1}/{max_retries})")
            raw = caller(prompt)
            result = extract_json(raw)

            # 기본 유효성 검증: scores 키가 있고 비어있지 않은지 확인
            if "scores" not in result or not result["scores"]:
                raise ValueError("scores 필드가 비어있습니다")

            _print(f"  [{label}] {gov} ({analysis}) 완료 ✓")
            return result, ""
        except Exception as e:
            last_error = str(e)
            _print(f"  [{label}] {gov} ({analysis}) 오류 (시도 {attempt+1}): {last_error}")
            if attempt < max_retries - 1:
                wait = 3 * (2 ** attempt)  # 3, 6, 12, 24, 48
                _print(f"    → {wait}초 대기 후 재시도...")
                time.sleep(wait)

    _print(f"  [{label}] {gov} ({analysis}) 최종 실패 ✗")
    return None, last_error


def _is_acw_complete(data: dict, expected_codes: List[str]) -> bool:
    """ACW 결과가 모든 기대 코드를 포함하는지 확인"""
    scores = data.get("scores", {})
    return all(code in scores for code in expected_codes)


# ═══════════════════════════════════════════════════════════
# PANEL 1: 중앙정부
# ═══════════════════════════════════════════════════════════

def run_panel1(models: List[str], analysis: str, tracker: CompletionTracker,
               reuse_acw: Optional[dict] = None, reuse_inst: Optional[dict] = None):
    """Panel 1 (중앙정부) 스코어링"""

    if analysis in ("acw", "all"):
        _print("\n▶ Panel 1: ACW 스코어링")
        _print("=" * 60)
        for model_key in models:
            label, _ = MODEL_CALLERS[model_key]
            for gov in GOVERNMENTS:
                # 재사용 가능한 결과 확인
                if reuse_acw:
                    existing = reuse_acw.get(model_key, {}).get(gov)
                    if existing and _is_acw_complete(existing, ALL_ACW_CODES):
                        _print(f"  [{label}] {gov} (ACW) 기존 결과 재사용 ✓")
                        tracker.record("panel1_acw", model_key, gov, existing)
                        continue

                prompt = build_acw_prompt(gov)
                data, err = score_one(model_key, prompt, gov, "ACW")
                tracker.record("panel1_acw", model_key, gov, data, err)
                time.sleep(1)

    if analysis in ("inst", "all"):
        _print("\n▶ Panel 1: 제도적 메커니즘 스코어링")
        _print("=" * 60)
        for model_key in models:
            label, _ = MODEL_CALLERS[model_key]
            for gov in GOVERNMENTS:
                # 재사용 가능한 결과 확인
                if reuse_inst:
                    existing = reuse_inst.get(model_key, {}).get(gov)
                    if existing and "scores" in existing and existing["scores"]:
                        _print(f"  [{label}] {gov} (INST) 기존 결과 재사용 ✓")
                        tracker.record("panel1_inst", model_key, gov, existing)
                        continue

                prompt = build_inst_prompt(gov)
                data, err = score_one(model_key, prompt, gov, "INST")
                tracker.record("panel1_inst", model_key, gov, data, err)
                time.sleep(1)


# ═══════════════════════════════════════════════════════════
# PANEL 2: 지방정부
# ═══════════════════════════════════════════════════════════

def run_panel2(models: List[str], analysis: str, tracker: CompletionTracker):
    """Panel 2 (지방정부) 스코어링"""

    if analysis in ("acw", "all"):
        _print("\n▶ Panel 2: ACW sub-wheel 스코어링 (지방정부)")
        _print("=" * 60)
        for model_key in models:
            label, _ = MODEL_CALLERS[model_key]
            for gov in LOCAL_GOVERNMENTS:
                prompt = build_acw_local_prompt(gov)
                data, err = score_one(model_key, prompt, gov, "ACW-local")
                tracker.record("panel2_acw", model_key, gov, data, err)
                time.sleep(1)

    if analysis in ("inst", "all"):
        _print("\n▶ Panel 2: 제도적 메커니즘 스코어링 (지방정부, 기능적 등가)")
        _print("=" * 60)
        for model_key in models:
            label, _ = MODEL_CALLERS[model_key]
            for gov in LOCAL_GOVERNMENTS:
                prompt = build_inst_local_prompt(gov)
                data, err = score_one(model_key, prompt, gov, "INST-local")
                tracker.record("panel2_inst", model_key, gov, data, err)
                time.sleep(1)

    if analysis in ("agenda", "all"):
        _print("\n▶ Panel 2: Lowi 정책유형 분류 스코어링 (지방정부)")
        _print("=" * 60)
        for model_key in models:
            label, _ = MODEL_CALLERS[model_key]
            for gov in LOCAL_GOVERNMENTS:
                prompt = build_agenda_prompt(gov)
                data, err = score_one(model_key, prompt, gov, "AGENDA")
                tracker.record("panel2_agenda", model_key, gov, data, err)
                time.sleep(1)


# ═══════════════════════════════════════════════════════════
# RETRY GAPS
# ═══════════════════════════════════════════════════════════

PROMPT_BUILDERS = {
    "panel1_acw": lambda gov: build_acw_prompt(gov),
    "panel1_inst": lambda gov: build_inst_prompt(gov),
    "panel2_acw": lambda gov: build_acw_local_prompt(gov),
    "panel2_inst": lambda gov: build_inst_local_prompt(gov),
    "panel2_agenda": lambda gov: build_agenda_prompt(gov),
}

ANALYSIS_LABELS = {
    "panel1_acw": "ACW",
    "panel1_inst": "INST",
    "panel2_acw": "ACW-local",
    "panel2_inst": "INST-local",
    "panel2_agenda": "AGENDA",
}


def retry_gaps(tracker: CompletionTracker, max_rounds: int = 3):
    """실패 항목 자동 재시도 (최대 3라운드)"""
    for round_num in range(1, max_rounds + 1):
        all_failures = []
        for panel_key in PROMPT_BUILDERS:
            failures = tracker.get_failures(panel_key)
            all_failures.extend([(panel_key, m, g) for m, g in failures])

        if not all_failures:
            _print(f"\n✓ 모든 항목 완료 — 재시도 불필요")
            return

        _print(f"\n▶ 재시도 라운드 {round_num}/{max_rounds}: {len(all_failures)}건 실패 항목")
        _print("=" * 60)

        for panel_key, model_key, gov in all_failures:
            label = ANALYSIS_LABELS.get(panel_key, panel_key)
            prompt = PROMPT_BUILDERS[panel_key](gov)
            data, err = score_one(model_key, prompt, gov, label, max_retries=3)
            tracker.record(panel_key, model_key, gov, data, err)
            time.sleep(2)

    # 최종 실패 보고
    remaining = []
    for panel_key in PROMPT_BUILDERS:
        remaining.extend(tracker.get_failures(panel_key))
    if remaining:
        _print(f"\n⚠ {len(remaining)}건 최종 실패:")
        for m, g in remaining:
            _print(f"  - {MODEL_CALLERS[m][0]}: {g}")


# ═══════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════

def fleiss_kappa(ratings_matrix: List[List[int]], k: int) -> float:
    N = len(ratings_matrix)
    n = sum(ratings_matrix[0]) if ratings_matrix else 0
    if N == 0 or n <= 1:
        return 0.0

    P_i = []
    for row in ratings_matrix:
        sum_sq = sum(r * r for r in row)
        P_i.append((sum_sq - n) / (n * (n - 1)))
    P_bar = sum(P_i) / N

    p_j = []
    for j in range(k):
        total_j = sum(row[j] for row in ratings_matrix)
        p_j.append(total_j / (N * n))
    P_e = sum(p * p for p in p_j)

    if abs(1 - P_e) < 1e-10:
        return 1.0 if abs(P_bar - 1.0) < 1e-10 else 0.0
    return (P_bar - P_e) / (1 - P_e)


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


def compute_reliability(results: Dict[str, Dict[str, dict]],
                        govs: List[str],
                        criteria_codes: List[str],
                        score_range: Tuple[int, int] = (-2, 2)) -> Dict[str, Any]:
    """범용 코더 간 신뢰도 계산"""
    models = list(results.keys())
    n_coders = len(models)

    lo, hi = score_range
    n_categories = hi - lo + 1
    score_to_cat = {s: s - lo for s in range(lo, hi + 1)}

    all_ratings = []
    gov_kappas = {}

    for gov in govs:
        ratings_matrix = []
        for code in criteria_codes:
            row = [0] * n_categories
            for model_key in models:
                gov_data = results.get(model_key, {}).get(gov, {})
                scores = gov_data.get("scores", {})
                item = scores.get(code, {})
                score = item.get("score", 0)
                score = max(lo, min(hi, int(score)))
                cat = score_to_cat[score]
                row[cat] += 1
            # 코더 수가 일정해야 kappa 계산 가능
            if sum(row) == n_coders:
                ratings_matrix.append(row)
                all_ratings.append(row)

        if ratings_matrix:
            kappa = fleiss_kappa(ratings_matrix, n_categories)
            gov_kappas[gov] = round(kappa, 3)

    overall_kappa = fleiss_kappa(all_ratings, n_categories) if all_ratings else 0.0

    return {
        "n_coders": n_coders,
        "n_items_per_gov": len(criteria_codes),
        "overall_kappa": round(overall_kappa, 3),
        "gov_kappas": gov_kappas,
        "interpretation": interpret_kappa(overall_kappa),
    }


def compute_consensus(results: Dict[str, Dict[str, dict]],
                      govs: List[str],
                      criteria_codes: List[str]) -> Dict[str, Dict[str, float]]:
    """모델 간 합의 점수(평균) 계산"""
    models = list(results.keys())
    consensus = {}
    for gov in govs:
        scores = {}
        for code in criteria_codes:
            values = []
            for model_key in models:
                gov_data = results.get(model_key, {}).get(gov, {})
                item = gov_data.get("scores", {}).get(code, {})
                score = item.get("score", None)
                if score is not None:
                    values.append(int(score))
            scores[code] = round(sum(values) / len(values), 2) if values else 0.0
        consensus[gov] = scores
    return consensus


# ═══════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════

def generate_v2_report(tracker: CompletionTracker, models: List[str]) -> str:
    """통합 보고서 생성"""
    model_labels = [MODEL_CALLERS[m][0] for m in models if m in MODEL_CALLERS]
    lines = [
        "# 2-Panel Multi-AI 스코어링 v2 결과",
        "",
        f"> **생성일**: {time.strftime('%Y-%m-%d %H:%M')}",
        f"> **코더**: {', '.join(model_labels)}",
        f"> **Panel 1**: 중앙정부 {len(GOVERNMENTS)}개 대통령",
        f"> **Panel 2**: 지방정부 (성남시장, 경기도지사)",
        "",
    ]

    # ── Panel 1: ACW ──
    p1_acw = tracker.get_panel_results("panel1_acw")
    if p1_acw:
        p1_acw_models = [m for m in models if m in p1_acw and p1_acw[m]]
        if p1_acw_models:
            rel = compute_reliability(p1_acw, GOVERNMENTS, ALL_ACW_CODES, (-2, 2))
            consensus = compute_consensus(p1_acw, GOVERNMENTS, ALL_ACW_CODES)
            lines.extend(_panel1_acw_section(p1_acw, p1_acw_models, rel, consensus))

    # ── Panel 1: INST ──
    p1_inst = tracker.get_panel_results("panel1_inst")
    if p1_inst:
        p1_inst_models = [m for m in models if m in p1_inst and p1_inst[m]]
        if p1_inst_models:
            dim_codes = [c for c, _, _ in INST_DIMENSIONS]
            rel = compute_reliability(p1_inst, GOVERNMENTS, dim_codes, (0, 2))
            consensus = compute_consensus(p1_inst, GOVERNMENTS, dim_codes)
            lines.extend(_panel1_inst_section(p1_inst, p1_inst_models, rel, consensus))

    # ── Panel 2: ACW sub-wheel ──
    p2_acw = tracker.get_panel_results("panel2_acw")
    if p2_acw:
        p2_acw_models = [m for m in models if m in p2_acw and p2_acw[m]]
        if p2_acw_models:
            lines.extend(_panel2_acw_section(p2_acw, p2_acw_models))

    # ── Panel 2: INST ──
    p2_inst = tracker.get_panel_results("panel2_inst")
    if p2_inst:
        p2_inst_models = [m for m in models if m in p2_inst and p2_inst[m]]
        if p2_inst_models:
            lines.extend(_panel2_inst_section(p2_inst, p2_inst_models))

    # ── Panel 2: Agenda/Lowi ──
    p2_agenda = tracker.get_panel_results("panel2_agenda")
    if p2_agenda:
        p2_agenda_models = [m for m in models if m in p2_agenda and p2_agenda[m]]
        if p2_agenda_models:
            lines.extend(_panel2_agenda_section(p2_agenda, p2_agenda_models))

    # ── 완료율 ──
    success, total = tracker.completion_rate()
    rate = (success / total * 100) if total else 0
    lines.extend([
        "---",
        "## 완료 현황",
        "",
        f"- **성공**: {success}/{total} ({rate:.1f}%)",
        "",
    ])

    # ── 방법론 주석 ──
    lines.extend(_methodology_notes())

    return "\n".join(lines)


def _panel1_acw_section(results, models, rel, consensus) -> List[str]:
    dim_criteria = {dim: [c[0] for c in criteria] for dim, criteria in ACW_CRITERIA.items()}
    lines = [
        "---",
        "## Panel 1: ACW — 중앙정부 5모델 결과",
        "",
        f"### 코더 간 신뢰도 (Fleiss' kappa)",
        "",
        f"- **전체 kappa**: {rel['overall_kappa']} ({rel['interpretation']})",
        f"- **코더 수**: {rel['n_coders']}",
        f"- **항목 수(정부당)**: {rel['n_items_per_gov']}",
        "",
    ]

    if rel["gov_kappas"]:
        lines.extend(["| 정부 | kappa |", "|------|-------|"])
        for gov, k in rel["gov_kappas"].items():
            lines.append(f"| {gov} | {k} |")
        lines.append("")

    # 모델별 총 평균
    lines.extend(["### 모델별 정부 총 평균 점수", ""])
    header = "| 정부 | " + " | ".join(MODEL_CALLERS[m][0] for m in models) + " | **합의** |"
    sep = "|------|" + "|".join(["------"] * len(models)) + "|--------|"
    lines.extend([header, sep])

    for gov in GOVERNMENTS:
        row = f"| {gov} |"
        for m in models:
            gov_data = results.get(m, {}).get(gov, {})
            scores = gov_data.get("scores", {})
            vals = [int(scores.get(c, {}).get("score", 0)) for c in ALL_ACW_CODES]
            avg = sum(vals) / len(vals) if vals else 0
            row += f" {avg:+.2f} |"
        if gov in consensus:
            c_vals = list(consensus[gov].values())
            c_avg = sum(c_vals) / len(c_vals) if c_vals else 0
            row += f" **{c_avg:+.2f}** |"
        else:
            row += " — |"
        lines.append(row)

    # 차원별 합의 점수
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

    row = "| **총 평균** |"
    for gov in GOVERNMENTS:
        all_vals = list(consensus.get(gov, {}).values())
        avg = sum(all_vals) / len(all_vals) if all_vals else 0
        row += f" **{avg:+.2f}** |"
    lines.append(row)
    lines.append("")
    return lines


def _panel1_inst_section(results, models, rel, consensus) -> List[str]:
    dim_codes = [c for c, _, _ in INST_DIMENSIONS]
    lines = [
        "---",
        "## Panel 1: 제도적 적응 메커니즘 — 중앙정부 결과",
        "",
        f"### 코더 간 신뢰도 (Fleiss' kappa)",
        "",
        f"- **전체 kappa**: {rel['overall_kappa']} ({rel['interpretation']})",
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
        if gov in consensus:
            c_total = sum(consensus[gov].get(c, 0) for c in dim_codes)
            row += f" **{c_total:.1f}** |"
        else:
            row += " — |"
        lines.append(row)

    lines.append("")
    return lines


def _panel2_acw_section(results, models) -> List[str]:
    lines = [
        "---",
        "## Panel 2: ACW Sub-wheel — 이재명 지방정부",
        "",
    ]

    for gov in LOCAL_GOVERNMENTS:
        codes = _get_acw_local_codes(gov)
        exclude = _get_acw_exclude(gov)
        n_codes = len(codes)

        consensus = compute_consensus(results, [gov], codes)
        rel = compute_reliability(results, [gov], codes, (-2, 2))

        lines.extend([
            f"### {gov} ({n_codes}/22 기준, 제외: {', '.join(sorted(exclude))})",
            "",
            f"- **kappa**: {rel['overall_kappa']} ({rel['interpretation']})",
            "",
        ])

        header = "| 기준 | " + " | ".join(MODEL_CALLERS[m][0] for m in models) + " | **합의** |"
        sep = "|------|" + "|".join(["------"] * len(models)) + "|--------|"
        lines.extend([header, sep])

        for code in codes:
            row = f"| {code} |"
            for m in models:
                gov_data = results.get(m, {}).get(gov, {})
                score = gov_data.get("scores", {}).get(code, {}).get("score", "—")
                row += f" {score} |"
            c_score = consensus.get(gov, {}).get(code, 0)
            row += f" **{c_score:+.2f}** |"
            lines.append(row)

        # 총 평균
        c_vals = [consensus.get(gov, {}).get(c, 0) for c in codes]
        c_avg = sum(c_vals) / len(c_vals) if c_vals else 0
        lines.append(f"\n**평균**: {c_avg:+.2f}\n")

    return lines


def _panel2_inst_section(results, models) -> List[str]:
    dim_codes = [c for c, _, _ in INST_LOCAL_DIMENSIONS]
    lines = [
        "---",
        "## Panel 2: 제도적 적응 메커니즘 — 지방정부 (기능적 등가)",
        "",
    ]

    consensus = compute_consensus(results, LOCAL_GOVERNMENTS, dim_codes)

    header = "| 차원 | " + " | ".join(f"{gov.split('(')[0]}" for gov in LOCAL_GOVERNMENTS) + " |"
    sep = "|------|" + "|".join(["------"] * len(LOCAL_GOVERNMENTS)) + "|"
    lines.extend([header, sep])

    for code in dim_codes:
        row = f"| {code} |"
        for gov in LOCAL_GOVERNMENTS:
            c_score = consensus.get(gov, {}).get(code, 0)
            row += f" {c_score:.1f} |"
        lines.append(row)

    lines.append("")
    return lines


def _panel2_agenda_section(results, models) -> List[str]:
    agenda_codes = [c for c, _, _ in AGENDA_CRITERIA]
    lines = [
        "---",
        "## Panel 2: Lowi 정책유형 분류 — 지방정부",
        "",
    ]

    consensus = compute_consensus(results, LOCAL_GOVERNMENTS, agenda_codes)

    header = "| 유형 | " + " | ".join(f"{gov.split('(')[0]}" for gov in LOCAL_GOVERNMENTS) + " |"
    sep = "|------|" + "|".join(["------"] * len(LOCAL_GOVERNMENTS)) + "|"
    lines.extend([header, sep])

    type_names = {"E1": "분배", "E2": "규제", "E3": "재분배", "E4": "구성", "E5": "적응도구"}
    for code in agenda_codes:
        name = type_names.get(code, code)
        row = f"| {code} ({name}) |"
        for gov in LOCAL_GOVERNMENTS:
            c_score = consensus.get(gov, {}).get(code, 0)
            row += f" {c_score:.1f}% |"
        lines.append(row)

    lines.append("")
    return lines


def _methodology_notes() -> List[str]:
    return [
        "---",
        "## 방법론 주석",
        "",
        "### 비교 제약 조건",
        "- Panel 1(중앙정부)과 Panel 2(지방정부)의 ACW 점수는 **직접 비교 불가**.",
        "- Panel 2 ACW는 중앙정부에만 해당하는 기준을 제외한 sub-wheel로 구성.",
        "  - 성남시장: 19/22 기준 (V2, Re3, L2 제외)",
        "  - 경기도지사: 20/22 기준 (Re3, L2 제외)",
        "- 국제 지표(방법 C)는 국가 단위 측정으로 지방정부 적용 불가하여 Panel 2에서 제외.",
        "",
        "### 기능적 등가성 적용 (제도적 메커니즘)",
        "- 지방정부의 조례·규칙은 중앙정부의 법률·대통령령과 기능적으로 등가하게 취급.",
        "- 지방위원회·도정회의는 국가위원회·국무회의와 기능적으로 등가하게 취급.",
        "- 이 등가성은 법적 위계가 아닌 기능적 역할에 근거한 비교 방법론적 결정임.",
        "",
        "### Lowi 분류 적용",
        "- Lowi(1964)의 정책유형 분류는 정부 수준과 무관하게 적용 가능 (4/4 방법론 전문가 동의).",
        "- 시정/도정 공약·핵심과제를 분류 단위로 사용.",
        "",
        "### 역량 궤적 분석",
        "- 공통 기준(성남 19개, 경기 20개 중 교집합 19개)에 한정하여 시장→도지사→대통령 점수 변화 추적.",
        "- 지방↔중앙 점수는 구조적 차이로 인해 절대값 비교가 아닌 상대적 변화 방향만 해석.",
        "",
    ]


# ═══════════════════════════════════════════════════════════
# CAPACITY TRAJECTORY
# ═══════════════════════════════════════════════════════════

def generate_capacity_trajectory(tracker: CompletionTracker, models: List[str]) -> str:
    """이재명 역량 궤적 분석: 시장→도지사→대통령"""
    p1_acw = tracker.get_panel_results("panel1_acw")
    p2_acw = tracker.get_panel_results("panel2_acw")

    # 공통 기준: 성남(19) ∩ 경기(20) ∩ 전체(22) = 성남 기준 19개
    common_codes = _get_acw_local_codes("이재명 성남시장(2010-2018)")

    lines = [
        "# 이재명 역량 궤적 분석 (ACW 공통 기준)",
        "",
        f"> **생성일**: {time.strftime('%Y-%m-%d %H:%M')}",
        f"> **공통 기준 수**: {len(common_codes)}개 (V2, Re3, L2 제외)",
        "",
        "## 궤적 개요",
        "",
        "성남시장(2010-2018) → 경기도지사(2018-2022) → 대통령(2025-) 순으로",
        "공통 ACW 기준에 대한 모델별 점수 변화를 추적합니다.",
        "",
    ]

    trajectories = {
        "이재명 성남시장(2010-2018)": p2_acw,
        "이재명 경기도지사(2018-2022)": p2_acw,
        "이재명(2025-)": p1_acw,
    }

    # 모델별 궤적 테이블
    active_models = [m for m in models if m in MODEL_CALLERS]

    for model_key in active_models:
        label = MODEL_CALLERS[model_key][0]
        lines.extend([f"### {label}", ""])

        header = "| 기준 | 성남시장 | 경기도지사 | 대통령 | 변화방향 |"
        sep = "|------|---------|-----------|--------|---------|"
        lines.extend([header, sep])

        for code in common_codes:
            scores = []
            for gov, data_source in trajectories.items():
                gov_data = data_source.get(model_key, {}).get(gov, {})
                s = gov_data.get("scores", {}).get(code, {}).get("score", None)
                scores.append(s)

            vals = [str(s) if s is not None else "—" for s in scores]
            # 변화 방향 판단
            valid = [int(s) for s in scores if s is not None]
            if len(valid) >= 2:
                if valid[-1] > valid[0]:
                    direction = "↑ 상승"
                elif valid[-1] < valid[0]:
                    direction = "↓ 하락"
                else:
                    direction = "→ 유지"
            else:
                direction = "—"

            lines.append(f"| {code} | {vals[0]} | {vals[1]} | {vals[2]} | {direction} |")

        # 평균
        avgs = []
        for gov, data_source in trajectories.items():
            gov_data = data_source.get(model_key, {}).get(gov, {})
            vals = [int(gov_data.get("scores", {}).get(c, {}).get("score", 0)) for c in common_codes
                    if gov_data.get("scores", {}).get(c)]
            avgs.append(sum(vals) / len(vals) if vals else 0)
        lines.append(f"| **평균** | **{avgs[0]:+.2f}** | **{avgs[1]:+.2f}** | **{avgs[2]:+.2f}** | |")
        lines.append("")

    # 합의 궤적
    lines.extend(["## 합의 점수 기반 궤적", ""])
    header = "| 기준 | 성남시장 | 경기도지사 | 대통령 | 변화방향 |"
    sep = "|------|---------|-----------|--------|---------|"
    lines.extend([header, sep])

    for code in common_codes:
        vals = []
        for gov, data_source in trajectories.items():
            model_scores = []
            for m in active_models:
                s = data_source.get(m, {}).get(gov, {}).get("scores", {}).get(code, {}).get("score")
                if s is not None:
                    model_scores.append(int(s))
            avg = sum(model_scores) / len(model_scores) if model_scores else 0
            vals.append(avg)

        direction = "—"
        if vals[0] != 0 or vals[2] != 0:
            if vals[2] > vals[0]:
                direction = "↑ 상승"
            elif vals[2] < vals[0]:
                direction = "↓ 하락"
            else:
                direction = "→ 유지"

        lines.append(f"| {code} | {vals[0]:+.2f} | {vals[1]:+.2f} | {vals[2]:+.2f} | {direction} |")

    overall = []
    for gov, data_source in trajectories.items():
        all_model_vals = []
        for m in active_models:
            for c in common_codes:
                s = data_source.get(m, {}).get(gov, {}).get("scores", {}).get(c, {}).get("score")
                if s is not None:
                    all_model_vals.append(int(s))
        overall.append(sum(all_model_vals) / len(all_model_vals) if all_model_vals else 0)
    lines.append(f"| **총 평균** | **{overall[0]:+.2f}** | **{overall[1]:+.2f}** | **{overall[2]:+.2f}** | |")

    lines.extend([
        "",
        "## 해석 주의사항",
        "",
        "- 지방정부 점수와 중앙정부 점수는 분석 단위가 다르므로 절대값 비교는 부적절합니다.",
        "- 변화 방향(↑↓→)은 동일 인물의 역할 전환에 따른 상대적 변화를 나타냅니다.",
        "- 공통 19개 기준에 한정한 비교이며, 제외된 기준(V2, Re3, L2)의 영향은 반영되지 않습니다.",
        "",
    ])

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# GEMINI CONNECTIVITY TEST
# ═══════════════════════════════════════════════════════════

def test_gemini() -> bool:
    """Gemini API 연결 테스트"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            _print("⚠ GEMINI_API_KEY가 설정되지 않았습니다.")
            return False

        resp = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
            params={"key": api_key},
            json={
                "contents": [{"parts": [{"text": "Hello, respond with just 'OK'"}]}],
                "generationConfig": {"temperature": 0, "maxOutputTokens": 10},
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            _print("✓ Gemini 연결 테스트 성공")
            return True
        else:
            _print("⚠ Gemini 응답 비정상")
            return False
    except Exception as e:
        _print(f"⚠ Gemini 연결 실패: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Multi-AI 2-Panel Scoring v2")
    parser.add_argument("--models", nargs="+",
                        default=["gpt", "claude", "grok", "clova", "gemini"],
                        choices=["gpt", "claude", "grok", "clova", "gemini"],
                        help="사용할 모델 (기본: 전체 5개)")
    parser.add_argument("--panel", default="all", choices=["1", "2", "all"],
                        help="실행할 패널 (기본: all)")
    parser.add_argument("--analysis", default="all",
                        choices=["acw", "inst", "agenda", "all"],
                        help="분석 유형 (기본: all)")
    parser.add_argument("--reuse-panel1", action="store_true",
                        help="기존 Panel 1 결과 재사용 (성공분만)")
    parser.add_argument("--skip-gemini-on-fail", action="store_true", default=True,
                        help="Gemini 연결 실패 시 자동 제외 (기본: True)")
    args = parser.parse_args()

    models = list(args.models)

    _print("=" * 60)
    _print("Multi-AI 2-Panel Scoring v2")
    _print(f"모델: {', '.join(MODEL_CALLERS[m][0] for m in models)}")
    _print(f"패널: {args.panel}")
    _print(f"분석: {args.analysis}")
    _print(f"Panel 1 재사용: {args.reuse_panel1}")
    _print("=" * 60)

    # ── Gemini 연결 테스트 ──
    if "gemini" in models:
        _print("\n▶ Gemini 연결 테스트")
        if not test_gemini():
            if args.skip_gemini_on_fail:
                _print("→ Gemini를 제외하고 진행합니다.")
                models.remove("gemini")
            else:
                _print("→ --skip-gemini-on-fail=False이므로 중단합니다.")
                sys.exit(1)

    # ── 기존 결과 로드 (--reuse-panel1) ──
    reuse_acw = None
    reuse_inst = None
    if args.reuse_panel1:
        _print("\n▶ 기존 Panel 1 결과 로드")
        acw_path = OUTPUT_DIR / "acw_raw_results.json"
        inst_path = OUTPUT_DIR / "inst_raw_results.json"

        if acw_path.exists():
            with open(acw_path, "r", encoding="utf-8") as f:
                reuse_acw = json.load(f)
            _print(f"  ACW 로드: {sum(len(v) for v in reuse_acw.values())}건")
        else:
            _print(f"  ACW 파일 없음: {acw_path}")

        if inst_path.exists():
            with open(inst_path, "r", encoding="utf-8") as f:
                reuse_inst = json.load(f)
            _print(f"  INST 로드: {sum(len(v) for v in reuse_inst.values())}건")
        else:
            _print(f"  INST 파일 없음: {inst_path}")

    # ── 실행 ──
    tracker = CompletionTracker()

    if args.panel in ("1", "all"):
        run_panel1(models, args.analysis, tracker, reuse_acw, reuse_inst)

    if args.panel in ("2", "all"):
        run_panel2(models, args.analysis, tracker)

    # ── 실패 항목 재시도 ──
    retry_gaps(tracker, max_rounds=3)

    # ── 결과 저장 ──
    _print("\n▶ 결과 저장")

    # 전체 원시 결과 (기존 데이터와 병합)
    raw_path = OUTPUT_DIR / "scoring_v2_raw.json"
    raw_all = {}
    if raw_path.exists():
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_all = json.load(f)
    for panel_key in ["panel1_acw", "panel1_inst", "panel2_acw", "panel2_inst", "panel2_agenda"]:
        panel_data = tracker.get_panel_results(panel_key)
        if panel_data:
            raw_all.setdefault(panel_key, {})
            for mk, govs in panel_data.items():
                raw_all[panel_key].setdefault(mk, {}).update(govs)

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_all, f, ensure_ascii=False, indent=2)
    _print(f"  원시 결과: {raw_path}")

    # Panel 1 ACW/INST 원시 결과도 별도 저장 (기존 데이터와 병합)
    p1_acw = tracker.get_panel_results("panel1_acw")
    if p1_acw:
        acw_path = OUTPUT_DIR / "acw_raw_results.json"
        existing = {}
        if acw_path.exists():
            with open(acw_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        for mk, govs in p1_acw.items():
            existing.setdefault(mk, {}).update(govs)
        with open(acw_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    p1_inst = tracker.get_panel_results("panel1_inst")
    if p1_inst:
        inst_path = OUTPUT_DIR / "inst_raw_results.json"
        existing = {}
        if inst_path.exists():
            with open(inst_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        for mk, govs in p1_inst.items():
            existing.setdefault(mk, {}).update(govs)
        with open(inst_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    # 완료 매트릭스
    matrix = tracker.completion_matrix()
    matrix_path = OUTPUT_DIR / "completion_matrix.json"
    with open(matrix_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)
    _print(f"  완료 매트릭스: {matrix_path}")

    # 통합 보고서
    report = generate_v2_report(tracker, models)
    report_path = OUTPUT_DIR / "scoring_v2_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    _print(f"  통합 보고서: {report_path}")

    # 역량 궤적
    trajectory = generate_capacity_trajectory(tracker, models)
    trajectory_path = OUTPUT_DIR / "capacity_trajectory.md"
    with open(trajectory_path, "w", encoding="utf-8") as f:
        f.write(trajectory)
    _print(f"  역량 궤적: {trajectory_path}")

    # ── 최종 완료율 ──
    success, total = tracker.completion_rate()
    rate = (success / total * 100) if total else 0
    _print(f"\n{'=' * 60}")
    _print(f"최종 완료율: {success}/{total} ({rate:.1f}%)")
    _print(f"{'=' * 60}")

    if rate < 100:
        _print("⚠ 일부 항목이 실패했습니다. completion_matrix.json을 확인하세요.")
    else:
        _print("✓ 모든 항목 100% 완료!")


if __name__ == "__main__":
    main()
