"""
Crisis Response Adequacy Scoring: 18개 위기 사례에 대한 5 AI 블라인드 채점

- 18개 사건일지를 블라인드 처리 (정부명 → Alpha~Zeta)
- 5개 AI 모델이 3차원(D1 인지·결정, D2 적절성, D3 집행) × 0-4 채점
- 결과를 raw_deprecated/ (원시) 및 verified/ (최종) 에 저장

Usage:
    python data/scripts/crisis_scoring.py
    python data/scripts/crisis_scoring.py --models gpt claude   # 특정 모델만
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
from dotenv import load_dotenv

# ── .env 로드 ──
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DOWNLOADS = DATA_DIR / "raw_downloads"
RAW_DEPRECATED = DATA_DIR / "raw_deprecated"
VERIFIED = DATA_DIR / "verified"

# ═══════════════════════════════════════════════════════════
# BLIND MAPPING
# ═══════════════════════════════════════════════════════════

# Level 2 블라인딩: 대통령명 + 정당명 + 연도 일반화 + 고유사건명 추상화 (M14 해결)
BLIND_MAP = {
    # 대통령명/정부명
    "노무현": "Alpha", "노무현 정부": "Alpha 정부",
    "이명박": "Beta", "이명박 정부": "Beta 정부",
    "박근혜": "Gamma", "박근혜 정부": "Gamma 정부",
    "문재인": "Delta", "문재인 정부": "Delta 정부",
    "윤석열": "Epsilon", "윤석열 정부": "Epsilon 정부",
    "이재명": "Zeta", "이재명 정부": "Zeta 정부",
    # 정당명
    "더불어민주당": "여당A", "민주당": "여당A", "열린우리당": "여당A",
    "국민의힘": "여당B", "새누리당": "여당B", "한나라당": "여당B",
    "자유한국당": "여당B",
    # 고유 위기명 → 일반화
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
    "Zeta": [16, 17, 18],
}

SYSTEM_PROMPT = "당신은 정부의 위기 대응 역량을 평가하는 행정학·위기관리 전문가입니다. 요청된 JSON 형식에 맞춰 정확히 응답하세요."

# ═══════════════════════════════════════════════════════════
# AI MODEL CALLERS (ai_scoring_v2.py에서 재활용)
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
        raise ValueError(f"Gemini 응답에 candidates 없음: {data}")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise ValueError(f"Gemini 응답에 parts 없음: {candidates[0]}")
    return parts[0].get("text", "")


MODEL_CALLERS = {
    "gpt":    ("GPT-5.2",             call_openai),
    "claude": ("Claude Sonnet 4.6",   call_claude),
    "grok":   ("Grok-4-1",           call_grok),
    "clova":  ("HyperCLOVA HCX-007", call_clova),
    "gemini": ("Gemini 3 Flash",      call_gemini),
}

# ═══════════════════════════════════════════════════════════
# TIMELINE PARSING & BLINDING
# ═══════════════════════════════════════════════════════════

def load_timelines() -> str:
    path = RAW_DOWNLOADS / "crisis_timelines.md"
    return path.read_text(encoding="utf-8")


def blind_text(text: str) -> str:
    """Level 2 블라인딩: 이름 치환 + 연도 일반화 (M14 해결)."""
    result = text
    for orig, blind in sorted(BLIND_MAP.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, blind)
    # 연도 일반화: 4자리 연도 → "Y년" (임기 추론 방지)
    result = re.sub(r'(19|20)\d{2}년', 'Y년', result)
    result = re.sub(r'(19|20)\d{2}\.\d{1,2}', 'Y.M', result)
    result = re.sub(r'(19|20)\d{2}', 'YYYY', result)
    return result


def split_cases(raw: str) -> Dict[int, str]:
    """타임라인 파일을 Case별로 분리"""
    cases = {}
    pattern = re.compile(r"### Case (\d+):")
    parts = pattern.split(raw)
    # parts: [preamble, "1", case1_text, "2", case2_text, ...]
    for i in range(1, len(parts) - 1, 2):
        case_num = int(parts[i])
        case_text = parts[i + 1].strip()
        # 다음 섹션 헤더(## ) 이전까지만
        next_section = re.search(r"\n## ", case_text)
        if next_section:
            case_text = case_text[:next_section.start()]
        cases[case_num] = f"### Case {case_num}: {case_text}"
    return cases


# ═══════════════════════════════════════════════════════════
# SCORING PROMPT
# ═══════════════════════════════════════════════════════════

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

def make_prompt(case_text: str) -> str:
    return f"""아래 사건일지를 읽고, 해당 정부의 위기 대응을 3개 차원에서 0-4로 채점하십시오.

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


