"""
A-2: 블라인딩 유무 점수 비교
블라인딩 없이(정부명 노출) CRS 1라운드를 채점하여, 기존 블라인딩 점수와 비교.

목적: 블라인딩이 뚫려도 모델이 점수를 조정하는지(anchoring effect) 확인.

Usage:
    python blinding_comparison.py
    python blinding_comparison.py --models gpt claude
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "data" / "validation"
OUTPUT_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════

GOV_CASES = {
    "노무현 정부(2003-2008)": [1, 2, 3],
    "이명박 정부(2008-2013)": [4, 5, 6],
    "박근혜 정부(2013-2017)": [7, 8, 9],
    "문재인 정부(2017-2022)": [10, 11, 12],
    "윤석열 정부(2022-2025)": [13, 14, 15],
}

BLIND_LABEL_MAP = {
    "노무현 정부(2003-2008)": "Alpha",
    "이명박 정부(2008-2013)": "Beta",
    "박근혜 정부(2013-2017)": "Gamma",
    "문재인 정부(2017-2022)": "Delta",
    "윤석열 정부(2022-2025)": "Epsilon",
}

SYSTEM_PROMPT = "당신은 정부의 위기 대응 역량을 평가하는 행정학·위기관리 전문가입니다. 요청된 JSON 형식에 맞춰 정확히 응답하세요."

RUBRIC = """
## 평가 차원 (3차원, 각 0-4점)

### D1: 인지·결정 신속성 (Recognition & Decision Speed)
- 0: 위기 인지 부재 또는 극도로 지연(수주 이상), 거버넌스 붕괴로 결정 불가
- 1: 위기 인지했으나 결정 매우 지연(수주). 초기 대응 체계 미작동
- 2: 위기 인지 수일 내, 실질적 결정까지 상당 시간. 대응 체계 느리게 작동
- 3: 위기 인지 후 수일 내 실질적 결정. 위기관리 체계 보통 수준 작동
- 4: 위기 발생 즉시(~1일) 인지, 수일 내 결정. 선제적 대비 또는 즉각 체계 가동

### D2: 대응 규모·방식 적절성 (Response Appropriateness)
- 0: 대응 부재, 또는 위기와 무관한 조치
- 1: 형식적 대응. 규모 현저히 부족하거나 핵심 문제 비켜감
- 2: 일부 적절한 조치 있으나 규모·범위·초점에서 주요 결함
- 3: 대체로 적절. 위기 규모에 상응하는 자원 투입과 정책 수단 동원
- 4: 위기 성격·규모에 정확히 부합하는 포괄적 대응

