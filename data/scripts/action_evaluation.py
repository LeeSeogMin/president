"""
Step 6: AI Action Evaluation (Task 2 + Task 3)

Task 2: Score each I/D action on adaptive governance impact (+1/0/-1)
Task 3: Time sensitivity test (same action in 2003 vs 2023)

5 models × 3 rounds × 2 tasks
"""
import json, os, re, sys, time
from pathlib import Path
from dotenv import load_dotenv

PROJECT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT / ".env")

TIDE_PATH = PROJECT / "data" / "verified" / "tide_attribution.md"
OUTPUT_PATH = PROJECT / "data" / "verified" / "action_evaluation_results.md"
RAW_PATH = PROJECT / "data" / "raw_downloads" / "action_evaluation_raw.json"

# ── API Callers ──

def call_openai(system, user, model="gpt-5.2", base_url=None, api_key_env="OPENAI_API_KEY"):
    from openai import OpenAI
    kwargs = {"api_key": os.getenv(api_key_env)}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    r = client.chat.completions.create(
        model=model, temperature=0.2, max_completion_tokens=16384,
        messages=[{"role":"system","content":system},{"role":"user","content":user}])
    return r.choices[0].message.content

def call_claude(system, user):
    from anthropic import Anthropic
    c = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    r = c.messages.create(model="claude-sonnet-4-6", max_tokens=16384, temperature=0.2,
                          system=system, messages=[{"role":"user","content":user}])
    return r.content[0].text

def call_gemini(system, user):
    import requests
    key = os.getenv("GEMINI_API_KEY")
    for m in ["gemini-3-flash-preview", "gemini-2.5-flash-preview-04-17"]:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                params={"key": key},
                json={"system_instruction":{"parts":[{"text":system}]},
                      "contents":[{"parts":[{"text":user}]}],
                      "generationConfig":{"temperature":0.2,"maxOutputTokens":16384}},
                timeout=180)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            if m == "gemini-2.5-flash-preview-04-17":
                raise
            print(f"  {m}: {e}, trying next...")

def call_clova(system, user):
    import requests
    key = os.getenv("CLOVA_STUDIO_API_KEY","").strip()
    base = os.getenv("CLOVA_STUDIO_BASE_URL","https://clovastudio.stream.ntruss.com").rstrip("/")
    r = requests.post(f"{base}/v3/chat-completions/HCX-007",
        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
        json={"messages":[{"role":"system","content":system},{"role":"user","content":user}],
              "temperature":0.2}, timeout=180)
    r.raise_for_status()
    return r.json().get("result",{}).get("message",{}).get("content","")

def retry(fn, *args, retries=3):
    for i in range(retries):
        try:
            return fn(*args)
        except Exception as e:
            print(f"  [Retry {i+1}/{retries}] {e}")
            time.sleep(2 ** i)
    return None

MODELS = {
    "GPT-5.2": lambda s,u: call_openai(s, u, model="gpt-5.2"),
    "Claude-4.6": lambda s,u: call_claude(s, u),
    "Grok-4-1": lambda s,u: call_openai(s, u, model="grok-4-1-fast-reasoning",
                                          base_url="https://api.x.ai/v1", api_key_env="XAI_API_KEY"),
    "Gemini-3": lambda s,u: call_gemini(s, u),
    "HCX-007": lambda s,u: call_clova(s, u),
}

# ── Extract I and D actions ──

def extract_id_actions():
    """Extract all I, I-, and D coded actions from tide_attribution.md"""
    text = TIDE_PATH.read_text(encoding="utf-8")
    actions = []
    current_gov = ""
    for line in text.split("\n"):
        if line.startswith("## ") and "정부" in line:
            current_gov = line.replace("## ", "").split("(")[0].strip()
            # Clean up numbering
            for n in ["1. ","2. ","3. ","4. ","5. ","6. "]:
                current_gov = current_gov.replace(n, "")
        if "| " in line and ("-A" in line or "-B" in line or "-C" in line or
                              "-D" in line or "-E" in line or "-F" in line or "-G" in line):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                aid = parts[1]
                action = parts[2]
                code = parts[3].replace("**","").strip()
                if code in ["I", "I-", "D", "T+I", "I-"]:
                    actions.append({
                        "id": aid,
                        "gov": current_gov,
                        "action": action,
                        "researcher_code": code,
                    })
    return actions

