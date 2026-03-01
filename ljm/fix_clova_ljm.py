"""CLOVA 이재명(2025-) ACW 재평가 — 다른 모델 점수 참고 제공"""
import json, os, sys, re, requests

sys.path.insert(0, os.path.dirname(__file__))
from ai_scoring_v2 import call_clova, extract_json, ACW_CRITERIA

# 기존 데이터 로드
RAW_PATH = os.path.join(os.path.dirname(__file__), "tables", "scoring_v2_raw.json")
raw = json.load(open(RAW_PATH, "r", encoding="utf-8"))

# 다른 모델 점수 추출
ref_lines = []
for model_key, label in [("gpt", "GPT-5.2"), ("claude", "Claude Sonnet 4.6"), ("grok", "Grok-4-1")]:
    scores = raw["panel1_acw"][model_key]["이재명(2025-)"]["scores"]
    ref_lines.append(f"### {label}")
    for code in ["V1","V2","V3","V4","L1","L2","L3","L4","R1","R2","R3","R4",
                  "Le1","Le2","Le3","Le4","Re1","Re2","Re3","F1","F2","F3"]:
        s = scores.get(code, {})
        ref_lines.append(f"- {code}: {s.get('score','?')} ({s.get('rationale','?')})")
    ref_lines.append("")

ref_text = "\n".join(ref_lines)

# 로컬 컨텍스트
ctx_path = os.path.join(os.path.dirname(__file__), "data", "ljm_local_context.md")
local_ctx = open(ctx_path, "r", encoding="utf-8").read()[:2000]

# 프롬프트
prompt = (
    "당신은 한국 행정학 전문가입니다. Gupta et al.(2010)의 Adaptive Capacity Wheel(ACW) 프레임워크를 사용하여 "
    "**이재명(2025-)** 정부의 적응 역량을 평가해주세요.\n\n"
    "## 중요 지침\n"
    "- 이재명 정부는 출범 초기이지만, 다른 3개 AI 모델(GPT-5.2, Claude, Grok)은 이미 평가를 완료했습니다.\n"
    "- 아래에 다른 모델들의 평가 결과를 참고로 제공합니다.\n"
    "- 당신도 반드시 각 기준에 대해 -2~+2 범위의 점수를 부여해야 합니다. 0점 일괄 부여는 허용되지 않습니다.\n"
    "- 출범 초기라도 공약, 인수위 계획, 초기 행정명령, 지방행정 경력에서의 정책 연속성 등을 근거로 판단하세요.\n\n"
    "## 다른 모델들의 평가 결과 (참고용)\n"
    f"{ref_text}\n\n"
    "## 이재명의 지방행정 경력 컨텍스트\n"
    f"{local_ctx}\n\n"
    "## 점수 척도\n"
    "- +2: 매우 긍정적 (해당 기준이 체계적·제도적으로 구현되어 작동)\n"
    "- +1: 긍정적 (해당 기준이 부분적으로 존재하나 일관성 부족)\n"
    "-  0: 중립/해당 없음\n"
    "- -1: 부정적 (해당 기준과 반대되는 특성이 관찰됨)\n"
    "- -2: 매우 부정적 (해당 기준이 구조적으로 억제됨)\n\n"
    "## 평가 기준 (22개)\n"
)

for dim, criteria in ACW_CRITERIA.items():
    prompt += f"### {dim}\n"
    for code, name, definition in criteria:
        prompt += f"- **{code}. {name}**: {definition}\n"
    prompt += "\n"

prompt += (
    '## 출력 형식 (반드시 이 JSON만 출력)\n'
    'rationale는 반드시 1문장, 최대 50자로 제한하세요.\n'
    '{"government":"이재명(2025-)","scores":{"V1":{"score":0,"rationale":"근거"},...22개 모두}}\n'
)

# CLOVA 호출
print("CLOVA 호출 중...")
for attempt in range(1, 4):
    try:
        text = call_clova(prompt)
        print(f"응답 길이: {len(text)}자 (시도 {attempt})")
        result = extract_json(text)
        scores = result.get("scores", {})
        print(f"파싱 성공: {len(scores)}개 기준")

        zero_count = sum(1 for v in scores.values() if int(v.get("score", 0)) == 0)
        print(f"0점 개수: {zero_count}/22")

        for code in ["V1","V2","V3","V4","L1","L2","L3","L4","R1","R2","R3","R4",
                      "Le1","Le2","Le3","Le4","Re1","Re2","Re3","F1","F2","F3"]:
            s = scores.get(code, {})
            print(f"  {code}: {s.get('score','?'):>2}  {s.get('rationale','')}")

        # 저장
        raw["panel1_acw"]["clova"]["이재명(2025-)"] = result
        with open(RAW_PATH, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        print("\nscoring_v2_raw.json 업데이트 완료!")
        break
    except Exception as e:
        print(f"시도 {attempt} 실패: {e}")
        if attempt < 3:
            import time
            time.sleep(5)
else:
    print("3회 시도 모두 실패")
    sys.exit(1)