### D3: 집행 실효성 (Implementation Effectiveness)
- 0: 결정 미집행 또는 극도로 지연, 실효성 없음
- 1: 집행 시작되었으나 매우 지연/불완전. 위기 완화 미미
- 2: 일부 조치 집행, 주요 조치 지연/미집행. 부분적 효과
- 3: 대부분 조치 적시 집행. 측정 가능한 위기 완화 효과
- 4: 모든 주요 조치 신속 집행, 위기 완화에 명확한 기여, 후속 조치까지 체계적
"""

# ═══════════════════════════════════════════════════════════
# MODEL CALLERS (probe_test.py와 동일)
# ═══════════════════════════════════════════════════════════

def call_openai(prompt: str) -> str:
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("OPENAI_MODEL", "gpt-5.2"),
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            "temperature": 0.2, "max_completion_tokens": 4096,
            "response_format": {"type": "json_object"},
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def call_claude(prompt: str) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.getenv("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        json={
            "model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            "max_tokens": 4096, "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

def call_grok(prompt: str) -> str:
    resp = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('XAI_API_KEY')}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning"),
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            "temperature": 0.2, "max_completion_tokens": 4096,
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def call_clova(prompt: str) -> str:
    base_url = (os.getenv("CLOVA_STUDIO_BASE_URL") or "https://clovastudio.stream.ntruss.com").rstrip("/")
    model = os.getenv("CLOVA_STUDIO_MODEL", "HCX-007")
    resp = requests.post(
        f"{base_url}/v3/chat-completions/{model}",
        headers={"Authorization": f"Bearer {os.getenv('CLOVA_STUDIO_API_KEY')}", "Content-Type": "application/json"},
        json={
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            "temperature": 0.2, "thinking": {"type": "enabled"},
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", data).get("message", {}).get("content", "")

def call_gemini(prompt: str) -> str:
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
        params={"key": os.getenv("GEMINI_API_KEY")},
        json={
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096},
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

MODEL_CALLERS = {
    "gpt":    ("GPT-5.2",             call_openai),
    "claude": ("Claude Sonnet 4.6",   call_claude),
    "grok":   ("Grok-4-1",           call_grok),
    "clova":  ("HyperCLOVA HCX-007", call_clova),
    "gemini": ("Gemini 3 Flash",      call_gemini),
}

# ═══════════════════════════════════════════════════════════
# TIMELINE PARSING (블라인딩 없이 원문 그대로 사용)
# ═══════════════════════════════════════════════════════════

def load_timelines() -> str:
    return (DATA_DIR / "raw_downloads" / "crisis_timelines.md").read_text(encoding="utf-8")

def split_cases(raw: str) -> dict[int, str]:
    cases = {}
    pattern = re.compile(r"### Case (\d+):")
    parts = pattern.split(raw)
    for i in range(1, len(parts) - 1, 2):
        case_num = int(parts[i])
        case_text = parts[i + 1].strip()
        next_section = re.search(r"\n## ", case_text)
        if next_section:
            case_text = case_text[:next_section.start()]
        cases[case_num] = f"### Case {case_num}: {case_text}"
    return cases

def extract_json(text: str) -> dict:
    md = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if md:
        return json.loads(md.group(1))
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        return json.loads(m.group(0))
    return json.loads(text)

def parse_scores(response: str) -> dict:
    try:
        data = extract_json(response)
        for dim in ["D1", "D2", "D3"]:
            if dim in data:
                if isinstance(data[dim], dict):
                    data[dim]["score"] = int(data[dim].get("score", -1))
                else:
                    data[dim] = {"score": int(data[dim]), "rationale": ""}
        return data
    except Exception:
        return {"D1": {"score": -1}, "D2": {"score": -1}, "D3": {"score": -1}}

# ═══════════════════════════════════════════════════════════
# UNBLINDED SCORING
# ═══════════════════════════════════════════════════════════

def make_unblinded_prompt(gov_name: str, case_text: str) -> str:
    return f"""아래는 **{gov_name}**의 위기 대응 사례입니다.
이 정부의 위기 대응을 3개 차원에서 0-4로 채점하십시오.

{RUBRIC}

---

{case_text}

---