# ── Task 2: Impact Evaluation ──

TASK2_SYSTEM = """You are an adaptive governance expert. Evaluate each policy action's impact on adaptive governance capacity.

For each action, assign:
- +1: Strengthens adaptive governance (improves feedback, learning, flexibility, or responsiveness)
- 0: Neutral (no significant impact on adaptive capacity)
- -1: Weakens adaptive governance (reduces feedback, learning, flexibility, or responsiveness)

Respond ONLY as a JSON array: [{"id":"...", "impact": +1/0/-1, "rationale":"brief reason in Korean"}]"""

def build_task2_prompt(actions):
    lines = ["다음 정책 행위들의 적응적 거버넌스 역량에 대한 영향을 평가하시오.\n"]
    for a in actions:
        # Anonymize
        desc = a["action"]
        for name in ["노무현","이명박","박근혜","문재인","윤석열","이재명"]:
            desc = desc.replace(name, "정부 X")
        lines.append(f'{a["id"]}: {desc}')
    lines.append("\nJSON 배열로 응답: [{\"id\":\"...\", \"impact\": +1/0/-1, \"rationale\":\"...\"}]")
    return "\n".join(lines)

# ── Task 3: Time Sensitivity ──

TASK3_SYSTEM = """You are a comparative governance analyst. Test whether the evaluation of policy actions changes based on the time period.

For each action, consider: Would this action have the SAME adaptive governance impact if implemented in 2003 vs 2023?

Respond ONLY as a JSON array: [{"id":"...", "time_sensitive": true/false, "reason":"brief explanation in Korean"}]"""

def build_task3_prompt(actions):
    lines = ["다음 정책 행위가 2003년에 시행된 경우와 2023년에 시행된 경우, 적응적 거버넌스 관점에서 평가가 달라지는가?\n"]
    for a in actions:
        desc = a["action"]
        for name in ["노무현","이명박","박근혜","문재인","윤석열","이재명"]:
            desc = desc.replace(name, "정부 X")
        lines.append(f'{a["id"]}: {desc}')
    lines.append("\nJSON 배열로 응답: [{\"id\":\"...\", \"time_sensitive\": true/false, \"reason\":\"...\"}]")
    return "\n".join(lines)

def parse_json_response(text):
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return []

# ── Main ──

