"""
Probe Test: 블라인딩 침투 검증
Level 2 블라인딩된 위기 사례에서 5개 LLM이 정부 정체성을 추론할 수 있는지 측정.

Usage:
    python probe_test.py
    python probe_test.py --models gpt claude    # 특정 모델만
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
OUTPUT_DIR = PROJECT_ROOT / "paper_a"
OUTPUT_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════
# BLIND MAPPING (crisis_scoring.py에서 동일)
# ═══════════════════════════════════════════════════════════

BLIND_MAP = {
    "노무현": "Alpha", "노무현 정부": "Alpha 정부",
    "이명박": "Beta", "이명박 정부": "Beta 정부",
    "박근혜": "Gamma", "박근혜 정부": "Gamma 정부",
    "문재인": "Delta", "문재인 정부": "Delta 정부",
    "윤석열": "Epsilon", "윤석열 정부": "Epsilon 정부",
    "이재명": "Zeta", "이재명 정부": "Zeta 정부",
    "더불어민주당": "여당A", "민주당": "여당A", "열린우리당": "여당A",
    "국민의힘": "여당B", "새누리당": "여당B", "한나라당": "여당B",
    "자유한국당": "여당B",
    "세월호": "여객선 침몰 사고", "메르스": "감염병 확산", "MERS": "감염병 확산",
    "코로나19": "감염병 대유행", "코로나": "감염병 대유행", "COVID-19": "감염병 대유행",
    "이태원": "대규모 압사 사고", "오송": "지하차도 침수 사고",
    "잼버리": "국제행사 운영 실패",
    "천안함": "해군 함정 침몰", "연평도": "포격 도발",
    "카드대란": "신용카드 부실 위기",
}

GOV_CASES = {
    "Alpha": [1, 2, 3],
    "Beta": [4, 5, 6],
    "Gamma": [7, 8, 9],
    "Delta": [10, 11, 12],
    "Epsilon": [13, 14, 15],
}

GROUND_TRUTH = {
    "Alpha": "노무현",
    "Beta": "이명박",
    "Gamma": "박근혜",
    "Delta": "문재인",
    "Epsilon": "윤석열",
}

SYSTEM_PROMPT = (
    "당신은 비교행정학 전문가입니다. "
    "아래에 익명화된 정부의 위기 대응 사례가 제시됩니다. "
    "정부의 이름, 정당, 이념 성향은 알려지지 않았습니다. "
    "요청된 JSON 형식에 맞춰 정확히 응답하세요."
)

# ═══════════════════════════════════════════════════════════
# MODEL CALLERS
# ═══════════════════════════════════════════════════════════

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
            "temperature": 0.2,
            "max_completion_tokens": 4096,
            "response_format": {"type": "json_object"},
        },
        timeout=300,
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
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


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
            "temperature": 0.2,
            "max_completion_tokens": 4096,
        },
        timeout=300,
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
            "temperature": 0.2,
            "thinking": {"type": "enabled"},
        },
        timeout=300,
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
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096},
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError(f"Gemini: candidates 없음")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise ValueError(f"Gemini: parts 없음")
    return parts[0].get("text", "")


MODEL_CALLERS = {
    "gpt":    ("GPT-5.2",             call_openai),
    "claude": ("Claude Sonnet 4.6",   call_claude),
    "grok":   ("Grok-4-1",           call_grok),
    "clova":  ("HyperCLOVA HCX-007", call_clova),
    "gemini": ("Gemini 3 Flash",      call_gemini),
}

# ═══════════════════════════════════════════════════════════
# BLINDING & PARSING
# ═══════════════════════════════════════════════════════════

def blind_text(text: str) -> str:
    result = text
    for orig, blind in sorted(BLIND_MAP.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, blind)
    result = re.sub(r'(19|20)\d{2}년', 'Y년', result)
    result = re.sub(r'(19|20)\d{2}\.\d{1,2}', 'Y.M', result)
    result = re.sub(r'(19|20)\d{2}', 'YYYY', result)
    return result


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


# ═══════════════════════════════════════════════════════════
# PROBE TEST
# ═══════════════════════════════════════════════════════════

def build_probe_prompt(blinded_cases: dict[int, str]) -> str:
    labels = sorted(GOV_CASES.keys())
    sample_texts = []
    for label in labels:
        case_nums = GOV_CASES[label]
        for cn in case_nums[:1]:  # 정부당 대표 1건
            if cn in blinded_cases:
                text = blinded_cases[cn][:500]
                sample_texts.append(f"--- [{label} 정부 사례] ---\n{text}")

    prompt = f"""아래는 블라인드 처리된 5개 정부의 위기 대응 사례입니다.
