"""Fix GPT-5.2 Task3 (time sensitivity) by batching into 8-item chunks."""
import os, json, re, time, math
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(Path(".env"))
RAW_PATH = Path("data/raw_downloads/action_evaluation_raw.json")

with open(RAW_PATH) as f:
    data = json.load(f)

actions = data["actions"]
BATCH_SIZE = 8
n_batches = math.ceil(len(actions) / BATCH_SIZE)

c = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

T3SYS = "동일 행위가 2003년 vs 2023년에 평가가 달라지는지 판단하시오. JSON 배열로만 응답: [{\"id\":\"...\",\"time_sensitive\":true/false,\"reason\":\"간략한 한국어\"}]"

def build_batch(batch):
    lines = []
    for a in batch:
        desc = a["action"]
        for n in ["노무현","이명박","박근혜","문재인","윤석열","이재명"]:
            desc = desc.replace(n, "정부 X")
        lines.append(f'{a["id"]}: {desc}')
    return "\n".join(lines)

def parse_json(text):
    m = re.search(r'\[.*?\]', text, re.DOTALL)
    if m:
        try: return json.loads(m.group())
        except: pass
    return []

print(f"GPT-5.2 Task3 배치: {len(actions)}건 → {n_batches}배치")

all_parsed = []
for bi in range(n_batches):
    batch = actions[bi*BATCH_SIZE:(bi+1)*BATCH_SIZE]
    prompt = build_batch(batch)
    print(f"  Batch {bi+1}/{n_batches} ({len(batch)}건)...", end=" ")
    for attempt in range(3):
        try:
            r = c.chat.completions.create(
                model="gpt-5.2", temperature=0.2, max_completion_tokens=4000,
                messages=[{"role":"system","content":T3SYS},{"role":"user","content":prompt}])
            parsed = parse_json(r.choices[0].message.content)
            all_parsed.extend(parsed)
            print(f"OK ({len(parsed)}건)")
            break
        except Exception as e:
            print(f"retry {attempt+1}...", end=" ")
            time.sleep(2**attempt)
    else:
        print("FAIL")
    time.sleep(1)

data["task3"]["GPT-5.2"] = {"parsed": all_parsed, "count": len(all_parsed)}
with open(RAW_PATH, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nGPT-5.2 Task3 완료: {len(all_parsed)}건")