# ═══════════════════════════════════════════════════════════
# JSON PARSING
# ═══════════════════════════════════════════════════════════

def parse_scores(raw: str) -> Dict[str, Any]:
    s = raw.strip()
    # Extract JSON from markdown code blocks if present
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, re.DOTALL)
    if m:
        s = m.group(1)
    else:
        # Try to find raw JSON
        m2 = re.search(r"\{.*\}", s, re.DOTALL)
        if m2:
            s = m2.group(0)
    # Repair trailing commas
    s = re.sub(r",\s*([}\]])", r"\1", s)
    try:
        data = json.loads(s)
    except json.JSONDecodeError:
        print(f"  ⚠ JSON 파싱 실패: {s[:200]}")
        return {"D1": {"score": -1}, "D2": {"score": -1}, "D3": {"score": -1}, "composite": -1}
    return data


# ═══════════════════════════════════════════════════════════
# IDENTIFICATION TEST (H2 해결: 블라인딩 실효성 검증)
# ═══════════════════════════════════════════════════════════

def run_identification_test(blinded_cases: Dict[int, str], model_keys: List[str]) -> Dict:
    """블라인드 사례를 LLM에게 제시하고, 어느 정부인지 추측하게 하여 블라인딩 실효성 검증."""
    labels = sorted(set(gov for gov, cases in GOV_CASES.items() for _ in cases))
    sample_texts = []
    for gov_label in labels:
        case_nums = GOV_CASES.get(gov_label, [])
        for cn in case_nums[:1]:  # 정부당 1건만 사용
            if cn in blinded_cases:
                sample_texts.append(f"[{gov_label}] {blinded_cases[cn][:300]}")

    prompt = f"""아래는 블라인드 처리된 위기 사례입니다. 각 정부 라벨이 실제로 어느 나라의 어떤 시기 정부인지 추측하십시오.
모르는 경우 "식별 불가"로 답하십시오.

{chr(10).join(sample_texts)}

반드시 아래 JSON 형식으로만 응답하십시오.
{{
  {', '.join(f'"{l}": {{"guess": "추측", "confidence": 0.0}}' for l in labels)}
}}"""

    results = {}
    for mkey in model_keys:
        model_name, caller = MODEL_CALLERS[mkey]
        try:
            response = caller(prompt)
            data = json.loads(re.search(r"\{.*\}", response, re.DOTALL).group(0))
            results[mkey] = data
            correct = sum(1 for k, v in data.items()
                         if any(name in str(v.get("guess", ""))
                                for name in ["노무현", "이명박", "박근혜", "문재인", "윤석열", "이재명"]))
            print(f"  식별 테스트 [{model_name}]: {correct}/{len(labels)} 정부 식별 (chance=1)")
        except Exception as e:
            print(f"  식별 테스트 [{model_name}] 실패: {e}")
            results[mkey] = {"error": str(e)}
    return results


# ═══════════════════════════════════════════════════════════
# MAIN SCORING LOOP
# ═══════════════════════════════════════════════════════════