각 정부의 라벨(Alpha, Beta, Gamma, Delta, Epsilon)이 실제로 어느 나라의 어떤 시기 정부인지 추측하십시오.

판단 근거도 함께 제시하십시오.
모르는 경우 "식별 불가"로 답하십시오.

{chr(10).join(sample_texts)}

반드시 아래 JSON 형식으로만 응답하십시오:
{{
  "Alpha": {{"guess": "추측한 정부명 또는 식별 불가", "confidence": 0.0, "clues": "판단 근거"}},
  "Beta": {{"guess": "...", "confidence": 0.0, "clues": "..."}},
  "Gamma": {{"guess": "...", "confidence": 0.0, "clues": "..."}},
  "Delta": {{"guess": "...", "confidence": 0.0, "clues": "..."}},
  "Epsilon": {{"guess": "...", "confidence": 0.0, "clues": "..."}}
}}"""
    return prompt


def check_identification(guess: str, true_name: str) -> str:
    if not guess or guess == "식별 불가":
        return "fail"
    guess_lower = guess.lower().replace(" ", "")
    if true_name in guess:
        return "exact"
    era_hints = {
        "노무현": ["참여정부", "2003", "2004", "2005", "2006", "2007"],
        "이명박": ["mb", "2008", "2009", "2010", "2011", "2012", "금융위기"],
        "박근혜": ["2013", "2014", "2015", "2016", "국정농단", "탄핵"],
        "문재인": ["2017", "2018", "2019", "2020", "2021", "코로나"],
        "윤석열": ["2022", "2023", "2024", "계엄", "비상계엄"],
    }
    for hint in era_hints.get(true_name, []):
        if hint in guess:
            return "partial"
    return "wrong"


def run_probe(model_keys: list[str]) -> dict:
    print("=" * 60)
    print("Probe Test: 블라인딩 침투 검증")
    print(f"시간: {datetime.now().isoformat()}")
    print("=" * 60)

    raw = (DATA_DIR / "raw_downloads" / "crisis_timelines.md").read_text(encoding="utf-8")
    blinded = blind_text(raw)
    cases = split_cases(blinded)
    print(f"✓ {len(cases)}개 사례 로드, 블라인드 처리 완료")

    # Case 16-18 (이재명) 제외
    cases = {k: v for k, v in cases.items() if k <= 15}
    print(f"✓ 이재명 제외, {len(cases)}개 사례 분석 대상")

    prompt = build_probe_prompt(cases)
    print(f"✓ 프롬프트 생성 완료 ({len(prompt)}자)")

    results = {
        "_metadata": {
            "timestamp": datetime.now().isoformat(),
            "n_governments": 5,
            "n_models": len(model_keys),
            "ground_truth": GROUND_TRUTH,
            "cases_per_gov": {k: v for k, v in GOV_CASES.items()},
        },
        "models": {},
        "summary": {},
    }

    for mkey in model_keys:
        model_name, caller = MODEL_CALLERS[mkey]
        print(f"\n{'─' * 40}")
        print(f"모델: {model_name}")
        print(f"{'─' * 40}")

        try:
            response = caller(prompt)
            data = extract_json(response)
            results["models"][mkey] = {
                "model_name": model_name,
                "raw_response": response[:2000],
                "parsed": data,
                "identification": {},
            }

            exact = 0
            partial = 0
            wrong = 0
            fail = 0

            for label, true_name in GROUND_TRUTH.items():
                entry = data.get(label, {})
                guess = entry.get("guess", "식별 불가")
                confidence = entry.get("confidence", 0.0)
                clues = entry.get("clues", "")
                status = check_identification(guess, true_name)

                results["models"][mkey]["identification"][label] = {
                    "true": true_name,
                    "guess": guess,
                    "confidence": confidence,
                    "clues": clues,
                    "status": status,
                }

                icon = {"exact": "●", "partial": "◐", "wrong": "✗", "fail": "○"}[status]
                print(f"  {label} ({true_name}): {icon} {status} — guess='{guess}' (conf={confidence})")

                if status == "exact":
                    exact += 1
                elif status == "partial":
                    partial += 1
                elif status == "wrong":
                    wrong += 1
                else:
                    fail += 1

            results["models"][mkey]["counts"] = {
                "exact": exact, "partial": partial, "wrong": wrong, "fail": fail,
            }
            rate = (exact + partial) / 5 * 100
            print(f"  → 식별률: {exact + partial}/5 ({rate:.0f}%), 정확={exact}, 부분={partial}, 오답={wrong}, 실패={fail}")

        except Exception as e:
            print(f"  ✗ 오류: {e}")
            results["models"][mkey] = {"error": str(e)}

        time.sleep(2)

    # Summary
    total_exact = sum(r.get("counts", {}).get("exact", 0) for r in results["models"].values() if "counts" in r)
    total_partial = sum(r.get("counts", {}).get("partial", 0) for r in results["models"].values() if "counts" in r)
    total_attempts = 5 * len([r for r in results["models"].values() if "counts" in r])

    results["summary"] = {
        "total_attempts": total_attempts,
        "exact_identifications": total_exact,
        "partial_identifications": total_partial,
        "total_identified": total_exact + total_partial,
        "identification_rate": (total_exact + total_partial) / total_attempts * 100 if total_attempts > 0 else 0,
        "chance_level": 20.0,
        "blinding_assessment": (
            "effective" if (total_exact + total_partial) / max(total_attempts, 1) <= 0.3
            else "partial" if (total_exact + total_partial) / max(total_attempts, 1) <= 0.6
            else "ineffective"
        ),
    }

    return results


def write_report(results: dict, path: Path):
    s = results["summary"]
    lines = [
        "# Probe Test 결과: 블라인딩 침투 검증",
        "",
        f"> 실행 시간: {results['_metadata']['timestamp']}",
        f"> 모델 수: {results['_metadata']['n_models']}",
        f"> 정부 수: {results['_metadata']['n_governments']} (이재명 제외)",
        "",
        "## 요약",
        "",
        f"- 총 식별 시도: {s['total_attempts']}건",
        f"- 정확 식별: {s['exact_identifications']}건",
        f"- 부분 식별: {s['partial_identifications']}건",
        f"- **총 식별률: {s['identification_rate']:.1f}%** (chance level: {s['chance_level']:.1f}%)",
        f"- **블라인딩 평가: {s['blinding_assessment']}**",
        "",
        "## 모델별 상세 결과",
        "",
    ]

    for mkey, mdata in results["models"].items():
        if "error" in mdata:
            lines.append(f"### {mkey}: 오류 — {mdata['error']}")
            continue

        model_name = mdata["model_name"]
        counts = mdata["counts"]
        rate = (counts["exact"] + counts["partial"]) / 5 * 100
        lines.append(f"### {model_name} — 식별률 {rate:.0f}%")
        lines.append("")
        lines.append("| 라벨 | 실제 정부 | 추측 | 신뢰도 | 결과 | 판단 근거 |")
        lines.append("|------|----------|------|:------:|:----:|----------|")

        for label in sorted(GROUND_TRUTH.keys()):
            ident = mdata["identification"].get(label, {})
            icon = {"exact": "●", "partial": "◐", "wrong": "✗", "fail": "○"}.get(ident.get("status", "fail"), "?")
            clues = ident.get("clues", "")[:80]
            lines.append(
                f"| {label} | {ident.get('true', '')} | {ident.get('guess', '')} "
                f"| {ident.get('confidence', 0):.2f} | {icon} {ident.get('status', '')} | {clues} |"
            )
        lines.append("")

    lines.extend([
        "## 해석 기준",
        "",
        "- **effective** (식별률 ≤30%): 블라인딩이 효과적. 논문에서 bias-mitigation 효과 주장 가능",
        "- **partial** (30% < 식별률 ≤ 60%): 부분적 블라인딩. 편향 완화 시도로 기록, 효과 주장 약화",
        "- **ineffective** (식별률 > 60%): 블라인딩 무효. 논문에서 블라인딩 효과 주장 불가",
        "",
        "● = 정확 식별, ◐ = 부분 식별(시기/맥락 추론), ✗ = 오답, ○ = 식별 실패/불가",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Probe Test: 블라인딩 침투 검증")
    parser.add_argument("--models", nargs="+", default=list(MODEL_CALLERS.keys()),
                        help="사용할 모델 (기본: 전체)")
    args = parser.parse_args()

    results = run_probe(args.models)

    json_path = OUTPUT_DIR / "probe_test_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 결과 저장: {json_path}")

    report_path = OUTPUT_DIR / "probe_test_report.md"
    write_report(results, report_path)
    print(f"✓ 보고서 저장: {report_path}")


if __name__ == "__main__":
    main()
