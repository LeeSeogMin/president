"""
5-Round Multi-AI Scoring: 기존 1회 측정에 4회 추가 → 총 5회 평균으로 측정 안정성 향상

- 판단유보(0점) 금지 지침 추가
- CLOVA thinking 비활성화
- 라운드별 독립 파일 저장 (덮어쓰기 방지)
- 건 단위 즉시 저장 (중단 복구 가능)

Usage:
    py multi_round_scoring.py                        # 라운드 2~5 실행 + 집계
    py multi_round_scoring.py --round 3              # 특정 라운드만
    py multi_round_scoring.py --aggregate-only        # 집계만
    py multi_round_scoring.py --models gpt claude     # 특정 모델만
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from dotenv import load_dotenv

# ── ai_scoring_v2.py에서 재사용 ──
from ai_scoring_v2 import (
    extract_json,
    ACW_CRITERIA, ALL_ACW_CODES, INST_DIMENSIONS, INST_LOCAL_DIMENSIONS,
    AGENDA_CRITERIA,
    SYSTEM_PROMPT,
    GOVERNMENTS, LOCAL_GOVERNMENTS,
    ACW_EXCLUDE_SEONGNAM, ACW_EXCLUDE_GYEONGGI,
    call_openai, call_claude, call_grok, call_gemini,
    build_acw_prompt, build_inst_prompt,
    build_acw_local_prompt, build_inst_local_prompt, build_agenda_prompt,
    fleiss_kappa, interpret_kappa,
    compute_reliability, compute_consensus,
    _get_acw_local_codes,
)

# ── .env 로드 ──
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

# ═══════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════

OUTPUT_DIR = Path(__file__).resolve().parent / "tables"
ROUNDS_DIR = OUTPUT_DIR / "rounds"
ROUNDS_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# CLOVA — thinking 비활성화 버전
# ═══════════════════════════════════════════════════════════

def call_clova_no_thinking(prompt: str) -> str:
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
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    result = data.get("result", data)
    message = result.get("message", {})
    return message.get("content", "")


# ═══════════════════════════════════════════════════════════
# MODEL CALLERS (clova만 교체)
# ═══════════════════════════════════════════════════════════

MODEL_CALLERS = {
    "gpt":    ("GPT-5.2",              call_openai),
    "claude": ("Claude Sonnet 4.6",    call_claude),
    "grok":   ("Grok-4-1",            call_grok),
    "clova":  ("HyperCLOVA HCX-007",  call_clova_no_thinking),
    "gemini": ("Gemini 3 Flash",       call_gemini),
}

# ═══════════════════════════════════════════════════════════
# 판단유보 금지 지침
# ═══════════════════════════════════════════════════════════

NO_RESERVATION_INSTRUCTION = """