def main():
    actions = extract_id_actions()
    print(f"Extracted {len(actions)} I/D actions for evaluation")

    if not actions:
        print("No actions found!")
        return

    task2_prompt = build_task2_prompt(actions)
    task3_prompt = build_task3_prompt(actions)

    all_results = {"actions": [a.copy() for a in actions], "task2": {}, "task3": {}}

    for model_name, caller in MODELS.items():
        print(f"\n{'='*50}")
        print(f"  {model_name}")
        print(f"{'='*50}")

        # Task 2: Impact evaluation (3 rounds)
        t2_rounds = []
        for rnd in range(1, 4):
            print(f"  Task2 Round {rnd}/3...")
            resp = retry(caller, TASK2_SYSTEM, task2_prompt)
            if resp:
                parsed = parse_json_response(resp)
                t2_rounds.append({"round": rnd, "parsed": parsed, "count": len(parsed)})
                print(f"    Got {len(parsed)} evaluations")
            else:
                t2_rounds.append({"round": rnd, "error": "failed"})
                print(f"    FAILED")
        all_results["task2"][model_name] = t2_rounds

        # Task 3: Time sensitivity (1 round only - binary question)
        print(f"  Task3...")
        resp = retry(caller, TASK3_SYSTEM, task3_prompt)
        if resp:
            parsed = parse_json_response(resp)
            all_results["task3"][model_name] = {"parsed": parsed, "count": len(parsed)}
            print(f"    Got {len(parsed)} sensitivity checks")
        else:
            all_results["task3"][model_name] = {"error": "failed"}
            print(f"    FAILED")

        # Save incrementally
        with open(RAW_PATH, "w") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"  Saved {model_name}")

    # ── Aggregate Results ──
    print(f"\n{'='*50}")
    print("Aggregating results...")

    # Task 2: Majority vote across models and rounds
    impact_votes = {}  # action_id -> list of votes
    for model, rounds in all_results["task2"].items():
        for rnd in rounds:
            for p in rnd.get("parsed", []):
                aid = p.get("id", "")
                impact = p.get("impact", 0)
                impact_votes.setdefault(aid, []).append(impact)

    # Task 3: Count time-sensitive items
    sensitivity_votes = {}
    for model, data in all_results["task3"].items():
        for p in data.get("parsed", []):
            aid = p.get("id", "")
            ts = p.get("time_sensitive", False)
            sensitivity_votes.setdefault(aid, []).append(ts)

    # Build final table
    lines = [
        "# AI Action Evaluation Results (Step 6)\n",
        f"> 실행일: {time.strftime('%Y-%m-%d %H:%M')}\n",
        "> Task 2: 개별 행위 적응적 거버넌스 영향 평가 (+1/0/-1)\n",
        "> Task 3: 시대 민감도 테스트\n",
        f"> 모델: {', '.join(MODELS.keys())}\n",
        "> 라운드: Task2 3회, Task3 1회\n",
        "\n---\n",
        "\n## 1. Task 2: 행위별 적응적 거버넌스 영향 평가\n",
        "\n| ID | 정부 | 행위 | 연구자 코드 | AI 합의 영향 | 투표 분포 |",
        "|-----|------|------|:----------:|:----------:|----------|",
    ]

    gov_impact_sums = {}

    for a in actions:
        aid = a["id"]
        votes = impact_votes.get(aid, [])
        if votes:
            avg = sum(votes) / len(votes)
            pos = votes.count(1)
            neg = votes.count(-1)
            neu = votes.count(0)
            consensus = "+1" if avg > 0.3 else "-1" if avg < -0.3 else "0"
            dist = f"+1:{pos} 0:{neu} -1:{neg}"
        else:
            consensus = "N/A"
            dist = "no data"
            avg = 0

        gov = a["gov"]
        gov_impact_sums.setdefault(gov, {"pos":0,"neg":0,"neu":0})
        if consensus == "+1":
            gov_impact_sums[gov]["pos"] += 1
        elif consensus == "-1":
            gov_impact_sums[gov]["neg"] += 1
        else:
            gov_impact_sums[gov]["neu"] += 1

        short_action = a["action"][:50] + "..." if len(a["action"]) > 50 else a["action"]
        lines.append(f"| {aid} | {gov} | {short_action} | {a['researcher_code']} | **{consensus}** | {dist} |")

    # Government summary
    lines.extend([
        "\n\n## 2. 정부별 적응적 거버넌스 영향 종합\n",
        "\n| 정부 | 긍정(+1) | 중립(0) | 부정(-1) | **Net Impact** |",
        "|------|:-------:|:------:|:-------:|:-----------:|",
    ])

    for gov in ["노무현","이명박","박근혜","문재인","윤석열","이재명"]:
        s = gov_impact_sums.get(gov, {"pos":0,"neg":0,"neu":0})
        net = s["pos"] - s["neg"]
        sign = "+" if net > 0 else ""
        lines.append(f"| {gov} | {s['pos']} | {s['neu']} | {s['neg']} | **{sign}{net}** |")

    # Task 3 summary
    lines.extend([
        "\n\n## 3. Task 3: 시대 민감도 테스트\n",
        "\n| ID | 시대 민감? | 모델 합의 |",
        "|-----|:--------:|----------|",
    ])

    ts_count = 0
    total_count = 0
    for a in actions:
        aid = a["id"]
        votes = sensitivity_votes.get(aid, [])
        if votes:
            total_count += 1
            true_count = sum(1 for v in votes if v)
            ratio = true_count / len(votes)
            sensitive = "YES" if ratio > 0.5 else "NO"
            if sensitive == "YES":
                ts_count += 1
            lines.append(f"| {aid} | **{sensitive}** | {true_count}/{len(votes)} models |")

    lines.extend([
        f"\n**시대 민감 항목**: {ts_count}/{total_count} ({100*ts_count/max(total_count,1):.0f}%)\n",
        "\n→ 시대 민감 항목은 T/I 경계 사례로, T 성분이 포함됨을 AI가 확인한 것임.\n",
        "\n---\n",
        f"\n원자료: `data/raw_downloads/action_evaluation_raw.json`\n",
    ])

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nResults saved to {OUTPUT_PATH}")
    print(f"Raw data saved to {RAW_PATH}")
    print("\n=== STEP 6 COMPLETE ===")

if __name__ == "__main__":
    main()