def run_scoring(model_keys: List[str]) -> Dict:
    print("=" * 60)
    print("Crisis Response Adequacy Scoring")
    print("=" * 60)

    # 1. Load & blind timelines
    raw = load_timelines()
    blinded = blind_text(raw)
    cases = split_cases(blinded)
    print(f"✓ {len(cases)}개 사례 로드 완료 (블라인드 처리)")

    # 2. Score each case with each model
    all_results: Dict[str, Dict[int, Dict]] = {}  # model -> case_num -> scores

    for mkey in model_keys:
        model_name, caller = MODEL_CALLERS[mkey]
        print(f"\n{'─' * 40}")
        print(f"모델: {model_name}")
        print(f"{'─' * 40}")
        all_results[mkey] = {}

        for case_num in sorted(cases.keys()):
            case_text = cases[case_num]
            prompt = make_prompt(case_text)
            print(f"  Case {case_num:2d} ... ", end="", flush=True)

            try:
                response = caller(prompt)
                scores = parse_scores(response)
                d1 = scores.get("D1", {}).get("score", -1)
                d2 = scores.get("D2", {}).get("score", -1)
                d3 = scores.get("D3", {}).get("score", -1)
                comp = scores.get("composite", -1)
                print(f"D1={d1} D2={d2} D3={d3} → {comp}")
                all_results[mkey][case_num] = scores
            except Exception as e:
                print(f"ERROR: {e}")
                all_results[mkey][case_num] = {
                    "D1": {"score": -1, "rationale": f"Error: {e}"},
                    "D2": {"score": -1, "rationale": f"Error: {e}"},
                    "D3": {"score": -1, "rationale": f"Error: {e}"},
                    "composite": -1,
                }

            time.sleep(2)  # rate limit

    return all_results


def compute_averages(all_results: Dict) -> Tuple[Dict, Dict]:
    """사례별 모델 평균, 정부별 평균 산출"""
    # Case-level averages
    case_avg = {}
    for case_num in range(1, 19):
        scores = []
        for mkey, mdata in all_results.items():
            if case_num in mdata:
                comp = mdata[case_num].get("composite", -1)
                if isinstance(comp, (int, float)) and comp >= 0:
                    scores.append(comp)
        if scores:
            case_avg[case_num] = round(sum(scores) / len(scores), 2)
        else:
            case_avg[case_num] = -1

    # Government-level averages
    gov_avg = {}
    for gov, case_nums in GOV_CASES.items():
        gov_scores = [case_avg[c] for c in case_nums if case_avg.get(c, -1) >= 0]
        if gov_scores:
            gov_avg[gov] = round(sum(gov_scores) / len(gov_scores), 2)
        else:
            gov_avg[gov] = -1

    return case_avg, gov_avg


def save_raw_results(all_results: Dict, case_avg: Dict, gov_avg: Dict):
    """원시 결과를 raw_deprecated/에 저장"""
    output = RAW_DEPRECATED / "crisis_scoring_results.md"

    lines = ["# Crisis Response Scoring: 원시 결과\n"]
    lines.append(f"> 모델: {', '.join(MODEL_CALLERS[k][0] for k in all_results.keys())}\n\n")

    # Model × Case detail
    for mkey, mdata in all_results.items():
        model_name = MODEL_CALLERS[mkey][0]
        lines.append(f"## {model_name}\n")
        lines.append("| Case | D1 | D2 | D3 | Composite | D1 근거 | D2 근거 | D3 근거 |")
        lines.append("|:----:|:--:|:--:|:--:|:---------:|---------|---------|---------|")
        for case_num in sorted(mdata.keys()):
            s = mdata[case_num]
            d1 = s.get("D1", {})
            d2 = s.get("D2", {})
            d3 = s.get("D3", {})
            comp = s.get("composite", -1)
            lines.append(
                f"| {case_num} | {d1.get('score', -1)} | {d2.get('score', -1)} | "
                f"{d3.get('score', -1)} | {comp} | "
                f"{d1.get('rationale', '')[:60]} | {d2.get('rationale', '')[:60]} | "
                f"{d3.get('rationale', '')[:60]} |"
            )
        lines.append("")

    # Case averages
    lines.append("## 사례별 모델 평균\n")
    lines.append("| Case | 평균 점수 |")
    lines.append("|:----:|:--------:|")
    for c in sorted(case_avg.keys()):
        lines.append(f"| {c} | {case_avg[c]} |")
    lines.append("")

    # Government averages
    lines.append("## 정부별 평균 (Crisis Response Score)\n")
    lines.append("| 정부 (블라인드) | 사례 | 평균 CRS |")
    lines.append("|:--------------:|:----:|:-------:|")
    for gov in ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]:
        cases_str = ", ".join(str(c) for c in GOV_CASES[gov])
        lines.append(f"| {gov} | {cases_str} | {gov_avg.get(gov, -1)} |")

    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ 원시 결과 저장: {output}")

    # Also save JSON
    json_out = RAW_DEPRECATED / "crisis_scoring_results.json"
    json_out.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ JSON 저장: {json_out}")


