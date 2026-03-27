"""
방법론 자문: 이재명 성남시장/경기도지사 경력의 비교 가능성
4개 AI 모델에게 방법론 전문가로서 의견을 구함
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

OUTPUT_DIR = Path(__file__).resolve().parent / "tables"
OUTPUT_DIR.mkdir(exist_ok=True)

def _print(msg):
    print(msg, flush=True)


PROMPT = """당신은 비교행정학·정책학 방법론 전문가입니다.

## 배경
한국 역대 6개 정부(노무현, 이명박, 박근혜, 문재인, 윤석열, 이재명)의 적응 역량을 비교분석하고 있습니다.
이재명 정부(2025-)는 출범 초기라 데이터가 부족합니다.
이재명은 대통령 이전에 **성남시장(2010-2018)**과 **경기도지사(2018-2022)** 경력이 있습니다.

## 5가지 분석 방법

| 방법 | 내용 | 비교 단위 |
|------|------|----------|
| A. ACW (Adaptive Capacity Wheel) | Gupta et al.(2010). 6개 차원 22개 기준(-2~+2) 점수화 | 중앙정부 행정 전반 |
| B. Policy Lag | OECD Agility Framework. 위기 인지→결정→실행 지연 일수 측정 | 위기 사례별 대응 속도 |
| C. 국제 지표 시계열 | WGI Government Effectiveness, UN EGDI, OECD DGI | 국가 단위 지표 |
| D. 제도적 적응 메커니즘 | Argyris & Schön(1978). 피드백/실험/참여/디지털 4차원, 0-2점 | 중앙정부 공식 제도 |
| E. 국정과제 유형 분류 | Lowi(1972) 정책 유형 + 적응적 도구 비율 | 정책 의제 항목 |

## 질문

각 방법(A~E)에 대해 다음을 판단해주세요:

1. **비교 가능성**: 이재명의 시장/도지사 시기 데이터를 다른 대통령들의 데이터와 동일 프레임워크로 비교할 수 있는가?
2. **비교 가능 조건**: 가능하다면, 어떤 조건/조정이 필요한가? (예: 특정 기준만 적용, 가중치 조정, 별도 패널 구성 등)
3. **비교 불가 사유**: 불가능하다면, 구체적으로 어떤 방법론적 문제가 있는가?
4. **대안 제안**: 비교 불가 시, 이재명의 지방행정 경력을 어떻게 활용할 수 있는가?

## 출력 형식 (반드시 이 JSON 형식을 준수)
```json
{
  "methods": {
    "A_ACW": {
      "comparable": true/false,
      "comparability_level": "full/partial/none",
      "conditions": "비교 가능 조건 설명",
      "issues": "방법론적 문제점",
      "alternative": "대안 제안",
      "rationale": "판단 근거 (2-3문장)"
    },
    "B_PolicyLag": { ... },
    "C_IntlIndices": { ... },
    "D_Institutional": { ... },
    "E_AgendaType": { ... }
  },
  "overall_recommendation": "전체적인 방법론 권고 (3-5문장)",
  "additional_methods": "이재명 지방행정 경력을 활용할 수 있는 추가 방법론 제안 (있다면)"
}
```

