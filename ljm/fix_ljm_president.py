"""이재명(2025-) Panel 1 ACW+INST 재평가: 5모델 전부, 연속성 관점"""
import json, os, sys, re, time, requests

sys.path.insert(0, os.path.dirname(__file__))
from ai_scoring_v2 import (
    extract_json, ACW_CRITERIA, INST_DIMENSIONS, SYSTEM_PROMPT,
    call_openai, call_claude, call_grok, call_gemini
)

RAW_PATH = os.path.join(os.path.dirname(__file__), "tables", "scoring_v2_raw.json")
raw = json.load(open(RAW_PATH, "r", encoding="utf-8"))

ctx_path = os.path.join(os.path.dirname(__file__), "data", "ljm_local_context.md")
local_ctx = open(ctx_path, "r", encoding="utf-8").read()[:2500]

CONTINUITY_INSTRUCTION = (
    "## 핵심 평가 지침: 정책 연속성 관점\n"
    "이재명 정부는 2025년 출범 초기입니다. 그러나 다음 원칙에 따라 평가하세요:\n\n"
    "1. **감점 금지**: '출범 초기', '임기가 짧다', '실적 부족'은 감점 사유가 아닙니다.\n"
    "2. **연속성 평가**: 이재명은 성남시장(2010-2018) 8년, 경기도지사(2018-2022) 4년의 "
    "행정 경력이 있습니다. 이 경력에서 입증된 역량이 대통령직에서도 연속된다고 보고 평가하세요.\n"
    "3. **평가 근거**: 공약, 초기 행정명령, 지방행정 경력의 정책 패턴(청년배당→기본소득, "
    "디지털 민원→공공배달앱→디지털플랫폼정부 등)을 근거로 사용하세요.\n"
    "4. **인수위 없음**: 이재명 정부는 별도 인수위원회 없이 출범했습니다.\n"
    "5. **차등 점수**: 기준별로 개별 근거에 따라 차등 점수를 부여하세요. "
    "0점 일괄이나 만점 일괄은 금지합니다.\n\n"
)


def call_clova_no_thinking(prompt):
    api_key = os.getenv("CLOVA_STUDIO_API_KEY")
    model = os.getenv("CLOVA_STUDIO_MODEL", "HCX-007")
    base_url = (os.getenv("CLOVA_STUDIO_BASE_URL") or "https://clovastudio.stream.ntruss.com").rstrip("/")
    resp = requests.post(
        f"{base_url}/v3/chat-completions/{model}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": "한국 행정학 전문가. JSON만 출력. 0점 일괄 금지. rationale 1문장 50자 이내."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.5,
            "thinking": {"type": "disabled"},
        },
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", data).get("message", {}).get("content", "")


CALLERS = {
    "gpt": ("GPT-5.2", call_openai),
    "claude": ("Claude Sonnet 4.6", call_claude),
    "grok": ("Grok-4-1", call_grok),
    "clova": ("HyperCLOVA", call_clova_no_thinking),
    "gemini": ("Gemini 3 Flash", call_gemini),
}


def build_acw_prompt():
    p = (
        "당신은 한국 행정학 전문가입니다. Gupta et al.(2010)의 Adaptive Capacity Wheel(ACW)로 "
        "**이재명(2025-)** 정부의 적응 역량을 평가하세요.\n\n"
        + CONTINUITY_INSTRUCTION +
        "## 이재명 지방행정 경력 팩트시트\n" + local_ctx + "\n\n"
        "## 점수 척도\n"
        "- +2: 매우 긍정적 (해당 기준이 체계적·제도적으로 구현되어 작동)\n"
        "- +1: 긍정적 (해당 기준이 부분적으로 존재하나 일관성 부족)\n"
        "-  0: 중립/해당 없음\n"
        "- -1: 부정적 (해당 기준과 반대되는 특성이 관찰됨)\n"
        "- -2: 매우 부정적 (해당 기준이 구조적으로 억제됨)\n\n"
        "## 22개 기준\n"
    )
    for dim, criteria in ACW_CRITERIA.items():
        for code, name, defn in criteria:
            p += f"- {code}. {name}: {defn}\n"
    p += (
        '\n## 출력 (JSON만, rationale 1문장 50자 이내)\n'
        '{"government":"이재명(2025-)","scores":{"V1":{"score":0,"rationale":"근거"},...22개}}\n'
    )
    return p


def build_inst_prompt():
    p = (
        "당신은 한국 행정학 전문가입니다. Argyris & Schön의 조직학습 이론 기반 "
        "제도적 적응 메커니즘으로 **이재명(2025-)** 정부를 평가하세요.\n\n"
        + CONTINUITY_INSTRUCTION +
        "## 이재명 지방행정 경력 팩트시트\n" + local_ctx + "\n\n"
        "## 4개 차원 (각 0-2점)\n"
    )
    for code, name, defn in INST_DIMENSIONS:
        p += f"- {code}. {name}: {defn}\n"
    p += (
        '\n## 출력 (JSON만, rationale 1문장 50자 이내)\n'
        '{"government":"이재명(2025-)","scores":{"D1":{"score":0,"rationale":"근거"},...4개}}\n'
    )
    return p


acw_prompt = build_acw_prompt()
inst_prompt = build_inst_prompt()
acw_codes = ['V1','V2','V3','V4','L1','L2','L3','L4','R1','R2','R3','R4',
             'Le1','Le2','Le3','Le4','Re1','Re2','Re3','F1','F2','F3']
inst_codes = ['D1','D2','D3','D4']

for mk, (label, caller) in CALLERS.items():
    for panel, prompt, codes in [
        ("panel1_acw", acw_prompt, acw_codes),
        ("panel1_inst", inst_prompt, inst_codes),
    ]:
        print(f"\n[{label}] 이재명(2025-) {panel.split('_')[1].upper()} 평가 중...")
        for attempt in range(1, 4):
            try:
                text = caller(prompt)
                result = extract_json(text)
                scores = result.get("scores", {})
                vals = [int(scores.get(k, {}).get("score", 0)) for k in codes if k in scores]
                zero_pct = vals.count(0) / len(vals) * 100 if vals else 100
                all_same = len(set(vals)) <= 1
                avg = sum(vals) / len(vals) if vals else 0

                print(f"  시도 {attempt}: {len(scores)}개, 평균 {avg:+.2f}, 0점 {zero_pct:.0f}%")

                if zero_pct >= 80 or all_same:
                    print(f"  ⚠ 이상 점수 — 재시도")
                    time.sleep(3)
                    continue

                raw[panel][mk]["이재명(2025-)"] = result
                with open(RAW_PATH, "w", encoding="utf-8") as f:
                    json.dump(raw, f, ensure_ascii=False, indent=2)
                print(f"  ✓ 저장")
                break
            except Exception as e:
                print(f"  시도 {attempt} 실패: {e}")
                time.sleep(5)
        else:
            print(f"  ✗ 3회 실패")

        time.sleep(2)

# 최종 확인
print("\n" + "=" * 60)
print("최종 이재명(2025-) 점수 확인")
print("=" * 60)
raw2 = json.load(open(RAW_PATH, "r", encoding="utf-8"))
for panel, codes in [("panel1_acw", acw_codes), ("panel1_inst", inst_codes)]:
    print(f"\n{panel}:")
    for mk in CALLERS:
        scores = raw2[panel][mk]["이재명(2025-)"]["scores"]
        vals = [int(scores.get(k, {}).get("score", 0)) for k in codes if k in scores]
        avg = sum(vals) / len(vals) if vals else 0
        print(f"  {CALLERS[mk][0]:20s}: 평균 {avg:+.2f}  값={vals}")
