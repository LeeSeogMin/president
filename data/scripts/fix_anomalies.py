"""이상치 3건 재평가: CLOVA ACW, Grok INST, Gemini INST — 이재명(2025-)"""
import json, os, sys, re, time, requests

sys.path.insert(0, os.path.dirname(__file__))
from ai_scoring_v2 import extract_json, ACW_CRITERIA, INST_DIMENSIONS, SYSTEM_PROMPT

RAW_PATH = os.path.join(os.path.dirname(__file__), "tables", "scoring_v2_raw.json")
raw = json.load(open(RAW_PATH, "r", encoding="utf-8"))

# 다른 모델 참조 점수 추출 함수
def get_ref_scores(panel, gov, exclude_model, score_keys):
    ref = []
    labels = {"gpt":"GPT-5.2","claude":"Claude Sonnet 4.6","grok":"Grok-4-1","clova":"CLOVA","gemini":"Gemini"}
    for m in ["gpt","claude","grok","clova","gemini"]:
        if m == exclude_model:
            continue
        scores = raw[panel].get(m,{}).get(gov,{}).get("scores",{})
        lines = []
        for k in score_keys:
            s = scores.get(k,{})
            lines.append(f"  {k}: {s.get('score','?')} ({s.get('rationale','?')})")
        ref.append(f"### {labels[m]}\n" + "\n".join(lines))
    return "\n\n".join(ref)

# 로컬 컨텍스트
ctx_path = os.path.join(os.path.dirname(__file__), "data", "ljm_local_context.md")
local_ctx = open(ctx_path, "r", encoding="utf-8").read()[:2000]

FORCE_INSTRUCTION = (
    "## 절대 준수 지침\n"
    "- 이재명 정부는 출범 초기이지만 다른 AI 모델들은 공약·인수위 계획·지방행정 경력을 근거로 이미 평가를 완료했습니다.\n"
    "- 당신도 반드시 실질적인 점수를 부여해야 합니다.\n"
    "- '평가 불가', '데이터 부족' 등의 이유로 0점 일괄 부여는 금지됩니다.\n"
    "- '미래 정부' 또는 '미설계'라는 이유로 0점 일괄 부여도 금지됩니다.\n"
    "- 반대로 근거 없이 전부 만점(2점)을 주는 것도 금지됩니다.\n"
    "- 기준별로 개별 근거에 따라 차등 점수를 반드시 부여하세요.\n"
    "- 아래에 다른 모델들의 평가를 참고로 제공합니다. 이를 참고하되 독립적으로 판단하세요.\n\n"
)


def call_clova_no_thinking(prompt):
    """CLOVA thinking 비활성화 호출"""
    api_key = os.getenv("CLOVA_STUDIO_API_KEY")
    model = os.getenv("CLOVA_STUDIO_MODEL", "HCX-007")
    base_url = (os.getenv("CLOVA_STUDIO_BASE_URL") or "https://clovastudio.stream.ntruss.com").rstrip("/")
    resp = requests.post(
        f"{base_url}/v3/chat-completions/{model}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": "한국 행정학 전문가. 반드시 JSON만 출력. 0점 일괄 부여 금지. rationale 1문장 50자 이내."},
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


def call_grok(prompt):
    api_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    resp = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning"),
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_gemini(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
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
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts)
    return ""


def fix_one(panel, gov, model_key, caller, score_keys, prompt_builder):
    print(f"\n{'='*60}")
    print(f"재평가: {panel} / {gov} / {model_key}")
    print(f"{'='*60}")

    ref = get_ref_scores(panel, gov, model_key, score_keys)
    prompt = prompt_builder(ref)

    for attempt in range(1, 4):
        try:
            text = caller(prompt)
            print(f"  응답 {len(text)}자 (시도 {attempt})")
            result = extract_json(text)
            scores = result.get("scores", {})

            vals = [int(scores.get(k, {}).get("score", 0)) for k in score_keys if k in scores]
            zero_pct = vals.count(0) / len(vals) * 100 if vals else 100
            all_same = len(set(vals)) <= 1

            print(f"  파싱: {len(scores)}개, 0점비율: {zero_pct:.0f}%, 전부동일: {all_same}")
            for k in score_keys:
                s = scores.get(k, {})
                print(f"    {k}: {s.get('score','?'):>2}  {s.get('rationale','')}")

            if zero_pct >= 80 or all_same:
                print(f"  ⚠ 여전히 이상 — 재시도")
                time.sleep(3)
                continue

            # 저장
            raw[panel][model_key][gov] = result
            with open(RAW_PATH, "w", encoding="utf-8") as f:
                json.dump(raw, f, ensure_ascii=False, indent=2)
            print(f"  ✓ 저장 완료")
            return True
        except Exception as e:
            print(f"  시도 {attempt} 실패: {e}")
            time.sleep(5)

    print(f"  ✗ 3회 모두 실패/이상")
    return False