주의: 반드시 JSON만 출력하세요. 다른 텍스트를 포함하지 마세요.
"""


# ── API callers (from ai_scoring.py) ──

def call_openai(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.2")
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "당신은 비교행정학·정책학 방법론 전문가입니다."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_completion_tokens": 8192,
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_claude(prompt):
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
            "max_tokens": 4096,
            "system": "당신은 비교행정학·정책학 방법론 전문가입니다.",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def call_grok(prompt):
    api_key = os.getenv("XAI_API_KEY")
    model = os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning")
    resp = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "당신은 비교행정학·정책학 방법론 전문가입니다."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_clova(prompt):
    api_key = os.getenv("CLOVA_STUDIO_API_KEY")
    model = os.getenv("CLOVA_STUDIO_MODEL", "HCX-007")
    base_url = (os.getenv("CLOVA_STUDIO_BASE_URL") or "https://clovastudio.stream.ntruss.com").rstrip("/")
    resp = requests.post(
        f"{base_url}/v3/chat-completions/{model}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": "당신은 비교행정학·정책학 방법론 전문가입니다."},
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


import re

def _repair_json(raw):
    s = raw.strip()
    s = re.sub(r",\s*([}\]])", r"\1", s)
    s = re.sub(r'"rational"(\s*:)', r'"rationale"\1', s)
    lines = s.split("\n")
    fixed = []
    for line in lines:
        unescaped = len(re.findall(r'(?<!\\)"', line))
        if unescaped % 2 != 0:
            line = line.rstrip()
            if line and line[-1] in (",", "}", "]"):
                line = line[:-1] + '"' + line[-1]
            else:
                line = line + '"'
        fixed.append(line)
    s = "\n".join(fixed)
    ob = s.count("{") - s.count("}")
    osb = s.count("[") - s.count("]")
    if ob > 0:
        s = s.rstrip() + "\n" + "}" * ob
    if osb > 0:
        s += "]" * osb
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s


def extract_json(text):
    candidates = []
    m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if m:
        candidates.append(m.group(1).strip())
    m = re.search(r'\{[\s\S]*"methods"[\s\S]*\}', text)
    if m:
        candidates.append(m.group(0))
    m = re.search(r'(\{[\s\S]*"methods"[\s\S]*)', text)
    if m:
        candidates.append(m.group(1))
    stripped = text.strip()
    if stripped.startswith("{"):
        candidates.append(stripped)
    for c in candidates:
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            pass
        try:
            return json.loads(_repair_json(c))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"JSON parse failed: {text[:300]}...")


MODELS = {
    "gpt": ("GPT-5.2", call_openai),
    "claude": ("Claude Sonnet 4.6", call_claude),
    "grok": ("Grok-4", call_grok),
    "clova": ("HyperCLOVA HCX-007", call_clova),
}


def main():
    results = {}

    for key, (label, caller) in MODELS.items():
        _print(f"\n{'='*50}")
        _print(f"[{label}] 방법론 자문 요청 중...")
        _print(f"{'='*50}")

        for attempt in range(3):
            try:
                raw = caller(PROMPT)
                parsed = extract_json(raw)
                results[key] = {"label": label, "response": parsed}
                _print(f"[{label}] 완료 ✓")
                break
            except Exception as e:
                _print(f"[{label}] 시도 {attempt+1} 실패: {e}")
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
        else:
            _print(f"[{label}] 최종 실패 ✗")
            # Save raw text for debugging
            results[key] = {"label": label, "response": None, "raw": raw[:2000] if 'raw' in dir() else "no response"}

        time.sleep(1)

    # Save raw results
    out_path = OUTPUT_DIR / "method_consult_raw.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    _print(f"\n원시 결과 저장: {out_path}")

    # Generate comparison report
    report = generate_report(results)
    report_path = OUTPUT_DIR / "method_consult_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    _print(f"보고서 저장: {report_path}")
    _print("\n완료!")


def generate_report(results):
    lines = [
        "# 방법론 자문 결과: 이재명 지방행정 경력의 비교 가능성",
        "",
        f"> **생성일**: {time.strftime('%Y-%m-%d %H:%M')}",
        f"> **자문 모델**: {', '.join(r['label'] for r in results.values())}",
        "",
        "---",
        "",
    ]

    methods = ["A_ACW", "B_PolicyLag", "C_IntlIndices", "D_Institutional", "E_AgendaType"]
    method_names = {
        "A_ACW": "A. ACW (Adaptive Capacity Wheel)",
        "B_PolicyLag": "B. Policy Lag (정책 대응 시간)",
        "C_IntlIndices": "C. 국제 지표 시계열",
        "D_Institutional": "D. 제도적 적응 메커니즘",
        "E_AgendaType": "E. 국정과제 유형 분류",
    }

    for method_key in methods:
        name = method_names[method_key]
        lines.append(f"## {name}")
        lines.append("")

        # Summary table
        lines.append("| 모델 | 비교 가능성 | 수준 | 핵심 판단 |")
        lines.append("|------|-----------|------|----------|")

        for key, data in results.items():
            label = data["label"]
            resp = data.get("response")
            if not resp or "methods" not in resp:
                lines.append(f"| {label} | — | — | 응답 실패 |")
                continue
            m = resp["methods"].get(method_key, {})
            comparable = "✓" if m.get("comparable") else "✗"
            level = m.get("comparability_level", "—")
            rationale = m.get("rationale", "—")
            # Truncate rationale for table
            if len(rationale) > 80:
                rationale = rationale[:77] + "..."
            lines.append(f"| {label} | {comparable} | {level} | {rationale} |")

        lines.append("")

        # Detailed conditions/issues per model
        lines.append("### 상세 의견")
        lines.append("")
        for key, data in results.items():
            label = data["label"]
            resp = data.get("response")
            if not resp or "methods" not in resp:
                continue
            m = resp["methods"].get(method_key, {})
            lines.append(f"**{label}**:")
            if m.get("conditions"):
                lines.append(f"- 조건: {m['conditions']}")
            if m.get("issues"):
                lines.append(f"- 문제: {m['issues']}")
            if m.get("alternative"):
                lines.append(f"- 대안: {m['alternative']}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Overall recommendations
    lines.append("## 종합 권고")
    lines.append("")
    for key, data in results.items():
        label = data["label"]
        resp = data.get("response")
        if not resp:
            continue
        rec = resp.get("overall_recommendation", "—")
        lines.append(f"**{label}**: {rec}")
        lines.append("")
        add = resp.get("additional_methods", "")
        if add:
            lines.append(f"- 추가 방법론 제안: {add}")
            lines.append("")

    # Consensus analysis
    lines.append("---")
    lines.append("")
    lines.append("## 합의 분석")
    lines.append("")
    lines.append("| 방법 | 비교 가능 판정 (모델 수) | 합의 |")
    lines.append("|------|----------------------|------|")

    for method_key in methods:
        name = method_names[method_key].split(".")[1].strip().split("(")[0].strip()
        yes = 0
        partial = 0
        no = 0
        total = 0
        for key, data in results.items():
            resp = data.get("response")
            if not resp or "methods" not in resp:
                continue
            total += 1
            m = resp["methods"].get(method_key, {})
            level = m.get("comparability_level", "none")
            if level == "full":
                yes += 1
            elif level == "partial":
                partial += 1
            else:
                no += 1
        consensus = ""
        if yes + partial >= 3:
            consensus = "**포함 가능**"
        elif no >= 3:
            consensus = "**포함 불가**"
        else:
            consensus = "의견 분분"
        lines.append(f"| {name} | 가능 {yes} / 부분 {partial} / 불가 {no} | {consensus} |")

    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
