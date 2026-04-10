"""
G: No-Zero-Score 규칙 효과 검증
zero 허용 조건으로 ACW 1라운드를 채점하여, 기존(zero 금지) 점수 분포와 비교.

목적: 0점 금지 규칙이 중앙값 편향을 억제했는지, 아니면 분포를 왜곡했는지 판단.

Usage:
    python zero_score_test.py
    python zero_score_test.py --models gpt claude
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import numpy as np
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

GOVERNMENTS = [
    "노무현(2003-2008)", "이명박(2008-2013)", "박근혜(2013-2017)",
    "문재인(2017-2022)", "윤석열(2022-2025)",
]

ACW_CRITERIA = {
    "다양성": [
        ("V1", "문제 프레이밍의 다양성"),
        ("V2", "다수준 거버넌스"),
        ("V3", "다부문 접근"),
        ("V4", "솔루션의 다양성"),
    ],
    "학습 역량": [
        ("Lc1", "신뢰할 수 있는 기록 관리"),
        ("Lc2", "단일고리 학습"),
        ("Lc3", "이중고리 학습"),
        ("Lc4", "제도적 기억"),
    ],
    "자율적 변화": [
        ("RAC1", "혁신 실험 여지"),
        ("RAC2", "즉흥·대응 능력"),
        ("RAC3", "중복·완충성"),
        ("RAC4", "비중첩적 의사결정"),
    ],
    "리더십": [
        ("Le1", "비전 제시형 리더십"),
        ("Le2", "기업가적 리더십"),
        ("Le3", "협력적 리더십"),
        ("Le4", "반응적 리더십"),
    ],
    "자원": [
        ("Re1", "재정 자원 배분"),
        ("Re2", "인적 자원"),
        ("Re3", "권위적 자원"),
    ],
    "공정 거버넌스": [
        ("FG1", "정당성·책임성"),
        ("FG2", "형평성"),
        ("FG3", "반응성"),
        ("FG4", "투명성"),
    ],
}

ALL_CRITERIA = []
for dim, items in ACW_CRITERIA.items():
    for code, name in items:
        ALL_CRITERIA.append((code, name, dim))

SYSTEM_PROMPT = "당신은 한국 행정학·정책학 전문가입니다. 요청된 형식에 맞춰 정확히 응답하세요."

# Factsheet loading
def load_gov_factsheet(gov: str) -> str:
    fs_path = DATA_DIR / "gov_factsheets.md"
    if not fs_path.exists():
        return ""
    text = fs_path.read_text(encoding="utf-8")
    name = gov.split("(")[0]
    pattern = re.compile(rf"## {name}.*?(?=\n## |\Z)", re.DOTALL)
    m = pattern.search(text)
    return m.group(0) if m else ""

# ═══════════════════════════════════════════════════════════
# MODEL CALLERS
# ═══════════════════════════════════════════════════════════

def call_openai(system: str, prompt: str) -> str:
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("OPENAI_MODEL", "gpt-5.2"),
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "temperature": 0.2, "max_completion_tokens": 8192,
            "response_format": {"type": "json_object"},
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def call_claude(system: str, prompt: str) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.getenv("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        json={
            "model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            "max_tokens": 8192, "system": system,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

def call_grok(system: str, prompt: str) -> str:
    resp = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('XAI_API_KEY')}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning"),
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "temperature": 0.2, "max_completion_tokens": 8192,
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def call_clova(system: str, prompt: str) -> str:
    base_url = (os.getenv("CLOVA_STUDIO_BASE_URL") or "https://clovastudio.stream.ntruss.com").rstrip("/")
    model = os.getenv("CLOVA_STUDIO_MODEL", "HCX-007")
    resp = requests.post(
        f"{base_url}/v3/chat-completions/{model}",
        headers={"Authorization": f"Bearer {os.getenv('CLOVA_STUDIO_API_KEY')}", "Content-Type": "application/json"},
        json={
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "temperature": 0.2, "thinking": {"type": "enabled"},
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", data).get("message", {}).get("content", "")

def call_gemini(system: str, prompt: str) -> str:
    resp = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
        params={"key": os.getenv("GEMINI_API_KEY")},
        json={
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192},
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
# PROMPT (zero 허용 버전)
# ═══════════════════════════════════════════════════════════

def make_zero_allowed_prompt(gov: str, factsheet: str) -> str:
    criteria_text = ""
    for dim, items in ACW_CRITERIA.items():
        criteria_text += f"\n### {dim}\n"
        for code, name in items:
            criteria_text += f"- **{code}**: {name}\n"

    return f"""아래 정부에 대해 적응역량 수레바퀴(ACW)의 22개 기준을 -2 ~ +2로 채점하십시오.

**0점 사용 가능**: 판단이 어렵거나 중립적인 경우 0점을 부여할 수 있습니다.

## 채점 척도
- +2: 해당 기준에서 강한 긍정적 기여
- +1: 약한 긍정적 기여
- 0: 중립 또는 판단 보류
- -1: 약한 부정적 기여
- -2: 강한 부정적 기여

## 채점 기준
{criteria_text}

## 대상 정부
{gov}