# ── 1. CLOVA ACW 이재명(2025-) ──
acw_codes = ['V1','V2','V3','V4','L1','L2','L3','L4','R1','R2','R3','R4',
             'Le1','Le2','Le3','Le4','Re1','Re2','Re3','F1','F2','F3']

def build_clova_acw_prompt(ref):
    p = (
        "당신은 한국 행정학 전문가입니다. Gupta et al.(2010)의 Adaptive Capacity Wheel(ACW)로 "
        "**이재명(2025-)** 정부의 적응 역량을 평가하세요.\n\n"
        + FORCE_INSTRUCTION +
        "## 다른 모델 평가 결과\n" + ref + "\n\n"
        "## 이재명 경력 컨텍스트\n" + local_ctx + "\n\n"
        "## 점수 척도: -2(매우부정) ~ +2(매우긍정)\n\n"
        "## 22개 기준\n"
    )
    for dim, criteria in ACW_CRITERIA.items():
        for code, name, defn in criteria:
            p += f"- {code}. {name}: {defn}\n"
    p += '\nrationale 1문장 50자 이내. JSON만 출력:\n{"government":"이재명(2025-)","scores":{"V1":{"score":0,"rationale":"근거"},...}}\n'
    return p

fix_one("panel1_acw", "이재명(2025-)", "clova", call_clova_no_thinking, acw_codes, build_clova_acw_prompt)


# ── 2. Grok INST 이재명(2025-) ──
inst_codes = ['D1','D2','D3','D4']

def build_grok_inst_prompt(ref):
    p = (
        "당신은 한국 행정학 전문가입니다. Argyris & Schön의 조직학습 이론에 기반한 "
        "제도적 적응 메커니즘으로 **이재명(2025-)** 정부를 평가하세요.\n\n"
        + FORCE_INSTRUCTION +
        "## 다른 모델 평가 결과\n" + ref + "\n\n"
        "## 이재명 경력 컨텍스트\n" + local_ctx + "\n\n"
        "## 4개 차원 (각 0-2점)\n"
    )
    for code, name, defn in INST_DIMENSIONS:
        p += f"- {code}. {name}: {defn}\n"
    p += '\nrationale 1문장 50자 이내. JSON만 출력:\n{"government":"이재명(2025-)","scores":{"D1":{"score":0,"rationale":"근거"},...}}\n'
    return p

time.sleep(2)
fix_one("panel1_inst", "이재명(2025-)", "grok", call_grok, inst_codes, build_grok_inst_prompt)


# ── 3. Gemini INST 이재명(2025-) ──
def build_gemini_inst_prompt(ref):
    p = (
        "당신은 한국 행정학 전문가입니다. Argyris & Schön의 조직학습 이론에 기반한 "
        "제도적 적응 메커니즘으로 **이재명(2025-)** 정부를 평가하세요.\n\n"
        + FORCE_INSTRUCTION +
        "## 다른 모델 평가 결과\n" + ref + "\n\n"
        "## 이재명 경력 컨텍스트\n" + local_ctx + "\n\n"
        "## 4개 차원 (각 0-2점)\n"
    )
    for code, name, defn in INST_DIMENSIONS:
        p += f"- {code}. {name}: {defn}\n"
    p += '\nrationale 1문장 50자 이내. JSON만 출력:\n{"government":"이재명(2025-)","scores":{"D1":{"score":0,"rationale":"근거"},...}}\n'
    return p

time.sleep(2)
fix_one("panel1_inst", "이재명(2025-)", "gemini", call_gemini, inst_codes, build_gemini_inst_prompt)

print("\n\n=== 최종 확인 ===")
raw2 = json.load(open(RAW_PATH, "r", encoding="utf-8"))
for panel, gov, mk in [("panel1_acw","이재명(2025-)","clova"),("panel1_inst","이재명(2025-)","grok"),("panel1_inst","이재명(2025-)","gemini")]:
    scores = raw2[panel][mk][gov]["scores"]
    keys = list(scores.keys())
    vals = [int(scores[k]["score"]) for k in keys]
    avg = sum(vals)/len(vals)
    print(f"  {panel}/{mk}: 평균={avg:+.2f}, 값={vals}")