반드시 아래 JSON 형식으로만 응답하십시오. 다른 텍스트를 포함하지 마십시오.
{{
  "D1": {{"score": <0-4>, "rationale": "<1-2문장>"}},
  "D2": {{"score": <0-4>, "rationale": "<1-2문장>"}},
  "D3": {{"score": <0-4>, "rationale": "<1-2문장>"}},
  "composite": <(D1+D2+D3)/3 소수점 둘째자리>
}}"""


def load_blinded_scores() -> dict:
    """기존 블라인딩 채점 결과(crisis_scoring_results.json) 로드"""
    paths = [
        DATA_DIR / "raw_deprecated" / "crisis_scoring_results.json",
    ]
    for p in paths:
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    return {}


def run_comparison(model_keys: list[str]) -> dict:
    print("=" * 60)
    print("A-2: 블라인딩 유무 점수 비교")
    print(f"시간: {datetime.now().isoformat()}")
    print("조건: 정부명 노출(unblinded), 1라운드")
    print("=" * 60)

    raw = load_timelines()
    cases = split_cases(raw)
    # Case 16-18 (이재명) 제외
    cases = {k: v for k, v in cases.items() if k <= 15}
    print(f"✓ {len(cases)}개 사례 로드 (이재명 제외)")

    results = {
        "_metadata": {
            "timestamp": datetime.now().isoformat(),
            "condition": "unblinded (government name exposed)",
            "n_cases": len(cases),
            "n_models": len(model_keys),
        },
        "unblinded_scores": {},
    }

    for mkey in model_keys:
        model_name, caller = MODEL_CALLERS[mkey]
        print(f"\n{'─' * 40}")
        print(f"모델: {model_name}")
        print(f"{'─' * 40}")
        results["unblinded_scores"][mkey] = {"model_name": model_name, "cases": {}}

        for gov_name, case_nums in GOV_CASES.items():
            for cn in case_nums:
                if cn not in cases:
                    continue
                case_text = cases[cn]
                prompt = make_unblinded_prompt(gov_name, case_text)
                print(f"  Case {cn:2d} ({gov_name[:3]}) ... ", end="", flush=True)

                try:
                    response = caller(prompt)
                    scores = parse_scores(response)
                    d1 = scores.get("D1", {}).get("score", -1)
                    d2 = scores.get("D2", {}).get("score", -1)
                    d3 = scores.get("D3", {}).get("score", -1)
                    comp = (d1 + d2 + d3) / 3 if all(s >= 0 for s in [d1, d2, d3]) else -1
                    results["unblinded_scores"][mkey]["cases"][str(cn)] = {
                        "government": gov_name,
                        "D1": d1, "D2": d2, "D3": d3,
                        "composite": round(comp, 2),
                    }
                    print(f"D1={d1} D2={d2} D3={d3} comp={comp:.2f}")
                except Exception as e:
                    print(f"오류: {e}")
                    results["unblinded_scores"][mkey]["cases"][str(cn)] = {
                        "government": gov_name, "error": str(e),
                    }

                time.sleep(1)

    return results


def write_comparison_report(results: dict, path: Path):
    import numpy as np

    lines = [
        "# A-2: 블라인딩 유무 점수 비교 결과",
        "",
        f"> 실행 시간: {results['_metadata']['timestamp']}",
        f"> 조건: {results['_metadata']['condition']}",
        f"> 사례 수: {results['_metadata']['n_cases']} (이재명 제외)",
        "",
        "## 비교 방법",
        "",
        "- **블라인딩 조건**: 기존 crisis_scoring.py 결과 (정부명 Greek 라벨 치환)",
        "- **비블라인딩 조건**: 본 실험 결과 (정부명 노출)",
        "- **비교 지표**: 정부별 CRS 평균, 모델별 점수 차이(unblinded - blinded)",
        "",
    ]

    # 정부별 unblinded CRS 요약
    lines.append("## 비블라인딩 조건 정부별 CRS")
    lines.append("")
    lines.append("| 정부 | " + " | ".join(
        results["unblinded_scores"][m]["model_name"]
        for m in results["unblinded_scores"]
    ) + " | 평균 |")
    lines.append("|------|" + "|".join(":------:" for _ in results["unblinded_scores"]) + "|:------:|")

    for gov_name, case_nums in GOV_CASES.items():
        short = gov_name.split('(')[0]
        row = [f"| {short} "]
        model_avgs = []
        for mkey, mdata in results["unblinded_scores"].items():
            comps = []
            for cn in case_nums:
                case_data = mdata["cases"].get(str(cn), {})
                comp = case_data.get("composite", -1)
                if comp >= 0:
                    comps.append(comp)
            avg = np.mean(comps) if comps else -1
            model_avgs.append(avg)
            row.append(f"| {avg:.2f} " if avg >= 0 else "| N/A ")
        total_avg = np.mean([v for v in model_avgs if v >= 0])
        row.append(f"| {total_avg:.2f} |")
        lines.append("".join(row))

    lines.append("")
    lines.append("## 블라인딩 조건 기존 CRS (참고)")
    lines.append("")
    lines.append("| 정부 | CRS (블라인딩) |")
    lines.append("|------|:-----------:|")
    blinded_crs = {
        "노무현 정부": 3.53, "이명박 정부": 3.40,
        "박근혜 정부": 2.07, "문재인 정부": 3.76, "윤석열 정부": 2.04,
    }
    for gov, crs in blinded_crs.items():
        lines.append(f"| {gov} | {crs:.2f} |")

    lines.extend([
        "",
        "## 해석",
        "",
        "- 블라인딩/비블라인딩 점수 차이가 작으면: 블라인딩이 채점 행위에 영향을 주지 않았음 (probe test와 일관)",
        "- 차이가 크면: 블라인딩이 실효적이지 않더라도 모델의 채점 앵커링에 영향을 줬을 가능성",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="A-2: 블라인딩 유무 점수 비교")
    parser.add_argument("--models", nargs="+", default=list(MODEL_CALLERS.keys()))
    args = parser.parse_args()

    results = run_comparison(args.models)

    json_path = OUTPUT_DIR / "blinding_comparison_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 결과 저장: {json_path}")

    report_path = OUTPUT_DIR / "blinding_comparison_report.md"
    write_comparison_report(results, report_path)
    print(f"✓ 보고서 저장: {report_path}")


if __name__ == "__main__":
    main()