{factsheet}

## 응답 형식 (JSON)
각 기준에 대해 score와 rationale을 제시하십시오.
```json
{{
{', '.join(f'  "{code}": {{"score": <-2~+2>, "rationale": "<1문장>"}}' for code, _, _ in ALL_CRITERIA)}
}}
```"""


def extract_json(text: str) -> dict:
    md = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if md:
        return json.loads(md.group(1))
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        return json.loads(m.group(0))
    return json.loads(text)


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def run_zero_test(model_keys: list[str]) -> dict:
    print("=" * 60)
    print("G: No-Zero-Score 규칙 효과 검증")
    print(f"시간: {datetime.now().isoformat()}")
    print("조건: 0점 허용 (zero-allowed), ACW 22기준, 1라운드")
    print("=" * 60)

    results = {
        "_metadata": {
            "timestamp": datetime.now().isoformat(),
            "condition": "zero-allowed (0점 허용)",
            "n_governments": len(GOVERNMENTS),
            "n_criteria": len(ALL_CRITERIA),
            "n_models": len(model_keys),
        },
        "scores": {},
    }

    for mkey in model_keys:
        model_name, caller = MODEL_CALLERS[mkey]
        print(f"\n{'─' * 40}")
        print(f"모델: {model_name}")
        print(f"{'─' * 40}")
        results["scores"][mkey] = {"model_name": model_name, "governments": {}}

        for gov in GOVERNMENTS:
            short = gov.split("(")[0]
            factsheet = load_gov_factsheet(gov)
            prompt = make_zero_allowed_prompt(gov, factsheet)
            print(f"  {short} ... ", end="", flush=True)

            try:
                response = caller(SYSTEM_PROMPT, prompt)
                data = extract_json(response)

                gov_scores = {}
                zeros = 0
                for code, _, _ in ALL_CRITERIA:
                    entry = data.get(code, {})
                    score = int(entry.get("score", 0)) if isinstance(entry, dict) else int(entry)
                    gov_scores[code] = score
                    if score == 0:
                        zeros += 1

                results["scores"][mkey]["governments"][gov] = gov_scores
                avg = np.mean(list(gov_scores.values()))
                print(f"avg={avg:+.2f}, zeros={zeros}/{len(ALL_CRITERIA)}")

            except Exception as e:
                print(f"오류: {e}")
                results["scores"][mkey]["governments"][gov] = {"error": str(e)}

            time.sleep(2)

    return results


def write_report(results: dict, path: Path):
    # Load original no-zero scores for comparison
    raw_path = DATA_DIR / "scripts" / "tables" / "scoring_v2_raw.json"
    original = {}
    if raw_path.exists():
        with open(raw_path, 'r') as f:
            original = json.load(f)

    model_map = {"gpt": "gpt", "claude": "claude", "grok": "grok", "clova": "clova", "gemini": "gemini"}

    lines = [
        "# G: No-Zero-Score 규칙 효과 검증 결과",
        "",
        f"> 실행 시간: {results['_metadata']['timestamp']}",
        f"> 조건: {results['_metadata']['condition']}",
        f"> 기준 수: {results['_metadata']['n_criteria']}개 (ACW 22기준)",
        "",
        "## 비교 설계",
        "",
        "- **no-zero 조건**: 기존 scoring_v2_raw.json (0점 금지, -2~-1 또는 +1~+2만 허용)",
        "- **zero-allowed 조건**: 본 실험 (0점 허용, -2~+2 전체 사용 가능)",
        "",
        "## 0점 발생 빈도",
        "",
    ]

    # Zero counts per model per government
    lines.append("| 정부 |" + "|".join(
        f" {results['scores'][m]['model_name']} " for m in results['scores']
    ) + "| 평균 |")
    lines.append("|------|" + "|".join(":------:" for _ in results['scores']) + "|:------:|")

    for gov in GOVERNMENTS:
        short = gov.split("(")[0]
        row = [f"| {short} "]
        zero_counts = []
        for mkey in results["scores"]:
            gov_data = results["scores"][mkey]["governments"].get(gov, {})
            if "error" in gov_data:
                row.append("| ERR ")
                continue
            zeros = sum(1 for v in gov_data.values() if v == 0)
            zero_counts.append(zeros)
            row.append(f"| {zeros}/22 ")
        avg_z = np.mean(zero_counts) if zero_counts else 0
        row.append(f"| {avg_z:.1f}/22 |")
        lines.append("".join(row))

    # Score distribution comparison
    lines.extend([
        "",
        "## 점수 분포 비교 (전체 항목)",
        "",
        "| 조건 | -2 | -1 | 0 | +1 | +2 | 평균 |",
        "|------|:---:|:---:|:---:|:---:|:---:|:---:|",
    ])

    # Original (no-zero)
    orig_all = []
    if original and "panel1_acw" in original:
        for mkey in model_map:
            if mkey in original["panel1_acw"]:
                for gov in GOVERNMENTS:
                    if gov in original["panel1_acw"][mkey]:
                        for code, data in original["panel1_acw"][mkey][gov]["scores"].items():
                            orig_all.append(int(data["score"]))

    if orig_all:
        dist_orig = {s: orig_all.count(s) for s in [-2, -1, 0, 1, 2]}
        total_orig = len(orig_all)
        lines.append(
            f"| No-zero | {dist_orig.get(-2,0)} ({dist_orig.get(-2,0)/total_orig*100:.0f}%) "
            f"| {dist_orig.get(-1,0)} ({dist_orig.get(-1,0)/total_orig*100:.0f}%) "
            f"| {dist_orig.get(0,0)} ({dist_orig.get(0,0)/total_orig*100:.0f}%) "
            f"| {dist_orig.get(1,0)} ({dist_orig.get(1,0)/total_orig*100:.0f}%) "
            f"| {dist_orig.get(2,0)} ({dist_orig.get(2,0)/total_orig*100:.0f}%) "
            f"| {np.mean(orig_all):+.2f} |"
        )

    # Zero-allowed
    zero_all = []
    for mkey in results["scores"]:
        for gov in GOVERNMENTS:
            gov_data = results["scores"][mkey]["governments"].get(gov, {})
            if "error" not in gov_data:
                zero_all.extend(gov_data.values())

    if zero_all:
        dist_zero = {s: zero_all.count(s) for s in [-2, -1, 0, 1, 2]}
        total_zero = len(zero_all)
        lines.append(
            f"| Zero-allowed | {dist_zero.get(-2,0)} ({dist_zero.get(-2,0)/total_zero*100:.0f}%) "
            f"| {dist_zero.get(-1,0)} ({dist_zero.get(-1,0)/total_zero*100:.0f}%) "
            f"| {dist_zero.get(0,0)} ({dist_zero.get(0,0)/total_zero*100:.0f}%) "
            f"| {dist_zero.get(1,0)} ({dist_zero.get(1,0)/total_zero*100:.0f}%) "
            f"| {dist_zero.get(2,0)} ({dist_zero.get(2,0)/total_zero*100:.0f}%) "
            f"| {np.mean(zero_all):+.2f} |"
        )

    # Government average comparison
    lines.extend([
        "",
        "## 정부별 평균 점수 비교",
        "",
        "| 정부 | No-zero 평균 | Zero-allowed 평균 | 차이 | 순위(NZ) | 순위(ZA) |",
        "|------|:-----------:|:----------------:|:----:|:-------:|:-------:|",
    ])

    nz_avgs = {}
    za_avgs = {}
    for gov in GOVERNMENTS:
        short = gov.split("(")[0]
        # No-zero averages
        nz_vals = []
        if original and "panel1_acw" in original:
            for mkey in model_map:
                if mkey in original["panel1_acw"] and gov in original["panel1_acw"][mkey]:
                    scores = original["panel1_acw"][mkey][gov]["scores"]
                    nz_vals.extend(int(s["score"]) for s in scores.values())
        nz_avg = np.mean(nz_vals) if nz_vals else 0
        nz_avgs[gov] = nz_avg

        # Zero-allowed averages
        za_vals = []
        for mkey in results["scores"]:
            gov_data = results["scores"][mkey]["governments"].get(gov, {})
            if "error" not in gov_data:
                za_vals.extend(gov_data.values())
        za_avg = np.mean(za_vals) if za_vals else 0
        za_avgs[gov] = za_avg

    nz_ranked = sorted(nz_avgs.items(), key=lambda x: -x[1])
    za_ranked = sorted(za_avgs.items(), key=lambda x: -x[1])
    nz_rank = {k: i+1 for i, (k, _) in enumerate(nz_ranked)}
    za_rank = {k: i+1 for i, (k, _) in enumerate(za_ranked)}

    for gov in GOVERNMENTS:
        short = gov.split("(")[0]
        diff = za_avgs[gov] - nz_avgs[gov]
        lines.append(f"| {short} | {nz_avgs[gov]:+.2f} | {za_avgs[gov]:+.2f} | {diff:+.2f} | {nz_rank[gov]} | {za_rank[gov]} |")

    rank_changed = any(nz_rank[g] != za_rank[g] for g in GOVERNMENTS)
    lines.extend([
        "",
        f"**순위 변동: {'있음' if rank_changed else '없음'}**",
        "",
        "## 결론",
        "",
        "- 0점 발생 빈도가 높으면: no-zero 규칙이 중립 판단을 억제하여 분포를 왜곡했을 가능성",
        "- 0점 발생 빈도가 낮으면: no-zero 규칙이 실질적 영향이 없었음 (모델이 원래 극단값 선호)",
        "- 순위 변동 유무가 핵심: 변동 없으면 no-zero 규칙이 결과 방향성에 영향 없음",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="G: No-Zero-Score 규칙 효과 검증")
    parser.add_argument("--models", nargs="+", default=list(MODEL_CALLERS.keys()))
    args = parser.parse_args()

    results = run_zero_test(args.models)

    json_path = OUTPUT_DIR / "zero_score_test_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 결과 저장: {json_path}")

    report_path = OUTPUT_DIR / "zero_score_test_report.md"
    write_report(results, report_path)
    print(f"✓ 보고서 저장: {report_path}")


if __name__ == "__main__":
    main()