## 절대 준수: 판단유보 금지
- 0점을 '정보 부족', '판단 유보', '평가 불가'의 이유로 부여하는 것은 금지됩니다.
- 0점은 긍정적 요소와 부정적 요소가 진정으로 상쇄되는 경우에만 허용됩니다.
- 근거가 있다면 반드시 양수(+1/+2) 또는 음수(-1/-2)를 선택하세요.
- 각 기준에 대해 반드시 구체적 근거와 함께 차등 점수를 부여하세요.
"""


def wrap_prompt(original_prompt: str) -> str:
    return original_prompt + NO_RESERVATION_INSTRUCTION


# ═══════════════════════════════════════════════════════════
# TASK 정의 — 모든 panel/analysis 조합
# ═══════════════════════════════════════════════════════════

def _get_all_tasks() -> list:
    """
    Returns list of (panel_key, analysis_label, gov_list, prompt_builder, expected_codes_fn)
    expected_codes_fn(gov) → list of expected score codes for validation
    """
    inst_codes = [c for c, _, _ in INST_DIMENSIONS]
    inst_local_codes = [c for c, _, _ in INST_LOCAL_DIMENSIONS]
    agenda_codes = [c for c, _, _ in AGENDA_CRITERIA]

    return [
        # Panel 1
        ("panel1_acw",     "ACW",       GOVERNMENTS,       build_acw_prompt,        lambda gov: ALL_ACW_CODES),
        ("panel1_inst",    "INST",      GOVERNMENTS,       build_inst_prompt,       lambda gov: inst_codes),
        # Panel 2
        ("panel2_acw",     "ACW-local", LOCAL_GOVERNMENTS, build_acw_local_prompt,  lambda gov: _get_acw_local_codes(gov)),
        ("panel2_inst",    "INST-local",LOCAL_GOVERNMENTS, build_inst_local_prompt, lambda gov: inst_local_codes),
        ("panel2_agenda",  "AGENDA",    LOCAL_GOVERNMENTS, build_agenda_prompt,     lambda gov: agenda_codes),
    ]


# ═══════════════════════════════════════════════════════════
# VALIDATION — 점수 검증 및 판단유보 감지
# ═══════════════════════════════════════════════════════════

def _validate_acw_result(data: dict, expected_codes: List[str]) -> Tuple[bool, str]:
    """ACW 결과 검증: 코드 완전성, 0점 비율, 획일성"""
    scores = data.get("scores", {})
    found = [c for c in expected_codes if c in scores]

    if len(found) < len(expected_codes) * 0.8:
        return False, f"코드 부족: {len(found)}/{len(expected_codes)}"

    values = []
    for c in found:
        s = scores[c].get("score", 0)
        s = int(s) if s is not None else 0
        if s < -2 or s > 2:
            return False, f"범위 초과: {c}={s}"
        values.append(s)

    if not values:
        return False, "점수 없음"

    zero_count = values.count(0)
    zero_ratio = zero_count / len(values)
    if zero_ratio >= 0.5:
        return False, f"0점 비율 과다: {zero_count}/{len(values)} ({zero_ratio:.0%})"

    if len(set(values)) == 1:
        return False, f"전부 동일 점수: {values[0]}"

    return True, "OK"


def _validate_inst_result(data: dict, expected_codes: List[str]) -> Tuple[bool, str]:
    """INST 결과 검증: D1~D4, 0점 과다, 범위"""
    scores = data.get("scores", {})
    found = [c for c in expected_codes if c in scores]

    if len(found) < len(expected_codes):
        return False, f"코드 부족: {len(found)}/{len(expected_codes)}"

    values = []
    zero_count = 0
    for c in found:
        s = scores[c].get("score", 0)
        s = int(s) if s is not None else 0
        if s < 0 or s > 2:
            return False, f"범위 초과: {c}={s} (0~2 필요)"
        values.append(s)
        if s == 0:
            zero_count += 1

    if zero_count >= 3:
        return False, f"0점 {zero_count}개 이상"

    return True, "OK"


def _validate_agenda_result(data: dict, expected_codes: List[str]) -> Tuple[bool, str]:
    """Lowi/Agenda 결과 검증: E1~E5 백분율"""
    scores = data.get("scores", {})
    found = [c for c in expected_codes if c in scores]

    if len(found) < len(expected_codes):
        return False, f"코드 부족: {len(found)}/{len(expected_codes)}"

    return True, "OK"


def validate_result(panel_key: str, data: dict, expected_codes: List[str]) -> Tuple[bool, str]:
    if "scores" not in data or not data["scores"]:
        return False, "scores 필드 없음"

    if "acw" in panel_key:
        return _validate_acw_result(data, expected_codes)
    elif "inst" in panel_key:
        return _validate_inst_result(data, expected_codes)
    elif "agenda" in panel_key:
        return _validate_agenda_result(data, expected_codes)
    return True, "OK"


# ═══════════════════════════════════════════════════════════
# SCORE ONE — 단일 건 호출 (검증 + 재시도)
# ═══════════════════════════════════════════════════════════

def _print(msg: str) -> None:
    print(msg, flush=True)


def _extract_scores_fallback(raw: str, expected_codes: List[str]) -> Optional[dict]:
    """잘린 JSON에서 score 항목을 정규식으로 직접 추출 (fallback)"""
    scores = {}
    for code in expected_codes:
        # "V1": {"score": -1, "rationale": "..."} 패턴
        pattern = rf'"{code}"\s*:\s*\{{\s*"score"\s*:\s*([+-]?\d+)'
        m = re.search(pattern, raw)
        if m:
            score_val = int(m.group(1))
            # rationale도 추출 시도
            rat_pattern = rf'"{code}"\s*:\s*\{{\s*"score"\s*:\s*[+-]?\d+\s*,\s*"rationale"\s*:\s*"([^"]*)"'
            rm = re.search(rat_pattern, raw)
            rationale = rm.group(1) if rm else "fallback 추출"
            scores[code] = {"score": score_val, "rationale": rationale}

    if len(scores) >= len(expected_codes) * 0.8:  # 80% 이상 추출 성공
        return {"scores": scores}
    return None


def score_one_round(model_key: str, prompt: str, panel_key: str,
                    expected_codes: List[str], max_retries: int = 5) -> Tuple[Optional[dict], str]:
    """단일 건 API 호출 + 검증 + 지수 백오프 재시도"""
    label, caller = MODEL_CALLERS[model_key]
    last_error = ""
    last_raw = ""

    for attempt in range(max_retries):
        try:
            raw = caller(prompt)
            last_raw = raw
            result = extract_json(raw)

            valid, reason = validate_result(panel_key, result, expected_codes)
            if not valid:
                raise ValueError(f"검증 실패: {reason}")

            return result, ""
        except Exception as e:
            last_error = str(e)
            # JSON 파싱 실패 시 fallback 추출 시도
            if "JSON" in last_error or "검증 실패: 코드 부족" in last_error:
                fallback = _extract_scores_fallback(last_raw, expected_codes)
                if fallback:
                    valid, reason = validate_result(panel_key, fallback, expected_codes)
                    if valid:
                        _print(f"    fallback 추출 성공 (시도 {attempt+1})")
                        return fallback, ""
            if attempt < max_retries - 1:
                wait = 3 * (2 ** attempt)  # 3, 6, 12, 24, 48
                _print(f"    오류 (시도 {attempt+1}): {last_error} → {wait}초 대기")
                time.sleep(wait)

    return None, last_error


# ═══════════════════════════════════════════════════════════
# INCREMENTAL SAVE — 건 단위 즉시 저장
# ═══════════════════════════════════════════════════════════

def save_incremental(round_path: Path, panel_key: str, model_key: str,
                     gov: str, result: dict) -> None:
    """건 단위 즉시 저장 — 중단 시 복구 가능"""
    data = {}
    if round_path.exists():
        with open(round_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    data.setdefault(panel_key, {}).setdefault(model_key, {})[gov] = result
    with open(round_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_already_done(round_data: dict, panel_key: str, model_key: str, gov: str) -> bool:
    """해당 건이 이미 완료되었는지 확인"""
    return gov in round_data.get(panel_key, {}).get(model_key, {})


# ═══════════════════════════════════════════════════════════
# RUN ROUND — 한 라운드 전체 실행
# ═══════════════════════════════════════════════════════════

def run_round(round_num: int, model_filter: Optional[List[str]] = None) -> None:
    """한 라운드 전체 실행 (미완료 건만 처리, 이미 완료된 라운드는 스킵)"""
    round_path = ROUNDS_DIR / f"round_{round_num}.json"

    # 기존 데이터 로드 (이어하기 지원)
    existing = {}
    if round_path.exists():
        with open(round_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    all_tasks = _get_all_tasks()
    all_models = list(MODEL_CALLERS.keys())
    if model_filter:
        all_models = [m for m in all_models if m in model_filter]

    total_tasks = 0
    completed_tasks = 0
    skipped_tasks = 0

    # 전체 건수 사전 계산
    for panel_key, analysis_label, gov_list, prompt_builder, codes_fn in all_tasks:
        for mk in all_models:
            for gov in gov_list:
                total_tasks += 1
                if is_already_done(existing, panel_key, mk, gov):
                    skipped_tasks += 1

    _print(f"\n{'='*60}")
    _print(f"[Round {round_num}] 시작 — 총 {total_tasks}건 (완료 {skipped_tasks}건, 남은 {total_tasks - skipped_tasks}건)")
    _print(f"{'='*60}")

    if skipped_tasks == total_tasks:
        _print(f"[Round {round_num}] 이미 모든 건 완료 — 스킵")
        return

    for panel_key, analysis_label, gov_list, prompt_builder, codes_fn in all_tasks:
        _print(f"\n▶ [Round {round_num}] {panel_key} ({analysis_label})")
        for mk in all_models:
            label = MODEL_CALLERS[mk][0]
            for gov in gov_list:
                if is_already_done(existing, panel_key, mk, gov):
                    continue

                expected_codes = codes_fn(gov)
                prompt = wrap_prompt(prompt_builder(gov))

                _print(f"  [{label}] {gov} ({analysis_label})...", )
                result, err = score_one_round(mk, prompt, panel_key, expected_codes)

                if result:
                    save_incremental(round_path, panel_key, mk, gov, result)
                    # 간략 요약
                    scores = result.get("scores", {})
                    if "acw" in panel_key:
                        vals = [int(scores.get(c, {}).get("score", 0)) for c in expected_codes if c in scores]
                        avg = sum(vals) / len(vals) if vals else 0
                        _print(f"    ✓ avg={avg:+.2f}")
                    elif "inst" in panel_key:
                        vals = [int(scores.get(c, {}).get("score", 0)) for c in expected_codes if c in scores]
                        total = sum(vals)
                        _print(f"    ✓ sum={total}")
                    else:
                        _print(f"    ✓ OK")
                    completed_tasks += 1
                else:
                    _print(f"    ✗ 실패: {err}")

                # 라운드 내 쿨다운
                time.sleep(1)

    _print(f"\n[Round {round_num}] 완료 — 신규 {completed_tasks}건 처리")


# ═══════════════════════════════════════════════════════════
# AGGREGATE — 5라운드 평균 계산
# ═══════════════════════════════════════════════════════════

def aggregate_rounds(n_rounds: int = 5) -> dict:
    """5라운드 데이터를 로드하여 기준별 평균/표준편차 계산"""
    rounds_data = []
    for i in range(1, n_rounds + 1):
        path = ROUNDS_DIR / f"round_{i}.json"
        if not path.exists():
            _print(f"⚠ round_{i}.json 없음 — 건너뜀")
            continue
        with open(path, "r", encoding="utf-8") as f:
            rounds_data.append(json.load(f))

    if not rounds_data:
        _print("⚠ 로드된 라운드 데이터 없음")
        return {}

    n_actual = len(rounds_data)
    _print(f"\n▶ 집계: {n_actual}개 라운드 데이터 로드")

    aggregated = {}

    # 모든 panel_key를 수집
    all_panel_keys: Set[str] = set()
    for rd in rounds_data:
        all_panel_keys.update(rd.keys())

    for panel_key in sorted(all_panel_keys):
        aggregated[panel_key] = {}

        # 모든 model_key 수집
        all_model_keys: Set[str] = set()
        for rd in rounds_data:
            all_model_keys.update(rd.get(panel_key, {}).keys())

        for mk in sorted(all_model_keys):
            aggregated[panel_key][mk] = {}

            # 모든 gov 수집
            all_govs: Set[str] = set()
            for rd in rounds_data:
                all_govs.update(rd.get(panel_key, {}).get(mk, {}).keys())

            for gov in sorted(all_govs):
                gov_results = []
                for rd in rounds_data:
                    gov_data = rd.get(panel_key, {}).get(mk, {}).get(gov)
                    if gov_data:
                        gov_results.append(gov_data)

                if not gov_results:
                    continue

                # scores 키 수집
                all_codes: Set[str] = set()
                for gr in gov_results:
                    all_codes.update(gr.get("scores", {}).keys())

                avg_scores = {}
                for code in sorted(all_codes):
                    score_values = []
                    for gr in gov_results:
                        s = gr.get("scores", {}).get(code, {}).get("score")
                        if s is not None:
                            score_values.append(float(s))

                    if score_values:
                        mean_val = statistics.mean(score_values)
                        std_val = statistics.stdev(score_values) if len(score_values) > 1 else 0.0
                        avg_scores[code] = {
                            "score": round(mean_val, 2),
                            "std": round(std_val, 2),
                            "scores_all": score_values,
                            "n_rounds": len(score_values),
                        }

                aggregated[panel_key][mk][gov] = {
                    "government": gov_results[0].get("government", gov),
                    "scores": avg_scores,
                    "n_rounds_available": len(gov_results),
                }

    # 저장
    avg_path = OUTPUT_DIR / "scoring_v2_5round_avg.json"
    with open(avg_path, "w", encoding="utf-8") as f:
        json.dump(aggregated, f, ensure_ascii=False, indent=2)
    _print(f"  5라운드 평균 저장: {avg_path}")

    return aggregated


# ═══════════════════════════════════════════════════════════
# REPORT — 5회 평균 기반 보고서 생성
# ═══════════════════════════════════════════════════════════

def _extract_simple_scores(aggregated: dict, panel_key: str) -> Dict[str, Dict[str, dict]]:
    """aggregated 데이터에서 score만 추출 → compute_consensus 등에 넘기기 위한 형태로 변환"""
    result = {}
    for mk, govs in aggregated.get(panel_key, {}).items():
        result[mk] = {}
        for gov, gdata in govs.items():
            scores_simple = {}
            for code, cdata in gdata.get("scores", {}).items():
                scores_simple[code] = {"score": cdata["score"], "rationale": f"{cdata['n_rounds']}회 평균"}
            result[mk][gov] = {"government": gdata.get("government", gov), "scores": scores_simple}
    return result


def generate_5round_report(aggregated: dict) -> str:
    """5회 평균 기반 통합 보고서"""
    models = list(MODEL_CALLERS.keys())
    model_labels = [MODEL_CALLERS[m][0] for m in models]

    lines = [
        "# 2-Panel Multi-AI 스코어링 v2 — 5회 평균 결과",
        "",
        f"> **생성일**: {time.strftime('%Y-%m-%d %H:%M')}",
        f"> **코더**: {', '.join(model_labels)}",
        f"> **측정 횟수**: 5회 (라운드 1~5 평균)",
        f"> **Panel 1**: 중앙정부 {len(GOVERNMENTS)}개 대통령",
        f"> **Panel 2**: 지방정부 (성남시장, 경기도지사)",
        "",
    ]

    # ── Panel 1: ACW ──
    p1_acw = _extract_simple_scores(aggregated, "panel1_acw")
    if p1_acw:
        p1_acw_models = [m for m in models if m in p1_acw and p1_acw[m]]
        if p1_acw_models:
            rel = compute_reliability(p1_acw, GOVERNMENTS, ALL_ACW_CODES, (-2, 2))
            consensus = compute_consensus(p1_acw, GOVERNMENTS, ALL_ACW_CODES)

            dim_criteria = {dim: [c[0] for c in criteria] for dim, criteria in ACW_CRITERIA.items()}

            lines.extend([
                "---",
                "## Panel 1: ACW — 중앙정부 5모델 결과 (5회 평균)",
                "",
                f"### 코더 간 신뢰도 (Fleiss' kappa, 5회 평균 점수 기반)",
                "",
                f"- **Fleiss' kappa**: {rel['overall_kappa']} ({rel['interpretation_kappa']})",
                f"- **Krippendorff α(ordinal)**: {rel.get('overall_alpha_ordinal', 'N/A')} ({rel.get('interpretation_alpha', '')})",
                f"- **코더 수**: {rel['n_coders']}",
                "",
            ])

            if rel["gov_kappas"]:
                lines.extend(["| 정부 | kappa |", "|------|-------|"])
                for gov, k in rel["gov_kappas"].items():
                    lines.append(f"| {gov} | {k} |")
                lines.append("")

            # 모델별 총 평균
            lines.extend(["### 모델별 정부 총 평균 점수 (5회 평균)", ""])
            header = "| 정부 | " + " | ".join(MODEL_CALLERS[m][0] for m in p1_acw_models) + " | **합의** |"
            sep = "|------|" + "|".join(["------"] * len(p1_acw_models)) + "|--------|"
            lines.extend([header, sep])

            for gov in GOVERNMENTS:
                row = f"| {gov} |"
                for m in p1_acw_models:
                    gov_data = p1_acw.get(m, {}).get(gov, {})
                    scores = gov_data.get("scores", {})
                    vals = [float(scores.get(c, {}).get("score", 0)) for c in ALL_ACW_CODES]
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
            lines.extend(["", "### 합의 점수 — 차원별 비교 (5회 평균)", ""])
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

            # ── 표준편차 요약 ──
            lines.extend(["### 측정 안정성 (5회 표준편차 요약)", ""])
            lines.append("| 모델 | 정부 | 평균 std | max std |")
            lines.append("|------|------|---------|---------|")
            for m in p1_acw_models:
                for gov in GOVERNMENTS:
                    gov_agg = aggregated.get("panel1_acw", {}).get(m, {}).get(gov, {})
                    stds = [v.get("std", 0) for v in gov_agg.get("scores", {}).values()]
                    if stds:
                        lines.append(f"| {MODEL_CALLERS[m][0]} | {gov} | {statistics.mean(stds):.2f} | {max(stds):.2f} |")
            lines.append("")

    # ── Panel 1: INST ──
    p1_inst = _extract_simple_scores(aggregated, "panel1_inst")
    if p1_inst:
        p1_inst_models = [m for m in models if m in p1_inst and p1_inst[m]]
        if p1_inst_models:
            dim_codes = [c for c, _, _ in INST_DIMENSIONS]
            consensus = compute_consensus(p1_inst, GOVERNMENTS, dim_codes)

            lines.extend([
                "---",
                "## Panel 1: 제도적 적응 메커니즘 — 중앙정부 결과 (5회 평균)",
                "",
                "### 모델별 정부 합계 점수 (/8)",
                "",
            ])
            header = "| 정부 | " + " | ".join(MODEL_CALLERS[m][0] for m in p1_inst_models) + " | **합의** |"
            sep = "|------|" + "|".join(["------"] * len(p1_inst_models)) + "|--------|"
            lines.extend([header, sep])

            for gov in GOVERNMENTS:
                row = f"| {gov} |"
                for m in p1_inst_models:
                    gov_data = p1_inst.get(m, {}).get(gov, {})
                    scores = gov_data.get("scores", {})
                    total = sum(float(scores.get(c, {}).get("score", 0)) for c in dim_codes)
                    row += f" {total:.1f} |"
                if gov in consensus:
                    c_total = sum(consensus[gov].get(c, 0) for c in dim_codes)
                    row += f" **{c_total:.1f}** |"
                else:
                    row += " — |"
                lines.append(row)
            lines.append("")

    # ── Panel 2: ACW sub-wheel ──
    p2_acw = _extract_simple_scores(aggregated, "panel2_acw")
    if p2_acw:
        p2_acw_models = [m for m in models if m in p2_acw and p2_acw[m]]
        if p2_acw_models:
            lines.extend([
                "---",
                "## Panel 2: ACW Sub-wheel — 이재명 지방정부 (5회 평균)",
                "",
            ])

            for gov in LOCAL_GOVERNMENTS:
                codes = _get_acw_local_codes(gov)
                exclude = ACW_EXCLUDE_SEONGNAM if "성남" in gov else ACW_EXCLUDE_GYEONGGI if "경기" in gov else set()
                n_codes = len(codes)

                consensus = compute_consensus(p2_acw, [gov], codes)

                lines.extend([
                    f"### {gov} ({n_codes}/22 기준, 제외: {', '.join(sorted(exclude))})",
                    "",
                ])

                header = "| 기준 | " + " | ".join(MODEL_CALLERS[m][0] for m in p2_acw_models) + " | **합의** |"
                sep = "|------|" + "|".join(["------"] * len(p2_acw_models)) + "|--------|"
                lines.extend([header, sep])

                for code in codes:
                    row = f"| {code} |"
                    for m in p2_acw_models:
                        gov_data = p2_acw.get(m, {}).get(gov, {})
                        score = gov_data.get("scores", {}).get(code, {}).get("score", "—")
                        row += f" {score} |"
                    c_score = consensus.get(gov, {}).get(code, 0)
                    row += f" **{c_score:+.2f}** |"
                    lines.append(row)

                c_vals = [consensus.get(gov, {}).get(c, 0) for c in codes]
                c_avg = sum(c_vals) / len(c_vals) if c_vals else 0
                lines.append(f"\n**평균**: {c_avg:+.2f}\n")

    # ── Panel 2: INST ──
    p2_inst = _extract_simple_scores(aggregated, "panel2_inst")
    if p2_inst:
        p2_inst_models = [m for m in models if m in p2_inst and p2_inst[m]]
        if p2_inst_models:
            dim_codes = [c for c, _, _ in INST_LOCAL_DIMENSIONS]
            consensus = compute_consensus(p2_inst, LOCAL_GOVERNMENTS, dim_codes)

            lines.extend([
                "---",
                "## Panel 2: 제도적 적응 메커니즘 — 지방정부 (5회 평균)",
                "",
            ])

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

    # ── Panel 2: Agenda/Lowi ──
    p2_agenda = _extract_simple_scores(aggregated, "panel2_agenda")
    if p2_agenda:
        p2_agenda_models = [m for m in models if m in p2_agenda and p2_agenda[m]]
        if p2_agenda_models:
            agenda_codes = [c for c, _, _ in AGENDA_CRITERIA]
            consensus = compute_consensus(p2_agenda, LOCAL_GOVERNMENTS, agenda_codes)

            type_names = {"E1": "분배", "E2": "규제", "E3": "재분배", "E4": "구성", "E5": "적응도구"}

            lines.extend([
                "---",
                "## Panel 2: Lowi 정책유형 분류 — 지방정부 (5회 평균)",
                "",
            ])

            header = "| 유형 | " + " | ".join(f"{gov.split('(')[0]}" for gov in LOCAL_GOVERNMENTS) + " |"
            sep = "|------|" + "|".join(["------"] * len(LOCAL_GOVERNMENTS)) + "|"
            lines.extend([header, sep])

            for code in agenda_codes:
                name = type_names.get(code, code)
                row = f"| {code} ({name}) |"
                for gov in LOCAL_GOVERNMENTS:
                    c_score = consensus.get(gov, {}).get(code, 0)
                    row += f" {c_score:.1f}% |"
                lines.append(row)
            lines.append("")

    # ── 방법론 주석 ──
    lines.extend([
        "---",
        "## 방법론 주석",
        "",
        "### 5회 반복 측정",
        "- 각 모델이 동일 프롬프트로 5회 독립 측정을 수행한 후 평균 점수를 사용.",
        "- 판단유보(0점) 금지 지침을 추가하여 정보 부족에 의한 0점 남발을 방지.",
        "- CLOVA thinking 비활성화로 응답 일관성 향상.",
        "- 표준편차(std)로 각 기준별 측정 안정성을 확인.",
        "",
        "### 비교 제약 조건",
        "- Panel 1(중앙정부)과 Panel 2(지방정부)의 ACW 점수는 **직접 비교 불가**.",
        "- Panel 2 ACW는 중앙정부에만 해당하는 기준을 제외한 sub-wheel로 구성.",
        "  - 성남시장: 19/22 기준 (V2, Re3, L2 제외)",
        "  - 경기도지사: 20/22 기준 (Re3, L2 제외)",
        "",
        "### 기능적 등가성 적용 (제도적 메커니즘)",
        "- 지방정부의 조례·규칙은 중앙정부의 법률·대통령령과 기능적으로 등가하게 취급.",
        "",
        "### 합의 점수 계산",
        "- 모델별 5라운드 평균 먼저 계산 → 5모델 평균 = 최종 합의.",
        "",
    ])

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# ROUND 검증
# ═══════════════════════════════════════════════════════════

def verify_round(round_num: int) -> dict:
    """라운드 완료 상태 확인"""
    path = ROUNDS_DIR / f"round_{round_num}.json"
    if not path.exists():
        return {"round": round_num, "exists": False, "total": 0, "complete": 0}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = 0
    complete = 0
    missing = []
    all_tasks = _get_all_tasks()

    for panel_key, _, gov_list, _, _ in all_tasks:
        for mk in MODEL_CALLERS:
            for gov in gov_list:
                total += 1
                if is_already_done(data, panel_key, mk, gov):
                    complete += 1
                else:
                    missing.append(f"{panel_key}/{mk}/{gov}")

    return {
        "round": round_num,
        "exists": True,
        "total": total,
        "complete": complete,
        "missing": missing[:10],  # 최대 10개만 표시
    }


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="5-Round Multi-AI Scoring")
    parser.add_argument("--round", type=int, default=0,
                        help="특정 라운드만 실행 (2~5). 0이면 미완료 라운드 전부")
    parser.add_argument("--aggregate-only", action="store_true",
                        help="집계만 수행 (API 호출 없음)")
    parser.add_argument("--models", nargs="+",
                        default=None,
                        choices=["gpt", "claude", "grok", "clova", "gemini"],
                        help="특정 모델만 실행")
    parser.add_argument("--verify", action="store_true",
                        help="각 라운드 완료 상태만 확인")
    args = parser.parse_args()

    _print("=" * 60)
    _print("5-Round Multi-AI Scoring")
    _print(f"모델: {', '.join(MODEL_CALLERS[m][0] for m in (args.models or MODEL_CALLERS.keys()))}")
    _print("=" * 60)

    # ── 검증 모드 ──
    if args.verify:
        for i in range(1, 6):
            info = verify_round(i)
            status = f"✓ {info['complete']}/{info['total']}" if info["exists"] else "✗ 파일 없음"
            _print(f"  Round {i}: {status}")
            if info.get("missing"):
                for m in info["missing"]:
                    _print(f"    미완료: {m}")
        return

    # ── 집계 전용 모드 ──
    if args.aggregate_only:
        aggregated = aggregate_rounds()
        if aggregated:
            report = generate_5round_report(aggregated)
            report_path = OUTPUT_DIR / "scoring_v2_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            _print(f"  보고서 갱신: {report_path}")
        return

    # ── 라운드 실행 ──
    if args.round:
        rounds_to_run = [args.round]
    else:
        rounds_to_run = [2, 3, 4, 5]

    for rn in rounds_to_run:
        run_round(rn, model_filter=args.models)
        _print(f"\n{'─'*40}")

    # ── 자동 집계 ──
    _print("\n▶ 5라운드 집계")
    aggregated = aggregate_rounds()
    if aggregated:
        report = generate_5round_report(aggregated)
        report_path = OUTPUT_DIR / "scoring_v2_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        _print(f"  보고서 갱신: {report_path}")

    # ── 검증 ──
    _print("\n▶ 라운드 검증")
    for i in range(1, 6):
        info = verify_round(i)
        status = f"✓ {info['complete']}/{info['total']}" if info["exists"] else "✗ 파일 없음"
        _print(f"  Round {i}: {status}")

    _print(f"\n{'='*60}")
    _print("완료!")
    _print(f"{'='*60}")


if __name__ == "__main__":
    main()
