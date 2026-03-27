"""Retry blind coding for 3 failed models: Claude, Gemini, CLOVA."""
import json, os, sys, time, re
from pathlib import Path
from dotenv import load_dotenv

PROJECT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT / ".env")

RESULTS_JSON = PROJECT / "data" / "raw_downloads" / "blind_coding_responses.json"
TIDE_PATH = PROJECT / "data" / "verified" / "tide_attribution.md"

SYSTEM_PROMPT = """You are an institutional change analyst. Classify each policy action as:
- T (Trend): Would happen regardless of president (inherited law, global technology trend)
- I (Intentional): Direct result of president's deliberate decision
- I- (Intentional Negative): Deliberate action that REDUCED adaptive capacity
- D (Drift): Institution exists but fails to function under this president
- E (External): Outside presidential control (global crisis, technology paradigm shift)

Respond in JSON format: [{"id": "item_id", "code": "T/I/I-/D/E", "rationale": "brief reason"}]
Only output the JSON array, no other text."""

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
            d = r.json()
            return d["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"  {m}: {e}")
            continue
    raise RuntimeError("All Gemini models failed")

def call_clova(system, user):
    import requests
    key = os.getenv("CLOVA_STUDIO_API_KEY","").strip()
    base = os.getenv("CLOVA_STUDIO_BASE_URL","https://clovastudio.stream.ntruss.com").rstrip("/")
    r = requests.post(f"{base}/v3/chat-completions/HCX-007",
        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
        json={"messages":[{"role":"system","content":system},{"role":"user","content":user}],
              "temperature":0.2}, timeout=180)
    r.raise_for_status()
    d = r.json()
    return d.get("result",d).get("message",{}).get("content","")

def retry_call(fn, system, user, retries=3):
    for i in range(retries):
        try:
            return fn(system, user)
        except Exception as e:
            print(f"  [Retry {i+1}/{retries}] {e}")
            time.sleep(2 ** i)
    return None

def extract_items():
    """Extract blind items from existing results JSON."""
    with open(RESULTS_JSON) as f:
        data = json.load(f)
    # Get the prompt that was used for successful models
    for model, rounds in data.get("classification_results", {}).items():
        for rnd in rounds:
            if rnd.get("raw_response"):
                # Found a working prompt - reconstruct items from it
                break
    # Fallback: parse TIDE file for borderline items
    text = TIDE_PATH.read_text(encoding="utf-8")
    items = []
    for line in text.split("\n"):
        if "| Y |" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                items.append({"id": parts[1], "action": parts[2], "code": parts[3]})
    return items, data

def build_prompt(items):
    lines = ["Classify each action below as T, I, I-, D, or E:\n"]
    # Vignettes first
    lines.append("CALIBRATION (known answers):")
    lines.append("V1: A government expanded nationwide digital infrastructure, improving e-government rankings → Expected: T")
    lines.append("V2: After a major infectious disease management failure, a government completely restructured the disease control system → Expected: I")
    lines.append("V3: A government maintained a citizen participation platform but policy adoption rate dropped significantly → Expected: D")
    lines.append("\nITEMS TO CLASSIFY:")
    for i, item in enumerate(items):
        # Anonymize: remove president names and specific dates
        action = item["action"]
        for name in ["노무현","이명박","박근혜","문재인","윤석열","이재명"]:
            action = action.replace(name, "Government X")
        action = re.sub(r'\d{4}\.\d{2}\.\d{2}', 'YYYY.MM.DD', action)
        action = re.sub(r'\d{4}\.\d{2}', 'YYYY.MM', action)
        lines.append(f"{item['id']}: {action}")
    lines.append("\nRespond as JSON array: [{\"id\":\"...\",\"code\":\"T/I/I-/D/E\",\"rationale\":\"...\"}]")
    return "\n".join(lines)

def parse_response(text, items):
    """Parse JSON from model response."""
    # Try to find JSON array
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return []

def main():
    items, existing_data = extract_items()
    print(f"Found {len(items)} borderline items")

    if not items:
        print("No borderline items found, exiting")
        return

    prompt = build_prompt(items)

    models = {
        "Claude-Sonnet-4.6": call_claude,
        "Gemini-3-Flash": call_gemini,
        "HCX-007": call_clova,
    }

    retry_results = existing_data.get("retry_results", {})

    for model_name, caller in models.items():
        print(f"\n{'='*50}")
        print(f"  {model_name} - 3 rounds")
        print(f"{'='*50}")
        rounds = []
        for rnd in range(1, 4):
            print(f"  Round {rnd}/3...")
            resp = retry_call(caller, SYSTEM_PROMPT, prompt)
            if resp:
                parsed = parse_response(resp, items)
                rounds.append({"round": rnd, "parsed": parsed, "raw": resp[:2000], "count": len(parsed)})
                print(f"    Got {len(parsed)} classifications")
            else:
                rounds.append({"round": rnd, "error": "All retries failed"})
                print(f"    FAILED")

        retry_results[model_name] = rounds
        existing_data["retry_results"] = retry_results
        with open(RESULTS_JSON, "w") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved {model_name}")

    # Calculate agreement for retry models
    print(f"\n{'='*50}")
    print("Agreement summary (retry models):")
    for model_name, rounds in retry_results.items():
        agree = 0
        total = 0
        for rnd in rounds:
            for p in rnd.get("parsed", []):
                for item in items:
                    if p.get("id") == item["id"]:
                        total += 1
                        if p.get("code","").replace("+","") in item["code"]:
                            agree += 1
        if total > 0:
            print(f"  {model_name}: {agree}/{total} ({100*agree/total:.1f}%)")
        else:
            print(f"  {model_name}: no data")

    print("\nRetry complete! Results saved to blind_coding_responses.json")

if __name__ == "__main__":
    main()