def save_final_score(gov_avg: Dict):
    """최종 점수를 verified/에 저장"""
    UNBLIND = {
        "Alpha": "노무현", "Beta": "이명박", "Gamma": "박근혜",
        "Delta": "문재인", "Epsilon": "윤석열", "Zeta": "이재명",
    }

    output = VERIFIED / "crisis_response_score.md"
    lines = [
        "# Crisis Response Score (위기 대응 적절성 점수)\n",
        "> 방법: 18개 위기 사례 × 5 AI 모델 블라인드 채점 (D1 인지·결정 + D2 적절성 + D3 집행, 각 0-4)",
        "> 최종 점수: 3차원 합계 / 3 → 사례별 모델 평균 → 정부별 사례 평균",
        "> 스케일: 0-4 (높을수록 좋음)\n",
        "---\n",
        "## 정부별 Crisis Response Score\n",
        "| 정부 | 사례 1 | 사례 2 | 사례 3 | **CRS** |",
        "|------|--------|--------|--------|:-------:|",
    ]

    for gov in ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]:
        name = UNBLIND[gov]
        case_nums = GOV_CASES[gov]
        crs = gov_avg.get(gov, -1)
        lines.append(f"| {name} | Case {case_nums[0]} | Case {case_nums[1]} | Case {case_nums[2]} | **{crs}** |")

    lines.append("\n---\n")
    lines.append("## Composite Scoring 반영\n")
    lines.append("- 기존 Recognition Lag를 **Crisis Response Score**로 교체")
    lines.append("- 방향: 높을수록 좋음")
    lines.append("- 스케일: 0-4\n")
    lines.append("---\n")
    lines.append("*5개 AI 모델의 블라인드 독립 채점을 통해 산출. 채점 원시 데이터는 raw_deprecated/crisis_scoring_results.md 참조.*")

    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ 최종 점수 저장: {output}")


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Crisis Response Adequacy Scoring")
    parser.add_argument("--models", nargs="*", default=list(MODEL_CALLERS.keys()),
                        choices=list(MODEL_CALLERS.keys()),
                        help="사용할 모델 (기본: 전체)")
    args = parser.parse_args()

    # Check API keys
    key_map = {
        "gpt": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "grok": "XAI_API_KEY",
        "clova": "CLOVA_STUDIO_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }
    available = []
    for m in args.models:
        env_key = key_map.get(m, "")
        if os.getenv(env_key):
            available.append(m)
        else:
            print(f"⚠ {MODEL_CALLERS[m][0]}: {env_key} 미설정 → 건너뜀")

    if not available:
        print("❌ 사용 가능한 모델이 없습니다. .env 파일의 API 키를 확인하세요.")
        sys.exit(1)

    print(f"사용 모델: {', '.join(MODEL_CALLERS[m][0] for m in available)}")

    # Run scoring
    all_results = run_scoring(available)

    # Compute averages
    case_avg, gov_avg = compute_averages(all_results)

    # Save
    save_raw_results(all_results, case_avg, gov_avg)
    save_final_score(gov_avg)

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)

    # Print summary
    UNBLIND = {"Alpha": "노무현", "Beta": "이명박", "Gamma": "박근혜",
               "Delta": "문재인", "Epsilon": "윤석열", "Zeta": "이재명"}
    print("\n정부별 Crisis Response Score:")
    for gov in ["Delta", "Zeta", "Alpha", "Beta", "Epsilon", "Gamma"]:
        print(f"  {UNBLIND[gov]:4s}: {gov_avg.get(gov, -1)}")


if __name__ == "__main__":
    main()
